from django.contrib import admin, messages
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Q
from django.shortcuts import redirect, render
from django.urls import path, reverse
from django.utils import timezone
from django.utils.html import format_html

from .models import ActionType, ModeratorActionLog


@admin.register(ModeratorActionLog)
class ModeratorActionLogAdmin(admin.ModelAdmin):
    list_display = ["moderator", "action_type", "target_model", "target_id", "created_at"]
    list_filter = ["action_type", "target_model", "created_at", "moderator"]
    search_fields = ["description", "comment", "moderator__email"]
    readonly_fields = [
        "moderator",
        "action_type",
        "target_model",
        "target_id",
        "description",
        "old_value",
        "new_value",
        "comment",
        "created_at",
    ]
    date_hierarchy = "created_at"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class ModerationDashboardAdmin(admin.AdminSite):
    site_header = "NIS SuperApp Moderation"
    site_title = "NIS Moderation"
    index_title = "Moderation Dashboard"

    def index(self, request, extra_context=None):
        """Redirect to dashboard instead of showing default admin index."""
        from django.shortcuts import redirect

        return redirect("/moderation/dashboard/")

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("dashboard/", self.admin_view(self.dashboard_view), name="moderation_dashboard"),
            path(
                "approve-event/<int:event_id>/",
                self.admin_view(self.approve_event_view),
                name="approve_event",
            ),
            path(
                "reject-event/<int:event_id>/",
                self.admin_view(self.reject_event_view),
                name="reject_event",
            ),
            path(
                "approve-booking/<int:booking_id>/",
                self.admin_view(self.approve_booking_view),
                name="approve_booking",
            ),
            path(
                "reject-booking/<int:booking_id>/",
                self.admin_view(self.reject_booking_view),
                name="reject_booking",
            ),
        ]
        return custom_urls + urls

    def each_context(self, request):
        """Add main admin URLs to the context so templates can access them."""
        context = super().each_context(request)
        # Add a way to access main admin URLs
        from django.urls import reverse

        try:
            context["main_admin_pointtransaction_url"] = reverse(
                "admin:shanyraq_pointtransaction_changelist"
            )
        except:
            context["main_admin_pointtransaction_url"] = "/admin/shanyraq/pointtransaction/"
        try:
            context["main_admin_user_url"] = reverse("admin:accounts_user_changelist")
        except:
            context["main_admin_user_url"] = "/admin/accounts/user/"
        try:
            context["main_admin_shanyraq_url"] = reverse("admin:shanyraq_shanyraq_changelist")
        except:
            context["main_admin_shanyraq_url"] = "/admin/shanyraq/shanyraq/"
        return context

    def dashboard_view(self, request):
        # Check permissions
        if not request.user.is_staff and not getattr(request.user, "is_moderator", False):
            from django.http import HttpResponseForbidden

            return HttpResponseForbidden("Access denied. Moderator privileges required.")

        from apps.accounts.models import User
        from apps.events.models import Event, EventStatus
        from apps.shanyraq.models import Shanyraq
        from apps.spaces.models import BookingStatus, SpaceBooking

        # Get pending items
        pending_events = (
            Event.objects.filter(status=EventStatus.PENDING)
            .select_related("created_by")
            .order_by("created_at")
        )
        pending_bookings = (
            SpaceBooking.objects.filter(status=BookingStatus.PENDING)
            .select_related("space", "booked_by")
            .order_by("start_time")
        )

        # Recent actions
        recent_actions = ModeratorActionLog.objects.select_related("moderator").order_by(
            "-created_at"
        )[:10]

        # Stats
        stats = {
            "pending_events_count": pending_events.count(),
            "pending_bookings_count": pending_bookings.count(),
            "total_users": User.objects.count(),
            "total_shanyraqs": Shanyraq.objects.count(),
            "actions_today": ModeratorActionLog.objects.filter(
                created_at__date=timezone.now().date()
            ).count(),
        }

        context = {
            "pending_events": pending_events,
            "pending_bookings": pending_bookings,
            "recent_actions": recent_actions,
            "stats": stats,
            "title": "Moderation Dashboard",
        }
        return render(request, "admin/moderation/dashboard.html", context)

    def approve_event_view(self, request, event_id):
        # Check permissions
        if not request.user.is_staff and not getattr(request.user, "is_moderator", False):
            from django.http import HttpResponseForbidden

            return HttpResponseForbidden("Access denied. Moderator privileges required.")

        from apps.events.models import Event, EventApprovalLog, EventStatus

        try:
            event = Event.objects.get(pk=event_id, status=EventStatus.PENDING)
            old_status = event.status
            event.status = EventStatus.APPROVED
            event.save()

            # Log approval
            EventApprovalLog.objects.create(
                event=event,
                from_status=old_status,
                to_status=event.status,
                changed_by=request.user,
                comment=request.POST.get("comment", ""),
            )

            # Log moderator action
            ModeratorActionLog.objects.create(
                moderator=request.user,
                action_type=ActionType.APPROVE_EVENT,
                target_model="events.Event",
                target_id=event_id,
                description=f"Approved event: {event.title}",
                old_value=f'{{"status": "{old_status}"}}',
                new_value=f'{{"status": "{event.status}"}}',
                comment=request.POST.get("comment", ""),
            )

            messages.success(request, f'Event "{event.title}" has been approved.')
        except Event.DoesNotExist:
            messages.error(request, "Event not found or not pending.")

        return redirect("/moderation/dashboard/")

    def reject_event_view(self, request, event_id):
        # Check permissions
        if not request.user.is_staff and not getattr(request.user, "is_moderator", False):
            from django.http import HttpResponseForbidden

            return HttpResponseForbidden("Access denied. Moderator privileges required.")

        from apps.events.models import Event, EventApprovalLog, EventStatus

        if request.method == "POST":
            try:
                event = Event.objects.get(pk=event_id, status=EventStatus.PENDING)
                old_status = event.status
                event.status = EventStatus.REJECTED
                event.rejection_comment = request.POST.get("comment", "")
                event.save()

                # Log rejection
                EventApprovalLog.objects.create(
                    event=event,
                    from_status=old_status,
                    to_status=event.status,
                    changed_by=request.user,
                    comment=request.POST.get("comment", ""),
                )

                # Log moderator action
                ModeratorActionLog.objects.create(
                    moderator=request.user,
                    action_type=ActionType.REJECT_EVENT,
                    target_model="events.Event",
                    target_id=event_id,
                    description=f"Rejected event: {event.title}",
                    old_value=f'{{"status": "{old_status}"}}',
                    new_value=f'{{"status": "{event.status}"}}',
                    comment=request.POST.get("comment", ""),
                )

                messages.success(request, f'Event "{event.title}" has been rejected.')
            except Event.DoesNotExist:
                messages.error(request, "Event not found or not pending.")

        return redirect("/moderation/dashboard/")

    def approve_booking_view(self, request, booking_id):
        # Check permissions
        if not request.user.is_staff and not getattr(request.user, "is_moderator", False):
            from django.http import HttpResponseForbidden

            return HttpResponseForbidden("Access denied. Moderator privileges required.")

        from apps.spaces.models import BookingApprovalLog, BookingStatus, SpaceBooking

        try:
            booking = SpaceBooking.objects.get(pk=booking_id, status=BookingStatus.PENDING)
            old_status = booking.status
            booking.status = BookingStatus.APPROVED
            booking.reviewed_by = request.user
            booking.reviewed_at = timezone.now()
            booking.save()

            # Log approval
            BookingApprovalLog.objects.create(
                booking=booking,
                from_status=old_status,
                to_status=booking.status,
                changed_by=request.user,
                comment=request.POST.get("comment", ""),
            )

            # Log moderator action
            ModeratorActionLog.objects.create(
                moderator=request.user,
                action_type=ActionType.APPROVE_BOOKING,
                target_model="spaces.SpaceBooking",
                target_id=booking_id,
                description=f"Approved booking: {booking}",
                old_value=f'{{"status": "{old_status}"}}',
                new_value=f'{{"status": "{booking.status}"}}',
                comment=request.POST.get("comment", ""),
            )

            messages.success(request, f'Booking "{booking}" has been approved.')
        except SpaceBooking.DoesNotExist:
            messages.error(request, "Booking not found or not pending.")

        return redirect("/moderation/dashboard/")

    def reject_booking_view(self, request, booking_id):
        # Check permissions
        if not request.user.is_staff and not getattr(request.user, "is_moderator", False):
            from django.http import HttpResponseForbidden

            return HttpResponseForbidden("Access denied. Moderator privileges required.")

        from apps.spaces.models import BookingApprovalLog, BookingStatus, SpaceBooking

        if request.method == "POST":
            try:
                booking = SpaceBooking.objects.get(pk=booking_id, status=BookingStatus.PENDING)
                old_status = booking.status
                booking.status = BookingStatus.REJECTED
                booking.reviewed_by = request.user
                booking.reviewed_at = timezone.now()
                booking.rejection_reason = request.POST.get("comment", "")
                booking.save()

                # Log rejection
                BookingApprovalLog.objects.create(
                    booking=booking,
                    from_status=old_status,
                    to_status=booking.status,
                    changed_by=request.user,
                    comment=request.POST.get("comment", ""),
                )

                # Log moderator action
                ModeratorActionLog.objects.create(
                    moderator=request.user,
                    action_type=ActionType.REJECT_BOOKING,
                    target_model="spaces.SpaceBooking",
                    target_id=booking_id,
                    description=f"Rejected booking: {booking}",
                    old_value=f'{{"status": "{old_status}"}}',
                    new_value=f'{{"status": "{booking.status}"}}',
                    comment=request.POST.get("comment", ""),
                )

                messages.success(request, f'Booking "{booking}" has been rejected.')
            except SpaceBooking.DoesNotExist:
                messages.error(request, "Booking not found or not pending.")

        return redirect("/moderation/dashboard/")


# Create the moderation admin site
moderation_admin = ModerationDashboardAdmin(name="moderation_admin")

# Register models with the moderation admin
moderation_admin.register(ModeratorActionLog, ModeratorActionLogAdmin)
