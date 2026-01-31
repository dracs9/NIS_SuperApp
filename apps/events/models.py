"""
Events app: school events with approval workflow.
Status flow: Draft -> Pending -> Approved -> Rejected
"""
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class EventStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    PENDING = "pending", "Pending"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"


class EventPolicy(models.Model):
    """Policy template (JSON or text) for event rules."""
    name = models.CharField(max_length=128)
    body = models.TextField(blank=True, help_text="JSON or plain text policy content")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "event policy"
        verbose_name_plural = "event policies"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class Event(models.Model):
    """School event: title, dates, location, status, creator."""
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    location = models.CharField(max_length=255, blank=True)
    status = models.CharField(
        max_length=20,
        choices=EventStatus.choices,
        default=EventStatus.DRAFT,
    )
    policy = models.ForeignKey(
        EventPolicy,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="events",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_events",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    rejection_comment = models.TextField(blank=True, help_text="Set when status is Rejected")

    class Meta:
        verbose_name = "event"
        verbose_name_plural = "events"
        ordering = ["-start_at"]

    def __str__(self):
        return self.title

    def clean(self):
        super().clean()
        if self.start_at and self.end_at and self.end_at <= self.start_at:
            raise ValidationError({"end_at": "End must be after start."})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def is_draft(self):
        return self.status == EventStatus.DRAFT

    @property
    def is_pending(self):
        return self.status == EventStatus.PENDING

    @property
    def is_approved(self):
        return self.status == EventStatus.APPROVED

    @property
    def is_rejected(self):
        return self.status == EventStatus.REJECTED

    def can_edit(self, user):
        """Only creator (or staff) can edit draft."""
        if not user.is_authenticated:
            return False
        if user.is_staff or getattr(user, "role", None) == "admin":
            return True
        return (self.created_by and self.created_by.id == user.id and self.status == EventStatus.DRAFT)

    def can_submit(self, user):
        """Creator can submit for approval when draft."""
        if not user.is_authenticated:
            return False
        return (self.created_by and self.created_by.id == user.id and self.status == EventStatus.DRAFT)

    def can_approve_or_reject(self, user):
        """Admin or Teacher can approve/reject when pending."""
        if not user.is_authenticated:
            return False
        return getattr(user, "role", None) in ("admin", "teacher") and self.status == EventStatus.PENDING


class EventApplication(models.Model):
    """Submission record when event is sent for approval (one per event)."""
    event = models.OneToOneField(
        Event,
        on_delete=models.CASCADE,
        related_name="application",
    )
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="event_submissions",
    )
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "event application"
        verbose_name_plural = "event applications"

    def __str__(self):
        return f"Application for {self.event.title}"


class EventApprovalLog(models.Model):
    """Status change history: who changed status, when, and optional comment."""
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="approval_logs",
    )
    from_status = models.CharField(max_length=20, choices=EventStatus.choices)
    to_status = models.CharField(max_length=20, choices=EventStatus.choices)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="event_approval_actions",
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "event approval log"
        verbose_name_plural = "event approval logs"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.event.pk}: {self.from_status} → {self.to_status}"
