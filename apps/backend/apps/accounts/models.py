from __future__ import annotations

from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils import timezone as django_timezone
from django.utils.text import slugify

from apps.common.form_validation import validate_digit_phone
from apps.common.models import TimeStampedModel


class AccountRole(TimeStampedModel):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name


class UserRole(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="glow_role_assignments", on_delete=models.CASCADE)
    role = models.ForeignKey(AccountRole, related_name="user_assignments", on_delete=models.CASCADE)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["user", "role"], name="unique_user_account_role")]
        ordering = ["role__name", "user_id"]

    def __str__(self) -> str:
        return f"{self.user_id}:{self.role.slug}"


class CustomerProfile(TimeStampedModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name="customer_profile", on_delete=models.CASCADE)
    contact = models.ForeignKey("contacts.Contact", related_name="customer_profiles", on_delete=models.SET_NULL, blank=True, null=True)
    phone = models.CharField(max_length=32, blank=True)
    normalized_phone = models.CharField(max_length=32, blank=True, db_index=True)
    verified_phone_at = models.DateTimeField(blank=True, null=True)
    verified_email_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["normalized_phone"],
                condition=~Q(normalized_phone=""),
                name="unique_customer_profile_normalized_phone",
            )
        ]

    def save(self, *args, **kwargs):
        cleaned, error = validate_digit_phone(self.phone)
        self.normalized_phone = "" if error else cleaned
        if kwargs.get("update_fields") and "phone" in kwargs["update_fields"]:
            kwargs["update_fields"] = set(kwargs["update_fields"]) | {"normalized_phone"}
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.phone or self.user.email or f"Customer #{self.pk}"


class CustomerNotificationSubscription(TimeStampedModel):
    class Channel(models.TextChoices):
        EXPO = "expo", "Expo push"
        WEB_PUSH = "web_push", "Web push"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="customer_notification_subscriptions", on_delete=models.CASCADE)
    contact = models.ForeignKey("contacts.Contact", related_name="notification_subscriptions", on_delete=models.SET_NULL, blank=True, null=True)
    channel = models.CharField(max_length=32, choices=Channel.choices)
    platform = models.CharField(max_length=40, blank=True)
    device_id = models.CharField(max_length=180, blank=True, db_index=True)
    device_name = models.CharField(max_length=180, blank=True)
    app_version = models.CharField(max_length=80, blank=True)
    token = models.TextField(blank=True)
    subscription_endpoint = models.URLField(max_length=500, blank=True, db_index=True)
    subscription = models.JSONField(default=dict, blank=True)
    permission_status = models.CharField(max_length=40, default="unknown")
    enabled = models.BooleanField(default=True)
    locale = models.CharField(max_length=40, blank=True)
    timezone = models.CharField(max_length=80, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    last_registered_at = models.DateTimeField(default=django_timezone.now)
    disabled_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["-last_registered_at", "-id"]
        constraints = [
            models.UniqueConstraint(
                fields=["channel", "token"],
                condition=~Q(token=""),
                name="unique_customer_notification_channel_token",
            ),
            models.UniqueConstraint(
                fields=["channel", "subscription_endpoint"],
                condition=~Q(subscription_endpoint=""),
                name="unique_customer_notification_channel_endpoint",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.channel}:{self.user_id}"
