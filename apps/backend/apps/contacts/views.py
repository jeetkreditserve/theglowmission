from __future__ import annotations

from io import BytesIO

from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse
from django.utils import timezone
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from apps.contacts.exports import build_contacts_workbook
from apps.contacts.models import Contact, ContactAuditEvent, ContactNote, ContactStatus
from apps.contacts.serializers import ContactNoteSerializer, ContactSerializer, ContactStatusSerializer, ContactSummarySerializer
from apps.contacts.services import CONTACT_PROFILE_FIELDS, normalize_email, normalize_phone, refresh_contact_response_count


class ContactStatusViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]
    queryset = ContactStatus.objects.prefetch_related("contacts").all()
    serializer_class = ContactStatusSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "slug"]
    ordering_fields = ["ordering", "name", "updated_at"]

    def destroy(self, request, *args, **kwargs):
        status_obj = self.get_object()
        if status_obj.contacts.exists() or status_obj.is_default:
            return Response({"detail": "Choose a replacement status before deleting this status."}, status=400)
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=["post"], url_path="delete-with-replacement")
    def delete_with_replacement(self, request, pk=None):
        status_obj = self.get_object()
        replacement_id = request.data.get("replacement_status")
        if not replacement_id:
            return Response({"replacement_status": "Choose a replacement status."}, status=400)
        if str(replacement_id) == str(status_obj.pk):
            return Response({"replacement_status": "Replacement must be a different status."}, status=400)
        try:
            replacement = ContactStatus.objects.get(pk=replacement_id)
        except ContactStatus.DoesNotExist:
            return Response({"replacement_status": "Replacement status was not found."}, status=404)
        with transaction.atomic():
            contacts = list(status_obj.contacts.all())
            if status_obj.is_default:
                replacement.is_default = True
                replacement.save(update_fields=["is_default", "updated_at"])
            Contact.objects.filter(status=status_obj).update(status=replacement)
            for contact in contacts:
                ContactAuditEvent.objects.create(
                    contact=contact,
                    event_type=ContactAuditEvent.EventType.STATUS_CHANGED,
                    field_name="status",
                    old_value=status_obj.name,
                    new_value=replacement.name,
                    source_type="status_delete",
                    source_id=str(status_obj.pk),
                    actor=request.user,
                    message=f"Status deleted and migrated to {replacement.name}.",
                )
            status_obj.delete()
        return Response({"status": "deleted", "migrated_contacts": len(contacts)})


class ContactViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]
    serializer_class = ContactSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["updated_at", "last_activity_at", "full_name", "email", "phone"]

    def get_serializer_class(self):
        if self.action == "list":
            return ContactSummarySerializer
        return ContactSerializer

    def get_queryset(self):
        queryset = (
            Contact.objects.select_related("status", "merged_into")
            .prefetch_related("notes", "audit_events", "campaign_responses__form")
            .filter(is_merged=False)
        )
        search = self.request.query_params.get("search") or self.request.query_params.get("q")
        if search:
            queryset = queryset.filter(
                Q(full_name__icontains=search)
                | Q(email__icontains=search)
                | Q(phone__icontains=search)
                | Q(address__icontains=search)
                | Q(skin_goal__icontains=search)
            )
        status_id = self.request.query_params.get("status")
        if status_id:
            queryset = queryset.filter(status_id=status_id)
        consent = self.request.query_params.get("marketing_consent")
        if consent in {"true", "false"}:
            queryset = queryset.filter(marketing_consent=consent == "true")
        return queryset

    def perform_create(self, serializer):
        contact = serializer.save()
        ContactAuditEvent.objects.create(
            contact=contact,
            event_type=ContactAuditEvent.EventType.CREATED,
            new_value={field: getattr(contact, field) for field in CONTACT_PROFILE_FIELDS},
            source_type="manual",
            actor=self.request.user,
        )

    def perform_update(self, serializer):
        before = self.snapshot(serializer.instance)
        contact = serializer.save()
        after = self.snapshot(contact)
        for field_name, old_value in before.items():
            new_value = after[field_name]
            if old_value == new_value:
                continue
            event_type = ContactAuditEvent.EventType.UPDATED
            if field_name == "status":
                event_type = ContactAuditEvent.EventType.STATUS_CHANGED
            if field_name == "marketing_consent":
                event_type = ContactAuditEvent.EventType.CONSENT_CHANGED
            ContactAuditEvent.objects.create(
                contact=contact,
                event_type=event_type,
                field_name=field_name,
                old_value=old_value,
                new_value=new_value,
                source_type="manual",
                actor=self.request.user,
            )

    def destroy(self, request, *args, **kwargs):
        return Response({"detail": "Contacts are not deleted. Move the contact to an inactive status instead."}, status=400)

    @action(detail=False, methods=["get"], url_path="export")
    def export(self, request):
        workbook = build_contacts_workbook(self.filter_queryset(self.get_queryset()))
        output = BytesIO()
        workbook.save(output)
        output.seek(0)
        response = HttpResponse(
            output.read(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = 'attachment; filename="contacts.xlsx"'
        return response

    @action(detail=True, methods=["post"])
    def merge(self, request, pk=None):
        target = self.get_object()
        source_id = request.data.get("source_contact")
        if not source_id:
            return Response({"source_contact": "Choose a contact to merge."}, status=400)
        try:
            source = Contact.objects.select_related("status").get(pk=source_id, is_merged=False)
        except Contact.DoesNotExist:
            return Response({"source_contact": "Source contact was not found."}, status=404)
        if source.pk == target.pk:
            return Response({"source_contact": "A contact cannot be merged into itself."}, status=400)

        with transaction.atomic():
            source.mark_merged_into(target)
            changed_fields = merge_contact_values(target, source)
            source.campaign_responses.update(contact=target, contact_sync_status="synced", contact_sync_error="")
            source.notes.update(contact=target)
            source.audit_events.update(contact=target)
            refresh_contact_response_count(target)
            refresh_contact_response_count(source)
            ContactAuditEvent.objects.create(
                contact=target,
                event_type=ContactAuditEvent.EventType.MERGED,
                old_value={"source_contact": source.pk},
                new_value={"target_contact": target.pk, "changed_fields": changed_fields},
                source_type="manual_merge",
                source_id=str(source.pk),
                actor=request.user,
                message=f"Merged contact #{source.pk} into contact #{target.pk}.",
            )
        return Response(ContactSerializer(target, context={"request": request}).data)

    @staticmethod
    def snapshot(contact: Contact):
        data = {field: getattr(contact, field) for field in CONTACT_PROFILE_FIELDS}
        data["status"] = contact.status.name if contact.status else ""
        return data


class ContactNoteViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]
    serializer_class = ContactNoteSerializer

    def get_queryset(self):
        queryset = ContactNote.objects.select_related("contact", "created_by").all()
        contact_id = self.request.query_params.get("contact")
        if contact_id:
            queryset = queryset.filter(contact_id=contact_id)
        return queryset

    def perform_create(self, serializer):
        note = serializer.save(created_by=self.request.user)
        ContactAuditEvent.objects.create(
            contact=note.contact,
            event_type=ContactAuditEvent.EventType.UPDATED,
            field_name="note",
            new_value=note.body,
            source_type="manual_note",
            source_id=str(note.pk),
            actor=self.request.user,
            message="Admin note added.",
        )


def merge_contact_values(target: Contact, source: Contact) -> list[str]:
    changed_fields: list[str] = []
    source_is_newer = source.updated_at and target.updated_at and source.updated_at > target.updated_at
    for field_name in CONTACT_PROFILE_FIELDS:
        source_value = getattr(source, field_name)
        target_value = getattr(target, field_name)
        if field_name == "marketing_consent":
            chosen = source_value if source_is_newer else target_value
        else:
            chosen = source_value if source_is_newer and source_value not in (None, "", []) else target_value
            if chosen in (None, "", []) and source_value not in (None, "", []):
                chosen = source_value
        if chosen != target_value:
            ContactAuditEvent.objects.create(
                contact=target,
                event_type=ContactAuditEvent.EventType.CONSENT_CHANGED if field_name == "marketing_consent" else ContactAuditEvent.EventType.UPDATED,
                field_name=field_name,
                old_value=target_value,
                new_value=chosen,
                source_type="manual_merge",
                source_id=str(source.pk),
            )
            setattr(target, field_name, chosen)
            changed_fields.append(field_name)

    if source.status and (source_is_newer or not target.status):
        old_status = target.status.name if target.status else ""
        target.status = source.status
        ContactAuditEvent.objects.create(
            contact=target,
            event_type=ContactAuditEvent.EventType.STATUS_CHANGED,
            field_name="status",
            old_value=old_status,
            new_value=source.status.name,
            source_type="manual_merge",
            source_id=str(source.pk),
        )
        changed_fields.append("status")

    dates = [value for value in [target.first_activity_at, source.first_activity_at] if value]
    target.first_activity_at = min(dates) if dates else target.first_activity_at
    dates = [value for value in [target.last_activity_at, source.last_activity_at, timezone.now()] if value]
    target.last_activity_at = max(dates) if dates else target.last_activity_at
    target.normalized_email = normalize_email(target.email)
    target.normalized_phone = normalize_phone(target.phone)
    target.save()
    return changed_fields
