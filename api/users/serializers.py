from rest_framework import serializers
from rest_framework.exceptions import APIException

from .models import User


class UserTypeSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    possible_duration = serializers.IntegerField(read_only=True)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password', 'name', 'email', 'user_type']
        extra_kwargs = {
            'password': {
                'write_only': True, 'required': False,
            },
        }

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['user_type'] = UserTypeSerializer(instance.user_type).data

        return ret

    def validate_password(self, value):
        if self.instance is not None:
            raise APIException('Cannot update password with UserSerializer instance.')

        return value


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(write_only=True, trim_whitespace=False)
    password = serializers.CharField(write_only=True, trim_whitespace=False)
