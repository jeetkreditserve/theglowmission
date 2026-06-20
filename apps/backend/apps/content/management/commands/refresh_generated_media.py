from __future__ import annotations

from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError

from apps.common.image_variants import ensure_image_variants
from apps.campaigns.models import CampaignForm
from apps.content.models import GalleryImage, HeroSlide, Page, PageSection, Service


HERO_DEFAULTS = [
    {
        "ordering": 0,
        "asset": "glow-hero-signature.webp",
        "storage_name": "hero-slide-0.webp",
        "image_alt": "Luxury facial massage ritual in a calm boutique spa setting",
    },
    {
        "ordering": 1,
        "asset": "glow-hero-offer.webp",
        "storage_name": "hero-slide-1.webp",
        "image_alt": "Premium spa consultation setting for a limited glow session offer",
    },
    {
        "ordering": 2,
        "asset": "glow-hero-face-yoga.webp",
        "storage_name": "hero-slide-2.webp",
        "title": "A sculpted lift in 40 calm minutes.",
        "subtitle": "The Face Lift Ritual refreshes tired skin with restorative massage, gua sha, and cooling therapy.",
        "body": "A focused sculpting ritual for a lifted, energised look when your face needs a quick reset.",
        "offer_label": "The Face Lift Ritual",
        "primary_cta_label": "Book the ritual",
        "primary_cta_url": "/campaigns/glow-consultation",
        "secondary_cta_label": "View ritual menu",
        "secondary_cta_url": "/glow-rituals",
        "image_alt": "The Face Lift Ritual in a calm boutique spa setting",
    },
]

SERVICE_ASSETS = {
    "the-face-lift-ritual": ("glow-service-face-yoga.webp", "the-face-lift-ritual.webp"),
    "the-glow-cleanse": ("glow-service-natural-facial.webp", "the-glow-cleanse.webp"),
    "the-occasion-glow-ritual": ("glow-gallery-post-treatment.webp", "the-occasion-glow-ritual.webp"),
    "the-rest-reset-ritual": ("glow-gallery-warm-towel.webp", "the-rest-reset-ritual.webp"),
    "the-glow-mission-signature": ("glow-service-signature.webp", "the-glow-mission-signature.webp"),
}

GALLERY_DEFAULTS = [
    ("Treatment room calm", "Prepared boutique spa treatment bed with ivory linens", "A quiet room prepared for slow facial care.", 0, "glow-gallery-treatment-room.webp"),
    ("Warm towel ritual", "Warm towel compress prepared for a facial ritual", "Soft towels, warm hands, and a slower pace.", 1, "glow-gallery-warm-towel.webp"),
    ("Signature massage detail", "Luxury facial massage treatment detail", "A quiet hour of massage, touch, and rest.", 2, "glow-gallery-massage-detail.webp"),
    ("Botanical ritual textures", "Natural facial ingredients prepared in ceramic bowls", "Honey, cucumber, citrus, herbs, and warm towels for a sensory ritual.", 3, "glow-gallery-botanicals.webp"),
    ("Post-treatment glow", "Rested client after a natural facial ritual", "Skin that feels rested, soft, and cared for.", 4, "glow-gallery-post-treatment.webp"),
    ("Quiet spa still life", "Elegant spa still life with natural care tools", "A personal practice shaped by care, consistency, and gentle hands.", 5, "glow-gallery-still-life.webp"),
]


class Command(BaseCommand):
    help = "Refresh current CMS media fields from generated seed assets without reseeding all copy."

    def handle(self, *args, **options):
        self.refresh_hero_slides()
        self.refresh_services()
        self.refresh_page_sections()
        self.refresh_gallery()
        self.refresh_campaign()
        self.stdout.write(self.style.SUCCESS("Refreshed generated media assets."))

    def asset_path(self, filename: str) -> Path:
        path = Path(settings.BASE_DIR) / "seed_assets" / filename
        if not path.exists():
            raise CommandError(f"Missing generated seed asset: {filename}")
        return path

    def save_asset(self, instance, field_name: str, filename: str, storage_name: str):
        field = getattr(instance, field_name)
        with self.asset_path(filename).open("rb") as handle:
            field.save(storage_name, File(handle), save=False)
        instance.save()
        ensure_image_variants(field)

    def refresh_hero_slides(self):
        campaign = CampaignForm.objects.filter(slug="glow-consultation").first()
        for item in HERO_DEFAULTS:
            ordering = item["ordering"]
            slide = HeroSlide.objects.filter(ordering=ordering).first()
            if slide is None:
                slide = HeroSlide.objects.create(
                    title=item.get("title", ""),
                    subtitle=item.get("subtitle", ""),
                    body=item.get("body", ""),
                    offer_label=item.get("offer_label", ""),
                    primary_cta_label=item.get("primary_cta_label", "Book a consultation"),
                    primary_cta_url=item.get("primary_cta_url", "/campaigns/glow-consultation"),
                    secondary_cta_label=item.get("secondary_cta_label", ""),
                    secondary_cta_url=item.get("secondary_cta_url", ""),
                    linked_campaign=campaign,
                    ordering=ordering,
                    active=True,
                    image_alt=item["image_alt"],
                )
            elif not slide.image_alt:
                slide.image_alt = item["image_alt"]
                slide.save(update_fields=["image_alt", "updated_at"])
            self.save_asset(slide, "image", item["asset"], item["storage_name"])

    def refresh_services(self):
        for slug, (asset, storage_name) in SERVICE_ASSETS.items():
            service = Service.objects.filter(slug=slug).first()
            if service is None:
                self.stdout.write(self.style.WARNING(f"Skipping missing service: {slug}"))
                continue
            self.save_asset(service, "image", asset, storage_name)

    def refresh_page_sections(self):
        story = PageSection.objects.filter(page__slug="home", section_type=PageSection.SectionType.STORY).first()
        if story:
            self.save_asset(story, "media", "glow-gallery-still-life.webp", "home-section-story.webp")

    def refresh_gallery(self):
        managed_titles = [item[0] for item in GALLERY_DEFAULTS]
        GalleryImage.objects.exclude(title__in=managed_titles).update(active=False)

        for title, alt_text, caption, ordering, asset in GALLERY_DEFAULTS:
            gallery, created = GalleryImage.objects.get_or_create(
                title=title,
                defaults={"alt_text": alt_text, "caption": caption, "ordering": ordering, "active": True},
            )
            if not created:
                gallery.alt_text = gallery.alt_text or alt_text
                gallery.caption = gallery.caption or caption
                gallery.ordering = ordering
                gallery.active = True
                gallery.save()
            self.save_asset(gallery, "image", asset, f"gallery-{ordering}.webp")

    def refresh_campaign(self):
        form = CampaignForm.objects.filter(slug="glow-consultation").first()
        if form is None:
            self.stdout.write(self.style.WARNING("Skipping missing campaign: glow-consultation"))
            return
        self.save_asset(form, "hero_image", "glow-consultation.webp", "glow-consultation-campaign.webp")
