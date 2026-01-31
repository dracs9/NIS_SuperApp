from django.contrib import admin
from django.utils.html import format_html

from .models import BookingApprovalLog, BookingStatus, Space, SpaceBooking


@admin.register(Space)
class SpaceAdmin(admin.ModelAdmin):
    list_display = ("name", "space_type", "capacity", "location", "is_active", "created_at")
    list_filter = ("space_type", "is_active")
    search_fields = ("name", "location", "description")
    readonly_fields = ("created_at", "updated_at")


@admin.register(SpaceBooking)
class SpaceBookingAdmin(admin.ModelAdmin):
    list_display = ("space", "booked_by", "start_time", "end_time", "status_badge", "attendees_count", "created_at")
    list_filter = ("status", "space", "start_time")
    search_fields = ("space__name", "booked_by__email", "purpose")
    raw_id_fields = ("space", "booked_by", "reviewed_by")
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "start_time"

    def status_badge(self, obj):
        colors = {
            "pending": "orange",
            "approved": "green",
            "rejected": "red",
            "cancelled": "gray",
        }
        c = colors.get(obj.status, "gray")
        return format_html('<span style="color: {};">{}</span>', c, obj.get_status_display())

    status_badge.short_description = "Status"


@admin.register(BookingApprovalLog)
class BookingApprovalLogAdmin(admin.ModelAdmin):
    list_display = ("booking", "from_status", "to_status", "changed_by", "created_at")
    list_filter = ("to_status", "created_at")
    raw_id_fields = ("booking", "changed_by")
    readonly_fields = ("booking", "from_status", "to_status", "changed_by", "comment", "created_at")
