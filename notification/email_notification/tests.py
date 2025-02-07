from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch
from django.core.mail import EmailMessage
from rest_framework_api_key.models import APIKey

class SendSingleEmailTest(TestCase):
    def setUp(self):
        # Create API key for authentication
        self.api_key, self.key = APIKey.objects.create_key(name="Test Email Key")
        
        self.url = reverse('send_single_email')  
        self.valid_payload = {
            "subject": "Test Email",
            "message": "This is a test email message.",
            "recipients": "test1@example.com, test2@example.com"
        }
        self.invalid_payload = {
            "message": "This is a test email message.",
            "recipients": "test1@example.com, test2@example.com"
        }

    # Mock the send method  
    @patch('django.core.mail.EmailMessage.send')  
    def test_send_email_success(self, mock_send):
        # Simulate successful email sending
        mock_send.return_value = 1

        # Include API key in headers
        headers = {'HTTP_AUTHORIZATION': f'Api-Key {self.key}'}
        response = self.client.post(self.url, data=self.valid_payload, content_type='application/json', **headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "Email sent successfully"})

        # Ensure the email was called only once
        mock_send.assert_called_once()

    def test_send_email_missing_fields(self):
        # Include API key in headers
        headers = {'HTTP_AUTHORIZATION': f'Api-Key {self.key}'}
        response = self.client.post(self.url, data=self.invalid_payload, content_type='application/json', **headers)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {
            "status": "Missing required fields",
            "error": "subject, message, and recipients are required"
        })
        
    # Mock the send method
    @patch('django.core.mail.EmailMessage.send')  
    def test_send_email_failure(self, mock_send):
        # Simulate an exception being raised during email sending
        mock_send.side_effect = Exception("SMTP server not responding")

        # Include API key in headers
        headers = {'HTTP_AUTHORIZATION': f'Api-Key {self.key}'}
        response = self.client.post(self.url, data=self.valid_payload, content_type='application/json', **headers)
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json(), {
            "status": "Failed to send email",
            "error": "SMTP server not responding"
        })
