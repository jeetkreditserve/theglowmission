from django.contrib import admin

from apps.accounts.models import AccountRole, CustomerNotificationSubscription, CustomerProfile, UserRole


@admin.register(AccountRole)
class AccountRoleAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "updated_at"]
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name", "slug"]


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ["user", "role", "updated_at"]
    list_filter = ["role"]
    search_fields = ["user__email", "user__username", "role__name", "role__slug"]


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "phone", "contact", "verified_phone_at", "verified_email_at", "updated_at"]
    search_fields = ["user__email", "user__username", "phone", "normalized_phone", "contact__full_name", "contact__email", "contact__phone"]
    readonly_fields = ["normalized_phone", "created_at", "updated_at"]


@admin.register(CustomerNotificationSubscription)
class CustomerNotificationSubscriptionAdmin(admin.ModelAdmin):
    list_display = ["channel", "platform", "user", "contact", "enabled", "permission_status", "last_registered_at"]
    list_filter = ["channel", "platform", "enabled", "permission_status"]
    search_fields = [
        "user__email",
        "user__username",
        "contact__full_name",
        "contact__email",
        "contact__phone",
        "device_id",
        "device_name",
        "token",
        "subscription_endpoint",
    ]
    readonly_fields = ["created_at", "updated_at", "last_registered_at", "disabled_at"]
