"""
Opportunities app: olympiads, projects, and student opportunities.
"""
from django.conf import settings
from django.db import models
from django.utils import timezone


class OpportunityTag(models.Model):
    """Tag for categorizing opportunities (e.g. Math, Science, Regional)."""
    name = models.CharField(max_length=64)
    slug = models.SlugField(max_length=64, unique=True)

    class Meta:
        verbose_name = "opportunity tag"
        verbose_name_plural = "opportunity tags"
        ordering = ["name"]

    def __str__(self):
        return self.name


class OpportunityType(models.TextChoices):
    OLYMPIAD = "olympiad", "Olympiad"
    PROJECT = "project", "Project"
    COMPETITION = "competition", "Competition"
    PROGRAM = "program", "Program"
    OTHER = "other", "Other"


class Opportunity(models.Model):
    """Olympiad, project, or other student opportunity."""
    title = models.CharField(max_length=255)
    opportunity_type = models.CharField(
        max_length=20,
        choices=OpportunityType.choices,
        default=OpportunityType.OTHER,
    )
    subject = models.CharField(max_length=128, blank=True, help_text="e.g. Mathematics, Physics")
    description = models.TextField(blank=True)
    organization = models.CharField(max_length=255, blank=True)
    deadline = models.DateField(null=True, blank=True)
    url = models.URLField(blank=True, help_text="External link for more info")
    tags = models.ManyToManyField(
        OpportunityTag,
        related_name="opportunities",
        blank=True,
    )
    prep_checklist = models.TextField(
        blank=True,
        help_text="One item per line: prepare documents, register online, etc.",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_opportunities",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "opportunity"
        verbose_name_plural = "opportunities"
        ordering = ["-deadline", "-created_at"]

    def __str__(self):
        return self.title

    @property
    def is_past_deadline(self):
        if not self.deadline:
            return False
        return timezone.now().date() > self.deadline

    def get_prep_items(self):
        """Return prep checklist as list of non-empty lines."""
        if not self.prep_checklist:
            return []
        return [line.strip() for line in self.prep_checklist.splitlines() if line.strip()]
