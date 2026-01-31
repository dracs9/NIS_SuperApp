"""
Django settings entry. Set DJANGO_ENV=development|production|test.
Defaults to development if unset.
"""
import os

_env = os.environ.get('DJANGO_ENV', 'development')

if _env == 'production':
    from config.settings.production import *  # noqa: F401, F403
elif _env == 'test':
    from config.settings.test import *  # noqa: F401, F403
else:
    from config.settings.development import *  # noqa: F401, F403
