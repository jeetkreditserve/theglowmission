from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("campaigns", "0002_campaign_presentation_fields"),
    ]

    operations = [
        migrations.AlterField(
            model_name="campaignform",
            name="slug",
            field=models.SlugField(blank=True, unique=True),
        ),
        migrations.AddField(
            model_name="campaignform",
            name="checkbox_label",
            field=models.CharField(default="Yes", max_length=120),
        ),
        migrations.AddField(
            model_name="campaignform",
            name="empty_select_label",
            field=models.CharField(default="Select one", max_length=120),
        ),
        migrations.AddField(
            model_name="campaignform",
            name="error_message",
            field=models.TextField(default="Please check the highlighted fields and try again."),
        ),
        migrations.AddField(
            model_name="campaignform",
            name="schedule_enabled",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="campaignform",
            name="submitting_label",
            field=models.CharField(default="Sending...", max_length=120),
        ),
        migrations.AlterField(
            model_name="campaignformfield",
            name="key",
            field=models.SlugField(blank=True, max_length=120),
        ),
    ]
