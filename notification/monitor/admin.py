from django.contrib import admin
from .models import RequestLog, ErrorLog

@admin.register(RequestLog)
class RequestLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'sent_at', 'response_status_code', 'sent_to', 'error_log')
    list_filter = ('sent_to', 'response_status_code', 'sent_at')
    search_fields = ('sender__name', 'sent_to')  

@admin.register(ErrorLog)
class ErrorLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'error_type', 'timestamp', 'error_message')
    list_filter = ('error_type', 'timestamp')
    search_fields = ('error_type', 'error_message')

