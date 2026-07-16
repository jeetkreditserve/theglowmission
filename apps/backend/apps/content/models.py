from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.text import slugify

from apps.common.models import TimeStampedModel


class BrandSettings(TimeStampedModel):
    site_title = models.CharField(max_length=160, default="The Glow Mission")
    tagline = models.CharField(max_length=240, default="Glow, the natural way.")
    essence = models.TextField(default="Soft. Elegant. Timeless. Made to make you glow.")
    mission_statement = models.TextField(blank=True)
    canonical_site_url = models.URLField(default="https://theglowmission.com")
    seo_title = models.CharField(
        max_length=180,
        default="The Glow Mission | Natural Facial Rituals in Chandivali, Powai",
    )
    seo_description = models.TextField(
        default=(
            "The Glow Mission is a boutique facial wellness studio in Chandivali and Powai, Mumbai, "
            "offering natural facial rituals, facial massage, face yoga, gua sha, and glow treatments."
        )
    )
    business_description = models.TextField(
        default=(
            "The Glow Mission is a boutique facial wellness studio built around natural ingredients, "
            "facial massage, face yoga, lifting techniques, calming rituals, and visible glow."
        )
    )
    area_served = models.CharField(max_length=180, default="Chandivali, Powai, Mumbai, India")
    same_as_links = models.JSONField(default=list, blank=True)
    opening_hours = models.JSONField(default=list, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    logo_image = models.ImageField(upload_to="brand/", blank=True, null=True)
    favicon = models.ImageField(upload_to="brand/", blank=True, null=True)
    primary_color = models.CharField(max_length=16, default="#D9B88C")
    background_color = models.CharField(max_length=16, default="#FFF7F0")
    surface_color = models.CharField(max_length=16, default="#F6EEE4")
    muted_color = models.CharField(max_length=16, default="#CDB8A9")
    accent_color = models.CharField(max_length=16, default="#E6D6C6")
    text_color = models.CharField(max_length=16, default="#2B2623")
    heading_font = models.CharField(max_length=120, default="Cinzel")
    body_font = models.CharField(max_length=120, default="Montserrat")
    cta_style = models.JSONField(default=dict, blank=True)
    contact_email = models.EmailField(blank=True)
    phone = models.CharField(max_length=80, blank=True)
    address = models.TextField(blank=True)
    instagram_handle = models.CharField(max_length=120, blank=True)
    social_links = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = "Brand settings"
        verbose_name_plural = "Brand settings"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError("Brand settings cannot be deleted.")

    def __str__(self) -> str:
        return self.site_title


class ImageVariant(TimeStampedModel):
    class Format(models.TextChoices):
        WEBP = "webp", "WebP"
        JPEG = "jpeg", "JPEG"

    source_key = models.CharField(max_length=512, db_index=True)
    variant_key = models.CharField(max_length=512, unique=True)
    width = models.PositiveIntegerField()
    height = models.PositiveIntegerField()
    format = models.CharField(max_length=16, choices=Format.choices)
    byte_size = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["source_key", "format", "width"]
        constraints = [
            models.UniqueConstraint(fields=["source_key", "width", "format"], name="unique_image_variant_size_format"),
        ]

    def __str__(self) -> str:
        return f"{self.source_key} {self.width}w {self.format}"


class HeroSlide(TimeStampedModel):
    title = models.CharField(max_length=220)
    subtitle = models.CharField(max_length=260, blank=True)
    body = models.TextField(blank=True)
    image = models.ImageField(upload_to="hero-slides/", blank=True, null=True)
    image_alt = models.CharField(max_length=220, blank=True)
    offer_label = models.CharField(max_length=120, blank=True)
    primary_cta_label = models.CharField(max_length=120, default="Book a consultation")
    primary_cta_url = models.CharField(max_length=240, default="/campaigns/glow-consultation")
    secondary_cta_label = models.CharField(max_length=120, blank=True)
    secondary_cta_url = models.CharField(max_length=240, blank=True)
    linked_campaign = models.ForeignKey(
        "campaigns.CampaignForm",
        related_name="hero_slides",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    schedule_enabled = models.BooleanField(default=False)
    starts_at = models.DateTimeField(blank=True, null=True)
    ends_at = models.DateTimeField(blank=True, null=True)
    active = models.BooleanField(default=True)
    ordering = models.PositiveIntegerField(default=0)
    config = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["ordering", "id"]

    @property
    def is_active_now(self) -> bool:
        now = timezone.now()
        if not self.active:
            return False
        if not self.schedule_enabled:
            return True
        if self.starts_at and self.starts_at > now:
            return False
        if self.ends_at and self.ends_at < now:
            return False
        return True

    def __str__(self) -> str:
        return self.title


class Page(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
        ARCHIVED = "archived", "Archived"

    title = models.CharField(max_length=180)
    slug = models.SlugField(unique=True, blank=True)
    status = models.CharField(max_length=24, choices=Status.choices, default=Status.DRAFT)
    seo_title = models.CharField(max_length=180, blank=True)
    seo_description = models.TextField(blank=True)
    ordering = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["ordering", "title"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.title


class PageSection(TimeStampedModel):
    class SectionType(models.TextChoices):
        HERO = "hero", "Hero"
        STORY = "story", "Story"
        SERVICES = "services", "Services"
        GALLERY = "gallery", "Gallery"
        TESTIMONIALS = "testimonials", "Testimonials"
        FAQS = "faqs", "FAQs"
        CTA = "cta", "CTA"
        RICH_TEXT = "rich_text", "Rich text"

    page = models.ForeignKey(Page, related_name="sections", on_delete=models.CASCADE)
    section_type = models.CharField(max_length=40, choices=SectionType.choices)
    eyebrow = models.CharField(max_length=140, blank=True)
    title = models.CharField(max_length=220, blank=True)
    subtitle = models.CharField(max_length=260, blank=True)
    body = models.TextField(blank=True)
    media = models.ImageField(upload_to="page-sections/", blank=True, null=True)
    media_alt = models.CharField(max_length=220, blank=True)
    cta_label = models.CharField(max_length=120, blank=True)
    cta_url = models.CharField(max_length=240, blank=True)
    cta_style = models.CharField(max_length=40, blank=True)
    secondary_cta_label = models.CharField(max_length=120, blank=True)
    secondary_cta_url = models.CharField(max_length=240, blank=True)
    secondary_cta_style = models.CharField(max_length=40, blank=True)
    layout_variant = models.CharField(max_length=80, blank=True)
    background_variant = models.CharField(max_length=80, blank=True)
    ordering = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)
    config = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["ordering", "id"]

    def __str__(self) -> str:
        return f"{self.page.slug}: {self.section_type}"


class Service(TimeStampedModel):
    title = models.CharField(max_length=180)
    slug = models.SlugField(unique=True, blank=True)
    short_description = models.CharField(max_length=260)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="services/", blank=True, null=True)
    image_alt = models.CharField(max_length=220, blank=True)
    duration = models.CharField(max_length=80, blank=True)
    session_count = models.PositiveSmallIntegerField(default=1)
    currency = models.CharField(max_length=8, default="INR")
    price_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    sale_price_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    discount_label = models.CharField(max_length=120, blank=True)
    price_note = models.CharField(max_length=160, blank=True)
    inclusions = models.JSONField(default=list, blank=True)
    featured = models.BooleanField(default=False)
    cta_label = models.CharField(max_length=120, default="Book this ritual")
    cta_url = models.CharField(max_length=240, blank=True)
    calendly_event_url = models.URLField(max_length=300, blank=True)
    booking_campaign = models.ForeignKey(
        "campaigns.CampaignForm",
        related_name="services",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    active = models.BooleanField(default=True)
    ordering = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["ordering", "title"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.title


class Testimonial(TimeStampedModel):
    name = models.CharField(max_length=160)
    quote = models.TextField()
    role = models.CharField(max_length=120, blank=True)
    is_anonymized = models.BooleanField(default=True)
    active = models.BooleanField(default=True)
    ordering = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["ordering", "name"]

    def __str__(self) -> str:
        return self.name


class FAQ(TimeStampedModel):
    question = models.CharField(max_length=240)
    answer = models.TextField()
    active = models.BooleanField(default=True)
    ordering = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["ordering", "question"]

    def __str__(self) -> str:
        return self.question


class GalleryImage(TimeStampedModel):
    title = models.CharField(max_length=180)
    alt_text = models.CharField(max_length=220, blank=True)
    image = models.ImageField(upload_to="gallery/", blank=True, null=True)
    caption = models.CharField(max_length=260, blank=True)
    active = models.BooleanField(default=True)
    ordering = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["ordering", "title"]

    def __str__(self) -> str:
        return self.title


class MediaAsset(TimeStampedModel):
    title = models.CharField(max_length=180)
    file = models.FileField(upload_to="media-assets/")
    alt_text = models.CharField(max_length=220, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title


class SiteNavigationItem(TimeStampedModel):
    class Placement(models.TextChoices):
        HEADER = "header", "Header navigation"
        HEADER_CTA = "header_cta", "Header CTA"
        FOOTER = "footer", "Footer navigation"
        FOOTER_CTA = "footer_cta", "Footer CTA"
        FOOTER_CONTACT = "footer_contact", "Footer contact"
        SOCIAL = "social", "Social link"

    class Style(models.TextChoices):
        LINK = "link", "Link"
        PRIMARY = "primary", "Primary button"
        SECONDARY = "secondary", "Secondary button"
        MUTED = "muted", "Muted"

    label = models.CharField(max_length=120)
    url = models.CharField(max_length=240)
    placement = models.CharField(max_length=32, choices=Placement.choices, default=Placement.HEADER)
    style = models.CharField(max_length=32, choices=Style.choices, default=Style.LINK)
    open_in_new_tab = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    ordering = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["placement", "ordering", "id"]

    def __str__(self) -> str:
        return f"{self.get_placement_display()}: {self.label}"
