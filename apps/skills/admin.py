from django.contrib import admin

from .models import Skill, UserSkill


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "is_active", "created_at", "user_count"]
    list_filter = ["category", "is_active"]
    search_fields = ["name", "description"]
    ordering = ["category", "name"]
    readonly_fields = ["created_at"]

    fieldsets = (
        (
            "Basic Information",
            {
                "fields": ("name", "category", "description"),
            },
        ),
        (
            "Settings",
            {
                "fields": ("is_active",),
                "classes": ("collapse",),
            },
        ),
        (
            "Metadata",
            {
                "fields": ("created_at",),
                "classes": ("collapse",),
            },
        ),
    )

    def user_count(self, obj):
        return obj.userskill_set.count()

    user_count.short_description = "Users"


@admin.register(UserSkill)
class UserSkillAdmin(admin.ModelAdmin):
    list_display = ["user", "skill", "level", "is_featured", "updated_at"]
    list_filter = ["level", "is_featured", "skill__category", "updated_at"]
    search_fields = ["user__email", "user__username", "skill__name"]
    raw_id_fields = ["user", "skill"]
    ordering = ["-updated_at"]
    readonly_fields = ["created_at", "updated_at"]

    fieldsets = (
        (
            "User & Skill",
            {
                "fields": ("user", "skill"),
            },
        ),
        (
            "Proficiency",
            {
                "fields": ("level", "is_featured"),
                "description": "Level indicates proficiency. Featured skills appear prominently on user profiles.",
            },
        ),
        (
            "Metadata",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )
