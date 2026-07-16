from django.db import migrations, models


RITUAL_CALENDLY_URLS = {
    "the-glow-mission-signature": "https://calendly.com/theglowmission-info/the-glow-mission-signature-01-hour-30-minutes",
    "the-rest-reset-ritual": "https://calendly.com/theglowmission-info/the-rest-rest-ritual-01-hour-20-minutes",
    "the-occasion-glow-ritual": "https://calendly.com/theglowmission-info/the-occasion-glow-ritual-01-hour-10-minutes",
    "the-glow-cleanse": "https://calendly.com/theglowmission-info/the-glow-cleanse-01-hour",
    "the-face-lift-ritual": "https://calendly.com/theglowmission-info/the-glow-lift-ritual",
}
RITUAL_DURATIONS = {
    "the-glow-mission-signature": "90 MINS",
    "the-rest-reset-ritual": "80 MINS",
    "the-occasion-glow-ritual": "70 MINS",
    "the-glow-cleanse": "60 MINS",
    "the-face-lift-ritual": "50 MINS",
}


def seed_calendly_urls_and_campaign_phone_rules(apps, schema_editor):
    Service = apps.get_model("content", "Service")
    CampaignFormField = apps.get_model("campaigns", "CampaignFormField")

    for slug, calendly_url in RITUAL_CALENDLY_URLS.items():
        Service.objects.filter(slug=slug, calendly_event_url="").update(calendly_event_url=calendly_url)
    for slug, duration in RITUAL_DURATIONS.items():
        Service.objects.filter(slug=slug).update(duration=duration)

    CampaignFormField.objects.filter(key="email", field_type="email").update(required=False)
    CampaignFormField.objects.filter(key="phone", field_type="phone").update(required=True)


def clear_seeded_calendly_urls(apps, schema_editor):
    Service = apps.get_model("content", "Service")
    for slug, calendly_url in RITUAL_CALENDLY_URLS.items():
        Service.objects.filter(slug=slug, calendly_event_url=calendly_url).update(calendly_event_url="")


class Migration(migrations.Migration):
    dependencies = [
        ("campaigns", "0004_response_contact_sync"),
        ("content", "0005_brandsettings_seo_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="service",
            name="calendly_event_url",
            field=models.URLField(blank=True, max_length=300),
        ),
        migrations.RunPython(seed_calendly_urls_and_campaign_phone_rules, clear_seeded_calendly_urls),
    ]
