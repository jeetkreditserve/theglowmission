from __future__ import annotations

import re

from django.core.validators import validate_email
from django.utils.dateparse import parse_date
from django.utils.text import slugify
from rest_framework import serializers

from apps.common.image_variants import image_variant_set
from apps.common.form_validation import validate_digit_phone
from apps.common.storage import file_key, file_url
from apps.campaigns.models import CampaignForm, CampaignFormField, CampaignFormResponse


class S3FileMixin:
    def get_url_for(self, obj, field_name: str):
        return file_url(getattr(obj, field_name))

    def get_key_for(self, obj, field_name: str):
        return file_key(getattr(obj, field_name))

    def get_variants_for(self, obj, field_name: str):
        return image_variant_set(getattr(obj, field_name))


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
        extra_kwargs = {"key": {"required": False, "allow_blank": True}}

    def validate(self, attrs):
        label = attrs.get("label", getattr(self.instance, "label", ""))
        key = attrs.get("key", getattr(self.instance, "key", ""))
        form = attrs.get("form", getattr(self.instance, "form", None))
        if not key and label:
            key = slugify(label).replace("-", "_")
            attrs["key"] = key
        if form and key:
            queryset = CampaignFormField.objects.filter(form=form, key=key)
            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise serializers.ValidationError({"key": "A field with this key already exists on this campaign."})
        field_type = attrs.get("field_type", getattr(self.instance, "field_type", CampaignFormField.FieldType.TEXT))
        active = attrs.get("active", getattr(self.instance, "active", True))
        options = attrs.get("options", getattr(self.instance, "options", [])) or []
        validation = attrs.get("validation", getattr(self.instance, "validation", {})) or {}
        if not isinstance(validation, dict):
            raise serializers.ValidationError({"validation": "Validation rules must be a JSON object."})
        if not isinstance(options, list):
            raise serializers.ValidationError({"options": "Options must be a list."})
        if active and field_type in {CampaignFormField.FieldType.SELECT, CampaignFormField.FieldType.RADIO} and not options:
            raise serializers.ValidationError({"options": "Add at least one option for select and radio fields."})

        key = attrs.get("key")
        if self.instance and key and key != self.instance.key and self.instance.form.responses.exists():
            raise serializers.ValidationError({"key": "Field key cannot be changed after responses exist."})
        return attrs


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
    hero_image_variants = serializers.SerializerMethodField()

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
            "hero_image_variants",
            "hero_image_alt",
            "button_label",
            "submitting_label",
            "empty_select_label",
            "checkbox_label",
            "error_message",
            "schedule_enabled",
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
        read_only_fields = ["hero_image_url", "hero_image_key", "hero_image_variants", "response_count", "is_active_now", "updated_at"]
        extra_kwargs = {
            "hero_image": {"write_only": True, "required": False},
            "slug": {"required": False, "allow_blank": True},
        }

    def validate(self, attrs):
        title = attrs.get("title", getattr(self.instance, "title", ""))
        slug = attrs.get("slug", getattr(self.instance, "slug", ""))
        if not slug and title:
            slug = slugify(title)
            attrs["slug"] = slug
        if slug:
            queryset = CampaignForm.objects.filter(slug=slug)
            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise serializers.ValidationError({"slug": "A campaign with this slug already exists."})
        schedule_enabled = attrs.get("schedule_enabled", getattr(self.instance, "schedule_enabled", False))
        starts_at = attrs.get("starts_at", getattr(self.instance, "starts_at", None))
        ends_at = attrs.get("ends_at", getattr(self.instance, "ends_at", None))
        if schedule_enabled and not starts_at and not ends_at:
            raise serializers.ValidationError({"starts_at": "Add a start or end date, or turn scheduling off."})
        if starts_at and ends_at and ends_at <= starts_at:
            raise serializers.ValidationError({"ends_at": "End date must be after the start date."})
        return attrs

    def get_hero_image_url(self, obj):
        return self.get_url_for(obj, "hero_image")

    def get_hero_image_key(self, obj):
        return self.get_key_for(obj, "hero_image")

    def get_hero_image_variants(self, obj):
        return self.get_variants_for(obj, "hero_image")


class PublicCampaignFormSerializer(S3FileMixin, serializers.ModelSerializer):
    fields = PublicCampaignFormFieldSerializer(many=True, read_only=True)
    hero_image_url = serializers.SerializerMethodField()
    hero_image_variants = serializers.SerializerMethodField()

    class Meta:
        model = CampaignForm
        fields = [
            "id",
            "title",
            "slug",
            "summary",
            "offer_label",
            "hero_image_url",
            "hero_image_variants",
            "hero_image_alt",
            "button_label",
            "submitting_label",
            "empty_select_label",
            "checkbox_label",
            "error_message",
            "success_message",
            "redirect_url",
            "seo_title",
            "seo_description",
            "fields",
        ]

    def get_hero_image_url(self, obj):
        return self.get_url_for(obj, "hero_image")

    def get_hero_image_variants(self, obj):
        return self.get_variants_for(obj, "hero_image")


class CampaignFormResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampaignFormResponse
        fields = ["id", "form", "submitted_at", "response_data", "metadata", "field_snapshot", "created_at"]
        read_only_fields = ["submitted_at", "created_at"]


class PublicCampaignResponseSerializer(serializers.Serializer):
    response_data = serializers.JSONField()

    def validate_response_data(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError("Response data must be an object.")
        form = self.context["form"]
        active_fields = list(form.fields.filter(active=True))
        cleaned = {}
        errors = {}

        for field in active_fields:
            raw = value.get(field.key)
            if self._is_required_missing(field, raw):
                errors[field.key] = "This field is required."
                continue
            if raw in (None, ""):
                cleaned[field.key] = raw
                continue

            cleaned_value = raw

            if field.field_type == CampaignFormField.FieldType.EMAIL:
                try:
                    validate_email(str(raw))
                except Exception:
                    errors[field.key] = "Enter a valid email address."
            elif field.field_type == CampaignFormField.FieldType.PHONE:
                min_length = self._coerce_int((field.validation or {}).get("min_length"))
                max_length = self._coerce_int((field.validation or {}).get("max_length"))
                cleaned_value, phone_error = validate_digit_phone(raw, min_length=min_length, max_length=max_length)
                if phone_error:
                    errors[field.key] = phone_error
            elif field.field_type == CampaignFormField.FieldType.NUMBER:
                try:
                    cleaned_value = float(raw)
                except (TypeError, ValueError):
                    errors[field.key] = "Enter a valid number."
            elif field.field_type == CampaignFormField.FieldType.DATE:
                if parse_date(str(raw)) is None:
                    errors[field.key] = "Enter a valid date."
            elif field.field_type in {CampaignFormField.FieldType.SELECT, CampaignFormField.FieldType.RADIO}:
                options = field.options or []
                if options and raw not in options:
                    errors[field.key] = "Select a valid option."
            elif field.field_type == CampaignFormField.FieldType.CHECKBOX:
                if not isinstance(raw, (bool, list)):
                    errors[field.key] = "Enter a valid checkbox value."

            if field.key not in errors:
                validation_error = self._validate_custom_rules(field, cleaned_value)
                if validation_error:
                    errors[field.key] = validation_error

            cleaned[field.key] = cleaned_value

        if errors:
            raise serializers.ValidationError(errors)
        return cleaned

    @staticmethod
    def _is_required_missing(field: CampaignFormField, value) -> bool:
        if not field.required:
            return False
        if field.field_type == CampaignFormField.FieldType.CHECKBOX:
            return value is not True
        return value is None or value == "" or value == []

    def _validate_custom_rules(self, field: CampaignFormField, value):
        validation = field.validation or {}

        min_length = self._coerce_int(validation.get("min_length"))
        if min_length is not None and len(str(value)) < min_length:
            return f"Ensure this value has at least {min_length} characters."

        max_length = self._coerce_int(validation.get("max_length"))
        if max_length is not None and len(str(value)) > max_length:
            return f"Ensure this value has no more than {max_length} characters."

        pattern = validation.get("pattern")
        if isinstance(pattern, str) and pattern and not re.fullmatch(pattern, str(value)):
            return "Enter a valid value."

        min_value = self._coerce_float(validation.get("min"))
        max_value = self._coerce_float(validation.get("max"))
        if min_value is not None or max_value is not None:
            try:
                numeric_value = float(value)
            except (TypeError, ValueError):
                return "Enter a valid number."
            if min_value is not None and numeric_value < min_value:
                return f"Ensure this value is at least {self._format_number(min_value)}."
            if max_value is not None and numeric_value > max_value:
                return f"Ensure this value is no more than {self._format_number(max_value)}."

        return ""

    @staticmethod
    def _coerce_int(value):
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _coerce_float(value):
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _format_number(value: float) -> str:
        return str(int(value)) if value.is_integer() else str(value)

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
