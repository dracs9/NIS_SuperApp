"""
Event workflow: submit for approval, approve, reject, and log status changes.
"""
from django.utils import timezone

from .models import Event, EventApplication, EventApprovalLog, EventStatus


def submit_event_for_approval(event, user):
    """Set event to Pending, create EventApplication and log."""
    if event.status != EventStatus.DRAFT:
        return False, "Event is not in draft."
    if event.created_by_id != user.id:
        return False, "Only the creator can submit."
    old_status = event.status
    event.status = EventStatus.PENDING
    event.save(update_fields=["status", "updated_at"])
    EventApplication.objects.get_or_create(event=event, defaults={"submitted_by": user})
    EventApprovalLog.objects.create(
        event=event,
        from_status=old_status,
        to_status=EventStatus.PENDING,
        changed_by=user,
        comment="Submitted for approval",
    )
    return True, None


def approve_event(event, user, comment=""):
    """Set event to Approved and log."""
    if event.status != EventStatus.PENDING:
        return False, "Event is not pending."
    if user.role not in ("admin", "teacher"):
        return False, "Only Admin or Teacher can approve."
    old_status = event.status
    event.status = EventStatus.APPROVED
    event.rejection_comment = ""
    event.save(update_fields=["status", "rejection_comment", "updated_at"])
    EventApprovalLog.objects.create(
        event=event,
        from_status=old_status,
        to_status=EventStatus.APPROVED,
        changed_by=user,
        comment=comment or "Approved",
    )
    return True, None


def reject_event(event, user, comment):
    """Set event to Rejected, set comment, and log."""
    if event.status != EventStatus.PENDING:
        return False, "Event is not pending."
    if user.role not in ("admin", "teacher"):
        return False, "Only Admin or Teacher can reject."
    if not (comment or "").strip():
        return False, "Rejection reason is required."
    old_status = event.status
    event.status = EventStatus.REJECTED
    event.rejection_comment = comment.strip()
    event.save(update_fields=["status", "rejection_comment", "updated_at"])
    EventApprovalLog.objects.create(
        event=event,
        from_status=old_status,
        to_status=EventStatus.REJECTED,
        changed_by=user,
        comment=comment.strip(),
    )
    return True, None
