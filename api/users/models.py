from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **kwargs):
        user = self.model(
            email=self.normalize_email(email),
            **kwargs
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create(self, **kwargs):
        return self.create_user(**kwargs)


class User(AbstractBaseUser):
    id = models.AutoField(primary_key=True)
    username = models.CharField(unique=True, max_length=45)
    name = models.CharField(max_length=45)
    email = models.EmailField()
    user_type = models.ForeignKey('UserType', models.DO_NOTHING)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'username'

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
        return f'{self.username} {self.name}({self.user_type})'


class UserType(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20)
    possible_duration = models.IntegerField()

    class Meta:
        db_table = 'user_type'
        ordering = ['id']

    def __str__(self):
        return self.name
