from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from rest_framework import status
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
import logging
from django.shortcuts import render
from monitor.models import RequestLog
from monitor.utils import data_from_request, build_error_log
from .spectacular_schemas import send_email_schema

logger = logging.getLogger(__name__)

@csrf_exempt
@send_email_schema
@api_view(('POST',))
def send_single_email(request):

    client_name, ip_address = data_from_request(request)

    try:
        subject = request.data.get('subject')
        message = request.data.get('message')
        recipients = request.data.get('recipients')


        if not subject or not message or not recipients:
            RequestLog.objects.create(sender = client_name, 
                                response_status_code=400,
                                sent_to = RequestLog.EMAIL)


            return Response(
                {"status": "Missing required fields", "error": "subject, message, and recipients are required"},
                status=status.HTTP_400_BAD_REQUEST
            )


        # Ensure recipients is a list (it can be a comma-separated string)
        if isinstance(recipients, str):
            recipients = [email.strip() for email in recipients.split(',')]

        # Build email
        html_message = render_to_string('email_template.html', {
            'subject': subject,
            'message': message
        })

        email = EmailMessage(
            subject=subject,
            body=html_message,
            from_email=settings.EMAIL_HOST_USER,
            to=recipients
        )
        email.content_subtype = 'html'
        
        email.send(fail_silently=False)

        RequestLog.objects.create(sender = client_name, 
                                response_status_code=200,
                                sent_to = RequestLog.EMAIL)

        logger.info(f"{client_name}({ip_address}) sent subject: {subject} to {recipients}")
        return Response({"status": "Email sent successfully"}, status=status.HTTP_200_OK)

    except Exception as e:
        my_error = build_error_log(e)
        RequestLog.objects.create(sender = client_name, 
                                response_status_code=500,
                                sent_to = RequestLog.EMAIL,
                                error_log = my_error)
        logger.error(e)
        return Response({"status": "Failed to send email", "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def home(request):
    return render(request, 'home.html')

