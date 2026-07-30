from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from apps.accounts.models import CustomerNotificationSubscription
from apps.accounts.services import account_roles_for_user, account_type_for_user, customer_contact_for_user, phone_for_user
from apps.common.form_validation import validate_digit_phone
from apps.contacts.services import normalize_email


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(trim_whitespace=False)

    def validate(self, attrs):
        User = get_user_model()
        try:
            user = User.objects.get(email__iexact=attrs["email"])
        except User.DoesNotExist as exc:
            raise serializers.ValidationError("Invalid email or password.") from exc

        user = authenticate(username=user.get_username(), password=attrs["password"])
        if not user or not user.is_active:
            raise serializers.ValidationError("Invalid email or password.")
        if not user.is_staff and not user.is_superuser:
            raise serializers.ValidationError("This account does not have staff access.")
        attrs["user"] = user
        return attrs


class UserSerializer(serializers.ModelSerializer):
    roles = serializers.SerializerMethodField()
    account_type = serializers.SerializerMethodField()
    contact = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = ["id", "email", "first_name", "last_name", "is_staff", "is_superuser", "roles", "account_type", "contact", "phone"]

    def get_roles(self, obj):
        return account_roles_for_user(obj)

    def get_account_type(self, obj):
        return account_type_for_user(obj)

    def get_contact(self, obj):
        contact = customer_contact_for_user(obj)
        return contact.pk if contact else None

    def get_phone(self, obj):
        return phone_for_user(obj)


class CustomerRegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)
    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True, trim_whitespace=True)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True, trim_whitespace=True)
    full_name = serializers.CharField(max_length=180, required=False, allow_blank=True, trim_whitespace=True)
    phone = serializers.CharField(max_length=32, required=False, allow_blank=True, trim_whitespace=True)
    marketing_consent = serializers.BooleanField(required=False, default=False)

    def validate_email(self, value):
        normalized = normalize_email(value)
        if get_user_model().objects.filter(email__iexact=normalized).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return normalized

    def validate_password(self, value):
        try:
            validate_password(value)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(list(exc.messages)) from exc
        return value

    def validate_phone(self, value):
        if not value:
            return ""
        cleaned, error = validate_digit_phone(value)
        if error:
            raise serializers.ValidationError(error)
        return cleaned


class CustomerLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(trim_whitespace=False)

    def validate_email(self, value):
        return normalize_email(value)


class CustomerPasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        return normalize_email(value)


class CustomerPasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField(trim_whitespace=True)
    token = serializers.CharField(trim_whitespace=False)
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate_password(self, value):
        try:
            validate_password(value)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(list(exc.messages)) from exc
        return value


class CustomerProfileUpdateSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True, trim_whitespace=True)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True, trim_whitespace=True)
    full_name = serializers.CharField(max_length=180, required=False, allow_blank=True, trim_whitespace=True)
    phone = serializers.CharField(max_length=32, required=False, allow_blank=True, trim_whitespace=True)
    address = serializers.CharField(required=False, allow_blank=True, trim_whitespace=True)
    age = serializers.IntegerField(required=False, allow_null=True, min_value=0, max_value=130)
    skin_type = serializers.CharField(max_length=120, required=False, allow_blank=True, trim_whitespace=True)
    preferred_ritual = serializers.CharField(max_length=180, required=False, allow_blank=True, trim_whitespace=True)
    preferred_day = serializers.CharField(max_length=160, required=False, allow_blank=True, trim_whitespace=True)
    skin_goal = serializers.CharField(required=False, allow_blank=True, trim_whitespace=True)
    marketing_consent = serializers.BooleanField(required=False)

    def validate_phone(self, value):
        if not value:
            return ""
        cleaned, error = validate_digit_phone(value)
        if error:
            raise serializers.ValidationError(error)
        return cleaned


class CustomerNotificationSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerNotificationSubscription
        fields = [
            "id",
            "channel",
            "platform",
            "device_id",
            "device_name",
            "app_version",
            "token",
            "subscription_endpoint",
            "subscription",
            "permission_status",
            "enabled",
            "locale",
            "timezone",
            "metadata",
            "last_registered_at",
            "disabled_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "last_registered_at", "disabled_at", "created_at", "updated_at"]
        validators = []
        extra_kwargs = {
            "token": {"required": False, "allow_blank": True},
            "subscription_endpoint": {"required": False, "allow_blank": True},
            "subscription": {"required": False},
            "device_id": {"required": False, "allow_blank": True},
            "device_name": {"required": False, "allow_blank": True},
            "app_version": {"required": False, "allow_blank": True},
            "platform": {"required": False, "allow_blank": True},
            "permission_status": {"required": False, "allow_blank": True},
            "locale": {"required": False, "allow_blank": True},
            "timezone": {"required": False, "allow_blank": True},
            "metadata": {"required": False},
        }

    def validate(self, attrs):
        channel = attrs.get("channel", getattr(self.instance, "channel", ""))
        token = str(attrs.get("token", getattr(self.instance, "token", "")) or "").strip()
        subscription = attrs.get("subscription", getattr(self.instance, "subscription", {}) or {})
        if subscription is None:
            subscription = {}
        if not isinstance(subscription, dict):
            raise serializers.ValidationError({"subscription": "Subscription must be a JSON object."})
        subscription_endpoint = str(attrs.get("subscription_endpoint", getattr(self.instance, "subscription_endpoint", "")) or subscription.get("endpoint") or "").strip()
        if channel == CustomerNotificationSubscription.Channel.EXPO and not token:
            raise serializers.ValidationError({"token": "Expo push subscriptions require a token."})
        if channel == CustomerNotificationSubscription.Channel.WEB_PUSH and not subscription_endpoint:
            raise serializers.ValidationError({"subscription": "Web push subscriptions require an endpoint."})
        attrs["token"] = token
        attrs["subscription"] = subscription
        attrs["subscription_endpoint"] = subscription_endpoint
        return attrs
