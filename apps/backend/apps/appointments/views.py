from __future__ import annotations

from datetime import datetime, time, timedelta

from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.dateparse import parse_date
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.appointments.models import Appointment, AppointmentAvailabilityWindow, AppointmentBlock, AppointmentFinanceEntry
from apps.appointments.serializers import (
    AppointmentAvailabilityImpactAppointmentSerializer,
    AppointmentAvailabilityImpactRequestSerializer,
    AppointmentAvailabilityWindowSerializer,
    AppointmentBlockSerializer,
    AppointmentFinanceEntrySerializer,
    AppointmentPhotoSerializer,
    AppointmentSerializer,
    AppointmentSlotSerializer,
    AvailableSlotsQuerySerializer,
    CustomerAppointmentCancelSerializer,
    CustomerAppointmentCreateSerializer,
    CustomerAppointmentRescheduleSerializer,
    PublicAppointmentCreateSerializer,
    service_for_slug,
)
from apps.appointments.services import (
    availability_impact_for_window_change,
    available_slots_for_service,
    cancel_customer_appointment,
    create_customer_appointment,
    create_public_appointment,
    founder_dashboard_metrics,
    notify_appointment_cancellation,
    notify_appointment_confirmation,
    notify_appointment_reschedule,
    reschedule_customer_appointment,
)
from apps.content.models import Service


class PublicServiceAvailableSlotsView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, slug: str):
        service = get_object_or_404(Service.objects.filter(active=True), slug=slug)
        serializer = AvailableSlotsQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        slots = available_slots_for_service(service, serializer.validated_data["date"])
        return Response(AppointmentSlotSerializer(slots, many=True).data)


class PublicServiceAppointmentView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, slug: str):
        service = get_object_or_404(Service.objects.select_related("booking_campaign").filter(active=True), slug=slug)
        serializer = PublicAppointmentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        appointment = create_public_appointment(service=service, values=serializer.validated_data, request=request)
        return Response(AppointmentSerializer(appointment, context={"request": request}).data, status=status.HTTP_201_CREATED)


class CustomerAppointmentListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        appointments = customer_appointments_for_request(request)
        return Response(AppointmentSerializer(appointments, many=True, context={"request": request}).data)

    def post(self, request):
        serializer = CustomerAppointmentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        service = service_for_slug(serializer.validated_data["service_slug"])
        appointment = create_customer_appointment(service=service, user=request.user, values=serializer.validated_data, request=request)
        return Response(AppointmentSerializer(appointment, context={"request": request}).data, status=status.HTTP_201_CREATED)


class CustomerAppointmentCancelView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk: int):
        appointment = get_object_or_404(customer_appointments_for_request(request), pk=pk)
        serializer = CustomerAppointmentCancelSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        appointment = cancel_customer_appointment(
            appointment=appointment,
            user=request.user,
            reason=serializer.validated_data.get("reason", ""),
        )
        return Response(AppointmentSerializer(appointment, context={"request": request}).data)


class CustomerAppointmentRescheduleView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk: int):
        appointment = get_object_or_404(customer_appointments_for_request(request), pk=pk)
        serializer = CustomerAppointmentRescheduleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        appointment = reschedule_customer_appointment(
            appointment=appointment,
            user=request.user,
            starts_at=serializer.validated_data["starts_at"],
        )
        return Response(AppointmentSerializer(appointment, context={"request": request}).data)


def customer_appointments_for_request(request):
    from apps.appointments.services import customer_appointment_queryset

    return customer_appointment_queryset(request.user)


class AppointmentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]
    serializer_class = AppointmentSerializer
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["full_name", "phone", "email", "service__title", "contact__full_name", "contact__phone"]
    ordering_fields = ["starts_at", "created_at", "updated_at", "status"]

    def get_queryset(self):
        queryset = Appointment.objects.select_related(
            "service",
            "contact",
            "customer",
            "campaign_response",
            "created_by",
            "cancelled_by",
        ).prefetch_related("notification_logs", "photos")
        status_filter = self.request.query_params.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        service_id = self.request.query_params.get("service")
        if service_id:
            queryset = queryset.filter(service_id=service_id)
        contact_id = self.request.query_params.get("contact")
        if contact_id:
            queryset = queryset.filter(contact_id=contact_id)
        customer_id = self.request.query_params.get("customer")
        if customer_id:
            queryset = queryset.filter(customer_id=customer_id)
        if self.request.query_params.get("upcoming") == "true":
            queryset = queryset.filter(starts_at__gte=timezone.now()).exclude(status=Appointment.Status.CANCELLED)
        date_value = self.request.query_params.get("date")
        if date_value:
            parsed = parse_date(date_value)
            if parsed:
                start = timezone.make_aware(datetime.combine(parsed, time.min), timezone.get_current_timezone())
                end = start + timedelta(days=1)
                queryset = queryset.filter(starts_at__gte=start, starts_at__lt=end)
        else:
            date_from = parse_date(self.request.query_params.get("date_from") or "")
            if date_from:
                start = timezone.make_aware(datetime.combine(date_from, time.min), timezone.get_current_timezone())
                queryset = queryset.filter(starts_at__gte=start)
            date_to = parse_date(self.request.query_params.get("date_to") or "")
            if date_to:
                end = timezone.make_aware(datetime.combine(date_to, time.min), timezone.get_current_timezone()) + timedelta(days=1)
                queryset = queryset.filter(starts_at__lt=end)
        return queryset

    def perform_create(self, serializer):
        appointment = serializer.save(created_by=self.request.user)
        if appointment.status == Appointment.Status.CONFIRMED:
            notify_appointment_confirmation(appointment)

    def perform_update(self, serializer):
        previous = self.get_object()
        old_status = previous.status
        old_starts_at = previous.starts_at
        old_ends_at = previous.ends_at
        appointment = serializer.save()
        if appointment.status == Appointment.Status.CANCELLED and old_status != Appointment.Status.CANCELLED:
            if not appointment.cancelled_by_id:
                appointment.cancelled_by = self.request.user
                appointment.save(update_fields=["cancelled_by", "updated_at"])
            notify_appointment_cancellation(appointment)
        elif appointment.status == Appointment.Status.CONFIRMED and old_status == Appointment.Status.CONFIRMED:
            if appointment.starts_at != old_starts_at or appointment.ends_at != old_ends_at:
                notify_appointment_reschedule(appointment)

    @action(detail=True, methods=["patch"])
    def cancel(self, request, pk=None):
        appointment = self.get_object()
        if appointment.status != Appointment.Status.CANCELLED:
            appointment.status = Appointment.Status.CANCELLED
            appointment.cancelled_by = request.user
            appointment.cancellation_reason = request.data.get("reason", appointment.cancellation_reason)
            appointment.save(update_fields=["status", "cancelled_by", "cancellation_reason", "updated_at"])
            notify_appointment_cancellation(appointment)
        return Response(self.get_serializer(appointment).data)

    @action(detail=True, methods=["patch"])
    def complete(self, request, pk=None):
        appointment = self.get_object()
        appointment.status = Appointment.Status.COMPLETED
        appointment.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(appointment).data)

    @action(detail=True, methods=["patch"], url_path="no-show")
    def no_show(self, request, pk=None):
        appointment = self.get_object()
        appointment.status = Appointment.Status.NO_SHOW
        appointment.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(appointment).data)

    @action(detail=True, methods=["get", "post"], url_path="photos")
    def photos(self, request, pk=None):
        appointment = self.get_object()
        if request.method == "GET":
            photos = appointment.photos.select_related("created_by").all()
            return Response(AppointmentPhotoSerializer(photos, many=True, context={"request": request}).data)
        serializer = AppointmentPhotoSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        photo = serializer.save(appointment=appointment, created_by=request.user)
        return Response(AppointmentPhotoSerializer(photo, context={"request": request}).data, status=status.HTTP_201_CREATED)


class AppointmentAvailabilityWindowViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]
    queryset = AppointmentAvailabilityWindow.objects.all()
    serializer_class = AppointmentAvailabilityWindowSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["date", "weekday", "starts_at", "ordering", "updated_at"]

    def get_queryset(self):
        queryset = super().get_queryset()
        weekday = self.request.query_params.get("weekday")
        if weekday not in {None, ""}:
            queryset = queryset.filter(weekday=weekday)
        active = self.request.query_params.get("active")
        if active in {"true", "false"}:
            queryset = queryset.filter(active=active == "true")
        date_value = parse_date(self.request.query_params.get("date") or "")
        if date_value:
            queryset = queryset.filter(date=date_value)
        date_from = parse_date(self.request.query_params.get("date_from") or "")
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        date_to = parse_date(self.request.query_params.get("date_to") or "")
        if date_to:
            queryset = queryset.filter(date__lte=date_to)
        return queryset

    def perform_destroy(self, instance):
        if instance.date:
            instance.active = False
            instance.save(update_fields=["active", "updated_at"])
            return
        instance.delete()

    @action(detail=True, methods=["post"], url_path="impact")
    def impact(self, request, pk=None):
        window = self.get_object()
        data = request.data.copy() if hasattr(request.data, "copy") else dict(request.data)
        for key in ["delete", "action", "operation", "mode"]:
            if key not in data and key in request.query_params:
                data[key] = request.query_params[key]

        serializer = AppointmentAvailabilityImpactRequestSerializer(data=data, context={"window": window})
        serializer.is_valid(raise_exception=True)
        proposed_fields = {"date", "weekday", "starts_at", "ends_at", "active", "label", "ordering"}
        proposed_values = {key: value for key, value in serializer.validated_data.items() if key in proposed_fields}
        appointments = availability_impact_for_window_change(
            window,
            proposed_values=proposed_values,
            delete=serializer.validated_data["delete"],
        )
        appointment_data = AppointmentAvailabilityImpactAppointmentSerializer(appointments, many=True).data
        return Response({"affected_count": len(appointment_data), "appointments": appointment_data})


class AppointmentBlockViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]
    queryset = AppointmentBlock.objects.all()
    serializer_class = AppointmentBlockSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["reason"]
    ordering_fields = ["starts_at", "ends_at", "updated_at"]

    def get_queryset(self):
        queryset = super().get_queryset()
        active = self.request.query_params.get("active")
        if active in {"true", "false"}:
            queryset = queryset.filter(active=active == "true")
        return queryset


class AppointmentFinanceEntryViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]
    serializer_class = AppointmentFinanceEntrySerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["label", "notes", "appointment__full_name", "appointment__phone"]
    ordering_fields = ["entry_date", "amount", "created_at", "updated_at"]

    def get_queryset(self):
        queryset = AppointmentFinanceEntry.objects.select_related("appointment", "appointment__service", "created_by").all()
        entry_type = self.request.query_params.get("entry_type")
        if entry_type:
            queryset = queryset.filter(entry_type=entry_type)
        appointment_id = self.request.query_params.get("appointment")
        if appointment_id:
            queryset = queryset.filter(appointment_id=appointment_id)
        return queryset

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class FounderDashboardView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        period = request.query_params.get("period", "today")
        return Response(founder_dashboard_metrics(period))
