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
        admin_user_type = UserType.objects.create(id=1, name='admin', possible_duration=0)
        UserType.objects.create(id=2, name='faculty', possible_duration=12)
        UserType.objects.create(id=3, name='postgraduate', possible_duration=2)
        UserType.objects.create(id=4, name='undergraduate', possible_duration=1)

        cls.user = User.objects.create_user(username='username', password='password', name='name', email='email@sejong.ac.kr', user_type=admin_user_type)

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

    def test_custom_manager(self):
        self.assertIsInstance(User.objects, UserManager)

    def test_is_admin(self):
        self.assertTrue(self.user.is_admin())
        self.assertFalse(self.user.is_faculty())
        self.assertFalse(self.user.is_postgraduate())
        self.assertFalse(self.user.is_undergraduate())

    def test_is_faculty(self):
        self.user.user_type_id = 2
        self.user.save()

        self.assertFalse(self.user.is_admin())
        self.assertTrue(self.user.is_faculty())
        self.assertFalse(self.user.is_postgraduate())
        self.assertFalse(self.user.is_undergraduate())

    def test_is_postgraduate(self):
        self.user.user_type_id = 3
        self.user.save()

        self.assertFalse(self.user.is_admin())
        self.assertFalse(self.user.is_faculty())
        self.assertTrue(self.user.is_postgraduate())
        self.assertFalse(self.user.is_undergraduate())

    def test_is_undergraduate(self):
        self.user.user_type_id = 4
        self.user.save()

        self.assertFalse(self.user.is_admin())
        self.assertFalse(self.user.is_faculty())
        self.assertFalse(self.user.is_postgraduate())
        self.assertTrue(self.user.is_undergraduate())

    def test_str_representaion(self):
        self.assertEqual(str(self.user), 
                         f'{self.user.username} {self.user.name}({self.user.user_type})')


class UserTypeTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_type = UserType.objects.create(name='name', possible_duration=0)

    def test_create(self):
        user_type = UserType.objects.create(name='name', possible_duration=0)
        self.assertIsInstance(user_type, UserType)

    def test_pk_is_id(self):
        pk_name = UserType._meta.pk.name
        self.assertEqual(pk_name, 'id')

    def test_name_max_length(self):
        max_length = self.user_type._meta.get_field('name').max_length
        self.assertEqual(max_length, 20)

    def test_str_representaion(self):
        self.assertEqual(str(self.user_type), self.user_type.name)
