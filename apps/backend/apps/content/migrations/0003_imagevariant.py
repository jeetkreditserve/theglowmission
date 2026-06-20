from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("content", "0002_luxury_cms_fields"),
    ]

    operations = [
        migrations.CreateModel(
            name="ImageVariant",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("source_key", models.CharField(db_index=True, max_length=512)),
                ("variant_key", models.CharField(max_length=512, unique=True)),
                ("width", models.PositiveIntegerField()),
                ("height", models.PositiveIntegerField()),
                (
                    "format",
                    models.CharField(choices=[("webp", "WebP"), ("jpeg", "JPEG")], max_length=16),
                ),
                ("byte_size", models.PositiveIntegerField(default=0)),
            ],
            options={
                "ordering": ["source_key", "format", "width"],
            },
        ),
        migrations.AddConstraint(
            model_name="imagevariant",
            constraint=models.UniqueConstraint(fields=("source_key", "width", "format"), name="unique_image_variant_size_format"),
        ),
    ]
