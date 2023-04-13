from rest_framework.test import APITestCase
from rest_framework.exceptions import APIException

from ..serializers import UserTypeSerializer, UserSerializer
from ..models import UserType, User


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
        user_type = UserType.objects.create(name='admin', possible_duration=0)
        cls.user = User.objects.create_user(username='username', password='password', name='name',
                                        email='email@sejong.ac.kr', user_type=user_type)

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
