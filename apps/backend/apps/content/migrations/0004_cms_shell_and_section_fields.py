from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("content", "0003_imagevariant"),
    ]

    operations = [
        migrations.CreateModel(
            name="SiteNavigationItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("label", models.CharField(max_length=120)),
                ("url", models.CharField(max_length=240)),
                (
                    "placement",
                    models.CharField(
                        choices=[
                            ("header", "Header navigation"),
                            ("header_cta", "Header CTA"),
                            ("footer", "Footer navigation"),
                            ("footer_cta", "Footer CTA"),
                            ("footer_contact", "Footer contact"),
                            ("social", "Social link"),
                        ],
                        default="header",
                        max_length=32,
                    ),
                ),
                (
                    "style",
                    models.CharField(
                        choices=[
                            ("link", "Link"),
                            ("primary", "Primary button"),
                            ("secondary", "Secondary button"),
                            ("muted", "Muted"),
                        ],
                        default="link",
                        max_length=32,
                    ),
                ),
                ("open_in_new_tab", models.BooleanField(default=False)),
                ("active", models.BooleanField(default=True)),
                ("ordering", models.PositiveIntegerField(default=0)),
            ],
            options={"ordering": ["placement", "ordering", "id"]},
        ),
        migrations.AddField(
            model_name="heroslide",
            name="schedule_enabled",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="page",
            name="slug",
            field=models.SlugField(blank=True, unique=True),
        ),
        migrations.AddField(
            model_name="pagesection",
            name="background_variant",
            field=models.CharField(blank=True, max_length=80),
        ),
        migrations.AddField(
            model_name="pagesection",
            name="cta_style",
            field=models.CharField(blank=True, max_length=40),
        ),
        migrations.AddField(
            model_name="pagesection",
            name="eyebrow",
            field=models.CharField(blank=True, max_length=140),
        ),
        migrations.AddField(
            model_name="pagesection",
            name="layout_variant",
            field=models.CharField(blank=True, max_length=80),
        ),
        migrations.AddField(
            model_name="pagesection",
            name="media_alt",
            field=models.CharField(blank=True, max_length=220),
        ),
        migrations.AddField(
            model_name="pagesection",
            name="secondary_cta_label",
            field=models.CharField(blank=True, max_length=120),
        ),
        migrations.AddField(
            model_name="pagesection",
            name="secondary_cta_style",
            field=models.CharField(blank=True, max_length=40),
        ),
        migrations.AddField(
            model_name="pagesection",
            name="secondary_cta_url",
            field=models.CharField(blank=True, max_length=240),
        ),
        migrations.AlterField(
            model_name="service",
            name="slug",
            field=models.SlugField(blank=True, unique=True),
        ),
        migrations.AddField(
            model_name="testimonial",
            name="is_anonymized",
            field=models.BooleanField(default=True),
        ),
    ]
