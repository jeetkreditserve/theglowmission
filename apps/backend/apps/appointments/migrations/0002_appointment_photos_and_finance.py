from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("appointments", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="AppointmentFinanceEntry",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("entry_date", models.DateField()),
                ("entry_type", models.CharField(choices=[("income", "Income"), ("expense", "Expense")], max_length=16)),
                ("label", models.CharField(max_length=180)),
                ("amount", models.DecimalField(decimal_places=2, max_digits=12)),
                ("notes", models.TextField(blank=True)),
                (
                    "appointment",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="finance_entries",
                        to="appointments.appointment",
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="appointment_finance_entries",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-entry_date", "-id"],
            },
        ),
        migrations.CreateModel(
            name="AppointmentPhoto",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("photo_type", models.CharField(choices=[("before", "Before"), ("after", "After")], max_length=16)),
                ("image", models.ImageField(upload_to="appointment-photos/")),
                ("notes", models.TextField(blank=True)),
                (
                    "appointment",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="photos", to="appointments.appointment"),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="appointment_photos",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["created_at", "id"],
            },
        ),
        migrations.AddIndex(
            model_name="appointmentfinanceentry",
            index=models.Index(fields=["entry_type", "entry_date"], name="appointment_entry_t_ea6c62_idx"),
        ),
        migrations.AddIndex(
            model_name="appointmentphoto",
            index=models.Index(fields=["appointment", "photo_type"], name="appointment_appoint_a253a5_idx"),
        ),
    ]
