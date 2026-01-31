"""
Production settings.
"""
from .base import *  # noqa: F401, F403

DEBUG = False
# ALLOWED_HOSTS set from env in base
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
