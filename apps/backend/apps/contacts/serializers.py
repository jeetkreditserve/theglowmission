from __future__ import annotations

from django.core.validators import validate_email
from rest_framework import serializers

from apps.common.form_validation import validate_digit_phone
from apps.common.storage import file_key, file_url
from apps.contacts.models import Contact, ContactAuditEvent, ContactHistoryEntry, ContactNote, ContactStatus
from apps.contacts.services import default_contact_status, normalize_email, normalize_phone, possible_duplicate_contacts


class ContactStatusSerializer(serializers.ModelSerializer):
    contact_count = serializers.IntegerField(source="contacts.count", read_only=True)

    class Meta:
        model = ContactStatus
        fields = ["id", "name", "slug", "ordering", "is_default", "contact_count", "updated_at"]
        read_only_fields = ["contact_count", "updated_at"]
        extra_kwargs = {"slug": {"required": False, "allow_blank": True}}


class ContactSummarySerializer(serializers.ModelSerializer):
    status_name = serializers.CharField(source="status.name", read_only=True)
    display_name = serializers.CharField(read_only=True)

    class Meta:
        model = Contact
        fields = [
            "id",
            "display_name",
            "full_name",
            "email",
            "phone",
            "status",
            "status_name",
            "marketing_consent",
            "last_activity_at",
            "source_response_count",
            "is_merged",
        ]


class ContactAuditEventSerializer(serializers.ModelSerializer):
    actor_email = serializers.EmailField(source="actor.email", read_only=True)

    class Meta:
        model = ContactAuditEvent
        fields = [
            "id",
            "event_type",
            "field_name",
            "old_value",
            "new_value",
            "source_type",
            "source_id",
            "actor_email",
            "message",
            "created_at",
        ]


class ContactNoteSerializer(serializers.ModelSerializer):
    created_by_email = serializers.EmailField(source="created_by.email", read_only=True)

    class Meta:
        model = ContactNote
        fields = ["id", "contact", "body", "created_by_email", "created_at", "updated_at"]
        read_only_fields = ["created_by_email", "created_at", "updated_at"]


class ContactHistoryEntrySerializer(serializers.ModelSerializer):
    contact_display_name = serializers.CharField(source="contact.display_name", read_only=True)
    appointment_starts_at = serializers.DateTimeField(source="appointment.starts_at", read_only=True)
    appointment_status = serializers.CharField(source="appointment.status", read_only=True)
    created_by_email = serializers.EmailField(source="created_by.email", read_only=True)
    before_photo_url = serializers.SerializerMethodField()
    before_photo_key = serializers.SerializerMethodField()
    after_photo_url = serializers.SerializerMethodField()
    after_photo_key = serializers.SerializerMethodField()

    class Meta:
        model = ContactHistoryEntry
        fields = [
            "id",
            "contact",
            "contact_display_name",
            "appointment",
            "appointment_starts_at",
            "appointment_status",
            "event_at",
            "service_label",
            "amount",
            "notes",
            "before_photo",
            "before_photo_url",
            "before_photo_key",
            "after_photo",
            "after_photo_url",
            "after_photo_key",
            "created_by",
            "created_by_email",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_by", "created_by_email", "created_at", "updated_at"]
        extra_kwargs = {
            "service_label": {"required": False, "allow_blank": True},
            "amount": {"required": False, "allow_null": True},
            "notes": {"required": False, "allow_blank": True},
            "appointment": {"required": False, "allow_null": True},
            "before_photo": {"required": False, "allow_null": True},
            "after_photo": {"required": False, "allow_null": True},
        }

    def validate(self, attrs):
        appointment = attrs.get("appointment", getattr(self.instance, "appointment", None))
        contact = attrs.get("contact", getattr(self.instance, "contact", None))
        if appointment and contact and appointment.contact_id and appointment.contact_id != contact.pk:
            raise serializers.ValidationError({"appointment": "Appointment belongs to a different contact."})
        if appointment and not attrs.get("service_label") and not getattr(self.instance, "service_label", ""):
            attrs["service_label"] = appointment.service.title
        return attrs

    def get_before_photo_url(self, obj):
        return file_url(obj.before_photo.image) if obj.before_photo_id and obj.before_photo else None

    def get_before_photo_key(self, obj):
        return file_key(obj.before_photo.image) if obj.before_photo_id and obj.before_photo else None

    def get_after_photo_url(self, obj):
        return file_url(obj.after_photo.image) if obj.after_photo_id and obj.after_photo else None

    def get_after_photo_key(self, obj):
        return file_key(obj.after_photo.image) if obj.after_photo_id and obj.after_photo else None


class ContactSerializer(serializers.ModelSerializer):
    status_name = serializers.CharField(source="status.name", read_only=True)
    display_name = serializers.CharField(read_only=True)
    notes = ContactNoteSerializer(many=True, read_only=True)
    audit_events = ContactAuditEventSerializer(many=True, read_only=True)
    history_entries = ContactHistoryEntrySerializer(many=True, read_only=True)
    appointments = serializers.SerializerMethodField()
    appointment_count = serializers.SerializerMethodField()
    completed_appointment_count = serializers.SerializerMethodField()
    photo_count = serializers.SerializerMethodField()
    possible_duplicate_count = serializers.SerializerMethodField()
    possible_duplicates = serializers.SerializerMethodField()

    class Meta:
        model = Contact
        fields = [
            "id",
            "display_name",
            "full_name",
            "email",
            "phone",
            "address",
            "age",
            "skin_type",
            "preferred_ritual",
            "preferred_day",
            "skin_goal",
            "marketing_consent",
            "status",
            "status_name",
            "first_activity_at",
            "last_activity_at",
            "source_response_count",
            "is_merged",
            "merged_into",
            "merged_at",
            "possible_duplicate_count",
            "possible_duplicates",
            "notes",
            "audit_events",
            "history_entries",
            "appointments",
            "appointment_count",
            "completed_appointment_count",
            "photo_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "display_name",
            "first_activity_at",
            "last_activity_at",
            "source_response_count",
            "is_merged",
            "merged_into",
            "merged_at",
            "possible_duplicate_count",
            "possible_duplicates",
            "notes",
            "audit_events",
            "history_entries",
            "appointments",
            "appointment_count",
            "completed_appointment_count",
            "photo_count",
            "created_at",
            "updated_at",
        ]
        extra_kwargs = {
            "email": {"required": False, "allow_blank": True},
            "phone": {"required": False, "allow_blank": True},
            "full_name": {"required": False, "allow_blank": True},
            "address": {"required": False, "allow_blank": True},
            "skin_type": {"required": False, "allow_blank": True},
            "preferred_ritual": {"required": False, "allow_blank": True},
            "preferred_day": {"required": False, "allow_blank": True},
            "skin_goal": {"required": False, "allow_blank": True},
        }

    def validate_email(self, value):
        value = normalize_email(value)
        if value:
            validate_email(value)
        return value

    def validate_phone(self, value):
        if not value:
            return ""
        cleaned, error = validate_digit_phone(value)
        if error:
            raise serializers.ValidationError(error)
        return cleaned

    def validate(self, attrs):
        values = self.current_values(attrs)
        if not self.instance and not values.get("phone"):
            raise serializers.ValidationError({"phone": "New contacts require a phone number."})
        if not any(values.get(field) for field in ["full_name", "email", "phone", "address"]):
            raise serializers.ValidationError("A contact needs at least one identity field.")

        normalized_email = normalize_email(values.get("email"))
        if normalized_email:
            queryset = Contact.objects.filter(is_merged=False, normalized_email=normalized_email)
            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise serializers.ValidationError({"email": "This email already belongs to another contact."})

        normalized_phone = normalize_phone(values.get("phone"))
        if normalized_phone:
            queryset = Contact.objects.filter(is_merged=False, normalized_phone=normalized_phone)
            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise serializers.ValidationError({"phone": "This phone already belongs to another contact."})
        return attrs

    def current_values(self, attrs):
        fields = ["full_name", "email", "phone", "address"]
        values = {}
        for field in fields:
            if field in attrs:
                values[field] = attrs[field]
            elif self.instance:
                values[field] = getattr(self.instance, field)
            else:
                values[field] = ""
        return values

    def get_appointments(self, obj):
        appointments = obj.appointments.select_related("service").prefetch_related("photos").all()
        return [
            {
                "id": appointment.pk,
                "service": appointment.service_id,
                "service_title": appointment.service.title if appointment.service_id else "",
                "service_slug": appointment.service.slug if appointment.service_id else "",
                "contact": appointment.contact_id,
                "contact_display_name": obj.display_name,
                "full_name": appointment.full_name,
                "phone": appointment.phone,
                "email": appointment.email,
                "skin_goal": appointment.skin_goal,
                "customer_notes": appointment.customer_notes,
                "starts_at": appointment.starts_at,
                "ends_at": appointment.ends_at,
                "status": appointment.status,
                "source": appointment.source,
                "photo_count": appointment.photos.count(),
                "created_at": appointment.created_at,
                "updated_at": appointment.updated_at,
            }
            for appointment in appointments
        ]

    def get_appointment_count(self, obj):
        return obj.appointments.count()

    def get_completed_appointment_count(self, obj):
        return obj.appointments.filter(status="completed").count()

    def get_photo_count(self, obj):
        return sum(appointment.photos.count() for appointment in obj.appointments.prefetch_related("photos").all())

    def create(self, validated_data):
        validated_data["normalized_email"] = normalize_email(validated_data.get("email"))
        validated_data["normalized_phone"] = normalize_phone(validated_data.get("phone"))
        if not validated_data.get("status"):
            validated_data["status"] = default_contact_status()
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if "email" in validated_data:
            validated_data["normalized_email"] = normalize_email(validated_data.get("email"))
        if "phone" in validated_data:
            validated_data["normalized_phone"] = normalize_phone(validated_data.get("phone"))
        return super().update(instance, validated_data)

    def get_possible_duplicate_count(self, obj):
        return possible_duplicate_contacts(obj).count()

    def get_possible_duplicates(self, obj):
        request = self.context.get("request")
        if request and request.parser_context and request.parser_context.get("kwargs", {}).get("pk"):
            return ContactSummarySerializer(possible_duplicate_contacts(obj)[:8], many=True).data
        return []
