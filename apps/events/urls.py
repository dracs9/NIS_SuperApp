from django.urls import path

from . import views

app_name = "events"

urlpatterns = [
    path("", views.event_list_view, name="list"),
    path("create/<int:step>/", views.event_wizard_view, name="wizard"),
    path("review/", views.event_review_list_view, name="review_list"),
    path("<int:pk>/", views.event_detail_view, name="detail"),
    path("<int:pk>/submit/", views.event_submit_view, name="submit"),
    path("<int:pk>/review/", views.event_review_view, name="review"),
]
