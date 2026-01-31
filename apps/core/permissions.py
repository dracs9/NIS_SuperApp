"""
Custom permission classes and role-based access.
Use with view mixins or in view dispatch.
"""
from django.core.exceptions import PermissionDenied


def user_is_moderator(user):
    if not user or not user.is_authenticated:
        return False
    return getattr(user, 'is_moderator', False)


def user_is_admin(user):
    if not user or not user.is_authenticated:
        return False
    return getattr(user, 'is_admin', False)


def user_owns_or_moderator(user, obj):
    if not user or not user.is_authenticated:
        return False
    if user_is_moderator(user):
        return True
    owner = getattr(obj, 'user', None) or getattr(obj, 'owner', None) or getattr(obj, 'created_by', None)
    return owner == user


class IsModeratorMixin:
    """Mixin: require moderator or admin role."""
    def dispatch(self, request, *args, **kwargs):
        if not user_is_moderator(request.user):
            raise PermissionDenied()
        return super(IsModeratorMixin, self).dispatch(request, *args, **kwargs)


class IsAdminMixin:
    """Mixin: require admin role."""
    def dispatch(self, request, *args, **kwargs):
        if not user_is_admin(request.user):
            raise PermissionDenied()
        return super().dispatch(request, *args, **kwargs)
