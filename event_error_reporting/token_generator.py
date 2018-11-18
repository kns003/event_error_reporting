''''
This file is used to generate token
'''
import time
from datetime import date, datetime

from django.utils import six
from django.utils.crypto import salted_hmac
from django.utils.http import base36_to_int, int_to_base36

from token_app.models import UserToken

class GenerateToken(object):
    """
    Strategy object used to generate and check tokens
    """
    key_salt = "django.contrib.auth.tokens.PasswordResetTokenGenerator"

    def make_token(self, user):
        """
        Returns a token to the user.
        """

        return self._make_token_with_timestamp(user, self._num_days(self._today()))

    def check_token(self, user, token):
        """
        Check that a password reset token is correct for a given user.
        """
        # Parse the token
        try:
            ts_b36, hash = token.split("-")
        except ValueError:
            return False

        try:
            ts = base36_to_int(ts_b36)
        except ValueError as e:
            return False

        try:
            token_obj = UserToken.objects.get(access_token=token)
            if token_obj.expiry_date < datetime.now():
                return False
        except Exception as e:
            return False

        return True

    def _make_token_with_timestamp(self, user, timestamp):
        ts_b36 = int_to_base36(timestamp)
        try:
            hash = salted_hmac(
                self.key_salt,
                self._make_hash_value(user, timestamp),
            ).hexdigest()[::2]
        except Exception as e:
            raise ValueError(e)

        return "%s-%s" % (ts_b36, hash)

    def _make_hash_value(self, user, timestamp):
        # Ensure results are consistent across DB backends
        login_timestamp = '' if user.last_login is None else user.last_login.replace(microsecond=0, tzinfo=None)
        return (
            six.text_type(user.pk) + user.password +
            six.text_type(login_timestamp) + six.text_type(timestamp)
        )

    def _num_days(self, dt):
        return int(str(time.time()).split('.')[0])

    def _today(self):
        return date.today()