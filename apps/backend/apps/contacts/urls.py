from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.contacts.views import ContactHistoryEntryViewSet, ContactNoteViewSet, ContactStatusViewSet, ContactViewSet


router = DefaultRouter()
router.register("admin/contact-statuses", ContactStatusViewSet, basename="admin-contact-statuses")
router.register("admin/contacts", ContactViewSet, basename="admin-contacts")
router.register("admin/contact-notes", ContactNoteViewSet, basename="admin-contact-notes")
router.register("admin/contact-history", ContactHistoryEntryViewSet, basename="admin-contact-history")

urlpatterns = [
    path("", include(router.urls)),
]
