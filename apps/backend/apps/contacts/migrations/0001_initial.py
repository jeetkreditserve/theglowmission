from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
from django.db.models import Q


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="ContactStatus",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=80, unique=True)),
                ("slug", models.SlugField(blank=True, max_length=100, unique=True)),
                ("ordering", models.PositiveIntegerField(default=0)),
                ("is_default", models.BooleanField(default=False)),
            ],
            options={
                "verbose_name_plural": "Contact statuses",
                "ordering": ["ordering", "name"],
            },
        ),
        migrations.CreateModel(
            name="Contact",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("full_name", models.CharField(blank=True, max_length=180)),
                ("email", models.EmailField(blank=True, max_length=254)),
                ("normalized_email", models.CharField(blank=True, db_index=True, max_length=254)),
                ("phone", models.CharField(blank=True, max_length=32)),
                ("normalized_phone", models.CharField(blank=True, db_index=True, max_length=32)),
                ("address", models.TextField(blank=True)),
                ("age", models.PositiveSmallIntegerField(blank=True, null=True)),
                ("skin_type", models.CharField(blank=True, max_length=120)),
                ("preferred_ritual", models.CharField(blank=True, max_length=180)),
                ("preferred_day", models.CharField(blank=True, max_length=160)),
                ("skin_goal", models.TextField(blank=True)),
                ("marketing_consent", models.BooleanField(default=False)),
                ("first_activity_at", models.DateTimeField(blank=True, null=True)),
                ("last_activity_at", models.DateTimeField(blank=True, null=True)),
                ("source_response_count", models.PositiveIntegerField(default=0)),
                ("is_merged", models.BooleanField(default=False)),
                ("merged_at", models.DateTimeField(blank=True, null=True)),
                (
                    "merged_into",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="merged_contacts",
                        to="contacts.contact",
                    ),
                ),
                (
                    "status",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="contacts",
                        to="contacts.contactstatus",
                    ),
                ),
            ],
            options={
                "ordering": ["-last_activity_at", "-updated_at"],
            },
        ),
        migrations.CreateModel(
            name="ContactNote",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("body", models.TextField()),
                (
                    "contact",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="notes", to="contacts.contact"),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="contact_notes",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at", "-id"],
            },
        ),
        migrations.CreateModel(
            name="ContactAuditEvent",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "event_type",
                    models.CharField(
                        choices=[
                            ("created", "Created"),
                            ("updated", "Updated"),
                            ("status_changed", "Status changed"),
                            ("consent_changed", "Consent changed"),
                            ("merged", "Merged"),
                            ("sync_failed", "Sync failed"),
                        ],
                        max_length=40,
                    ),
                ),
                ("field_name", models.CharField(blank=True, max_length=80)),
                ("old_value", models.JSONField(blank=True, null=True)),
                ("new_value", models.JSONField(blank=True, null=True)),
                ("source_type", models.CharField(blank=True, max_length=80)),
                ("source_id", models.CharField(blank=True, max_length=80)),
                ("message", models.TextField(blank=True)),
                (
                    "actor",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="contact_audit_events",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "contact",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="audit_events", to="contacts.contact"),
                ),
            ],
            options={
                "ordering": ["-created_at", "-id"],
            },
        ),
        migrations.AddConstraint(
            model_name="contact",
            constraint=models.UniqueConstraint(
                condition=Q(is_merged=False) & ~Q(normalized_email=""),
                fields=("normalized_email",),
                name="unique_contact_normalized_email",
            ),
        ),
        migrations.AddConstraint(
            model_name="contact",
            constraint=models.UniqueConstraint(
                condition=Q(is_merged=False) & ~Q(normalized_phone=""),
                fields=("normalized_phone",),
                name="unique_contact_normalized_phone",
            ),
        ),
    ]
