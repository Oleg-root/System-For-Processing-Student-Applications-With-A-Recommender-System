import os.path

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
# !!!
# each class is an each own table in database
# each field is a different field in the datatable
# FIND-A-TOPIC MODELS

class Topic(models.Model):
    name_russian = models.CharField('Название на русском', max_length=300)
    name_english = models.CharField('Название на английском', max_length=300)
    description = models.TextField('Краткое описание темы')
    lecturer = models.ForeignKey(User, on_delete=models.CASCADE)
    date_created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name_russian

class StudentRequestForTopic(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    associatedTopic = models.ForeignKey(Topic, on_delete=models.CASCADE, default=0)
    receiver = models.CharField(max_length=200)
    description = models.TextField('Опишите свои интересы')
    responded = models.BooleanField(default=False)
    lecturer_answer = models.TextField(max_length=2000, default='')
    declined = models.BooleanField(default=False)
    no_topic = models.BooleanField(default=False)
    date_created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.student.username} --> {self.receiver}'

class RequestResponse(models.Model):
    associatedRequest = models.ForeignKey(StudentRequestForTopic, on_delete=models.CASCADE, default=0)
    lecturer = models.ForeignKey(User, on_delete=models.CASCADE)
    receiver = models.CharField(max_length=200)
    content = models.TextField('Введите ваш ответ (до 2000 символов)', max_length=2000)
    date_created = models.DateTimeField(default=timezone.now)

class Notification(models.Model):
    receiver = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    content = models.TextField()
    #read = models.BooleanField(default=False)
    date_created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title

