from django.contrib import admin

from apps.content.models import BrandSettings, FAQ, GalleryImage, HeroSlide, MediaAsset, Page, PageSection, Service, Testimonial


class PageSectionInline(admin.TabularInline):
    model = PageSection
    extra = 0


@admin.register(BrandSettings)
class BrandSettingsAdmin(admin.ModelAdmin):
    list_display = ["site_title", "tagline", "updated_at"]


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ["title", "slug", "status", "ordering", "updated_at"]
    list_filter = ["status"]
    prepopulated_fields = {"slug": ("title",)}
    inlines = [PageSectionInline]


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ["title", "slug", "featured", "active", "ordering"]
    list_filter = ["active", "featured"]
    prepopulated_fields = {"slug": ("title",)}


@admin.register(HeroSlide)
class HeroSlideAdmin(admin.ModelAdmin):
    list_display = ["title", "offer_label", "active", "ordering", "starts_at", "ends_at"]
    list_filter = ["active"]


admin.site.register(Testimonial)
admin.site.register(FAQ)
admin.site.register(GalleryImage)
admin.site.register(MediaAsset)
