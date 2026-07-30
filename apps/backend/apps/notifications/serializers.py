from __future__ import annotations

from rest_framework import serializers

from apps.notifications.models import NotificationCampaign, NotificationMessageLog, NotificationRecipient


class NotificationRecipientSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationRecipient
        fields = ["id", "campaign", "contact", "user", "display_name", "email", "phone", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at"]


class NotificationMessageLogSerializer(serializers.ModelSerializer):
    campaign_title = serializers.CharField(source="campaign.title", read_only=True)
    campaign_subject = serializers.CharField(source="campaign.subject", read_only=True)
    campaign_body = serializers.CharField(source="campaign.body", read_only=True)
    recipient_display_name = serializers.CharField(source="recipient.display_name", read_only=True)

    class Meta:
        model = NotificationMessageLog
        fields = [
            "id",
            "campaign",
            "campaign_title",
            "campaign_subject",
            "campaign_body",
            "recipient",
            "recipient_display_name",
            "contact",
            "user",
            "channel",
            "recipient_address",
            "status",
            "error",
            "sent_at",
            "opened_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class NotificationCampaignSerializer(serializers.ModelSerializer):
    recipient_count = serializers.IntegerField(source="recipients.count", read_only=True)
    message_log_count = serializers.IntegerField(source="message_logs.count", read_only=True)
    created_by_email = serializers.EmailField(source="created_by.email", read_only=True)

    class Meta:
        model = NotificationCampaign
        fields = [
            "id",
            "title",
            "subject",
            "body",
            "status",
            "target_status",
            "marketing_consent_only",
            "include_customers",
            "scheduled_at",
            "sent_at",
            "created_by",
            "created_by_email",
            "recipient_count",
            "message_log_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_by", "created_by_email", "recipient_count", "message_log_count", "sent_at", "created_at", "updated_at"]
        extra_kwargs = {
            "target_status": {"required": False, "allow_null": True},
            "scheduled_at": {"required": False, "allow_null": True},
        }


class NotificationCampaignSendResultSerializer(serializers.Serializer):
    campaign = serializers.IntegerField()
    recipients = serializers.IntegerField()
    email_sent = serializers.IntegerField()
    email_skipped = serializers.IntegerField()
    email_failed = serializers.IntegerField()
    push_pending = serializers.IntegerField()
    push_skipped = serializers.IntegerField()
