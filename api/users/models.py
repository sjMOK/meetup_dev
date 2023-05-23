from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(self, *args, **kwargs):
        user = self.get_user_instance(**kwargs)
        user.save()
        return user

    def create(self, **kwargs):
        return self.create_user(**kwargs)

    def get_user_instance(self, email, password=None, **kwargs):
        user = self.model(
            email=self.normalize_email(email),
            **kwargs
        )

        user.set_password(password)
        return user


class User(AbstractBaseUser):
    id = models.AutoField(primary_key=True)
    user_no = models.CharField(unique=True, max_length=45)
    name = models.CharField(max_length=45)
    email = models.EmailField()
    user_type = models.ForeignKey('UserType', models.DO_NOTHING)
    major = models.ForeignKey('UserMajor', models.DO_NOTHING)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'user_no'

    objects = UserManager()

    class Meta:
        db_table = 'user'

    def is_admin(self):
        return self.user_type_id == 1

    def is_faculty(self):
        return self.user_type_id == 2

    def is_postgraduate(self):
        return self.user_type_id == 3

    def is_undergraduate(self):
        return self.user_type_id == 4

    def __str__(self):
        return f'{self.user_no} {self.name}({self.user_type})'


class UserType(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20)
    possible_duration = models.IntegerField()

    class Meta:
        db_table = 'user_type'
        ordering = ['id']

    def __str__(self):
        return self.name


class UserMajor(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20)

    class Meta:
        db_table = 'user_major'
        ordering = ['id']

    def __str__(self):
        return self.name
