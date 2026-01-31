from django.urls import path

from . import views

app_name = "teams"

urlpatterns = [
    path("", views.team_feed_view, name="feed"),
    path("create/", views.team_create_view, name="create"),
    path("<int:pk>/", views.team_detail_view, name="detail"),
    path("<int:pk>/apply/", views.team_apply_view, name="apply"),
    path("<int:pk>/invite/", views.team_invite_view, name="invite"),
    path("<int:pk>/request/<int:request_id>/accept/", views.team_request_accept_view, name="request_accept"),
    path("<int:pk>/request/<int:request_id>/reject/", views.team_request_reject_view, name="request_reject"),
]
