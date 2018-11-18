'''
Token based authentication
'''
import logging
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from event_error_reporting.token_generator import GenerateToken
from token_app.models import UserToken
logger = logging.getLogger(__name__)


class TokenBackend(ModelBackend):
    def authenticate(self, token=None):

        try:
            token_object = UserToken.objects.get(access_token=token)
        except Exception as e:
            return None

        if GenerateToken().check_token(token_object.user, token_object.access_token):
            return token_object.user
        else:
            return None

    def get_user(self, user_id):
        """ Get a User object from the user_id. """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None