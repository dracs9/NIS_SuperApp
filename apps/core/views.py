from datetime import timedelta

from django.db.models import ExpressionWrapper, F, IntegerField
from django.utils import timezone
from django.views.generic import TemplateView

from apps.accounts.models import UserProfile
from apps.events.models import Event
from apps.notifications.models import Notification
from apps.season.models import Quest, UserQuestProgress

from .mixins import BaseTemplateMixin


class HomeView(BaseTemplateMixin, TemplateView):
    template_name = "core/home.html"
    section_name = "Home"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        if user.is_authenticated:
            # 1. User profile
            user_profile = user.get_profile()
            context["user_profile"] = user_profile

            # 2. Weekly Hall of Fame (top 5 students by weekly growth)
            weekly_hall_of_fame = (
                UserProfile.objects.filter(NIS_points__gt=0)
                .values("user")
                .annotate(
                    delta_points=ExpressionWrapper(F("NIS_points"), output_field=IntegerField())
                )
                .order_by("-delta_points")[:5]
            )

            # Convert to UserProfile objects
            hall_of_fame_ids = [item["user"] for item in weekly_hall_of_fame]
            hall_of_fame_profiles = UserProfile.objects.filter(
                user_id__in=hall_of_fame_ids
            ).select_related("user")

            # Reconstruct with delta points
            hall_of_fame_with_delta = []
            for profile in hall_of_fame_profiles:
                delta = next(
                    (
                        item["delta_points"]
                        for item in weekly_hall_of_fame
                        if item["user"] == profile.user_id
                    ),
                    0,
                )
                hall_of_fame_with_delta.append({"user": profile.user, "delta_points": delta})

            context["weekly_hall_of_fame"] = sorted(
                hall_of_fame_with_delta, key=lambda x: x["delta_points"], reverse=True
            )[:5]

            # 3. Upcoming events (next 7 days, approved)
            now = timezone.now()
            context["upcoming_events"] = Event.objects.filter(
                start_at__gte=now, start_at__lte=(now + timedelta(days=7)), status="approved"
            ).order_by("start_at")[:6]

            # 4. Active quests for user
            active_quests = Quest.objects.filter(is_active=True)[:5]
            quest_progress_map = {}

            for quest in active_quests:
                progress, _ = UserQuestProgress.objects.get_or_create(
                    user=user, quest=quest, defaults={"current_progress": 0}
                )
                quest_progress_map[quest.id] = progress

            # Attach progress to quests for template access
            for quest in active_quests:
                quest.progress = quest_progress_map[quest.id]

            context["active_quests"] = active_quests
            try:
                context["unread_notifications_count"] = Notification.objects.filter(
                    user=user, is_read=False
                ).count()
            except Exception:
                context["unread_notifications_count"] = 0

        return context
