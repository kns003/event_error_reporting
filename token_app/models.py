from datetime import datetime, timedelta
import json
from django.conf import settings
from django.db import models
from django.contrib.admin.models import LogEntry
from django.contrib.postgres.fields import JSONField
from django.contrib.auth.models import User


class TimeStampedModel(models.Model):
    """
    Time stamped model for all the models.
    """
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Modified At')


def token_expiry_date():
    return datetime.now() + timedelta(minutes=settings.TOKEN_EXPIRY_TIME_MINUTES)

class UserToken(TimeStampedModel):
    """
    connects the user model with the token
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    access_token = models.CharField(max_length=200, null=True, blank=True)
    expiry_date = models.DateTimeField(default=token_expiry_date)


class CustomLogEntry(LogEntry):
    """
    extend the buildin admin class
    """
    changed_data = JSONField(default=dict, null=True, blank=True)
    request_meta = models.TextField(null=True, blank=True)
    ipaddress = models.GenericIPAddressField(null=True, blank=True)

class TestApp(TimeStampedModel):
    name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    phone_number = models.CharField(max_length=10, null=True, blank=True)
    address = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name + str(self.id)