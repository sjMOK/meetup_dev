from django.urls import path
from .views import (
    NotiveView,
    ReservationView,
    RoomView,
)

urlpatterns = [
    path("", RoomView.as_view({"get": "list", "post": "create"})),
    path(
        "/<int:id>",
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
        "/reservations",
        ReservationView.as_view({"get": "list", "post": "create"}),
    ),
    path(
        "/reservations/<int:pk>",
        ReservationView.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
    ),
    path(
        "/notice",
        NotiveView.as_view({"get": "list", "post": "create"}),
    ),
    path(
        "/notice/<int:pk>",
        NotiveView.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
    ),
]
