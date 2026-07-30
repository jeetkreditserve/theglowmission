from __future__ import annotations

from rest_framework import serializers

from apps.appointments.models import (
    Appointment,
    AppointmentAvailabilityWindow,
    AppointmentBlock,
    AppointmentFinanceEntry,
    AppointmentNotificationLog,
    AppointmentPhoto,
)
from apps.appointments.services import appointment_end_for_service, validate_no_confirmed_overlap
from apps.common.storage import file_key, file_url
from apps.common.form_validation import validate_digit_phone
from apps.contacts.services import normalize_email
from apps.content.models import Service


class AvailableSlotsQuerySerializer(serializers.Serializer):
    date = serializers.DateField(required=True)


class AppointmentSlotSerializer(serializers.Serializer):
    starts_at = serializers.DateTimeField()
    ends_at = serializers.DateTimeField()


class PublicAppointmentCreateSerializer(serializers.Serializer):
    starts_at = serializers.DateTimeField()
    full_name = serializers.CharField(max_length=180, trim_whitespace=True)
    phone = serializers.CharField(max_length=32, trim_whitespace=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    skin_goal = serializers.CharField(required=False, allow_blank=True, trim_whitespace=True)
    notes = serializers.CharField(required=False, allow_blank=True, trim_whitespace=True)
    customer_notes = serializers.CharField(required=False, allow_blank=True, trim_whitespace=True)

    def validate_phone(self, value):
        cleaned, error = validate_digit_phone(value)
        if error:
            raise serializers.ValidationError(error)
        return cleaned

    def validate_email(self, value):
        return normalize_email(value)


class CustomerAppointmentCreateSerializer(PublicAppointmentCreateSerializer):
    service_slug = serializers.SlugField(max_length=120)
    full_name = serializers.CharField(max_length=180, required=False, allow_blank=True, trim_whitespace=True)
    phone = serializers.CharField(max_length=32, required=False, allow_blank=True, trim_whitespace=True)

    def validate_phone(self, value):
        if not value:
            return ""
        return super().validate_phone(value)


class CustomerAppointmentCancelSerializer(serializers.Serializer):
    reason = serializers.CharField(required=False, allow_blank=True, trim_whitespace=True)


class CustomerAppointmentRescheduleSerializer(serializers.Serializer):
    starts_at = serializers.DateTimeField()


class AppointmentNotificationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppointmentNotificationLog
        fields = ["id", "channel", "event_type", "reminder_minutes", "recipient", "status", "error", "sent_at", "created_at"]
        read_only_fields = fields


class AppointmentPhotoSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    image_key = serializers.SerializerMethodField()
    created_by_email = serializers.EmailField(source="created_by.email", read_only=True)

    class Meta:
        model = AppointmentPhoto
        fields = [
            "id",
            "appointment",
            "photo_type",
            "image",
            "image_url",
            "image_key",
            "notes",
            "created_by",
            "created_by_email",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_by", "created_by_email", "created_at", "updated_at"]
        extra_kwargs = {
            "image": {"write_only": True},
            "appointment": {"required": False},
            "notes": {"required": False, "allow_blank": True},
        }

    def get_image_url(self, obj):
        return file_url(obj.image)

    def get_image_key(self, obj):
        return file_key(obj.image)


class AppointmentSerializer(serializers.ModelSerializer):
    service_title = serializers.CharField(source="service.title", read_only=True)
    service_slug = serializers.CharField(source="service.slug", read_only=True)
    contact_display_name = serializers.CharField(source="contact.display_name", read_only=True)
    customer_email = serializers.EmailField(source="customer.email", read_only=True)
    created_by_email = serializers.EmailField(source="created_by.email", read_only=True)
    cancelled_by_email = serializers.EmailField(source="cancelled_by.email", read_only=True)
    notification_logs = AppointmentNotificationLogSerializer(many=True, read_only=True)
    photos = AppointmentPhotoSerializer(many=True, read_only=True)
    ends_at = serializers.DateTimeField(required=False)
    duration_minutes = serializers.IntegerField(required=False, min_value=1, max_value=1440)

    class Meta:
        model = Appointment
        fields = [
            "id",
            "service",
            "service_title",
            "service_slug",
            "contact",
            "contact_display_name",
            "customer",
            "customer_email",
            "full_name",
            "phone",
            "email",
            "notes",
            "skin_goal",
            "starts_at",
            "ends_at",
            "duration_minutes",
            "status",
            "source",
            "campaign_response",
            "created_by",
            "created_by_email",
            "cancelled_by",
            "cancelled_by_email",
            "cancellation_reason",
            "customer_notes",
            "internal_notes",
            "notification_logs",
            "photos",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_by", "cancelled_by", "created_at", "updated_at", "notification_logs", "photos"]
        extra_kwargs = {
            "full_name": {"required": False, "allow_blank": True},
            "phone": {"required": False, "allow_blank": True},
            "email": {"required": False, "allow_blank": True},
            "notes": {"required": False, "allow_blank": True},
            "skin_goal": {"required": False, "allow_blank": True},
            "customer_notes": {"required": False, "allow_blank": True},
            "internal_notes": {"required": False, "allow_blank": True},
            "campaign_response": {"required": False, "allow_null": True},
            "contact": {"required": False, "allow_null": True},
            "customer": {"required": False, "allow_null": True},
        }

    def validate_phone(self, value):
        if not value:
            return ""
        cleaned, error = validate_digit_phone(value)
        if error:
            raise serializers.ValidationError(error)
        return cleaned

    def validate_email(self, value):
        return normalize_email(value)

    def validate(self, attrs):
        values = self.current_values(attrs)
        contact = values.get("contact")
        if contact:
            attrs.setdefault("full_name", contact.full_name or contact.display_name)
            attrs.setdefault("phone", contact.phone)
            attrs.setdefault("email", contact.email)
            values = self.current_values(attrs)

        if not values.get("full_name"):
            raise serializers.ValidationError({"full_name": "Full name is required."})
        if not values.get("phone"):
            raise serializers.ValidationError({"phone": "Phone is required."})

        service = values.get("service")
        starts_at = values.get("starts_at")
        if service and starts_at:
            duration_minutes = int(values.get("duration_minutes") or service.duration_minutes or 60)
            attrs.setdefault("duration_minutes", duration_minutes)
            if "ends_at" not in attrs and (not self.instance or "starts_at" in attrs or "duration_minutes" in attrs):
                attrs["ends_at"] = appointment_end_for_service(service, starts_at)
                values["ends_at"] = attrs["ends_at"]
            ends_at = attrs.get("ends_at", values.get("ends_at"))
            if ends_at and values.get("status", Appointment.Status.CONFIRMED) == Appointment.Status.CONFIRMED:
                validate_no_confirmed_overlap(starts_at, ends_at, exclude_appointment_id=self.instance.pk if self.instance else None)
        return attrs

    def current_values(self, attrs):
        values = {}
        for field in ["service", "contact", "full_name", "phone", "email", "starts_at", "ends_at", "duration_minutes", "status"]:
            if field in attrs:
                values[field] = attrs[field]
            elif self.instance:
                values[field] = getattr(self.instance, field)
            elif field == "status":
                values[field] = Appointment.Status.CONFIRMED
            else:
                values[field] = None
        return values

    def create(self, validated_data):
        validated_data.setdefault("source", Appointment.Source.ADMIN)
        if not validated_data.get("duration_minutes") and validated_data.get("service"):
            validated_data["duration_minutes"] = validated_data["service"].duration_minutes or 60
        if not validated_data.get("ends_at") and validated_data.get("starts_at") and validated_data.get("service"):
            validated_data["ends_at"] = appointment_end_for_service(validated_data["service"], validated_data["starts_at"])
        return super().create(validated_data)


class AppointmentAvailabilityWindowSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppointmentAvailabilityWindow
        fields = ["id", "weekday", "starts_at", "ends_at", "active", "label", "ordering", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at"]

    def validate(self, attrs):
        starts_at = attrs.get("starts_at", getattr(self.instance, "starts_at", None))
        ends_at = attrs.get("ends_at", getattr(self.instance, "ends_at", None))
        if starts_at and ends_at and ends_at <= starts_at:
            raise serializers.ValidationError({"ends_at": "End time must be after the start time."})
        return attrs


class AppointmentAvailabilityImpactRequestSerializer(serializers.Serializer):
    delete = serializers.BooleanField(required=False, default=False)
    action = serializers.CharField(required=False, allow_blank=True, trim_whitespace=True)
    operation = serializers.CharField(required=False, allow_blank=True, trim_whitespace=True)
    mode = serializers.CharField(required=False, allow_blank=True, trim_whitespace=True)
    weekday = serializers.IntegerField(required=False, min_value=0, max_value=6)
    starts_at = serializers.TimeField(required=False)
    ends_at = serializers.TimeField(required=False)
    active = serializers.BooleanField(required=False)
    label = serializers.CharField(required=False, allow_blank=True, max_length=120, trim_whitespace=True)
    ordering = serializers.IntegerField(required=False, min_value=0)

    def validate(self, attrs):
        operation_values = [attrs.get("action", ""), attrs.get("operation", ""), attrs.get("mode", "")]
        if any(value.lower() in {"delete", "destroy", "remove"} for value in operation_values):
            attrs["delete"] = True
        if attrs.get("delete"):
            return attrs

        window = self.context["window"]
        starts_at = attrs.get("starts_at", window.starts_at)
        ends_at = attrs.get("ends_at", window.ends_at)
        if ends_at <= starts_at:
            raise serializers.ValidationError({"ends_at": "End time must be after the start time."})
        return attrs


class AppointmentAvailabilityImpactAppointmentSerializer(serializers.ModelSerializer):
    service_title = serializers.CharField(source="service.title", read_only=True)

    class Meta:
        model = Appointment
        fields = ["id", "full_name", "service_title", "starts_at", "ends_at", "status"]
        read_only_fields = fields


class AppointmentBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppointmentBlock
        fields = ["id", "starts_at", "ends_at", "reason", "active", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at"]

    def validate(self, attrs):
        starts_at = attrs.get("starts_at", getattr(self.instance, "starts_at", None))
        ends_at = attrs.get("ends_at", getattr(self.instance, "ends_at", None))
        if starts_at and ends_at and ends_at <= starts_at:
            raise serializers.ValidationError({"ends_at": "End time must be after the start time."})
        return attrs


class AppointmentFinanceEntrySerializer(serializers.ModelSerializer):
    appointment_label = serializers.SerializerMethodField()
    created_by_email = serializers.EmailField(source="created_by.email", read_only=True)

    class Meta:
        model = AppointmentFinanceEntry
        fields = [
            "id",
            "entry_date",
            "entry_type",
            "label",
            "amount",
            "appointment",
            "appointment_label",
            "notes",
            "created_by",
            "created_by_email",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_by", "created_by_email", "created_at", "updated_at"]
        extra_kwargs = {
            "appointment": {"required": False, "allow_null": True},
            "notes": {"required": False, "allow_blank": True},
        }

    def get_appointment_label(self, obj):
        return str(obj.appointment) if obj.appointment_id and obj.appointment else ""


def service_for_slug(slug: str) -> Service:
    try:
        return Service.objects.get(slug=slug, active=True)
    except Service.DoesNotExist as exc:
        raise serializers.ValidationError({"service_slug": "Service was not found."}) from exc
