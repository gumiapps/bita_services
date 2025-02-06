from django.test import TestCase, override_settings
from django.urls import reverse
from unittest.mock import patch, Mock
from rest_framework_api_key.models import APIKey
import requests

@override_settings(
    SMS_API_KEY='test_api_key',  
    SMS_API_HEADER_FIELD='Authorization',  
    SMS_API_URL='https://api.geezsms.com/api/v1/sms/send',  
    SMS_SHORT_CODE='',  
)
class SendSingleSMSTest(TestCase):

    def setUp(self):
        # Create API key for authentication
        self.api_key, self.key = APIKey.objects.create_key(name="Test Email Key")

        self.url = reverse('single_sms')  
        self.valid_payload = {
            "phone": "+1234567890",
            "message": "This is a test SMS message."
        }
        self.invalid_payload = {
            "message": "This is a test SMS message."
        }

    @patch('requests.post')
    def test_send_sms_success(self, mock_post):
        # Mock the external API response
        mock_response = Mock()
        mock_response.json.return_value = {"error": False, "message": "SMS sent successfully"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        # Include API key in headers
        headers = {'HTTP_AUTHORIZATION': f'Api-Key {self.key}'}
        response = self.client.post(self.url, data=self.valid_payload, content_type='application/json', **headers)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "SMS sent successfully", "error": False, "message": "SMS sent successfully"})

        # Ensure the external API was called with the correct payload and headers
        mock_post.assert_called_once_with(
            'https://api.geezsms.com/api/v1/sms/send',
            json={"phone": "+1234567890", "msg": "This is a test SMS message.", "shortcode_id": ""},
            headers={'Authorization': 'test_api_key'}
        )


    def test_send_sms_missing_fields(self, mock_post):
        # Include API key in headers
        headers = {'HTTP_AUTHORIZATION': f'Api-Key {self.key}'}
        response = self.client.post(self.url, data=self.invalid_payload, content_type='application/json', **headers)
        
        # Assert the response status code and message
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "Missing required fields (phone, message)"})

        # Ensure the external API was not called
        mock_post.assert_not_called()

    @patch('requests.post')
    def test_send_sms_failure(self, mock_post):
        # Mock the external API response to simulate an error
        mock_response = Mock()
        mock_response.json.return_value = {"error": True, "message": "Failed to send SMS"}
        mock_response.raise_for_status.side_effect = requests.exceptions.RequestException("API request failed")
        mock_post.return_value = mock_response

        # Include API key in headers

        headers = {'HTTP_AUTHORIZATION': f'Api-Key {self.key}'}
        response = self.client.post(self.url, data=self.valid_payload, content_type='application/json', **headers)
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error_message": "Failed to send SMS: API request failed", "error": True, "message": "Failed to send SMS"})




@override_settings(
    SMS_API_KEY='test_api_key',  
    SMS_BULK_API_URL='https://api.geezsms.com/api/v1/sms/send/bulk',  
)
class SendBulkSMSTest(TestCase):
    def setUp(self):
        # Create API key for authentication
        self.api_key, self.key = APIKey.objects.create_key(name="Test Bulk SMS Key")
        
        self.url = reverse('bulk_sms')  
        self.valid_payload = {
            "contacts": [
                {"phone_number": "+1234567890", "name": "John Doe"},
                {"phone_number": "+0987654321", "name": "Jane Doe"},
            ],
            "sender_id": "TEST_SENDER",
            "msg": "This is a test bulk SMS message.",
            "notify_url": "https://example.com/notify",
        }
        self.invalid_payload_missing_fields = {
            "contacts": [
                {"phone_number": "+1234567890", "name": "John Doe"},
            ],
            "msg": "This is a test bulk SMS message.",
            # Missing 'notify_url'
        }
        self.invalid_payload_invalid_contacts = {
            "contacts": [
                {"name": "John Doe"},  # Missing 'phone_number'
                {"phone_number": "+0987654321", "name": "Jane Doe"},
            ],
            "sender_id": "TEST_SENDER",
            "msg": "This is a test bulk SMS message.",
            "notify_url": "https://example.com/notify",
        }

    @patch('requests.post')
    def test_send_bulk_sms_success(self, mock_post):
        # Mock the external API response
        mock_response = Mock()
        mock_response.json.return_value = {"error": False, "message": "Bulk SMS sent successfully"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        # Include API key in headers
        headers = {'HTTP_AUTHORIZATION': f'Api-Key {self.key}'}
        response = self.client.post(self.url, data=self.valid_payload, content_type='application/json', **headers)
        
        # Assert the response status code and message
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "status": "Bulk SMS sent successfully",
            "error": False,
            "message": "Bulk SMS sent successfully",
        })

        # Ensure the external API was called with the correct payload and headers
        mock_post.assert_called_once_with(
            'https://api.geezsms.com/api/v1/sms/send/bulk',
            json={
                "token": "test_api_key",
                "contacts": [
                    {"phone_number": "+1234567890", "name": "John Doe"},
                    {"phone_number": "+0987654321", "name": "Jane Doe"},
                ],
                "sender_id": "TEST_SENDER",
                "msg": "This is a test bulk SMS message.",
                "notify_url": "https://example.com/notify",
            },
        )

    @patch('requests.post')
    def test_send_bulk_sms_missing_fields(self, mock_post):
        # Include API key in headers
        headers = {'HTTP_AUTHORIZATION': f'Api-Key {self.key}'}
        response = self.client.post(self.url, data=self.invalid_payload_missing_fields, content_type='application/json', **headers)
        
        # Assert the response status code and message
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "Missing required fields (contacts, msg, notify_url)"})

        # Ensure the external API was not called
        mock_post.assert_not_called()

    @patch('requests.post')
    def test_send_bulk_sms_invalid_contacts(self, mock_post):
        # Include API key in headers
        headers = {'HTTP_AUTHORIZATION': f'Api-Key {self.key}'}
        response = self.client.post(self.url, data=self.invalid_payload_invalid_contacts, content_type='application/json', **headers)
        
        # Assert the response status code and message
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "Each contact must have a 'phone_number' field"})

        # Ensure the external API was not called
        mock_post.assert_not_called()

    @patch('requests.post')
    def test_send_bulk_sms_failure(self, mock_post):
        # Mock the external API response to simulate an error
        mock_response = Mock()
        mock_response.json.return_value = {"error": True, "message": "Failed to send bulk SMS"}
        mock_response.raise_for_status.side_effect = requests.exceptions.RequestException("API request failed")
        mock_post.return_value = mock_response

        # Include API key in headers
        headers = {'HTTP_AUTHORIZATION': f'Api-Key {self.key}'}
        response = self.client.post(self.url, data=self.valid_payload, content_type='application/json', **headers)
        
        # Assert the response status code and message
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {
            "error_message": "Failed to send bulk SMS: API request failed",
            "error": True,
            "message": "Failed to send bulk SMS",
        })
