import json

from django.contrib.sessions.backends.db import SessionStore

from rest_framework.test import APITestCase
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN

from .factories import UserFactory, TEST_PASSWORD, UserTypeFactory
from ..models import User, UserType
from ..serializers import UserSerializer, UserTypeSerializer


class LoginViewTestCase(APITestCase):
    url = '/users/login'

    @classmethod
    def setUpTestData(cls):
        user_type = UserTypeFactory()
        cls.user = UserFactory(user_type=user_type)

    def test_success(self):
        response = self.client.post(self.url, {'user_no': self.user.user_no, 'password': TEST_PASSWORD}, format='json')
        body_data = json.loads(response.content)

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(body_data, UserSerializer(self.user).data)
        self.assertIn('sessionid', response.cookies)
        self.assertIn('csrftoken', response.cookies)

    def test_fail_with_wrong_credentials(self):
        response = self.client.post(self.url, {'user_no': 'user_no', 'password': 'wrong_password'}, format='json')
        body_data = json.loads(response.content)

        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)
        self.assertEqual(body_data, {'detail': 'No matching user.'})

    def test_validation_fail(self):
        response = self.client.post(self.url, {'user_no': 'user_no'}, format='json')
        self.assertContains(response, 'password', status_code=HTTP_400_BAD_REQUEST)


class LogoutViewTestCase(APITestCase):
    url = '/users/logout'

    def test(self):
        user_type = UserTypeFactory()
        user = UserFactory(user_type=user_type)
        s = SessionStore()
        
        login_response = self.client.post('/users/login', {'user_no': user.user_no, 'password': TEST_PASSWORD}, format='json')
        session_id = login_response.cookies['sessionid'].value
        self.assertTrue(s.exists(session_id))
        
        self.client.post(self.url)
        self.assertFalse(s.exists(session_id))


class GetAllUserTypeTestCase(APITestCase):
    url = '/users/types'

    def test_success(self):
        UserTypeFactory.create_batch(5)
        response = self.client.get(self.url)
        body_data = json.loads(response.content)

        self.assertListEqual(body_data, UserTypeSerializer(UserType.objects.all(), many=True).data)


class ChangePasswordTestCase(APITestCase):
    url = '/users/password'

    @classmethod
    def setUpTestData(cls):
        cls.user_raw_password = 'raw_password'
        cls.user = UserFactory(password=cls.user_raw_password)

    def test_success(self):
        request_data = {
            'current_password': self.user_raw_password,
            'new_password': 'new_password',
        }

        self.client.force_authenticate(user=self.user)
        response = self.client.patch(self.url, request_data, format='json')
        user = User.objects.get(id=self.user.id)

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertTrue(user.check_password(request_data['new_password']))

    def test_admin_user_permission_denied(self):
        admin_type = UserTypeFactory.create_admin_user_type()
        admin_user = UserFactory(user_type=admin_type)

        self.client.force_authenticate(user=admin_user)
        response = self.client.patch(self.url)

        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)

    def test_anonymous_user_permission_denied(self):
        self.client.force_authenticate(user=None)
        response = self.client.patch(self.url)

        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)


class UserViewSetTestCase(APITestCase):
    url = '/users'

    @classmethod
    def setUpTestData(cls):
        admin_user_type = UserTypeFactory.create_admin_user_type()
        cls.user_type = UserTypeFactory()

        cls.admin_user = UserFactory(user_type=admin_user_type)
        cls.user = UserFactory(user_type=cls.user_type)
        cls.dummy_user = UserFactory(user_type=cls.user_type)

    def test_get_by_admin_user(self):
        self.url += f'/{self.user.id}'

        self.client.force_authenticate(self.admin_user)
        response = self.client.get(self.url)
        body_data = json.loads(response.content)

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertDictEqual(body_data, UserSerializer(self.user).data)

    def test_get_by_normal_user(self):
        self.url += f'/{self.dummy_user.id}'

        self.client.force_authenticate(self.user)
        response = self.client.get(self.url)
        body_data = json.loads(response.content)

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertDictEqual(body_data, UserSerializer(self.user).data)

    def test_get_by_anonymous_user(self):
        self.url += f'/{self.user.id}'

        self.client.force_authenticate(user=None)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)

    def __test_pagination(self, body_data):
        self.assertTrue('count' in body_data)
        self.assertTrue('next' in body_data)
        self.assertTrue('previous' in body_data)

    def test_list_by_admin_user(self):
        self.client.force_authenticate(self.admin_user)
        response = self.client.get(self.url)
        body_data = json.loads(response.content)

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.__test_pagination(body_data)
        self.assertListEqual(body_data['results'], UserSerializer(User.objects.all(), many=True).data)

    def test_list_by_normal_user(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)

    def test_list_by_anonymous_user(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)

    def test_list_search_by_user_no(self):
        user_no = self.user.user_no
        query_params = {'user_no': user_no}

        self.client.force_authenticate(self.admin_user)
        response = self.client.get(self.url, query_params)
        body_data = json.loads(response.content)

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.__test_pagination(body_data)
        self.assertListEqual(body_data['results'], UserSerializer(User.objects.filter(user_no=user_no), many=True).data)

    def test_create(self):
        request_data = {
            'user_no': 'new_user_no',
            'password': 'password',
            'name': 'newname',
            'email': 'new@naver.com',
            'user_type': self.user_type.id,
        }
        
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(self.url, request_data, format='json')
        body_data = json.loads(response.content)
        created_user = User.objects.get(id=body_data['id'])

        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertDictEqual(body_data, UserSerializer(created_user).data)

    def test_create_by_normal_user(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)
    
    def test_create_by_anonymous_user(self):
        self.client.force_authenticate(user=None)
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)

    def test_partial_update_by_admin_user(self):
        self.url += f'/{self.user.id}'
        reqeust_data = {'name': 'newname', 'email': 'new@naver.com'}

        self.client.force_authenticate(user=self.admin_user)
        response = self.client.patch(self.url, reqeust_data, format='json')
        user = User.objects.get(id=self.user.id)

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(user.name, reqeust_data['name'])
        self.assertEqual(user.email, reqeust_data['email'])

    def test_partial_update_by_normal_user(self):
        self.url += f'/{self.dummy_user.id}'
        reqeust_data = {'name': 'newname', 'email': 'new@naver.com'}

        self.client.force_authenticate(user=self.user)
        response = self.client.patch(self.url, reqeust_data, format='json')
        user = User.objects.get(id=self.user.id)

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(user.name, reqeust_data['name'])
        self.assertEqual(user.email, reqeust_data['email'])

    def test_normal_user_try_to_update_non_patchable_field(self):
        self.url += f'/{self.user.id}'
        reqeust_data = {'user_no': 'new_user_no', 'name': 'newname', 'email': 'new@naver.com'}

        self.client.force_authenticate(user=self.user)
        response = self.client.patch(self.url, reqeust_data, format='json')
        body_data = json.loads(response.content)

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(body_data, 'The data contains fields cannot be updated.')

    def test_admin_user_try_to_update_non_patchable_field(self):
        self.url += f'/{self.user.id}'
        reqeust_data = {'user_no': 'new_user_no', 'name': 'newname', 'email': 'new@naver.com'}

        self.client.force_authenticate(user=self.admin_user)
        response = self.client.patch(self.url, reqeust_data, format='json')

        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_partial_update_by_anonymous_user(self):
        self.url += f'/{self.user.id}'
        reqeust_data = {'name': 'newname', 'email': 'new@naver.com'}

        self.client.force_authenticate(user=None)
        response = self.client.patch(self.url, reqeust_data, format='json')

        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)

    def test_delete_by_admin_user(self):
        self.url += f'/{self.user.id}'

        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(id=self.user.id).exists())

    def test_delete_by_normal_user(self):
        self.url += f'/{self.dummy_user.id}'

        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(id=self.user.id).exists())

    def test_delete_by_anonymous_user(self):
        self.url += f'/{self.user.id}'

        self.client.force_authenticate(user=None)
        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)
