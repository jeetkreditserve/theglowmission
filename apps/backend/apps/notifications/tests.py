from __future__ import annotations

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.accounts.models import CustomerProfile
from apps.contacts.models import Contact
from apps.contacts.services import ensure_default_contact_statuses
from apps.notifications.models import NotificationCampaign, NotificationMessageLog, NotificationRecipient


@override_settings(
    ALLOWED_HOSTS=["testserver"],
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    EXPO_PUSH_ACCESS_TOKEN="",
    WEB_PUSH_PUBLIC_KEY="",
    WEB_PUSH_PRIVATE_KEY="",
)
class NotificationCampaignApiTests(TestCase):
    def setUp(self):
        self.status = ensure_default_contact_statuses()
        self.admin = get_user_model().objects.create_superuser("admin", "admin@example.com", "password")
        self.customer = get_user_model().objects.create_user("asha", "asha@example.com", "StrongPass123!")
        self.contact = Contact.objects.create(
            full_name="Asha Rao",
            email="asha@example.com",
            normalized_email="asha@example.com",
            phone="9876543210",
            normalized_phone="9876543210",
            status=self.status,
            marketing_consent=True,
        )
        CustomerProfile.objects.create(user=self.customer, contact=self.contact, phone="9876543210")
        self.client = APIClient()
        self.client.force_authenticate(self.admin)

    def test_admin_can_preview_send_and_customer_can_read_inbox(self):
        create_response = self.client.post(
            "/api/v1/admin/notification-campaigns/",
            {
                "title": "July Ritual Reminder",
                "subject": "Your glow ritual",
                "body": "A new ritual slot is open.",
                "target_status": self.status.pk,
                "marketing_consent_only": True,
                "include_customers": True,
            },
            format="json",
        )
        self.assertEqual(create_response.status_code, 201)
        campaign_id = create_response.data["id"]

        preview_response = self.client.get(f"/api/v1/admin/notification-campaigns/{campaign_id}/recipients/preview/")
        send_response = self.client.post(f"/api/v1/admin/notification-campaigns/{campaign_id}/send/", {}, format="json")

        self.assertEqual(preview_response.status_code, 200)
        self.assertEqual(preview_response.data["count"], 1)
        self.assertEqual(send_response.status_code, 200)
        self.assertEqual(send_response.data["recipients"], 1)
        self.assertEqual(send_response.data["email_sent"], 1)
        self.assertEqual(send_response.data["push_skipped"], 2)
        self.assertEqual(NotificationRecipient.objects.count(), 1)
        self.assertEqual(NotificationMessageLog.objects.count(), 3)
        self.assertEqual(NotificationCampaign.objects.get().status, NotificationCampaign.Status.SENT)
        self.assertEqual(len(mail.outbox), 1)

        customer_client = APIClient()
        customer_client.force_authenticate(self.customer)
        inbox_response = customer_client.get("/api/v1/auth/customer/notifications/")

        self.assertEqual(inbox_response.status_code, 200)
        self.assertEqual(len(inbox_response.data), 3)
        self.assertEqual(inbox_response.data[0]["campaign_title"], "July Ritual Reminder")
