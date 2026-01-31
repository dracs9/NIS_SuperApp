"""
Booking workflow: conflict detection, approval, smart slot suggestions.
"""
from datetime import datetime, timedelta

from django.db.models import Q
from django.utils import timezone

from .models import BookingApprovalLog, BookingStatus, Space, SpaceBooking


def check_booking_conflicts(space, start_time, end_time, exclude_booking_id=None):
    """Return conflicting bookings for the given time range."""
    conflicts = SpaceBooking.objects.filter(
        space=space,
        status__in=(BookingStatus.PENDING, BookingStatus.APPROVED),
        start_time__lt=end_time,
        end_time__gt=start_time,
    ).select_related("booked_by")
    if exclude_booking_id:
        conflicts = conflicts.exclude(pk=exclude_booking_id)
    return list(conflicts)


def suggest_available_slots(space, date, duration_hours=1, max_suggestions=5):
    """Suggest available time slots for a given date and duration."""
    # Define working hours: 8 AM to 6 PM
    start_hour = 8
    end_hour = 18
    slots = []
    
    current_time = timezone.make_aware(datetime.combine(date, datetime.min.time()).replace(hour=start_hour))
    end_of_day = timezone.make_aware(datetime.combine(date, datetime.min.time()).replace(hour=end_hour))
    duration = timedelta(hours=duration_hours)
    
    while current_time + duration <= end_of_day and len(slots) < max_suggestions:
        slot_end = current_time + duration
        if not check_booking_conflicts(space, current_time, slot_end):
            slots.append({
                "start": current_time,
                "end": slot_end,
                "available": True,
            })
        current_time += timedelta(hours=1)  # Check every hour
    
    return slots


def create_booking(space, booked_by, start_time, end_time, purpose="", attendees_count=1):
    """Create a new booking request (status: Pending)."""
    conflicts = check_booking_conflicts(space, start_time, end_time)
    if conflicts:
        return None, f"Time slot conflicts with {len(conflicts)} existing booking(s)."
    
    booking = SpaceBooking.objects.create(
        space=space,
        booked_by=booked_by,
        start_time=start_time,
        end_time=end_time,
        purpose=purpose,
        attendees_count=attendees_count,
        status=BookingStatus.PENDING,
    )
    BookingApprovalLog.objects.create(
        booking=booking,
        from_status="",
        to_status=BookingStatus.PENDING,
        changed_by=booked_by,
        comment="Booking created",
    )
    return booking, None


def approve_booking(booking, user, comment=""):
    """Approve a pending booking."""
    if booking.status != BookingStatus.PENDING:
        return False, "Booking is not pending."
    if getattr(user, "role", None) not in ("admin", "teacher"):
        return False, "Only Admin or Teacher can approve."
    
    # Double-check for conflicts
    conflicts = check_booking_conflicts(booking.space, booking.start_time, booking.end_time, booking.pk)
    if conflicts:
        return False, f"Time slot now conflicts with {len(conflicts)} approved booking(s)."
    
    old_status = booking.status
    booking.status = BookingStatus.APPROVED
    booking.reviewed_by = user
    booking.reviewed_at = timezone.now()
    booking.save(update_fields=["status", "reviewed_by", "reviewed_at", "updated_at"])
    
    BookingApprovalLog.objects.create(
        booking=booking,
        from_status=old_status,
        to_status=BookingStatus.APPROVED,
        changed_by=user,
        comment=comment or "Approved",
    )
    return True, None


def reject_booking(booking, user, reason):
    """Reject a pending booking."""
    if booking.status != BookingStatus.PENDING:
        return False, "Booking is not pending."
    if getattr(user, "role", None) not in ("admin", "teacher"):
        return False, "Only Admin or Teacher can reject."
    if not (reason or "").strip():
        return False, "Rejection reason is required."
    
    old_status = booking.status
    booking.status = BookingStatus.REJECTED
    booking.rejection_reason = reason.strip()
    booking.reviewed_by = user
    booking.reviewed_at = timezone.now()
    booking.save(update_fields=["status", "rejection_reason", "reviewed_by", "reviewed_at", "updated_at"])
    
    BookingApprovalLog.objects.create(
        booking=booking,
        from_status=old_status,
        to_status=BookingStatus.REJECTED,
        changed_by=user,
        comment=reason.strip(),
    )
    return True, None


def cancel_booking(booking, user, reason=""):
    """Cancel a pending or approved booking."""
    if booking.status not in (BookingStatus.PENDING, BookingStatus.APPROVED):
        return False, "Booking cannot be cancelled."
    if not booking.can_cancel(user):
        return False, "You cannot cancel this booking."
    
    old_status = booking.status
    booking.status = BookingStatus.CANCELLED
    booking.save(update_fields=["status", "updated_at"])
    
    BookingApprovalLog.objects.create(
        booking=booking,
        from_status=old_status,
        to_status=BookingStatus.CANCELLED,
        changed_by=user,
        comment=reason or "Cancelled by user",
    )
    return True, None
