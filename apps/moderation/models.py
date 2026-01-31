from django.conf import settings
from django.db import models


class ActionType(models.TextChoices):
    """Types of moderation actions."""

    APPROVE_EVENT = "approve_event", "Approve Event"
    REJECT_EVENT = "reject_event", "Reject Event"
    APPROVE_BOOKING = "approve_booking", "Approve Space Booking"
    REJECT_BOOKING = "reject_booking", "Reject Space Booking"
    CANCEL_BOOKING = "cancel_booking", "Cancel Space Booking"
    ADD_POINTS = "add_points", "Add Points"
    REVOKE_POINTS = "revoke_points", "Revoke Points"
    UPDATE_USER = "update_user", "Update User"
    UPDATE_SHANYRAQ = "update_shanyraq", "Update Shanyraq"


class ModeratorActionLog(models.Model):
    """Log of all moderator actions for audit trail."""

    moderator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="moderator_actions",
    )
    action_type = models.CharField(
        max_length=20,
        choices=ActionType.choices,
    )
    target_model = models.CharField(max_length=100, help_text="Model name (e.g. 'events.Event')")
    target_id = models.PositiveIntegerField(help_text="Primary key of the target object")
    description = models.TextField(blank=True, help_text="Human-readable description of the action")
    old_value = models.TextField(blank=True, help_text="JSON representation of old state")
    new_value = models.TextField(blank=True, help_text="JSON representation of new state")
    comment = models.TextField(blank=True, help_text="Optional moderator comment")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "moderator action log"
        verbose_name_plural = "moderator action logs"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["action_type", "created_at"]),
            models.Index(fields=["moderator", "created_at"]),
        ]

    def __str__(self):
        return f"{self.moderator} {self.get_action_type_display()} {self.target_id}"
