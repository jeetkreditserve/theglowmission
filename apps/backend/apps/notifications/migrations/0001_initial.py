from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("contacts", "0003_contact_history"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="NotificationCampaign",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("title", models.CharField(max_length=180)),
                ("subject", models.CharField(max_length=180)),
                ("body", models.TextField()),
                ("status", models.CharField(choices=[("draft", "Draft"), ("ready", "Ready"), ("sent", "Sent")], default="draft", max_length=24)),
                ("marketing_consent_only", models.BooleanField(default=True)),
                ("include_customers", models.BooleanField(default=True)),
                ("scheduled_at", models.DateTimeField(blank=True, null=True)),
                ("sent_at", models.DateTimeField(blank=True, null=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="created_notification_campaigns",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "target_status",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="notification_campaigns",
                        to="contacts.contactstatus",
                    ),
                ),
            ],
            options={
                "ordering": ["-updated_at", "-id"],
            },
        ),
        migrations.CreateModel(
            name="NotificationRecipient",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("display_name", models.CharField(blank=True, max_length=180)),
                ("email", models.EmailField(blank=True, max_length=254)),
                ("phone", models.CharField(blank=True, max_length=32)),
                (
                    "campaign",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="recipients", to="notifications.notificationcampaign"),
                ),
                (
                    "contact",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="notification_recipients",
                        to="contacts.contact",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="notification_recipients",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["display_name", "id"],
            },
        ),
        migrations.CreateModel(
            name="NotificationMessageLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("channel", models.CharField(choices=[("email", "Email"), ("expo", "Expo push"), ("web_push", "Web push")], max_length=32)),
                ("recipient_address", models.CharField(blank=True, max_length=500)),
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
                ("opened_at", models.DateTimeField(blank=True, null=True)),
                (
                    "campaign",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="message_logs", to="notifications.notificationcampaign"),
                ),
                (
                    "contact",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="notification_message_logs",
                        to="contacts.contact",
                    ),
                ),
                (
                    "recipient",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="message_logs", to="notifications.notificationrecipient"),
                ),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="notification_message_logs",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at", "-id"],
            },
        ),
        migrations.AddIndex(
            model_name="notificationmessagelog",
            index=models.Index(fields=["channel", "status"], name="notificatio_channel_74f529_idx"),
        ),
        migrations.AddIndex(
            model_name="notificationmessagelog",
            index=models.Index(fields=["contact", "created_at"], name="notificatio_contact_6fd7be_idx"),
        ),
        migrations.AddIndex(
            model_name="notificationmessagelog",
            index=models.Index(fields=["user", "created_at"], name="notificatio_user_id_01ba6d_idx"),
        ),
        migrations.AddConstraint(
            model_name="notificationrecipient",
            constraint=models.UniqueConstraint(fields=("campaign", "contact"), name="unique_notification_campaign_contact"),
        ),
        migrations.AddConstraint(
            model_name="notificationrecipient",
            constraint=models.UniqueConstraint(fields=("campaign", "user"), name="unique_notification_campaign_user"),
        ),
        migrations.AddIndex(
            model_name="notificationcampaign",
            index=models.Index(fields=["status", "scheduled_at"], name="notificatio_status_8150c2_idx"),
        ),
    ]
