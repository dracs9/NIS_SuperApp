"""
Common view mixins for auth and context.
"""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import TemplateView


class LoginRequiredMixinView(LoginRequiredMixin):
    """Use for class-based views that require login."""
    login_url = '/accounts/login/'


class StaffRequiredMixin(LoginRequiredMixin):
    """Require staff (admin) user."""
    login_url = '/accounts/login/'

    def dispatch(self, request, *args, **kwargs):
        # Use hasattr to safely check if user has 'is_staff' attribute
        if not getattr(request.user, "is_staff", False):
            from django.http import HttpResponseForbidden
            return HttpResponseForbidden()
        return super().dispatch(request, *args, **kwargs)


class BaseTemplateMixin:
    """Inject common template context (e.g. section name)."""
    section_name = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.section_name is not None:
            context['section_name'] = self.section_name
        return context



class SuccessMessageMixinView(SuccessMessageMixin):
    """Add success_message for form views."""
    pass
