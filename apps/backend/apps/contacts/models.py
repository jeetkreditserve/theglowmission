from __future__ import annotations

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.text import slugify

from apps.common.form_validation import validate_digit_phone
from apps.common.models import TimeStampedModel


class ContactStatus(TimeStampedModel):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    ordering = models.PositiveIntegerField(default=0)
    is_default = models.BooleanField(default=False)

    class Meta:
        ordering = ["ordering", "name"]
        verbose_name_plural = "Contact statuses"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        if self.is_default:
            ContactStatus.objects.exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.contacts.exists():
            raise ValidationError("Move contacts to another status before deleting this status.")
        super().delete(*args, **kwargs)

    def __str__(self) -> str:
        return self.name


class Contact(TimeStampedModel):
    full_name = models.CharField(max_length=180, blank=True)
    email = models.EmailField(blank=True)
    normalized_email = models.CharField(max_length=254, blank=True, db_index=True)
    phone = models.CharField(max_length=32, blank=True)
    normalized_phone = models.CharField(max_length=32, blank=True, db_index=True)
    address = models.TextField(blank=True)
    age = models.PositiveSmallIntegerField(blank=True, null=True)
    skin_type = models.CharField(max_length=120, blank=True)
    preferred_ritual = models.CharField(max_length=180, blank=True)
    preferred_day = models.CharField(max_length=160, blank=True)
    skin_goal = models.TextField(blank=True)
    marketing_consent = models.BooleanField(default=False)
    status = models.ForeignKey(
        ContactStatus,
        related_name="contacts",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    first_activity_at = models.DateTimeField(blank=True, null=True)
    last_activity_at = models.DateTimeField(blank=True, null=True)
    source_response_count = models.PositiveIntegerField(default=0)
    is_merged = models.BooleanField(default=False)
    merged_into = models.ForeignKey(
        "self",
        related_name="merged_contacts",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    merged_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["-last_activity_at", "-updated_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["normalized_email"],
                condition=Q(is_merged=False) & ~Q(normalized_email=""),
                name="unique_contact_normalized_email",
            ),
            models.UniqueConstraint(
                fields=["normalized_phone"],
                condition=Q(is_merged=False) & ~Q(normalized_phone=""),
                name="unique_contact_normalized_phone",
            ),
        ]

    def __str__(self) -> str:
        return self.display_name

    @property
    def display_name(self) -> str:
        if self.full_name:
            return self.full_name
        if self.email:
            return self.email
        if self.phone:
            return self.phone
        if self.address:
            return self.address.splitlines()[0]
        return f"Contact #{self.pk or 'new'}"

    def clean(self):
        if not any([self.full_name, self.email, self.phone, self.address]):
            raise ValidationError("A contact needs at least one identity field.")

    def save(self, *args, **kwargs):
        self.normalized_email = str(self.email or "").strip().lower()
        cleaned_phone, phone_error = validate_digit_phone(self.phone)
        self.normalized_phone = "" if phone_error else cleaned_phone
        super().save(*args, **kwargs)

    def mark_merged_into(self, target: "Contact") -> None:
        if target.pk == self.pk:
            raise ValidationError("A contact cannot be merged into itself.")
        self.is_merged = True
        self.merged_into = target
        self.merged_at = timezone.now()
        self.save(update_fields=["is_merged", "merged_into", "merged_at", "updated_at"])


class ContactAuditEvent(TimeStampedModel):
    class EventType(models.TextChoices):
        CREATED = "created", "Created"
        UPDATED = "updated", "Updated"
        STATUS_CHANGED = "status_changed", "Status changed"
        CONSENT_CHANGED = "consent_changed", "Consent changed"
        MERGED = "merged", "Merged"
        SYNC_FAILED = "sync_failed", "Sync failed"

    contact = models.ForeignKey(Contact, related_name="audit_events", on_delete=models.CASCADE)
    event_type = models.CharField(max_length=40, choices=EventType.choices)
    field_name = models.CharField(max_length=80, blank=True)
    old_value = models.JSONField(blank=True, null=True)
    new_value = models.JSONField(blank=True, null=True)
    source_type = models.CharField(max_length=80, blank=True)
    source_id = models.CharField(max_length=80, blank=True)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="contact_audit_events",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    message = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at", "-id"]

    def __str__(self) -> str:
        return f"{self.contact_id} {self.event_type} {self.field_name}".strip()


class ContactNote(TimeStampedModel):
    contact = models.ForeignKey(Contact, related_name="notes", on_delete=models.CASCADE)
    body = models.TextField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="contact_notes",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ["-created_at", "-id"]

    def __str__(self) -> str:
        return f"Note for contact {self.contact_id}"
