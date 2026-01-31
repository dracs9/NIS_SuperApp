from django.contrib import admin, messages
from django.contrib.auth import get_user_model
from django.shortcuts import redirect, render
from django.urls import path, reverse
from django.utils.html import format_html

from .models import PointTransaction, Shanyraq, ShanyraqMembership, SourceType
from .services.points import add_points, recalculate_shanyraq_total, revoke_points

User = get_user_model()


@admin.register(Shanyraq)
class ShanyraqAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "total_points", "member_count")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("total_points",)

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


@admin.register(PointTransaction)
class PointTransactionAdmin(admin.ModelAdmin):
    list_display = ("created_at", "user", "shanyraq", "amount_display", "reason", "source_type", "approved_by")
    list_filter = ("source_type", "shanyraq", "created_at")
    search_fields = ("user__email", "reason")
    raw_id_fields = ("user", "approved_by")
    autocomplete_fields = ("shanyraq",)
    readonly_fields = ("created_at",)
    date_hierarchy = "created_at"
    change_list_template = "admin/shanyraq/pointtransaction_changelist.html"

    def amount_display(self, obj):
        if obj.amount >= 0:
            return format_html('<span style="color: green;">+{}</span>', obj.amount)
        return format_html('<span style="color: red;">{}</span>', obj.amount)

    amount_display.short_description = "Amount"

    def has_add_permission(self, request):
        return False  # Use "Issue / Revoke points" custom view instead

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path("issue/", self.admin_site.admin_view(self.issue_points_view), name="shanyraq_pointtransaction_issue"),
            path("revoke/", self.admin_site.admin_view(self.revoke_points_view), name="shanyraq_pointtransaction_revoke"),
        ]
        return custom + urls

    def issue_points_view(self, request):
        if request.method == "POST":
            user_id = request.POST.get("user")
            shanyraq_id = request.POST.get("shanyraq")
            amount = request.POST.get("amount")
            reason = request.POST.get("reason", "").strip()
            source_type = request.POST.get("source_type", SourceType.ADMIN)
            if not all([user_id, shanyraq_id, amount]):
                messages.error(request, "User, Shanyraq and Amount are required.")
            else:
                try:
                    user = User.objects.get(pk=user_id)
                    shanyraq = Shanyraq.objects.get(pk=shanyraq_id)
                    amount_int = int(amount)
                    if amount_int <= 0:
                        messages.error(request, "Amount must be positive for issue.")
                    else:
                        add_points(
                            user=user,
                            shanyraq=shanyraq,
                            amount=amount_int,
                            reason=reason or "Manual issue (admin)",
                            source_type=source_type,
                            approved_by=request.user,
                        )
                        messages.success(request, f"Added {amount_int} points to {user.email} in {shanyraq.name}.")
                        return redirect(reverse("admin:shanyraq_pointtransaction_changelist"))
                except (User.DoesNotExist, Shanyraq.DoesNotExist, ValueError) as e:
                    messages.error(request, str(e))
        users = User.objects.filter(is_active=True).order_by("email")[:500]
        shanyraqs = Shanyraq.objects.all().order_by("name")
        return render(
            request,
            "admin/shanyraq/issue_points.html",
            {
                "title": "Issue points",
                "users": users,
                "shanyraqs": shanyraqs,
                "source_types": SourceType.choices,
                "opts": self.model._meta,
            },
        )

    def revoke_points_view(self, request):
        if request.method == "POST":
            user_id = request.POST.get("user")
            shanyraq_id = request.POST.get("shanyraq")
            amount = request.POST.get("amount")
            reason = request.POST.get("reason", "").strip()
            if not all([user_id, shanyraq_id, amount]):
                messages.error(request, "User, Shanyraq and Amount are required.")
            else:
                try:
                    user = User.objects.get(pk=user_id)
                    shanyraq = Shanyraq.objects.get(pk=shanyraq_id)
                    amount_int = int(amount)
                    if amount_int <= 0:
                        messages.error(request, "Amount must be positive for revoke (will be subtracted).")
                    else:
                        revoke_points(
                            user=user,
                            shanyraq=shanyraq,
                            amount=amount_int,
                            reason=reason or "Manual revoke (admin)",
                            approved_by=request.user,
                        )
                        messages.success(request, f"Revoked {amount_int} points from {user.email} in {shanyraq.name}.")
                        return redirect(reverse("admin:shanyraq_pointtransaction_changelist"))
                except (User.DoesNotExist, Shanyraq.DoesNotExist, ValueError) as e:
                    messages.error(request, str(e))
        users = User.objects.filter(is_active=True).order_by("email")[:500]
        shanyraqs = Shanyraq.objects.all().order_by("name")
        return render(
            request,
            "admin/shanyraq/revoke_points.html",
            {
                "title": "Revoke points",
                "users": users,
                "shanyraqs": shanyraqs,
                "opts": self.model._meta,
            },
        )
