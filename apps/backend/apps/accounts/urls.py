from django.urls import path

from apps.accounts.views import (
    CustomerLoginView,
    CustomerNotificationSubscriptionDetailView,
    CustomerNotificationSubscriptionListCreateView,
    CustomerPasswordResetConfirmView,
    CustomerPasswordResetRequestView,
    CustomerProfileView,
    CustomerRegisterView,
    LoginView,
    LogoutView,
    MeView,
)

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("me/", MeView.as_view(), name="me"),
    path("customer/register/", CustomerRegisterView.as_view(), name="customer-register"),
    path("customer/login/", CustomerLoginView.as_view(), name="customer-login"),
    path("customer/password-reset/request/", CustomerPasswordResetRequestView.as_view(), name="customer-password-reset-request"),
    path("customer/password-reset/confirm/", CustomerPasswordResetConfirmView.as_view(), name="customer-password-reset-confirm"),
    path("customer/profile/", CustomerProfileView.as_view(), name="customer-profile"),
    path("customer/devices/", CustomerNotificationSubscriptionListCreateView.as_view(), name="customer-devices"),
    path("customer/devices/<int:pk>/", CustomerNotificationSubscriptionDetailView.as_view(), name="customer-device-detail"),
]
