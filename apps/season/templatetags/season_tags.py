"""Template tags for season app."""
from django import template
from django.template.defaulttags import IfNode

register = template.Library()


@register.inclusion_tag("season/quest_progress.html", takes_context=True)
def quest_progress(context, quest, user):
    """Render quest progress bar."""
    progress = None
    if user and user.is_authenticated and hasattr(quest, "_user_progress") and quest._user_progress:
        progress = quest._user_progress
    return {
        "quest": quest,
        "progress": progress,
        "user": user,
    }
