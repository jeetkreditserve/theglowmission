from __future__ import annotations

from datetime import datetime, time, timedelta
from io import StringIO
from tempfile import TemporaryDirectory

from django.contrib.auth import get_user_model
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework.test import APIClient

from apps.appointments.models import Appointment, AppointmentAvailabilityWindow, AppointmentFinanceEntry, AppointmentNotificationLog, AppointmentPhoto
from apps.campaigns.models import CampaignForm, CampaignFormResponse
from apps.contacts.models import Contact
from apps.contacts.services import ensure_default_contact_statuses
from apps.content.models import Service


def local_dt(day, hour: int, minute: int = 0):
    return timezone.make_aware(datetime.combine(day, time(hour, minute)), timezone.get_current_timezone())


def next_weekday(weekday: int):
    day = timezone.localdate() + timedelta(days=1)
    while day.weekday() != weekday:
        day += timedelta(days=1)
    return day


@override_settings(
    ALLOWED_HOSTS=["testserver"],
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    FIRST_PARTY_SCHEDULING_ENABLED=True,
    CALENDLY_BOOKING_FALLBACK_ENABLED=False,
    APPOINTMENT_MIN_LEAD_MINUTES=0,
    APPOINTMENT_DOWNTIME_MINUTES=15,
    APPOINTMENT_CUSTOMER_CHANGE_CUTOFF_MINUTES=0,
    APPOINTMENT_REMINDER_MINUTES=[1440, 120],
)
class AppointmentSchedulingApiTests(TestCase):
    def setUp(self):
        ensure_default_contact_statuses()
        self.client = APIClient()
        self.form = CampaignForm.objects.create(title="Glow Consultation", slug="glow-consultation", status=CampaignForm.Status.PUBLISHED)
        self.service = Service.objects.create(
            title="The Glow Cleanse",
            slug="the-glow-cleanse",
            short_description="A comforting reset.",
            duration="60 MINS",
            duration_minutes=60,
            booking_buffer_minutes=0,
            accepts_online_booking=True,
            calendly_fallback_enabled=True,
            booking_campaign=self.form,
            active=True,
        )
        self.day = timezone.localdate() + timedelta(days=1)
        AppointmentAvailabilityWindow.objects.create(weekday=self.day.weekday(), starts_at=time(10, 0), ends_at=time(13, 0), active=True)

    def test_public_available_slots_returns_service_slots(self):
        response = self.client.get(f"/api/v1/public/services/{self.service.slug}/available-slots/", {"date": self.day.isoformat()})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        self.assertIn("starts_at", response.data[0])
        self.assertIn("ends_at", response.data[0])

    def test_slots_and_public_create_respect_confirmed_appointment_downtime(self):
        Appointment.objects.create(
            service=self.service,
            full_name="Existing Client",
            phone="9876543211",
            starts_at=local_dt(self.day, 10),
            ends_at=local_dt(self.day, 11),
            duration_minutes=60,
            status=Appointment.Status.CONFIRMED,
            source=Appointment.Source.ADMIN,
        )

        slots = self.client.get(f"/api/v1/public/services/{self.service.slug}/available-slots/", {"date": self.day.isoformat()})
        create_response = self.client.post(
            f"/api/v1/public/services/{self.service.slug}/appointments/",
            {
                "starts_at": local_dt(self.day, 11).isoformat(),
                "full_name": "Asha Rao",
                "phone": "9876543210",
            },
            format="json",
        )

        self.assertEqual(slots.status_code, 200)
        self.assertEqual(len(slots.data), 1)
        self.assertIn("11:15", slots.data[0]["starts_at"])
        self.assertEqual(create_response.status_code, 400)
        self.assertEqual(Appointment.objects.count(), 1)

    def test_public_appointment_creation_syncs_contact_and_campaign_response(self):
        response = self.client.post(
            f"/api/v1/public/services/{self.service.slug}/appointments/",
            {
                "starts_at": local_dt(self.day, 10).isoformat(),
                "full_name": "Asha Rao",
                "phone": "9876543210",
                "email": "asha@example.com",
                "skin_goal": "Hydration",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Appointment.objects.count(), 1)
        self.assertEqual(CampaignFormResponse.objects.count(), 1)
        contact = Contact.objects.get()
        appointment = Appointment.objects.get()
        self.assertEqual(contact.full_name, "Asha Rao")
        self.assertEqual(contact.email, "asha@example.com")
        self.assertEqual(contact.phone, "9876543210")
        self.assertEqual(appointment.contact_id, contact.pk)
        self.assertEqual(appointment.status, Appointment.Status.CONFIRMED)
        self.assertEqual(appointment.source, Appointment.Source.WEBSITE)
        self.assertEqual(len(mail.outbox), 1)

    def test_public_appointment_rejects_overlapping_confirmed_slot(self):
        Appointment.objects.create(
            service=self.service,
            full_name="Existing Client",
            phone="9876543211",
            starts_at=local_dt(self.day, 10),
            ends_at=local_dt(self.day, 11),
            duration_minutes=60,
            status=Appointment.Status.CONFIRMED,
            source=Appointment.Source.ADMIN,
        )

        response = self.client.post(
            f"/api/v1/public/services/{self.service.slug}/appointments/",
            {
                "starts_at": local_dt(self.day, 10).isoformat(),
                "full_name": "Asha Rao",
                "phone": "9876543210",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Appointment.objects.count(), 1)
        self.assertEqual(CampaignFormResponse.objects.count(), 0)

    def test_customer_list_reschedule_cancel_and_permissions(self):
        User = get_user_model()
        user = User.objects.create_user("asha", "asha@example.com", "StrongPass123!")
        other = User.objects.create_user("other", "other@example.com", "StrongPass123!")
        self.client.force_authenticate(user)

        create_response = self.client.post(
            "/api/v1/auth/customer/appointments/",
            {
                "service_slug": self.service.slug,
                "starts_at": local_dt(self.day, 10).isoformat(),
                "full_name": "Asha Rao",
                "phone": "9876543210",
            },
            format="json",
        )
        self.assertEqual(create_response.status_code, 201)
        appointment_id = create_response.data["id"]

        list_response = self.client.get("/api/v1/auth/customer/appointments/")
        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(len(list_response.data), 1)

        self.client.force_authenticate(other)
        hidden_response = self.client.get("/api/v1/auth/customer/appointments/")
        cancel_denied = self.client.patch(f"/api/v1/auth/customer/appointments/{appointment_id}/cancel/", {"reason": "No"}, format="json")
        self.assertEqual(hidden_response.status_code, 200)
        self.assertEqual(hidden_response.data, [])
        self.assertEqual(cancel_denied.status_code, 404)

        self.client.force_authenticate(user)
        reschedule_response = self.client.patch(
            f"/api/v1/auth/customer/appointments/{appointment_id}/reschedule/",
            {"starts_at": local_dt(self.day, 11, 15).isoformat()},
            format="json",
        )
        self.assertEqual(reschedule_response.status_code, 200)
        self.assertIn("11:15", reschedule_response.data["starts_at"])

        cancel_response = self.client.patch(
            f"/api/v1/auth/customer/appointments/{appointment_id}/cancel/",
            {"reason": "Travel"},
            format="json",
        )
        self.assertEqual(cancel_response.status_code, 200)
        self.assertEqual(cancel_response.data["status"], Appointment.Status.CANCELLED)

    def test_staff_can_create_appointment(self):
        user = get_user_model().objects.create_superuser("admin", "admin@example.com", "password")
        self.client.force_authenticate(user)

        response = self.client.post(
            "/api/v1/admin/appointments/",
            {
                "service": self.service.pk,
                "full_name": "Staff Client",
                "phone": "9876543212",
                "starts_at": local_dt(self.day, 15).isoformat(),
                "source": Appointment.Source.STAFF_APP,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        appointment = Appointment.objects.get(pk=response.data["id"])
        self.assertEqual(appointment.created_by_id, user.pk)
        self.assertEqual(appointment.source, Appointment.Source.STAFF_APP)
        self.assertEqual(appointment.duration_minutes, 60)

    def test_staff_appointment_list_filters_by_date_range(self):
        user = get_user_model().objects.create_superuser("admin", "admin@example.com", "password")
        self.client.force_authenticate(user)
        inside = Appointment.objects.create(
            service=self.service,
            full_name="Inside Client",
            phone="9876543212",
            starts_at=local_dt(self.day, 15),
            ends_at=local_dt(self.day, 16),
            duration_minutes=60,
            status=Appointment.Status.CONFIRMED,
            source=Appointment.Source.ADMIN,
        )
        Appointment.objects.create(
            service=self.service,
            full_name="Outside Client",
            phone="9876543213",
            starts_at=local_dt(self.day + timedelta(days=3), 15),
            ends_at=local_dt(self.day + timedelta(days=3), 16),
            duration_minutes=60,
            status=Appointment.Status.CONFIRMED,
            source=Appointment.Source.ADMIN,
        )

        response = self.client.get(
            "/api/v1/admin/appointments/",
            {"date_from": self.day.isoformat(), "date_to": self.day.isoformat(), "ordering": "starts_at"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual([appointment["id"] for appointment in response.data], [inside.pk])

    def test_staff_create_rejects_downtime_overlap(self):
        user = get_user_model().objects.create_superuser("admin", "admin@example.com", "password")
        self.client.force_authenticate(user)
        Appointment.objects.create(
            service=self.service,
            full_name="Existing Client",
            phone="9876543211",
            starts_at=local_dt(self.day, 10),
            ends_at=local_dt(self.day, 11),
            duration_minutes=60,
            status=Appointment.Status.CONFIRMED,
            source=Appointment.Source.ADMIN,
        )

        response = self.client.post(
            "/api/v1/admin/appointments/",
            {
                "service": self.service.pk,
                "full_name": "Staff Client",
                "phone": "9876543212",
                "starts_at": local_dt(self.day, 11).isoformat(),
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("downtime", str(response.data).lower())

    def test_staff_can_upload_and_list_appointment_photos(self):
        user = get_user_model().objects.create_superuser("admin", "admin@example.com", "password")
        self.client.force_authenticate(user)
        appointment = Appointment.objects.create(
            service=self.service,
            full_name="Asha Rao",
            phone="9876543210",
            starts_at=local_dt(self.day, 10),
            ends_at=local_dt(self.day, 11),
            duration_minutes=60,
            status=Appointment.Status.CONFIRMED,
            source=Appointment.Source.ADMIN,
        )

        with TemporaryDirectory() as media_root, override_settings(
            MEDIA_ROOT=media_root,
            STORAGES={"default": {"BACKEND": "django.core.files.storage.FileSystemStorage"}},
        ):
            upload = SimpleUploadedFile(
                "before.png",
                (
                    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
                    b"\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00"
                    b"\x00\x00\x0cIDATx\x9cc```\x00\x00\x00\x04\x00\x01"
                    b"\xf6\x178U\x00\x00\x00\x00IEND\xaeB`\x82"
                ),
                content_type="image/png",
            )
            create_response = self.client.post(
                f"/api/v1/admin/appointments/{appointment.pk}/photos/",
                {"photo_type": AppointmentPhoto.PhotoType.BEFORE, "image": upload, "notes": "Before cleanse"},
                format="multipart",
            )
            appointment_response = self.client.get(f"/api/v1/admin/appointments/{appointment.pk}/")

        self.assertEqual(create_response.status_code, 201)
        self.assertEqual(create_response.data["photo_type"], AppointmentPhoto.PhotoType.BEFORE)
        self.assertEqual(appointment_response.status_code, 200)
        self.assertEqual(len(appointment_response.data["photos"]), 1)

    def test_founder_dashboard_includes_appointments_contacts_and_manual_finance(self):
        user = get_user_model().objects.create_superuser("admin", "admin@example.com", "password")
        self.client.force_authenticate(user)
        self.service.price_amount = "2500.00"
        self.service.save(update_fields=["price_amount", "updated_at"])
        starts_at = timezone.now()
        appointment = Appointment.objects.create(
            service=self.service,
            full_name="Asha Rao",
            phone="9876543210",
            starts_at=starts_at,
            ends_at=starts_at + timedelta(minutes=60),
            duration_minutes=60,
            status=Appointment.Status.COMPLETED,
            source=Appointment.Source.ADMIN,
        )
        AppointmentFinanceEntry.objects.create(entry_date=timezone.localdate(), entry_type=AppointmentFinanceEntry.EntryType.EXPENSE, label="Supplies", amount="400.00", appointment=appointment)

        response = self.client.get("/api/v1/admin/dashboard/founder/", {"period": "today"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["appointments"]["completed"], 1)
        self.assertEqual(str(response.data["finance"]["service_revenue"]), "2500.00")
        self.assertEqual(str(response.data["finance"]["manual_expense"]), "400.00")

    def test_app_config_feature_flags_use_scheduling_settings(self):
        response = self.client.get("/api/v1/public/app-config/")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["feature_flags"]["first_party_scheduling"])
        self.assertFalse(response.data["feature_flags"]["calendly_booking"])

    def test_availability_impact_previews_narrowing_future_confirmed_appointments(self):
        user = get_user_model().objects.create_superuser("admin", "admin@example.com", "password")
        self.client.force_authenticate(user)
        day = next_weekday(0)
        window = AppointmentAvailabilityWindow.objects.create(
            weekday=day.weekday(),
            starts_at=time(13, 30),
            ends_at=time(19, 30),
            active=True,
            label="Studio hours",
        )
        affected = Appointment.objects.create(
            service=self.service,
            full_name="Asha Rao",
            phone="9876543210",
            starts_at=local_dt(day, 14),
            ends_at=local_dt(day, 15),
            duration_minutes=60,
            status=Appointment.Status.CONFIRMED,
            source=Appointment.Source.ADMIN,
        )
        Appointment.objects.create(
            service=self.service,
            full_name="Mira Shah",
            phone="9876543211",
            starts_at=local_dt(day, 16),
            ends_at=local_dt(day, 17),
            duration_minutes=60,
            status=Appointment.Status.CONFIRMED,
            source=Appointment.Source.ADMIN,
        )

        response = self.client.post(
            f"/api/v1/admin/appointment-availability/{window.pk}/impact/",
            {"starts_at": "15:00:00", "ends_at": "19:30:00"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["affected_count"], 1)
        self.assertEqual([appointment["id"] for appointment in response.data["appointments"]], [affected.pk])
        self.assertEqual(response.data["appointments"][0]["service_title"], self.service.title)

    def test_availability_impact_previews_deleting_current_window(self):
        user = get_user_model().objects.create_superuser("admin", "admin@example.com", "password")
        self.client.force_authenticate(user)
        day = next_weekday(0)
        window = AppointmentAvailabilityWindow.objects.create(
            weekday=day.weekday(),
            starts_at=time(13, 30),
            ends_at=time(19, 30),
            active=True,
            label="Studio hours",
        )
        AppointmentAvailabilityWindow.objects.create(
            weekday=day.weekday(),
            starts_at=time(16, 0),
            ends_at=time(17, 30),
            active=True,
            label="Late cover",
        )
        affected = Appointment.objects.create(
            service=self.service,
            full_name="Asha Rao",
            phone="9876543210",
            starts_at=local_dt(day, 14),
            ends_at=local_dt(day, 15),
            duration_minutes=60,
            status=Appointment.Status.CONFIRMED,
            source=Appointment.Source.ADMIN,
        )
        Appointment.objects.create(
            service=self.service,
            full_name="Mira Shah",
            phone="9876543211",
            starts_at=local_dt(day, 16),
            ends_at=local_dt(day, 17),
            duration_minutes=60,
            status=Appointment.Status.CONFIRMED,
            source=Appointment.Source.ADMIN,
        )
        Appointment.objects.create(
            service=self.service,
            full_name="Leela Shah",
            phone="9876543212",
            starts_at=local_dt(day, 20),
            ends_at=local_dt(day, 21),
            duration_minutes=60,
            status=Appointment.Status.CONFIRMED,
            source=Appointment.Source.ADMIN,
        )

        response = self.client.post(
            f"/api/v1/admin/appointment-availability/{window.pk}/impact/",
            {"delete": True},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["affected_count"], 1)
        self.assertEqual([appointment["id"] for appointment in response.data["appointments"]], [affected.pk])


class AppointmentAvailabilitySeedCommandTests(TestCase):
    def test_seed_creates_missing_mon_sat_only_and_is_idempotent(self):
        output = StringIO()
        call_command("seed_appointment_availability", stdout=output)

        windows = AppointmentAvailabilityWindow.objects.order_by("weekday")
        self.assertEqual(windows.count(), 6)
        self.assertEqual(list(windows.values_list("weekday", flat=True)), [0, 1, 2, 3, 4, 5])
        self.assertFalse(AppointmentAvailabilityWindow.objects.filter(weekday=6).exists())
        for window in windows:
            self.assertEqual(window.starts_at, time(13, 30))
            self.assertEqual(window.ends_at, time(19, 30))
            self.assertEqual(window.label, "Studio hours")
            self.assertEqual(window.ordering, 0)
            self.assertTrue(window.active)

        second_output = StringIO()
        call_command("seed_appointment_availability", stdout=second_output)

        self.assertEqual(AppointmentAvailabilityWindow.objects.count(), 6)
        self.assertIn("created=0", second_output.getvalue())
        self.assertIn("skipped=6", second_output.getvalue())

    def test_seed_skips_existing_weekday_and_supports_dry_run(self):
        AppointmentAvailabilityWindow.objects.create(
            weekday=2,
            starts_at=time(9, 0),
            ends_at=time(11, 0),
            active=False,
            label="Manual edit",
            ordering=7,
        )

        dry_run_output = StringIO()
        call_command("seed_appointment_availability", dry_run=True, label="Dry run", ordering=3, stdout=dry_run_output)

        self.assertEqual(AppointmentAvailabilityWindow.objects.count(), 1)
        self.assertIn("would_create=5", dry_run_output.getvalue())

        call_command("seed_appointment_availability", label="Default hours", ordering=3, stdout=StringIO())

        self.assertEqual(AppointmentAvailabilityWindow.objects.count(), 6)
        manual_window = AppointmentAvailabilityWindow.objects.get(weekday=2)
        self.assertEqual(manual_window.starts_at, time(9, 0))
        self.assertEqual(manual_window.ends_at, time(11, 0))
        self.assertEqual(manual_window.label, "Manual edit")
        self.assertFalse(manual_window.active)


@override_settings(
    ALLOWED_HOSTS=["testserver"],
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    APPOINTMENT_REMINDER_MINUTES=[1440, 120],
)
class AppointmentReminderCommandTests(TestCase):
    def test_reminder_command_logs_each_offset_once(self):
        service = Service.objects.create(
            title="The Glow Cleanse",
            slug="the-glow-cleanse",
            short_description="A comforting reset.",
            duration_minutes=60,
            active=True,
        )
        starts_at = timezone.now() + timedelta(hours=23, minutes=59)
        Appointment.objects.create(
            service=service,
            full_name="Asha Rao",
            phone="9876543210",
            email="asha@example.com",
            starts_at=starts_at,
            ends_at=starts_at + timedelta(minutes=60),
            duration_minutes=60,
            status=Appointment.Status.CONFIRMED,
            source=Appointment.Source.ADMIN,
        )

        first_output = StringIO()
        call_command("send_appointment_reminders", stdout=first_output)
        second_output = StringIO()
        call_command("send_appointment_reminders", stdout=second_output)

        self.assertIn("sent=1", first_output.getvalue())
        self.assertIn("skipped=1", second_output.getvalue())
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(AppointmentNotificationLog.objects.filter(event_type=AppointmentNotificationLog.EventType.REMINDER).count(), 1)
        self.assertEqual(AppointmentNotificationLog.objects.get().reminder_minutes, 1440)
