from __future__ import annotations

from datetime import datetime, time, timedelta
from decimal import Decimal
from typing import Any
from zoneinfo import ZoneInfo

from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import Min, Q, Sum
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.accounts.models import CustomerNotificationSubscription
from apps.accounts.services import customer_profile_payload, ensure_customer_profile_for_user, validate_customer_account_user
from apps.appointments.models import Appointment, AppointmentAvailabilityWindow, AppointmentBlock, AppointmentFinanceEntry, AppointmentNotificationLog
from apps.campaigns.models import CampaignForm, CampaignFormResponse
from apps.contacts.services import normalize_email, sync_campaign_response_to_contact
from apps.content.models import Service


APPOINTMENT_AVAILABILITY_ZONE = ZoneInfo("Asia/Kolkata")


def service_duration_minutes(service: Service) -> int:
    return max(int(service.duration_minutes or 60), 1)


def service_buffer_minutes(service: Service) -> int:
    return max(int(service.booking_buffer_minutes or 0), 0)


def appointment_downtime_minutes() -> int:
    return max(int(getattr(settings, "APPOINTMENT_DOWNTIME_MINUTES", 15) or 0), 0)


def effective_buffer_minutes_for_service(service: Service) -> int:
    return max(appointment_downtime_minutes(), service_buffer_minutes(service))


def appointment_end_for_service(service: Service, starts_at) -> datetime:
    return starts_at + timedelta(minutes=service_duration_minutes(service))


def local_datetime(slot_date, clock: time) -> datetime:
    return timezone.make_aware(datetime.combine(slot_date, clock), timezone.get_current_timezone())


def validate_scheduling_enabled() -> None:
    if not getattr(settings, "FIRST_PARTY_SCHEDULING_ENABLED", True):
        raise ValidationError({"detail": "First-party scheduling is not enabled."})


def validate_service_bookable(service: Service) -> None:
    validate_scheduling_enabled()
    if not service.active:
        raise ValidationError({"service": "This service is not active."})
    if not service.accepts_online_booking:
        raise ValidationError({"service": "This service is not accepting online bookings."})


def available_slots_for_service(service: Service, slot_date, *, now: datetime | None = None, exclude_appointment_id: int | None = None) -> list[dict[str, datetime]]:
    validate_service_bookable(service)
    now = now or timezone.now()
    local_today = timezone.localdate(now)
    horizon_days = int(getattr(settings, "APPOINTMENT_SLOT_HORIZON_DAYS", 60))
    if slot_date < local_today or slot_date > local_today + timedelta(days=horizon_days):
        return []

    duration = timedelta(minutes=service_duration_minutes(service))
    buffer = timedelta(minutes=effective_buffer_minutes_for_service(service))
    min_start = now + timedelta(minutes=int(getattr(settings, "APPOINTMENT_MIN_LEAD_MINUTES", 240)))
    slots: list[dict[str, datetime]] = []
    dated_windows = AppointmentAvailabilityWindow.objects.filter(date=slot_date).order_by("ordering", "starts_at", "id")
    if dated_windows.exists():
        windows = dated_windows.filter(active=True)
    else:
        windows = AppointmentAvailabilityWindow.objects.filter(active=True, date__isnull=True, weekday=slot_date.weekday()).order_by("ordering", "starts_at", "id")
    for window in windows:
        current = local_datetime(slot_date, window.starts_at)
        window_end = local_datetime(slot_date, window.ends_at)
        while current + duration <= window_end:
            slot_end = current + duration
            if current >= min_start and is_slot_available(service, current, slot_end, exclude_appointment_id=exclude_appointment_id):
                slots.append({"starts_at": current, "ends_at": slot_end})
            current = slot_end + buffer
    return slots


def is_slot_available(service: Service, starts_at: datetime, ends_at: datetime, *, exclude_appointment_id: int | None = None) -> bool:
    if AppointmentBlock.objects.filter(active=True, starts_at__lt=ends_at, ends_at__gt=starts_at).exists():
        return False

    appointments = Appointment.objects.select_related("service").filter(status=Appointment.Status.CONFIRMED)
    if exclude_appointment_id:
        appointments = appointments.exclude(pk=exclude_appointment_id)
    for appointment in appointments:
        buffer = effective_buffer_minutes_for_service(appointment.service)
        appointment_range_start = appointment.starts_at - timedelta(minutes=buffer)
        appointment_range_end = appointment.ends_at + timedelta(minutes=buffer)
        if starts_at < appointment_range_end and ends_at > appointment_range_start:
            return False
    return True


def availability_window_covers_appointment(window: AppointmentAvailabilityWindow, appointment: Appointment) -> bool:
    if not window.active:
        return False
    starts_at = timezone.localtime(appointment.starts_at, APPOINTMENT_AVAILABILITY_ZONE)
    ends_at = timezone.localtime(appointment.ends_at, APPOINTMENT_AVAILABILITY_ZONE)
    if starts_at.date() != ends_at.date():
        return False
    if window.date and starts_at.date() != window.date:
        return False
    return (
        starts_at.weekday() == window.weekday
        and window.starts_at <= starts_at.time()
        and ends_at.time() <= window.ends_at
    )


def proposed_availability_window(
    window: AppointmentAvailabilityWindow,
    proposed_values: dict[str, Any],
) -> AppointmentAvailabilityWindow:
    return AppointmentAvailabilityWindow(
        date=proposed_values.get("date", window.date),
        weekday=proposed_values.get("weekday", window.weekday),
        starts_at=proposed_values.get("starts_at", window.starts_at),
        ends_at=proposed_values.get("ends_at", window.ends_at),
        active=proposed_values.get("active", window.active),
        label=proposed_values.get("label", window.label),
        ordering=proposed_values.get("ordering", window.ordering),
    )


def availability_impact_for_window_change(
    window: AppointmentAvailabilityWindow,
    *,
    proposed_values: dict[str, Any] | None = None,
    delete: bool = False,
    now: datetime | None = None,
) -> list[Appointment]:
    if not window.active:
        return []

    now = now or timezone.now()
    proposed_values = proposed_values or {}
    all_windows = list(
        AppointmentAvailabilityWindow.objects.exclude(pk=window.pk).order_by("date", "weekday", "ordering", "starts_at", "id")
    )
    if not delete:
        proposed_window = proposed_availability_window(window, proposed_values)
        if proposed_window.date:
            proposed_window.weekday = proposed_window.date.weekday()
        all_windows.append(proposed_window)
    active_windows = [candidate for candidate in all_windows if candidate.active]

    affected: list[Appointment] = []
    appointments = (
        Appointment.objects.select_related("service")
        .filter(status=Appointment.Status.CONFIRMED, starts_at__gte=now)
        .order_by("starts_at", "id")
    )
    for appointment in appointments:
        if not availability_window_covers_appointment(window, appointment):
            continue
        if not appointment_is_covered_by_effective_windows(appointment, all_windows, active_windows):
            affected.append(appointment)
    return affected


def appointment_is_covered_by_effective_windows(
    appointment: Appointment,
    all_windows: list[AppointmentAvailabilityWindow],
    active_windows: list[AppointmentAvailabilityWindow],
) -> bool:
    local_date = timezone.localtime(appointment.starts_at, APPOINTMENT_AVAILABILITY_ZONE).date()
    if any(window.date == local_date for window in all_windows):
        candidates = [window for window in active_windows if window.date == local_date]
    else:
        candidates = [window for window in active_windows if window.date is None]
    return any(availability_window_covers_appointment(candidate, appointment) for candidate in candidates)


def validate_selected_slot(service: Service, starts_at: datetime, *, exclude_appointment_id: int | None = None) -> datetime:
    ends_at = appointment_end_for_service(service, starts_at)
    slot_date = timezone.localdate(starts_at)
    for slot in available_slots_for_service(service, slot_date, exclude_appointment_id=exclude_appointment_id):
        if slot["starts_at"] == starts_at and slot["ends_at"] == ends_at:
            return ends_at
    raise ValidationError({"starts_at": "Choose an available slot."})


def validate_no_confirmed_overlap(starts_at: datetime, ends_at: datetime, *, exclude_appointment_id: int | None = None) -> None:
    overlaps = Appointment.objects.select_related("service").filter(status=Appointment.Status.CONFIRMED)
    if exclude_appointment_id:
        overlaps = overlaps.exclude(pk=exclude_appointment_id)
    for appointment in overlaps:
        buffer = effective_buffer_minutes_for_service(appointment.service)
        if starts_at < appointment.ends_at + timedelta(minutes=buffer) and ends_at > appointment.starts_at - timedelta(minutes=buffer):
            raise ValidationError({"starts_at": "This appointment overlaps another confirmed appointment or downtime window."})


@transaction.atomic
def create_public_appointment(*, service: Service, values: dict[str, Any], request=None) -> Appointment:
    validate_service_bookable(service)
    starts_at = values["starts_at"]
    ends_at = validate_selected_slot(service, starts_at)
    response, contact = create_booking_campaign_response(service=service, values=values, request=request, source=Appointment.Source.WEBSITE)
    appointment = Appointment.objects.create(
        service=service,
        contact=contact,
        full_name=values["full_name"],
        phone=values["phone"],
        email=normalize_email(values.get("email", "")),
        notes=values.get("notes", ""),
        skin_goal=values.get("skin_goal", ""),
        starts_at=starts_at,
        ends_at=ends_at,
        duration_minutes=service_duration_minutes(service),
        status=Appointment.Status.CONFIRMED,
        source=Appointment.Source.WEBSITE,
        campaign_response=response,
        customer_notes=values.get("customer_notes", ""),
    )
    notify_appointment_confirmation(appointment)
    return appointment


@transaction.atomic
def create_customer_appointment(*, user, service: Service, values: dict[str, Any], request=None) -> Appointment:
    validate_customer_account_user(user)
    profile = ensure_customer_profile_for_user(user, phone=values.get("phone", ""), full_name=values.get("full_name", ""))
    profile_data = customer_profile_payload(user)
    full_name = values.get("full_name") or profile_data.get("full_name") or user.get_full_name() or user.email
    phone = values.get("phone") or profile_data.get("phone") or ""
    if not phone:
        raise ValidationError({"phone": "Phone is required to book an appointment."})
    appointment_values = {
        **values,
        "full_name": full_name,
        "phone": phone,
        "email": normalize_email(values.get("email") or profile_data.get("email") or user.email),
    }
    validate_service_bookable(service)
    starts_at = appointment_values["starts_at"]
    ends_at = validate_selected_slot(service, starts_at)
    response, contact = create_booking_campaign_response(
        service=service,
        values=appointment_values,
        request=request,
        source=Appointment.Source.CUSTOMER_APP,
    )
    appointment = Appointment.objects.create(
        service=service,
        contact=contact or profile.contact,
        customer=user,
        full_name=appointment_values["full_name"],
        phone=appointment_values["phone"],
        email=appointment_values["email"],
        notes=appointment_values.get("notes", ""),
        skin_goal=appointment_values.get("skin_goal", ""),
        starts_at=starts_at,
        ends_at=ends_at,
        duration_minutes=service_duration_minutes(service),
        status=Appointment.Status.CONFIRMED,
        source=Appointment.Source.CUSTOMER_APP,
        campaign_response=response,
        customer_notes=appointment_values.get("customer_notes", ""),
    )
    notify_appointment_confirmation(appointment)
    return appointment


def create_booking_campaign_response(*, service: Service, values: dict[str, Any], request=None, source: str) -> tuple[CampaignFormResponse, Any]:
    form = service.booking_campaign or CampaignForm.objects.filter(slug="glow-consultation").first()
    if not form:
        raise ValidationError({"detail": "Booking form is not configured."})

    starts_at = values["starts_at"]
    response_data = {
        "full_name": values["full_name"],
        "phone": values["phone"],
        "email": normalize_email(values.get("email", "")),
        "preferred_ritual": service.title,
        "skin_goal": values.get("skin_goal", ""),
        "appointment_starts_at": starts_at.isoformat(),
    }
    metadata = {
        "source": "first_party_appointment",
        "appointment_source": source,
        "service_id": service.pk,
        "service_slug": service.slug,
    }
    if request:
        metadata.update(
            {
                "ip": request.META.get("HTTP_X_FORWARDED_FOR", request.META.get("REMOTE_ADDR", "")),
                "user_agent": request.META.get("HTTP_USER_AGENT", ""),
            }
        )
    response = CampaignFormResponse.objects.create(
        form=form,
        response_data=response_data,
        metadata=metadata,
        field_snapshot=appointment_booking_field_snapshot(),
    )
    result = sync_campaign_response_to_contact(response)
    return response, result.contact


def appointment_booking_field_snapshot() -> list[dict[str, Any]]:
    return [
        {"id": 0, "label": "Full name", "key": "full_name", "field_type": "text", "required": True, "options": [], "validation": {}, "ordering": 0},
        {"id": 0, "label": "Phone", "key": "phone", "field_type": "phone", "required": True, "options": [], "validation": {}, "ordering": 1},
        {"id": 0, "label": "Email", "key": "email", "field_type": "email", "required": False, "options": [], "validation": {}, "ordering": 2},
        {"id": 0, "label": "Preferred ritual", "key": "preferred_ritual", "field_type": "text", "required": False, "options": [], "validation": {}, "ordering": 3},
        {"id": 0, "label": "Skin goal", "key": "skin_goal", "field_type": "textarea", "required": False, "options": [], "validation": {}, "ordering": 4},
        {"id": 0, "label": "Appointment start", "key": "appointment_starts_at", "field_type": "text", "required": False, "options": [], "validation": {}, "ordering": 5},
    ]


def customer_appointment_queryset(user):
    validate_customer_account_user(user)
    profile = ensure_customer_profile_for_user(user)
    queryset = Appointment.objects.select_related("service", "contact", "customer", "campaign_response")
    filters = Q(customer=user)
    if profile.contact_id:
        filters |= Q(contact=profile.contact)
    return queryset.filter(filters).distinct().order_by("starts_at", "id")


def assert_customer_can_change(appointment: Appointment) -> None:
    cutoff = timezone.now() + timedelta(minutes=int(getattr(settings, "APPOINTMENT_CUSTOMER_CHANGE_CUTOFF_MINUTES", 720)))
    if appointment.starts_at <= cutoff:
        raise ValidationError({"starts_at": "This appointment is too close to change from the customer app."})


@transaction.atomic
def cancel_customer_appointment(*, appointment: Appointment, user, reason: str = "") -> Appointment:
    validate_customer_account_user(user)
    assert_customer_can_change(appointment)
    if appointment.status != Appointment.Status.CONFIRMED:
        raise ValidationError({"status": "Only confirmed appointments can be cancelled."})
    appointment.status = Appointment.Status.CANCELLED
    appointment.cancelled_by = user
    appointment.cancellation_reason = reason
    appointment.save(update_fields=["status", "cancelled_by", "cancellation_reason", "updated_at"])
    notify_appointment_cancellation(appointment)
    return appointment


@transaction.atomic
def reschedule_customer_appointment(*, appointment: Appointment, user, starts_at: datetime) -> Appointment:
    validate_customer_account_user(user)
    assert_customer_can_change(appointment)
    if appointment.status != Appointment.Status.CONFIRMED:
        raise ValidationError({"status": "Only confirmed appointments can be rescheduled."})
    ends_at = validate_selected_slot(appointment.service, starts_at, exclude_appointment_id=appointment.pk)
    appointment.starts_at = starts_at
    appointment.ends_at = ends_at
    appointment.duration_minutes = service_duration_minutes(appointment.service)
    appointment.save(update_fields=["starts_at", "ends_at", "duration_minutes", "updated_at"])
    notify_appointment_reschedule(appointment)
    return appointment


def notify_appointment_confirmation(appointment: Appointment) -> list[AppointmentNotificationLog]:
    return dispatch_appointment_notifications(appointment, AppointmentNotificationLog.EventType.CONFIRMATION)


def notify_appointment_reschedule(appointment: Appointment) -> list[AppointmentNotificationLog]:
    return dispatch_appointment_notifications(appointment, AppointmentNotificationLog.EventType.RESCHEDULE)


def notify_appointment_cancellation(appointment: Appointment) -> list[AppointmentNotificationLog]:
    return dispatch_appointment_notifications(appointment, AppointmentNotificationLog.EventType.CANCELLATION)


def notify_appointment_reminder(appointment: Appointment, reminder_minutes: int) -> list[AppointmentNotificationLog]:
    return dispatch_appointment_notifications(appointment, AppointmentNotificationLog.EventType.REMINDER, reminder_minutes=reminder_minutes)


def dispatch_appointment_notifications(
    appointment: Appointment,
    event_type: str,
    *,
    reminder_minutes: int | None = None,
) -> list[AppointmentNotificationLog]:
    logs = [send_appointment_email(appointment, event_type, reminder_minutes=reminder_minutes)]
    logs.extend(log_push_delivery_foundation(appointment, AppointmentNotificationLog.Channel.EXPO, event_type, reminder_minutes=reminder_minutes))
    logs.extend(log_push_delivery_foundation(appointment, AppointmentNotificationLog.Channel.WEB_PUSH, event_type, reminder_minutes=reminder_minutes))
    return logs


def send_appointment_email(appointment: Appointment, event_type: str, *, reminder_minutes: int | None = None) -> AppointmentNotificationLog:
    recipient = recipient_email_for_appointment(appointment)
    if not recipient:
        return create_notification_log(
            appointment,
            AppointmentNotificationLog.Channel.EMAIL,
            event_type,
            "",
            AppointmentNotificationLog.Status.SKIPPED,
            "No email recipient is available.",
            reminder_minutes=reminder_minutes,
        )
    try:
        send_mail(
            appointment_email_subject(appointment, event_type, reminder_minutes),
            appointment_email_body(appointment, event_type, reminder_minutes),
            getattr(settings, "DEFAULT_FROM_EMAIL", ""),
            [recipient],
            fail_silently=False,
        )
    except Exception as exc:  # pragma: no cover - depends on provider failures.
        return create_notification_log(
            appointment,
            AppointmentNotificationLog.Channel.EMAIL,
            event_type,
            recipient,
            AppointmentNotificationLog.Status.FAILED,
            str(exc),
            reminder_minutes=reminder_minutes,
        )
    return create_notification_log(
        appointment,
        AppointmentNotificationLog.Channel.EMAIL,
        event_type,
        recipient,
        AppointmentNotificationLog.Status.SENT,
        "",
        reminder_minutes=reminder_minutes,
        sent_at=timezone.now(),
    )


def log_push_delivery_foundation(
    appointment: Appointment,
    channel: str,
    event_type: str,
    *,
    reminder_minutes: int | None = None,
) -> list[AppointmentNotificationLog]:
    subscriptions = notification_subscriptions_for_appointment(appointment, channel)
    logs: list[AppointmentNotificationLog] = []
    for subscription in subscriptions:
        recipient = subscription.token if channel == AppointmentNotificationLog.Channel.EXPO else subscription.subscription_endpoint
        if channel == AppointmentNotificationLog.Channel.EXPO:
            has_credentials = bool(getattr(settings, "EXPO_PUSH_ACCESS_TOKEN", ""))
            missing_message = "EXPO_PUSH_ACCESS_TOKEN is not configured."
            unavailable_message = "Expo push delivery is not implemented yet."
        else:
            has_credentials = bool(getattr(settings, "WEB_PUSH_PUBLIC_KEY", "") and getattr(settings, "WEB_PUSH_PRIVATE_KEY", ""))
            missing_message = "WEB_PUSH_PUBLIC_KEY and WEB_PUSH_PRIVATE_KEY are not configured."
            unavailable_message = "Web push delivery is not implemented yet."
        status = AppointmentNotificationLog.Status.PENDING if has_credentials else AppointmentNotificationLog.Status.SKIPPED
        logs.append(
            create_notification_log(
                appointment,
                channel,
                event_type,
                recipient,
                status,
                unavailable_message if has_credentials else missing_message,
                reminder_minutes=reminder_minutes,
            )
        )
    return logs


def notification_subscriptions_for_appointment(appointment: Appointment, channel: str):
    filters = Q()
    if appointment.customer_id:
        filters |= Q(user=appointment.customer)
    if appointment.contact_id:
        filters |= Q(contact=appointment.contact)
    if not filters:
        return CustomerNotificationSubscription.objects.none()
    return CustomerNotificationSubscription.objects.filter(filters, channel=channel, enabled=True).distinct()


def create_notification_log(
    appointment: Appointment,
    channel: str,
    event_type: str,
    recipient: str,
    status: str,
    error: str = "",
    *,
    reminder_minutes: int | None = None,
    sent_at=None,
) -> AppointmentNotificationLog:
    return AppointmentNotificationLog.objects.create(
        appointment=appointment,
        channel=channel,
        event_type=event_type,
        reminder_minutes=reminder_minutes,
        recipient=recipient,
        status=status,
        error=error,
        sent_at=sent_at,
    )


def recipient_email_for_appointment(appointment: Appointment) -> str:
    if appointment.email:
        return appointment.email
    if appointment.customer_id and appointment.customer.email:
        return appointment.customer.email
    if appointment.contact_id and appointment.contact and appointment.contact.email:
        return appointment.contact.email
    return ""


def appointment_email_subject(appointment: Appointment, event_type: str, reminder_minutes: int | None = None) -> str:
    if event_type == AppointmentNotificationLog.EventType.REMINDER:
        hours = int((reminder_minutes or 0) / 60)
        return f"Reminder: your The Glow Mission appointment is in {hours} hours"
    labels = {
        AppointmentNotificationLog.EventType.CONFIRMATION: "Your The Glow Mission appointment is confirmed",
        AppointmentNotificationLog.EventType.RESCHEDULE: "Your The Glow Mission appointment was rescheduled",
        AppointmentNotificationLog.EventType.CANCELLATION: "Your The Glow Mission appointment was cancelled",
    }
    return labels.get(event_type, "The Glow Mission appointment update")


def appointment_email_body(appointment: Appointment, event_type: str, reminder_minutes: int | None = None) -> str:
    local_start = timezone.localtime(appointment.starts_at).strftime("%A, %d %B %Y at %I:%M %p")
    opening = {
        AppointmentNotificationLog.EventType.CONFIRMATION: "Your appointment is confirmed.",
        AppointmentNotificationLog.EventType.RESCHEDULE: "Your appointment has been rescheduled.",
        AppointmentNotificationLog.EventType.CANCELLATION: "Your appointment has been cancelled.",
        AppointmentNotificationLog.EventType.REMINDER: "This is a reminder for your upcoming appointment.",
    }.get(event_type, "Your appointment has an update.")
    return (
        f"{opening}\n\n"
        f"Service: {appointment.service.title}\n"
        f"When: {local_start}\n"
        f"Name: {appointment.full_name}\n\n"
        "The Glow Mission"
    )


def due_reminder_offsets() -> list[int]:
    return sorted({int(value) for value in getattr(settings, "APPOINTMENT_REMINDER_MINUTES", [1440, 120]) if int(value) > 0}, reverse=True)


def send_due_appointment_reminders(*, now: datetime | None = None) -> dict[str, int]:
    now = now or timezone.now()
    offsets = due_reminder_offsets()
    sent = 0
    skipped = 0
    for index, minutes in enumerate(offsets):
        lower_minutes = offsets[index + 1] if index + 1 < len(offsets) else 0
        lower_bound = now + timedelta(minutes=lower_minutes)
        upper_bound = now + timedelta(minutes=minutes)
        appointments = Appointment.objects.filter(
            status=Appointment.Status.CONFIRMED,
            starts_at__gt=lower_bound,
            starts_at__lte=upper_bound,
        ).select_related("service", "contact", "customer")
        for appointment in appointments:
            if AppointmentNotificationLog.objects.filter(
                appointment=appointment,
                event_type=AppointmentNotificationLog.EventType.REMINDER,
                reminder_minutes=minutes,
            ).exists():
                skipped += 1
                continue
            notify_appointment_reminder(appointment, minutes)
            sent += 1
    return {"sent": sent, "skipped": skipped}


def founder_dashboard_metrics(period: str) -> dict[str, Any]:
    start, end = dashboard_period_bounds(period)
    appointments = Appointment.objects.select_related("service").filter(starts_at__gte=start, starts_at__lt=end)
    active_appointments = appointments.exclude(status__in=[Appointment.Status.CANCELLED, Appointment.Status.NO_SHOW])
    completed_appointments = appointments.filter(status=Appointment.Status.COMPLETED)

    def appointment_value(appointment: Appointment) -> Decimal:
        amount = appointment.service.sale_price_amount
        if amount is None:
            amount = appointment.service.price_amount
        return amount or Decimal("0.00")

    service_revenue = Decimal("0.00")
    for appointment in active_appointments:
        service_revenue += appointment_value(appointment)

    completed_revenue = Decimal("0.00")
    returning_revenue = Decimal("0.00")
    returning_contact_ids: set[int] = set()
    completed_contact_ids = set(completed_appointments.exclude(contact_id__isnull=True).values_list("contact_id", flat=True))
    previous_completed_contact_ids = set(
        Appointment.objects.filter(status=Appointment.Status.COMPLETED, contact_id__in=completed_contact_ids, starts_at__lt=start).values_list("contact_id", flat=True)
    )
    for appointment in completed_appointments:
        amount = appointment_value(appointment)
        completed_revenue += amount
        if appointment.contact_id and appointment.contact_id in previous_completed_contact_ids:
            returning_revenue += amount
            returning_contact_ids.add(appointment.contact_id)

    finance_entries = AppointmentFinanceEntry.objects.filter(entry_date__gte=start.date(), entry_date__lt=end.date())
    manual_income = finance_entries.filter(entry_type=AppointmentFinanceEntry.EntryType.INCOME).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
    manual_expense = finance_entries.filter(entry_type=AppointmentFinanceEntry.EntryType.EXPENSE).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")

    from apps.campaigns.models import CampaignFormResponse
    from apps.contacts.models import Contact

    total_appointments = appointments.count()
    completed_count = completed_appointments.count()
    cancelled_count = appointments.filter(status=Appointment.Status.CANCELLED).count()
    no_show_count = appointments.filter(status=Appointment.Status.NO_SHOW).count()
    new_customer_count, first_to_second_visit_rate = first_to_second_visit_metrics(start, end)
    gross_margin = completed_revenue + manual_income - manual_expense
    gst_rate = Decimal(str(getattr(settings, "GLOW_GST_RATE_PERCENT", "18") or "0"))
    gst_reserve = (completed_revenue * gst_rate / Decimal("100.0")).quantize(Decimal("0.01"))
    available_cash_estimate = completed_revenue + manual_income - manual_expense - gst_reserve
    submitted_enquiries = CampaignFormResponse.objects.filter(submitted_at__gte=start, submitted_at__lt=end).count()
    capacity_minutes = available_treatment_minutes(start, end)
    completed_minutes = sum(int(value or 0) for value in completed_appointments.values_list("duration_minutes", flat=True))

    headline_metrics = [
        {"key": "net_revenue", "label": "Net revenue estimate", "value": money(completed_revenue + manual_income), "description": "Completed ritual value plus manual income; discounts/refunds are not fully modeled yet."},
        {"key": "cash_collected", "label": "Cash collected", "value": money(manual_income), "description": "Manual income entries recorded in finance."},
        {"key": "completed_rituals", "label": "Completed rituals", "value": completed_count},
        {"key": "average_booking_value", "label": "Average booking value", "value": money(completed_revenue / completed_count if completed_count else Decimal("0.00"))},
        {"key": "new_customers", "label": "New paying customers", "value": new_customer_count},
        {"key": "returning_customers", "label": "Returning customers", "value": len(returning_contact_ids)},
        {"key": "repeat_revenue_percentage", "label": "Repeat revenue %", "value": percent(returning_revenue, completed_revenue)},
        {"key": "first_to_second_visit_rate", "label": "First-to-second visit rate", "value": first_to_second_visit_rate},
        {"key": "enquiry_to_completed_booking", "label": "Enquiry-to-completed booking", "value": percent(completed_count, submitted_enquiries)},
        {"key": "customer_acquisition_cost", "label": "Customer acquisition cost", "value": "Not tracked", "description": "Needs marketing spend entries by source."},
        {"key": "cancellation_rate", "label": "Cancellation rate", "value": percent(cancelled_count, total_appointments)},
        {"key": "no_show_rate", "label": "No-show rate", "value": percent(no_show_count, total_appointments)},
        {"key": "capacity_utilisation", "label": "Capacity utilisation", "value": percent(completed_minutes, capacity_minutes), "description": "Based on active availability windows for the single room/founder setup."},
        {"key": "gross_margin", "label": "Gross margin estimate", "value": percent(gross_margin, completed_revenue + manual_income)},
        {"key": "gst_tax_reserve", "label": "GST/tax reserve estimate", "value": money(gst_reserve), "description": f"Uses {gst_rate}% GST reserve setting; confirm final tax treatment with the accountant."},
    ]

    return {
        "period": period,
        "period_start": start,
        "period_end": end,
        "generated_at": timezone.now(),
        "headline_metrics": headline_metrics,
        "appointments": {
            "total": appointments.count(),
            "confirmed": appointments.filter(status=Appointment.Status.CONFIRMED).count(),
            "completed": appointments.filter(status=Appointment.Status.COMPLETED).count(),
            "cancelled": appointments.filter(status=Appointment.Status.CANCELLED).count(),
            "no_show": appointments.filter(status=Appointment.Status.NO_SHOW).count(),
        },
        "contacts": {
            "created": Contact.objects.filter(created_at__gte=start, created_at__lt=end, is_merged=False).count(),
        },
        "campaign_responses": {
            "submitted": CampaignFormResponse.objects.filter(submitted_at__gte=start, submitted_at__lt=end).count(),
        },
        "finance": {
            "service_revenue": service_revenue,
            "manual_income": manual_income,
            "manual_expense": manual_expense,
            "manual_net": manual_income - manual_expense,
            "revenue_estimate": service_revenue + manual_income,
            "net_estimate": service_revenue + manual_income - manual_expense,
            "completed_revenue": completed_revenue,
            "gst_reserve_estimate": gst_reserve,
            "available_cash_estimate": available_cash_estimate,
        },
    }


def first_to_second_visit_metrics(start: datetime, end: datetime) -> tuple[int, str]:
    first_visits = (
        Appointment.objects.filter(status=Appointment.Status.COMPLETED, contact_id__isnull=False)
        .values("contact_id")
        .annotate(first_visit=Min("starts_at"))
        .filter(first_visit__gte=start, first_visit__lt=end)
    )
    converted = 0
    first_visits = list(first_visits)
    for item in first_visits:
        first_visit = item["first_visit"]
        if Appointment.objects.filter(
            status=Appointment.Status.COMPLETED,
            contact_id=item["contact_id"],
            starts_at__gt=first_visit,
            starts_at__lte=first_visit + timedelta(days=60),
        ).exists():
            converted += 1
    return len(first_visits), percent(converted, len(first_visits))


def available_treatment_minutes(start: datetime, end: datetime) -> int:
    windows = list(AppointmentAvailabilityWindow.objects.filter(date__isnull=False))
    recurring_by_weekday: dict[int, list[AppointmentAvailabilityWindow]] = {}
    dated_by_date: dict[Any, list[AppointmentAvailabilityWindow]] = {}
    for window in windows:
        dated_by_date.setdefault(window.date, []).append(window)
    for window in AppointmentAvailabilityWindow.objects.filter(active=True, date__isnull=True):
        recurring_by_weekday.setdefault(window.weekday, []).append(window)
    total = 0
    current_date = timezone.localtime(start).date()
    end_date = timezone.localtime(end).date()
    while current_date < end_date:
        if current_date in dated_by_date:
            day_windows = [window for window in dated_by_date[current_date] if window.active]
        else:
            day_windows = recurring_by_weekday.get(current_date.weekday(), [])
        for window in day_windows:
            window_start = datetime.combine(current_date, window.starts_at)
            window_end = datetime.combine(current_date, window.ends_at)
            total += max(int((window_end - window_start).total_seconds() // 60), 0)
        current_date += timedelta(days=1)
    return total


def money(value: Decimal) -> str:
    return f"₹{float(value or Decimal('0.00')):,.0f}"


def percent(numerator, denominator) -> str:
    numerator = Decimal(str(numerator or 0))
    denominator = Decimal(str(denominator or 0))
    if denominator == 0:
        return "0%"
    return f"{(numerator / denominator * Decimal('100')).quantize(Decimal('0.1'))}%"


def dashboard_period_bounds(period: str) -> tuple[datetime, datetime]:
    local_now = timezone.localtime(timezone.now())
    local_date = local_now.date()
    tz = timezone.get_current_timezone()
    if period == "today":
        start_date = local_date
        end_date = local_date + timedelta(days=1)
    elif period == "this_week":
        start_date = local_date - timedelta(days=local_date.weekday())
        end_date = start_date + timedelta(days=7)
    elif period == "this_month":
        start_date = local_date.replace(day=1)
        end_date = add_month(start_date)
    elif period == "previous_month":
        this_month = local_date.replace(day=1)
        start_date = add_month(this_month, -1)
        end_date = this_month
    elif period == "same_period_last_year":
        current_month_start = local_date.replace(day=1)
        days_elapsed = (local_date - current_month_start).days + 1
        start_date = safe_replace_year(current_month_start, current_month_start.year - 1)
        end_date = start_date + timedelta(days=days_elapsed)
    else:
        raise ValidationError({"period": "Choose today, this_week, this_month, previous_month, or same_period_last_year."})
    return timezone.make_aware(datetime.combine(start_date, time.min), tz), timezone.make_aware(datetime.combine(end_date, time.min), tz)


def add_month(value, offset: int = 1):
    month_index = value.month - 1 + offset
    year = value.year + month_index // 12
    month = month_index % 12 + 1
    return value.replace(year=year, month=month, day=1)


def safe_replace_year(value, year: int):
    try:
        return value.replace(year=year)
    except ValueError:
        return value.replace(year=year, day=28)
