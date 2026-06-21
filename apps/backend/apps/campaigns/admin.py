from django.contrib import admin

from apps.campaigns.models import CampaignForm, CampaignFormField, CampaignFormResponse


class CampaignFormFieldInline(admin.TabularInline):
    model = CampaignFormField
    extra = 0


@admin.register(CampaignForm)
class CampaignFormAdmin(admin.ModelAdmin):
    list_display = ["title", "slug", "status", "schedule_enabled", "starts_at", "ends_at", "updated_at"]
    list_filter = ["status", "schedule_enabled"]
    prepopulated_fields = {"slug": ("title",)}
    inlines = [CampaignFormFieldInline]


@admin.register(CampaignFormResponse)
class CampaignFormResponseAdmin(admin.ModelAdmin):
    list_display = ["form", "contact", "contact_sync_status", "submitted_at"]
    readonly_fields = ["submitted_at", "response_data", "metadata", "field_snapshot", "contact_sync_status", "contact_sync_error"]
