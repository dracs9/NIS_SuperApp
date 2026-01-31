from django.contrib import admin

from .models import Skill, UserSkill


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "is_active", "created_at"]
    list_filter = ["category", "is_active"]
    search_fields = ["name", "description"]
    ordering = ["category", "name"]


@admin.register(UserSkill)
class UserSkillAdmin(admin.ModelAdmin):
    list_display = ["user", "skill", "level", "is_featured", "updated_at"]
    list_filter = ["level", "is_featured", "skill__category"]
    search_fields = ["user__email", "user__username", "skill__name"]
    raw_id_fields = ["user", "skill"]
    ordering = ["-updated_at"]
