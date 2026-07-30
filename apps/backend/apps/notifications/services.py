from __future__ import annotations

from dataclasses import dataclass

from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from apps.accounts.models import CustomerNotificationSubscription, CustomerProfile
from apps.contacts.models import Contact
from apps.notifications.models import NotificationCampaign, NotificationMessageLog, NotificationRecipient


@dataclass(frozen=True)
class RecipientPreview:
    contact_id: int | None
    user_id: int | None
    display_name: str
    email: str
    phone: str


def preview_recipients(campaign: NotificationCampaign, limit: int = 250) -> list[RecipientPreview]:
    contacts = Contact.objects.filter(is_merged=False)
    if campaign.target_status_id:
        contacts = contacts.filter(status_id=campaign.target_status_id)
    if campaign.marketing_consent_only:
        contacts = contacts.filter(marketing_consent=True)
    contacts = list(contacts.order_by("full_name", "email", "phone", "id")[:limit])

    customer_by_contact = {}
    if campaign.include_customers:
        profiles = CustomerProfile.objects.select_related("user", "contact").filter(contact__in=contacts, user__is_active=True)
        customer_by_contact = {profile.contact_id: profile.user for profile in profiles}

    previews: list[RecipientPreview] = []
    seen: set[tuple[int | None, int | None]] = set()
    for contact in contacts:
        user = customer_by_contact.get(contact.pk)
        key = (contact.pk, user.pk if user else None)
        if key in seen:
            continue
        seen.add(key)
        previews.append(
            RecipientPreview(
                contact_id=contact.pk,
                user_id=user.pk if user else None,
                display_name=contact.display_name,
                email=contact.email or (user.email if user else ""),
                phone=contact.phone,
            )
        )
    return previews


@transaction.atomic
def send_notification_campaign(campaign: NotificationCampaign) -> dict[str, int]:
    recipients = ensure_campaign_recipients(campaign)
    totals = {
        "campaign": campaign.pk,
        "recipients": len(recipients),
        "email_sent": 0,
        "email_skipped": 0,
        "email_failed": 0,
        "push_pending": 0,
        "push_skipped": 0,
    }
    for recipient in recipients:
        email_log = send_campaign_email(campaign, recipient)
        if email_log.status == NotificationMessageLog.Status.SENT:
            totals["email_sent"] += 1
        elif email_log.status == NotificationMessageLog.Status.FAILED:
            totals["email_failed"] += 1
        else:
            totals["email_skipped"] += 1

        for push_log in log_campaign_push_foundation(campaign, recipient):
            if push_log.status == NotificationMessageLog.Status.PENDING:
                totals["push_pending"] += 1
            else:
                totals["push_skipped"] += 1

    campaign.status = NotificationCampaign.Status.SENT
    campaign.sent_at = timezone.now()
    campaign.save(update_fields=["status", "sent_at", "updated_at"])
    return totals


def ensure_campaign_recipients(campaign: NotificationCampaign) -> list[NotificationRecipient]:
    existing = list(campaign.recipients.select_related("contact", "user"))
    if existing:
        return existing
    recipients: list[NotificationRecipient] = []
    for preview in preview_recipients(campaign, limit=10000):
        recipients.append(
            NotificationRecipient.objects.create(
                campaign=campaign,
                contact_id=preview.contact_id,
                user_id=preview.user_id,
                display_name=preview.display_name,
                email=preview.email,
                phone=preview.phone,
            )
        )
    return recipients


def send_campaign_email(campaign: NotificationCampaign, recipient: NotificationRecipient) -> NotificationMessageLog:
    if not recipient.email:
        return create_message_log(
            campaign,
            recipient,
            NotificationMessageLog.Channel.EMAIL,
            "",
            NotificationMessageLog.Status.SKIPPED,
            "No email recipient is available.",
        )
    try:
        send_mail(campaign.subject, campaign.body, getattr(settings, "DEFAULT_FROM_EMAIL", ""), [recipient.email], fail_silently=False)
    except Exception as exc:  # pragma: no cover - depends on provider failures.
        return create_message_log(
            campaign,
            recipient,
            NotificationMessageLog.Channel.EMAIL,
            recipient.email,
            NotificationMessageLog.Status.FAILED,
            str(exc),
        )
    return create_message_log(
        campaign,
        recipient,
        NotificationMessageLog.Channel.EMAIL,
        recipient.email,
        NotificationMessageLog.Status.SENT,
        "",
        sent_at=timezone.now(),
    )


def log_campaign_push_foundation(campaign: NotificationCampaign, recipient: NotificationRecipient) -> list[NotificationMessageLog]:
    filters = Q()
    if recipient.user_id:
        filters |= Q(user_id=recipient.user_id)
    if recipient.contact_id:
        filters |= Q(contact_id=recipient.contact_id)
    if not filters:
        return [
            create_message_log(
                campaign,
                recipient,
                NotificationMessageLog.Channel.EXPO,
                "",
                NotificationMessageLog.Status.SKIPPED,
                "No customer notification subscription is available.",
            )
        ]

    subscriptions = CustomerNotificationSubscription.objects.filter(filters, enabled=True).distinct()
    logs: list[NotificationMessageLog] = []
    for channel in [NotificationMessageLog.Channel.EXPO, NotificationMessageLog.Channel.WEB_PUSH]:
        channel_subscriptions = subscriptions.filter(channel=channel)
        if not channel_subscriptions.exists():
            logs.append(create_message_log(campaign, recipient, channel, "", NotificationMessageLog.Status.SKIPPED, "No enabled subscription is available."))
            continue
        has_credentials = push_credentials_configured(channel)
        for subscription in channel_subscriptions:
            address = subscription.token if channel == NotificationMessageLog.Channel.EXPO else subscription.subscription_endpoint
            logs.append(
                create_message_log(
                    campaign,
                    recipient,
                    channel,
                    address,
                    NotificationMessageLog.Status.PENDING if has_credentials else NotificationMessageLog.Status.SKIPPED,
                    "Push delivery is pending implementation." if has_credentials else push_missing_credentials_message(channel),
                )
            )
    return logs


def push_credentials_configured(channel: str) -> bool:
    if channel == NotificationMessageLog.Channel.EXPO:
        return bool(getattr(settings, "EXPO_PUSH_ACCESS_TOKEN", ""))
    return bool(getattr(settings, "WEB_PUSH_PUBLIC_KEY", "") and getattr(settings, "WEB_PUSH_PRIVATE_KEY", ""))


def push_missing_credentials_message(channel: str) -> str:
    if channel == NotificationMessageLog.Channel.EXPO:
        return "EXPO_PUSH_ACCESS_TOKEN is not configured."
    return "WEB_PUSH_PUBLIC_KEY and WEB_PUSH_PRIVATE_KEY are not configured."


def create_message_log(
    campaign: NotificationCampaign,
    recipient: NotificationRecipient,
    channel: str,
    recipient_address: str,
    status: str,
    error: str = "",
    *,
    sent_at=None,
) -> NotificationMessageLog:
    return NotificationMessageLog.objects.create(
        campaign=campaign,
        recipient=recipient,
        contact=recipient.contact,
        user=recipient.user,
        channel=channel,
        recipient_address=recipient_address,
        status=status,
        error=error,
        sent_at=sent_at,
    )
