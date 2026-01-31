"""
Load settings based on DJANGO_ENV (development, production, test).
"""
import os

env = os.environ.get('DJANGO_ENV', 'development')

if env == 'production':
    from .production import *  # noqa: F401, F403
elif env == 'test':
    from .test import *  # noqa: F401, F403
else:
    from .development import *  # noqa: F401, F403
