from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("content", "0004_cms_shell_and_section_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="brandsettings",
            name="canonical_site_url",
            field=models.URLField(default="https://theglowmission.com"),
        ),
        migrations.AddField(
            model_name="brandsettings",
            name="seo_title",
            field=models.CharField(
                default="The Glow Mission | Natural Facial Rituals in Chandivali, Powai",
                max_length=180,
            ),
        ),
        migrations.AddField(
            model_name="brandsettings",
            name="seo_description",
            field=models.TextField(
                default=(
                    "The Glow Mission is a boutique facial wellness studio in Chandivali and Powai, Mumbai, "
                    "offering natural facial rituals, facial massage, face yoga, gua sha, and glow treatments."
                ),
            ),
        ),
        migrations.AddField(
            model_name="brandsettings",
            name="business_description",
            field=models.TextField(
                default=(
                    "The Glow Mission is a boutique facial wellness studio built around natural ingredients, "
                    "facial massage, face yoga, lifting techniques, calming rituals, and visible glow."
                ),
            ),
        ),
        migrations.AddField(
            model_name="brandsettings",
            name="area_served",
            field=models.CharField(default="Chandivali, Powai, Mumbai, India", max_length=180),
        ),
        migrations.AddField(
            model_name="brandsettings",
            name="same_as_links",
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name="brandsettings",
            name="opening_hours",
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name="brandsettings",
            name="latitude",
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True),
        ),
        migrations.AddField(
            model_name="brandsettings",
            name="longitude",
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True),
        ),
    ]
