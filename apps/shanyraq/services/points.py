"""
Points service: atomic add/revoke, recalc totals, leaderboard queries.
"""
from django.db import transaction
from django.db.models import Sum

from apps.accounts.models import UserProfile
from ..models import PointTransaction, Shanyraq, ShanyraqMembership, SourceType


def add_points(
    user,
    shanyraq,
    amount,
    reason="",
    source_type=SourceType.ADMIN,
    source_id=None,
    approved_by=None,
):
    """
    Add or subtract points for a user in a shanyraq (atomic).
    Updates UserProfile.shanyraq_points and Shanyraq.total_points.
    amount: positive = credit, negative = debit/penalty.
    """
    if amount == 0:
        return None
    with transaction.atomic():
        t = PointTransaction.objects.create(
            user=user,
            shanyraq=shanyraq,
            amount=amount,
            reason=reason or "",
            source_type=source_type,
            source_id=source_id,
            approved_by=approved_by,
        )
        profile = user.get_profile()
        profile.NIS_points = (profile.NIS_points or 0) + amount
        if profile.shanyraq_id == shanyraq.id:
            profile.shanyraq_points = (profile.shanyraq_points or 0) + amount
        profile.save(update_fields=["shanyraq_points", "NIS_points"])
        recalculate_shanyraq_total(shanyraq)
    return t


def revoke_points(user, shanyraq, amount, reason="", approved_by=None):
    """Revoke (subtract) points. amount should be positive; creates negative transaction."""
    if amount <= 0:
        return None
    return add_points(
        user=user,
        shanyraq=shanyraq,
        amount=-amount,
        reason=reason or "Revoked",
        source_type=SourceType.ADMIN,
        approved_by=approved_by,
    )


def recalculate_shanyraq_total(shanyraq):
    """Set Shanyraq.total_points to sum of all PointTransaction.amount for this shanyraq."""
    total = (
        PointTransaction.objects.filter(shanyraq=shanyraq).aggregate(s=Sum("amount"))["s"]
        or 0
    )
    shanyraq.total_points = max(0, total)
    shanyraq.save(update_fields=["total_points"])


def recalculate_all_shanyraq_totals():
    """Recalc total_points for every Shanyraq."""
    for shanyraq in Shanyraq.objects.all():
        recalculate_shanyraq_total(shanyraq)


def leaderboard_students(limit=50, shanyraq=None):
    """
    Live leaderboard: users with highest shanyraq_points (or NIS_points).
    If shanyraq is set, filter to members of that shanyraq.
    Returns list of dicts: user, profile, points, rank.
    """
    from django.contrib.auth import get_user_model

    User = get_user_model()
    qs = UserProfile.objects.select_related("user", "shanyraq").filter(
        user__is_active=True
    )
    if shanyraq:
        qs = qs.filter(shanyraq=shanyraq)
    qs = qs.order_by("-shanyraq_points")[:limit]
    return [
        {"user": p.user, "profile": p, "points": p.shanyraq_points or 0, "rank": i + 1}
        for i, p in enumerate(qs)
    ]


def leaderboard_shanyraqs(limit=20):
    """Live leaderboard: shanyraqs ordered by total_points."""
    return list(
        Shanyraq.objects.all().order_by("-total_points")[:limit]
    )


def user_contribution_breakdown(user, shanyraq=None):
    """
    Sum of point_transactions for user (optionally in one shanyraq),
    grouped by source_type.
    """
    qs = PointTransaction.objects.filter(user=user).values("source_type").annotate(
        total=Sum("amount")
    )
    if shanyraq:
        qs = qs.filter(shanyraq=shanyraq)
    return list(qs)
