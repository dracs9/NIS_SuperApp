from django.urls import path

from . import views

app_name = "people"

urlpatterns = [
    path("search/", views.PeopleSearchView.as_view(), name="search"),
]
