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
    list_display = (
        "user",
        "full_name",
        "class_name",
        "shanyraq",
        "rank",
        "onboarding_completed",
        "theme",
    )
    list_filter = ("shanyraq", "rank", "onboarding_completed", "theme", "class_name")
    search_fields = ("user__email", "full_name", "class_name", "bio")
    raw_id_fields = ("user",)
    autocomplete_fields = ("shanyraq",)
    readonly_fields = ("last_activity",)

    fieldsets = (
        (
            "User Information",
            {
                "fields": ("user", "full_name", "bio", "avatar"),
                "classes": ("wide",),
            },
        ),
        (
            "Academic Information",
            {
                "fields": ("class_name", "shanyraq"),
                "classes": ("wide",),
            },
        ),
        (
            "Ranking",
            {
                "fields": ("rank",),
                "classes": ("wide",),
                "description": "Rank is updated by the system.",
            },
        ),
        (
            "Social Links",
            {
                "fields": ("github_url", "instagram_url", "linkedin_url", "telegram_url"),
                "classes": ("wide", "collapse"),
            },
        ),
        (
            "System Settings",
            {
                "fields": ("onboarding_completed", "theme", "last_activity"),
                "classes": ("wide", "collapse"),
            },
        ),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user", "shanyraq")
