from __future__ import annotations

from datetime import timedelta
from io import BytesIO

from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from openpyxl import load_workbook
from rest_framework.test import APIClient

from apps.campaigns.models import CampaignForm, CampaignFormField, CampaignFormResponse
from apps.campaigns.serializers import PublicCampaignResponseSerializer
from apps.contacts.exports import build_contacts_workbook
from apps.contacts.models import Contact, ContactAuditEvent, ContactStatus
from apps.contacts.services import ensure_default_contact_statuses
from apps.contacts.views import merge_contact_values


class ContactIngestionTests(TestCase):
    def setUp(self):
        ensure_default_contact_statuses()
        self.form = CampaignForm.objects.create(
            title="Lead form",
            slug="lead-form",
            status=CampaignForm.Status.PUBLISHED,
        )
        CampaignFormField.objects.create(form=self.form, label="Full name", key="full_name", field_type=CampaignFormField.FieldType.TEXT, ordering=0)
        CampaignFormField.objects.create(form=self.form, label="Email", key="email", field_type=CampaignFormField.FieldType.EMAIL, ordering=1)
        CampaignFormField.objects.create(form=self.form, label="Phone", key="phone", field_type=CampaignFormField.FieldType.PHONE, ordering=2)
        CampaignFormField.objects.create(form=self.form, label="Address", key="address", field_type=CampaignFormField.FieldType.TEXTAREA, ordering=3)
        CampaignFormField.objects.create(form=self.form, label="Age", key="age", field_type=CampaignFormField.FieldType.NUMBER, ordering=4)
        CampaignFormField.objects.create(form=self.form, label="Skin type", key="skin_type", field_type=CampaignFormField.FieldType.TEXT, ordering=5)
        CampaignFormField.objects.create(form=self.form, label="Marketing consent", key="marketing_consent", field_type=CampaignFormField.FieldType.CHECKBOX, ordering=6)

    def submit(self, payload):
        serializer = PublicCampaignResponseSerializer(data={"response_data": payload}, context={"form": self.form})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        return serializer.save()

    def test_new_response_creates_contact(self):
        response = self.submit(
            {
                "full_name": "Asha Rao",
                "email": "ASHA@example.COM",
                "phone": "9876543210",
                "address": "Powai",
                "age": "34",
                "skin_type": "Dry",
                "marketing_consent": True,
            }
        )

        contact = response.contact
        self.assertIsNotNone(contact)
        self.assertEqual(contact.full_name, "Asha Rao")
        self.assertEqual(contact.email, "asha@example.com")
        self.assertEqual(contact.phone, "9876543210")
        self.assertEqual(contact.age, 34)
        self.assertTrue(contact.marketing_consent)
        self.assertEqual(contact.status.slug, "lead")
        self.assertEqual(response.contact_sync_status, "synced")
        self.assertEqual(contact.audit_events.filter(event_type=ContactAuditEvent.EventType.CREATED).count(), 1)

    def test_matching_updates_latest_non_empty_values_and_ignores_blanks(self):
        first = self.submit(
            {
                "full_name": "Asha Rao",
                "email": "asha@example.com",
                "phone": "9876543210",
                "address": "Powai",
                "marketing_consent": True,
            }
        )
        second = self.submit(
            {
                "full_name": "Asha R.",
                "email": "asha@example.com",
                "phone": "9876543210",
                "address": "",
                "marketing_consent": False,
            }
        )

        contact = Contact.objects.get(pk=first.contact_id)
        self.assertEqual(second.contact_id, contact.pk)
        self.assertEqual(contact.full_name, "Asha R.")
        self.assertEqual(contact.phone, "9876543210")
        self.assertEqual(contact.address, "Powai")
        self.assertFalse(contact.marketing_consent)
        self.assertTrue(contact.audit_events.filter(field_name="full_name", old_value="Asha Rao", new_value="Asha R.").exists())
        self.assertTrue(contact.audit_events.filter(field_name="marketing_consent").exists())

    def test_email_wins_when_phone_matches_another_contact(self):
        email_contact = self.submit({"full_name": "Email Owner", "email": "email@example.com", "phone": "9876543210"}).contact
        phone_contact = self.submit({"full_name": "Phone Owner", "email": "phone@example.com", "phone": "9876543211"}).contact

        response = self.submit({"full_name": "Conflict", "email": "email@example.com", "phone": "9876543211"})
        email_contact.refresh_from_db()
        phone_contact.refresh_from_db()

        self.assertEqual(response.contact_id, email_contact.pk)
        self.assertEqual(response.contact_sync_status, "conflict")
        self.assertIn(str(phone_contact.pk), response.contact_sync_error)
        self.assertEqual(email_contact.phone, "9876543210")

    def test_response_without_phone_is_rejected(self):
        serializer = PublicCampaignResponseSerializer(data={"response_data": {"marketing_consent": True}}, context={"form": self.form})

        self.assertFalse(serializer.is_valid())
        self.assertIn("phone", serializer.errors["response_data"])
        self.assertEqual(Contact.objects.count(), 0)


class ContactStatusTests(TestCase):
    def test_status_with_contacts_cannot_be_deleted_directly(self):
        status = ensure_default_contact_statuses()
        Contact.objects.create(full_name="Asha", email="asha@example.com", normalized_email="asha@example.com", status=status)

        with self.assertRaises(ValidationError):
            status.delete()


@override_settings(ALLOWED_HOSTS=["testserver"])
class ContactAdminApiTests(TestCase):
    def setUp(self):
        self.status = ensure_default_contact_statuses()
        self.user = get_user_model().objects.create_superuser("admin", "admin@example.com", "password")
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_contact_list_and_detail_load_with_possible_duplicate_fields(self):
        form = CampaignForm.objects.create(title="Lead form", slug="lead-form", status=CampaignForm.Status.PUBLISHED)
        contact = Contact.objects.create(full_name="Asha Rao", phone="9876543210", normalized_phone="9876543210", status=self.status)
        CampaignFormResponse.objects.create(form=form, contact=contact, response_data={"full_name": "Asha Rao", "phone": "9876543210"})

        list_response = self.client.get("/api/v1/admin/contacts/")
        detail_response = self.client.get(f"/api/v1/admin/contacts/{contact.pk}/")

        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(detail_response.status_code, 200)
        self.assertEqual(list_response.data[0]["id"], contact.pk)
        self.assertEqual(detail_response.data["possible_duplicate_count"], 0)

    def test_new_manual_contact_requires_phone(self):
        response = self.client.post("/api/v1/admin/contacts/", {"full_name": "Asha Rao", "email": "asha@example.com"}, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertIn("phone", response.data)

    def test_existing_email_only_contact_can_still_be_edited(self):
        contact = Contact.objects.create(full_name="Email Only", email="client@example.com", normalized_email="client@example.com", status=self.status)

        response = self.client.patch(f"/api/v1/admin/contacts/{contact.pk}/", {"full_name": "Updated Name"}, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["full_name"], "Updated Name")


class ContactMergeTests(TestCase):
    def test_merge_uses_latest_non_empty_values(self):
        status = ensure_default_contact_statuses()
        target = Contact.objects.create(full_name="Old Name", email="old@example.com", normalized_email="old@example.com", status=status)
        source = Contact.objects.create(full_name="New Name", phone="9876543210", normalized_phone="9876543210", status=status)
        source.mark_merged_into(target)
        source.updated_at = target.updated_at + timedelta(days=1)

        changed_fields = merge_contact_values(target, source)
        target.refresh_from_db()

        self.assertIn("full_name", changed_fields)
        self.assertIn("phone", changed_fields)
        self.assertEqual(target.full_name, "New Name")
        self.assertEqual(target.phone, "9876543210")


class ContactExportTests(TestCase):
    def test_contacts_export_contains_current_fields(self):
        status = ensure_default_contact_statuses()
        Contact.objects.create(
            full_name="Asha Rao",
            email="asha@example.com",
            normalized_email="asha@example.com",
            phone="9876543210",
            normalized_phone="9876543210",
            status=status,
            marketing_consent=True,
            source_response_count=2,
        )

        workbook = build_contacts_workbook(Contact.objects.select_related("status").all())
        output = BytesIO()
        workbook.save(output)
        output.seek(0)
        sheet = load_workbook(output)["Contacts"]

        self.assertEqual(sheet["A1"].value, "The Glow Mission")
        self.assertEqual(sheet["A2"].value, "Contacts export")
        self.assertEqual(sheet["C6"].value, "Full name")
        self.assertEqual(sheet["C7"].value, "Asha Rao")
        self.assertEqual(sheet["L7"].value, "Yes")
