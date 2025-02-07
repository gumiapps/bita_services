import requests
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, throttle_classes
from rest_framework.throttling import UserRateThrottle

from monitor.utils import build_error_log, data_from_request
from .spectacular_schemas import  single_sms_schema, bulk_sms_schema
from django.conf import settings  # Import Django settings
from monitor.models import RequestLog
import logging


logger = logging.getLogger(__name__)

# Custom SMS throttle
class SMSRateThrottle(UserRateThrottle):
    scope = 'sms'


@single_sms_schema
@api_view(['POST'])
@throttle_classes([SMSRateThrottle]) 
def single_sms(request):

    client_name, ip_address = data_from_request(request)

    # Pull the 3rd party sms providor's API key from settings
    api_key = settings.SMS_API_KEY
    if not api_key:
        RequestLog.objects.create(sender=client_name,
                                  response_status_code=500,
                                  sent_to = RequestLog.SMS
                                  )
        return Response(
            {"error": "Third party authorization failed"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    # Extract data from the request body
    phone = request.data.get('phone')
    message = request.data.get('message')

    # Validate required fields
    if not all([phone, message]):
        RequestLog.objects.create(sender=  client_name,
                                  response_status_code = 400,
                                  sent_to = RequestLog.SMS
                                  )
        return Response(
            {"error": "Missing required fields (phone, message)"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Prepare the payload for the GeezSMS API
    payload = {
        "phone": phone,
        "msg": message,
        # "shortcode_id": settings.SMS_SHORT_CODE,
    }

    # Prepare headers
    headers = {
        settings.SMS_API_HEADER_FIELD: api_key,
    }

    response_msg = {}

    # Make the POST 
    try:
        response = requests.post(settings.SMS_API_URL, json=payload, headers=headers)
        response_msg = response.json()
        response.raise_for_status()  # Raise an exception for HTTP errors
        if response_msg.get('error') in ['true', "True", True, '1']:
            RequestLog.objects.create(sender=  client_name,
                                  response_status_code = 400,
                                  sent_to = RequestLog.SMS
                                  )


            return Response(
                {"error_message": "Failed to send SMS", **response_msg},
                status=status.HTTP_400_BAD_REQUEST
            )

        RequestLog.objects.create(sender=  client_name,
                                  response_status_code = 200,
                                  sent_to = RequestLog.SMS
                                  )


        return Response(
            {"status": "SMS sent successfully", **response_msg},
            status=status.HTTP_200_OK
        )
    except requests.exceptions.RequestException as e:
        my_error = build_error_log(e)
        RequestLog.objects.create(sender=  client_name,
                                  response_status_code = 200,
                                  sent_to = RequestLog.SMS,
                                  error_log = my_error
                                  )

        logger.error(e)
        # Handle any errors from the API request
        return Response(
            {"error_message": f"Failed to send SMS: {str(e)}", **response_msg},
            status=status.HTTP_400_BAD_REQUEST
        )

@bulk_sms_schema
@api_view(['POST'])
@throttle_classes([SMSRateThrottle]) 
def bulk_sms(request):

    client_name, ip_address = data_from_request(request)

    # Pull the 3rd party SMS API key from settings
    api_key = settings.SMS_API_KEY
    if not api_key:
        RequestLog.objects.create(sender=  client_name,
                                  response_status_code = 400,
                                  sent_to = RequestLog.SMS
                                  )

        return Response(
            {"error": "Third party authorization failed"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    # Extract data from the request body
    contacts = request.data.get('contacts')
    sender_id = request.data.get('sender_id')
    message = request.data.get('msg')
    notify_url = request.data.get('notify_url')

    # Validate required fields
    if not all([contacts, message, notify_url]):
        RequestLog.objects.create(sender=  client_name,
                                  response_status_code = 400,
                                  sent_to = RequestLog.SMS
                                  )


        return Response(
            {"error": "Missing required fields (contacts, msg, notify_url)"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Validate contacts
    for contact in contacts:
        if not contact.get('phone_number'):
            RequestLog.objects.create(sender=  client_name,
                                  response_status_code = 400,
                                  sent_to = RequestLog.SMS
                                  )


            return Response(
                {"error": "Each contact must have a 'phone_number' field"},
                status=status.HTTP_400_BAD_REQUEST
            )

    # Prepare payload
    payload = {
        "token": api_key,
        "contacts": contacts,
        "sender_id": sender_id,
        "msg": message,
        "notify_url": notify_url,
    }

    response_msg = {}
    try:
        response = requests.post(settings.SMS_BULK_API_URL, json=payload)
        response_msg = response.json()
        response.raise_for_status()  # Raise an exception for HTTP errors

        if response_msg.get('error') in ['true', "True", True, '1']:
            RequestLog.objects.create(sender=  client_name,
                                  response_status_code = 400,
                                  sent_to = RequestLog.SMS
                                  )


            return Response(
                {"error_message": "Failed to send bulk SMS", **response_msg},
                status=status.HTTP_400_BAD_REQUEST
            )

        RequestLog.objects.create(sender=  client_name,
                                  response_status_code = 200,
                                  sent_to = RequestLog.SMS
                                  )


        return Response(
            {"status": "Bulk SMS sent successfully", **response.json()},
            status=status.HTTP_200_OK
        )
    except requests.exceptions.RequestException as e:
        my_error = build_error_log(e)
        RequestLog.objects.create(sender = client_name,
                                  response_status_code = 200,
                                  sent_to = RequestLog.SMS,
                                  error_log = my_error
                                  )

        logger.error(e)

        return Response(
            {"error_message": f"Failed to send bulk SMS: {str(e)}", **response_msg},
            status=status.HTTP_400_BAD_REQUEST
        )

