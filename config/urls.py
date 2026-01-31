"""
URL configuration for NIS_SuperApp.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

# Import moderation admin
from apps.moderation.admin import moderation_admin

urlpatterns = [
    path("admin/", admin.site.urls),
    path("moderation/", moderation_admin.urls),  # Custom moderation admin
    path("accounts/", include("apps.accounts.urls")),
    path("accounts/", include("allauth.urls")),
    path("shanyraq/", include("apps.shanyraq.urls")),
    path("events/", include("apps.events.urls")),
    path("spaces/", include("apps.spaces.urls")),
    path("season/", include("apps.season.urls")),
    path("opportunities/", include("apps.opportunities.urls")),
    path("teams/", include("apps.teams.urls")),
    path("", include("apps.core.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
