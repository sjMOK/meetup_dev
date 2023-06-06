from django.urls import path
from .views import (
    CommentView,
    NoticeView,
    ReportView,
)

urlpatterns = [
    path(
        "/notice",
        NoticeView.as_view({"get": "list", "post": "create"}),
    ),
    path(
        "/notice/<int:pk>",
        NoticeView.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
    ),
    path(
        "/report",
        ReportView.as_view({"get": "list", "post": "create"}),
    ),
    path(
        "/report/<int:pk>",
        ReportView.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
    ),
    path(
        "/comment",
        CommentView.as_view({"get": "list", "post": "create"}),
    ),
    path(
        "/comment/<int:pk>",
        CommentView.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
    ),
]
