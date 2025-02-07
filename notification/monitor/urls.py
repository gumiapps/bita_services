from django.urls import path
from .views import APIKeyListView, MonitorAPIView

urlpatterns = [
    path('api-keys/', APIKeyListView.as_view(), name='api-key-list'),
    path('performance-metrics/', MonitorAPIView.as_view(), name='performance-metrics'),
]
