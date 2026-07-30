from django.conf import settings
from django.db import migrations, models
import django.core.validators
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("campaigns", "0004_response_contact_sync"),
        ("contacts", "0002_seed_contact_statuses"),
        ("content", "0007_service_scheduling_fields"),
    ]

    operations = [
        migrations.CreateModel(
            name="AppointmentAvailabilityWindow",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "weekday",
                    models.PositiveSmallIntegerField(
                        validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(6)]
                    ),
                ),
                ("starts_at", models.TimeField()),
                ("ends_at", models.TimeField()),
                ("active", models.BooleanField(default=True)),
                ("label", models.CharField(blank=True, max_length=120)),
                ("ordering", models.PositiveIntegerField(default=0)),
            ],
            options={
                "ordering": ["weekday", "ordering", "starts_at", "id"],
            },
        ),
        migrations.CreateModel(
            name="AppointmentBlock",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("starts_at", models.DateTimeField()),
                ("ends_at", models.DateTimeField()),
                ("reason", models.CharField(blank=True, max_length=180)),
                ("active", models.BooleanField(default=True)),
            ],
            options={
                "ordering": ["starts_at", "id"],
            },
        ),
        migrations.CreateModel(
            name="Appointment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("full_name", models.CharField(max_length=180)),
                ("phone", models.CharField(max_length=32)),
                ("email", models.EmailField(blank=True, max_length=254)),
                ("notes", models.TextField(blank=True)),
                ("skin_goal", models.TextField(blank=True)),
                ("starts_at", models.DateTimeField()),
                ("ends_at", models.DateTimeField()),
                ("duration_minutes", models.PositiveSmallIntegerField(default=60)),
                (
                    "status",
                    models.CharField(
                        choices=[("confirmed", "Confirmed"), ("cancelled", "Cancelled"), ("completed", "Completed"), ("no_show", "No show")],
                        default="confirmed",
                        max_length=24,
                    ),
                ),
                (
                    "source",
                    models.CharField(
                        choices=[
                            ("customer_app", "Customer app"),
                            ("staff_app", "Staff app"),
                            ("website", "Website"),
                            ("admin", "Admin"),
                            ("campaign_response", "Campaign response"),
                        ],
                        default="website",
                        max_length=32,
                    ),
                ),
                ("cancellation_reason", models.TextField(blank=True)),
                ("customer_notes", models.TextField(blank=True)),
                ("internal_notes", models.TextField(blank=True)),
                (
                    "campaign_response",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="appointments",
                        to="campaigns.campaignformresponse",
                    ),
                ),
                (
                    "cancelled_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="cancelled_appointments",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "contact",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="appointments",
                        to="contacts.contact",
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="created_appointments",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "customer",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="customer_appointments",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "service",
                    models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="appointments", to="content.service"),
                ),
            ],
            options={
                "ordering": ["starts_at", "id"],
            },
        ),
        migrations.CreateModel(
            name="AppointmentNotificationLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("channel", models.CharField(choices=[("expo", "Expo push"), ("web_push", "Web push"), ("email", "Email")], max_length=32)),
                (
                    "event_type",
                    models.CharField(
                        choices=[
                            ("confirmation", "Confirmation"),
                            ("reschedule", "Reschedule"),
                            ("cancellation", "Cancellation"),
                            ("reminder", "Reminder"),
                        ],
                        max_length=32,
                    ),
                ),
                ("reminder_minutes", models.PositiveSmallIntegerField(blank=True, null=True)),
                ("recipient", models.CharField(blank=True, max_length=500)),
                (
                    "status",
                    models.CharField(
                        choices=[("pending", "Pending"), ("sent", "Sent"), ("skipped", "Skipped"), ("failed", "Failed")],
                        default="pending",
                        max_length=24,
                    ),
                ),
                ("error", models.TextField(blank=True)),
                ("sent_at", models.DateTimeField(blank=True, null=True)),
                (
                    "appointment",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="notification_logs", to="appointments.appointment"),
                ),
            ],
            options={
                "ordering": ["-created_at", "-id"],
            },
        ),
        migrations.AddIndex(
            model_name="appointmentnotificationlog",
            index=models.Index(fields=["event_type", "reminder_minutes"], name="appointment_event_t_1e07e6_idx"),
        ),
        migrations.AddIndex(
            model_name="appointmentnotificationlog",
            index=models.Index(fields=["channel", "status"], name="appointment_channel_fe7fc4_idx"),
        ),
        migrations.AddIndex(
            model_name="appointment",
            index=models.Index(fields=["status", "starts_at"], name="appointment_status_b30a74_idx"),
        ),
        migrations.AddIndex(
            model_name="appointment",
            index=models.Index(fields=["service", "starts_at"], name="appointment_service_900cd6_idx"),
        ),
        migrations.AddIndex(
            model_name="appointment",
            index=models.Index(fields=["contact", "starts_at"], name="appointment_contact_a551e1_idx"),
        ),
        migrations.AddIndex(
            model_name="appointment",
            index=models.Index(fields=["customer", "starts_at"], name="appointment_custome_4010bc_idx"),
        ),
    ]
