import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("contacts", "0002_seed_contact_statuses"),
        ("campaigns", "0003_campaign_form_authoring_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="campaignformresponse",
            name="contact",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="campaign_responses",
                to="contacts.contact",
            ),
        ),
        migrations.AddField(
            model_name="campaignformresponse",
            name="contact_sync_status",
            field=models.CharField(
                choices=[
                    ("pending", "Pending"),
                    ("synced", "Synced"),
                    ("skipped", "Skipped"),
                    ("conflict", "Conflict"),
                    ("failed", "Failed"),
                ],
                default="pending",
                max_length=24,
            ),
        ),
        migrations.AddField(
            model_name="campaignformresponse",
            name="contact_sync_error",
            field=models.TextField(blank=True),
        ),
    ]
