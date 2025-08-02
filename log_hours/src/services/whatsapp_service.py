import base64
import logging
from mimetypes import MimeTypes
import os
from typing import Optional, Dict
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class WhatsAppService:
    """WhatsApp service using Evolution API for sending messages and media"""
    
    def __init__(self):
        self.api_url = os.getenv("WHATSAPP_API_URL")
        self.api_key = os.getenv("WHATSAPP_API_KEY")
        self.instance = os.getenv("WHATSAPP_INSTANCE")
        self.default_recipient = os.getenv("WHATSAPP_RECIPIENT")
        self.enabled = os.getenv("WHATSAPP_ENABLED", "false").lower() == "true"
        
        # Validate configuration
        self._validate_config()
        
        # Setup session with retry strategy
        self.session = self._setup_session()
    
    def _validate_config(self):
        """Validate WhatsApp service configuration"""
        if not self.enabled:
            logger.info("🔕 WhatsApp notifications are disabled")
            return
            
        missing_vars = []
        if not self.api_url:
            missing_vars.append("WHATSAPP_API_URL")
        if not self.api_key:
            missing_vars.append("WHATSAPP_API_KEY")
        if not self.instance:
            missing_vars.append("WHATSAPP_INSTANCE")
        if not self.default_recipient:
            missing_vars.append("WHATSAPP_RECIPIENT")
            
        if missing_vars:
            logger.error(f"❌ Missing required WhatsApp environment variables: {', '.join(missing_vars)}")
            self.enabled = False
        else:
            logger.info(f"✅ WhatsApp service configured for instance: {self.instance}")
    
    def _setup_session(self) -> requests.Session:
        """Setup requests session with retry strategy and headers"""
        session = requests.Session()
        
        # Retry strategy
        retry_strategy = Retry(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "POST"],
            backoff_factor=1
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Default headers
        session.headers.update({
            "Content-Type": "application/json",
            "apikey": self.api_key,
        })
        
        return session
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests"""
        return {
            "Content-Type": "application/json",
            "apikey": self.api_key,
        }
    
    def send_text_message(self, message: str, recipient: Optional[str] = None) -> bool:
        """
        Send a text message via WhatsApp
        
        Args:
            message: The text message to send
            recipient: Phone number or group ID (optional, uses default if not provided)
            
        Returns:
            bool: True if message sent successfully, False otherwise
        """
        if not self.enabled:
            logger.debug("WhatsApp service is disabled, skipping message")
            return False
            
        recipient = recipient or self.default_recipient
        if not recipient:
            logger.error("❌ No recipient specified for WhatsApp message")
            return False
        
        url = f"{self.api_url}/message/sendText/{self.instance}"
        
        payload = {
            "number": recipient,
            "text": message,
        }
        
        try:
            logger.info(f"📱 Sending WhatsApp text message to {recipient}")
            response = self.session.post(url, json=payload, timeout=30)
            
            if str(response.status_code).startswith("2"):
                logger.info("✅ WhatsApp text message sent successfully")
                return True
            else:
                logger.error(f"❌ Failed to send WhatsApp message: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error sending WhatsApp message: {str(e)}")
            return False
    
    def send_image(self, image_path: str, caption: str = "", recipient: Optional[str] = None) -> bool:
        """
        Send an image via WhatsApp
        
        Args:
            image_path: Path to the image file
            caption: Optional caption for the image
            recipient: Phone number or group ID (optional, uses default if not provided)
            
        Returns:
            bool: True if image sent successfully, False otherwise
        """
        if not self.enabled:
            logger.debug("WhatsApp service is disabled, skipping image")
            return False
            
        recipient = recipient or self.default_recipient
        if not recipient:
            logger.error("❌ No recipient specified for WhatsApp image")
            return False
        
        if not os.path.exists(image_path):
            logger.error(f"❌ Image file not found: {image_path}")
            return False
        
        try:
            # Read and encode image
            with open(image_path, "rb") as image_file:
                image_data = image_file.read()
                image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            url = f"{self.api_url}/message/sendMedia/{self.instance}"
            
            payload = {
                "number": recipient,
                "mediatype": "image",
                "mimeType": MimeTypes().guess_type(image_path)[0] or "image/png",
                "media": image_base64,
                "caption": caption,
                "fileName": os.path.basename(image_path)
            }
            
            logger.info(f"📱 Sending WhatsApp image to {recipient}: {os.path.basename(image_path)}")
            response = self.session.post(url, json=payload, timeout=60)
            
            if str(response.status_code).startswith("2"):
                logger.info("✅ WhatsApp image sent successfully")
                return True
            else:
                logger.error(f"❌ Failed to send WhatsApp image: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error sending WhatsApp image: {str(e)}")
            return False
    
    def send_document(self, file_path: str, caption: str = "", recipient: Optional[str] = None) -> bool:
        """
        Send a document via WhatsApp
        
        Args:
            file_path: Path to the document file
            caption: Optional caption for the document
            recipient: Phone number or group ID (optional, uses default if not provided)
            
        Returns:
            bool: True if document sent successfully, False otherwise
        """
        if not self.enabled:
            logger.debug("WhatsApp service is disabled, skipping document")
            return False
            
        recipient = recipient or self.default_recipient
        if not recipient:
            logger.error("❌ No recipient specified for WhatsApp document")
            return False
        
        if not os.path.exists(file_path):
            logger.error(f"❌ Document file not found: {file_path}")
            return False
        
        try:
            # Read and encode document
            with open(file_path, "rb") as doc_file:
                doc_data = doc_file.read()
                doc_base64 = base64.b64encode(doc_data).decode('utf-8')
            
            url = f"{self.api_url}/message/sendMedia/{self.instance}"
            
            payload = {
                "number": recipient,
                "mediatype": "document",
                "mimeType": MimeTypes().guess_type(file_path)[0] or "application/pdf",
                "media": doc_base64,
                "caption": caption,
                "fileName": os.path.basename(file_path)
            }
            
            logger.info(f"📱 Sending WhatsApp document to {recipient}: {os.path.basename(file_path)}")
            response = self.session.post(url, json=payload, timeout=60)
            
            if str(response.status_code).startswith("2"):
                logger.info("✅ WhatsApp document sent successfully")
                return True
            else:
                logger.error(f"❌ Failed to send WhatsApp document: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error sending WhatsApp document: {str(e)}")
            return False
    
    def send_success_notification(self, date: str, screenshot_path: str, hours_logged: str = "") -> bool:
        """
        Send success notification with screenshot
        
        Args:
            date: The date for which hours were logged
            screenshot_path: Path to the verification screenshot
            hours_logged: Optional details about hours logged
            
        Returns:
            bool: True if notification sent successfully, False otherwise
        """
        message = f"✅ Hours logged successfully for {date}"
        if hours_logged:
            message += f"\n📊 {hours_logged}"
        message += "\n📸 Verification screenshot attached"
        
        # Send text message first
        text_sent = self.send_text_message(message)
        
        # Send screenshot
        screenshot_sent = self.send_image(screenshot_path, f"Verification screenshot for {date}")
        
        return text_sent and screenshot_sent
    
    def send_error_notification(self, date: str, error_message: str, screenshot_path: Optional[str] = None) -> bool:
        """
        Send error notification with optional screenshot
        
        Args:
            date: The date for which the error occurred
            error_message: Description of the error
            screenshot_path: Optional path to error screenshot
            
        Returns:
            bool: True if notification sent successfully, False otherwise
        """
        message = f"❌ Failed to log hours for {date}\n🔍 Error: {error_message}"
        if screenshot_path:
            message += "\n📸 Debug screenshot attached"
        
        # Send text message
        text_sent = self.send_text_message(message)
        
        # Send screenshot if available
        screenshot_sent = True
        if screenshot_path and os.path.exists(screenshot_path):
            screenshot_sent = self.send_image(screenshot_path, f"Error screenshot for {date}")
        
        return text_sent and screenshot_sent
    
    def send_debug_notification(self, date: str, debug_info: str, screenshot_path: Optional[str] = None) -> bool:
        """
        Send debug notification with optional screenshot
        
        Args:
            date: The date for which debug info is provided
            debug_info: Debug information
            screenshot_path: Optional path to debug screenshot
            
        Returns:
            bool: True if notification sent successfully, False otherwise
        """
        message = f"🔧 Debug info for {date}\n{debug_info}"
        if screenshot_path:
            message += "\n📸 Screenshot saved for troubleshooting"
        
        # Send text message
        text_sent = self.send_text_message(message)
        
        # Send screenshot if available
        screenshot_sent = True
        if screenshot_path and os.path.exists(screenshot_path):
            screenshot_sent = self.send_image(screenshot_path, f"Debug screenshot for {date}")
        
        return text_sent and screenshot_sent
    
    def test_connection(self) -> bool:
        """
        Test WhatsApp API connection
        
        Returns:
            bool: True if connection is successful, False otherwise
        """
        if not self.enabled:
            logger.info("WhatsApp service is disabled")
            return False
        
        try:
            # Test with a simple API status check
            url = f"{self.api_url}"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                logger.info("✅ WhatsApp API connection test successful")
                return True
            else:
                logger.error(f"❌ WhatsApp API connection test failed: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ WhatsApp API connection test failed: {str(e)}")
            return False