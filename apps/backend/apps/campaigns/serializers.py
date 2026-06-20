from __future__ import annotations

from django.core.validators import validate_email
from rest_framework import serializers

from apps.common.storage import file_key, file_url
from apps.campaigns.models import CampaignForm, CampaignFormField, CampaignFormResponse


class S3FileMixin:
    def get_url_for(self, obj, field_name: str):
        return file_url(getattr(obj, field_name))

    def get_key_for(self, obj, field_name: str):
        return file_key(getattr(obj, field_name))


class CampaignFormFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampaignFormField
        fields = [
            "id",
            "form",
            "label",
            "key",
            "field_type",
            "placeholder",
            "help_text",
            "required",
            "options",
            "validation",
            "ordering",
            "active",
            "updated_at",
        ]
        read_only_fields = ["updated_at"]


class PublicCampaignFormFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampaignFormField
        fields = ["id", "label", "key", "field_type", "placeholder", "help_text", "required", "options", "validation", "ordering"]


class CampaignFormSerializer(S3FileMixin, serializers.ModelSerializer):
    fields = CampaignFormFieldSerializer(many=True, read_only=True)
    response_count = serializers.IntegerField(source="responses.count", read_only=True)
    is_active_now = serializers.BooleanField(read_only=True)
    hero_image_url = serializers.SerializerMethodField()
    hero_image_key = serializers.SerializerMethodField()

    class Meta:
        model = CampaignForm
        fields = [
            "id",
            "title",
            "slug",
            "status",
            "summary",
            "offer_label",
            "hero_image",
            "hero_image_url",
            "hero_image_key",
            "hero_image_alt",
            "button_label",
            "starts_at",
            "ends_at",
            "success_message",
            "redirect_url",
            "seo_title",
            "seo_description",
            "fields",
            "response_count",
            "is_active_now",
            "updated_at",
        ]
        read_only_fields = ["hero_image_url", "hero_image_key", "response_count", "is_active_now", "updated_at"]

    def get_hero_image_url(self, obj):
        return self.get_url_for(obj, "hero_image")

    def get_hero_image_key(self, obj):
        return self.get_key_for(obj, "hero_image")


class PublicCampaignFormSerializer(S3FileMixin, serializers.ModelSerializer):
    fields = PublicCampaignFormFieldSerializer(many=True, read_only=True)
    hero_image_url = serializers.SerializerMethodField()

    class Meta:
        model = CampaignForm
        fields = [
            "id",
            "title",
            "slug",
            "summary",
            "offer_label",
            "hero_image_url",
            "hero_image_alt",
            "button_label",
            "success_message",
            "redirect_url",
            "seo_title",
            "seo_description",
            "fields",
        ]

    def get_hero_image_url(self, obj):
        return self.get_url_for(obj, "hero_image")


class CampaignFormResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampaignFormResponse
        fields = ["id", "form", "submitted_at", "response_data", "metadata", "field_snapshot", "created_at"]
        read_only_fields = ["submitted_at", "created_at"]


class PublicCampaignResponseSerializer(serializers.Serializer):
    response_data = serializers.DictField()

    def validate_response_data(self, value):
        form = self.context["form"]
        active_fields = list(form.fields.filter(active=True))
        cleaned = {}
        errors = {}

        for field in active_fields:
            raw = value.get(field.key)
            if field.required and (raw is None or raw == "" or raw == []):
                errors[field.key] = "This field is required."
                continue
            if raw in (None, ""):
                cleaned[field.key] = raw
                continue

            if field.field_type == CampaignFormField.FieldType.EMAIL:
                try:
                    validate_email(str(raw))
                except Exception:
                    errors[field.key] = "Enter a valid email address."
            elif field.field_type == CampaignFormField.FieldType.NUMBER:
                try:
                    cleaned[field.key] = float(raw)
                    continue
                except (TypeError, ValueError):
                    errors[field.key] = "Enter a valid number."
            elif field.field_type in {CampaignFormField.FieldType.SELECT, CampaignFormField.FieldType.RADIO}:
                options = field.options or []
                if options and raw not in options:
                    errors[field.key] = "Select a valid option."
            elif field.field_type == CampaignFormField.FieldType.CHECKBOX:
                if not isinstance(raw, (bool, list)):
                    errors[field.key] = "Enter a valid checkbox value."

            cleaned[field.key] = raw

        if errors:
            raise serializers.ValidationError(errors)
        return cleaned

    def create(self, validated_data):
        form = self.context["form"]
        fields = list(form.fields.filter(active=True))
        snapshot = [
            {
                "id": field.id,
                "label": field.label,
                "key": field.key,
                "field_type": field.field_type,
                "required": field.required,
                "options": field.options,
                "validation": field.validation,
                "ordering": field.ordering,
            }
            for field in fields
        ]
        request = self.context.get("request")
        metadata = {}
        if request:
            metadata = {
                "ip": request.META.get("HTTP_X_FORWARDED_FOR", request.META.get("REMOTE_ADDR", "")),
                "user_agent": request.META.get("HTTP_USER_AGENT", ""),
            }
        return CampaignFormResponse.objects.create(
            form=form,
            response_data=validated_data["response_data"],
            metadata=metadata,
            field_snapshot=snapshot,
        )
