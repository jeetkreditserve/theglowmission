from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.appointments.views import (
    AppointmentAvailabilityWindowViewSet,
    AppointmentBlockViewSet,
    AppointmentFinanceEntryViewSet,
    AppointmentViewSet,
    CustomerAppointmentCancelView,
    CustomerAppointmentListCreateView,
    CustomerAppointmentRescheduleView,
    FounderDashboardView,
    PublicServiceAppointmentView,
    PublicServiceAvailableSlotsView,
)

router = DefaultRouter()
router.register("admin/appointments", AppointmentViewSet, basename="admin-appointments")
router.register("admin/appointment-availability", AppointmentAvailabilityWindowViewSet, basename="admin-appointment-availability")
router.register("admin/appointment-blocks", AppointmentBlockViewSet, basename="admin-appointment-blocks")
router.register("admin/finance-entries", AppointmentFinanceEntryViewSet, basename="admin-finance-entries")

urlpatterns = [
    path("public/services/<slug:slug>/available-slots/", PublicServiceAvailableSlotsView.as_view(), name="public-service-available-slots"),
    path("public/services/<slug:slug>/appointments/", PublicServiceAppointmentView.as_view(), name="public-service-appointments"),
    path("auth/customer/appointments/", CustomerAppointmentListCreateView.as_view(), name="customer-appointments"),
    path("auth/customer/appointments/<int:pk>/cancel/", CustomerAppointmentCancelView.as_view(), name="customer-appointment-cancel"),
    path("auth/customer/appointments/<int:pk>/reschedule/", CustomerAppointmentRescheduleView.as_view(), name="customer-appointment-reschedule"),
    path("admin/dashboard/founder/", FounderDashboardView.as_view(), name="admin-founder-dashboard"),
    *router.urls,
]
