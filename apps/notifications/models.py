from django.contrib.auth import get_user_model
from django.db import models


class NotificationType(models.TextChoices):
    """Types of notifications in the system."""

    EVENT_APPROVED = "event_approved", "Event Approved"
    EVENT_REJECTED = "event_rejected", "Event Rejected"
    QUEST_COMPLETED = "quest_completed", "Quest Completed"
    TEAM_INVITE = "team_invite", "Team Invite"
    ACTIVITY_APPROVED = "activity_approved", "Activity Approved"
    ACHIEVEMENT_UNLOCKED = "achievement_unlocked", "Achievement Unlocked"
    LEADERBOARD_MILESTONE = "leaderboard_milestone", "Leaderboard Milestone"
    SYSTEM = "system", "System Notification"


class Notification(models.Model):
    """Notification for users about system events."""

    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(
        max_length=30,
        choices=NotificationType.choices,
        default=NotificationType.SYSTEM,
    )
    is_read = models.BooleanField(default=False)

    # Optional: Link to related object (Event, Quest, etc.)
    related_object_type = models.CharField(max_length=50, blank=True, null=True)
    related_object_id = models.PositiveIntegerField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "notification"
        verbose_name_plural = "notifications"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} - {self.user.email}"
