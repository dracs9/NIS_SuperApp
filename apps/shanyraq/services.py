"""
Services for XP and SP management.
"""

from django.db import transaction
from django.db.models import Sum

from .models import Shanyraq, SourceType, XPLedger


def leaderboard_shanyraqs(limit=30):
    """Get top shanyraqs by season SP."""
    return Shanyraq.objects.filter(season_sp__gt=0).order_by("-season_sp")[:limit]


def leaderboard_students(limit=50, shanyraq=None):
    """Get top students by season XP, optionally filtered by shanyraq."""
    from apps.accounts.models import User, UserProfile

    queryset = User.objects.filter(is_active=True, season_xp__gt=0).select_related("profile")

    if shanyraq:
        queryset = queryset.filter(profile__shanyraq=shanyraq)

    users = queryset.order_by("-season_xp")[:limit]

    # Add rank and format for template
    result = []
    for i, user in enumerate(users, 1):
        result.append(
            {
                "user": user,
                "profile": user.profile,
                "rank": i,
                "points": user.season_xp,
            }
        )

    return result


def user_contribution_breakdown(user):
    """Get XP breakdown by source type for a user."""
    from django.db.models import Sum

    breakdown = (
        XPLedger.objects.filter(user=user)
        .values("source_type")
        .annotate(total=Sum("delta_xp"))
        .order_by("source_type")
    )

    return list(breakdown)


class XPService:
    """Service for managing XP awards and SP recalculation."""

    @staticmethod
    @transaction.atomic
    def award_xp(
        user,
        delta_xp,
        reason="",
        source_type=SourceType.ADMIN,
        reference_id=None,
        approved_by=None,
    ):
        """
        Award XP to a user and update their Shanyraq's SP.

        Args:
            user: User instance
            delta_xp: Integer XP change (can be negative)
            reason: Optional reason string
            source_type: SourceType choice
            reference_id: Optional reference ID
            approved_by: User who approved (optional)
        """
        # Create ledger entry
        ledger_entry = XPLedger.objects.create(
            user=user,
            delta_xp=delta_xp,
            reason=reason,
            source_type=source_type,
            reference_id=reference_id,
            approved_by=approved_by,
        )

        # Update user XP
        user.season_xp += delta_xp
        user.lifetime_xp += delta_xp
        user.save(update_fields=["season_xp", "lifetime_xp"])

        # Recalculate Shanyraq SP if user has a shanyraq
        if hasattr(user, "profile") and user.profile.shanyraq:
            XPService._recalculate_shanyraq_sp(user.profile.shanyraq)

        return ledger_entry

    @staticmethod
    def _recalculate_shanyraq_sp(shanyraq):
        """Recalculate season_sp and lifetime_sp for a Shanyraq."""
        # Calculate season SP (sum of member season_xp)
        season_sp = shanyraq.members.aggregate(total=Sum("user__season_xp"))["total"] or 0

        # Calculate lifetime SP (sum of member lifetime_xp)
        lifetime_sp = shanyraq.members.aggregate(total=Sum("user__lifetime_xp"))["total"] or 0

        # Update Shanyraq
        shanyraq.season_sp = season_sp
        shanyraq.lifetime_sp = lifetime_sp
        shanyraq.save(update_fields=["season_sp", "lifetime_sp"])

    @staticmethod
    def recalculate_all_shanyraq_sp():
        """Recalculate SP for all Shanyraqs (useful for data migration)."""
        for shanyraq in Shanyraq.objects.all():
            XPService._recalculate_shanyraq_sp(shanyraq)

    @staticmethod
    @transaction.atomic
    def reset_season():
        """Reset season XP for all users and recalculate Shanyraq SP."""
        from apps.accounts.models import User

        # Reset all user season XP
        User.objects.all().update(season_xp=0)

        # Reset all Shanyraq season SP
        Shanyraq.objects.all().update(season_sp=0)
