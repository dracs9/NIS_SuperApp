"""
Role-based access: decorators and mixins.
"""
from functools import wraps

from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import resolve_url
from django.utils.decorators import method_decorator

from .models import Role


def role_required(*roles, login_url=None, redirect_field_name=REDIRECT_FIELD_NAME):
    """
    Decorator: require user to be logged in and have one of the given roles.
    Roles are Role enum values, e.g. Role.ADMIN, Role.TEACHER.
    """
    if not roles:
        raise ValueError("At least one role must be specified")

    role_codes = {r if isinstance(r, str) else r.value for r in roles}

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                from django.contrib.auth.views import redirect_to_login
                path = request.get_full_path()
                return redirect_to_login(path, resolve_url(login_url or "/accounts/login/"), redirect_field_name)
            if request.user.role not in role_codes:
                return HttpResponseForbidden()
            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator


def admin_required(view_func):
    """Require role Admin."""
    return login_required(role_required(Role.ADMIN)(view_func))


def teacher_required(view_func):
    """Require role Teacher or Admin."""
    return login_required(role_required(Role.TEACHER, Role.ADMIN)(view_func))


def student_council_required(view_func):
    """Require role Student Council, Teacher, or Admin."""
    return login_required(role_required(Role.STUDENT_COUNCIL, Role.TEACHER, Role.ADMIN)(view_func))


def event_creator_required(view_func):
    """Require role Student Council or Admin (only they can create events)."""
    return login_required(role_required(Role.STUDENT_COUNCIL, Role.ADMIN)(view_func))


def shanyraq_leader_required(view_func):
    """Require role Shanyraq Leader, Student Council, Teacher, or Admin."""
    return login_required(
        role_required(Role.SHANYRAQ_LEADER, Role.STUDENT_COUNCIL, Role.TEACHER, Role.ADMIN)(view_func)
    )


class RoleRequiredMixin:
    """CBV mixin: require one of the given roles. Set .required_roles = [Role.ADMIN, ...]."""
    required_roles = []
    login_url = "/accounts/login/"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(request.get_full_path(), self.login_url)
        if self.required_roles and request.user.role not in [r.value if hasattr(r, "value") else r for r in self.required_roles]:
            return HttpResponseForbidden()
        return super(RoleRequiredMixin, self).dispatch(request, *args, **kwargs)


class AdminRequiredMixin(RoleRequiredMixin):
    required_roles = [Role.ADMIN]


class TeacherRequiredMixin(RoleRequiredMixin):
    required_roles = [Role.TEACHER, Role.ADMIN]
