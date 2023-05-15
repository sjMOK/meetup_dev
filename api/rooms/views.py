import json
from rest_framework import viewsets
from rest_framework.response import Response
from .models import Reservation, Room, RoomImages
from .serializers import (
    ReservationSerializer,
    RoomSerializer,
)
from rest_framework.permissions import IsAuthenticated, AllowAny
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
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({"message": "complete"})
            except:
                return Response({"message": "fail"})
        return Response({"message": "invalid form"})


class ReservationView(viewsets.ModelViewSet):
    serializer_class = ReservationSerializer
    queryset = Reservation.objects.all()
