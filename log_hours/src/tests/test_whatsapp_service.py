import os
import unittest
from unittest.mock import patch, MagicMock, mock_open
import tempfile
import requests
from datetime import datetime

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from services.whatsapp_service import WhatsAppService


class TestWhatsAppService(unittest.TestCase):
    """Test cases for WhatsAppService class"""

    def setUp(self):
        """Set up test fixtures"""
        # Mock environment variables for testing
        self.env_patcher = patch.dict(os.environ, {
            'WHATSAPP_API_URL': 'https://test-api.example.com',
            'WHATSAPP_API_KEY': 'test-api-key',
            'WHATSAPP_INSTANCE': 'test-instance',
            'WHATSAPP_RECIPIENT': '1234567890@c.us',
            'WHATSAPP_ENABLED': 'true'
        })
        self.env_patcher.start()

    def tearDown(self):
        """Clean up test fixtures"""
        self.env_patcher.stop()

    def test_init_with_valid_config(self):
        """Test WhatsAppService initialization with valid configuration"""
        service = WhatsAppService()
        
        self.assertEqual(service.api_url, 'https://test-api.example.com')
        self.assertEqual(service.api_key, 'test-api-key')
        self.assertEqual(service.instance, 'test-instance')
        self.assertEqual(service.default_recipient, '1234567890@c.us')
        self.assertTrue(service.enabled)

    @patch.dict(os.environ, {'WHATSAPP_ENABLED': 'false'})
    def test_init_with_disabled_service(self):
        """Test WhatsAppService initialization when disabled"""
        service = WhatsAppService()
        self.assertFalse(service.enabled)

    @patch.dict(os.environ, {}, clear=True)
    def test_init_with_missing_config(self):
        """Test WhatsAppService initialization with missing configuration"""
        with patch.dict(os.environ, {'WHATSAPP_ENABLED': 'true'}, clear=True):
            service = WhatsAppService()
            self.assertFalse(service.enabled)  # Should be disabled due to missing config
    
    @patch.dict(os.environ, {'WHATSAPP_RECIPIENT': ''})
    def test_init_with_missing_recipient(self):
        """Test WhatsAppService initialization with missing recipient"""
        service = WhatsAppService()
        self.assertFalse(service.enabled)  # Should be disabled due to missing recipient

    @patch('services.whatsapp_service.requests.Session.post')
    def test_send_text_message_success(self, mock_post):
        """Test successful text message sending"""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        service = WhatsAppService()
        result = service.send_text_message("Test message", "1234567890@c.us")

        self.assertTrue(result)
        mock_post.assert_called_once()
        
        # Check the call arguments - verify the new payload structure
        call_args = mock_post.call_args
        self.assertIn('1234567890@c.us', str(call_args))
        self.assertIn('Test message', str(call_args))
        # Verify the payload structure matches the new format
        payload = call_args.kwargs['json']
        self.assertEqual(payload['number'], '1234567890@c.us')
        self.assertEqual(payload['text'], f'Work Logger - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: Test message')

    @patch('services.whatsapp_service.requests.Session.post')
    def test_send_text_message_failure(self, mock_post):
        """Test failed text message sending"""
        # Mock failed response
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_post.return_value = mock_response

        service = WhatsAppService()
        result = service.send_text_message("Test message")

        self.assertFalse(result)
    
    @patch('services.whatsapp_service.requests.Session.post')
    def test_send_text_message_success_201(self, mock_post):
        """Test successful text message sending with 201 status code"""
        # Mock successful response with 201 (also valid 2xx)
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_post.return_value = mock_response

        service = WhatsAppService()
        result = service.send_text_message("Test message", "1234567890@c.us")

        self.assertTrue(result)  # Should succeed with any 2xx status

    @patch('services.whatsapp_service.requests.Session.post')
    def test_send_text_message_exception(self, mock_post):
        """Test text message sending with request exception"""
        mock_post.side_effect = requests.exceptions.RequestException("Connection error")

        service = WhatsAppService()
        result = service.send_text_message("Test message")

        self.assertFalse(result)

    def test_send_text_message_disabled_service(self):
        """Test text message sending when service is disabled"""
        with patch.dict(os.environ, {'WHATSAPP_ENABLED': 'false'}):
            service = WhatsAppService()
            result = service.send_text_message("Test message")
            self.assertFalse(result)

    def test_send_text_message_no_recipient(self):
        """Test text message sending without recipient"""
        with patch.dict(os.environ, {'WHATSAPP_RECIPIENT': ''}, clear=False):
            # Need to create service after environment is patched
            service = WhatsAppService()
            # Service should be disabled due to missing recipient
            self.assertFalse(service.enabled)
            result = service.send_text_message("Test message")
            self.assertFalse(result)

    @patch('services.whatsapp_service.requests.Session.post')
    @patch('builtins.open', new_callable=mock_open, read_data=b'fake image data')
    @patch('os.path.exists')
    @patch('services.whatsapp_service.MimeTypes')
    def test_send_image_success(self, mock_mimetypes, mock_exists, mock_file, mock_post):
        """Test successful image sending"""
        mock_exists.return_value = True
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        # Mock MimeTypes
        mock_mime_instance = MagicMock()
        mock_mime_instance.guess_type.return_value = ('image/png', None)
        mock_mimetypes.return_value = mock_mime_instance

        service = WhatsAppService()
        result = service.send_image("/fake/path/image.png", "Test caption")

        self.assertTrue(result)
        mock_post.assert_called_once()
        
        # Verify the payload structure includes mimeType
        payload = mock_post.call_args.kwargs['json']
        self.assertEqual(payload['mediatype'], 'image')
        self.assertEqual(payload['mimeType'], 'image/png')
        self.assertEqual(payload['caption'], 'Test caption')

    @patch('os.path.exists')
    def test_send_image_file_not_found(self, mock_exists):
        """Test image sending with non-existent file"""
        mock_exists.return_value = False

        service = WhatsAppService()
        result = service.send_image("/fake/path/image.png")

        self.assertFalse(result)
    
    @patch('services.whatsapp_service.requests.Session.post')
    @patch('builtins.open', new_callable=mock_open, read_data=b'fake image data')
    @patch('os.path.exists')
    @patch('services.whatsapp_service.MimeTypes')
    def test_send_image_success_202(self, mock_mimetypes, mock_exists, mock_file, mock_post):
        """Test successful image sending with 202 status code"""
        mock_exists.return_value = True
        mock_response = MagicMock()
        mock_response.status_code = 202  # Another valid 2xx status
        mock_post.return_value = mock_response
        
        # Mock MimeTypes
        mock_mime_instance = MagicMock()
        mock_mime_instance.guess_type.return_value = ('image/jpeg', None)
        mock_mimetypes.return_value = mock_mime_instance

        service = WhatsAppService()
        result = service.send_image("/fake/path/image.jpg", "Test caption")

        self.assertTrue(result)  # Should succeed with any 2xx status

    @patch('services.whatsapp_service.requests.Session.post')
    @patch('builtins.open', new_callable=mock_open, read_data=b'fake document data')
    @patch('os.path.exists')
    @patch('services.whatsapp_service.MimeTypes')
    def test_send_document_success(self, mock_mimetypes, mock_exists, mock_file, mock_post):
        """Test successful document sending"""
        mock_exists.return_value = True
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        # Mock MimeTypes
        mock_mime_instance = MagicMock()
        mock_mime_instance.guess_type.return_value = ('application/pdf', None)
        mock_mimetypes.return_value = mock_mime_instance

        service = WhatsAppService()
        result = service.send_document("/fake/path/document.pdf", "Test caption")

        self.assertTrue(result)
        mock_post.assert_called_once()
        
        # Verify the payload structure includes mimeType
        payload = mock_post.call_args.kwargs['json']
        self.assertEqual(payload['mediatype'], 'document')
        self.assertEqual(payload['mimeType'], 'application/pdf')
        self.assertEqual(payload['caption'], 'Test caption')
    
    @patch('services.whatsapp_service.requests.Session.post')
    @patch('builtins.open', new_callable=mock_open, read_data=b'fake document data')
    @patch('os.path.exists')
    @patch('services.whatsapp_service.MimeTypes')
    def test_send_document_unknown_mimetype(self, mock_mimetypes, mock_exists, mock_file, mock_post):
        """Test document sending with unknown mime type"""
        mock_exists.return_value = True
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        # Mock MimeTypes to return None (unknown type)
        mock_mime_instance = MagicMock()
        mock_mime_instance.guess_type.return_value = (None, None)
        mock_mimetypes.return_value = mock_mime_instance

        service = WhatsAppService()
        result = service.send_document("/fake/path/unknown.xyz", "Test caption")

        self.assertTrue(result)
        
        # Should default to application/pdf for unknown document types
        payload = mock_post.call_args.kwargs['json']
        self.assertEqual(payload['mimeType'], 'application/pdf')
    
    @patch('services.whatsapp_service.requests.Session.post')
    @patch('builtins.open', new_callable=mock_open, read_data=b'fake image data')
    @patch('os.path.exists')
    @patch('services.whatsapp_service.MimeTypes')
    def test_send_image_unknown_mimetype(self, mock_mimetypes, mock_exists, mock_file, mock_post):
        """Test image sending with unknown mime type"""
        mock_exists.return_value = True
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        # Mock MimeTypes to return None (unknown type)
        mock_mime_instance = MagicMock()
        mock_mime_instance.guess_type.return_value = (None, None)
        mock_mimetypes.return_value = mock_mime_instance

        service = WhatsAppService()
        result = service.send_image("/fake/path/unknown.xyz", "Test caption")

        self.assertTrue(result)
        
        # Should default to image/png for unknown image types
        payload = mock_post.call_args.kwargs['json']
        self.assertEqual(payload['mimeType'], 'image/png')

    @patch('services.whatsapp_service.WhatsAppService.send_text_message')
    @patch('services.whatsapp_service.WhatsAppService.send_image')
    def test_send_success_notification(self, mock_send_image, mock_send_text):
        """Test success notification sending"""
        mock_send_text.return_value = True
        mock_send_image.return_value = True

        service = WhatsAppService()
        result = service.send_success_notification(
            "2024-01-15", 
            "/fake/screenshot.png", 
            "8 hours logged"
        )

        self.assertTrue(result)
        mock_send_text.assert_called_once()
        mock_send_image.assert_called_once()

        # Check the message content
        call_args = mock_send_text.call_args[0][0]
        self.assertIn("✅ Hours logged successfully", call_args)
        self.assertIn("2024-01-15", call_args)
        self.assertIn("8 hours logged", call_args)

    @patch('services.whatsapp_service.WhatsAppService.send_text_message')
    @patch('services.whatsapp_service.WhatsAppService.send_image')
    @patch('os.path.exists')
    def test_send_error_notification(self, mock_exists, mock_send_image, mock_send_text):
        """Test error notification sending"""
        mock_exists.return_value = True
        mock_send_text.return_value = True
        mock_send_image.return_value = True

        service = WhatsAppService()
        result = service.send_error_notification(
            "2024-01-15", 
            "Login failed", 
            "/fake/error_screenshot.png"
        )

        self.assertTrue(result)
        mock_send_text.assert_called_once()
        mock_send_image.assert_called_once()

        # Check the message content
        call_args = mock_send_text.call_args[0][0]
        self.assertIn("❌ Failed to log hours", call_args)
        self.assertIn("2024-01-15", call_args)
        self.assertIn("Login failed", call_args)

    @patch('services.whatsapp_service.WhatsAppService.send_text_message')
    @patch('services.whatsapp_service.WhatsAppService.send_image')
    @patch('os.path.exists')
    def test_send_debug_notification(self, mock_exists, mock_send_image, mock_send_text):
        """Test debug notification sending"""
        mock_exists.return_value = True
        mock_send_text.return_value = True
        mock_send_image.return_value = True

        service = WhatsAppService()
        result = service.send_debug_notification(
            "2024-01-15", 
            "Element not found", 
            "/fake/debug_screenshot.png"
        )

        self.assertTrue(result)
        mock_send_text.assert_called_once()
        mock_send_image.assert_called_once()

        # Check the message content
        call_args = mock_send_text.call_args[0][0]
        self.assertIn("🔧 Debug info", call_args)
        self.assertIn("2024-01-15", call_args)
        self.assertIn("Element not found", call_args)

    @patch('services.whatsapp_service.requests.Session.get')
    def test_test_connection_success(self, mock_get):
        """Test successful connection test"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        service = WhatsAppService()
        result = service.test_connection()

        self.assertTrue(result)
        mock_get.assert_called_once()

    @patch('services.whatsapp_service.requests.Session.get')
    def test_test_connection_failure(self, mock_get):
        """Test failed connection test"""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        service = WhatsAppService()
        result = service.test_connection()

        self.assertFalse(result)

    @patch('services.whatsapp_service.requests.Session.get')
    def test_test_connection_exception(self, mock_get):
        """Test connection test with exception"""
        mock_get.side_effect = requests.exceptions.RequestException("Connection error")

        service = WhatsAppService()
        result = service.test_connection()

        self.assertFalse(result)

    def test_test_connection_disabled_service(self):
        """Test connection test when service is disabled"""
        with patch.dict(os.environ, {'WHATSAPP_ENABLED': 'false'}):
            service = WhatsAppService()
            result = service.test_connection()
            self.assertFalse(result)

    @patch('services.whatsapp_service.WhatsAppService.send_text_message')
    def test_partial_success_notification(self, mock_send_text):
        """Test that partial success still sends text even if image fails"""
        mock_send_text.return_value = True

        service = WhatsAppService()
        
        with patch.object(service, 'send_image', return_value=False):
            result = service.send_success_notification(
                "2024-01-15", 
                "/fake/screenshot.png"
            )
            # Should return False because image sending failed
            self.assertFalse(result)
            # But text message should still be sent
            mock_send_text.assert_called_once()


if __name__ == '__main__':
    unittest.main()