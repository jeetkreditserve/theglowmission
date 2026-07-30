from __future__ import annotations

import re

from django.db import migrations, models


def backfill_duration_minutes(apps, schema_editor):
    Service = apps.get_model("content", "Service")
    for service in Service.objects.all():
        service.duration_minutes = duration_minutes_from_label(service.duration)
        service.save(update_fields=["duration_minutes"])


def duration_minutes_from_label(value: str) -> int:
    label = str(value or "").strip().lower()
    match = re.search(r"\d+", label)
    if not match:
        return 60
    amount = int(match.group(0))
    if amount <= 0:
        return 60
    if "hour" in label or "hr" in label:
        return amount * 60
    return amount


class Migration(migrations.Migration):
    dependencies = [
        ("content", "0006_service_calendly_event_url"),
    ]

    operations = [
        migrations.AddField(
            model_name="service",
            name="accepts_online_booking",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="service",
            name="booking_buffer_minutes",
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="service",
            name="calendly_fallback_enabled",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="service",
            name="duration_minutes",
            field=models.PositiveSmallIntegerField(default=60),
        ),
        migrations.RunPython(backfill_duration_minutes, migrations.RunPython.noop),
    ]
