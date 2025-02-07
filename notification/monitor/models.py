from django.db import models
from rest_framework_api_key.models import APIKey
from django.db.models import Count

class RequestLog(models.Model):
    # Constants for choices
    EMAIL = 'email'
    SMS = 'sms'
    IN_APP = 'in-app'

    SEND_TO_CHOICES = [
        (EMAIL, 'Email'),
        (SMS, 'SMS'),
        (IN_APP, 'In-App'),
    ]

    id = models.AutoField(primary_key=True)  #
    sender = models.ForeignKey(APIKey, on_delete=models.CASCADE)
    sent_at = models.DateTimeField(auto_now_add=True)  
    response_status_code = models.IntegerField()  
    sent_to = models.CharField(
        max_length=10,
        choices=SEND_TO_CHOICES,
        default=EMAIL,  
    )  

    error_log = models.OneToOneField(
        'ErrorLog',
        on_delete=models.SET_NULL,  
        null=True,                
        blank=True,                 
        related_name='request_log'  
    )

    def __str__(self):
        return f"Request {self.id} from {self.sender} to {self.get_sent_to_display()} at {self.sent_at}"


    @classmethod
    def total_request_count(cls):
        return cls.objects.count()

    @classmethod
    def success_count(cls):
        return cls.objects.filter(response_status_code=200).count()

    @classmethod
    def failure_count(cls):
        return cls.objects.exclude(response_status_code=200).count()

    @classmethod
    def request_count_by_endpoint(cls):
        counts = cls.objects.values('sent_to').annotate(request_count=Count('id'))
        default_endpoints = {choice[0]: 0 for choice in cls.SEND_TO_CHOICES}
        result = {item['sent_to']: item['request_count'] for item in counts}
        default_endpoints.update(result)
        return default_endpoints

    @classmethod
    def request_count_by_client(cls):
        counts = cls.objects.values('sender__name').annotate(request_count=Count('id'))
        return {item['sender__name']: item['request_count'] for item in counts}




class ErrorLog(models.Model):
    id = models.AutoField(primary_key=True)           
    timestamp = models.DateTimeField(auto_now_add=True) 
    error_type = models.CharField(max_length=255)   
    error_message = models.TextField()                  
    traceback = models.TextField(blank=True, null=True) 

    def __str__(self):
        return f"{self.error_type} at {self.timestamp}"
