#-*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.urlresolvers import reverse
from model_utils.models import TimeStampedModel, StatusModel
from codenote import settings

# 모델변경시, syncdb 에서 오류가 난다면 south를 이용한다. 다음 두 줄을 수행한다.
# $ python manage.py schemamigration note --auto
# $ python manage.py migrate note

# Create your models here.
class Topic(TimeStampedModel):
    name = models.CharField(max_length=128)
    content = models.TextField(blank=True, null=True)
    img = models.ImageField(blank=True, null=True, upload_to=lambda instance, filename: '/static/img/'.join(['topic', str(instance.pk), filename]))
    url = models.URLField(blank=True, null=True)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True)

    extra_data = models.TextField(blank=True, null=True)
    status = models.BooleanField(default=True)

    def __unicode__(self):
        return "%s" % self.name


class Note(TimeStampedModel):
    name = models.CharField(max_length=128)
    content = models.TextField(blank=True, null=True)
    img = models.ImageField(blank=True, null=True, upload_to=lambda instance, filename: '/static/img/'.join(['note', str(instance.pk), filename]))
    url = models.URLField(blank=True, null=True)

    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    topic = models.ManyToManyField(Topic, blank=True, null=True)

    isPublic = models.BooleanField(default=True)

    extra_data = models.TextField(blank=True, null=True)
    status = models.BooleanField(default=True)

    def __unicode__(self):
        return "%s" % self.name


class CodenoteUser(AbstractUser):
    content = models.TextField(blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    img = models.ImageField(blank=True, null=True, upload_to=lambda instance, filename: '/static/img/'.join(['user', str(instance.pk), filename]))

    gender = models.CharField(max_length=128, blank=True, null=True)
    age = models.IntegerField(blank=True, null=True)
    country = models.CharField(max_length=128, blank=True, null=True)
    occupation = models.CharField(max_length=128, blank=True, null=True)

    extra_data = models.TextField(blank=True, null=True)
    status = models.BooleanField(default=True)

    def __unicode__(self):
        return "%s" % self.username


class Comment(TimeStampedModel):
    content = models.TextField()

    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    note = models.ForeignKey(Note, blank=True, null=True)

    status = models.BooleanField(default=True)

    def __unicode__(self):
        return "%s" % self.content


class Collection(TimeStampedModel):
    content = models.TextField()

    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    note = models.ForeignKey(Note, blank=True, null=True)

    status = models.BooleanField(default=True)

    def __unicode__(self):
        return "%s" % self.content


class Like(TimeStampedModel):
    type = models.CharField(max_length=64)

    user = models.ForeignKey(settings.AUTH_USER_MODEL)

    note = models.ForeignKey(Note, blank=True, null=True)
    comment = models.ForeignKey(Comment, blank=True, null=True)

    status = models.BooleanField(default=True)

    def __unicode__(self):
        return "%s" % self.type
