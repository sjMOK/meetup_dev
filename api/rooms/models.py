from django.db import models


class Room(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=60)
    notification = models.CharField(max_length=1000, blank=True, null=True)

    class Meta:
        db_table = 'room'


class RoomImages(models.Model):
    id = models.AutoField(primary_key=True)
    room = models.ForeignKey(Room, models.DO_NOTHING)
    image_url = models.CharField(max_length=200)
    sequence = models.IntegerField()

    class Meta:
        db_table = 'room_images'


class Reservation(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey('users.User', models.DO_NOTHING)
    room = models.ForeignKey('Room', models.DO_NOTHING)
    start = models.DateTimeField()
    end = models.DateTimeField()

    class Meta:
        db_table = 'reservation'


class ReservationAttendees(models.Model):
    id = models.AutoField(primary_key=True)
    reservation = models.ForeignKey('Reservation', models.DO_NOTHING)
    user = models.ForeignKey('users.User', models.DO_NOTHING)

    class Meta:
        db_table = 'reservation_attendees'
