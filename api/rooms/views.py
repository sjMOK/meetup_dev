import json
import pytz
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_202_ACCEPTED,
    HTTP_400_BAD_REQUEST,
)
from rest_framework.decorators import api_view
from django.core.exceptions import BadRequest
from rest_framework.exceptions import APIException
from users.models import User

from common.calendars import create_calendar_event, delete_calendar_event
from .models import GoogleCalenderLog, Reservation, Room, RoomImages
from .serializers import (
    MyReservationSerializer,
    ReservationSerializer,
    RoomSerializer,
)
from rest_framework.permissions import IsAuthenticated, AllowAny

from rest_framework.filters import SearchFilter
import django_filters
from django_filters.rest_framework import DjangoFilterBackend
from datetime import datetime, timedelta
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from drf_yasg.utils import swagger_auto_schema
from drf_yasg.openapi import Parameter, IN_QUERY, TYPE_STRING, TYPE_INTEGER, TYPE_NUMBER
import logging
from haversine import haversine
from drf_yasg.utils import swagger_auto_schema


from users.permissions import (
    IsAdminOrReadOnly,
    IsOwnerOrAdmin,
    UserAccessPermission,
    IsNonAdminUser,
)


AI_CENTER_POINT = (37.551100, 127.075750)
ALLOWED_DISTANCE = 25


logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")


def check_schedule_conflict(date, start, end):
    conflicting_schedules = Reservation.objects.filter(
        date=date,
        start__lt=end,  # 등록하려는 일정의 종료일 이후에 시작하는 일정
        end__gt=start,  # 등록하려는 일정의 시작일 이전에 종료하는 일정
    ).all()
    logger.warning(conflicting_schedules)
    if conflicting_schedules:
        raise BadRequest  # 겹치는 일정이 존재하는 경우
    return True  # 겹치는 일정이 없는 경우


@swagger_auto_schema(
    method="POST",
    manual_parameters=[
        Parameter(
            "latitude",
            IN_QUERY,
            type=TYPE_NUMBER,
            description="실수 형식으로 표현된 위도\nex)37.551100",
        ),
        Parameter(
            "logtitude",
            IN_QUERY,
            type=TYPE_NUMBER,
            description="실수 형식으로 표현된 경도\nex) 127.075750",
        ),
    ],
    responses={
        200: '위치 인증 성공\n"message": "complete"',
        400: '가능한 시간대 확인(시작 시간 +- 10분)\n"message": "not available time"\n\n위치 인증 실패\n"message": "fail"\n\n위도 경도 데이터 유무 및 형식(실수)확인',
    },
    operation_description="현재 위치의 위도와 경도를 기준으로 위치 인증",
)
@api_view(["POST"])
def authenticate_location(request, id):
    latitude, logtitude = request.query_params.get(
        "latitude", None
    ), request.query_params.get("logtitude", None)
    if latitude is None or logtitude is None:
        return Response("pass latitude and logtitude", HTTP_400_BAD_REQUEST)

    try:
        latitude, logtitude = float(latitude), float(logtitude)
    except ValueError:
        return Response(
            "latitude and logtitude must be a float format.", HTTP_400_BAD_REQUEST
        )

    reservation = Reservation.objects.get(id=id)
    start_datetime = datetime.combine(reservation.date, reservation.start)
    criteria = timedelta(seconds=600)
    if not (start_datetime - criteria < timezone.now() < start_datetime + criteria):
        return Response({"message": "not available time"}, status=HTTP_400_BAD_REQUEST)

    current_point = (latitude, logtitude)
    distance = haversine(AI_CENTER_POINT, current_point, unit="m")

    if distance < ALLOWED_DISTANCE:
        reservation.is_attended = True
        reservation.save()
        return Response({"message": "complete"}, status=HTTP_202_ACCEPTED)
    else:
        return Response({"message": "fail"}, status=HTTP_400_BAD_REQUEST)

    return Response(distance < ALLOWED_DISTANCE)


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
    permission_classes = [IsAuthenticated]
    serializer_class = ReservationSerializer
    queryset = Reservation.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["date", "room", "schedule_daedline"]

    def __send_email(self, room_name, user_name, date, start, end, to_email):
        context = {
            "room_name": room_name,
            "user_name": user_name,
            "date": date,
            "start": start,
            "end": end,
        }
        send_mail(
            "회의 일정을 안내해드립니다.",
            "",
            from_email=None,
            recipient_list=[to_email],
            html_message=render_to_string("mailing/reservation.html", context=context),
        )

    def create(self, request):
        if not check_schedule_conflict(
            request.data.get("date"), request.data.get("start"), request.data.get("end")
        ):
            raise BadRequest
        serializer = ReservationSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            try:
                serializer.save()
            except Exception as e:
                return Response({"message": e})

            timezone = pytz.timezone("Asia/Seoul")
            date = datetime.strptime(serializer.data["date"], "%Y-%m-%d").date()
            start = datetime.strptime(serializer.data["start"], "%H:%M:%S").time()
            end = datetime.strptime(serializer.data["end"], "%H:%M:%S").time()
            start_datetime = timezone.localize(
                datetime.combine(date, start)
            ).isoformat()
            end_datetime = timezone.localize(datetime.combine(date, end)).isoformat()

            room = Room.objects.filter(id=serializer.data["room"]).get()
            reservation = Reservation.objects.filter(id=serializer.data["id"]).get()
        try:
            # 예약자 구글 캘린더 등록
            booker = User.objects.filter(id=serializer.data["booker"]).get()
            logger.warning(booker)
            event_result = create_calendar_event(
                user=booker,
                summary=serializer.data["reason"],
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                location=room.name,
            ).json()

            try:
                log = GoogleCalenderLog.objects.create(
                    owner=booker,
                    event_id=event_result["id"],
                    reservation=reservation,
                )
            except Exception as e:
                logger.warning({"message": e})
        except APIException:
            pass
        except Exception as e:
            return Response({"message": e})

        try:  # 동반 참석자들 구글 캘린더 등록
            for com in serializer.data["companion"]:
                logger.warning(com)
                companion = User.objects.filter(id=com).get()

                event_result = create_calendar_event(
                    user=companion,
                    summary=serializer.data["reason"],
                    start_datetime=start_datetime,
                    end_datetime=end_datetime,
                    location=room.name,
                ).json()
                logger.warning(event_result["id"])
                try:
                    log = GoogleCalenderLog.objects.create(
                        owner=companion,
                        event_id=event_result["id"],
                        reservation=reservation,
                    )
                except Exception as e:
                    return Response({"error": e})
            return Response({"message": "complete"})
        except APIException:
            pass
        except Exception as e:
            return Response({"message": e})


class MyReservationFilter(django_filters.FilterSet):
    schedule_daedline = django_filters.DateFilter(
        field_name="schedule_daedline", lookup_expr="gt"
    )

    class Meta:
        model = Reservation
        fields = ["schedule_daedline", "date", "booker", "is_scheduled"]


class MyReservationView(viewsets.ModelViewSet):
    permission_classes = [IsOwnerOrAdmin]
    serializer_class = MyReservationSerializer
    queryset = Reservation.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = MyReservationFilter
    search_fields = ["day"]

    def destroy(self, request, pk, *args, **kwargs):
        reservation = Reservation.objects.filter(id=pk).get()
        google_calender_log = GoogleCalenderLog.objects.filter(reservation__id=pk).all()

        for log in google_calender_log:
            try:
                event_result = delete_calendar_event(log.owner, log.event_id).json()
                logger.warning(event_result)
            except Exception as e:
                logger.warning(e)

        return super().destroy(request, *args, **kwargs)
