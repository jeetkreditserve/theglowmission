from __future__ import annotations

from io import BytesIO

from django.test import TestCase
from openpyxl import load_workbook

from apps.campaigns.exports import build_campaign_responses_workbook
from apps.campaigns.models import CampaignForm, CampaignFormField, CampaignFormResponse
from apps.campaigns.serializers import CampaignFormResponseSerializer, PublicCampaignResponseSerializer


class CampaignResponseValidationTests(TestCase):
    def setUp(self):
        self.form = CampaignForm.objects.create(
            title="Validation campaign",
            slug="validation-campaign",
            status=CampaignForm.Status.PUBLISHED,
        )

    def create_field(self, key: str, field_type: str, **kwargs) -> CampaignFormField:
        return CampaignFormField.objects.create(
            form=self.form,
            label=kwargs.pop("label", key.replace("_", " ").title()),
            key=key,
            field_type=field_type,
            ordering=self.form.fields.count(),
            **kwargs,
        )

    def validate_payload(self, payload: dict) -> PublicCampaignResponseSerializer:
        serializer = PublicCampaignResponseSerializer(data={"response_data": payload}, context={"form": self.form})
        serializer.is_valid()
        return serializer

    def field_errors_for(self, payload: dict):
        serializer = self.validate_payload(payload)
        self.assertFalse(serializer.is_valid())
        return serializer.errors["response_data"]

    def test_required_field_is_enforced(self):
        self.create_field("full_name", CampaignFormField.FieldType.TEXT, required=True)

        errors = self.field_errors_for({"full_name": ""})

        self.assertIn("full_name", errors)

    def test_email_field_must_be_valid(self):
        self.create_field("email", CampaignFormField.FieldType.EMAIL, required=True)

        errors = self.field_errors_for({"email": "not-an-email"})
        valid_serializer = self.validate_payload({"email": "client@example.com"})
        missing_serializer = self.validate_payload({"email": ""})

        self.assertIn("email", errors)
        self.assertTrue(valid_serializer.is_valid(), valid_serializer.errors)
        self.assertTrue(missing_serializer.is_valid(), missing_serializer.errors)

    def test_phone_field_rejects_non_digits_and_requires_ten_digits(self):
        self.create_field("phone", CampaignFormField.FieldType.PHONE, required=True)

        non_digit_errors = self.field_errors_for({"phone": "98765abc10"})
        short_errors = self.field_errors_for({"phone": "98765"})
        valid_serializer = self.validate_payload({"phone": "9876543210"})

        self.assertEqual(str(non_digit_errors["phone"]), "Phone number can contain digits only.")
        self.assertEqual(str(short_errors["phone"]), "Enter a 10-digit phone number.")
        self.assertTrue(valid_serializer.is_valid(), valid_serializer.errors)
        self.assertEqual(valid_serializer.validated_data["response_data"]["phone"], "9876543210")

    def test_phone_key_is_required_even_if_field_is_configured_optional(self):
        self.create_field("phone", CampaignFormField.FieldType.PHONE, required=False)

        errors = self.field_errors_for({"phone": ""})

        self.assertIn("phone", errors)

    def test_number_min_max_is_enforced(self):
        self.create_field("age", CampaignFormField.FieldType.NUMBER, required=True, validation={"min": 18, "max": 80})

        low_errors = self.field_errors_for({"age": "12"})
        high_errors = self.field_errors_for({"age": "100"})
        valid_serializer = self.validate_payload({"age": "35"})

        self.assertIn("age", low_errors)
        self.assertIn("age", high_errors)
        self.assertTrue(valid_serializer.is_valid(), valid_serializer.errors)

    def test_select_radio_date_and_required_checkbox_are_enforced(self):
        self.create_field("skin_type", CampaignFormField.FieldType.SELECT, required=True, options=["Dry", "Oily"])
        self.create_field("visit_day", CampaignFormField.FieldType.DATE, required=True)
        self.create_field("consent", CampaignFormField.FieldType.CHECKBOX, required=True)

        errors = self.field_errors_for({"skin_type": "Normal", "visit_day": "not-a-date", "consent": False})
        valid_serializer = self.validate_payload({"skin_type": "Dry", "visit_day": "2026-06-21", "consent": True})

        self.assertIn("skin_type", errors)
        self.assertIn("visit_day", errors)
        self.assertIn("consent", errors)
        self.assertTrue(valid_serializer.is_valid(), valid_serializer.errors)


class CampaignExportWorkbookTests(TestCase):
    def test_workbook_is_branded_and_formatted(self):
        form = CampaignForm.objects.create(
            title="Complimentary Facial Session",
            slug="complimentary-facial-session",
            status=CampaignForm.Status.PUBLISHED,
        )
        CampaignFormField.objects.create(form=form, label="Full name", key="full_name", field_type=CampaignFormField.FieldType.TEXT, ordering=0)
        CampaignFormField.objects.create(form=form, label="Phone", key="phone", field_type=CampaignFormField.FieldType.PHONE, ordering=1)
        CampaignFormResponse.objects.create(form=form, response_data={"full_name": "Asha Rao", "phone": "9876543210"})

        workbook = build_campaign_responses_workbook(form)
        output = BytesIO()
        workbook.save(output)
        output.seek(0)
        loaded = load_workbook(output)
        sheet = loaded["Responses"]

        self.assertEqual(sheet["A1"].value, "The Glow Mission")
        self.assertEqual(sheet["A2"].value, "Complimentary Facial Session responses")
        self.assertEqual(sheet["A6"].value, "Submitted At")
        self.assertEqual(sheet["C6"].value, "Full name")
        self.assertEqual(sheet["C7"].value, "Asha Rao")
        self.assertEqual(sheet.freeze_panes, "B7")
        self.assertEqual(sheet.auto_filter.ref, "A6:D7")
        self.assertGreaterEqual(sheet.column_dimensions["C"].width, len("Full name"))


class CampaignResponseSerializerTests(TestCase):
    def test_admin_response_includes_campaign_metadata(self):
        form = CampaignForm.objects.create(
            title="Complimentary Facial Session",
            slug="complimentary-facial-session",
            status=CampaignForm.Status.PUBLISHED,
        )
        response = CampaignFormResponse.objects.create(form=form, response_data={"email": "client@example.com"})

        data = CampaignFormResponseSerializer(response).data

        self.assertEqual(data["form_title"], "Complimentary Facial Session")
        self.assertEqual(data["form_slug"], "complimentary-facial-session")
