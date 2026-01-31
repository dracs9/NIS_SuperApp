"""
Season app: gamified Season Pass with quests, XP, levels, and rewards.
"""
from django.conf import settings
from django.db import models
from django.utils import timezone


class Season(models.Model):
    """A season/term with quests and rewards."""
    name = models.CharField(max_length=128)
    slug = models.SlugField(max_length=64, unique=True)
    description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    xp_per_level = models.PositiveIntegerField(default=100, help_text="XP needed per level")
    max_level = models.PositiveIntegerField(default=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "season"
        verbose_name_plural = "seasons"
        ordering = ["-start_date"]

    def __str__(self):
        return self.name

    @property
    def is_current(self):
        today = timezone.now().date()
        return self.start_date <= today <= self.end_date

    def get_user_xp(self, user):
        """Total XP earned by user from completed quests in this season."""
        total = 0
        for prog in UserQuestProgress.objects.filter(
            user=user, quest__season=self, quest__is_active=True
        ).select_related("quest"):
            if prog.completed_at or prog.current_progress >= prog.quest.target:
                total += prog.quest.xp_reward
        return total

    def get_user_level(self, user):
        """User's current level (1-10) based on XP."""
        xp = self.get_user_xp(user)
        level = min(self.max_level, (xp // self.xp_per_level) + 1)
        return level

    def get_user_progress(self, user):
        """XP progress within current level (0 to xp_per_level-1)."""
        xp = self.get_user_xp(user)
        level = self.get_user_level(user)
        if level >= self.max_level:
            return self.xp_per_level, self.xp_per_level  # full
        xp_in_level = xp % self.xp_per_level
        return xp_in_level, self.xp_per_level


class QuestType(models.TextChoices):
    DAILY = "daily", "Daily"
    WEEKLY = "weekly", "Weekly"
    MILESTONE = "milestone", "Milestone"


class Quest(models.Model):
    """Quest: daily, weekly, or milestone task for XP."""
    season = models.ForeignKey(
        Season,
        on_delete=models.CASCADE,
        related_name="quests",
    )
    quest_type = models.CharField(
        max_length=20,
        choices=QuestType.choices,
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    target = models.PositiveIntegerField(default=1, help_text="Target count to complete (e.g. 5 for 'Attend 5 events')")
    xp_reward = models.PositiveIntegerField(default=25)
    order = models.PositiveIntegerField(default=0, help_text="Display order")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "quest"
        verbose_name_plural = "quests"
        ordering = ["season", "quest_type", "order", "pk"]

    def __str__(self):
        return f"{self.get_quest_type_display()}: {self.title}"

    def get_user_progress(self, user):
        """Get or create UserQuestProgress for this user."""
        progress, _ = UserQuestProgress.objects.get_or_create(
            user=user,
            quest=self,
            defaults={"current_progress": 0},
        )
        return progress


class UserQuestProgress(models.Model):
    """User's progress on a quest."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="quest_progress",
    )
    quest = models.ForeignKey(
        Quest,
        on_delete=models.CASCADE,
        related_name="user_progress",
    )
    current_progress = models.PositiveIntegerField(default=0)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "user quest progress"
        verbose_name_plural = "user quest progresses"
        unique_together = [["user", "quest"]]
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.user.email} — {self.quest.title}: {self.current_progress}/{self.quest.target}"

    @property
    def is_completed(self):
        return self.completed_at is not None or self.current_progress >= self.quest.target

    @property
    def progress_percent(self):
        return min(100, int(100 * self.current_progress / max(1, self.quest.target)))


class RewardType(models.TextChoices):
    XP = "xp", "XP Bonus"
    COSMETIC = "cosmetic", "Cosmetic"
    BADGE = "badge", "Badge"
    TITLE = "title", "Title"
    OTHER = "other", "Other"


class SeasonReward(models.Model):
    """Reward at a specific level on the season track."""
    season = models.ForeignKey(
        Season,
        on_delete=models.CASCADE,
        related_name="rewards",
    )
    level = models.PositiveIntegerField(help_text="Level 1-10")
    name = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    reward_type = models.CharField(
        max_length=20,
        choices=RewardType.choices,
        default=RewardType.OTHER,
    )
    icon = models.CharField(max_length=64, blank=True, help_text="Emoji or icon name")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "season reward"
        verbose_name_plural = "season rewards"
        unique_together = [["season", "level"]]
        ordering = ["season", "level"]

    def __str__(self):
        return f"Lv.{self.level}: {self.name}"


class UserReward(models.Model):
    """User has claimed a season reward."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="claimed_rewards",
    )
    season_reward = models.ForeignKey(
        SeasonReward,
        on_delete=models.CASCADE,
        related_name="claims",
    )
    claimed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "user reward"
        verbose_name_plural = "user rewards"
        unique_together = [["user", "season_reward"]]
        ordering = ["-claimed_at"]

    def __str__(self):
        return f"{self.user.email} claimed {self.season_reward.name}"
