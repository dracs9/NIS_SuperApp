"""
Middleware: redirect authenticated users away from login/signup.
"""
from django.shortcuts import redirect


class RedirectAuthenticatedUserMiddleware:
    """
    If user is authenticated and requests login/signup/password_reset,
    redirect to LOGIN_REDIRECT_URL (e.g. home/dashboard).
    """
    paths = ("/accounts/login/", "/accounts/signup/", "/accounts/password/reset/")

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and request.path.rstrip("/") in [p.rstrip("/") for p in self.paths]:
            from django.conf import settings
            return redirect(settings.LOGIN_REDIRECT_URL)
        return self.get_response(request)
