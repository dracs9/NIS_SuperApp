"""
Events app: list, detail, creation wizard, submit, approve/reject, review panel.
"""

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods, require_safe

from apps.accounts.decorators import event_creator_required, teacher_required

from .forms import (
    EventApproveRejectForm,
    EventWizardStep1Form,
    EventWizardStep2Form,
    EventWizardStep3Form,
)
from .models import Event, EventStatus
from .services import approve_event, reject_event, submit_event_for_approval

User = get_user_model()
SESSION_WIZARD_KEY = "event_wizard_data"


def _get_upcoming_approved():
    """Events that are approved and start in the future."""
    now = timezone.now()
    return (
        Event.objects.filter(status=EventStatus.APPROVED, start_at__gt=now)
        .select_related("created_by")
        .order_by("start_at")
    )


def _get_planned():
    """Draft or pending events (awaiting approval or not yet submitted)."""
    return (
        Event.objects.filter(status__in=(EventStatus.DRAFT, EventStatus.PENDING))
        .select_related("created_by")
        .order_by("-updated_at")
    )


def _get_past():
    """Events that have ended (approved and end_at in the past)."""
    now = timezone.now()
    return (
        Event.objects.filter(status=EventStatus.APPROVED, end_at__lt=now)
        .select_related("created_by")
        .order_by("-end_at")[:50]
    )


@require_safe
def event_list_view(request):
    """Event list: Upcoming, Planned, Past tabs."""
    upcoming = _get_upcoming_approved()
    planned = _get_planned()
    past = _get_past()
    return render(
        request,
        "events/event_list.html",
        {
            "section_name": "Events",
            "upcoming_events": upcoming,
            "planned_events": planned,
            "past_events": past,
        },
    )


@require_safe
def event_detail_view(request, pk):
    """Event detail: show event and status; creator sees submit, moderator sees approve/reject."""
    event = get_object_or_404(Event.objects.select_related("created_by", "policy"), pk=pk)
    logs = event.approval_logs.select_related("changed_by").order_by("-created_at")[:20]  # type: ignore[union-attr]
    return render(
        request,
        "events/event_detail.html",
        {
            "section_name": "Events",
            "event": event,
            "approval_logs": logs,
            "can_submit": event.can_submit(request.user),
            "can_approve_or_reject": event.can_approve_or_reject(request.user),
        },
    )


@event_creator_required
@require_http_methods(["GET", "POST"])
def event_wizard_view(request, step):
    """Multi-step event creation wizard. step in (1, 2, 3)."""
    step = int(step)
    if step not in (1, 2, 3):
        return redirect("events:wizard", step=1)
    wizard_data = request.session.get(SESSION_WIZARD_KEY, {})

    if request.method == "POST":
        if step == 1:
            form = EventWizardStep1Form(request.POST)
            if form.is_valid():
                wizard_data["title"] = form.cleaned_data["title"]
                wizard_data["description"] = form.cleaned_data.get("description", "")
                request.session[SESSION_WIZARD_KEY] = wizard_data
                return redirect("events:wizard", step=2)
        elif step == 2:
            form = EventWizardStep2Form(request.POST)
            if form.is_valid():
                wizard_data["start_at"] = form.cleaned_data["start_at"].isoformat()
                wizard_data["end_at"] = form.cleaned_data["end_at"].isoformat()
                wizard_data["location"] = form.cleaned_data.get("location", "")
                request.session[SESSION_WIZARD_KEY] = wizard_data
                return redirect("events:wizard", step=3)
        elif step == 3:
            form = EventWizardStep3Form(request.POST)
            if form.is_valid():
                from datetime import datetime

                policy = form.cleaned_data.get("policy")
                start_at = wizard_data["start_at"]
                end_at = wizard_data["end_at"]
                if isinstance(start_at, str):
                    start_at = datetime.fromisoformat(start_at.replace("Z", "+00:00"))
                if isinstance(end_at, str):
                    end_at = datetime.fromisoformat(end_at.replace("Z", "+00:00"))
                if timezone.is_naive(start_at):
                    start_at = timezone.make_aware(start_at)
                if timezone.is_naive(end_at):
                    end_at = timezone.make_aware(end_at)
                event = Event.objects.create(
                    title=wizard_data["title"],
                    description=wizard_data.get("description", ""),
                    start_at=start_at,
                    end_at=end_at,
                    location=wizard_data.get("location", ""),
                    status=EventStatus.DRAFT,
                    policy=policy,
                    created_by=request.user,
                )
                del request.session[SESSION_WIZARD_KEY]
                messages.success(
                    request,
                    f"Event «{event.title}» created as draft. You can submit it for approval.",
                )
                return redirect("events:detail", pk=event.pk)
    else:
        if step == 1:
            form = EventWizardStep1Form(
                initial={
                    "title": wizard_data.get("title"),
                    "description": wizard_data.get("description", ""),
                }
            )
        elif step == 2:
            from datetime import datetime

            start = wizard_data.get("start_at")
            end = wizard_data.get("end_at")
            if start:
                try:
                    if isinstance(start, str) and "T" in start:
                        start = datetime.fromisoformat(start.replace("Z", "+00:00"))
                    elif isinstance(start, str):
                        start = datetime.fromisoformat(start)
                except (ValueError, TypeError):
                    start = None
            if end:
                try:
                    if isinstance(end, str) and "T" in end:
                        end = datetime.fromisoformat(end.replace("Z", "+00:00"))
                    elif isinstance(end, str):
                        end = datetime.fromisoformat(end)
                except (ValueError, TypeError):
                    end = None
            form = EventWizardStep2Form(
                initial={
                    "start_at": start,
                    "end_at": end,
                    "location": wizard_data.get("location", ""),
                }
            )
        else:
            form = EventWizardStep3Form()

    return render(
        request,
        "events/event_wizard.html",
        {
            "section_name": "Events",
            "step": step,
            "form": form,
            "wizard_data": wizard_data,
        },
    )


@login_required
@require_http_methods(["POST"])
def event_submit_view(request, pk):
    """Submit event for approval (creator only)."""
    event = get_object_or_404(Event, pk=pk)
    if not event.can_submit(request.user):
        return HttpResponseForbidden()
    ok, err = submit_event_for_approval(event, request.user)
    if ok:
        messages.success(request, "Event submitted for approval.")
    else:
        messages.error(request, err or "Could not submit.")
    return redirect("events:detail", pk=pk)


@teacher_required
@require_http_methods(["GET", "POST"])
def event_review_view(request, pk):
    """Admin/Teacher review panel: approve or reject with comment."""
    event = get_object_or_404(Event.objects.select_related("created_by", "policy"), pk=pk)
    if event.status != EventStatus.PENDING:
        messages.info(request, "This event is not pending review.")
        return redirect("events:detail", pk=pk)
    logs = event.approval_logs.select_related("changed_by").order_by("-created_at")  # type: ignore[union-attr]
    if request.method == "POST":
        form = EventApproveRejectForm(request.POST)
        if form.is_valid():
            action = form.cleaned_data["action"]
            comment = (form.cleaned_data.get("comment") or "").strip()
            if action == "approve":
                ok, err = approve_event(event, request.user, comment)
                if ok:
                    messages.success(request, "Event approved.")
                    return redirect("events:detail", pk=pk)
                messages.error(request, err or "Could not approve.")
            else:
                ok, err = reject_event(event, request.user, comment)
                if ok:
                    messages.success(request, "Event rejected.")
                    return redirect("events:detail", pk=pk)
                messages.error(request, err or "Could not reject.")
        else:
            messages.error(request, "Please fix the form errors.")
    else:
        form = EventApproveRejectForm(initial={"action": "approve"})
    return render(
        request,
        "events/event_review.html",
        {
            "section_name": "Events",
            "event": event,
            "form": form,
            "approval_logs": logs,
        },
    )


@teacher_required
@require_safe
def event_review_list_view(request):
    """List of events pending review (Admin/Teacher)."""
    pending = (
        Event.objects.filter(status=EventStatus.PENDING)
        .select_related("created_by")
        .order_by("-updated_at")
    )
    return render(
        request,
        "events/event_review_list.html",
        {
            "section_name": "Events",
            "pending_events": pending,
        },
    )
