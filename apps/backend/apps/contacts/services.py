from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.utils import timezone

from apps.common.form_validation import validate_digit_phone
from apps.contacts.models import Contact, ContactAuditEvent, ContactStatus


DEFAULT_STATUSES = [
    ("Lead", "lead", 0, True),
    ("Prospect", "prospect", 1, False),
    ("Customer", "customer", 2, False),
    ("Inactive", "inactive", 3, False),
]

CONTACT_FIELD_KEYS = {
    "full_name": ("full_name", "name"),
    "email": ("email",),
    "phone": ("phone",),
    "address": ("address",),
    "age": ("age",),
    "skin_type": ("skin_type",),
    "preferred_ritual": ("preferred_ritual",),
    "preferred_day": ("preferred_day",),
    "skin_goal": ("skin_goal",),
    "marketing_consent": ("marketing_consent",),
}

CONTACT_PROFILE_FIELDS = [
    "full_name",
    "email",
    "phone",
    "address",
    "age",
    "skin_type",
    "preferred_ritual",
    "preferred_day",
    "skin_goal",
    "marketing_consent",
]


@dataclass
class ContactSyncResult:
    contact: Contact | None
    status: str
    error: str = ""


def ensure_default_contact_statuses() -> ContactStatus:
    default_status: ContactStatus | None = None
    for name, slug, ordering, is_default in DEFAULT_STATUSES:
        status, _ = ContactStatus.objects.update_or_create(
            slug=slug,
            defaults={"name": name, "ordering": ordering, "is_default": is_default},
        )
        if is_default:
            default_status = status
    return default_status or ContactStatus.objects.order_by("ordering", "id").first()


def default_contact_status() -> ContactStatus | None:
    status = ContactStatus.objects.filter(is_default=True).first()
    if status:
        return status
    return ensure_default_contact_statuses()


def normalize_email(value: object) -> str:
    return str(value or "").strip().lower()


def normalize_phone(value: object) -> str:
    cleaned, error = validate_digit_phone(value)
    return "" if error else cleaned


def extract_contact_values(response_data: dict[str, Any]) -> dict[str, Any]:
    values: dict[str, Any] = {}
    for contact_field, source_keys in CONTACT_FIELD_KEYS.items():
        for key in source_keys:
            if key in response_data:
                values[contact_field] = coerce_contact_value(contact_field, response_data.get(key))
                break
    if "email" in values:
        values["email"] = normalize_email(values["email"])
    if "phone" in values:
        values["phone"] = normalize_phone(values["phone"])
    return values


def coerce_contact_value(field_name: str, value: Any) -> Any:
    if field_name == "marketing_consent":
        return bool(value)
    if value is None:
        return None
    if field_name == "age":
        if value == "":
            return None
        try:
            return int(float(value))
        except (TypeError, ValueError):
            return None
    if isinstance(value, str):
        return value.strip()
    return value


def has_identity(values: dict[str, Any]) -> bool:
    return any(not is_empty(values.get(field)) for field in ["full_name", "email", "phone", "address"])


def is_empty(value: Any) -> bool:
    return value is None or value == "" or value == []


def sync_campaign_response_to_contact(response) -> ContactSyncResult:
    try:
        return _sync_campaign_response_to_contact(response)
    except Exception as exc:  # pragma: no cover - defensive boundary for public form submissions.
        response.contact_sync_status = "failed"
        response.contact_sync_error = str(exc)
        response.save(update_fields=["contact_sync_status", "contact_sync_error", "updated_at"])
        return ContactSyncResult(contact=None, status="failed", error=str(exc))


@transaction.atomic
def _sync_campaign_response_to_contact(response) -> ContactSyncResult:
    values = extract_contact_values(response.response_data or {})
    if not has_identity(values):
        response.contact = None
        response.contact_sync_status = "skipped"
        response.contact_sync_error = ""
        response.save(update_fields=["contact", "contact_sync_status", "contact_sync_error", "updated_at"])
        return ContactSyncResult(contact=None, status="skipped")

    normalized_email = normalize_email(values.get("email"))
    normalized_phone = normalize_phone(values.get("phone"))
    if not normalized_phone:
        existing_contact = Contact.objects.filter(is_merged=False, normalized_email=normalized_email).first() if normalized_email else None
        if not existing_contact:
            message = "Phone is required to create a new contact."
            response.contact = None
            response.contact_sync_status = "skipped"
            response.contact_sync_error = message
            response.save(update_fields=["contact", "contact_sync_status", "contact_sync_error", "updated_at"])
            return ContactSyncResult(contact=None, status="skipped", error=message)

    contact, created, conflict = find_or_create_contact(values, response)
    skipped_fields: set[str] = set()
    if conflict:
        skipped_fields.add("phone")
    apply_contact_values(
        contact,
        values,
        source_type="campaign_response",
        source_id=str(response.pk),
        allow_blank=False,
        activity_at=response.submitted_at,
        skipped_fields=skipped_fields,
    )

    if created:
        ContactAuditEvent.objects.create(
            contact=contact,
            event_type=ContactAuditEvent.EventType.CREATED,
            new_value=snapshot_contact(contact),
            source_type="campaign_response",
            source_id=str(response.pk),
            message=f"Created from {response.form.title} response.",
        )

    if conflict:
        ContactAuditEvent.objects.create(
            contact=contact,
            event_type=ContactAuditEvent.EventType.UPDATED,
            field_name="phone",
            old_value=contact.phone or None,
            new_value=values.get("phone") or None,
            source_type="campaign_response",
            source_id=str(response.pk),
            message=conflict,
        )

    response.contact = contact
    response.contact_sync_status = "conflict" if conflict else "synced"
    response.contact_sync_error = conflict
    response.save(update_fields=["contact", "contact_sync_status", "contact_sync_error", "updated_at"])
    refresh_contact_response_count(contact)
    return ContactSyncResult(contact=contact, status=response.contact_sync_status, error=conflict)


def find_or_create_contact(values: dict[str, Any], response) -> tuple[Contact, bool, str]:
    normalized_email = normalize_email(values.get("email"))
    normalized_phone = normalize_phone(values.get("phone"))
    email_contact = Contact.objects.filter(is_merged=False, normalized_email=normalized_email).first() if normalized_email else None
    phone_contact = Contact.objects.filter(is_merged=False, normalized_phone=normalized_phone).first() if normalized_phone else None

    if email_contact and phone_contact and email_contact.pk != phone_contact.pk:
        return (
            email_contact,
            False,
            f"Email matched contact #{email_contact.pk}; phone matched contact #{phone_contact.pk}. Email match was used.",
        )
    if email_contact:
        return email_contact, False, ""
    if phone_contact:
        return phone_contact, False, ""
    if not normalized_phone:
        raise ValidationError("Phone is required to create a new contact.")

    contact = Contact(
        status=default_contact_status(),
        first_activity_at=response.submitted_at,
        last_activity_at=response.submitted_at,
    )
    for field_name in CONTACT_PROFILE_FIELDS:
        if field_name in values and not is_empty(values[field_name]):
            setattr(contact, field_name, values[field_name])
    contact.normalized_email = normalize_email(contact.email)
    contact.normalized_phone = normalize_phone(contact.phone)
    try:
        contact.save()
    except IntegrityError as exc:
        raise ValidationError("Unable to create contact because the email or phone already belongs to another contact.") from exc
    return contact, True, ""


def apply_contact_values(
    contact: Contact,
    values: dict[str, Any],
    *,
    source_type: str,
    source_id: str = "",
    actor=None,
    allow_blank: bool,
    activity_at=None,
    skipped_fields: set[str] | None = None,
) -> list[ContactAuditEvent]:
    skipped_fields = skipped_fields or set()
    changes: list[tuple[str, Any, Any, str]] = []

    for field_name in CONTACT_PROFILE_FIELDS:
        if field_name not in values or field_name in skipped_fields:
            continue
        new_value = values[field_name]
        if not allow_blank and is_empty(new_value):
            continue
        if field_name == "email":
            new_value = normalize_email(new_value)
            contact.normalized_email = new_value
        if field_name == "phone":
            new_value = normalize_phone(new_value)
            contact.normalized_phone = new_value
        old_value = getattr(contact, field_name)
        if old_value != new_value:
            event_type = ContactAuditEvent.EventType.CONSENT_CHANGED if field_name == "marketing_consent" else ContactAuditEvent.EventType.UPDATED
            changes.append((field_name, old_value, new_value, event_type))
            setattr(contact, field_name, new_value)

    if activity_at:
        if not contact.first_activity_at or activity_at < contact.first_activity_at:
            contact.first_activity_at = activity_at
        if not contact.last_activity_at or activity_at > contact.last_activity_at:
            contact.last_activity_at = activity_at

    contact.normalized_email = normalize_email(contact.email)
    contact.normalized_phone = normalize_phone(contact.phone)
    contact.save()

    events = []
    for field_name, old_value, new_value, event_type in changes:
        events.append(
            ContactAuditEvent.objects.create(
                contact=contact,
                event_type=event_type,
                field_name=field_name,
                old_value=old_value,
                new_value=new_value,
                source_type=source_type,
                source_id=source_id,
                actor=actor if getattr(actor, "is_authenticated", False) else None,
            )
        )
    return events


def snapshot_contact(contact: Contact) -> dict[str, Any]:
    return {field: getattr(contact, field) for field in CONTACT_PROFILE_FIELDS}


def refresh_contact_response_count(contact: Contact) -> None:
    count = contact.campaign_responses.count()
    if contact.source_response_count != count:
        contact.source_response_count = count
        contact.save(update_fields=["source_response_count", "updated_at"])


def possible_duplicate_contacts(contact: Contact):
    queryset = Contact.objects.filter(is_merged=False).exclude(pk=contact.pk)
    filters = Q()
    if contact.full_name:
        filters |= Q(full_name__iexact=contact.full_name)
    if contact.address:
        filters |= Q(address__iexact=contact.address)
    if not filters:
        return queryset.none()
    return queryset.filter(filters).order_by("-last_activity_at", "-updated_at")
