# Generated for The Glow Mission initial CMS schema.

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="BrandSettings",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("site_title", models.CharField(default="The Glow Mission", max_length=160)),
                ("tagline", models.CharField(default="Glow, the natural way.", max_length=240)),
                ("essence", models.TextField(default="Soft. Elegant. Timeless. Made to make you glow.")),
                ("mission_statement", models.TextField(blank=True)),
                ("logo_image", models.ImageField(blank=True, null=True, upload_to="brand/")),
                ("favicon", models.ImageField(blank=True, null=True, upload_to="brand/")),
                ("primary_color", models.CharField(default="#D9B88C", max_length=16)),
                ("background_color", models.CharField(default="#FFF7F0", max_length=16)),
                ("surface_color", models.CharField(default="#F6EEE4", max_length=16)),
                ("muted_color", models.CharField(default="#CDB8A9", max_length=16)),
                ("accent_color", models.CharField(default="#E6D6C6", max_length=16)),
                ("text_color", models.CharField(default="#2B2623", max_length=16)),
                ("heading_font", models.CharField(default="Cinzel", max_length=120)),
                ("body_font", models.CharField(default="Montserrat", max_length=120)),
                ("cta_style", models.JSONField(blank=True, default=dict)),
                ("contact_email", models.EmailField(blank=True, max_length=254)),
                ("phone", models.CharField(blank=True, max_length=80)),
                ("address", models.TextField(blank=True)),
                ("instagram_handle", models.CharField(blank=True, max_length=120)),
                ("social_links", models.JSONField(blank=True, default=dict)),
            ],
            options={"verbose_name": "Brand settings", "verbose_name_plural": "Brand settings"},
        ),
        migrations.CreateModel(
            name="FAQ",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("question", models.CharField(max_length=240)),
                ("answer", models.TextField()),
                ("active", models.BooleanField(default=True)),
                ("ordering", models.PositiveIntegerField(default=0)),
            ],
            options={"ordering": ["ordering", "question"]},
        ),
        migrations.CreateModel(
            name="GalleryImage",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("title", models.CharField(max_length=180)),
                ("alt_text", models.CharField(blank=True, max_length=220)),
                ("image", models.ImageField(blank=True, null=True, upload_to="gallery/")),
                ("caption", models.CharField(blank=True, max_length=260)),
                ("active", models.BooleanField(default=True)),
                ("ordering", models.PositiveIntegerField(default=0)),
            ],
            options={"ordering": ["ordering", "title"]},
        ),
        migrations.CreateModel(
            name="MediaAsset",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("title", models.CharField(max_length=180)),
                ("file", models.FileField(upload_to="media-assets/")),
                ("alt_text", models.CharField(blank=True, max_length=220)),
                ("metadata", models.JSONField(blank=True, default=dict)),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="Page",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("title", models.CharField(max_length=180)),
                ("slug", models.SlugField(unique=True)),
                ("status", models.CharField(choices=[("draft", "Draft"), ("published", "Published"), ("archived", "Archived")], default="draft", max_length=24)),
                ("seo_title", models.CharField(blank=True, max_length=180)),
                ("seo_description", models.TextField(blank=True)),
                ("ordering", models.PositiveIntegerField(default=0)),
            ],
            options={"ordering": ["ordering", "title"]},
        ),
        migrations.CreateModel(
            name="Service",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("title", models.CharField(max_length=180)),
                ("slug", models.SlugField(unique=True)),
                ("short_description", models.CharField(max_length=260)),
                ("description", models.TextField(blank=True)),
                ("image", models.ImageField(blank=True, null=True, upload_to="services/")),
                ("duration", models.CharField(blank=True, max_length=80)),
                ("price_note", models.CharField(blank=True, max_length=120)),
                ("active", models.BooleanField(default=True)),
                ("ordering", models.PositiveIntegerField(default=0)),
            ],
            options={"ordering": ["ordering", "title"]},
        ),
        migrations.CreateModel(
            name="Testimonial",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=160)),
                ("quote", models.TextField()),
                ("role", models.CharField(blank=True, max_length=120)),
                ("active", models.BooleanField(default=True)),
                ("ordering", models.PositiveIntegerField(default=0)),
            ],
            options={"ordering": ["ordering", "name"]},
        ),
        migrations.CreateModel(
            name="PageSection",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("section_type", models.CharField(choices=[("hero", "Hero"), ("story", "Story"), ("services", "Services"), ("gallery", "Gallery"), ("testimonials", "Testimonials"), ("faqs", "FAQs"), ("cta", "CTA"), ("rich_text", "Rich text")], max_length=40)),
                ("title", models.CharField(blank=True, max_length=220)),
                ("subtitle", models.CharField(blank=True, max_length=260)),
                ("body", models.TextField(blank=True)),
                ("media", models.ImageField(blank=True, null=True, upload_to="page-sections/")),
                ("cta_label", models.CharField(blank=True, max_length=120)),
                ("cta_url", models.CharField(blank=True, max_length=240)),
                ("ordering", models.PositiveIntegerField(default=0)),
                ("active", models.BooleanField(default=True)),
                ("config", models.JSONField(blank=True, default=dict)),
                ("page", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="sections", to="content.page")),
            ],
            options={"ordering": ["ordering", "id"]},
        ),
    ]

