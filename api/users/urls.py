from django.urls import path

from rest_framework.authtoken.views import obtain_auth_token

from .views import get_all_user_type, change_password, UserCsvCreateView


urlpatterns = [
    path('/login', obtain_auth_token),
    path('/types', get_all_user_type),
    path('/password', change_password),
    path('/bulk', UserCsvCreateView.as_view()),
]
