# Generated for The Glow Mission campaign form schema.

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="CampaignForm",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("title", models.CharField(max_length=180)),
                ("slug", models.SlugField(unique=True)),
                ("status", models.CharField(choices=[("draft", "Draft"), ("published", "Published"), ("archived", "Archived")], default="draft", max_length=24)),
                ("starts_at", models.DateTimeField(blank=True, null=True)),
                ("ends_at", models.DateTimeField(blank=True, null=True)),
                ("success_message", models.TextField(default="Thank you. We will get back to you soon.")),
                ("redirect_url", models.CharField(blank=True, max_length=240)),
                ("seo_title", models.CharField(blank=True, max_length=180)),
                ("seo_description", models.TextField(blank=True)),
            ],
            options={"ordering": ["-updated_at"]},
        ),
        migrations.CreateModel(
            name="CampaignFormField",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("label", models.CharField(max_length=180)),
                ("key", models.SlugField(max_length=120)),
                ("field_type", models.CharField(choices=[("text", "Text"), ("textarea", "Textarea"), ("email", "Email"), ("phone", "Phone"), ("select", "Select"), ("checkbox", "Checkbox"), ("radio", "Radio"), ("date", "Date"), ("number", "Number")], default="text", max_length=32)),
                ("placeholder", models.CharField(blank=True, max_length=180)),
                ("help_text", models.CharField(blank=True, max_length=260)),
                ("required", models.BooleanField(default=False)),
                ("options", models.JSONField(blank=True, default=list)),
                ("validation", models.JSONField(blank=True, default=dict)),
                ("ordering", models.PositiveIntegerField(default=0)),
                ("active", models.BooleanField(default=True)),
                ("form", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="fields", to="campaigns.campaignform")),
            ],
            options={"ordering": ["ordering", "id"], "unique_together": {("form", "key")}},
        ),
        migrations.CreateModel(
            name="CampaignFormResponse",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("submitted_at", models.DateTimeField(auto_now_add=True)),
                ("response_data", models.JSONField(default=dict)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("field_snapshot", models.JSONField(default=list)),
                ("form", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="responses", to="campaigns.campaignform")),
            ],
            options={"ordering": ["-submitted_at"]},
        ),
    ]

