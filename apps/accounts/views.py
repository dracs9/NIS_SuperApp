from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods

from apps.shanyraq.models import Shanyraq
from apps.skills.models import Skill, UserSkill

from .forms import ProfileEditForm
from .models import User, UserProfile


@login_required
@require_http_methods(["GET", "POST"])
def profile_edit_view(request):
    """Edit profile page for the current user."""
    profile = request.user.get_profile()

    if request.method == "POST":
        form = ProfileEditForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect("accounts:profile")
    else:
        form = ProfileEditForm(instance=profile)

    context = {
        "profile": profile,
        "form": form,
        "section_name": "Edit Profile",
    }

    return render(request, "accounts/profile_edit.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def profile_view(request):
    """Profile page for the current user."""
    profile = request.user.get_profile()

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "update_skills":
            # Handle skills update
            selected_skills = request.POST.getlist("skills")
            interests = request.POST.get("interests", "").strip()

            # Clear existing skills
            UserSkill.objects.filter(user=request.user).delete()

            # Add new skills
            for skill_id in selected_skills:
                try:
                    skill_id = int(skill_id)
                    level = request.POST.get(f"skill_level_{skill_id}", "beginner")
                    UserSkill.objects.create(user=request.user, skill_id=skill_id, level=level)
                except (ValueError, TypeError):
                    continue

            # Update interests
            profile.interests = interests
            profile.save()

            messages.success(request, "Skills updated successfully!")
            return redirect("accounts:profile")

    # Get context for template
    all_skills = Skill.objects.filter(is_active=True).order_by("category", "name")
    user_skill_ids = set(request.user.user_skills.values_list("skill_id", flat=True))
    user_skill_levels = {us.skill_id: us.level for us in request.user.user_skills.all()}

    context = {
        "profile": profile,
        "section_name": "Profile",
        "all_skills": all_skills,
        "user_skill_ids": user_skill_ids,
        "user_skill_levels": user_skill_levels,
        "skill_levels": UserSkill.LEVEL_CHOICES,
    }

    return render(request, "accounts/profile.html", context)


@login_required
@require_http_methods(["GET"])
def profile_by_id_view(request, user_id):
    """Public profile view by user ID (optional; for viewing others)."""
    user = get_object_or_404(User, pk=user_id)
    profile = user.get_profile()

    context = {
        "profile": profile,
        "section_name": "Profile",
        "is_own_profile": request.user == user,
    }

    # Add skills context for viewing
    if request.user == user:
        # Own profile - show edit context
        all_skills = Skill.objects.filter(is_active=True).order_by("category", "name")
        user_skill_ids = set(user.user_skills.values_list("skill_id", flat=True))
        user_skill_levels = {us.skill_id: us.level for us in user.user_skills.all()}

        context.update(
            {
                "all_skills": all_skills,
                "user_skill_ids": user_skill_ids,
                "user_skill_levels": user_skill_levels,
                "skill_levels": UserSkill.LEVEL_CHOICES,
            }
        )

    return render(request, "accounts/profile.html", context)


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
