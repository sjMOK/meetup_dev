from rest_framework.test import APITestCase
from rest_framework.exceptions import APIException, ValidationError

from .factories import UserFactory, UserTypeFactory
from ..serializers import UserTypeSerializer, UserSerializer, LoginSerializer, PasswordChangeSerializer
from ..models import UserType


class UserTypeSerializerTestCase(APITestCase):
    def test_all_fields_are_read_only(self):
        serializer = UserTypeSerializer()
        self.assertTrue(serializer.fields['id'].read_only)
        self.assertTrue(serializer.fields['name'].read_only)
        self.assertTrue(serializer.fields['possible_duration'].read_only)

    def test_serialization(self):
        user_type = UserType.objects.create(name='admin', possible_duration=0)
        serializer = UserTypeSerializer(user_type)
        expected_data = {
            'id': user_type.id,
            'name': user_type.name,
            'possible_duration': user_type.possible_duration,
        }

        self.assertDictEqual(serializer.data, expected_data)


class UserSerializerTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        user_type = UserTypeFactory()
        cls.user = UserFactory(user_type=user_type)

    def test_password_is_write_only(self):
        serializer = UserSerializer()
        self.assertTrue(serializer.fields['password'].write_only)

    def test_password_required_false(self):
        serializer = UserSerializer()
        self.assertFalse(serializer.fields['password'].required)

    def test_serialization(self):
        serializer = UserSerializer(self.user)
        expected_data = {
            'username': self.user.username,
            'name': self.user.name, 
            'email': self.user.email,
            'user_type': UserTypeSerializer(self.user.user_type).data,
        }

        self.assertDictEqual(serializer.data, expected_data)

    def test_update_password_raise_error(self):
        data = {
            'password': 'update_password',
        }
        serializer = UserSerializer(self.user, data, partial=True)
        
        self.assertRaisesMessage(
            APIException,
            'Cannot update password with UserSerializer instance.',
            serializer.is_valid,
            raise_exception=True
        )


class LoginSerializerTestCase(APITestCase):
    def test_all_fields_are_write_only(self):
        serializer = LoginSerializer()
        self.assertTrue(serializer.fields['username'].write_only)
        self.assertTrue(serializer.fields['password'].write_only)

    def test_trim_white_space_option(self):
        serializer = LoginSerializer()
        self.assertFalse(serializer.fields['username'].trim_whitespace)
        self.assertFalse(serializer.fields['password'].trim_whitespace)


class PasswordChangeSerializerTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.raw_password = 'raw_password'
        cls.user = UserFactory(password=cls.raw_password)

    def test_current_password_and_new_password_are_same(self):
        data = {
            'current_password': self.raw_password,
            'new_password': self.raw_password,
        }
        serializer = PasswordChangeSerializer(self.user, data=data)

        self.assertRaisesMessage(
            ValidationError,
            'The new password is same as the current password.',
            serializer.is_valid,
            raise_exception=True
        )

    def test_current_password_and_new_password_are_different(self):
        data = {
            'current_password': self.raw_password,
            'new_password': 'new_password',
        }
        serializer = PasswordChangeSerializer(self.user, data=data)

        self.assertTrue(serializer.is_valid())
        self.assertDictEqual(serializer.validated_data, data)

    def test_current_password_not_match(self):
        data = {
            'current_password': '_' + self.raw_password,
            'new_password': 'new_password',
        }
        serializer = PasswordChangeSerializer(self.user, data=data)

        self.assertRaisesMessage(
            ValidationError,
            'The current password not matched.',
            serializer.is_valid,
            raise_exception=True
        )

    def test_current_password_match(self):
        data = {
            'current_password': self.raw_password,
            'new_password': 'new_password',
        }
        serializer = PasswordChangeSerializer(self.user, data=data)

        self.assertTrue(serializer.is_valid())
        self.assertDictEqual(serializer.validated_data, data)
