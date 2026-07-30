from django.contrib import admin

from apps.contacts.models import Contact, ContactAuditEvent, ContactHistoryEntry, ContactNote, ContactStatus


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


class ContactHistoryEntryInline(admin.TabularInline):
    model = ContactHistoryEntry
    extra = 0
    readonly_fields = ["created_at", "updated_at"]
    raw_id_fields = ["appointment", "before_photo", "after_photo", "created_by"]


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ["display_name", "email", "phone", "status", "marketing_consent", "last_activity_at", "is_merged"]
    list_filter = ["status", "marketing_consent", "is_merged"]
    search_fields = ["full_name", "email", "phone", "address"]
    readonly_fields = ["normalized_email", "normalized_phone", "source_response_count", "first_activity_at", "last_activity_at", "merged_into", "merged_at"]
    inlines = [ContactNoteInline, ContactHistoryEntryInline, ContactAuditEventInline]


@admin.register(ContactHistoryEntry)
class ContactHistoryEntryAdmin(admin.ModelAdmin):
    list_display = ["contact", "event_at", "service_label", "amount", "appointment", "created_by"]
    list_filter = ["event_at"]
    search_fields = ["contact__full_name", "contact__email", "contact__phone", "service_label", "notes"]
    raw_id_fields = ["contact", "appointment", "before_photo", "after_photo", "created_by"]
