from django.urls import path

from . import views

app_name = "shanyraq"

urlpatterns = [
    path("", views.leaderboard_view, name="leaderboard"),
    path("ledger/", views.ledger_view, name="ledger"),
    path("<slug:slug>/", views.shanyraq_detail_view, name="detail"),
    path("user/<int:user_id>/contribution/", views.user_contribution_view, name="user_contribution"),
]
