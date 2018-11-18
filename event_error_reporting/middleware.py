import traceback
import requests
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin

from reports.models import ErrorReport


class ExceptionMiddleWare(MiddlewareMixin):
    def process_request(self, request):
        request.request_time = timezone.now()


    def process_exception(self, request, exception):

        try:
            # the below variable helps to find who is actually trying
            self._store_response(request, exception)
        except Exception as e:
            print (e)
            pass


    def _store_response(self, request, exception):
        ip_address_info = requests.get('https://ipapi.co/' + get_client_ip(request) + '/json/').json()
        if request.method == 'POST':
            request_params = request.POST.dict()
        elif request.method == 'GET':
            request_params = request.GET.dict()
        elif request.method == 'PUT':
            request_params = request.POST.dict()

        if hasattr(exception, 'message'):
            message = exception.message
        else:
            message = exception.args
        ErrorReport.objects.create(
            status='ERROR',
            message=message,
            code=500,
            traceback=traceback.format_exc(),
            duration=str((timezone.now() - request.request_time).total_seconds()),
            path=request.path,
            request_method=request.method,
            user=request.user,
            ip_address=get_client_ip(request),
            ip_address_info=ip_address_info,
            request_headers=request.META,
            request_params = request_params
        )

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return '111.93.143.166'