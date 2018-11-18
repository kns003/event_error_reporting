from django.db import models
from django.contrib.auth.models import User
from token_app.models import TimeStampedModel
from django.contrib.postgres.fields import JSONField

# Create your models here.

class ErrorReport(TimeStampedModel):
    status = models.CharField(max_length=20, null=True, blank=True)
    path = models.TextField(null=True, blank=True)
    request_method = models.CharField(max_length=10, null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    code = models.CharField(max_length=20, null=True, blank=True)
    duration = models.CharField(max_length=50, null=True, blank=True)
    traceback = models.TextField(null=True, blank=True)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    ip_address_info = JSONField(default=dict, null=True, blank=True)
    request_params = models.TextField(null=True, blank=True)
    request_headers = models.TextField(null=True, blank=True)

    def __str__(self):
        return str(self.code) + str(self.duration)
