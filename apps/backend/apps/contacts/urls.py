from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.contacts.views import ContactNoteViewSet, ContactStatusViewSet, ContactViewSet


router = DefaultRouter()
router.register("admin/contact-statuses", ContactStatusViewSet, basename="admin-contact-statuses")
router.register("admin/contacts", ContactViewSet, basename="admin-contacts")
router.register("admin/contact-notes", ContactNoteViewSet, basename="admin-contact-notes")

urlpatterns = [
    path("", include(router.urls)),
]
