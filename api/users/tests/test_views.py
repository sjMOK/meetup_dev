import json

from django.contrib.sessions.backends.db import SessionStore

from rest_framework.test import APITestCase
from rest_framework.status import HTTP_200_OK, HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST

from ..models import User, UserType


class LoginViewTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        user_type = UserType.objects.create(name='admin', possible_duration=0)
        cls.user = User.objects.create_user(username='username', name='name', email='email@naver.com', password='password', user_type=user_type)

    def test_success(self):
        response = self.client.post('/users/login', {'username': 'username', 'password': 'password'}, format='json')
        body_data = json.loads(response.content)

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(body_data, str(self.user))
        self.assertIn('sessionid', response.cookies)
        self.assertIn('csrftoken', response.cookies)

    def test_fail_with_wrong_credentials(self):
        response = self.client.post('/users/login', {'username': 'username', 'password': 'wrong_password'}, format='json')
        body_data = json.loads(response.content)

        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)
        self.assertEqual(body_data, {'detail': 'No matching user.'})

    def test_validation_fail(self):
        response = self.client.post('/users/login', {'username': 'username'}, format='json')
        self.assertContains(response, 'password', status_code=HTTP_400_BAD_REQUEST)


class LogoutViewTestCase(APITestCase):
    def test(self):
        user_type = UserType.objects.create(name='admin', possible_duration=0)
        User.objects.create_user(username='username', name='name', email='email@naver.com', password='password', user_type=user_type)
        s = SessionStore()
        
        login_response = self.client.post('/users/login', {'username': 'username', 'password': 'password'}, format='json')
        session_id = login_response.cookies['sessionid'].value
        self.assertTrue(s.exists(session_id))
        
        self.client.post('/users/logout')
        self.assertFalse(s.exists(session_id))
