"""
Teams app: team formation for olympiads, projects, and collaboration.
"""
from django.conf import settings
from django.db import models
from django.utils import timezone


class Team(models.Model):
    """Team for an olympiad, project, or collaboration."""
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    opportunity = models.ForeignKey(
        "opportunities.Opportunity",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="teams",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_teams",
    )
    is_open = models.BooleanField(default=True, help_text="Accepting new members")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "team"
        verbose_name_plural = "teams"
        ordering = ["-updated_at"]

    def __str__(self):
        return self.name

    def get_members(self):
        """Return team members with roles."""
        return self.members.select_related("user").order_by("-is_leader", "created_at")

    def is_member(self, user):
        return self.members.filter(user=user).exists()

    def is_leader(self, user):
        return self.members.filter(user=user, is_leader=True).exists()

    def can_manage(self, user):
        """Can invite, accept, reject requests."""
        if not user.is_authenticated:
            return False
        return self.is_leader(user) or self.created_by_id == user.id


class TeamMember(models.Model):
    """User membership in a team."""
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name="members",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="team_memberships",
    )
    is_leader = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "team member"
        verbose_name_plural = "team members"
        unique_together = [["team", "user"]]
        ordering = ["-is_leader", "created_at"]

    def __str__(self):
        return f"{self.user.email} in {self.team.name}"


class TeamRequestStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    ACCEPTED = "accepted", "Accepted"
    REJECTED = "rejected", "Rejected"


class TeamRequest(models.Model):
    """Application to join a team or invitation to join."""
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name="requests",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="team_requests",
    )
    message = models.TextField(blank=True, help_text="Application message or invite note")
    status = models.CharField(
        max_length=20,
        choices=TeamRequestStatus.choices,
        default=TeamRequestStatus.PENDING,
    )
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sent_invites",
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_team_requests",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "team request"
        verbose_name_plural = "team requests"
        unique_together = [["team", "user"]]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.email} → {self.team.name} ({self.status})"

    @property
    def is_application(self):
        """User applied to join (not invited)."""
        return self.invited_by_id is None

    @property
    def is_invitation(self):
        """User was invited by someone."""
        return self.invited_by_id is not None
