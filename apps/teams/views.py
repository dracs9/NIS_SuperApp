"""
Teams app: finder feed, detail, create, apply, invite, accept/reject.
"""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods, require_safe

from .forms import TeamCreateForm, TeamInviteForm
from .models import Team, TeamRequest, TeamRequestStatus
from .services import accept_request, apply_to_team, create_team, invite_to_team, reject_request


@require_safe
def team_feed_view(request):
    """Team finder feed: list of open teams."""
    qs = Team.objects.filter(is_open=True).select_related("created_by", "opportunity").prefetch_related("members")
    opportunity_id = request.GET.get("opportunity", "").strip()
    if opportunity_id:
        try:
            qs = qs.filter(opportunity_id=int(opportunity_id))
        except ValueError:
            pass
    teams = list(qs[:50])
    return render(
        request,
        "teams/feed.html",
        {
            "section_name": "Teams",
            "teams": teams,
            "filter_opportunity": opportunity_id,
        },
    )


@require_safe
def team_detail_view(request, pk):
    """Team detail: members, requests, apply/invite actions."""
    team = get_object_or_404(
        Team.objects.select_related("created_by", "opportunity").prefetch_related("members__user"),
        pk=pk,
    )
    members = team.get_members()
    pending_requests = []
    user_request = None
    if request.user.is_authenticated:
        pending_requests = list(team.requests.filter(status=TeamRequestStatus.PENDING).select_related("user", "invited_by")[:20])
        user_request = team.requests.filter(user=request.user).first()
    return render(
        request,
        "teams/detail.html",
        {
            "section_name": "Teams",
            "team": team,
            "members": members,
            "pending_requests": pending_requests,
            "user_request": user_request,
            "is_member": team.is_member(request.user),
            "can_manage": team.can_manage(request.user),
        },
    )


@login_required
@require_http_methods(["GET", "POST"])
def team_create_view(request):
    """Create a new team."""
    if request.method == "POST":
        form = TeamCreateForm(request.POST)
        if form.is_valid():
            team = create_team(
                created_by=request.user,
                name=form.cleaned_data["name"],
                description=form.cleaned_data.get("description", ""),
                opportunity=form.cleaned_data.get("opportunity"),
            )
            messages.success(request, f"Team «{team.name}» created.")
            return redirect("teams:detail", pk=team.pk)
    else:
        form = TeamCreateForm()
    return render(
        request,
        "teams/create.html",
        {
            "section_name": "Teams",
            "form": form,
        },
    )


@login_required
@require_http_methods(["POST"])
def team_apply_view(request, pk):
    """Apply to join a team."""
    team = get_object_or_404(Team, pk=pk)
    message = request.POST.get("message", "").strip()
    req, error = apply_to_team(team, request.user, message)
    if req:
        messages.success(request, "Application sent.")
    else:
        messages.error(request, error or "Could not apply.")
    return redirect("teams:detail", pk=pk)


@login_required
@require_http_methods(["GET", "POST"])
def team_invite_view(request, pk):
    """Invite a user to join team (leader/creator only)."""
    team = get_object_or_404(Team, pk=pk)
    if not team.can_manage(request.user):
        return HttpResponseForbidden()
    if request.method == "POST":
        form = TeamInviteForm(request.POST)
        if form.is_valid():
            invitee = form.invitee
            req, error = invite_to_team(team, request.user, invitee, form.cleaned_data.get("message", ""))
            if req:
                messages.success(request, f"Invitation sent to {invitee.email}.")
                return redirect("teams:detail", pk=pk)
            else:
                messages.error(request, error or "Could not invite.")
    else:
        form = TeamInviteForm()
    return render(
        request,
        "teams/invite.html",
        {
            "section_name": "Teams",
            "team": team,
            "form": form,
        },
    )


@login_required
@require_http_methods(["POST"])
def team_request_accept_view(request, pk, request_id):
    """Accept a team request (leader or the applicant for self-withdraw)."""
    team = get_object_or_404(Team, pk=pk)
    team_req = get_object_or_404(team.requests, pk=request_id)
    ok, error = accept_request(team_req, request.user)
    if ok:
        messages.success(request, "Request accepted.")
    else:
        messages.error(request, error or "Could not accept.")
    return redirect("teams:detail", pk=pk)


@login_required
@require_http_methods(["POST"])
def team_request_reject_view(request, pk, request_id):
    """Reject a team request."""
    team = get_object_or_404(Team, pk=pk)
    team_req = get_object_or_404(team.requests, pk=request_id)
    ok, error = reject_request(team_req, request.user)
    if ok:
        messages.success(request, "Request rejected.")
    else:
        messages.error(request, error or "Could not reject.")
    return redirect("teams:detail", pk=pk)
