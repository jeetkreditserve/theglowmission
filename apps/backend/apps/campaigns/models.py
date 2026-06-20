from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.text import slugify

from apps.common.models import TimeStampedModel


class CampaignForm(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
        ARCHIVED = "archived", "Archived"

    title = models.CharField(max_length=180)
    slug = models.SlugField(unique=True, blank=True)
    status = models.CharField(max_length=24, choices=Status.choices, default=Status.DRAFT)
    summary = models.CharField(max_length=280, blank=True)
    offer_label = models.CharField(max_length=140, blank=True)
    hero_image = models.ImageField(upload_to="campaigns/", blank=True, null=True)
    hero_image_alt = models.CharField(max_length=220, blank=True)
    button_label = models.CharField(max_length=120, default="Submit request")
    submitting_label = models.CharField(max_length=120, default="Sending...")
    empty_select_label = models.CharField(max_length=120, default="Select one")
    checkbox_label = models.CharField(max_length=120, default="Yes")
    error_message = models.TextField(default="Please check the highlighted fields and try again.")
    schedule_enabled = models.BooleanField(default=False)
    starts_at = models.DateTimeField(blank=True, null=True)
    ends_at = models.DateTimeField(blank=True, null=True)
    success_message = models.TextField(default="Thank you. We will get back to you soon.")
    redirect_url = models.CharField(max_length=240, blank=True)
    seo_title = models.CharField(max_length=180, blank=True)
    seo_description = models.TextField(blank=True)

    class Meta:
        ordering = ["-updated_at"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    @property
    def is_active_now(self) -> bool:
        now = timezone.now()
        if self.status != self.Status.PUBLISHED:
            return False
        if not self.schedule_enabled:
            return True
        if self.starts_at and self.starts_at > now:
            return False
        if self.ends_at and self.ends_at < now:
            return False
        return True

    def __str__(self) -> str:
        return self.title


class CampaignFormField(TimeStampedModel):
    class FieldType(models.TextChoices):
        TEXT = "text", "Text"
        TEXTAREA = "textarea", "Textarea"
        EMAIL = "email", "Email"
        PHONE = "phone", "Phone"
        SELECT = "select", "Select"
        CHECKBOX = "checkbox", "Checkbox"
        RADIO = "radio", "Radio"
        DATE = "date", "Date"
        NUMBER = "number", "Number"

    form = models.ForeignKey(CampaignForm, related_name="fields", on_delete=models.CASCADE)
    label = models.CharField(max_length=180)
    key = models.SlugField(max_length=120, blank=True)
    field_type = models.CharField(max_length=32, choices=FieldType.choices, default=FieldType.TEXT)
    placeholder = models.CharField(max_length=180, blank=True)
    help_text = models.CharField(max_length=260, blank=True)
    required = models.BooleanField(default=False)
    options = models.JSONField(default=list, blank=True)
    validation = models.JSONField(default=dict, blank=True)
    ordering = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["ordering", "id"]
        unique_together = [("form", "key")]

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = slugify(self.label).replace("-", "_")
        if self.pk:
            original = CampaignFormField.objects.get(pk=self.pk)
            if original.key != self.key and self.form.responses.exists():
                raise ValidationError("Field key cannot be changed after responses exist.")
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.form.slug}.{self.key}"


class CampaignFormResponse(TimeStampedModel):
    form = models.ForeignKey(CampaignForm, related_name="responses", on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)
    response_data = models.JSONField(default=dict)
    metadata = models.JSONField(default=dict, blank=True)
    field_snapshot = models.JSONField(default=list)

    class Meta:
        ordering = ["-submitted_at"]

    def __str__(self) -> str:
        return f"{self.form.slug} response {self.pk}"
