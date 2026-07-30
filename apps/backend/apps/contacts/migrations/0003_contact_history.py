from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("appointments", "0002_appointment_photos_and_finance"),
        ("contacts", "0002_seed_contact_statuses"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="ContactHistoryEntry",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("event_at", models.DateTimeField()),
                ("service_label", models.CharField(blank=True, max_length=180)),
                ("amount", models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ("notes", models.TextField(blank=True)),
                (
                    "after_photo",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="after_contact_history_entries",
                        to="appointments.appointmentphoto",
                    ),
                ),
                (
                    "appointment",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="contact_history_entries",
                        to="appointments.appointment",
                    ),
                ),
                (
                    "before_photo",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="before_contact_history_entries",
                        to="appointments.appointmentphoto",
                    ),
                ),
                ("contact", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="history_entries", to="contacts.contact")),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="contact_history_entries",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-event_at", "-id"],
            },
        ),
        migrations.AddIndex(
            model_name="contacthistoryentry",
            index=models.Index(fields=["contact", "event_at"], name="contacts_co_contact_e87e16_idx"),
        ),
        migrations.AddIndex(
            model_name="contacthistoryentry",
            index=models.Index(fields=["appointment", "event_at"], name="contacts_co_appoint_696fb2_idx"),
        ),
    ]
