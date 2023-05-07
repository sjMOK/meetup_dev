from django.urls import path
from .views import RoomView, RoomRetrieveView

urlpatterns = [
    path("", RoomView.as_view({"get": "list", "post": "create"})),
    path("/<int:pk>", RoomRetrieveView.as_view({"get": "retrieve"})),
]
