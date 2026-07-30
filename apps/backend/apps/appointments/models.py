from __future__ import annotations

from datetime import timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.common.models import TimeStampedModel


class AppointmentAvailabilityWindow(TimeStampedModel):
    date = models.DateField(blank=True, null=True, db_index=True)
    weekday = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(6)])
    starts_at = models.TimeField()
    ends_at = models.TimeField()
    active = models.BooleanField(default=True)
    label = models.CharField(max_length=120, blank=True)
    ordering = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["date", "weekday", "ordering", "starts_at", "id"]
        indexes = [
            models.Index(fields=["date", "starts_at"], name="appointment_date_77b8e5_idx"),
            models.Index(fields=["weekday", "starts_at"], name="appointment_weekda_c56b14_idx"),
        ]

    def clean(self):
        if self.date:
            self.weekday = self.date.weekday()
        if self.starts_at and self.ends_at and self.ends_at <= self.starts_at:
            raise ValidationError({"ends_at": "End time must be after the start time."})

    def save(self, *args, **kwargs):
        if self.date:
            self.weekday = self.date.weekday()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        day = self.date.isoformat() if self.date else str(self.weekday)
        return self.label or f"{day} {self.starts_at}-{self.ends_at}"


class AppointmentBlock(TimeStampedModel):
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    reason = models.CharField(max_length=180, blank=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["starts_at", "id"]

    def clean(self):
        if self.starts_at and self.ends_at and self.ends_at <= self.starts_at:
            raise ValidationError({"ends_at": "End time must be after the start time."})

    def __str__(self) -> str:
        return self.reason or f"Blocked {self.starts_at}"


class Appointment(TimeStampedModel):
    class Status(models.TextChoices):
        CONFIRMED = "confirmed", "Confirmed"
        CANCELLED = "cancelled", "Cancelled"
        COMPLETED = "completed", "Completed"
        NO_SHOW = "no_show", "No show"

    class Source(models.TextChoices):
        CUSTOMER_APP = "customer_app", "Customer app"
        STAFF_APP = "staff_app", "Staff app"
        WEBSITE = "website", "Website"
        ADMIN = "admin", "Admin"
        CAMPAIGN_RESPONSE = "campaign_response", "Campaign response"

    service = models.ForeignKey("content.Service", related_name="appointments", on_delete=models.PROTECT)
    contact = models.ForeignKey("contacts.Contact", related_name="appointments", on_delete=models.SET_NULL, blank=True, null=True)
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="customer_appointments", on_delete=models.SET_NULL, blank=True, null=True)
    full_name = models.CharField(max_length=180)
    phone = models.CharField(max_length=32)
    email = models.EmailField(blank=True)
    notes = models.TextField(blank=True)
    skin_goal = models.TextField(blank=True)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    duration_minutes = models.PositiveSmallIntegerField(default=60)
    status = models.CharField(max_length=24, choices=Status.choices, default=Status.CONFIRMED)
    source = models.CharField(max_length=32, choices=Source.choices, default=Source.WEBSITE)
    campaign_response = models.ForeignKey(
        "campaigns.CampaignFormResponse",
        related_name="appointments",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="created_appointments",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    cancelled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="cancelled_appointments",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    cancellation_reason = models.TextField(blank=True)
    customer_notes = models.TextField(blank=True)
    internal_notes = models.TextField(blank=True)

    class Meta:
        ordering = ["starts_at", "id"]
        indexes = [
            models.Index(fields=["status", "starts_at"]),
            models.Index(fields=["service", "starts_at"]),
            models.Index(fields=["contact", "starts_at"]),
            models.Index(fields=["customer", "starts_at"]),
        ]

    def clean(self):
        errors = {}
        if self.starts_at and self.ends_at and self.ends_at <= self.starts_at:
            errors["ends_at"] = "End time must be after the start time."
        if self.status == self.Status.CONFIRMED and self.starts_at and self.ends_at:
            appointments = Appointment.objects.select_related("service").filter(status=self.Status.CONFIRMED)
            if self.pk:
                appointments = appointments.exclude(pk=self.pk)
            for appointment in appointments:
                buffer = appointment_effective_buffer_minutes(appointment)
                expanded_start = appointment.starts_at - timedelta(minutes=buffer)
                expanded_end = appointment.ends_at + timedelta(minutes=buffer)
                if self.starts_at < expanded_end and self.ends_at > expanded_start:
                    errors["starts_at"] = "This appointment overlaps another confirmed appointment or downtime window."
                    break
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.full_name} - {self.service} at {self.starts_at}"


def appointment_effective_buffer_minutes(appointment: Appointment) -> int:
    downtime = max(int(getattr(settings, "APPOINTMENT_DOWNTIME_MINUTES", 15) or 0), 0)
    service_buffer = max(int(getattr(appointment.service, "booking_buffer_minutes", 0) or 0), 0)
    return max(downtime, service_buffer)


class AppointmentPhoto(TimeStampedModel):
    class PhotoType(models.TextChoices):
        BEFORE = "before", "Before"
        AFTER = "after", "After"

    appointment = models.ForeignKey(Appointment, related_name="photos", on_delete=models.CASCADE)
    photo_type = models.CharField(max_length=16, choices=PhotoType.choices)
    image = models.ImageField(upload_to="appointment-photos/")
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="appointment_photos",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ["created_at", "id"]
        indexes = [
            models.Index(fields=["appointment", "photo_type"]),
        ]

    def __str__(self) -> str:
        return f"{self.appointment_id} {self.photo_type}"


class AppointmentFinanceEntry(TimeStampedModel):
    class EntryType(models.TextChoices):
        INCOME = "income", "Income"
        EXPENSE = "expense", "Expense"

    entry_date = models.DateField()
    entry_type = models.CharField(max_length=16, choices=EntryType.choices)
    label = models.CharField(max_length=180)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    appointment = models.ForeignKey(Appointment, related_name="finance_entries", on_delete=models.SET_NULL, blank=True, null=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="appointment_finance_entries",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ["-entry_date", "-id"]
        indexes = [
            models.Index(fields=["entry_type", "entry_date"]),
        ]

    def __str__(self) -> str:
        return f"{self.entry_type} {self.amount} on {self.entry_date}"


class AppointmentNotificationLog(TimeStampedModel):
    class Channel(models.TextChoices):
        EXPO = "expo", "Expo push"
        WEB_PUSH = "web_push", "Web push"
        EMAIL = "email", "Email"

    class EventType(models.TextChoices):
        CONFIRMATION = "confirmation", "Confirmation"
        RESCHEDULE = "reschedule", "Reschedule"
        CANCELLATION = "cancellation", "Cancellation"
        REMINDER = "reminder", "Reminder"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SENT = "sent", "Sent"
        SKIPPED = "skipped", "Skipped"
        FAILED = "failed", "Failed"

    appointment = models.ForeignKey(Appointment, related_name="notification_logs", on_delete=models.CASCADE)
    channel = models.CharField(max_length=32, choices=Channel.choices)
    event_type = models.CharField(max_length=32, choices=EventType.choices)
    reminder_minutes = models.PositiveSmallIntegerField(blank=True, null=True)
    recipient = models.CharField(max_length=500, blank=True)
    status = models.CharField(max_length=24, choices=Status.choices, default=Status.PENDING)
    error = models.TextField(blank=True)
    sent_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        indexes = [
            models.Index(fields=["event_type", "reminder_minutes"]),
            models.Index(fields=["channel", "status"]),
        ]

    def __str__(self) -> str:
        return f"{self.appointment_id} {self.channel} {self.event_type} {self.status}"
