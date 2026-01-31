"""
Season progress: XP calculation, quest completion, claim rewards.
"""
from django.utils import timezone

from .models import Quest, Season, SeasonReward, UserQuestProgress, UserReward


def get_user_season_xp(user, season):
    """Total XP earned by user in this season from completed quests."""
    return season.get_user_xp(user)


def add_quest_progress(user, quest, amount=1):
    """Add progress to a quest. Returns (progress_obj, completed)."""
    prog = quest.get_user_progress(user)
    if prog.completed_at:
        return prog, False  # already completed
    prog.current_progress = min(prog.quest.target, prog.current_progress + amount)
    prog.save(update_fields=["current_progress", "updated_at"])
    if prog.current_progress >= prog.quest.target:
        prog.completed_at = timezone.now()
        prog.save(update_fields=["completed_at", "updated_at"])
        return prog, True
    return prog, False


def can_claim_reward(user, season, level):
    """Check if user can claim the reward at this level."""
    user_level = season.get_user_level(user)
    if level > user_level:
        return False, "Level too low"
    try:
        reward = SeasonReward.objects.get(season=season, level=level)
    except SeasonReward.DoesNotExist:
        return False, "Reward not found"
    if UserReward.objects.filter(user=user, season_reward=reward).exists():
        return False, "Already claimed"
    return True, reward


def claim_reward(user, season, level):
    """Claim a season reward. Returns (UserReward or None, error_msg)."""
    ok, result = can_claim_reward(user, season, level)
    if not ok:
        if isinstance(result, str):
            return None, result
        return None, "Cannot claim"
    reward = result
    user_reward, created = UserReward.objects.get_or_create(
        user=user,
        season_reward=reward,
    )
    return user_reward, None


def get_user_reward_track(user, season):
    """List of rewards with claim status for user."""
    rewards = list(season.rewards.all().order_by("level"))
    claimed_ids = set(
        UserReward.objects.filter(user=user, season_reward__season=season).values_list(
            "season_reward_id", flat=True
        )
    )
    user_level = season.get_user_level(user)
    result = []
    for r in rewards:
        can_claim = r.level <= user_level and r.id not in claimed_ids
        claimed = r.id in claimed_ids
        result.append({
            "reward": r,
            "can_claim": can_claim,
            "claimed": claimed,
            "locked": r.level > user_level,
        })
    return result
