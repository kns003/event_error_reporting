import logging
import requests

from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from rest_framework import exceptions as RestExceptions
from django.core import exceptions
from rest_framework.authentication import TokenAuthentication
from django.contrib.auth.models import AnonymousUser

from .backends import TokenBackend

auth_logger = logging.getLogger(__name__)


class VerifyApiAndUserAuthentication(TokenAuthentication):
    """
    Token auth class for rest framework
    """
    def __init__(self, *args, **kwargs):
        super(VerifyApiAndUserAuthentication, self).__init__(*args, **kwargs)
        self.backend = TokenBackend()

    def authenticate(self, request, **kwargs):

        if request.META[settings.HTTP_ACCESS_TOKEN]:
            user = self.backend.authenticate(
                token=request.META[settings.HTTP_ACCESS_TOKEN]
            )
            if user:
                return (user, request.META[settings.HTTP_ACCESS_TOKEN])
            else:
                raise RestExceptions.NotAuthenticated("Invalid token")
        else:
            raise RestExceptions.NotAcceptable(_('Access token not present'))


def check_token_header(function):
    """
    token auth decorator for all the apis
    :param function:
    :return:
    """
    def wrap(request, *args, **kwargs):
        backend = TokenBackend()
        if settings.HTTP_ACCESS_TOKEN in request.META:
            if request.META[settings.HTTP_ACCESS_TOKEN]:
                user = backend.authenticate(request.META[settings.TOKEN_NAME])
                if user:
                    request.user = user
                    return function(request, *args, **kwargs)
                else:
                    request.user = AnonymousUser()
                    raise exceptions.PermissionDenied('User not authorised', 400)
            else:
                raise exceptions.PermissionDenied('Token not found', 400)
        else:
            raise exceptions.PermissionDenied('Token not preset', 400)

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap
