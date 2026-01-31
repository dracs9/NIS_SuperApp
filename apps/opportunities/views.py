"""
Opportunities app: wall, filters, detail with prep checklist.
"""
from django.db.models import Q
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_safe

from .models import Opportunity


@require_safe
def opportunity_wall_view(request):
    """Opportunities wall with filters by subject and deadline."""
    qs = Opportunity.objects.filter(is_active=True).prefetch_related("tags").order_by("-deadline", "-created_at")
    subject = request.GET.get("subject", "").strip()
    deadline_filter = request.GET.get("deadline", "")
    if subject:
        qs = qs.filter(Q(subject__icontains=subject) | Q(title__icontains=subject) | Q(description__icontains=subject))
    if deadline_filter == "upcoming":
        from django.utils import timezone
        today = timezone.now().date()
        qs = qs.filter(deadline__gte=today)
    elif deadline_filter == "past":
        from django.utils import timezone
        today = timezone.now().date()
        qs = qs.filter(deadline__lt=today)
    opportunities = list(qs[:100])
    return render(
        request,
        "opportunities/wall.html",
        {
            "section_name": "Opportunities",
            "opportunities": opportunities,
            "filter_subject": subject,
            "filter_deadline": deadline_filter,
        },
    )


@require_safe
def opportunity_detail_view(request, pk):
    """Opportunity detail with prep checklist."""
    opportunity = get_object_or_404(
        Opportunity.objects.prefetch_related("tags").filter(is_active=True),
        pk=pk,
    )
    prep_items = opportunity.get_prep_items()
    return render(
        request,
        "opportunities/detail.html",
        {
            "section_name": "Opportunities",
            "opportunity": opportunity,
            "prep_items": prep_items,
        },
    )
