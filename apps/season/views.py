"""
Season app: dashboard, quests, reward track, claim rewards.
"""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods, require_safe

from .models import QuestType, Season
from .services import claim_reward, get_user_reward_track, get_user_season_xp


def _get_active_season():
    """Get current active season or most recent."""
    from django.utils import timezone
    today = timezone.now().date()
    season = Season.objects.filter(is_active=True, start_date__lte=today, end_date__gte=today).first()
    if not season:
        season = Season.objects.filter(is_active=True).order_by("-start_date").first()
    return season


@require_safe
def season_dashboard_view(request):
    """Season dashboard: progress bar, quests, reward track."""
    season = _get_active_season()
    if not season:
        return render(
            request,
            "season/dashboard.html",
            {
                "section_name": "Season",
                "season": None,
                "quests_daily": [],
                "quests_weekly": [],
                "quests_milestone": [],
                "reward_track": [],
                "user_level": 0,
                "user_xp": 0,
                "xp_progress": 0,
                "xp_needed": 100,
            },
        )

    # Quests grouped by type
    quests = season.quests.filter(is_active=True).select_related("season")
    quests_daily = list(quests.filter(quest_type=QuestType.DAILY).order_by("order", "pk"))
    quests_weekly = list(quests.filter(quest_type=QuestType.WEEKLY).order_by("order", "pk"))
    quests_milestone = list(quests.filter(quest_type=QuestType.MILESTONE).order_by("order", "pk"))

    if request.user.is_authenticated:
        user_level = season.get_user_level(request.user)
        user_xp = season.get_user_xp(request.user)
        xp_progress, xp_needed = season.get_user_progress(request.user)
        reward_track = get_user_reward_track(request.user, season)
        # Load user progress for each quest
        from .models import UserQuestProgress
        user_progress = {
            p.quest_id: p
            for p in UserQuestProgress.objects.filter(
                user=request.user,
                quest__in=quests_daily + quests_weekly + quests_milestone,
            ).select_related("quest")
        }
        for q in quests_daily + quests_weekly + quests_milestone:
            q._user_progress = user_progress.get(q.id)
    else:
        user_level = 1
        user_xp = 0
        xp_progress = 0
        xp_needed = season.xp_per_level
        reward_track = [{"reward": r, "can_claim": False, "claimed": False, "locked": True} for r in season.rewards.all().order_by("level")]
        for q in quests_daily + quests_weekly + quests_milestone:
            q._user_progress = None

    return render(
        request,
        "season/dashboard.html",
        {
            "section_name": "Season",
            "season": season,
            "quests_daily": quests_daily,
            "quests_weekly": quests_weekly,
            "quests_milestone": quests_milestone,
            "reward_track": reward_track,
            "user_level": user_level,
            "user_xp": user_xp,
            "xp_progress": xp_progress,
            "xp_needed": xp_needed,
        },
    )


@login_required
@require_http_methods(["POST"])
def claim_reward_view(request, season_id, level):
    """Claim a season reward."""
    season = get_object_or_404(Season, pk=season_id, is_active=True)
    level = int(level)
    if level < 1 or level > season.max_level:
        messages.error(request, "Invalid level.")
        return redirect("season:dashboard")
    user_reward, error = claim_reward(request.user, season, level)
    if user_reward:
        messages.success(request, f"Claimed: {user_reward.season_reward.name}")
    else:
        messages.error(request, error or "Could not claim reward.")
    return redirect("season:dashboard")


@require_safe
def quest_list_view(request):
    """All quests for current season."""
    season = _get_active_season()
    if not season:
        return render(
            request,
            "season/quest_list.html",
            {"section_name": "Season", "season": None, "quests": []},
        )
    quests = list(season.quests.filter(is_active=True).select_related("season").order_by("quest_type", "order", "pk"))
    if request.user.is_authenticated:
        from .models import UserQuestProgress
        user_progress = {
            p.quest_id: p for p in UserQuestProgress.objects.filter(user=request.user, quest__in=quests).select_related("quest")
        }
        for q in quests:
            q._user_progress = user_progress.get(q.id)
    else:
        for q in quests:
            q._user_progress = None
    return render(
        request,
        "season/quest_list.html",
        {
            "section_name": "Season",
            "season": season,
            "quests": list(quests),
        },
    )
