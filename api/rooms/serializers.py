from rest_framework import serializers
from .models import DailyReservationCard, Reservation, Room, RoomImages
from django.contrib.auth.models import User
import logging, json
from PIL import Image

logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")


class RoomImageSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    image = serializers.ImageField(use_url=True, required=False)

    class Meta:
        model = RoomImages
        fields = "__all__"


class RoomSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    discription = serializers.CharField()
    images = RoomImageSerializer(read_only=True)
    image = serializers.ImageField(required=False)

    def create(self, validated_data):
        data = {
            "name": validated_data["name"],
            "discription": validated_data["discription"],
        }
        try:
            image = validated_data.pop("image")
            room_images = RoomImages.objects.create(image=image)
            data["images"] = room_images
        except ValueError:
            logging.warning("이미지 없음")

        room = Room.objects.create(**data)

        return room

    class Meta:
        model = Room
        fields = "__all__"


class ReservationSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    status = serializers.IntegerField(read_only=True)

    class Meta:
        model = Reservation
        fields = "__all__"


class DailyReservationCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyReservationCard
        fields = "__all__"
