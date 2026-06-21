from __future__ import annotations

from django.core.validators import validate_email
from rest_framework import serializers

from apps.common.form_validation import validate_digit_phone
from apps.contacts.models import Contact, ContactAuditEvent, ContactNote, ContactStatus
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


class ContactSerializer(serializers.ModelSerializer):
    status_name = serializers.CharField(source="status.name", read_only=True)
    display_name = serializers.CharField(read_only=True)
    notes = ContactNoteSerializer(many=True, read_only=True)
    audit_events = ContactAuditEventSerializer(many=True, read_only=True)
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
        if not self.instance and not (values.get("email") or values.get("phone")):
            raise serializers.ValidationError("Manual contacts require an email or phone.")
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
