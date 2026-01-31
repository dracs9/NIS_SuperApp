"""
Context processors for accounts: user profile, stats, theme, onboarding.
"""


def user_profile_stats(request):
    """
    Add user_profile, nis_points, shanyraq_points, user_rank, theme_preference,
    onboarding_needed for templates (navbar, theme toggle, onboarding modal).
    """
    from apps.shanyraq.models import Shanyraq

    context = {
        "user_profile": None,
        "nis_points": 0,
        "shanyraq_points": 0,
        "user_rank": "",
        "theme_preference": "system",
        "onboarding_needed": False,
        "onboarding_shanyraq_list": [],
    }
    if request.user.is_authenticated:
        profile = request.user.get_profile()
        context["user_profile"] = profile
        context["nis_points"] = profile.NIS_points
        context["shanyraq_points"] = profile.shanyraq_points
        context["user_rank"] = profile.rank or ""
        context["theme_preference"] = profile.theme or "system"
        context["onboarding_needed"] = not profile.onboarding_completed
        if context["onboarding_needed"]:
            context["onboarding_shanyraq_list"] = list(Shanyraq.objects.all().values("id", "name"))
    return context
