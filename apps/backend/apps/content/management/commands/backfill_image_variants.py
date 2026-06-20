from __future__ import annotations

from dataclasses import dataclass

from django.core.management.base import BaseCommand

from apps.campaigns.models import CampaignForm
from apps.common.image_variants import ensure_image_variants
from apps.common.storage import file_key
from apps.content.models import BrandSettings, GalleryImage, HeroSlide, MediaAsset, PageSection, Service


@dataclass(frozen=True)
class ImageSource:
    label: str
    field_name: str
    instance: object


class Command(BaseCommand):
    help = "Create missing responsive image variants for existing CMS images."

    def add_arguments(self, parser):
        parser.add_argument("--force", action="store_true", help="Regenerate variants even when matching records already exist.")
        parser.add_argument("--dry-run", action="store_true", help="List image sources without creating variants.")

    def handle(self, *args, **options):
        force = options["force"]
        dry_run = options["dry_run"]
        sources = list(self.iter_sources())
        processed = 0
        variants = 0

        for source in sources:
            field = getattr(source.instance, source.field_name)
            key = file_key(field)
            if not key:
                continue
            processed += 1
            if dry_run:
                self.stdout.write(f"{source.label}: {key}")
                continue
            created = ensure_image_variants(field, force=force)
            variants += len(created)
            self.stdout.write(f"{source.label}: {key} ({len(created)} variants)")

        if dry_run:
            self.stdout.write(self.style.SUCCESS(f"Found {processed} image sources."))
        else:
            self.stdout.write(self.style.SUCCESS(f"Processed {processed} image sources and confirmed {variants} variants."))

    def iter_sources(self):
        brand = BrandSettings.objects.first()
        if brand:
            yield ImageSource("brand.logo", "logo_image", brand)
            yield ImageSource("brand.favicon", "favicon", brand)

        for item in HeroSlide.objects.all():
            yield ImageSource(f"hero-slide.{item.pk}", "image", item)
        for item in PageSection.objects.all():
            yield ImageSource(f"page-section.{item.pk}", "media", item)
        for item in Service.objects.all():
            yield ImageSource(f"service.{item.pk}", "image", item)
        for item in GalleryImage.objects.all():
            yield ImageSource(f"gallery.{item.pk}", "image", item)
        for item in MediaAsset.objects.all():
            yield ImageSource(f"media.{item.pk}", "file", item)
        for item in CampaignForm.objects.all():
            yield ImageSource(f"campaign.{item.pk}", "hero_image", item)
