import os
import typing
import datetime

from ..core.config import settings
from ..core.exceptions import IntegrationException
from ..utils.logging_utils import get_component_logger, mask_sensitive_data
from ..utils.email_utils import (
    EmailTemplate,
    render_template,
    create_email_context,
    generate_email_subject,
    format_email_address
)
from ..integrations.sendgrid import SendGridClient, SendGridException
from ..monitoring.metrics import record_integration_metrics
from ..monitoring.logging import PerformanceLoggingContext

# Initialize logger for email service
logger = get_component_logger('email_service')

class EmailService:
    """Service class for sending emails using configured email provider"""
    
    def __init__(self):
        """Initializes the email service with configuration settings"""
        self._email_client = None
        self._default_from_email = settings.EMAIL_FROM
        self._default_from_name = settings.EMAIL_FROM_NAME
        self._admin_email = settings.ADMIN_EMAIL
        self._initialized = False
        
        logger.info("Email service initialized")
    
    def initialize(self):
        """Lazily initializes the email client when first needed"""
        if self._initialized:
            return
        
        self._email_client = SendGridClient(
            default_from_email=self._default_from_email,
            default_from_name=self._default_from_name
        )
        self._initialized = True
        logger.info("Email client initialized")
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        from_email: str = None,
        from_name: str = None,
        cc: list = None,
        bcc: list = None,
        attachments: list = None,
        categories: list = None,
        custom_args: dict = None,
        trace_id: str = None
    ) -> dict:
        """Sends an email using the configured email provider
        
        Args:
            to_email: Recipient email address
            subject: Email subject line
            html_content: HTML content of the email
            from_email: Sender email address (defaults to configured default)
            from_name: Sender name (defaults to configured default)
            cc: List of CC recipients
            bcc: List of BCC recipients
            attachments: List of file attachments
            categories: Categories for email tracking
            custom_args: Custom arguments for email provider
            trace_id: Trace ID for logging and monitoring
            
        Returns:
            Response from email provider with status and message
        """
        # Ensure the email client is initialized
        self.initialize()
        
        try:
            # Use performance logging to track email sending time
            with PerformanceLoggingContext("email_send", {"to": mask_sensitive_data(to_email)}):
                # Set default sender if not provided
                sender_email = from_email or self._default_from_email
                sender_name = from_name or self._default_from_name
                
                logger.info(
                    f"Sending email to {mask_sensitive_data(to_email)} with subject: {subject}",
                    extra={"trace_id": trace_id}
                )
                
                # Send the email using the client
                response = self._email_client.send_email(
                    to_email=to_email,
                    subject=subject,
                    html_content=html_content,
                    from_email=sender_email,
                    from_name=sender_name,
                    cc=cc,
                    bcc=bcc,
                    attachments=attachments,
                    categories=categories,
                    custom_args=custom_args
                )
                
                # Record metrics for the email operation
                record_integration_metrics(
                    "sendgrid",
                    "send_email",
                    200,  # Using a default duration since we can't easily get it here
                    success=response.get("status") == "success",
                    trace_id=trace_id
                )
                
                return response
                
        except SendGridException as e:
            error_message = f"Failed to send email to {mask_sensitive_data(to_email)}: {str(e)}"
            logger.error(error_message, extra={"trace_id": trace_id}, exc_info=True)
            
            raise IntegrationException(
                message=f"Email sending failed: {str(e)}",
                details={
                    "provider": "SendGrid",
                    "status_code": getattr(e, "status_code", None),
                    "error": str(e)
                }
            )
    
    def send_template_email(
        self,
        to_email: str,
        template: EmailTemplate,
        context: dict = None,
        subject: str = None,
        from_email: str = None,
        from_name: str = None,
        cc: list = None,
        bcc: list = None,
        attachments: list = None,
        categories: list = None,
        custom_args: dict = None,
        trace_id: str = None
    ) -> dict:
        """Sends an email using a template and context data
        
        Args:
            to_email: Recipient email address
            template: EmailTemplate enum value specifying the template to use
            context: Dictionary of context variables for the template
            subject: Email subject (generated from template if not provided)
            from_email: Sender email address (defaults to configured default)
            from_name: Sender name (defaults to configured default)
            cc: List of CC recipients
            bcc: List of BCC recipients
            attachments: List of file attachments
            categories: Categories for email tracking
            custom_args: Custom arguments for email provider
            trace_id: Trace ID for logging and monitoring
            
        Returns:
            Response from email provider with status and message
        """
        # Create email context by merging default context with provided context
        email_context = create_email_context(context or {})
        
        # Get template filename
        template_filename = template.get_filename()
        
        # Render the template
        html_content = render_template(template_filename, email_context)
        if not html_content:
            # Handle template rendering error
            error_message = f"Failed to render email template: {template_filename}"
            logger.error(error_message, extra={"trace_id": trace_id})
            
            raise IntegrationException(
                message=error_message,
                details={"template": template_filename}
            )
        
        # Generate subject if not provided
        if not subject:
            subject = generate_email_subject(template.value, email_context)
        
        # Send the email
        return self.send_email(
            to_email=to_email,
            subject=subject,
            html_content=html_content,
            from_email=from_email,
            from_name=from_name,
            cc=cc,
            bcc=bcc,
            attachments=attachments,
            categories=categories,
            custom_args=custom_args,
            trace_id=trace_id
        )
    
    def send_contact_confirmation(
        self,
        to_email: str,
        name: str,
        form_data: dict,
        trace_id: str = None
    ) -> dict:
        """Sends a confirmation email for contact form submission
        
        Args:
            to_email: Recipient email address
            name: Recipient's name
            form_data: Form submission data
            trace_id: Trace ID for logging and monitoring
            
        Returns:
            Response from email provider with status and message
        """
        # Create context with user's name and form data
        context = {
            "name": name,
            "form_data": form_data,
            "submission_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Send email using the contact confirmation template
        return self.send_template_email(
            to_email=to_email,
            template=EmailTemplate.CONTACT_CONFIRMATION,
            context=context,
            categories=["contact"],
            trace_id=trace_id
        )
    
    def send_demo_request_confirmation(
        self,
        to_email: str,
        name: str,
        form_data: dict,
        trace_id: str = None
    ) -> dict:
        """Sends a confirmation email for demo request submission
        
        Args:
            to_email: Recipient email address
            name: Recipient's name
            form_data: Form submission data
            trace_id: Trace ID for logging and monitoring
            
        Returns:
            Response from email provider with status and message
        """
        # Create context with user's name and form data
        context = {
            "name": name,
            "form_data": form_data,
            "submission_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Add service interests if available
        if "service_interests" in form_data:
            context["service_interests"] = form_data["service_interests"]
        
        # Format preferred date/time if provided
        if "preferred_date" in form_data and "preferred_time" in form_data:
            preferred_datetime = f"{form_data['preferred_date']} at {form_data['preferred_time']}"
            context["preferred_datetime"] = preferred_datetime
        
        # Send email using the demo request template
        return self.send_template_email(
            to_email=to_email,
            template=EmailTemplate.DEMO_REQUEST,
            context=context,
            categories=["demo-request"],
            trace_id=trace_id
        )
    
    def send_quote_request_confirmation(
        self,
        to_email: str,
        name: str,
        form_data: dict,
        trace_id: str = None
    ) -> dict:
        """Sends a confirmation email for quote request submission
        
        Args:
            to_email: Recipient email address
            name: Recipient's name
            form_data: Form submission data
            trace_id: Trace ID for logging and monitoring
            
        Returns:
            Response from email provider with status and message
        """
        # Create context with user's name and form data
        context = {
            "name": name,
            "form_data": form_data,
            "submission_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Add service interests if available
        if "service_interests" in form_data:
            context["service_interests"] = form_data["service_interests"]
        
        # Send email using the quote request template
        return self.send_template_email(
            to_email=to_email,
            template=EmailTemplate.QUOTE_REQUEST,
            context=context,
            categories=["quote-request"],
            trace_id=trace_id
        )
    
    def send_upload_confirmation(
        self,
        to_email: str,
        name: str,
        upload_data: dict,
        trace_id: str = None
    ) -> dict:
        """Sends a confirmation email for file upload
        
        Args:
            to_email: Recipient email address
            name: Recipient's name
            upload_data: File upload metadata
            trace_id: Trace ID for logging and monitoring
            
        Returns:
            Response from email provider with status and message
        """
        # Create context with user's name and upload details
        context = {
            "name": name,
            "upload_data": upload_data,
            "filename": upload_data.get("filename", "your file"),
            "filesize": upload_data.get("size", 0),
            "filetype": upload_data.get("mime_type", "file"),
            "upload_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Send email using the upload confirmation template
        return self.send_template_email(
            to_email=to_email,
            template=EmailTemplate.UPLOAD_CONFIRMATION,
            context=context,
            categories=["file-upload"],
            trace_id=trace_id
        )
    
    def send_upload_complete(
        self,
        to_email: str,
        name: str,
        upload_data: dict,
        processing_results: dict,
        trace_id: str = None
    ) -> dict:
        """Sends a notification email when file processing is complete
        
        Args:
            to_email: Recipient email address
            name: Recipient's name
            upload_data: File upload metadata
            processing_results: Results of file processing
            trace_id: Trace ID for logging and monitoring
            
        Returns:
            Response from email provider with status and message
        """
        # Create context with user's name, upload details, and processing results
        context = {
            "name": name,
            "upload_data": upload_data,
            "filename": upload_data.get("filename", "your file"),
            "processing_results": processing_results,
            "processing_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Add result summary and next steps
        context["result_summary"] = processing_results.get("summary", "Your file has been processed successfully.")
        context["next_steps"] = "Our team will review the results and contact you shortly with recommendations."
        
        # Send email using the upload complete template
        return self.send_template_email(
            to_email=to_email,
            template=EmailTemplate.UPLOAD_COMPLETE,
            context=context,
            categories=["file-processing"],
            trace_id=trace_id
        )
    
    def send_upload_failed(
        self,
        to_email: str,
        name: str,
        upload_data: dict,
        error_message: str,
        trace_id: str = None
    ) -> dict:
        """Sends a notification email when file processing fails
        
        Args:
            to_email: Recipient email address
            name: Recipient's name
            upload_data: File upload metadata
            error_message: Description of the error
            trace_id: Trace ID for logging and monitoring
            
        Returns:
            Response from email provider with status and message
        """
        # Create context with user's name, upload details, and error information
        context = {
            "name": name,
            "upload_data": upload_data,
            "filename": upload_data.get("filename", "your file"),
            "error_message": error_message,
            "error_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Add next steps for troubleshooting
        context["next_steps"] = (
            "Please check your file and try uploading again. If you continue to experience "
            "issues, please contact our support team for assistance."
        )
        
        # Send email using the upload failed template
        return self.send_template_email(
            to_email=to_email,
            template=EmailTemplate.UPLOAD_FAILED,
            context=context,
            categories=["file-processing-error"],
            trace_id=trace_id
        )
    
    def send_internal_notification(
        self,
        subject: str,
        notification_type: str,
        data: dict,
        recipients: list = None,
        trace_id: str = None
    ) -> dict:
        """Sends an internal notification email to administrators
        
        Args:
            subject: Email subject
            notification_type: Type of notification (form submission, error, etc.)
            data: Notification data
            recipients: List of recipient email addresses (defaults to admin email)
            trace_id: Trace ID for logging and monitoring
            
        Returns:
            Response from email provider with status and message
        """
        # Determine recipients (use provided list or default to admin email)
        to_email = self._admin_email
        cc = None
        
        if recipients:
            if len(recipients) == 1:
                to_email = recipients[0]
            else:
                to_email = recipients[0]
                cc = recipients[1:]
        
        # Create context with notification details
        context = {
            "notification_type": notification_type,
            "data": data,
            "environment": settings.ENVIRONMENT,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Send email using the internal notification template
        return self.send_template_email(
            to_email=to_email,
            template=EmailTemplate.INTERNAL_NOTIFICATION,
            subject=subject,
            context=context,
            cc=cc,
            categories=["internal-notification"],
            trace_id=trace_id
        )


# Create singleton instance for application use
email_service = EmailService()