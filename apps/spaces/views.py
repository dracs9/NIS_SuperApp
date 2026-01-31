"""
Spaces app: list, calendar, booking, approval views.
"""
from datetime import datetime, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods, require_safe

from apps.accounts.decorators import teacher_required

from .forms import BookingApproveRejectForm, BookingRequestForm
from .models import BookingStatus, Space, SpaceBooking
from .services import (
    approve_booking,
    cancel_booking,
    check_booking_conflicts,
    create_booking,
    reject_booking,
    suggest_available_slots,
)


@require_safe
def space_list_view(request):
    """List all active spaces."""
    spaces = Space.objects.filter(is_active=True).order_by("space_type", "name")
    return render(
        request,
        "spaces/space_list.html",
        {
            "section_name": "Spaces",
            "spaces": spaces,
        },
    )


@require_safe
def space_detail_view(request, pk):
    """Space detail with weekly calendar view."""
    space = get_object_or_404(Space.objects.filter(is_active=True), pk=pk)
    
    # Get week parameter (default: current week)
    week_offset = int(request.GET.get("week", 0))
    today = timezone.now().date()
    # Start from Monday of the current week
    start_of_week = today - timedelta(days=today.weekday()) + timedelta(weeks=week_offset)
    
    # Generate 7 days
    days = []
    for i in range(7):
        day_date = start_of_week + timedelta(days=i)
        days.append({
            "date": day_date,
            "day_name": day_date.strftime("%A"),
            "is_today": day_date == today,
        })
    
    # Get bookings for this week
    week_start = timezone.make_aware(datetime.combine(start_of_week, datetime.min.time()))
    week_end = week_start + timedelta(days=7)
    bookings = space.bookings.filter(
        status__in=(BookingStatus.APPROVED, BookingStatus.PENDING),
        start_time__lt=week_end,
        end_time__gt=week_start,
    ).select_related("booked_by").order_by("start_time")
    
    # Organize bookings by day and attach to day dict
    bookings_by_day = {day["date"]: [] for day in days}
    for booking in bookings:
        booking_date = booking.start_time.date()
        if booking_date in bookings_by_day:
            bookings_by_day[booking_date].append(booking)
    
    # Attach bookings to each day
    for day in days:
        day["bookings"] = bookings_by_day.get(day["date"], [])
    
    return render(
        request,
        "spaces/space_detail.html",
        {
            "section_name": "Spaces",
            "space": space,
            "days": days,
            "week_offset": week_offset,
            "prev_week": week_offset - 1,
            "next_week": week_offset + 1,
        },
    )


@login_required
@require_http_methods(["GET", "POST"])
def booking_create_view(request, space_id=None):
    """Create a new booking request."""
    if request.method == "POST":
        form = BookingRequestForm(request.POST, space_id=space_id)
        if form.is_valid():
            space = form.cleaned_data["space"]
            start = form.cleaned_data["start_time"]
            end = form.cleaned_data["end_time"]
            
            # Make timezone-aware if naive
            if timezone.is_naive(start):
                start = timezone.make_aware(start)
            if timezone.is_naive(end):
                end = timezone.make_aware(end)
            
            booking, error = create_booking(
                space=space,
                booked_by=request.user,
                start_time=start,
                end_time=end,
                purpose=form.cleaned_data.get("purpose", ""),
                attendees_count=form.cleaned_data.get("attendees_count", 1),
            )
            if booking:
                messages.success(request, f"Booking request created for {space.name}. Awaiting approval.")
                return redirect("spaces:booking_detail", pk=booking.pk)
            else:
                messages.error(request, error or "Could not create booking.")
    else:
        # Pre-fill with suggested slot if date provided
        date_str = request.GET.get("date")
        initial = {}
        if space_id:
            initial["space"] = space_id
        if date_str and space_id:
            try:
                date = datetime.strptime(date_str, "%Y-%m-%d").date()
                space = Space.objects.get(pk=space_id, is_active=True)
                slots = suggest_available_slots(space, date, duration_hours=1, max_suggestions=1)
                if slots:
                    initial["start_time"] = slots[0]["start"]
                    initial["end_time"] = slots[0]["end"]
            except (ValueError, Space.DoesNotExist):
                pass
        form = BookingRequestForm(initial=initial, space_id=space_id)
    
    return render(
        request,
        "spaces/booking_create.html",
        {
            "section_name": "Spaces",
            "form": form,
        },
    )


@login_required
@require_safe
def booking_detail_view(request, pk):
    """Booking detail with status and actions."""
    booking = get_object_or_404(SpaceBooking.objects.select_related("space", "booked_by", "reviewed_by"), pk=pk)
    logs = booking.approval_logs.select_related("changed_by").order_by("-created_at")[:20]  # type: ignore[union-attr]
    
    # Check for conflicts (for pending bookings)
    conflicts = []
    if booking.status == BookingStatus.PENDING:
        conflicts = check_booking_conflicts(booking.space, booking.start_time, booking.end_time, booking.pk)
    
    return render(
        request,
        "spaces/booking_detail.html",
        {
            "section_name": "Spaces",
            "booking": booking,
            "approval_logs": logs,
            "conflicts": conflicts,
            "can_cancel": booking.can_cancel(request.user),
            "can_approve_or_reject": booking.can_approve_or_reject(request.user),
        },
    )


@login_required
@require_http_methods(["POST"])
def booking_cancel_view(request, pk):
    """Cancel a booking."""
    booking = get_object_or_404(SpaceBooking, pk=pk)
    if not booking.can_cancel(request.user):
        return HttpResponseForbidden()
    
    reason = request.POST.get("reason", "")
    ok, err = cancel_booking(booking, request.user, reason)
    if ok:
        messages.success(request, "Booking cancelled.")
    else:
        messages.error(request, err or "Could not cancel booking.")
    return redirect("spaces:booking_detail", pk=pk)


@teacher_required
@require_http_methods(["GET", "POST"])
def booking_review_view(request, pk):
    """Admin/Teacher review panel: approve or reject."""
    booking = get_object_or_404(SpaceBooking.objects.select_related("space", "booked_by"), pk=pk)
    if booking.status != BookingStatus.PENDING:
        messages.info(request, "This booking is not pending review.")
        return redirect("spaces:booking_detail", pk=pk)
    
    logs = booking.approval_logs.select_related("changed_by").order_by("-created_at")  # type: ignore[union-attr]
    conflicts = check_booking_conflicts(booking.space, booking.start_time, booking.end_time, booking.pk)
    
    if request.method == "POST":
        form = BookingApproveRejectForm(request.POST)
        if form.is_valid():
            action = form.cleaned_data["action"]
            comment = (form.cleaned_data.get("comment") or "").strip()
            if action == "approve":
                ok, err = approve_booking(booking, request.user, comment)
                if ok:
                    messages.success(request, "Booking approved.")
                    return redirect("spaces:booking_detail", pk=pk)
                messages.error(request, err or "Could not approve.")
            else:
                ok, err = reject_booking(booking, request.user, comment)
                if ok:
                    messages.success(request, "Booking rejected.")
                    return redirect("spaces:booking_detail", pk=pk)
                messages.error(request, err or "Could not reject.")
        else:
            messages.error(request, "Please fix the form errors.")
    else:
        form = BookingApproveRejectForm(initial={"action": "approve"})
    
    return render(
        request,
        "spaces/booking_review.html",
        {
            "section_name": "Spaces",
            "booking": booking,
            "form": form,
            "approval_logs": logs,
            "conflicts": conflicts,
        },
    )


@teacher_required
@require_safe
def booking_review_list_view(request):
    """List of bookings pending review (Admin/Teacher)."""
    pending = SpaceBooking.objects.filter(status=BookingStatus.PENDING).select_related("space", "booked_by").order_by("start_time")
    return render(
        request,
        "spaces/booking_review_list.html",
        {
            "section_name": "Spaces",
            "pending_bookings": pending,
        },
    )


@login_required
@require_safe
def my_bookings_view(request):
    """User's own bookings."""
    bookings = SpaceBooking.objects.filter(booked_by=request.user).select_related("space").order_by("-start_time")[:50]
    return render(
        request,
        "spaces/my_bookings.html",
        {
            "section_name": "Spaces",
            "bookings": bookings,
        },
    )
