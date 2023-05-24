from django.urls import path

from rest_framework.authtoken.views import obtain_auth_token

from .views import get_all_user_type, get_all_user_departments, change_password, google_login, google_callback, google_revoke, UserCsvCreateView


urlpatterns = [
    path('/login', obtain_auth_token),
    path('/types', get_all_user_type),
    path('/departments', get_all_user_departments),
    path('/password', change_password),
    path('/bulk', UserCsvCreateView.as_view()),
    path('/google-login', google_login),
    path('/google-callback', google_callback),
    path('/google-revoke', google_revoke),
]
