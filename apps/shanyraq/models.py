from django.conf import settings
from django.db import models


class Shanyraq(models.Model):
    """Shanyraq group (e.g. class/house)."""
    name = models.CharField(max_length=128)
    slug = models.SlugField(max_length=64, unique=True, blank=True)
    total_points = models.PositiveIntegerField(default=0, help_text="Cached sum of member shanyraq_points")

    class Meta:
        ordering = ["name"]
        verbose_name = "Shanyraq"
        verbose_name_plural = "Shanyraqs"

    def __str__(self):
        return self.name


class ShanyraqMembership(models.Model):
    """User membership in a Shanyraq."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="shanyraq_memberships",
    )
    shanyraq = models.ForeignKey(
        Shanyraq,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    joined_at = models.DateTimeField(auto_now_add=True)
    is_leader = models.BooleanField(default=False)

    class Meta:
        ordering = ["-joined_at"]
        unique_together = [["user", "shanyraq"]]
        verbose_name = "Shanyraq membership"
        verbose_name_plural = "Shanyraq memberships"

    def __str__(self):
        return f"{self.user.email} in {self.shanyraq.name}"


class SourceType(models.TextChoices):
    EVENT = "event", "Event"
    ACTIVITY = "activity", "Activity"
    ADMIN = "admin", "Admin"
    PENALTY = "penalty", "Penalty"


class PointTransaction(models.Model):
    """Ledger entry: points added or revoked for a user in a shanyraq."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="point_transactions",
    )
    shanyraq = models.ForeignKey(
        Shanyraq,
        on_delete=models.CASCADE,
        related_name="point_transactions",
    )
    amount = models.IntegerField(help_text="Positive = credit, negative = debit/penalty")
    reason = models.CharField(max_length=255, blank=True)
    source_type = models.CharField(
        max_length=20,
        choices=SourceType.choices,
        default=SourceType.ADMIN,
    )
    source_id = models.PositiveIntegerField(null=True, blank=True, help_text="PK of event/activity etc.")
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_transactions",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Point transaction"
        verbose_name_plural = "Point transactions"

    def __str__(self):
        return f"{self.user.email} {self.amount:+d} @ {self.shanyraq.name} ({self.get_source_type_display()})"
