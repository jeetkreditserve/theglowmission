from __future__ import annotations

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.accounts.models import CustomerNotificationSubscription, CustomerProfile
from apps.accounts.services import build_password_reset_payload
from apps.contacts.models import Contact
from apps.contacts.services import ensure_default_contact_statuses


@override_settings(
    ALLOWED_HOSTS=["testserver"],
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    CUSTOMER_PASSWORD_RESET_EXPOSE_TOKEN=True,
)
class CustomerEmailAuthTests(TestCase):
    def setUp(self):
        ensure_default_contact_statuses()
        self.client = APIClient()

    def test_customer_register_creates_user_profile_contact_and_role(self):
        response = self.client.post(
            "/api/v1/auth/customer/register/",
            {
                "email": "asha@example.com",
                "password": "StrongPass123!",
                "full_name": "Asha Rao",
                "phone": "9876543210",
                "marketing_consent": True,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertIn("token", response.data)
        user = response.data["user"]
        self.assertEqual(user["email"], "asha@example.com")
        self.assertEqual(user["roles"], ["customer"])
        self.assertEqual(user["account_type"], "customer")
        self.assertEqual(user["phone"], "9876543210")
        self.assertIsNotNone(user["contact"])
        profile = CustomerProfile.objects.get()
        self.assertEqual(profile.contact_id, user["contact"])
        contact = Contact.objects.get()
        self.assertEqual(contact.email, "asha@example.com")
        self.assertEqual(contact.phone, "9876543210")
        self.assertTrue(contact.marketing_consent)

    def test_register_rejects_duplicate_email(self):
        get_user_model().objects.create_user("asha", "asha@example.com", "StrongPass123!")

        response = self.client.post(
            "/api/v1/auth/customer/register/",
            {"email": "asha@example.com", "password": "StrongPass123!"},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("email", response.data)

    def test_customer_login_rejects_staff_account(self):
        get_user_model().objects.create_superuser("admin", "admin@example.com", "StrongPass123!")

        response = self.client.post(
            "/api/v1/auth/customer/login/",
            {"email": "admin@example.com", "password": "StrongPass123!"},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("email", response.data)

    def test_customer_login_links_existing_customer(self):
        user = get_user_model().objects.create_user("asha", "asha@example.com", "StrongPass123!")
        contact = Contact.objects.create(full_name="Asha Rao", email="asha@example.com", phone="9876543210")
        profile = CustomerProfile.objects.create(user=user, contact=contact, phone="9876543210")

        response = self.client.post(
            "/api/v1/auth/customer/login/",
            {"email": "asha@example.com", "password": "StrongPass123!"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["user"]["contact"], contact.pk)
        self.assertEqual(CustomerProfile.objects.get(pk=profile.pk).contact_id, contact.pk)

    def test_password_reset_request_sends_non_enumerating_email(self):
        user = get_user_model().objects.create_user("asha", "asha@example.com", "StrongPass123!")

        response = self.client.post("/api/v1/auth/customer/password-reset/request/", {"email": user.email}, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.data)
        self.assertIn("token", response.data)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(response.data["token"], mail.outbox[0].body)

    def test_password_reset_confirm_changes_password_and_returns_session(self):
        user = get_user_model().objects.create_user("asha", "asha@example.com", "StrongPass123!")
        uid, token, _ = build_password_reset_payload(user)

        response = self.client.post(
            "/api/v1/auth/customer/password-reset/confirm/",
            {"uid": uid, "token": token, "password": "NewStrongPass123!"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("token", response.data)
        self.assertTrue(get_user_model().objects.get(pk=user.pk).check_password("NewStrongPass123!"))


@override_settings(ALLOWED_HOSTS=["testserver"])
class CustomerProfileAndDeviceTests(TestCase):
    def setUp(self):
        ensure_default_contact_statuses()
        self.client = APIClient()
        response = self.client.post(
            "/api/v1/auth/customer/register/",
            {
                "email": "asha@example.com",
                "password": "StrongPass123!",
                "full_name": "Asha Rao",
                "phone": "9876543210",
            },
            format="json",
        )
        self.token = response.data["token"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token}")

    def test_customer_profile_get_and_patch_updates_contact(self):
        get_response = self.client.get("/api/v1/auth/customer/profile/")
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(get_response.data["phone"], "9876543210")

        patch_response = self.client.patch(
            "/api/v1/auth/customer/profile/",
            {"skin_goal": "Hydration", "preferred_day": "Saturday", "marketing_consent": True},
            format="json",
        )

        self.assertEqual(patch_response.status_code, 200)
        self.assertEqual(patch_response.data["skin_goal"], "Hydration")
        contact = Contact.objects.get(pk=patch_response.data["contact"])
        self.assertEqual(contact.preferred_day, "Saturday")
        self.assertTrue(contact.marketing_consent)

    def test_register_expo_notification_device(self):
        response = self.client.post(
            "/api/v1/auth/customer/devices/",
            {
                "channel": "expo",
                "platform": "ios",
                "device_id": "device-1",
                "device_name": "iPhone",
                "app_version": "0.1.0",
                "token": "ExponentPushToken[test]",
                "permission_status": "granted",
                "metadata": {"source": "profile"},
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(CustomerNotificationSubscription.objects.get().token, "ExponentPushToken[test]")


@override_settings(ALLOWED_HOSTS=["testserver"])
class ExistingStaffAuthTests(TestCase):
    def test_staff_login_response_includes_role_fields(self):
        get_user_model().objects.create_superuser("admin", "admin@example.com", "StrongPass123!")
        client = APIClient()

        response = client.post("/api/v1/auth/login/", {"email": "admin@example.com", "password": "StrongPass123!"}, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertIn("token", response.data)
        self.assertEqual(response.data["user"]["account_type"], "superuser")
        self.assertIn("superuser", response.data["user"]["roles"])
        self.assertIn("staff", response.data["user"]["roles"])

    def test_password_login_rejects_non_staff_accounts(self):
        get_user_model().objects.create_user("client", "client@example.com", "StrongPass123!")
        client = APIClient()

        response = client.post("/api/v1/auth/login/", {"email": "client@example.com", "password": "StrongPass123!"}, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertIn("staff access", str(response.data))
