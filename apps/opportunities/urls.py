from django.urls import path

from . import views

app_name = "opportunities"

urlpatterns = [
    path("", views.opportunity_wall_view, name="wall"),
    path("<int:pk>/", views.opportunity_detail_view, name="detail"),
]
