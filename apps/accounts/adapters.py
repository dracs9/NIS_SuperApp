"""
Custom allauth adapter: redirect, school email validation.
"""
from django.conf import settings
from django.urls import reverse

from allauth.account.adapter import DefaultAccountAdapter


class ShanyraqAccountAdapter(DefaultAccountAdapter):
    def get_login_redirect_url(self, request):
        """Redirect to home (dashboard) after login, or respect ?next=."""
        next_url = request.GET.get("next")
        if next_url:
            return next_url
        return getattr(settings, "LOGIN_REDIRECT_URL", "/")

    def get_signup_redirect_url(self, request):
        """Redirect after signup (e.g. onboarding)."""
        next_url = request.GET.get("next")
        if next_url:
            return next_url
        return getattr(settings, "LOGIN_REDIRECT_URL", "/")
