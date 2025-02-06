from rest_framework_api_key.models import APIKey
import traceback
from monitor.models import ErrorLog

def data_from_request(request):

    key = request.META["HTTP_AUTHORIZATION"].split()[1]
    client_name = APIKey.objects.get_from_key(key)


    ip_address = request.META.get('HTTP_X_FORWARDED_FOR', None)
    if ip_address:
        ip_address = ip_address.split(',')[0]
    else:
        ip_address = request.META.get('REMOTE_ADDR')

    return client_name, ip_address

def build_error_log(e):
    error_type = type(e).__name__  # error type (e.g., ZeroDivisionError)
    error_message = str(e)         # error message
    tb = traceback.format_exc()    # full traceback as a string

    error_log = ErrorLog.objects.create(
        error_type=error_type,
        error_message=error_message,
        traceback=tb
    )


    return error_log
