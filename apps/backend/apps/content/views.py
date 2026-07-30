from __future__ import annotations

from django.conf import settings
from django.db.models import Max
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from apps.common.image_variants import ensure_image_variants
from apps.campaigns.models import CampaignForm, CampaignFormResponse
from apps.contacts.services import sync_campaign_response_to_contact
from apps.content.models import BrandSettings, FAQ, GalleryImage, HeroSlide, MediaAsset, Page, PageSection, Service, SiteNavigationItem, Testimonial
from apps.content.serializers import (
    BrandSettingsSerializer,
    FAQSerializer,
    GalleryImageSerializer,
    HeroSlideSerializer,
    MediaAssetSerializer,
    PageSectionSerializer,
    PageSerializer,
    RitualBookingLeadSerializer,
    ServiceSerializer,
    SiteNavigationItemSerializer,
    TestimonialSerializer,
)


class PublicBrandSettingsView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        brand, _ = BrandSettings.objects.get_or_create(pk=1)
        return Response(BrandSettingsSerializer(brand, context={"request": request}).data)


class PublicAppConfigView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        brand, _ = BrandSettings.objects.get_or_create(pk=1)
        pages = Page.objects.filter(status=Page.Status.PUBLISHED).prefetch_related(
            Prefetch("sections", queryset=PageSection.objects.filter(active=True).order_by("ordering", "id"))
        )
        services = Service.objects.filter(active=True).order_by("ordering", "title")
        navigation_items = SiteNavigationItem.objects.filter(active=True).order_by("placement", "ordering", "id")
        gallery = GalleryImage.objects.filter(active=True).order_by("ordering", "title")[:12]
        faqs = FAQ.objects.filter(active=True).order_by("ordering", "question")[:20]
        testimonials = Testimonial.objects.filter(active=True).order_by("ordering", "name")[:12]
        hero_slides = [slide for slide in HeroSlide.objects.select_related("linked_campaign").order_by("ordering", "id") if slide.is_active_now]
        return Response(
            {
                "schema_version": 1,
                "generated_at": timezone.now(),
                "content_version": latest_content_version(),
                "cache": {"max_age_seconds": getattr(settings, "APP_CONFIG_CACHE_SECONDS", 300)},
                "brand": app_brand_payload(brand, request),
                "theme": app_theme_payload(brand),
                "contact": app_contact_payload(brand),
                "navigation": grouped_navigation_payload(navigation_items),
                "feature_flags": app_feature_flags_payload(),
                "pages": PageSerializer(pages, many=True, context={"request": request}).data,
                "services": ServiceSerializer(services, many=True, context={"request": request}).data,
                "hero_slides": HeroSlideSerializer(hero_slides, many=True, context={"request": request}).data,
                "gallery": GalleryImageSerializer(gallery, many=True, context={"request": request}).data,
                "faqs": FAQSerializer(faqs, many=True).data,
                "testimonials": TestimonialSerializer(testimonials, many=True).data,
            }
        )


class PublicPageView(RetrieveAPIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = PageSerializer
    lookup_field = "slug"
    lookup_url_kwarg = "slug"

    def get_queryset(self):
        return Page.objects.filter(status=Page.Status.PUBLISHED).prefetch_related(
            Prefetch("sections", queryset=PageSection.objects.filter(active=True).order_by("ordering", "id"))
        )


class PublicServiceListView(ListAPIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = ServiceSerializer

    def get_queryset(self):
        return Service.objects.filter(active=True)


class PublicServiceDetailView(RetrieveAPIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = ServiceSerializer
    lookup_field = "slug"
    lookup_url_kwarg = "slug"

    def get_queryset(self):
        return Service.objects.filter(active=True)


class PublicServiceBookingLeadView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, slug: str):
        service = get_object_or_404(Service.objects.select_related("booking_campaign").filter(active=True), slug=slug)
        serializer = RitualBookingLeadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        form = service.booking_campaign or CampaignForm.objects.filter(slug="glow-consultation").first()
        if not form:
            return Response({"detail": "Booking form is not configured."}, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        response_data = {
            "full_name": data["full_name"],
            "phone": data["phone"],
            "email": data.get("email", ""),
            "preferred_ritual": service.title,
            "skin_goal": data.get("skin_goal", ""),
        }
        response = CampaignFormResponse.objects.create(
            form=form,
            response_data=response_data,
            metadata={
                "source": "ritual_booking",
                "service_id": service.pk,
                "service_slug": service.slug,
                "ip": request.META.get("HTTP_X_FORWARDED_FOR", request.META.get("REMOTE_ADDR", "")),
                "user_agent": request.META.get("HTTP_USER_AGENT", ""),
            },
            field_snapshot=ritual_booking_field_snapshot(),
        )
        sync_campaign_response_to_contact(response)
        return Response(
            {
                "id": response.pk,
                "contact": response.contact_id,
                "contact_sync_status": response.contact_sync_status,
                "message": "Your details have been saved. Choose a time that works for you.",
            },
            status=status.HTTP_201_CREATED,
        )


class PublicSeoIndexView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        items = []
        for page in Page.objects.filter(status=Page.Status.PUBLISHED).order_by("ordering", "title"):
            path = "/" if page.slug == "home" else f"/{page.slug}"
            items.append(
                {
                    "path": path,
                    "title": page.seo_title or page.title,
                    "description": page.seo_description,
                    "type": "page",
                    "updated_at": page.updated_at,
                    "priority": 1.0 if page.slug == "home" else 0.8,
                    "image_url": None,
                }
            )

        for service in Service.objects.filter(active=True).order_by("ordering", "title"):
            items.append(
                {
                    "path": f"/glow-rituals/{service.slug}",
                    "title": f"{service.title} | The Glow Mission",
                    "description": service.short_description,
                    "type": "service",
                    "updated_at": service.updated_at,
                    "priority": 0.75,
                    "image_url": ServiceSerializer(service, context={"request": request}).data.get("image_url"),
                }
            )

        for form in CampaignForm.objects.filter(status=CampaignForm.Status.PUBLISHED).order_by("-updated_at"):
            if not form.is_active_now:
                continue
            items.append(
                {
                    "path": f"/campaigns/{form.slug}",
                    "title": form.seo_title or form.title,
                    "description": form.seo_description or form.summary,
                    "type": "campaign",
                    "updated_at": form.updated_at,
                    "priority": 0.65,
                    "image_url": None,
                }
            )

        return Response(items)


def ritual_booking_field_snapshot():
    return [
        {"id": 0, "label": "Full name", "key": "full_name", "field_type": "text", "required": True, "options": [], "validation": {}, "ordering": 0},
        {"id": 0, "label": "Phone", "key": "phone", "field_type": "phone", "required": True, "options": [], "validation": {}, "ordering": 1},
        {"id": 0, "label": "Email", "key": "email", "field_type": "email", "required": False, "options": [], "validation": {}, "ordering": 2},
        {"id": 0, "label": "Preferred ritual", "key": "preferred_ritual", "field_type": "text", "required": False, "options": [], "validation": {}, "ordering": 3},
        {"id": 0, "label": "Skin goal", "key": "skin_goal", "field_type": "textarea", "required": False, "options": [], "validation": {}, "ordering": 4},
    ]


def app_brand_payload(brand: BrandSettings, request) -> dict:
    serializer = BrandSettingsSerializer(brand, context={"request": request})
    data = serializer.data
    return {
        "site_title": data["site_title"],
        "tagline": data["tagline"],
        "essence": data["essence"],
        "mission_statement": data["mission_statement"],
        "canonical_site_url": data["canonical_site_url"],
        "seo_title": data["seo_title"],
        "seo_description": data["seo_description"],
        "business_description": data["business_description"],
        "area_served": data["area_served"],
        "logo_url": data["logo_url"],
        "logo_variants": data["logo_variants"],
        "favicon_url": data["favicon_url"],
        "favicon_variants": data["favicon_variants"],
        "updated_at": data["updated_at"],
    }


def app_theme_payload(brand: BrandSettings) -> dict:
    return {
        "colors": {
            "primary": brand.primary_color,
            "background": brand.background_color,
            "surface": brand.surface_color,
            "muted": brand.muted_color,
            "accent": brand.accent_color,
            "text": brand.text_color,
        },
        "fonts": {
            "heading": brand.heading_font,
            "body": brand.body_font,
        },
        "cta_style": brand.cta_style or {},
    }


def app_contact_payload(brand: BrandSettings) -> dict:
    return {
        "email": brand.contact_email,
        "phone": brand.phone,
        "address": brand.address,
        "instagram_handle": brand.instagram_handle,
        "social_links": brand.social_links or {},
        "same_as_links": brand.same_as_links or [],
        "opening_hours": brand.opening_hours or [],
        "location": {
            "latitude": str(brand.latitude) if brand.latitude is not None else "",
            "longitude": str(brand.longitude) if brand.longitude is not None else "",
        },
    }


def grouped_navigation_payload(items) -> dict:
    grouped = {choice[0]: [] for choice in SiteNavigationItem.Placement.choices}
    for item in items:
        grouped.setdefault(item.placement, []).append(SiteNavigationItemSerializer(item).data)
    return grouped


def app_feature_flags_payload() -> dict:
    return {
        "customer_registration": getattr(settings, "CUSTOMER_REGISTRATION_ENABLED", True),
        "customer_password_reset": True,
        "customer_notifications": getattr(settings, "CUSTOMER_NOTIFICATIONS_ENABLED", True),
        "web_push": bool(getattr(settings, "WEB_PUSH_PUBLIC_KEY", "")),
        "native_push": getattr(settings, "CUSTOMER_NOTIFICATIONS_ENABLED", True),
        "calendly_booking": True,
        "first_party_scheduling": False,
    }


def latest_content_version():
    updated_values = []
    for model in [BrandSettings, Page, PageSection, Service, HeroSlide, GalleryImage, FAQ, Testimonial, SiteNavigationItem]:
        updated_at = model.objects.aggregate(value=Max("updated_at"))["value"]
        if updated_at:
            updated_values.append(updated_at)
    return max(updated_values) if updated_values else None


class PublicHeroSlideListView(ListAPIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = HeroSlideSerializer

    def get_queryset(self):
        return HeroSlide.objects.select_related("linked_campaign").all()

    def list(self, request, *args, **kwargs):
        slides = [slide for slide in self.get_queryset() if slide.is_active_now]
        serializer = self.get_serializer(slides, many=True)
        return Response(serializer.data)


class PublicGalleryListView(ListAPIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = GalleryImageSerializer

    def get_queryset(self):
        return GalleryImage.objects.filter(active=True)


class PublicFAQListView(ListAPIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = FAQSerializer

    def get_queryset(self):
        return FAQ.objects.filter(active=True)


class PublicTestimonialListView(ListAPIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = TestimonialSerializer

    def get_queryset(self):
        return Testimonial.objects.filter(active=True)


class PublicNavigationListView(ListAPIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = SiteNavigationItemSerializer

    def get_queryset(self):
        return SiteNavigationItem.objects.filter(active=True)


class AdminModelViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    parser_classes = [JSONParser, MultiPartParser, FormParser]


class ImageVariantGenerationMixin:
    image_variant_fields: tuple[str, ...] = ()

    def perform_create(self, serializer):
        instance = serializer.save()
        self.generate_image_variants(instance)

    def perform_update(self, serializer):
        instance = serializer.save()
        self.generate_image_variants(instance)

    def generate_image_variants(self, instance):
        for field_name in self.image_variant_fields:
            ensure_image_variants(getattr(instance, field_name, None))


class ReorderMixin:
    @action(detail=False, methods=["post"], url_path="reorder")
    def reorder(self, request):
        items = request.data.get("items", [])
        if not isinstance(items, list):
            return Response({"detail": "items must be a list."}, status=400)
        queryset = self.get_queryset()
        for item in items:
            item_id = item.get("id")
            ordering = item.get("ordering")
            if item_id is None or ordering is None:
                continue
            queryset.filter(pk=item_id).update(ordering=ordering)
        return Response({"status": "ok"})


class BrandSettingsViewSet(ImageVariantGenerationMixin, AdminModelViewSet):
    image_variant_fields = ("logo_image", "favicon")
    queryset = BrandSettings.objects.all()
    serializer_class = BrandSettingsSerializer

    def list(self, request, *args, **kwargs):
        brand, _ = BrandSettings.objects.get_or_create(pk=1)
        return Response([self.get_serializer(brand).data])


class PageViewSet(AdminModelViewSet):
    queryset = Page.objects.prefetch_related("sections").all()
    serializer_class = PageSerializer
    search_fields = ["title", "slug"]
    ordering_fields = ["ordering", "title", "updated_at"]


class HeroSlideViewSet(ReorderMixin, ImageVariantGenerationMixin, AdminModelViewSet):
    image_variant_fields = ("image",)
    queryset = HeroSlide.objects.select_related("linked_campaign").all()
    serializer_class = HeroSlideSerializer
    search_fields = ["title", "subtitle", "body", "offer_label"]
    ordering_fields = ["ordering", "updated_at", "starts_at", "ends_at"]


class PageSectionViewSet(ReorderMixin, ImageVariantGenerationMixin, AdminModelViewSet):
    image_variant_fields = ("media",)
    queryset = PageSection.objects.select_related("page").all()
    serializer_class = PageSectionSerializer
    search_fields = ["title", "page__title"]
    ordering_fields = ["ordering", "updated_at"]

    def get_queryset(self):
        queryset = super().get_queryset()
        page_id = self.request.query_params.get("page")
        if page_id:
            queryset = queryset.filter(page_id=page_id)
        return queryset


class ServiceViewSet(ReorderMixin, ImageVariantGenerationMixin, AdminModelViewSet):
    image_variant_fields = ("image",)
    queryset = Service.objects.select_related("booking_campaign").all()
    serializer_class = ServiceSerializer
    search_fields = ["title", "slug", "short_description"]
    ordering_fields = ["ordering", "title", "updated_at", "price_amount", "sale_price_amount"]


class TestimonialViewSet(AdminModelViewSet):
    queryset = Testimonial.objects.all()
    serializer_class = TestimonialSerializer
    search_fields = ["name", "quote"]
    ordering_fields = ["ordering", "updated_at"]


class FAQViewSet(ReorderMixin, AdminModelViewSet):
    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer
    search_fields = ["question", "answer"]
    ordering_fields = ["ordering", "updated_at"]


class GalleryImageViewSet(ReorderMixin, ImageVariantGenerationMixin, AdminModelViewSet):
    image_variant_fields = ("image",)
    queryset = GalleryImage.objects.all()
    serializer_class = GalleryImageSerializer
    search_fields = ["title", "caption", "alt_text"]
    ordering_fields = ["ordering", "updated_at"]


class MediaAssetViewSet(ImageVariantGenerationMixin, AdminModelViewSet):
    image_variant_fields = ("file",)
    queryset = MediaAsset.objects.all()
    serializer_class = MediaAssetSerializer
    search_fields = ["title", "alt_text"]
    ordering_fields = ["created_at"]


class SiteNavigationItemViewSet(ReorderMixin, AdminModelViewSet):
    queryset = SiteNavigationItem.objects.all()
    serializer_class = SiteNavigationItemSerializer
    search_fields = ["label", "url"]
    ordering_fields = ["placement", "ordering", "updated_at"]
