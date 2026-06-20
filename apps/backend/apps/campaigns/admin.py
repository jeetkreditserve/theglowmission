from django.contrib import admin

from apps.campaigns.models import CampaignForm, CampaignFormField, CampaignFormResponse


class CampaignFormFieldInline(admin.TabularInline):
    model = CampaignFormField
    extra = 0


@admin.register(CampaignForm)
class CampaignFormAdmin(admin.ModelAdmin):
    list_display = ["title", "slug", "status", "starts_at", "ends_at", "updated_at"]
    list_filter = ["status"]
    prepopulated_fields = {"slug": ("title",)}
    inlines = [CampaignFormFieldInline]


@admin.register(CampaignFormResponse)
class CampaignFormResponseAdmin(admin.ModelAdmin):
    list_display = ["form", "submitted_at"]
    readonly_fields = ["submitted_at", "response_data", "metadata", "field_snapshot"]

