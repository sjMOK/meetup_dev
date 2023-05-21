from django.shortcuts import render

import json
from rest_framework import viewsets
from rest_framework.response import Response
from .models import Comment, Notice, Report
from .serializers import (
    CommentSerializer,
    NoticeSerializer,
    ReportSerializer,
)

# Create your views here.


class NoticeView(viewsets.ModelViewSet):
    serializer_class = NoticeSerializer
    queryset = Notice.objects.all()


class ReportView(viewsets.ModelViewSet):
    serializer_class = ReportSerializer
    queryset = Report.objects.all()


class CommentView(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()
