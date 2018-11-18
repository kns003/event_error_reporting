import logging
from rest_framework.views import APIView
from .authentication import VerifyApiAndUserAuthentication

logger = logging.getLogger(__name__)


class CustomTokenAPIView(APIView):
    authentication_classes = (VerifyApiAndUserAuthentication,)