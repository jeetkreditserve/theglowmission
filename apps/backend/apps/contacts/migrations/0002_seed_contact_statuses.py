from django.db import migrations


def seed_contact_statuses(apps, schema_editor):
    ContactStatus = apps.get_model("contacts", "ContactStatus")
    statuses = [
        ("Lead", "lead", 0, True),
        ("Prospect", "prospect", 1, False),
        ("Customer", "customer", 2, False),
        ("Inactive", "inactive", 3, False),
    ]
    for name, slug, ordering, is_default in statuses:
        ContactStatus.objects.update_or_create(
            slug=slug,
            defaults={"name": name, "ordering": ordering, "is_default": is_default},
        )


def unseed_contact_statuses(apps, schema_editor):
    ContactStatus = apps.get_model("contacts", "ContactStatus")
    ContactStatus.objects.filter(slug__in=["lead", "prospect", "customer", "inactive"], contacts__isnull=True).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("contacts", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_contact_statuses, unseed_contact_statuses),
    ]
