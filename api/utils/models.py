import datetime
from django.db import models

from users.models import User

# Create your models here.


class Notice(models.Model):
    id = models.AutoField(primary_key=True)
    popup = models.BooleanField(default=False)
    start = models.DateTimeField(default=datetime.datetime.now)
    end = models.DateTimeField(default=datetime.datetime.now)
    title = models.CharField(max_length=63, null=True, blank=True)
    content = models.TextField()
    create_at = models.DateTimeField(auto_now_add=True)


class Report(models.Model):
    CATEGORY_CHOICE = (
        (0, "개선사항"),
        (1, "문의"),
    )
    id = models.AutoField(primary_key=True)
    reporter = models.ForeignKey(User, related_name="repoter", on_delete=models.CASCADE)
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICE)
    title = models.CharField(max_length=64, null=False)
    content = models.TextField(null=False)


class Comment(models.Model):
    id = models.AutoField(primary_key=True)
    author = models.ForeignKey(User, related_name="author", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now=True)
    content = models.CharField(max_length=300)
    report = models.ForeignKey(Report, related_name="comment", on_delete=models.CASCADE)
