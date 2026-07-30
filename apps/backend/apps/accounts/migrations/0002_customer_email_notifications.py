from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_mobile_auth_models"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.DeleteModel(name="MobileOtpChallenge"),
        migrations.DeleteModel(name="SocialAccount"),
        migrations.CreateModel(
            name="CustomerNotificationSubscription",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("channel", models.CharField(choices=[("expo", "Expo push"), ("web_push", "Web push")], max_length=32)),
                ("platform", models.CharField(blank=True, max_length=40)),
                ("device_id", models.CharField(blank=True, db_index=True, max_length=180)),
                ("device_name", models.CharField(blank=True, max_length=180)),
                ("app_version", models.CharField(blank=True, max_length=80)),
                ("token", models.TextField(blank=True)),
                ("subscription_endpoint", models.URLField(blank=True, db_index=True, max_length=500)),
                ("subscription", models.JSONField(blank=True, default=dict)),
                ("permission_status", models.CharField(default="unknown", max_length=40)),
                ("enabled", models.BooleanField(default=True)),
                ("locale", models.CharField(blank=True, max_length=40)),
                ("timezone", models.CharField(blank=True, max_length=80)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("last_registered_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("disabled_at", models.DateTimeField(blank=True, null=True)),
                ("contact", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="notification_subscriptions", to="contacts.contact")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="customer_notification_subscriptions", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-last_registered_at", "-id"]},
        ),
        migrations.AddConstraint(
            model_name="customernotificationsubscription",
            constraint=models.UniqueConstraint(condition=~models.Q(token=""), fields=("channel", "token"), name="unique_customer_notification_channel_token"),
        ),
        migrations.AddConstraint(
            model_name="customernotificationsubscription",
            constraint=models.UniqueConstraint(condition=~models.Q(subscription_endpoint=""), fields=("channel", "subscription_endpoint"), name="unique_customer_notification_channel_endpoint"),
        ),
    ]
