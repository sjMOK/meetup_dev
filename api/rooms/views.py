import json
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_202_ACCEPTED,
    HTTP_400_BAD_REQUEST,
)
from django.core.exceptions import BadRequest
from .models import Reservation, Room, RoomImages
from .serializers import (
    MyReservationSerializer,
    ReservationSerializer,
    RoomSerializer,
)
from rest_framework.permissions import IsAuthenticated, AllowAny

from django_filters.rest_framework import DjangoFilterBackend
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
import logging

from users.permissions import (
    IsAdminOrReadOnly,
    IsOwnerOrAdmin,
    UserAccessPermission,
    IsNonAdminUser,
)

logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")


def check_schedule_conflict(start_date, end_date):
    conflicting_schedules = Room.objects.filter(
        start_date__lt=end_date,  # 등록하려는 일정의 종료일 이후에 시작하는 일정
        end_date__gt=start_date,  # 등록하려는 일정의 시작일 이전에 종료하는 일정
    )

    if conflicting_schedules.exists():
        raise BadRequest  # 겹치는 일정이 존재하는 경우

    # 등록하려는 일정이 현재 시간 이전인지 확인합니다.
    if start_date < datetime.now():
        raise BadRequest  # 이미 지난 일정인 경우

    return  # 겹치는 일정이 없는 경우


class RoomView(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    lookup_field = "id"

    def create(self, request):
        serializer = RoomSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            try:
                serializer.save()
                return Response({"message": "complete"})
            except Exception as e:
                return Response({"message": e})
        return Response({"message": "invalid form"})

    def update(self, request, id):
        room = Room.objects.filter(id=id)
        serializer = RoomSerializer(room, data=request.data)
        if serializer.is_valid(raise_exception=True):
            try:
                serializer.save()
                return Response({"message": "complete"})
            except Exception as e:
                return Response({"message": e})
        return Response({"message": "invalid form"})


class ReservationView(viewsets.ModelViewSet):
    # permission_classes = [IsAuthenticated]
    serializer_class = ReservationSerializer
    queryset = Reservation.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["date", "room"]

    def create(self, request):
        logger.warning(request.user)
        serializer = ReservationSerializer(data=request.data, booker=request.user)
        if serializer.is_valid(raise_exception=True):
            try:
                serializer.save()
                return Response({"message": "complete"})
            except Exception as e:
                return Response({"message": e})
        return Response({"message": "invalid form"})

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class MyReservationView(viewsets.ModelViewSet):
    # permission_classes = [IsOwnerOrAdmin]
    serializer_class = MyReservationSerializer
    queryset = Reservation.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["date", "booker"]
