from django.contrib.auth import login, authenticate, logout

from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.exceptions import NotFound

from .serializers import LoginSerializer


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
