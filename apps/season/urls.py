from django.urls import path

from . import views

app_name = "season"

urlpatterns = [
    path("", views.season_dashboard_view, name="dashboard"),
    path("quests/", views.quest_list_view, name="quest_list"),
    path("<int:season_id>/claim/<int:level>/", views.claim_reward_view, name="claim_reward"),
]
