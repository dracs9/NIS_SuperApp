from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Role, User


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("name", "code")
    search_fields = ("name", "code")


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("email", "username", "role", "is_staff", "is_active")
    list_filter = ("role", "is_staff", "is_active")
    search_fields = ("email", "username")
    ordering = ("email",)
    filter_horizontal = ()

    fieldsets = list(BaseUserAdmin.fieldsets) + [
        (None, {"fields": ("role", "avatar", "phone")}),
    ]
    add_fieldsets = list(BaseUserAdmin.add_fieldsets) + [
        (None, {"fields": ("email", "role")}),
    ]
