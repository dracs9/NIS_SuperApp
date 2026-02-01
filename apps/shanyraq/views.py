from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_http_methods

from . import services
from .models import ActivitySubmission, Shanyraq, ShanyraqMembership, SourceType, XPLedger
from .services import leaderboard_shanyraqs, leaderboard_students, user_contribution_breakdown

User = get_user_model()


@require_http_methods(["GET"])
def leaderboard_view(request):
    """Leaderboard page: top shanyraqs and top students."""
    shanyraqs = leaderboard_shanyraqs(limit=30)
    students = leaderboard_students(limit=50)
    return render(
        request,
        "shanyraq/leaderboard.html",
        {
            "section_name": "Leaderboard",
            "leaderboard_shanyraqs": shanyraqs,
            "leaderboard_students": students,
        },
    )


@require_http_methods(["GET"])
def shanyraq_detail_view(request, slug):
    """Shanyraq profile/detail page: info, members, recent transactions."""
    shanyraq = get_object_or_404(Shanyraq, slug=slug)
    members = leaderboard_students(limit=50, shanyraq=shanyraq)
    recent = (
        XPLedger.objects.filter(user__profile__shanyraq=shanyraq)
        .select_related("user", "approved_by")
        .order_by("-created_at")[:20]
    )
    return render(
        request,
        "shanyraq/shanyraq_detail.html",
        {
            "section_name": "Shanyraq",
            "shanyraq": shanyraq,
            "members": members,
            "recent_transactions": recent,
        },
    )


@require_http_methods(["GET"])
def ledger_view(request):
    """Ledger table with filters: user, shanyraq, source_type, date range."""
    qs = XPLedger.objects.select_related("user", "approved_by").order_by("-created_at")

    user_id = request.GET.get("user")
    if user_id:
        qs = qs.filter(user_id=user_id)
    shanyraq_id = request.GET.get("shanyraq")
    if shanyraq_id:
        qs = qs.filter(user__profile__shanyraq_id=shanyraq_id)
    source_type = request.GET.get("source_type")
    if source_type and source_type in dict(SourceType.choices):
        qs = qs.filter(source_type=source_type)

    transactions = qs[:200]
    shanyraqs = Shanyraq.objects.all().order_by("name")
    try:
        filter_shanyraq_id_int = int(shanyraq_id) if shanyraq_id else None
    except (ValueError, TypeError):
        filter_shanyraq_id_int = None
    return render(
        request,
        "shanyraq/ledger.html",
        {
            "section_name": "Ledger",
            "transactions": transactions,
            "shanyraqs": shanyraqs,
            "source_types": SourceType.choices,
            "filter_user_id": user_id,
            "filter_shanyraq_id": shanyraq_id,
            "filter_shanyraq_id_int": filter_shanyraq_id_int,
            "filter_source_type": source_type,
        },
    )


@require_http_methods(["GET"])
def user_contribution_view(request, user_id):
    """User contribution breakdown: points by source_type and ledger list."""
    user = get_object_or_404(User, pk=user_id)
    profile = user.get_profile()
    breakdown = user_contribution_breakdown(user)
    transactions = (
        XPLedger.objects.filter(user=user)
        .select_related("user__profile__shanyraq", "approved_by")
        .order_by("-created_at")[:100]
    )
    return render(
        request,
        "shanyraq/user_contribution.html",
        {
            "section_name": "Contribution",
            "profile_user": user,
            "profile": profile,
            "breakdown": breakdown,
            "transactions": transactions,
        },
    )
