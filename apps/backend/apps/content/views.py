from __future__ import annotations

from django.db.models import Prefetch
from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.image_variants import ensure_image_variants
from apps.content.models import BrandSettings, FAQ, GalleryImage, HeroSlide, MediaAsset, Page, PageSection, Service, Testimonial
from apps.content.serializers import (
    BrandSettingsSerializer,
    FAQSerializer,
    GalleryImageSerializer,
    HeroSlideSerializer,
    MediaAssetSerializer,
    PageSectionSerializer,
    PageSerializer,
    ServiceSerializer,
    TestimonialSerializer,
)


class PublicBrandSettingsView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        brand, _ = BrandSettings.objects.get_or_create(pk=1)
        return Response(BrandSettingsSerializer(brand, context={"request": request}).data)


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
