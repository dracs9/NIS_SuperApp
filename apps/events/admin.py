from django.contrib import admin
from django.utils.html import format_html

from .models import Event, EventApplication, EventApprovalLog, EventPolicy


@admin.register(EventPolicy)
class EventPolicyAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name",)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "status_badge", "start_at", "end_at", "location", "created_by", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("title", "description", "location")
    raw_id_fields = ("created_by", "policy")
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "start_at"

    def status_badge(self, obj):
        colors = {
            "draft": "gray",
            "pending": "orange",
            "approved": "green",
            "rejected": "red",
        }
        c = colors.get(obj.status, "gray")
        return format_html('<span style="color: {};">{}</span>', c, obj.get_status_display())

    status_badge.short_description = "Status"


@admin.register(EventApplication)
class EventApplicationAdmin(admin.ModelAdmin):
    list_display = ("event", "submitted_by", "submitted_at")
    list_filter = ("submitted_at",)
    raw_id_fields = ("event", "submitted_by")


@admin.register(EventApprovalLog)
class EventApprovalLogAdmin(admin.ModelAdmin):
    list_display = ("event", "from_status", "to_status", "changed_by", "created_at")
    list_filter = ("to_status", "created_at")
    raw_id_fields = ("event", "changed_by")
    readonly_fields = ("event", "from_status", "to_status", "changed_by", "comment", "created_at")
