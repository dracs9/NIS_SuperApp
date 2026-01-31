from django.urls import path

from . import views

app_name = "spaces"

urlpatterns = [
    path("", views.space_list_view, name="list"),
    path("my-bookings/", views.my_bookings_view, name="my_bookings"),
    path("booking/create/", views.booking_create_view, name="booking_create"),
    path("booking/create/<int:space_id>/", views.booking_create_view, name="booking_create_for_space"),
    path("booking/<int:pk>/", views.booking_detail_view, name="booking_detail"),
    path("booking/<int:pk>/cancel/", views.booking_cancel_view, name="booking_cancel"),
    path("booking/<int:pk>/review/", views.booking_review_view, name="booking_review"),
    path("review/", views.booking_review_list_view, name="review_list"),
    path("<int:pk>/", views.space_detail_view, name="detail"),
]
