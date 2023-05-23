import csv

from django.http import HttpResponse
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash

from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes, action
from rest_framework.exceptions import NotFound
from rest_framework.views import APIView
from rest_framework.viewsets import  ModelViewSet
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.parsers import MultiPartParser

from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema

from common.parsers import PlainTextParser
from .models import User, UserType
from .serializers import LoginSerializer, UserSerializer, UserTypeSerializer, PasswordChangeSerializer
from .permissions import IsNonAdminUser, UserAccessPermission
from .documentations import (
    logout_view_operation_description, login_view_operation_description, user_create_operation_description,
    user_partial_update_operation_description, change_password_operation_description, not_found_response,
    UserResponse, UserListResponse
)


class UserCsvCreateView(APIView):
    parser_classes = [MultiPartParser, PlainTextParser]

    def validate(self, rdr, user_no_list):
        error_occured = False

        lines = []
        validated_data_lst = []
        for line in rdr:
            if user_no_list.count(line['user_no']) > 1:
                line['user_no_duplicated'] = True
                error_occured = True

            serializer = UserSerializer(data=line)
            if serializer.is_valid():
                validated_data_lst.append(serializer.validated_data)
            else:
                line['errors'] = serializer.errors
                error_occured = True

            lines.append(line)

        return error_occured, lines, validated_data_lst

    def get_attachment_response(self):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="users.csv"'
        response.write(u'\ufeff'.encode('utf8'))
        return response

    def write_csv(self, response, fieldnames, lines):
        writer = csv.DictWriter(response, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(lines)

    def post(self, request, *args, **kwargs):
        if 'user_data' not in request.FILES:
            return Response("File key error(user_data).", HTTP_400_BAD_REQUEST)

        file = request.FILES['user_data']
        decoded_file = file.read().decode('euc-kr').splitlines()
    
        rdr = csv.reader(decoded_file)
        user_no_list = [line[0] for line in list(rdr)[2:]]

        file.seek(0)
        dict_rdr = csv.DictReader(decoded_file)
        next(dict_rdr)
        error_occured, lines, validated_data_lst = self.validate(dict_rdr, user_no_list)

        response = self.get_attachment_response()

        fieldnames = dict_rdr.fieldnames + ['user_no_duplicated', 'errors']
        self.write_csv(response, fieldnames, lines)

        if not error_occured:
            User.objects.bulk_create(
                [User.objects.get_user_instance(**data) for data in validated_data_lst]
            )

        return response
    
    def delete(self, request, *args, **kwargs):
        data_to_str = request.data.decode('utf-8')
        user_no_lst = data_to_str.splitlines()

        result = User.objects.filter(user_no__in=user_no_lst).delete()
        return Response(result[1].get('users.User', 0))


@swagger_auto_schema(method='POST', security=[], request_body=LoginSerializer, 
                     responses={200: UserResponse, 404: 'message: No matching user.\nbody의 user_no, password 틀렸을 때\n'}, 
                     operation_description=login_view_operation_description)
@api_view(['POST'])
def login_view(request):
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user_no = serializer.validated_data['user_no']
    password = serializer.validated_data['password']
    user = authenticate(user_no=user_no, password=password)

    if user is None:
        raise NotFound('No matching user.')

    login(request, user)
    return Response(UserSerializer(user).data)


@swagger_auto_schema(method='POST', security=[], responses={200: ''}, operation_description=logout_view_operation_description)
@api_view(['POST'])
@authentication_classes([])
def logout_view(request):
    logout(request)
    return Response()


@swagger_auto_schema(method='GET', security=[], responses={200: UserTypeSerializer(many=True)}, operation_description='모든 user type 데이터 조회')
@api_view(['GET'])
@authentication_classes([])
def get_all_user_type(request):
    queryset = UserType.objects.all()
    serializer = UserTypeSerializer(queryset, many=True)
    return Response(serializer.data)


@swagger_auto_schema(method='PATCH', request_body=PasswordChangeSerializer, responses={200: '', 400: '데이터 형식 확인'}, operation_description=change_password_operation_description)
@api_view(['PATCH'])
@permission_classes([IsNonAdminUser])
def change_password(request):
    serializer = PasswordChangeSerializer(request.user, data=request.data)
    serializer.is_valid(raise_exception=True)

    new_password = serializer.validated_data['new_password']
    request.user.set_password(new_password)
    request.user.save()
    update_session_auth_hash(request, request.user)

    return Response()


class UserViewSet(ModelViewSet):
    __normal_user_patchable_fields = ('name', 'email')
    lookup_value_regex = r'[0-9]+'
    queryset = User.objects.all().order_by('user_type', 'user_no')
    serializer_class = UserSerializer
    permission_classes = [UserAccessPermission]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user_no']

    def get_object(self):
        if self.request.user.is_admin():
            return super().get_object()
        return self.request.user

    def __validate_data_contains_non_patchable_fields(self):
        if not self.request.user.is_admin():
            return set(self.request.data).difference(self.__normal_user_patchable_fields)
        return False

    @swagger_auto_schema(responses={200: UserResponse, 404: not_found_response}, operation_description='id에 해당하는 유저 정보 조회')
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(responses={200: UserListResponse(many=True)}, operation_description='모든 user 정보 조회')
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(request_body=UserSerializer, responses={201: '', 400: '데이터 형식 확인'}, operation_description=user_create_operation_description)
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(request_body=UserSerializer, responses={200: '', 400: '데이터 형식 확인', 404: not_found_response},
                         operation_description=user_partial_update_operation_description)
    def partial_update(self, request, *args, **kwargs):
        if self.__validate_data_contains_non_patchable_fields():
            return Response('The data contains fields cannot be updated.', status=HTTP_400_BAD_REQUEST)

        return super().partial_update(request, *args, **kwargs)
    
    @swagger_auto_schema(responses={204: '', 404: not_found_response}, operation_description='id에 해당하는 유저 삭제')
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @swagger_auto_schema(responses={200: UserResponse}, operation_description='token에 해당하는 user 정보 조회')
    @action(detail=False, methods=['GET'], url_path='mine')
    def retrieve_mine(self, request, *args, **kwargs):
        return Response(UserSerializer(request.user).data)
