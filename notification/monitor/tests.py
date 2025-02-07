from django.urls import reverse
from django.test import TestCase
from rest_framework.test import APIClient, APITestCase
from rest_framework_api_key.models import APIKey
from rest_framework import status
from monitor.models import RequestLog

class MonitorAPIViewTest(APITestCase):
    def setUp(self):
        # Set up the API client
        self.client = APIClient()

        # Create an API key for authentication
        self.api_key, self.key = APIKey.objects.create_key(name="Test Admin Key")

        # Create sample request logs with a valid sender (APIKey)
        sender_api_key, _ = APIKey.objects.create_key(name="Test Sender Key")
        self.sender = sender_api_key

        # Create request logs
        RequestLog.objects.create(sender=self.sender, response_status_code=200, sent_to='email')
        RequestLog.objects.create(sender=self.sender, response_status_code=500, sent_to='sms')
        RequestLog.objects.create(sender=self.sender, response_status_code=200, sent_to = 'in-app')
        RequestLog.objects.create(sender=self.sender, response_status_code=400, sent_to = 'email')

    def test_monitor_api_view_with_valid_api_key(self):
        """Test MonitorAPIView with a valid API key"""
        # Include the API key in the headers
        self.client.credentials(HTTP_AUTHORIZATION=f'Api-Key {self.key}')
        
        # Perform GET request
        response = self.client.get(reverse('performance-metrics'))  
        
        # Assert the response status code
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = response.json()
        
        # Assertions on response data
        self.assertEqual(response_data['total_requests'], 4)
        self.assertEqual(response_data['success_count'], 2)
        self.assertEqual(response_data['failure_count'], 2)
        self.assertAlmostEqual(response_data['success_rate'], 0.5, places=2)
        self.assertAlmostEqual(response_data['failure_rate'], 0.5, places=2)
        self.assertIn('request_count_by_endpoint', response_data)
        self.assertIn('request_count_by_client', response_data)

    def test_monitor_api_view_with_invalid_api_key(self):
        """Test MonitorAPIView with an invalid API key"""
        # Include an invalid API key in the headers
        self.client.credentials(HTTP_AUTHORIZATION='Api-Key invalid-key')
        
        # Perform GET request
        response = self.client.get(reverse('performance-metrics'))  
        
        # Assert the response status code
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_monitor_api_view_without_api_key(self):
        """Test MonitorAPIView without providing an API key"""
        # Perform GET request without API key
        response = self.client.get(reverse('performance-metrics'))  
        
        # Assert the response status code
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_monitor_api_view_metrics_calculation(self):
        """Test metrics calculation logic in MonitorAPIView"""
        # Include the API key in the headers
        self.client.credentials(HTTP_AUTHORIZATION=f'Api-Key {self.key}')
        
        # Perform GET request
        response = self.client.get(reverse('performance-metrics')) 
        response_data = response.json()

        # Assertions for endpoint-specific counts
        endpoint_counts = response_data['request_count_by_endpoint']
        self.assertEqual(endpoint_counts['email'], 2)
        self.assertEqual(endpoint_counts['sms'], 1)
        self.assertEqual(endpoint_counts['in-app'], 1)

        # Assertions for client-specific counts (if implemented in model)
        client_counts = response_data['request_count_by_client']
        self.assertEqual(client_counts[str(self.sender.name)], 4) 

    def test_monitor_api_view_no_requests(self):
        """Test MonitorAPIView with no request logs"""
        # Clear all RequestLog entries
        RequestLog.objects.all().delete()

        # Include the API key in the headers
        self.client.credentials(HTTP_AUTHORIZATION=f'Api-Key {self.key}')
        
        # Perform GET request
        response = self.client.get(reverse('performance-metrics'))  
        response_data = response.json()

        # Assertions for metrics
        self.assertEqual(response_data['total_requests'], 0)
        self.assertEqual(response_data['success_count'], 0)
        self.assertEqual(response_data['failure_count'], 0)
        self.assertEqual(response_data['success_rate'], 0)
        self.assertEqual(response_data['failure_rate'], 0)


class APIKeyListViewTest(TestCase):
    def setUp(self):
        # Set up test data
        self.client = APIClient()
        
        # Create an API key for authentication
        self.api_key, self.key = APIKey.objects.create_key(name="Test Admin Key")
        
        # Create some test API keys
        self.api_key1, self.key1 = APIKey.objects.create_key(name="Test Key 1")
        self.api_key2, self.key2 = APIKey.objects.create_key(name="Test Key 2")

    def test_api_key_list_view_with_valid_api_key(self):
        # Include the API key in the headers
        self.client.credentials(HTTP_AUTHORIZATION=f'Api-Key {self.key}')
        
        # Perform GET request
        response = self.client.get(reverse('api-key-list'))  
        
        # Assert the response status code
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Assert the data returned
        response_data = response.json()
        self.assertEqual(len(response_data), 3)  # Three (including one for authentication) API keys created
        self.assertEqual(response_data[2]['name'], "Test Admin Key")
        self.assertEqual(response_data[1]['name'], "Test Key 1")
        self.assertEqual(response_data[0]['name'], "Test Key 2")
        self.assertIn('id', response_data[0])  # Check if 'id' field is present
        self.assertIn('name', response_data[0])  # Check if 'name' field is present

    def test_api_key_list_view_with_invalid_api_key(self):
        # Include an invalid API key in the headers
        self.client.credentials(HTTP_AUTHORIZATION='Api-Key invalid-key')
        
        # Perform GET request
        response = self.client.get(reverse('api-key-list'))  
        
        # Assert the response status code
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
