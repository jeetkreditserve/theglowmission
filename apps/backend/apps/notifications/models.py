from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.common.models import TimeStampedModel


class NotificationCampaign(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        READY = "ready", "Ready"
        SENT = "sent", "Sent"

    title = models.CharField(max_length=180)
    subject = models.CharField(max_length=180)
    body = models.TextField()
    status = models.CharField(max_length=24, choices=Status.choices, default=Status.DRAFT)
    target_status = models.ForeignKey(
        "contacts.ContactStatus",
        related_name="notification_campaigns",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    marketing_consent_only = models.BooleanField(default=True)
    include_customers = models.BooleanField(default=True)
    scheduled_at = models.DateTimeField(blank=True, null=True)
    sent_at = models.DateTimeField(blank=True, null=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="created_notification_campaigns",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ["-updated_at", "-id"]
        indexes = [
            models.Index(fields=["status", "scheduled_at"]),
        ]

    def __str__(self) -> str:
        return self.title


class NotificationRecipient(TimeStampedModel):
    campaign = models.ForeignKey(NotificationCampaign, related_name="recipients", on_delete=models.CASCADE)
    contact = models.ForeignKey("contacts.Contact", related_name="notification_recipients", on_delete=models.SET_NULL, blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="notification_recipients", on_delete=models.SET_NULL, blank=True, null=True)
    display_name = models.CharField(max_length=180, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=32, blank=True)

    class Meta:
        ordering = ["display_name", "id"]
        constraints = [
            models.UniqueConstraint(fields=["campaign", "contact"], name="unique_notification_campaign_contact"),
            models.UniqueConstraint(fields=["campaign", "user"], name="unique_notification_campaign_user"),
        ]

    def __str__(self) -> str:
        return self.display_name or self.email or f"Recipient #{self.pk}"


class NotificationMessageLog(TimeStampedModel):
    class Channel(models.TextChoices):
        EMAIL = "email", "Email"
        EXPO = "expo", "Expo push"
        WEB_PUSH = "web_push", "Web push"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SENT = "sent", "Sent"
        SKIPPED = "skipped", "Skipped"
        FAILED = "failed", "Failed"

    campaign = models.ForeignKey(NotificationCampaign, related_name="message_logs", on_delete=models.CASCADE)
    recipient = models.ForeignKey(NotificationRecipient, related_name="message_logs", on_delete=models.CASCADE)
    contact = models.ForeignKey("contacts.Contact", related_name="notification_message_logs", on_delete=models.SET_NULL, blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="notification_message_logs", on_delete=models.SET_NULL, blank=True, null=True)
    channel = models.CharField(max_length=32, choices=Channel.choices)
    recipient_address = models.CharField(max_length=500, blank=True)
    status = models.CharField(max_length=24, choices=Status.choices, default=Status.PENDING)
    error = models.TextField(blank=True)
    sent_at = models.DateTimeField(blank=True, null=True)
    opened_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        indexes = [
            models.Index(fields=["channel", "status"]),
            models.Index(fields=["contact", "created_at"]),
            models.Index(fields=["user", "created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.campaign_id} {self.channel} {self.status}"
