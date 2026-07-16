from __future__ import annotations

from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.campaigns.models import CampaignForm, CampaignFormResponse
from apps.contacts.models import Contact
from apps.content.models import Service


@override_settings(ALLOWED_HOSTS=["testserver"])
class RitualBookingLeadTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.form = CampaignForm.objects.create(title="Glow Consultation", slug="glow-consultation", status=CampaignForm.Status.PUBLISHED)
        self.service = Service.objects.create(
            title="The Glow Cleanse",
            slug="the-glow-cleanse",
            short_description="A comforting reset.",
            duration="60 MINS",
            cta_url="/campaigns/glow-consultation",
            calendly_event_url="https://calendly.com/theglowmission-info/the-glow-cleanse-01-hour",
            booking_campaign=self.form,
            active=True,
        )

    def test_booking_lead_creates_campaign_response_and_contact_without_email(self):
        response = self.client.post(
            f"/api/v1/public/services/{self.service.slug}/booking-leads/",
            {"full_name": "Asha Rao", "phone": "9876543210", "email": "", "skin_goal": "Glow"},
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(CampaignFormResponse.objects.count(), 1)
        contact = Contact.objects.get()
        self.assertEqual(contact.full_name, "Asha Rao")
        self.assertEqual(contact.phone, "9876543210")
        self.assertEqual(contact.preferred_ritual, "The Glow Cleanse")

    def test_booking_lead_requires_phone(self):
        response = self.client.post(
            f"/api/v1/public/services/{self.service.slug}/booking-leads/",
            {"full_name": "Asha Rao", "phone": "", "email": ""},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("phone", response.data)
