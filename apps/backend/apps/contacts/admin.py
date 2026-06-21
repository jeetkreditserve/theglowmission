from django.contrib import admin

from apps.contacts.models import Contact, ContactAuditEvent, ContactNote, ContactStatus


@admin.register(ContactStatus)
class ContactStatusAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "ordering", "is_default", "updated_at"]
    list_editable = ["ordering", "is_default"]
    prepopulated_fields = {"slug": ("name",)}


class ContactNoteInline(admin.TabularInline):
    model = ContactNote
    extra = 0
    readonly_fields = ["created_at", "updated_at"]


class ContactAuditEventInline(admin.TabularInline):
    model = ContactAuditEvent
    extra = 0
    readonly_fields = ["event_type", "field_name", "old_value", "new_value", "source_type", "source_id", "actor", "message", "created_at"]
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ["display_name", "email", "phone", "status", "marketing_consent", "last_activity_at", "is_merged"]
    list_filter = ["status", "marketing_consent", "is_merged"]
    search_fields = ["full_name", "email", "phone", "address"]
    readonly_fields = ["normalized_email", "normalized_phone", "source_response_count", "first_activity_at", "last_activity_at", "merged_into", "merged_at"]
    inlines = [ContactNoteInline, ContactAuditEventInline]
