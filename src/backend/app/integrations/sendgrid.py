import typing
import json
import base64
from sendgrid import SendGridAPIClient  # ^6.9.0
from sendgrid.helpers.mail import Mail, Attachment, Content, Email, MailSettings, TrackingSettings  # ^6.9.0

from ..core.config import settings
from ..utils.logging_utils import get_component_logger, mask_sensitive_data
from ..utils.email_utils import format_email_address, get_plain_text_from_html
from ..monitoring.logging import log_performance, PerformanceLoggingContext

# Initialize logger
logger = get_component_logger('sendgrid_integration')


class SendGridException(Exception):
    """Exception raised for SendGrid-specific errors"""
    
    def __init__(self, message, status_code=None, response_body=None):
        """Initializes the SendGrid exception with error details

        Args:
            message (str): Error message
            status_code (int): HTTP status code from SendGrid API
            response_body (dict): Response body from SendGrid API
        """
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body


class SendGridClient:
    """Client for interacting with the SendGrid API to send emails"""
    
    def __init__(self, api_key=None, default_from_email=None, default_from_name=None):
        """Initializes the SendGrid client with API key and default sender
        
        Args:
            api_key (str): SendGrid API key, defaults to settings.SENDGRID_API_KEY
            default_from_email (str): Default sender email, defaults to settings.EMAIL_FROM
            default_from_name (str): Default sender name, defaults to settings.EMAIL_FROM_NAME
        """
        self._api_key = api_key or settings.SENDGRID_API_KEY
        self._default_from_email = default_from_email or settings.EMAIL_FROM
        self._default_from_name = default_from_name or settings.EMAIL_FROM_NAME
        self._initialized = False
        self._client = None
        
        logger.info(f"SendGrid client initialized with default sender: {mask_sensitive_data(self._default_from_email)}")
    
    def initialize(self):
        """Lazily initializes the SendGrid API client when first needed"""
        if self._initialized:
            return
        
        self._client = SendGridAPIClient(self._api_key)
        self._initialized = True
        logger.info("SendGrid API client successfully initialized")
    
    def send_email(self, to_email, subject, html_content, from_email=None, from_name=None, 
                  cc=None, bcc=None, attachments=None, categories=None, custom_args=None):
        """Sends an email using the SendGrid API
        
        Args:
            to_email (str): Recipient email address
            subject (str): Email subject line
            html_content (str): HTML content of the email
            from_email (str): Sender email address, defaults to default_from_email
            from_name (str): Sender name, defaults to default_from_name
            cc (list): List of CC recipients
            bcc (list): List of BCC recipients
            attachments (list): List of file attachments
            categories (list): Categories for email tracking
            custom_args (dict): Custom arguments for SendGrid
            
        Returns:
            dict: Response from SendGrid API with status and message
        """
        # Ensure client is initialized
        self.initialize()
        
        try:
            # Format from email address
            sender = format_email_address(
                from_email or self._default_from_email, 
                from_name or self._default_from_name
            )
            
            # Create plain text version from HTML
            plain_text_content = get_plain_text_from_html(html_content)
            
            # Create mail object
            message = Mail(
                from_email=sender,
                to_emails=to_email,
                subject=subject
            )
            
            # Add HTML content
            message.add_content(Content("text/html", html_content))
            
            # Add plain text content
            if plain_text_content:
                message.add_content(Content("text/plain", plain_text_content))
            
            # Add CC recipients if provided
            if cc:
                for cc_recipient in cc:
                    message.add_cc(cc_recipient)
            
            # Add BCC recipients if provided
            if bcc:
                for bcc_recipient in bcc:
                    message.add_bcc(bcc_recipient)
            
            # Add attachments if provided
            if attachments:
                for attachment_data in attachments:
                    if isinstance(attachment_data, dict):
                        # Attachment is already a dict with required fields
                        attachment = self.create_attachment(**attachment_data)
                    else:
                        # Assume attachment_data is a tuple of (file_content, filename, mime_type)
                        file_content, filename, mime_type = attachment_data[:3]
                        disposition = attachment_data[3] if len(attachment_data) > 3 else 'attachment'
                        content_id = attachment_data[4] if len(attachment_data) > 4 else None
                        attachment = self.create_attachment(
                            file_content, filename, mime_type, disposition, content_id
                        )
                    message.add_attachment(attachment)
            
            # Add categories if provided
            if categories:
                for category in categories:
                    message.add_category(category)
            
            # Add custom arguments if provided
            if custom_args:
                for key, value in custom_args.items():
                    message.add_custom_arg(key, value)
            
            # Configure tracking settings
            tracking_settings = TrackingSettings()
            tracking_settings.open_tracking.enable = True
            tracking_settings.click_tracking.enable = True
            message.tracking_settings = tracking_settings
            
            # Send the email and track performance
            with PerformanceLoggingContext("sendgrid_send_email", {"to": mask_sensitive_data(to_email)}):
                response = self._client.send(message)
            
            logger.info(
                f"Email sent successfully to {mask_sensitive_data(to_email)} with subject: {subject}",
                extra={"status_code": response.status_code}
            )
            
            return {
                "status": "success",
                "message": "Email sent successfully",
                "status_code": response.status_code
            }
            
        except Exception as e:
            error_message = f"Failed to send email to {mask_sensitive_data(to_email)}: {str(e)}"
            logger.error(error_message, exc_info=True)
            
            status_code = None
            response_body = None
            
            # If it's a SendGrid API error, extract status code and response body
            if hasattr(e, 'status_code'):
                status_code = e.status_code
            if hasattr(e, 'body'):
                try:
                    response_body = json.loads(e.body)
                except (json.JSONDecodeError, AttributeError):
                    response_body = {"raw": str(e.body) if hasattr(e, 'body') else None}
            
            return {
                "status": "error",
                "message": str(e),
                "status_code": status_code,
                "response_body": response_body
            }
    
    def send_template_email(self, to_email, template_id, dynamic_data=None, subject=None,
                           from_email=None, from_name=None, cc=None, bcc=None,
                           attachments=None, categories=None, custom_args=None):
        """Sends an email using a SendGrid dynamic template
        
        Args:
            to_email (str): Recipient email address
            template_id (str): SendGrid template ID
            dynamic_data (dict): Dynamic template data
            subject (str): Optional subject line (may be defined in template)
            from_email (str): Sender email address, defaults to default_from_email
            from_name (str): Sender name, defaults to default_from_name
            cc (list): List of CC recipients
            bcc (list): List of BCC recipients
            attachments (list): List of file attachments
            categories (list): Categories for email tracking
            custom_args (dict): Custom arguments for SendGrid
            
        Returns:
            dict: Response from SendGrid API with status and message
        """
        # Ensure client is initialized
        self.initialize()
        
        try:
            # Format from email address
            sender = format_email_address(
                from_email or self._default_from_email, 
                from_name or self._default_from_name
            )
            
            # Create mail object with minimal required fields
            message = Mail(from_email=sender, to_emails=to_email)
            
            # Set subject if provided
            if subject:
                message.subject = subject
            
            # Set template ID
            message.template_id = template_id
            
            # Add dynamic template data if provided
            if dynamic_data:
                message.dynamic_template_data = dynamic_data
            
            # Add CC recipients if provided
            if cc:
                for cc_recipient in cc:
                    message.add_cc(cc_recipient)
            
            # Add BCC recipients if provided
            if bcc:
                for bcc_recipient in bcc:
                    message.add_bcc(bcc_recipient)
            
            # Add attachments if provided
            if attachments:
                for attachment_data in attachments:
                    if isinstance(attachment_data, dict):
                        # Attachment is already a dict with required fields
                        attachment = self.create_attachment(**attachment_data)
                    else:
                        # Assume attachment_data is a tuple of (file_content, filename, mime_type)
                        file_content, filename, mime_type = attachment_data[:3]
                        disposition = attachment_data[3] if len(attachment_data) > 3 else 'attachment'
                        content_id = attachment_data[4] if len(attachment_data) > 4 else None
                        attachment = self.create_attachment(
                            file_content, filename, mime_type, disposition, content_id
                        )
                    message.add_attachment(attachment)
            
            # Add categories if provided
            if categories:
                for category in categories:
                    message.add_category(category)
            
            # Add custom arguments if provided
            if custom_args:
                for key, value in custom_args.items():
                    message.add_custom_arg(key, value)
            
            # Configure tracking settings
            tracking_settings = TrackingSettings()
            tracking_settings.open_tracking.enable = True
            tracking_settings.click_tracking.enable = True
            message.tracking_settings = tracking_settings
            
            # Send the email and track performance
            with PerformanceLoggingContext("sendgrid_send_template_email", {"to": mask_sensitive_data(to_email)}):
                response = self._client.send(message)
            
            logger.info(
                f"Template email sent successfully to {mask_sensitive_data(to_email)} with template: {template_id}",
                extra={"status_code": response.status_code}
            )
            
            return {
                "status": "success",
                "message": "Template email sent successfully",
                "status_code": response.status_code
            }
            
        except Exception as e:
            error_message = f"Failed to send template email to {mask_sensitive_data(to_email)}: {str(e)}"
            logger.error(error_message, exc_info=True)
            
            status_code = None
            response_body = None
            
            # If it's a SendGrid API error, extract status code and response body
            if hasattr(e, 'status_code'):
                status_code = e.status_code
            if hasattr(e, 'body'):
                try:
                    response_body = json.loads(e.body)
                except (json.JSONDecodeError, AttributeError):
                    response_body = {"raw": str(e.body) if hasattr(e, 'body') else None}
            
            return {
                "status": "error",
                "message": str(e),
                "status_code": status_code,
                "response_body": response_body
            }
    
    def create_attachment(self, file_content, filename, mime_type, disposition='attachment', content_id=None):
        """Creates an email attachment from file data
        
        Args:
            file_content (bytes): Binary content of the file
            filename (str): Name of the file
            mime_type (str): MIME type of the file
            disposition (str): Attachment disposition (attachment or inline)
            content_id (str): Content ID for inline images
            
        Returns:
            Attachment: SendGrid Attachment object
        """
        encoded_content = base64.b64encode(file_content).decode()
        
        attachment = Attachment()
        attachment.file_content = encoded_content
        attachment.file_name = filename
        attachment.file_type = mime_type
        attachment.disposition = disposition
        
        if content_id:
            attachment.content_id = content_id
        
        return attachment
    
    def get_email_stats(self, start_date, end_date=None, aggregated_by=None):
        """Retrieves email sending statistics from SendGrid
        
        Args:
            start_date (str): Start date in YYYY-MM-DD format
            end_date (str): End date in YYYY-MM-DD format (defaults to current date)
            aggregated_by (str): Aggregation period (day, week, month)
            
        Returns:
            dict: Email statistics from SendGrid API
        """
        # Ensure client is initialized
        self.initialize()
        
        try:
            # Prepare query parameters
            query_params = {
                'start_date': start_date
            }
            
            if end_date:
                query_params['end_date'] = end_date
                
            if aggregated_by:
                query_params['aggregated_by'] = aggregated_by
            
            # Make API request
            with PerformanceLoggingContext("sendgrid_get_stats"):
                response = self._client.client.stats.get(query_params=query_params)
            
            # Parse response
            stats_data = json.loads(response.body)
            
            logger.info(f"Email statistics retrieved successfully for period {start_date} to {end_date or 'now'}")
            
            return {
                "status": "success",
                "message": "Statistics retrieved successfully",
                "data": stats_data
            }
            
        except Exception as e:
            error_message = f"Failed to retrieve email statistics: {str(e)}"
            logger.error(error_message, exc_info=True)
            
            status_code = None
            response_body = None
            
            # If it's a SendGrid API error, extract status code and response body
            if hasattr(e, 'status_code'):
                status_code = e.status_code
            if hasattr(e, 'body'):
                try:
                    response_body = json.loads(e.body)
                except (json.JSONDecodeError, AttributeError):
                    response_body = {"raw": str(e.body) if hasattr(e, 'body') else None}
            
            return {
                "status": "error",
                "message": str(e),
                "status_code": status_code,
                "response_body": response_body
            }