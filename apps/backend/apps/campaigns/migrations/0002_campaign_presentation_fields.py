from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("campaigns", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="campaignform",
            name="summary",
            field=models.CharField(blank=True, max_length=280),
        ),
        migrations.AddField(
            model_name="campaignform",
            name="offer_label",
            field=models.CharField(blank=True, max_length=140),
        ),
        migrations.AddField(
            model_name="campaignform",
            name="hero_image",
            field=models.ImageField(blank=True, null=True, upload_to="campaigns/"),
        ),
        migrations.AddField(
            model_name="campaignform",
            name="hero_image_alt",
            field=models.CharField(blank=True, max_length=220),
        ),
        migrations.AddField(
            model_name="campaignform",
            name="button_label",
            field=models.CharField(default="Submit request", max_length=120),
        ),
    ]
