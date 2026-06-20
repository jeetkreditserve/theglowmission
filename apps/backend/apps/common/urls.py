from django.urls import path

from apps.common.views import DeepHealthView, HealthView

urlpatterns = [
    path("health/", HealthView.as_view(), name="health"),
    path("health/deep/", DeepHealthView.as_view(), name="deep-health"),
]

