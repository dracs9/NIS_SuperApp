from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Case, Count, F, IntegerField, Q, Value, When
from django.shortcuts import render
from django.views.generic import TemplateView

from apps.accounts.models import UserProfile
from apps.skills.models import Skill, UserSkill


class PeopleSearchView(LoginRequiredMixin, TemplateView):
    template_name = "people/search.html"
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get query parameters
        query = self.request.GET.get("q", "").strip()
        class_filter = self.request.GET.get("class", "").strip()
        shanyraq_filter = self.request.GET.get("shanyraq", "").strip()
        skill_filters = self.request.GET.getlist("skills")
        level_filter = self.request.GET.get("level", "").strip()
        activity_min = self.request.GET.get("activity_min", "").strip()

        # Base queryset
        profiles = (
            UserProfile.objects.select_related("user", "shanyraq")
            .prefetch_related("user__user_skills__skill")
            .filter(user__is_active=True)
        )

        # Apply filters
        if query:
            profiles = profiles.filter(
                Q(user__username__icontains=query)
                | Q(user__email__icontains=query)
                | Q(full_name__icontains=query)
            )

        if class_filter:
            profiles = profiles.filter(class_name__iexact=class_filter)

        if shanyraq_filter:
            profiles = profiles.filter(shanyraq__name__iexact=shanyraq_filter)

        if skill_filters:
            # Filter users who have any of the selected skills
            skill_ids = [int(sid) for sid in skill_filters if sid.isdigit()]
            if skill_ids:
                profiles = profiles.filter(user__user_skills__skill_id__in=skill_ids).distinct()

        if level_filter:
            profiles = profiles.filter(user__user_skills__level=level_filter).distinct()

        if activity_min and activity_min.isdigit():
            profiles = profiles.filter(NIS_points__gte=int(activity_min))

        # Annotate with skill match count for sorting
        if skill_filters:
            skill_ids = [int(sid) for sid in skill_filters if sid.isdigit()]
            if skill_ids:
                skill_match_count = Count(
                    "user__user_skills",
                    filter=Q(user__user_skills__skill_id__in=skill_ids),
                    distinct=True,
                )
            else:
                skill_match_count = Value(0)
        else:
            skill_match_count = Value(0)

        profiles = profiles.annotate(
            skill_match_count=skill_match_count, total_points=F("NIS_points") + F("shanyraq_points")
        ).order_by(
            "-skill_match_count",  # Prioritize skill matches
            "-NIS_points",  # Then XP points
            "-total_points",  # Then total points
        )

        # Pagination
        paginator = Paginator(profiles, self.paginate_by)
        page_number = self.request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        # Available filter options
        available_classes = (
            UserProfile.objects.exclude(class_name="")
            .values_list("class_name", flat=True)
            .distinct()
            .order_by("class_name")
        )

        available_shanyraqs = (
            UserProfile.objects.exclude(shanyraq__isnull=True)
            .select_related("shanyraq")
            .values_list("shanyraq__name", flat=True)
            .distinct()
            .order_by("shanyraq__name")
        )

        available_skills = Skill.objects.filter(is_active=True).order_by("category", "name")

        context.update(
            {
                "page_obj": page_obj,
                "query": query,
                "class_filter": class_filter,
                "shanyraq_filter": shanyraq_filter,
                "skill_filters": skill_filters,
                "level_filter": level_filter,
                "activity_min": activity_min,
                "available_classes": available_classes,
                "available_shanyraqs": available_shanyraqs,
                "available_skills": available_skills,
                "skill_levels": UserSkill.LEVEL_CHOICES,
            }
        )

        return context
