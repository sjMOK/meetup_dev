from django.utils import timezone
from django.contrib.auth.hashers import check_password

from rest_framework.test import APITestCase

from freezegun import freeze_time

from ..models import UserManager, User, UserType


FREEZE_TIME = '2022-12-31 23:59:59'


class UserMangerTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        user_type = UserType.objects.create(id=1, name='admin', possible_duration=0)
        cls.data = {
            'username': 'username',
            'name': 'name',
            'email': 'email@SeJong.ac.kr',
            'user_type': user_type,
            'password': 'password',
        }

        cls.user = User.objects.create_user(**cls.data)

    def test_email_is_normalized(self):
        normalized_email = UserManager.normalize_email(self.data['email'])
        self.assertEqual(self.user.email, normalized_email)

    def test_password_is_hashed(self):
        raw_password = self.data['password']
        self.assertTrue(check_password(raw_password, self.user.password))

    def test_create_raise_exception(self):
        self.data['username'] += '_test'

        self.assertRaisesMessage(
            Exception,
            'You cannot call .crete() method. Call create_user() instead.',
            User.objects.create,
            **self.data
        )


class UserTestCase(APITestCase):
    @classmethod
    @freeze_time(FREEZE_TIME)
    def setUpTestData(cls):
        user_type = UserType.objects.create(id=1, name='admin', possible_duration=0)
        cls.user = User.objects.create_user(username='username', password='password', name='name', email='email@sejong.ac.kr', user_type=user_type)

    def test_pk_is_id(self):
        pk_name = User._meta.pk.name
        self.assertEqual(pk_name, 'id')

    def test_username_is_unique(self):
        is_unique = self.user._meta.get_field('username').unique
        self.assertTrue(is_unique)

    def test_username_max_length(self):
        max_length = self.user._meta.get_field('username').max_length
        self.assertEqual(max_length, 45)

    def test_name_max_length(self):
        max_length = self.user._meta.get_field('name').max_length
        self.assertEqual(max_length, 45)

    def test_is_active_default(self):
        self.assertTrue(self.user.is_active)

    @freeze_time(FREEZE_TIME)
    def test_date_joined_default(self):
        self.assertEqual(self.user.date_joined, timezone.now())

    def test_username_field(self):
        username_field = self.user.get_username()
        self.assertEqual(username_field, 'username')


class UserTypeTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin_user_type = UserType.objects.create(id=1, name='admin', possible_duration=0)
        cls.faculty_user_type = UserType.objects.create(id=2, name='faculty', possible_duration=12)
        cls.postgraduate_user_type = UserType.objects.create(id=3, name='postgraduate', possible_duration=2)
        cls.undergraduate_user_type = UserType.objects.create(id=4, name='undergraduate', possible_duration=1)

    def test_pk_is_id(self):
        pk_name = UserType._meta.pk.name
        self.assertEqual(pk_name, 'id')

    def test_name_max_length(self):
        max_length = self.admin_user_type._meta.get_field('name').max_length
        self.assertEqual(max_length, 20)

    def test_is_admin(self):
        self.assertTrue(self.admin_user_type.is_admin())
        self.assertFalse(self.faculty_user_type.is_admin())
        self.assertFalse(self.postgraduate_user_type.is_admin())
        self.assertFalse(self.undergraduate_user_type.is_admin())

    def test_is_faculty(self):
        self.assertFalse(self.admin_user_type.is_faculty())
        self.assertTrue(self.faculty_user_type.is_faculty())
        self.assertFalse(self.postgraduate_user_type.is_faculty())
        self.assertFalse(self.undergraduate_user_type.is_faculty())

    def test_is_postgraduate(self):
        self.assertFalse(self.admin_user_type.is_postgraduate())
        self.assertFalse(self.faculty_user_type.is_postgraduate())
        self.assertTrue(self.postgraduate_user_type.is_postgraduate())
        self.assertFalse(self.undergraduate_user_type.is_postgraduate())

    def test_is_undergraduate(self):
        self.assertFalse(self.admin_user_type.is_undergraduate())
        self.assertFalse(self.faculty_user_type.is_undergraduate())
        self.assertFalse(self.postgraduate_user_type.is_undergraduate())
        self.assertTrue(self.undergraduate_user_type.is_undergraduate())
