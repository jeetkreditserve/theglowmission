from __future__ import annotations

from io import BytesIO

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.generics import RetrieveAPIView
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.image_variants import ensure_image_variants
from apps.campaigns.exports import build_campaign_responses_workbook
from apps.campaigns.models import CampaignForm, CampaignFormField, CampaignFormResponse
from apps.campaigns.serializers import (
    CampaignFormFieldSerializer,
    CampaignFormResponseSerializer,
    CampaignFormSerializer,
    PublicCampaignFormSerializer,
    PublicCampaignResponseSerializer,
)


class PublicCampaignFormView(RetrieveAPIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = PublicCampaignFormSerializer
    lookup_field = "slug"
    lookup_url_kwarg = "slug"

    def get_queryset(self):
        return CampaignForm.objects.prefetch_related("fields")

    def get_object(self):
        form = super().get_object()
        if not form.is_active_now:
            raise NotFound("Campaign form is not active.")
        return form


class PublicCampaignResponseView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, slug: str):
        form = get_object_or_404(CampaignForm.objects.prefetch_related("fields"), slug=slug)
        if not form.is_active_now:
            raise ValidationError("Campaign form is not accepting responses.")
        serializer = PublicCampaignResponseSerializer(data=request.data, context={"form": form, "request": request})
        serializer.is_valid(raise_exception=True)
        response = serializer.save()
        return Response(
            {
                "id": response.id,
                "message": form.success_message,
                "redirect_url": form.redirect_url,
            },
            status=status.HTTP_201_CREATED,
        )


class CampaignFormViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    queryset = CampaignForm.objects.prefetch_related("fields", "responses").all()
    serializer_class = CampaignFormSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "slug"]
    ordering_fields = ["updated_at", "title", "status"]

    def perform_create(self, serializer):
        form = serializer.save()
        ensure_image_variants(form.hero_image)

    def perform_update(self, serializer):
        form = serializer.save()
        ensure_image_variants(form.hero_image)

    @action(detail=True, methods=["get"])
    def responses(self, request, pk=None):
        form = self.get_object()
        serializer = CampaignFormResponseSerializer(form.responses.all(), many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"], url_path="responses/export")
    def export_responses(self, request, pk=None):
        form = self.get_object()
        workbook = build_campaign_responses_workbook(form)
        output = BytesIO()
        workbook.save(output)
        output.seek(0)
        response = HttpResponse(
            output.read(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = f'attachment; filename="{form.slug}-responses.xlsx"'
        return response


class CampaignFormFieldViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    queryset = CampaignFormField.objects.select_related("form").all()
    serializer_class = CampaignFormFieldSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["label", "key", "form__title"]
    ordering_fields = ["ordering", "updated_at"]

    def get_queryset(self):
        queryset = super().get_queryset()
        form_id = self.request.query_params.get("form")
        if form_id:
            queryset = queryset.filter(form_id=form_id)
        return queryset

    @action(detail=False, methods=["post"], url_path="reorder")
    def reorder(self, request):
        items = request.data.get("items", [])
        if not isinstance(items, list):
            return Response({"detail": "items must be a list."}, status=400)
        queryset = self.get_queryset()
        for item in items:
            item_id = item.get("id")
            ordering = item.get("ordering")
            if item_id is None or ordering is None:
                continue
            queryset.filter(pk=item_id).update(ordering=ordering)
        return Response({"status": "ok"})


class CampaignFormResponseViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAdminUser]
    queryset = CampaignFormResponse.objects.select_related("form").all()
    serializer_class = CampaignFormResponseSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["form__title"]
    ordering_fields = ["submitted_at", "created_at"]
