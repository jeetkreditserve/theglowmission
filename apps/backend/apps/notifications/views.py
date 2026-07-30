from __future__ import annotations

from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.services import ensure_customer_profile_for_user
from apps.notifications.models import NotificationCampaign, NotificationMessageLog
from apps.notifications.serializers import (
    NotificationCampaignSerializer,
    NotificationMessageLogSerializer,
)
from apps.notifications.services import preview_recipients, send_notification_campaign


class NotificationCampaignViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]
    serializer_class = NotificationCampaignSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "subject", "body"]
    ordering_fields = ["updated_at", "created_at", "scheduled_at", "sent_at", "status"]

    def get_queryset(self):
        queryset = NotificationCampaign.objects.select_related("target_status", "created_by").prefetch_related("recipients", "message_logs")
        status_filter = self.request.query_params.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        return queryset

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=["get"], url_path="recipients/preview")
    def recipients_preview(self, request, pk=None):
        campaign = self.get_object()
        limit = int(request.query_params.get("limit", "250"))
        previews = preview_recipients(campaign, limit=max(min(limit, 1000), 1))
        return Response(
            {
                "count": len(previews),
                "results": [
                    {
                        "contact": item.contact_id,
                        "user": item.user_id,
                        "display_name": item.display_name,
                        "email": item.email,
                        "phone": item.phone,
                    }
                    for item in previews
                ],
            }
        )

    @action(detail=True, methods=["post"])
    def send(self, request, pk=None):
        campaign = self.get_object()
        return Response(send_notification_campaign(campaign))

    @action(detail=True, methods=["get"], url_path="message-logs")
    def message_logs(self, request, pk=None):
        campaign = self.get_object()
        logs = campaign.message_logs.select_related("campaign", "recipient", "contact", "user")
        return Response(NotificationMessageLogSerializer(logs, many=True).data)


class CustomerNotificationInboxView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = ensure_customer_profile_for_user(request.user)
        queryset = NotificationMessageLog.objects.select_related("campaign", "recipient", "contact", "user").filter(user=request.user)
        if profile.contact_id:
            queryset = queryset | NotificationMessageLog.objects.select_related("campaign", "recipient", "contact", "user").filter(contact_id=profile.contact_id)
        queryset = queryset.distinct().order_by("-created_at", "-id")
        return Response(NotificationMessageLogSerializer(queryset, many=True).data)
