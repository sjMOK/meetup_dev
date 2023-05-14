from django.urls import path
from .views import (
    ReservationRetrievView,
    ReservationView,
    RoomView,
    DailyReservationCardView,
)

urlpatterns = [
    path("", RoomView.as_view({"get": "list", "post": "create"})),
    path(
        "<int:id>",
        RoomView.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
    ),
    path(
        "/daily-reservation-card",
        DailyReservationCardView.as_view({"get": "list", "post": "create"}),
    ),
    path(
        "/daily-reservation-card/<int:pk>",
        DailyReservationCardView.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
    ),
    path(
        "/reservations/<int:pk>",
        ReservationRetrievView.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
    ),
    path(
        "/reservations/<int:card_id>/<str:time>",
        ReservationView.as_view({"get": "list", "post": "create"}),
    ),
]
