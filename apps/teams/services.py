"""
Team formation: create, apply, invite, accept, reject.
"""
from django.utils import timezone

from .models import Team, TeamMember, TeamRequest, TeamRequestStatus


def create_team(created_by, name, description="", opportunity=None):
    """Create a team with creator as leader."""
    team = Team.objects.create(
        name=name,
        description=description,
        opportunity=opportunity,
        created_by=created_by,
    )
    TeamMember.objects.create(team=team, user=created_by, is_leader=True)
    return team


def apply_to_team(team, user, message=""):
    """User applies to join team. Returns (TeamRequest or None, error)."""
    if team.members.filter(user=user).exists():
        return None, "Already a member"
    req, created = TeamRequest.objects.get_or_create(
        team=team,
        user=user,
        defaults={
            "message": message or "",
            "status": TeamRequestStatus.PENDING,
        },
    )
    if not created:
        if req.status == TeamRequestStatus.PENDING:
            return req, "Application already pending"
        if req.status == TeamRequestStatus.ACCEPTED:
            return None, "Already a member"
        # Rejected before - allow re-apply
        req.status = TeamRequestStatus.PENDING
        req.message = message or ""
        req.invited_by = None
        req.reviewed_by = None
        req.reviewed_at = None
        req.save(update_fields=["status", "message", "invited_by", "reviewed_by", "reviewed_at", "updated_at"])
    return req, None


def invite_to_team(team, inviter, invitee, message=""):
    """Inviter invites invitee to join team. Returns (TeamRequest or None, error)."""
    if not team.can_manage(inviter):
        return None, "You cannot invite to this team"
    if team.members.filter(user=invitee).exists():
        return None, "User is already a member"
    req, created = TeamRequest.objects.update_or_create(
        team=team,
        user=invitee,
        defaults={
            "message": message or "",
            "status": TeamRequestStatus.PENDING,
            "invited_by": inviter,
        },
    )
    return req, None


def accept_request(request, reviewer):
    """Accept a team request. Returns (ok, error)."""
    if request.status != TeamRequestStatus.PENDING:
        return False, "Request is not pending"
    if not request.team.can_manage(reviewer) and reviewer.id != request.user.id:
        return False, "You cannot manage this request"
    if request.team.members.filter(user=request.user).exists():
        return False, "User is already a member"
    request.status = TeamRequestStatus.ACCEPTED
    request.reviewed_by = reviewer
    request.reviewed_at = timezone.now()
    request.save(update_fields=["status", "reviewed_by", "reviewed_at", "updated_at"])
    TeamMember.objects.get_or_create(team=request.team, user=request.user, defaults={"is_leader": False})
    return True, None


def reject_request(request, reviewer):
    """Reject a team request. Returns (ok, error)."""
    if request.status != TeamRequestStatus.PENDING:
        return False, "Request is not pending"
    if request.team.can_manage(reviewer) or reviewer.id == request.user.id:
        request.status = TeamRequestStatus.REJECTED
        request.reviewed_by = reviewer
        request.reviewed_at = timezone.now()
        request.save(update_fields=["status", "reviewed_by", "reviewed_at", "updated_at"])
        return True, None
    return False, "You cannot manage this request"


def leave_team(team, user):
    """User leaves team. Returns (ok, error)."""
    member = team.members.filter(user=user).first()
    if not member:
        return False, "Not a member"
    if member.is_leader and team.members.filter(is_leader=True).count() <= 1:
        return False, "Transfer leadership before leaving"
    member.delete()
    return True, None
