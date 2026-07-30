from __future__ import annotations

import logging

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db import IntegrityError, transaction
from django.utils import timezone
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.text import slugify
from rest_framework.exceptions import PermissionDenied, ValidationError

from apps.accounts.models import AccountRole, CustomerNotificationSubscription, CustomerProfile, UserRole
from apps.contacts.models import Contact, ContactStatus
from apps.contacts.services import apply_contact_values, default_contact_status, normalize_email, normalize_phone


CUSTOMER_ROLE = "customer"
STAFF_ROLE = "staff"
SUPERUSER_ROLE = "superuser"
CUSTOMER_PROFILE_FIELDS = [
    "full_name",
    "phone",
    "address",
    "age",
    "skin_type",
    "preferred_ritual",
    "preferred_day",
    "skin_goal",
    "marketing_consent",
]
logger = logging.getLogger(__name__)


def account_roles_for_user(user) -> list[str]:
    roles = set(user.glow_role_assignments.select_related("role").values_list("role__slug", flat=True))
    if getattr(user, "is_superuser", False):
        roles.update({SUPERUSER_ROLE, STAFF_ROLE})
    elif getattr(user, "is_staff", False):
        roles.add(STAFF_ROLE)
    if hasattr(user, "customer_profile"):
        roles.add(CUSTOMER_ROLE)
    return sorted(roles)


def account_type_for_user(user) -> str:
    if getattr(user, "is_superuser", False):
        return SUPERUSER_ROLE
    if getattr(user, "is_staff", False):
        return STAFF_ROLE
    if hasattr(user, "customer_profile"):
        return CUSTOMER_ROLE
    return "user"


def customer_contact_for_user(user) -> Contact | None:
    profile = getattr(user, "customer_profile", None)
    return profile.contact if profile else None


def phone_for_user(user) -> str:
    profile = getattr(user, "customer_profile", None)
    if not profile:
        return ""
    return profile.phone or (profile.contact.phone if profile.contact else "")


def ensure_role(slug: str, name: str = "") -> AccountRole:
    role, _ = AccountRole.objects.get_or_create(slug=slug, defaults={"name": name or slug.replace("-", " ").title()})
    return role


def assign_role(user, slug: str, name: str = "") -> None:
    role = ensure_role(slug, name)
    UserRole.objects.get_or_create(user=user, role=role)


@transaction.atomic
def create_customer_user(*, email: str, password: str, first_name: str = "", last_name: str = "", full_name: str = "", phone: str = "", marketing_consent: bool = False):
    if not getattr(settings, "CUSTOMER_REGISTRATION_ENABLED", True):
        raise ValidationError({"detail": "Customer registration is not enabled."})
    User = get_user_model()
    normalized_email = normalize_email(email)
    if User.objects.filter(email__iexact=normalized_email).exists():
        raise ValidationError({"email": "An account with this email already exists."})

    first_name, last_name, full_name = normalize_customer_names(first_name=first_name, last_name=last_name, full_name=full_name)
    user = User.objects.create_user(
        username=unique_username(normalized_email.split("@")[0] or "customer"),
        email=normalized_email,
        password=password,
        first_name=first_name,
        last_name=last_name,
    )
    profile = ensure_customer_profile_for_user(user, phone=phone, full_name=full_name)
    if profile.contact:
        apply_contact_values(
            profile.contact,
            {"marketing_consent": bool(marketing_consent)},
            source_type="customer_register",
            actor=user,
            allow_blank=False,
            activity_at=timezone.now(),
        )
    return user


@transaction.atomic
def authenticate_customer_login(*, email: str, password: str):
    User = get_user_model()
    normalized_email = normalize_email(email)
    user_record = User.objects.filter(email__iexact=normalized_email).order_by("id").first()
    if not user_record:
        raise ValidationError("Invalid email or password.")
    user = authenticate(username=user_record.get_username(), password=password)
    if not user or not user.is_active:
        raise ValidationError("Invalid email or password.")
    validate_customer_login_user(user)
    ensure_customer_profile_for_user(user)
    return user


def request_customer_password_reset(email: str) -> dict:
    User = get_user_model()
    normalized_email = normalize_email(email)
    user = (
        User.objects.filter(email__iexact=normalized_email, is_active=True, is_staff=False, is_superuser=False)
        .order_by("id")
        .first()
    )
    response = {"message": "If an account exists, password reset instructions have been sent."}
    if not user:
        return response

    uid, token, reset_url = build_password_reset_payload(user)
    subject = getattr(settings, "CUSTOMER_PASSWORD_RESET_EMAIL_SUBJECT", "Reset your The Glow Mission password")
    body = (
        "We received a request to reset your The Glow Mission password.\n\n"
        f"Open this link to set a new password:\n{reset_url}\n\n"
        "If you did not request this, you can ignore this email."
    )
    send_mail(subject, body, getattr(settings, "DEFAULT_FROM_EMAIL", ""), [user.email], fail_silently=False)
    if getattr(settings, "CUSTOMER_PASSWORD_RESET_EXPOSE_TOKEN", False):
        response.update({"uid": uid, "token": token, "reset_url": reset_url})
    return response


@transaction.atomic
def confirm_customer_password_reset(*, uid: str, token: str, password: str):
    user = user_from_reset_uid(uid)
    invalid = ValidationError({"token": "Invalid or expired reset token."})
    if not user or not default_token_generator.check_token(user, token):
        raise invalid
    if user.is_staff or user.is_superuser or not user.is_active:
        raise invalid
    user.set_password(password)
    user.save(update_fields=["password"])
    profile = ensure_customer_profile_for_user(user)
    if not profile.verified_email_at:
        profile.verified_email_at = timezone.now()
        profile.save(update_fields=["verified_email_at", "updated_at"])
    return user


def build_password_reset_payload(user) -> tuple[str, str, str]:
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    template = getattr(settings, "CUSTOMER_PASSWORD_RESET_URL_TEMPLATE", "https://theglowmission.com/reset-password?uid={uid}&token={token}")
    reset_url = template.format(uid=uid, token=token)
    return uid, token, reset_url


def user_from_reset_uid(uid: str):
    try:
        user_id = force_str(urlsafe_base64_decode(uid))
        return get_user_model().objects.get(pk=user_id)
    except Exception:
        return None


@transaction.atomic
def ensure_customer_profile_for_user(user, *, phone: str = "", full_name: str = "") -> CustomerProfile:
    validate_customer_account_user(user)
    normalized_phone = normalize_phone(phone)
    first_name, last_name, full_name = normalize_customer_names(first_name=user.first_name, last_name=user.last_name, full_name=full_name)
    contact = link_contact_for_identity(phone=normalized_phone, email=user.email, first_name=first_name, last_name=last_name, full_name=full_name)
    profile, _ = CustomerProfile.objects.get_or_create(user=user)
    changed_fields: list[str] = []
    if normalized_phone and profile.phone != normalized_phone:
        assert_unique_customer_phone(profile, normalized_phone)
        profile.phone = normalized_phone
        changed_fields.append("phone")
    if contact and profile.contact_id != contact.pk:
        profile.contact = contact
        changed_fields.append("contact")
    if changed_fields:
        profile.save(update_fields=changed_fields + ["updated_at"])
    assign_role(user, CUSTOMER_ROLE, "Customer")
    return profile


@transaction.atomic
def update_customer_profile(user, values: dict) -> dict:
    profile = ensure_customer_profile_for_user(user)
    contact = profile.contact or link_contact_for_identity(email=user.email, first_name=user.first_name, last_name=user.last_name)
    if contact and profile.contact_id != contact.pk:
        profile.contact = contact
        profile.save(update_fields=["contact", "updated_at"])

    full_name = values.get("full_name", "")
    first_name, last_name, normalized_full_name = normalize_customer_names(
        first_name=values.get("first_name", user.first_name),
        last_name=values.get("last_name", user.last_name),
        full_name=full_name,
    )
    user_changes = []
    if "first_name" in values or full_name:
        if user.first_name != first_name:
            user.first_name = first_name
            user_changes.append("first_name")
    if "last_name" in values or full_name:
        if user.last_name != last_name:
            user.last_name = last_name
            user_changes.append("last_name")
    if user_changes:
        user.save(update_fields=user_changes)

    profile_changes = []
    if "phone" in values:
        normalized_phone = normalize_phone(values.get("phone"))
        assert_unique_customer_phone(profile, normalized_phone)
        if profile.phone != normalized_phone:
            profile.phone = normalized_phone
            profile_changes.append("phone")
    if profile_changes:
        profile.save(update_fields=profile_changes + ["updated_at"])

    if contact:
        contact_values = {field: values[field] for field in CUSTOMER_PROFILE_FIELDS if field in values}
        if normalized_full_name and "full_name" not in contact_values:
            contact_values["full_name"] = normalized_full_name
        if "phone" in contact_values:
            assert_unique_contact_phone(contact, normalize_phone(contact_values.get("phone")))
        if contact_values:
            apply_contact_values(
                contact,
                contact_values,
                source_type="customer_profile",
                actor=user,
                allow_blank=True,
                activity_at=timezone.now(),
            )
    return customer_profile_payload(user)


def customer_profile_payload(user) -> dict:
    profile = ensure_customer_profile_for_user(user)
    contact = profile.contact
    return {
        "id": profile.pk,
        "user": user.pk,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "full_name": contact.full_name if contact else full_name_for_user(user),
        "phone": profile.phone or (contact.phone if contact else ""),
        "contact": contact.pk if contact else None,
        "address": contact.address if contact else "",
        "age": contact.age if contact else None,
        "skin_type": contact.skin_type if contact else "",
        "preferred_ritual": contact.preferred_ritual if contact else "",
        "preferred_day": contact.preferred_day if contact else "",
        "skin_goal": contact.skin_goal if contact else "",
        "marketing_consent": contact.marketing_consent if contact else False,
        "verified_email_at": profile.verified_email_at,
        "verified_phone_at": profile.verified_phone_at,
        "updated_at": profile.updated_at,
    }


@transaction.atomic
def register_notification_subscription(user, values: dict) -> tuple[CustomerNotificationSubscription, bool]:
    if not getattr(settings, "CUSTOMER_NOTIFICATIONS_ENABLED", True):
        raise ValidationError({"detail": "Customer notifications are not enabled."})
    profile = ensure_customer_profile_for_user(user)
    channel = values["channel"]
    token = str(values.get("token") or "").strip()
    subscription = values.get("subscription") or {}
    subscription_endpoint = str(values.get("subscription_endpoint") or subscription.get("endpoint") or "").strip()
    device_id = str(values.get("device_id") or "").strip()

    queryset = CustomerNotificationSubscription.objects.select_for_update()
    existing = None
    if token:
        existing = queryset.filter(channel=channel, token=token).first()
    if not existing and subscription_endpoint:
        existing = queryset.filter(channel=channel, subscription_endpoint=subscription_endpoint).first()
    if not existing and device_id:
        existing = queryset.filter(user=user, channel=channel, device_id=device_id).first()

    subscription_obj = existing or CustomerNotificationSubscription(user=user, channel=channel)
    created = existing is None
    apply_notification_values(subscription_obj, values, profile=profile, token=token, subscription_endpoint=subscription_endpoint)
    try:
        subscription_obj.save()
    except IntegrityError as exc:
        raise ValidationError({"detail": "This notification subscription is already registered."}) from exc
    return subscription_obj, created


@transaction.atomic
def update_notification_subscription(user, subscription: CustomerNotificationSubscription, values: dict) -> CustomerNotificationSubscription:
    validate_customer_account_user(user)
    if subscription.user_id != user.pk:
        raise PermissionDenied("This notification subscription is not available.")
    profile = ensure_customer_profile_for_user(user)
    token = str(values.get("token", subscription.token) or "").strip()
    raw_subscription = values.get("subscription", subscription.subscription) or {}
    subscription_endpoint = str(values.get("subscription_endpoint", subscription.subscription_endpoint) or raw_subscription.get("endpoint") or "").strip()
    apply_notification_values(subscription, values, profile=profile, token=token, subscription_endpoint=subscription_endpoint)
    subscription.save()
    return subscription


def disable_notification_subscription(user, subscription: CustomerNotificationSubscription) -> None:
    validate_customer_account_user(user)
    if subscription.user_id != user.pk:
        raise PermissionDenied("This notification subscription is not available.")
    subscription.enabled = False
    subscription.permission_status = "denied"
    subscription.disabled_at = timezone.now()
    subscription.save(update_fields=["enabled", "permission_status", "disabled_at", "updated_at"])


def apply_notification_values(
    subscription_obj: CustomerNotificationSubscription,
    values: dict,
    *,
    profile: CustomerProfile,
    token: str,
    subscription_endpoint: str,
) -> None:
    subscription_obj.user = profile.user
    subscription_obj.contact = profile.contact
    subscription_obj.channel = values.get("channel", subscription_obj.channel)
    subscription_obj.platform = str(values.get("platform", subscription_obj.platform) or "")[:40]
    subscription_obj.device_id = str(values.get("device_id", subscription_obj.device_id) or "")[:180]
    subscription_obj.device_name = str(values.get("device_name", subscription_obj.device_name) or "")[:180]
    subscription_obj.app_version = str(values.get("app_version", subscription_obj.app_version) or "")[:80]
    subscription_obj.token = token
    subscription_obj.subscription_endpoint = subscription_endpoint
    subscription_obj.subscription = values.get("subscription", subscription_obj.subscription) or {}
    subscription_obj.permission_status = str(values.get("permission_status", subscription_obj.permission_status) or "unknown")[:40]
    subscription_obj.enabled = bool(values.get("enabled", subscription_obj.enabled))
    if subscription_obj.permission_status == "denied":
        subscription_obj.enabled = False
    subscription_obj.locale = str(values.get("locale", subscription_obj.locale) or "")[:40]
    subscription_obj.timezone = str(values.get("timezone", subscription_obj.timezone) or "")[:80]
    subscription_obj.metadata = values.get("metadata", subscription_obj.metadata) or {}
    subscription_obj.last_registered_at = timezone.now()
    subscription_obj.disabled_at = None if subscription_obj.enabled else timezone.now()


def link_contact_for_identity(*, phone: str = "", email: str = "", first_name: str = "", last_name: str = "", full_name: str = "") -> Contact | None:
    normalized_phone = normalize_phone(phone)
    normalized_email = normalize_email(email)
    email_contact = Contact.objects.filter(is_merged=False, normalized_email=normalized_email).first() if normalized_email else None
    phone_contact = Contact.objects.filter(is_merged=False, normalized_phone=normalized_phone).first() if normalized_phone else None
    contact = email_contact or phone_contact
    if not contact and not (normalized_phone or normalized_email or full_name):
        return None
    if not contact:
        contact = Contact(status=customer_contact_status(), first_activity_at=timezone.now(), last_activity_at=timezone.now())
    if not contact.status_id:
        contact.status = customer_contact_status()
    resolved_full_name = full_name or " ".join(part for part in [first_name, last_name] if part).strip()
    if resolved_full_name and not contact.full_name:
        contact.full_name = resolved_full_name
    if normalized_email and not contact.email:
        contact.email = normalized_email
    if normalized_phone and not contact.phone and (not phone_contact or phone_contact.pk == contact.pk):
        contact.phone = normalized_phone
    contact.save()
    return contact


def customer_contact_status():
    default_contact_status()
    return ContactStatus.objects.filter(slug="customer").first() or default_contact_status()


def validate_customer_login_user(user) -> None:
    if not user.is_active:
        raise ValidationError({"user": "This account is inactive."})
    if user.is_staff or user.is_superuser:
        raise ValidationError({"email": "Use staff sign in for this account."})


def validate_customer_account_user(user) -> None:
    if not getattr(user, "is_authenticated", False) or not user.is_active:
        raise PermissionDenied("A customer account is required.")
    if user.is_staff or user.is_superuser:
        raise PermissionDenied("Use a customer account for this endpoint.")


def assert_unique_customer_phone(profile: CustomerProfile, normalized_phone: str) -> None:
    if not normalized_phone:
        return
    queryset = CustomerProfile.objects.filter(normalized_phone=normalized_phone)
    if profile.pk:
        queryset = queryset.exclude(pk=profile.pk)
    if queryset.exists():
        raise ValidationError({"phone": "This phone is already linked to another customer account."})


def assert_unique_contact_phone(contact: Contact, normalized_phone: str) -> None:
    if not normalized_phone:
        return
    queryset = Contact.objects.filter(is_merged=False, normalized_phone=normalized_phone)
    if contact.pk:
        queryset = queryset.exclude(pk=contact.pk)
    if queryset.exists():
        raise ValidationError({"phone": "This phone belongs to another contact."})


def normalize_customer_names(*, first_name: str = "", last_name: str = "", full_name: str = "") -> tuple[str, str, str]:
    first_name = str(first_name or "").strip()
    last_name = str(last_name or "").strip()
    full_name = str(full_name or "").strip() or " ".join(part for part in [first_name, last_name] if part).strip()
    if full_name and not (first_name or last_name):
        parts = full_name.split(maxsplit=1)
        first_name = parts[0]
        last_name = parts[1] if len(parts) > 1 else ""
    return first_name[:150], last_name[:150], full_name[:180]


def full_name_for_user(user) -> str:
    return " ".join(part for part in [user.first_name, user.last_name] if part).strip()


def unique_username(seed: str) -> str:
    User = get_user_model()
    base = slugify(seed)[:120] or "customer"
    candidate = base
    suffix = 1
    while User.objects.filter(username=candidate).exists():
        suffix += 1
        candidate = f"{base}-{suffix}"[:150]
    return candidate
