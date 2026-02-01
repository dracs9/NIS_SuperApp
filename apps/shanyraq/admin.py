from django.contrib import admin
from django.contrib.auth import get_user_model
from django.shortcuts import redirect, render
from django.urls import path, reverse
from django.utils.html import format_html

from .models import ActivitySubmission, Shanyraq, ShanyraqMembership, SourceType, XPLedger

User = get_user_model()


@admin.register(Shanyraq)
class ShanyraqAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "season_sp", "lifetime_sp", "member_count")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("season_sp", "lifetime_sp")

    def member_count(self, obj):
        return obj.members.count()

    member_count.short_description = "Members"


@admin.register(ShanyraqMembership)
class ShanyraqMembershipAdmin(admin.ModelAdmin):
    list_display = ("user", "shanyraq", "joined_at", "is_leader")
    list_filter = ("shanyraq", "is_leader")
    search_fields = ("user__email", "shanyraq__name")
    raw_id_fields = ("user",)
    autocomplete_fields = ("shanyraq",)


@admin.register(XPLedger)
class XPLedgerAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "user",
        "delta_xp_display",
        "reason",
        "source_type",
        "approved_by",
    )
    list_filter = ("source_type", "created_at")
    search_fields = ("user__email", "reason")
    raw_id_fields = ("user", "approved_by")
    readonly_fields = ("created_at",)
    date_hierarchy = "created_at"

    def delta_xp_display(self, obj):
        if obj.delta_xp >= 0:
            return format_html('<span style="color: green;">+{}</span>', obj.delta_xp)
        return format_html('<span style="color: red;">{}</span>', obj.delta_xp)

    delta_xp_display.short_description = "XP Change"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("award-xp/", self.admin_site.admin_view(self.award_xp_view), name="award_xp"),
        ]
        return custom_urls + urls

    def award_xp_view(self, request):
        from .services import XPService

        if request.method == "POST":
            user_id = request.POST.get("user")
            delta_xp = request.POST.get("delta_xp")
            reason = request.POST.get("reason", "").strip()
            source_type = request.POST.get("source_type", SourceType.ADMIN)

            if not all([user_id, delta_xp]):
                self.message_user(request, "User and XP amount are required.", level="error")
            else:
                try:
                    user = User.objects.get(pk=user_id)
                    delta_xp_int = int(delta_xp)

                    XPService.award_xp(
                        user=user,
                        delta_xp=delta_xp_int,
                        reason=reason or "Manual XP award (admin)",
                        source_type=source_type,
                        approved_by=request.user,
                    )

                    self.message_user(
                        request, f"Awarded {delta_xp_int:+d} XP to {user.email}.", level="success"
                    )
                    return redirect(reverse("admin:shanyraq_xpledger_changelist"))

                except (User.DoesNotExist, ValueError) as e:
                    self.message_user(request, str(e), level="error")

        users = User.objects.filter(is_active=True).order_by("email")[:500]
        return render(
            request,
            "admin/shanyraq/award_xp.html",
            {
                "title": "Award XP",
                "users": users,
                "source_types": SourceType.choices,
                "opts": self.model._meta,
            },
        )


@admin.register(ActivitySubmission)
class ActivitySubmissionAdmin(admin.ModelAdmin):
    list_display = ("submitted_at", "user", "title", "awards_xp", "status", "reviewed_by")
    list_filter = ("status", "submitted_at", "reviewed_at")
    search_fields = ("user__email", "title", "description")
    raw_id_fields = ("user", "reviewed_by")
    readonly_fields = ("submitted_at", "reviewed_at")
    date_hierarchy = "submitted_at"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user", "reviewed_by")
