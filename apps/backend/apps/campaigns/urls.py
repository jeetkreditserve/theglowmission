from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.campaigns.views import (
    CampaignFormFieldViewSet,
    CampaignFormResponseViewSet,
    CampaignFormViewSet,
    PublicCampaignFormView,
    PublicCampaignResponseView,
)

router = DefaultRouter()
router.register("admin/campaign-forms", CampaignFormViewSet, basename="admin-campaign-forms")
router.register("admin/campaign-fields", CampaignFormFieldViewSet, basename="admin-campaign-fields")
router.register("admin/campaign-responses", CampaignFormResponseViewSet, basename="admin-campaign-responses")

urlpatterns = [
    path("public/campaign-forms/<slug:slug>/", PublicCampaignFormView.as_view(), name="public-campaign-form"),
    path("public/campaign-forms/<slug:slug>/responses/", PublicCampaignResponseView.as_view(), name="public-campaign-response"),
    path("", include(router.urls)),
]

