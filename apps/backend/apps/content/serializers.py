from __future__ import annotations

from rest_framework import serializers
from django.utils.text import slugify

from apps.common.form_validation import validate_digit_phone
from apps.common.image_variants import image_variant_set
from apps.common.storage import file_key, file_url
from apps.content.models import (
    BrandSettings,
    FAQ,
    GalleryImage,
    HeroSlide,
    MediaAsset,
    Page,
    PageSection,
    Service,
    SiteNavigationItem,
    Testimonial,
)


class S3FileMixin:
    def get_url_for(self, obj, field_name: str):
        return file_url(getattr(obj, field_name))

    def get_key_for(self, obj, field_name: str):
        return file_key(getattr(obj, field_name))

    def get_variants_for(self, obj, field_name: str):
        return image_variant_set(getattr(obj, field_name))


class BrandSettingsSerializer(S3FileMixin, serializers.ModelSerializer):
    logo_url = serializers.SerializerMethodField()
    logo_key = serializers.SerializerMethodField()
    logo_variants = serializers.SerializerMethodField()
    favicon_url = serializers.SerializerMethodField()
    favicon_key = serializers.SerializerMethodField()
    favicon_variants = serializers.SerializerMethodField()

    class Meta:
        model = BrandSettings
        fields = [
            "id",
            "site_title",
            "tagline",
            "essence",
            "mission_statement",
            "canonical_site_url",
            "seo_title",
            "seo_description",
            "business_description",
            "area_served",
            "same_as_links",
            "opening_hours",
            "latitude",
            "longitude",
            "logo_image",
            "logo_url",
            "logo_key",
            "logo_variants",
            "favicon",
            "favicon_url",
            "favicon_key",
            "favicon_variants",
            "primary_color",
            "background_color",
            "surface_color",
            "muted_color",
            "accent_color",
            "text_color",
            "heading_font",
            "body_font",
            "cta_style",
            "contact_email",
            "phone",
            "address",
            "instagram_handle",
            "social_links",
            "updated_at",
        ]
        read_only_fields = ["id", "logo_url", "logo_key", "logo_variants", "favicon_url", "favicon_key", "favicon_variants", "updated_at"]
        extra_kwargs = {
            "logo_image": {"write_only": True, "required": False},
            "favicon": {"write_only": True, "required": False},
        }

    def get_logo_url(self, obj):
        return self.get_url_for(obj, "logo_image")

    def get_logo_key(self, obj):
        return self.get_key_for(obj, "logo_image")

    def get_logo_variants(self, obj):
        return self.get_variants_for(obj, "logo_image")

    def get_favicon_url(self, obj):
        return self.get_url_for(obj, "favicon")

    def get_favicon_key(self, obj):
        return self.get_key_for(obj, "favicon")

    def get_favicon_variants(self, obj):
        return self.get_variants_for(obj, "favicon")

    def validate_phone(self, value):
        cleaned, error = validate_digit_phone(value)
        if error:
            raise serializers.ValidationError(error)
        return cleaned


class HeroSlideSerializer(S3FileMixin, serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    image_key = serializers.SerializerMethodField()
    image_variants = serializers.SerializerMethodField()
    campaign_slug = serializers.CharField(source="linked_campaign.slug", read_only=True)
    campaign_title = serializers.CharField(source="linked_campaign.title", read_only=True)
    is_active_now = serializers.BooleanField(read_only=True)

    class Meta:
        model = HeroSlide
        fields = [
            "id",
            "title",
            "subtitle",
            "body",
            "image",
            "image_url",
            "image_key",
            "image_variants",
            "image_alt",
            "offer_label",
            "primary_cta_label",
            "primary_cta_url",
            "secondary_cta_label",
            "secondary_cta_url",
            "linked_campaign",
            "campaign_slug",
            "campaign_title",
            "schedule_enabled",
            "starts_at",
            "ends_at",
            "active",
            "is_active_now",
            "ordering",
            "config",
            "updated_at",
        ]
        read_only_fields = ["image_url", "image_key", "image_variants", "campaign_slug", "campaign_title", "is_active_now", "updated_at"]
        extra_kwargs = {"image": {"write_only": True, "required": False}}

    def validate(self, attrs):
        schedule_enabled = attrs.get("schedule_enabled", getattr(self.instance, "schedule_enabled", False))
        starts_at = attrs.get("starts_at", getattr(self.instance, "starts_at", None))
        ends_at = attrs.get("ends_at", getattr(self.instance, "ends_at", None))
        if schedule_enabled and not starts_at and not ends_at:
            raise serializers.ValidationError({"starts_at": "Add a start or end date, or turn scheduling off."})
        if starts_at and ends_at and ends_at <= starts_at:
            raise serializers.ValidationError({"ends_at": "End date must be after the start date."})
        return attrs

    def get_image_url(self, obj):
        return self.get_url_for(obj, "image")

    def get_image_key(self, obj):
        return self.get_key_for(obj, "image")

    def get_image_variants(self, obj):
        return self.get_variants_for(obj, "image")


class PageSectionSerializer(S3FileMixin, serializers.ModelSerializer):
    media_url = serializers.SerializerMethodField()
    media_key = serializers.SerializerMethodField()
    media_variants = serializers.SerializerMethodField()

    class Meta:
        model = PageSection
        fields = [
            "id",
            "page",
            "section_type",
            "eyebrow",
            "title",
            "subtitle",
            "body",
            "media",
            "media_url",
            "media_key",
            "media_variants",
            "media_alt",
            "cta_label",
            "cta_url",
            "cta_style",
            "secondary_cta_label",
            "secondary_cta_url",
            "secondary_cta_style",
            "layout_variant",
            "background_variant",
            "ordering",
            "active",
            "config",
        ]
        read_only_fields = ["media_url", "media_key", "media_variants"]
        extra_kwargs = {"media": {"write_only": True, "required": False}}

    def get_media_url(self, obj):
        return self.get_url_for(obj, "media")

    def get_media_key(self, obj):
        return self.get_key_for(obj, "media")

    def get_media_variants(self, obj):
        return self.get_variants_for(obj, "media")


class PageSerializer(serializers.ModelSerializer):
    sections = PageSectionSerializer(many=True, read_only=True)

    class Meta:
        model = Page
        fields = ["id", "title", "slug", "status", "seo_title", "seo_description", "ordering", "sections", "updated_at"]
        read_only_fields = ["updated_at"]
        extra_kwargs = {"slug": {"required": False, "allow_blank": True}}

    def validate(self, attrs):
        title = attrs.get("title", getattr(self.instance, "title", ""))
        slug = attrs.get("slug", getattr(self.instance, "slug", ""))
        if not slug and title:
            slug = slugify(title)
            attrs["slug"] = slug
        if slug:
            queryset = Page.objects.filter(slug=slug)
            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise serializers.ValidationError({"slug": "A page with this slug already exists."})
        return attrs


class ServiceSerializer(S3FileMixin, serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    image_key = serializers.SerializerMethodField()
    image_variants = serializers.SerializerMethodField()
    booking_campaign_slug = serializers.CharField(source="booking_campaign.slug", read_only=True)

    class Meta:
        model = Service
        fields = [
            "id",
            "title",
            "slug",
            "short_description",
            "description",
            "image",
            "image_url",
            "image_key",
            "image_variants",
            "image_alt",
            "duration",
            "session_count",
            "currency",
            "price_amount",
            "sale_price_amount",
            "discount_label",
            "price_note",
            "inclusions",
            "featured",
            "cta_label",
            "cta_url",
            "calendly_event_url",
            "booking_campaign",
            "booking_campaign_slug",
            "active",
            "ordering",
            "updated_at",
        ]
        read_only_fields = ["image_url", "image_key", "image_variants", "booking_campaign_slug", "updated_at"]
        extra_kwargs = {
            "image": {"write_only": True, "required": False},
            "slug": {"required": False, "allow_blank": True},
        }

    def validate(self, attrs):
        title = attrs.get("title", getattr(self.instance, "title", ""))
        slug = attrs.get("slug", getattr(self.instance, "slug", ""))
        if not slug and title:
            slug = slugify(title)
            attrs["slug"] = slug
        if slug:
            queryset = Service.objects.filter(slug=slug)
            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise serializers.ValidationError({"slug": "A service with this slug already exists."})
        price_amount = attrs.get("price_amount", getattr(self.instance, "price_amount", None))
        sale_price_amount = attrs.get("sale_price_amount", getattr(self.instance, "sale_price_amount", None))
        if price_amount is not None and sale_price_amount is not None and sale_price_amount > price_amount:
            raise serializers.ValidationError({"sale_price_amount": "Sale price cannot be higher than the regular price."})
        return attrs

    def get_image_url(self, obj):
        return self.get_url_for(obj, "image")

    def get_image_key(self, obj):
        return self.get_key_for(obj, "image")

    def get_image_variants(self, obj):
        return self.get_variants_for(obj, "image")


class RitualBookingLeadSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=180, trim_whitespace=True)
    phone = serializers.CharField(max_length=32, trim_whitespace=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    skin_goal = serializers.CharField(required=False, allow_blank=True, trim_whitespace=True)

    def validate_phone(self, value):
        cleaned, error = validate_digit_phone(value)
        if error:
            raise serializers.ValidationError(error)
        return cleaned


class TestimonialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Testimonial
        fields = ["id", "name", "quote", "role", "is_anonymized", "active", "ordering", "updated_at"]
        read_only_fields = ["updated_at"]


class SiteNavigationItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteNavigationItem
        fields = [
            "id",
            "label",
            "url",
            "placement",
            "style",
            "open_in_new_tab",
            "active",
            "ordering",
            "updated_at",
        ]
        read_only_fields = ["updated_at"]


class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = ["id", "question", "answer", "active", "ordering", "updated_at"]
        read_only_fields = ["updated_at"]


class GalleryImageSerializer(S3FileMixin, serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    image_key = serializers.SerializerMethodField()
    image_variants = serializers.SerializerMethodField()

    class Meta:
        model = GalleryImage
        fields = ["id", "title", "alt_text", "image", "image_url", "image_key", "image_variants", "caption", "active", "ordering", "updated_at"]
        read_only_fields = ["image_url", "image_key", "image_variants", "updated_at"]
        extra_kwargs = {"image": {"write_only": True, "required": False}}

    def get_image_url(self, obj):
        return self.get_url_for(obj, "image")

    def get_image_key(self, obj):
        return self.get_key_for(obj, "image")

    def get_image_variants(self, obj):
        return self.get_variants_for(obj, "image")


class MediaAssetSerializer(S3FileMixin, serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    file_key = serializers.SerializerMethodField()
    file_variants = serializers.SerializerMethodField()

    class Meta:
        model = MediaAsset
        fields = ["id", "title", "file", "file_url", "file_key", "file_variants", "alt_text", "metadata", "created_at"]
        read_only_fields = ["file_url", "file_key", "file_variants", "created_at"]
        extra_kwargs = {"file": {"write_only": True}}

    def get_file_url(self, obj):
        return self.get_url_for(obj, "file")

    def get_file_key(self, obj):
        return self.get_key_for(obj, "file")

    def get_file_variants(self, obj):
        return self.get_variants_for(obj, "file")
