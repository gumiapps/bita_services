from django.urls import path
from . import views

urlpatterns = [
    path('single-sms/', views.single_sms, name='single_sms'),
    path('bulk-sms/', views.bulk_sms, name='bulk_sms'),
]
