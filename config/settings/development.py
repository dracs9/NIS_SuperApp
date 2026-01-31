"""
Development settings.
"""
from .base import *  # noqa: F401, F403

DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '[::1]']

# Optional: disable WhiteNoise compression in dev for faster reload
# STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
