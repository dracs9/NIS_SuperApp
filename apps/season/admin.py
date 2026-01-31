from django.contrib import admin

from .models import Quest, Season, SeasonReward, UserQuestProgress, UserReward


@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "start_date", "end_date", "is_active", "xp_per_level", "max_level")
    list_filter = ("is_active",)
    search_fields = ("name", "slug", "description")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("created_at", "updated_at")


@admin.register(Quest)
class QuestAdmin(admin.ModelAdmin):
    list_display = ("title", "season", "quest_type", "target", "xp_reward", "order", "is_active")
    list_filter = ("quest_type", "season", "is_active")
    search_fields = ("title", "description")
    raw_id_fields = ("season",)
    ordering = ("season", "quest_type", "order")


@admin.register(UserQuestProgress)
class UserQuestProgressAdmin(admin.ModelAdmin):
    list_display = ("user", "quest", "current_progress", "completed_at", "updated_at")
    list_filter = ("quest__quest_type", "quest__season")
    search_fields = ("user__email", "quest__title")
    raw_id_fields = ("user", "quest")
    readonly_fields = ("created_at", "updated_at")


@admin.register(SeasonReward)
class SeasonRewardAdmin(admin.ModelAdmin):
    list_display = ("season", "level", "name", "reward_type", "order")
    list_filter = ("season", "reward_type")
    search_fields = ("name", "description")
    raw_id_fields = ("season",)
    ordering = ("season", "level")


@admin.register(UserReward)
class UserRewardAdmin(admin.ModelAdmin):
    list_display = ("user", "season_reward", "claimed_at")
    list_filter = ("season_reward__season",)
    search_fields = ("user__email", "season_reward__name")
    raw_id_fields = ("user", "season_reward")
    readonly_fields = ("claimed_at",)
