from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import ensure_csrf_cookie

from .models import User, UserProfile
from apps.shanyraq.models import Shanyraq


@login_required
@require_http_methods(["GET"])
def profile_view(request):
    """Profile page for the current user."""
    profile = request.user.get_profile()
    return render(request, "accounts/profile.html", {"profile": profile, "section_name": "Profile"})


@login_required
@require_http_methods(["GET"])
def profile_by_id_view(request, user_id):
    """Public profile view by user ID (optional; for viewing others)."""
    user = get_object_or_404(User, pk=user_id)
    profile = user.get_profile()
    return render(
        request,
        "accounts/profile.html",
        {"profile": profile, "section_name": "Profile", "is_own_profile": request.user == user},
    )


@login_required
@require_http_methods(["POST"])
def onboarding_save_view(request):
    """Save onboarding: class_name, shanyraq, avatar. Then set onboarding_completed."""
    profile = request.user.get_profile()
    profile.class_name = (request.POST.get("class_name") or "").strip()[:64]
    shanyraq_id = request.POST.get("shanyraq")
    if shanyraq_id:
        try:
            profile.shanyraq_id = int(shanyraq_id)
        except (ValueError, TypeError):
            pass
    if request.FILES.get("avatar"):
        profile.avatar = request.FILES["avatar"]
    profile.onboarding_completed = True
    profile.save()
    messages.success(request, "Profile updated. Welcome!")
    return redirect("accounts:profile")


@login_required
@require_http_methods(["POST"])
@ensure_csrf_cookie
def theme_save_view(request):
    """Persist theme preference to user profile."""
    theme = (request.POST.get("theme") or "").strip()
    if theme not in ("light", "dark", "system"):
        return JsonResponse({"ok": False}, status=400)
    profile = request.user.get_profile()
    profile.theme = theme
    profile.save()
    return JsonResponse({"ok": True})
