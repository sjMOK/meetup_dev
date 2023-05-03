from django.contrib.auth import login, authenticate, logout, update_session_auth_hash

from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.exceptions import NotFound
from rest_framework.viewsets import GenericViewSet
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST

from .models import User
from .serializers import LoginSerializer, UserSerializer, PasswordChangeSerializer
from .permissions import IsAuthenticatedNonAdminUser, UserAccessPermission


@api_view(['POST'])
def login_view(request):
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    username = serializer.validated_data['username']
    password = serializer.validated_data['password']
    user = authenticate(username=username, password=password)

    if user is None:
        raise NotFound('No matching user.')

    login(request, user)
    return Response(str(request.user))


@api_view(['POST'])
@authentication_classes([])
def logout_view(request):
    logout(request)
    return Response('Logout success.')


@api_view(['PATCH'])
@permission_classes([IsAuthenticatedNonAdminUser])
def change_password(request):
    serializer = PasswordChangeSerializer(request.user, data=request.data)
    serializer.is_valid(raise_exception=True)

    new_password = serializer.validated_data['new_password']
    request.user.set_password(new_password)
    request.user.save()
    update_session_auth_hash(request, request.user)

    return Response()


class UserViewSet(GenericViewSet):
    __normal_user_patchable_fields = ('name', 'email')
    lookup_value_regex = r'[0-9]+'
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [UserAccessPermission]

    def __get_user(self):
        if self.request.user.is_admin():
            return self.get_object()
        return self.request.user

    def __validate_data_contains_non_patchable_fields(self):
        if not self.request.user.is_admin():
            return set(self.request.data).difference(self.__normal_user_patchable_fields)
        return False

    def retrieve(self, request, pk):
        user = self.__get_user()
        serializer = self.get_serializer(user)
        return Response(serializer.data)
    
    def list(self, request):
        users = self.get_queryset()
        serializer = self.get_serializer(users, many=True)
        return Response(serializer.data)
    
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(status=HTTP_201_CREATED, headers={'Location': user.id})
    
    def partial_update(self, request, pk):        
        if self.__validate_data_contains_non_patchable_fields():
            return Response('The data contains fields cannot be updated.', status=HTTP_400_BAD_REQUEST)
        user = self.__get_user()

        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response()
    
    def destroy(self, request, pk):
        user = self.__get_user()
        user.delete()
        return Response()
