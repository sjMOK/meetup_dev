from rest_framework import serializers
from .models import Reservation, Room, RoomImages

from users.models import User
import logging, json
from PIL import Image

logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")


class RoomImageSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    image = serializers.ImageField(required=False)

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
            "amenities": validated_data["amenities"],
        }
        try:
            image = validated_data.pop("image")
            room_images = RoomImages.objects.create(image=image)
            data["images"] = room_images
        except ValueError:
            logging.warning("이미지 없음")

        room = Room.objects.create(**data)
        return room

    def update(self, instance, validated_data):
        data = {
            "name": validated_data["name"],
            "discription": validated_data["discription"],
            "amenities": validated_data["amenities"],
        }
        try:
            image = validated_data.pop("image")
            room_images = RoomImages.objects.create(image=image)
            data["images"] = room_images
        except:
            logging.warning("이미지 없음")

        room = instance.update(**data)
        return room

    class Meta:
        model = Room
        fields = "__all__"


class BookerSerialzier(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["name", "email", "user_type", "department"]


class CompanionSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = User
        fields = ["id"]


class ReservationSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Reservation
        fields = "__all__"


class MyReservationSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    booker = BookerSerialzier(read_only=True)
    room = RoomSerializer(read_only=True)

    class Meta:
        model = Reservation
        fields = "__all__"
