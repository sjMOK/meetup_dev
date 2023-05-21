from django.urls import path

from rest_framework.authtoken.views import obtain_auth_token

from .views import login_view, logout_view, get_all_user_type, change_password


urlpatterns = [
    # path('/login', login_view),
    path('/logout', logout_view),
    path('/types', get_all_user_type),
    path('/password', change_password),
    path('/login', obtain_auth_token),
]
