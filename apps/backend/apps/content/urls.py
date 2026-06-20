from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.content.views import (
    BrandSettingsViewSet,
    FAQViewSet,
    GalleryImageViewSet,
    HeroSlideViewSet,
    MediaAssetViewSet,
    PageSectionViewSet,
    PageViewSet,
    PublicBrandSettingsView,
    PublicFAQListView,
    PublicGalleryListView,
    PublicHeroSlideListView,
    PublicPageView,
    PublicServiceListView,
    PublicTestimonialListView,
    ServiceViewSet,
    SiteNavigationItemViewSet,
    TestimonialViewSet,
    PublicNavigationListView,
)

router = DefaultRouter()
router.register("admin/brand-settings", BrandSettingsViewSet, basename="admin-brand-settings")
router.register("admin/hero-slides", HeroSlideViewSet, basename="admin-hero-slides")
router.register("admin/pages", PageViewSet, basename="admin-pages")
router.register("admin/page-sections", PageSectionViewSet, basename="admin-page-sections")
router.register("admin/services", ServiceViewSet, basename="admin-services")
router.register("admin/testimonials", TestimonialViewSet, basename="admin-testimonials")
router.register("admin/faqs", FAQViewSet, basename="admin-faqs")
router.register("admin/gallery", GalleryImageViewSet, basename="admin-gallery")
router.register("admin/media-assets", MediaAssetViewSet, basename="admin-media-assets")
router.register("admin/navigation-items", SiteNavigationItemViewSet, basename="admin-navigation-items")

urlpatterns = [
    path("public/brand-settings/", PublicBrandSettingsView.as_view(), name="public-brand-settings"),
    path("public/hero-slides/", PublicHeroSlideListView.as_view(), name="public-hero-slides"),
    path("public/pages/<slug:slug>/", PublicPageView.as_view(), name="public-page"),
    path("public/services/", PublicServiceListView.as_view(), name="public-services"),
    path("public/gallery/", PublicGalleryListView.as_view(), name="public-gallery"),
    path("public/faqs/", PublicFAQListView.as_view(), name="public-faqs"),
    path("public/testimonials/", PublicTestimonialListView.as_view(), name="public-testimonials"),
    path("public/navigation-items/", PublicNavigationListView.as_view(), name="public-navigation-items"),
    path("", include(router.urls)),
]
