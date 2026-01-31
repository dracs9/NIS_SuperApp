from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("profile/", views.profile_view, name="profile"),
    path("profile/edit/", views.profile_edit_view, name="profile_edit"),
    path("profile/<int:user_id>/", views.profile_by_id_view, name="profile_by_id"),
    path("onboarding/save/", views.onboarding_save_view, name="onboarding_save"),
    path("theme/save/", views.theme_save_view, name="theme_save"),
]
