"""
Template tags for role-based UI.
Usage: {% load role_tags %} ... {% if user|has_role:"admin" %} ...
"""
from django import template
from django.contrib.auth import get_user_model

register = template.Library()
User = get_user_model()


@register.filter
def has_role(user, role_code):
    """Return True if user has the given role (e.g. 'admin', 'teacher')."""
    if not user or not user.is_authenticated:
        return False
    return getattr(user, "role", None) == role_code


@register.filter
def role_display(user):
    """Return human-readable role label for user."""
    if not user or not user.is_authenticated:
        return ""
    from apps.accounts.models import Role
    return dict(Role.choices).get(getattr(user, "role", ""), "")
