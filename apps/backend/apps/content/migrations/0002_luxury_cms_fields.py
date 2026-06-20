import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("campaigns", "0002_campaign_presentation_fields"),
        ("content", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="HeroSlide",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("title", models.CharField(max_length=220)),
                ("subtitle", models.CharField(blank=True, max_length=260)),
                ("body", models.TextField(blank=True)),
                ("image", models.ImageField(blank=True, null=True, upload_to="hero-slides/")),
                ("image_alt", models.CharField(blank=True, max_length=220)),
                ("offer_label", models.CharField(blank=True, max_length=120)),
                ("primary_cta_label", models.CharField(default="Book a consultation", max_length=120)),
                ("primary_cta_url", models.CharField(default="/campaigns/glow-consultation", max_length=240)),
                ("secondary_cta_label", models.CharField(blank=True, max_length=120)),
                ("secondary_cta_url", models.CharField(blank=True, max_length=240)),
                ("starts_at", models.DateTimeField(blank=True, null=True)),
                ("ends_at", models.DateTimeField(blank=True, null=True)),
                ("active", models.BooleanField(default=True)),
                ("ordering", models.PositiveIntegerField(default=0)),
                ("config", models.JSONField(blank=True, default=dict)),
                (
                    "linked_campaign",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="hero_slides",
                        to="campaigns.campaignform",
                    ),
                ),
            ],
            options={"ordering": ["ordering", "id"]},
        ),
        migrations.AddField(
            model_name="service",
            name="image_alt",
            field=models.CharField(blank=True, max_length=220),
        ),
        migrations.AddField(
            model_name="service",
            name="session_count",
            field=models.PositiveSmallIntegerField(default=1),
        ),
        migrations.AddField(
            model_name="service",
            name="currency",
            field=models.CharField(default="INR", max_length=8),
        ),
        migrations.AddField(
            model_name="service",
            name="price_amount",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name="service",
            name="sale_price_amount",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name="service",
            name="discount_label",
            field=models.CharField(blank=True, max_length=120),
        ),
        migrations.AlterField(
            model_name="service",
            name="price_note",
            field=models.CharField(blank=True, max_length=160),
        ),
        migrations.AddField(
            model_name="service",
            name="inclusions",
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name="service",
            name="featured",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="service",
            name="cta_label",
            field=models.CharField(default="Book this ritual", max_length=120),
        ),
        migrations.AddField(
            model_name="service",
            name="cta_url",
            field=models.CharField(blank=True, max_length=240),
        ),
        migrations.AddField(
            model_name="service",
            name="booking_campaign",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="services",
                to="campaigns.campaignform",
            ),
        ),
    ]
