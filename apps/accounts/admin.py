from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Role, User, UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    fk_name = "user"
    extra = 0
    fields = (
        "avatar",
        "full_name",
        "class_name",
        "shanyraq",
        "NIS_points",
        "shanyraq_points",
        "rank",
        "onboarding_completed",
        "theme",
    )


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("email", "get_role_display", "is_staff", "is_active")
    list_filter = ("role", "is_staff", "is_active")
    search_fields = ("email", "username", "profile__full_name")
    ordering = ("email",)
    filter_horizontal = ()
    inlines = [UserProfileInline]

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Role", {"fields": ("role",)}),
        ("Permissions", {"fields": ("is_staff", "is_active", "is_superuser")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {"fields": ("email", "password1", "password2")}),
        ("Role", {"fields": ("role",)}),
    )

    def get_role_display(self, obj):
        return dict(Role.choices).get(obj.role, obj.role)

    get_role_display.short_description = "Role"


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "full_name", "class_name", "shanyraq", "NIS_points", "shanyraq_points", "rank", "onboarding_completed", "theme")
    list_filter = ("shanyraq", "rank", "onboarding_completed", "theme")
    search_fields = ("user__email", "full_name", "class_name")
    raw_id_fields = ("user",)
    autocomplete_fields = ("shanyraq",)
