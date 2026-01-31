from django.contrib import admin

from .models import Team, TeamMember, TeamRequest


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ("name", "opportunity", "created_by", "is_open", "created_at")
    list_filter = ("is_open", "created_at")
    search_fields = ("name", "description")
    raw_id_fields = ("created_by", "opportunity")
    readonly_fields = ("created_at", "updated_at")


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ("team", "user", "is_leader", "created_at")
    list_filter = ("is_leader",)
    search_fields = ("team__name", "user__email")
    raw_id_fields = ("team", "user")


@admin.register(TeamRequest)
class TeamRequestAdmin(admin.ModelAdmin):
    list_display = ("team", "user", "status", "invited_by", "created_at")
    list_filter = ("status",)
    search_fields = ("team__name", "user__email")
    raw_id_fields = ("team", "user", "invited_by", "reviewed_by")
    readonly_fields = ("created_at", "updated_at")
