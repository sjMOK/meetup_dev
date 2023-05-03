from django.urls import path

from .views import login_view, logout_view, change_password


urlpatterns = [
    path('/login', login_view),
    path('/logout', logout_view),
    path('/password', change_password),
]
