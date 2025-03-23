import pytest
from unittest.mock import patch, MagicMock

from app.services.email_service import EmailService, email_service
from app.integrations.sendgrid import SendGridClient, SendGridException
from app.utils.email_utils import EmailTemplate
from app.core.exceptions import IntegrationException


def setup_function():
    """Reset the EmailService state before each test"""
    # Reset the email service's _initialized flag to False
    if hasattr(email_service, '_initialized'):
        email_service._initialized = False
    
    # Set the email service's _email_client to None
    if hasattr(email_service, '_email_client'):
        email_service._email_client = None


def test_email_service_initialization():
    """Test that the EmailService initializes correctly with default values"""
    service = EmailService()
    
    assert service._initialized is False
    assert service._email_client is None
    assert service._default_from_email == 'noreply@indivillage.com'
    assert service._default_from_name == 'IndiVillage AI Services'
    assert service._admin_email == 'admin@indivillage.com'


@patch('app.services.email_service.SendGridClient')
def test_email_service_initialize_method(mock_sendgrid_client):
    """Test that the initialize method correctly sets up the SendGrid client"""
    # Mock the SendGridClient class
    mock_client = MagicMock()
    mock_sendgrid_client.return_value = mock_client
    
    # Create a new EmailService instance
    service = EmailService()
    service.initialize()
    
    # Assert that SendGridClient was instantiated with correct parameters
    mock_sendgrid_client.assert_called_once_with(
        default_from_email=service._default_from_email,
        default_from_name=service._default_from_name
    )
    
    # Assert that _initialized is now True
    assert service._initialized is True
    
    # Assert that _email_client is set to the mock client instance
    assert service._email_client == mock_client


@patch('app.services.email_service.SendGridClient')
def test_send_email_success(mock_sendgrid_client):
    """Test that send_email method correctly sends an email and returns success response"""
    # Mock the SendGridClient class and its send_email method
    mock_client = MagicMock()
    mock_sendgrid_client.return_value = mock_client
    
    # Configure the mock to return a success response
    mock_client.send_email.return_value = {
        "status": "success",
        "message": "Email sent successfully",
        "status_code": 202
    }
    
    # Create a new EmailService instance
    service = EmailService()
    
    # Call send_email with test parameters
    response = service.send_email(
        to_email="test@example.com",
        subject="Test Subject",
        html_content="<p>Test content</p>"
    )
    
    # Assert that SendGridClient.send_email was called with correct parameters
    mock_client.send_email.assert_called_once_with(
        to_email="test@example.com",
        subject="Test Subject",
        html_content="<p>Test content</p>",
        from_email=service._default_from_email,
        from_name=service._default_from_name,
        cc=None,
        bcc=None,
        attachments=None,
        categories=None,
        custom_args=None
    )
    
    # Assert that the response matches the expected success response
    assert response == {
        "status": "success",
        "message": "Email sent successfully",
        "status_code": 202
    }


@patch('app.services.email_service.SendGridClient')
def test_send_email_error(mock_sendgrid_client):
    """Test that send_email method correctly handles errors from the SendGrid client"""
    # Mock the SendGridClient class and its send_email method
    mock_client = MagicMock()
    mock_sendgrid_client.return_value = mock_client
    
    # Configure the mock to raise a SendGridException
    mock_client.send_email.side_effect = SendGridException("Failed to send email")
    
    # Create a new EmailService instance
    service = EmailService()
    
    # Use pytest.raises to assert that IntegrationException is raised when send_email is called
    with pytest.raises(IntegrationException) as excinfo:
        service.send_email(
            to_email="test@example.com",
            subject="Test Subject",
            html_content="<p>Test content</p>"
        )
    
    # Assert that SendGridClient.send_email was called with correct parameters
    mock_client.send_email.assert_called_once_with(
        to_email="test@example.com",
        subject="Test Subject",
        html_content="<p>Test content</p>",
        from_email=service._default_from_email,
        from_name=service._default_from_name,
        cc=None,
        bcc=None,
        attachments=None,
        categories=None,
        custom_args=None
    )
    
    # Assert that the exception message contains the expected text
    assert "Email sending failed: Failed to send email" in str(excinfo.value)


@patch('app.services.email_service.render_template')
@patch('app.services.email_service.SendGridClient')
def test_send_template_email(mock_sendgrid_client, mock_render_template):
    """Test that send_template_email method correctly renders and sends a template email"""
    # Mock the render_template function to return a test HTML content
    mock_render_template.return_value = "<p>Rendered template content</p>"
    
    # Mock the SendGridClient class and its send_email method
    mock_client = MagicMock()
    mock_sendgrid_client.return_value = mock_client
    
    # Configure the mock to return a success response
    mock_client.send_email.return_value = {
        "status": "success",
        "message": "Email sent successfully",
        "status_code": 202
    }
    
    # Create a new EmailService instance
    service = EmailService()
    
    # Call send_template_email with test parameters and template
    context = {"name": "Test User", "company": "Test Company"}
    response = service.send_template_email(
        to_email="test@example.com",
        template=EmailTemplate.CONTACT_CONFIRMATION,
        context=context,
        subject="Test Template Email"
    )
    
    # Assert that render_template was called with correct template and context
    mock_render_template.assert_called_once_with(
        EmailTemplate.CONTACT_CONFIRMATION.get_filename(),
        context
    )
    
    # Assert that SendGridClient.send_email was called with rendered HTML content
    mock_client.send_email.assert_called_once_with(
        to_email="test@example.com",
        subject="Test Template Email",
        html_content="<p>Rendered template content</p>",
        from_email=service._default_from_email,
        from_name=service._default_from_name,
        cc=None,
        bcc=None,
        attachments=None,
        categories=None,
        custom_args=None
    )
    
    # Assert that the response matches the expected success response
    assert response == {
        "status": "success",
        "message": "Email sent successfully",
        "status_code": 202
    }


@patch('app.services.email_service.EmailService.send_template_email')
def test_send_contact_confirmation(mock_send_template_email):
    """Test that send_contact_confirmation method correctly sends a contact form confirmation email"""
    # Mock the EmailService.send_template_email method
    mock_send_template_email.return_value = {
        "status": "success",
        "message": "Email sent successfully"
    }
    
    # Create a new EmailService instance
    service = EmailService()
    
    # Create test form data for a contact form
    form_data = {
        "name": "Test User",
        "email": "test@example.com",
        "company": "Test Company",
        "message": "This is a test message"
    }
    
    # Call send_contact_confirmation with test parameters
    response = service.send_contact_confirmation(
        to_email="test@example.com",
        name="Test User",
        form_data=form_data
    )
    
    # Assert that send_template_email was called with EmailTemplate.CONTACT_CONFIRMATION
    mock_send_template_email.assert_called_once()
    call_args = mock_send_template_email.call_args[1]
    assert call_args["to_email"] == "test@example.com"
    assert call_args["template"] == EmailTemplate.CONTACT_CONFIRMATION
    
    # Assert that send_template_email was called with correct context containing form data
    assert "name" in call_args["context"]
    assert call_args["context"]["name"] == "Test User"
    assert "form_data" in call_args["context"]
    assert call_args["context"]["form_data"] == form_data
    assert "submission_date" in call_args["context"]
    assert call_args["categories"] == ["contact"]
    
    # Assert that the response matches the expected success response
    assert response == {
        "status": "success",
        "message": "Email sent successfully"
    }


@patch('app.services.email_service.EmailService.send_template_email')
def test_send_demo_request_confirmation(mock_send_template_email):
    """Test that send_demo_request_confirmation method correctly sends a demo request confirmation email"""
    # Mock the EmailService.send_template_email method
    mock_send_template_email.return_value = {
        "status": "success",
        "message": "Email sent successfully"
    }
    
    # Create a new EmailService instance
    service = EmailService()
    
    # Create test form data for a demo request with service interests
    form_data = {
        "name": "Test User",
        "email": "test@example.com",
        "company": "Test Company",
        "service_interests": ["Data Collection", "AI Model Development"],
        "preferred_date": "2023-09-01",
        "preferred_time": "10:00 AM"
    }
    
    # Call send_demo_request_confirmation with test parameters
    response = service.send_demo_request_confirmation(
        to_email="test@example.com",
        name="Test User",
        form_data=form_data
    )
    
    # Assert that send_template_email was called with EmailTemplate.DEMO_REQUEST
    mock_send_template_email.assert_called_once()
    call_args = mock_send_template_email.call_args[1]
    assert call_args["to_email"] == "test@example.com"
    assert call_args["template"] == EmailTemplate.DEMO_REQUEST
    
    # Assert that send_template_email was called with correct context containing form data and services
    assert "name" in call_args["context"]
    assert call_args["context"]["name"] == "Test User"
    assert "form_data" in call_args["context"]
    assert call_args["context"]["form_data"] == form_data
    assert "service_interests" in call_args["context"]
    assert call_args["context"]["service_interests"] == ["Data Collection", "AI Model Development"]
    assert "preferred_datetime" in call_args["context"]
    assert call_args["context"]["preferred_datetime"] == "2023-09-01 at 10:00 AM"
    assert call_args["categories"] == ["demo-request"]
    
    # Assert that the response matches the expected success response
    assert response == {
        "status": "success",
        "message": "Email sent successfully"
    }


@patch('app.services.email_service.EmailService.send_template_email')
def test_send_quote_request_confirmation(mock_send_template_email):
    """Test that send_quote_request_confirmation method correctly sends a quote request confirmation email"""
    # Mock the EmailService.send_template_email method
    mock_send_template_email.return_value = {
        "status": "success",
        "message": "Email sent successfully"
    }
    
    # Create a new EmailService instance
    service = EmailService()
    
    # Create test form data for a quote request with service interests
    form_data = {
        "name": "Test User",
        "email": "test@example.com",
        "company": "Test Company",
        "service_interests": ["Data Preparation", "Human-in-the-Loop"],
        "project_description": "This is a test project"
    }
    
    # Call send_quote_request_confirmation with test parameters
    response = service.send_quote_request_confirmation(
        to_email="test@example.com",
        name="Test User",
        form_data=form_data
    )
    
    # Assert that send_template_email was called with EmailTemplate.QUOTE_REQUEST
    mock_send_template_email.assert_called_once()
    call_args = mock_send_template_email.call_args[1]
    assert call_args["to_email"] == "test@example.com"
    assert call_args["template"] == EmailTemplate.QUOTE_REQUEST
    
    # Assert that send_template_email was called with correct context containing form data and services
    assert "name" in call_args["context"]
    assert call_args["context"]["name"] == "Test User"
    assert "form_data" in call_args["context"]
    assert call_args["context"]["form_data"] == form_data
    assert "service_interests" in call_args["context"]
    assert call_args["context"]["service_interests"] == ["Data Preparation", "Human-in-the-Loop"]
    assert call_args["categories"] == ["quote-request"]
    
    # Assert that the response matches the expected success response
    assert response == {
        "status": "success",
        "message": "Email sent successfully"
    }


@patch('app.services.email_service.EmailService.send_template_email')
def test_send_upload_confirmation(mock_send_template_email):
    """Test that send_upload_confirmation method correctly sends a file upload confirmation email"""
    # Mock the EmailService.send_template_email method
    mock_send_template_email.return_value = {
        "status": "success",
        "message": "Email sent successfully"
    }
    
    # Create a new EmailService instance
    service = EmailService()
    
    # Create test upload data with filename, size, and type
    upload_data = {
        "filename": "test_data.csv",
        "size": 1024,
        "mime_type": "text/csv"
    }
    
    # Call send_upload_confirmation with test parameters
    response = service.send_upload_confirmation(
        to_email="test@example.com",
        name="Test User",
        upload_data=upload_data
    )
    
    # Assert that send_template_email was called with EmailTemplate.UPLOAD_CONFIRMATION
    mock_send_template_email.assert_called_once()
    call_args = mock_send_template_email.call_args[1]
    assert call_args["to_email"] == "test@example.com"
    assert call_args["template"] == EmailTemplate.UPLOAD_CONFIRMATION
    
    # Assert that send_template_email was called with correct context containing upload details
    assert "name" in call_args["context"]
    assert call_args["context"]["name"] == "Test User"
    assert "upload_data" in call_args["context"]
    assert call_args["context"]["upload_data"] == upload_data
    assert "filename" in call_args["context"]
    assert call_args["context"]["filename"] == "test_data.csv"
    assert "filesize" in call_args["context"]
    assert call_args["context"]["filesize"] == 1024
    assert "filetype" in call_args["context"]
    assert call_args["context"]["filetype"] == "text/csv"
    assert call_args["categories"] == ["file-upload"]
    
    # Assert that the response matches the expected success response
    assert response == {
        "status": "success",
        "message": "Email sent successfully"
    }


@patch('app.services.email_service.EmailService.send_template_email')
def test_send_upload_complete(mock_send_template_email):
    """Test that send_upload_complete method correctly sends a file processing completion email"""
    # Mock the EmailService.send_template_email method
    mock_send_template_email.return_value = {
        "status": "success",
        "message": "Email sent successfully"
    }
    
    # Create a new EmailService instance
    service = EmailService()
    
    # Create test upload data with filename, size, and type
    upload_data = {
        "filename": "test_data.csv",
        "size": 1024,
        "mime_type": "text/csv"
    }
    
    # Create test processing results with summary and details
    processing_results = {
        "summary": "Successfully processed 100 records",
        "details": "The file contains clean, well-structured data."
    }
    
    # Call send_upload_complete with test parameters
    response = service.send_upload_complete(
        to_email="test@example.com",
        name="Test User",
        upload_data=upload_data,
        processing_results=processing_results
    )
    
    # Assert that send_template_email was called with EmailTemplate.UPLOAD_COMPLETE
    mock_send_template_email.assert_called_once()
    call_args = mock_send_template_email.call_args[1]
    assert call_args["to_email"] == "test@example.com"
    assert call_args["template"] == EmailTemplate.UPLOAD_COMPLETE
    
    # Assert that send_template_email was called with correct context containing upload details and results
    assert "name" in call_args["context"]
    assert call_args["context"]["name"] == "Test User"
    assert "upload_data" in call_args["context"]
    assert call_args["context"]["upload_data"] == upload_data
    assert "filename" in call_args["context"]
    assert call_args["context"]["filename"] == "test_data.csv"
    assert "processing_results" in call_args["context"]
    assert call_args["context"]["processing_results"] == processing_results
    assert "result_summary" in call_args["context"]
    assert call_args["context"]["result_summary"] == "Successfully processed 100 records"
    assert call_args["categories"] == ["file-processing"]
    
    # Assert that the response matches the expected success response
    assert response == {
        "status": "success",
        "message": "Email sent successfully"
    }


@patch('app.services.email_service.EmailService.send_template_email')
def test_send_upload_failed(mock_send_template_email):
    """Test that send_upload_failed method correctly sends a file processing failure email"""
    # Mock the EmailService.send_template_email method
    mock_send_template_email.return_value = {
        "status": "success",
        "message": "Email sent successfully"
    }
    
    # Create a new EmailService instance
    service = EmailService()
    
    # Create test upload data with filename, size, and type
    upload_data = {
        "filename": "test_data.csv",
        "size": 1024,
        "mime_type": "text/csv"
    }
    
    # Create test error message
    error_message = "File format is not supported"
    
    # Call send_upload_failed with test parameters
    response = service.send_upload_failed(
        to_email="test@example.com",
        name="Test User",
        upload_data=upload_data,
        error_message=error_message
    )
    
    # Assert that send_template_email was called with EmailTemplate.UPLOAD_FAILED
    mock_send_template_email.assert_called_once()
    call_args = mock_send_template_email.call_args[1]
    assert call_args["to_email"] == "test@example.com"
    assert call_args["template"] == EmailTemplate.UPLOAD_FAILED
    
    # Assert that send_template_email was called with correct context containing upload details and error
    assert "name" in call_args["context"]
    assert call_args["context"]["name"] == "Test User"
    assert "upload_data" in call_args["context"]
    assert call_args["context"]["upload_data"] == upload_data
    assert "filename" in call_args["context"]
    assert call_args["context"]["filename"] == "test_data.csv"
    assert "error_message" in call_args["context"]
    assert call_args["context"]["error_message"] == "File format is not supported"
    assert "next_steps" in call_args["context"]
    assert call_args["categories"] == ["file-processing-error"]
    
    # Assert that the response matches the expected success response
    assert response == {
        "status": "success",
        "message": "Email sent successfully"
    }


@patch('app.services.email_service.EmailService.send_template_email')
def test_send_internal_notification(mock_send_template_email):
    """Test that send_internal_notification method correctly sends an internal notification email"""
    # Mock the EmailService.send_template_email method
    mock_send_template_email.return_value = {
        "status": "success",
        "message": "Email sent successfully"
    }
    
    # Create a new EmailService instance
    service = EmailService()
    
    # Create test notification data
    notification_data = {
        "event": "New form submission",
        "details": {
            "form_type": "contact",
            "user_email": "user@example.com",
            "submission_time": "2023-09-01 14:30:00"
        }
    }
    
    # Call send_internal_notification with test parameters
    response = service.send_internal_notification(
        subject="New Contact Form Submission",
        notification_type="form_submission",
        data=notification_data
    )
    
    # Assert that send_template_email was called with EmailTemplate.INTERNAL_NOTIFICATION
    mock_send_template_email.assert_called_once()
    call_args = mock_send_template_email.call_args[1]
    assert call_args["to_email"] == service._admin_email
    assert call_args["template"] == EmailTemplate.INTERNAL_NOTIFICATION
    assert call_args["subject"] == "New Contact Form Submission"
    
    # Assert that send_template_email was called with correct context containing notification data
    assert "notification_type" in call_args["context"]
    assert call_args["context"]["notification_type"] == "form_submission"
    assert "data" in call_args["context"]
    assert call_args["context"]["data"] == notification_data
    assert "environment" in call_args["context"]
    assert call_args["categories"] == ["internal-notification"]
    
    # Assert that the response matches the expected success response
    assert response == {
        "status": "success",
        "message": "Email sent successfully"
    }


def test_singleton_instance():
    """Test that the exported email_service is a singleton instance"""
    # Import the email_service singleton instance
    from app.services.email_service import email_service
    
    # Assert that it is an instance of EmailService
    assert isinstance(email_service, EmailService)
    
    # Create a new EmailService instance
    new_instance = EmailService()
    
    # Assert that the new instance is not the same object as the singleton
    assert email_service is not new_instance