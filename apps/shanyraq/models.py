from django.conf import settings
from django.db import models


class Shanyraq(models.Model):
    """Shanyraq group (e.g. class/house)."""

    name = models.CharField(max_length=128)
    slug = models.SlugField(max_length=64, unique=True, blank=True)
    season_sp = models.PositiveIntegerField(
        default=0, help_text="Season Shanyraq Points (cached sum of member season_xp)"
    )
    lifetime_sp = models.PositiveIntegerField(
        default=0, help_text="Lifetime Shanyraq Points (cached sum of member lifetime_xp)"
    )

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


class ActivitySubmission(models.Model):
    """Student activity submission for XP award."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="activity_submissions",
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    awards_xp = models.PositiveIntegerField(default=0, help_text="XP awarded for this activity")
    status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
        ],
        default="pending",
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_submissions",
    )
    review_notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-submitted_at"]
        verbose_name = "Activity submission"
        verbose_name_plural = "Activity submissions"

    def __str__(self):
        return f"{self.user.email}: {self.title} ({self.status})"


class XPLedger(models.Model):
    """Ledger entry: XP added or revoked for a user."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="xp_transactions",
    )
    delta_xp = models.IntegerField(
        help_text="XP change amount (positive = credit, negative = debit/penalty)"
    )
    reason = models.CharField(max_length=255, blank=True)
    source_type = models.CharField(
        max_length=20,
        choices=SourceType.choices,
        default=SourceType.ADMIN,
    )
    reference_id = models.PositiveIntegerField(
        null=True, blank=True, help_text="PK of event/activity etc."
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_xp_transactions",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "XP transaction"
        verbose_name_plural = "XP transactions"

    def __str__(self):
        return f"{self.user.email} {self.delta_xp:+d} XP ({self.get_source_type_display()})"
