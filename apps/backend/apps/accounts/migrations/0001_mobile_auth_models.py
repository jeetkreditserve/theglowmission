from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


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
            name="MobileOtpChallenge",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("phone", models.CharField(max_length=32)),
                ("normalized_phone", models.CharField(db_index=True, max_length=32)),
                ("code_hash", models.CharField(max_length=180)),
                ("expires_at", models.DateTimeField(db_index=True)),
                ("consumed_at", models.DateTimeField(blank=True, null=True)),
                ("attempts", models.PositiveSmallIntegerField(default=0)),
                ("request_ip", models.GenericIPAddressField(blank=True, null=True)),
                ("user_agent", models.TextField(blank=True)),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="SocialAccount",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("provider", models.CharField(max_length=40)),
                ("provider_user_id", models.CharField(max_length=180)),
                ("email", models.EmailField(blank=True, max_length=254)),
                ("first_name", models.CharField(blank=True, max_length=150)),
                ("last_name", models.CharField(blank=True, max_length=150)),
                ("raw_profile", models.JSONField(blank=True, default=dict)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="glow_social_accounts", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["provider", "provider_user_id"]},
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
            model_name="socialaccount",
            constraint=models.UniqueConstraint(fields=("provider", "provider_user_id"), name="unique_social_provider_user"),
        ),
        migrations.AddConstraint(
            model_name="userrole",
            constraint=models.UniqueConstraint(fields=("user", "role"), name="unique_user_account_role"),
        ),
    ]
