from django.urls import path

from .views import login_view, logout_view, get_all_user_type, change_password


urlpatterns = [
    path('/login', login_view),
    path('/logout', logout_view),
    path('/types', get_all_user_type),
    path('/password', change_password),
]
