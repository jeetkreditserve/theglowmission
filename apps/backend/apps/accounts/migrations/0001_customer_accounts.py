from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("contacts", "0002_seed_contact_statuses"),
    ]

    operations = [
        migrations.CreateModel(
            name="AccountRole",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=80, unique=True)),
                ("slug", models.SlugField(blank=True, max_length=100, unique=True)),
                ("description", models.TextField(blank=True)),
            ],
            options={"ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="CustomerProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("phone", models.CharField(blank=True, max_length=32)),
                ("normalized_phone", models.CharField(blank=True, db_index=True, max_length=32)),
                ("verified_phone_at", models.DateTimeField(blank=True, null=True)),
                ("verified_email_at", models.DateTimeField(blank=True, null=True)),
                ("contact", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="customer_profiles", to="contacts.contact")),
                ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="customer_profile", to=settings.AUTH_USER_MODEL)),
            ],
        ),
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
        migrations.CreateModel(
            name="UserRole",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("role", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="user_assignments", to="accounts.accountrole")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="glow_role_assignments", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["role__name", "user_id"]},
        ),
        migrations.AddConstraint(
            model_name="customerprofile",
            constraint=models.UniqueConstraint(condition=~models.Q(normalized_phone=""), fields=("normalized_phone",), name="unique_customer_profile_normalized_phone"),
        ),
        migrations.AddConstraint(
            model_name="customernotificationsubscription",
            constraint=models.UniqueConstraint(condition=~models.Q(token=""), fields=("channel", "token"), name="unique_customer_notification_channel_token"),
        ),
        migrations.AddConstraint(
            model_name="customernotificationsubscription",
            constraint=models.UniqueConstraint(condition=~models.Q(subscription_endpoint=""), fields=("channel", "subscription_endpoint"), name="unique_customer_notification_channel_endpoint"),
        ),
        migrations.AddConstraint(
            model_name="userrole",
            constraint=models.UniqueConstraint(fields=("user", "role"), name="unique_user_account_role"),
        ),
    ]
