"""
Spaces app: room/space booking with calendar and approval workflow.
Status flow: Pending -> Approved -> Rejected / Cancelled
"""
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils import timezone


class SpaceType(models.TextChoices):
    CLASSROOM = "classroom", "Classroom"
    AUDITORIUM = "auditorium", "Auditorium"
    LAB = "lab", "Lab"
    CONFERENCE = "conference", "Conference Room"
    SPORTS = "sports", "Sports Facility"
    OTHER = "other", "Other"


class Space(models.Model):
    """Physical space/room that can be booked."""
    name = models.CharField(max_length=255)
    space_type = models.CharField(
        max_length=20,
        choices=SpaceType.choices,
        default=SpaceType.OTHER,
    )
    capacity = models.PositiveIntegerField(default=0, help_text="Maximum number of people")
    description = models.TextField(blank=True)
    location = models.CharField(max_length=255, blank=True, help_text="Building/floor/room number")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "space"
        verbose_name_plural = "spaces"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.get_space_type_display()})"

    def get_bookings_for_week(self, start_date):
        """Get all approved bookings for a given week starting from start_date."""
        from datetime import timedelta
        end_date = start_date + timedelta(days=7)
        return self.bookings.filter(
            status=BookingStatus.APPROVED,
            start_time__lt=end_date,
            end_time__gt=start_date,
        ).select_related("booked_by").order_by("start_time")

    def is_available(self, start_time, end_time, exclude_booking_id=None):
        """Check if space is available for the given time range."""
        conflicts = self.bookings.filter(
            status__in=(BookingStatus.PENDING, BookingStatus.APPROVED),
            start_time__lt=end_time,
            end_time__gt=start_time,
        )
        if exclude_booking_id:
            conflicts = conflicts.exclude(pk=exclude_booking_id)
        return not conflicts.exists()


class BookingStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"
    CANCELLED = "cancelled", "Cancelled"


class SpaceBooking(models.Model):
    """Booking request for a space with approval workflow."""
    space = models.ForeignKey(
        Space,
        on_delete=models.CASCADE,
        related_name="bookings",
    )
    booked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="space_bookings",
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    purpose = models.TextField(blank=True, help_text="Purpose of booking")
    attendees_count = models.PositiveIntegerField(default=1, help_text="Expected number of attendees")
    status = models.CharField(
        max_length=20,
        choices=BookingStatus.choices,
        default=BookingStatus.PENDING,
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_bookings",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "space booking"
        verbose_name_plural = "space bookings"
        ordering = ["-start_time"]
        indexes = [
            models.Index(fields=["space", "start_time", "end_time"]),
            models.Index(fields=["status", "start_time"]),
        ]

    def __str__(self):
        return f"{self.space.name}: {self.start_time.strftime('%Y-%m-%d %H:%M')} - {self.end_time.strftime('%H:%M')}"

    def clean(self):
        super().clean()
        if self.start_time and self.end_time:
            if self.end_time <= self.start_time:
                raise ValidationError({"end_time": "End time must be after start time."})
            if self.start_time < timezone.now():
                raise ValidationError({"start_time": "Cannot book in the past."})
        if self.attendees_count and self.space and self.attendees_count > self.space.capacity:
            raise ValidationError({"attendees_count": f"Exceeds space capacity ({self.space.capacity})."})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def is_pending(self):
        return self.status == BookingStatus.PENDING

    @property
    def is_approved(self):
        return self.status == BookingStatus.APPROVED

    @property
    def is_rejected(self):
        return self.status == BookingStatus.REJECTED

    @property
    def is_cancelled(self):
        return self.status == BookingStatus.CANCELLED

    def can_cancel(self, user):
        """Booked user or staff can cancel pending/approved bookings."""
        if not user.is_authenticated:
            return False
        if user.is_staff or getattr(user, "role", None) == "admin":
            return True
        return (
            self.booked_by and self.booked_by.id == user.id
            and self.status in (BookingStatus.PENDING, BookingStatus.APPROVED)
            and self.start_time > timezone.now()
        )

    def can_approve_or_reject(self, user):
        """Admin or Teacher can approve/reject pending bookings."""
        if not user.is_authenticated:
            return False
        return getattr(user, "role", None) in ("admin", "teacher") and self.status == BookingStatus.PENDING


class BookingApprovalLog(models.Model):
    """Status change history for bookings."""
    booking = models.ForeignKey(
        SpaceBooking,
        on_delete=models.CASCADE,
        related_name="approval_logs",
    )
    from_status = models.CharField(max_length=20, choices=BookingStatus.choices)
    to_status = models.CharField(max_length=20, choices=BookingStatus.choices)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="booking_approval_actions",
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "booking approval log"
        verbose_name_plural = "booking approval logs"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.booking.pk}: {self.from_status} → {self.to_status}"
