from django.contrib import admin

from apps.appointments.models import (
    Appointment,
    AppointmentAvailabilityWindow,
    AppointmentBlock,
    AppointmentFinanceEntry,
    AppointmentNotificationLog,
    AppointmentPhoto,
)


@admin.register(AppointmentAvailabilityWindow)
class AppointmentAvailabilityWindowAdmin(admin.ModelAdmin):
    list_display = ["weekday", "starts_at", "ends_at", "label", "active", "ordering"]
    list_filter = ["weekday", "active"]
    ordering = ["weekday", "ordering", "starts_at"]


@admin.register(AppointmentBlock)
class AppointmentBlockAdmin(admin.ModelAdmin):
    list_display = ["starts_at", "ends_at", "reason", "active"]
    list_filter = ["active"]
    search_fields = ["reason"]


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ["starts_at", "ends_at", "full_name", "phone", "service", "status", "source"]
    list_filter = ["status", "source", "service"]
    search_fields = ["full_name", "phone", "email", "service__title"]
    raw_id_fields = ["service", "contact", "customer", "campaign_response", "created_by", "cancelled_by"]


@admin.register(AppointmentNotificationLog)
class AppointmentNotificationLogAdmin(admin.ModelAdmin):
    list_display = ["appointment", "channel", "event_type", "reminder_minutes", "recipient", "status", "sent_at"]
    list_filter = ["channel", "event_type", "status"]
    search_fields = ["recipient", "error"]


@admin.register(AppointmentPhoto)
class AppointmentPhotoAdmin(admin.ModelAdmin):
    list_display = ["appointment", "photo_type", "created_by", "created_at"]
    list_filter = ["photo_type"]
    raw_id_fields = ["appointment", "created_by"]


@admin.register(AppointmentFinanceEntry)
class AppointmentFinanceEntryAdmin(admin.ModelAdmin):
    list_display = ["entry_date", "entry_type", "label", "amount", "appointment", "created_by"]
    list_filter = ["entry_type", "entry_date"]
    search_fields = ["label", "notes", "appointment__full_name"]
    raw_id_fields = ["appointment", "created_by"]
