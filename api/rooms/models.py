from django.db import models
from users.models import User
from django.utils.translation import gettext_lazy as _


class RoomImages(models.Model):
    id = models.BigAutoField(primary_key=True, auto_created=True)
    image = models.ImageField(upload_to="images/", db_column="image")


class Room(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(blank=False, max_length=100, null=False)
    discription = models.TextField()
    images = models.ForeignKey(RoomImages, on_delete=models.CASCADE, null=True)


class Reservation(models.Model):
    STATUS_CHOICE = (
        (0, "available"),
        (1, "reserved"),
        (2, "is blocked"),
    )
    id = models.AutoField(primary_key=True)
    meeting_name = models.CharField(max_length=63, null=True, blank=True)
    status = models.IntegerField(choices=STATUS_CHOICE, default=0)
    booker = models.ForeignKey(
        User, related_name="booker", on_delete=models.SET_NULL, null=True
    )
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True)
    companion = models.ForeignKey(
        User, related_name="companion", on_delete=models.SET_NULL, null=True
    )


# 날짜 시간, 회의명, 참석 멤버


class DailyReservationCard(models.Model):
    id = models.AutoField(primary_key=True)
    date = models.DateField(auto_now=True)
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True)
    time_1 = models.ForeignKey(
        Reservation,
        related_name="time_1",
        help_text="9-10",
        on_delete=models.CASCADE,
        null=True,
    )
    time_2 = models.ForeignKey(
        Reservation,
        related_name="time_2",
        help_text="10-11",
        on_delete=models.CASCADE,
        null=True,
    )
    time_3 = models.ForeignKey(
        Reservation,
        related_name="time_3",
        help_text="11-12",
        on_delete=models.CASCADE,
        null=True,
    )
    time_4 = models.ForeignKey(
        Reservation,
        related_name="time_4",
        help_text="12-13",
        on_delete=models.CASCADE,
        null=True,
    )
    time_5 = models.ForeignKey(
        Reservation,
        related_name="time_5",
        help_text="13-14",
        on_delete=models.CASCADE,
        null=True,
    )
    time_6 = models.ForeignKey(
        Reservation,
        related_name="time_6",
        help_text="14-15",
        on_delete=models.CASCADE,
        null=True,
    )
    time_7 = models.ForeignKey(
        Reservation,
        related_name="time_7",
        help_text="15-16",
        on_delete=models.CASCADE,
        null=True,
    )
    time_8 = models.ForeignKey(
        Reservation,
        related_name="time_8",
        help_text="16-17",
        on_delete=models.CASCADE,
        null=True,
    )
    time_9 = models.ForeignKey(
        Reservation,
        related_name="time_9",
        help_text="17-18",
        on_delete=models.CASCADE,
        null=True,
    )
