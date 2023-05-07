from django.urls import path
from .views import RoomView, RoomDetailView

urlpatterns = [
    path("", RoomView.as_view({"get": "list", "post": "create"})),
    path(
        "/<int:pk>",
        RoomDetailView.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
    ),
]
