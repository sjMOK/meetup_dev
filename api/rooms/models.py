from django.db import models
from users.models import User
from django.utils.translation import gettext_lazy as _
import datetime


class RoomImages(models.Model):
    id = models.BigAutoField(primary_key=True, auto_created=True)
    image = models.ImageField(upload_to="images/", db_column="image")


class Room(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(blank=False, max_length=100, null=False)
    discription = models.TextField()
    amenities = models.TextField()
    images = models.ForeignKey(RoomImages, on_delete=models.CASCADE, null=True)


class Reservation(models.Model):
    STATUS_CHOICE = (
        (0, "reserved"),
        (1, "is blocked"),
    )
    id = models.AutoField(primary_key=True)
    is_scheduled = models.BooleanField(default=False)
    day = models.JSONField(default=dict)
    date = models.DateField(default=datetime.date.today)
    start = models.TimeField(default=datetime.time)
    end = models.TimeField(default=datetime.time)
    reason = models.CharField(max_length=63, null=True, blank=True)
    status = models.IntegerField(choices=STATUS_CHOICE, default=0)
    booker = models.ForeignKey(User, related_name="booker", on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    companion = models.ForeignKey(
        User, related_name="companion", on_delete=models.CASCADE
    )
