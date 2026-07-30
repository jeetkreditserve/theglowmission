from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.notifications.views import CustomerNotificationInboxView, NotificationCampaignViewSet


router = DefaultRouter()
router.register("admin/notification-campaigns", NotificationCampaignViewSet, basename="admin-notification-campaigns")

urlpatterns = [
    path("auth/customer/notifications/", CustomerNotificationInboxView.as_view(), name="customer-notifications"),
    path("", include(router.urls)),
]
