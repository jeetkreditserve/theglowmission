from __future__ import annotations

from rest_framework import serializers

from apps.common.storage import file_key, file_url
from apps.content.models import BrandSettings, FAQ, GalleryImage, HeroSlide, MediaAsset, Page, PageSection, Service, Testimonial


class S3FileMixin:
    def get_url_for(self, obj, field_name: str):
        return file_url(getattr(obj, field_name))

    def get_key_for(self, obj, field_name: str):
        return file_key(getattr(obj, field_name))


class BrandSettingsSerializer(S3FileMixin, serializers.ModelSerializer):
    logo_url = serializers.SerializerMethodField()
    logo_key = serializers.SerializerMethodField()
    favicon_url = serializers.SerializerMethodField()
    favicon_key = serializers.SerializerMethodField()

    class Meta:
        model = BrandSettings
        fields = [
            "id",
            "site_title",
            "tagline",
            "essence",
            "mission_statement",
            "logo_image",
            "logo_url",
            "logo_key",
            "favicon",
            "favicon_url",
            "favicon_key",
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
        read_only_fields = ["id", "logo_url", "logo_key", "favicon_url", "favicon_key", "updated_at"]

    def get_logo_url(self, obj):
        return self.get_url_for(obj, "logo_image")

    def get_logo_key(self, obj):
        return self.get_key_for(obj, "logo_image")

    def get_favicon_url(self, obj):
        return self.get_url_for(obj, "favicon")

    def get_favicon_key(self, obj):
        return self.get_key_for(obj, "favicon")


class HeroSlideSerializer(S3FileMixin, serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    image_key = serializers.SerializerMethodField()
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
            "image_alt",
            "offer_label",
            "primary_cta_label",
            "primary_cta_url",
            "secondary_cta_label",
            "secondary_cta_url",
            "linked_campaign",
            "campaign_slug",
            "campaign_title",
            "starts_at",
            "ends_at",
            "active",
            "is_active_now",
            "ordering",
            "config",
            "updated_at",
        ]
        read_only_fields = ["image_url", "image_key", "campaign_slug", "campaign_title", "is_active_now", "updated_at"]

    def get_image_url(self, obj):
        return self.get_url_for(obj, "image")

    def get_image_key(self, obj):
        return self.get_key_for(obj, "image")


class PageSectionSerializer(S3FileMixin, serializers.ModelSerializer):
    media_url = serializers.SerializerMethodField()
    media_key = serializers.SerializerMethodField()

    class Meta:
        model = PageSection
        fields = [
            "id",
            "page",
            "section_type",
            "title",
            "subtitle",
            "body",
            "media",
            "media_url",
            "media_key",
            "cta_label",
            "cta_url",
            "ordering",
            "active",
            "config",
        ]
        read_only_fields = ["media_url", "media_key"]

    def get_media_url(self, obj):
        return self.get_url_for(obj, "media")

    def get_media_key(self, obj):
        return self.get_key_for(obj, "media")


class PageSerializer(serializers.ModelSerializer):
    sections = PageSectionSerializer(many=True, read_only=True)

    class Meta:
        model = Page
        fields = ["id", "title", "slug", "status", "seo_title", "seo_description", "ordering", "sections", "updated_at"]
        read_only_fields = ["updated_at"]


class ServiceSerializer(S3FileMixin, serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    image_key = serializers.SerializerMethodField()
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
            "booking_campaign",
            "booking_campaign_slug",
            "active",
            "ordering",
            "updated_at",
        ]
        read_only_fields = ["image_url", "image_key", "booking_campaign_slug", "updated_at"]

    def get_image_url(self, obj):
        return self.get_url_for(obj, "image")

    def get_image_key(self, obj):
        return self.get_key_for(obj, "image")


class TestimonialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Testimonial
        fields = ["id", "name", "quote", "role", "active", "ordering", "updated_at"]
        read_only_fields = ["updated_at"]


class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = ["id", "question", "answer", "active", "ordering", "updated_at"]
        read_only_fields = ["updated_at"]


class GalleryImageSerializer(S3FileMixin, serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    image_key = serializers.SerializerMethodField()

    class Meta:
        model = GalleryImage
        fields = ["id", "title", "alt_text", "image", "image_url", "image_key", "caption", "active", "ordering", "updated_at"]
        read_only_fields = ["image_url", "image_key", "updated_at"]

    def get_image_url(self, obj):
        return self.get_url_for(obj, "image")

    def get_image_key(self, obj):
        return self.get_key_for(obj, "image")


class MediaAssetSerializer(S3FileMixin, serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    file_key = serializers.SerializerMethodField()

    class Meta:
        model = MediaAsset
        fields = ["id", "title", "file", "file_url", "file_key", "alt_text", "metadata", "created_at"]
        read_only_fields = ["file_url", "file_key", "created_at"]

    def get_file_url(self, obj):
        return self.get_url_for(obj, "file")

    def get_file_key(self, obj):
        return self.get_key_for(obj, "file")
