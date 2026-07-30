from django.contrib import admin

from apps.notifications.models import NotificationCampaign, NotificationMessageLog, NotificationRecipient


@admin.register(NotificationCampaign)
class NotificationCampaignAdmin(admin.ModelAdmin):
    list_display = ["title", "status", "target_status", "marketing_consent_only", "sent_at", "updated_at"]
    search_fields = ["title", "subject", "body"]
    list_filter = ["status", "marketing_consent_only", "target_status"]


@admin.register(NotificationRecipient)
class NotificationRecipientAdmin(admin.ModelAdmin):
    list_display = ["campaign", "display_name", "email", "contact", "user"]
    search_fields = ["display_name", "email", "phone"]
    list_filter = ["campaign"]


@admin.register(NotificationMessageLog)
class NotificationMessageLogAdmin(admin.ModelAdmin):
    list_display = ["campaign", "channel", "status", "recipient_address", "sent_at", "created_at"]
    search_fields = ["campaign__title", "recipient_address", "error"]
    list_filter = ["channel", "status"]
