import json
from rest_framework import viewsets
from rest_framework.response import Response
from .models import Reservation, Room, RoomImages
from .serializers import (
    ReservationSerializer,
    RoomSerializer,
)
from rest_framework.permissions import IsAuthenticated, AllowAny

from django_filters.rest_framework import DjangoFilterBackend
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")


class RoomView(viewsets.ModelViewSet):
    # permission_classes = [IsAuthenticated]
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
    serializer_class = ReservationSerializer
    queryset = Reservation.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["date"]
