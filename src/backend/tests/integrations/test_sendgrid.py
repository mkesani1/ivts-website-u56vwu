import pytest
import unittest.mock as mock
import json
import base64
from app.integrations.sendgrid import SendGridClient, SendGridException
from app.utils.email_utils import format_email_address, get_plain_text_from_html


class MockResponse:
    """Mock class for SendGrid API responses"""
    
    def __init__(self, status_code, body, headers=None):
        self.status_code = status_code
        self.body = body
        self.headers = headers or {}


def test_sendgrid_client_initialization():
    """Tests that SendGridClient initializes correctly with provided credentials"""
    # Create a client with test credentials
    api_key = "test_api_key"
    from_email = "test@example.com"
    from_name = "Test Sender"
    
    client = SendGridClient(api_key, from_email, from_name)
    
    # Assert that it's not yet initialized
    assert client._initialized is False
    
    # Check that credentials are stored correctly
    assert client._api_key == api_key
    assert client._default_from_email == from_email
    assert client._default_from_name == from_name


@mock.patch('sendgrid.SendGridAPIClient')
def test_sendgrid_client_lazy_initialization(mock_sendgrid):
    """Tests that SendGridClient initializes lazily when first needed"""
    # Create a client
    client = SendGridClient("test_api_key")
    
    # Assert that it's not yet initialized
    assert client._initialized is False
    
    # Call initialize
    client.initialize()
    
    # Assert that SendGridAPIClient was called with correct API key
    mock_sendgrid.assert_called_once_with("test_api_key")
    
    # Assert that client is now initialized
    assert client._initialized is True
    assert client._client == mock_sendgrid.return_value


@mock.patch('sendgrid.SendGridAPIClient')
def test_send_email_success(mock_sendgrid):
    """Tests successful email sending with SendGridClient"""
    # Mock the SendGridAPIClient.send method to return a successful response
    mock_client = mock_sendgrid.return_value
    mock_client.send.return_value = MockResponse(202, {"message": "success"})
    
    # Create a client
    client = SendGridClient("test_api_key")
    
    # Test sending an email
    response = client.send_email(
        to_email="recipient@example.com",
        subject="Test Subject",
        html_content="<p>Test content</p>"
    )
    
    # Assert that SendGridAPIClient.send was called
    mock_client.send.assert_called_once()
    
    # Check the response
    assert response["status"] == "success"
    assert response["message"] == "Email sent successfully"
    assert response["status_code"] == 202


@mock.patch('sendgrid.SendGridAPIClient')
def test_send_email_with_cc_bcc(mock_sendgrid):
    """Tests email sending with CC and BCC recipients"""
    # Mock the SendGridAPIClient.send method
    mock_client = mock_sendgrid.return_value
    mock_client.send.return_value = MockResponse(202, {"message": "success"})
    
    # Create a client
    client = SendGridClient("test_api_key")
    
    # Test sending an email with CC and BCC
    response = client.send_email(
        to_email="recipient@example.com",
        subject="Test Subject",
        html_content="<p>Test content</p>",
        cc=["cc@example.com"],
        bcc=["bcc@example.com"]
    )
    
    # Assert that SendGridAPIClient.send was called
    mock_client.send.assert_called_once()
    
    # Check the response
    assert response["status"] == "success"
    assert response["message"] == "Email sent successfully"
    assert response["status_code"] == 202


@mock.patch('sendgrid.SendGridAPIClient')
def test_send_email_with_attachments(mock_sendgrid):
    """Tests email sending with file attachments"""
    # Mock the SendGridAPIClient.send method
    mock_client = mock_sendgrid.return_value
    mock_client.send.return_value = MockResponse(202, {"message": "success"})
    
    # Create a client
    client = SendGridClient("test_api_key")
    
    # Create test attachment
    file_content = b"Test file content"
    filename = "test.txt"
    mime_type = "text/plain"
    
    # Test sending an email with attachment
    response = client.send_email(
        to_email="recipient@example.com",
        subject="Test Subject",
        html_content="<p>Test content</p>",
        attachments=[(file_content, filename, mime_type)]
    )
    
    # Assert that SendGridAPIClient.send was called
    mock_client.send.assert_called_once()
    
    # Check the response
    assert response["status"] == "success"
    assert response["message"] == "Email sent successfully"
    assert response["status_code"] == 202


@mock.patch('sendgrid.SendGridAPIClient')
def test_send_email_with_categories(mock_sendgrid):
    """Tests email sending with categories for tracking"""
    # Mock the SendGridAPIClient.send method
    mock_client = mock_sendgrid.return_value
    mock_client.send.return_value = MockResponse(202, {"message": "success"})
    
    # Create a client
    client = SendGridClient("test_api_key")
    
    # Test sending an email with categories
    response = client.send_email(
        to_email="recipient@example.com",
        subject="Test Subject",
        html_content="<p>Test content</p>",
        categories=["test", "example"]
    )
    
    # Assert that SendGridAPIClient.send was called
    mock_client.send.assert_called_once()
    
    # Check the response
    assert response["status"] == "success"
    assert response["message"] == "Email sent successfully"
    assert response["status_code"] == 202


@mock.patch('sendgrid.SendGridAPIClient')
def test_send_email_with_custom_args(mock_sendgrid):
    """Tests email sending with custom arguments"""
    # Mock the SendGridAPIClient.send method
    mock_client = mock_sendgrid.return_value
    mock_client.send.return_value = MockResponse(202, {"message": "success"})
    
    # Create a client
    client = SendGridClient("test_api_key")
    
    # Test sending an email with custom args
    response = client.send_email(
        to_email="recipient@example.com",
        subject="Test Subject",
        html_content="<p>Test content</p>",
        custom_args={"campaign_id": "test_campaign", "user_id": "12345"}
    )
    
    # Assert that SendGridAPIClient.send was called
    mock_client.send.assert_called_once()
    
    # Check the response
    assert response["status"] == "success"
    assert response["message"] == "Email sent successfully"
    assert response["status_code"] == 202


@mock.patch('sendgrid.SendGridAPIClient')
def test_send_email_failure(mock_sendgrid):
    """Tests error handling when email sending fails"""
    # Mock the SendGridAPIClient.send method to raise an exception
    mock_client = mock_sendgrid.return_value
    mock_client.send.side_effect = Exception("Failed to send email")
    
    # Create a client
    client = SendGridClient("test_api_key")
    
    # Test sending an email
    response = client.send_email(
        to_email="recipient@example.com",
        subject="Test Subject",
        html_content="<p>Test content</p>"
    )
    
    # Check the response
    assert response["status"] == "error"
    assert response["message"] == "Failed to send email"


@mock.patch('sendgrid.SendGridAPIClient')
def test_send_template_email_success(mock_sendgrid):
    """Tests successful template email sending"""
    # Mock the SendGridAPIClient.send method
    mock_client = mock_sendgrid.return_value
    mock_client.send.return_value = MockResponse(202, {"message": "success"})
    
    # Create a client
    client = SendGridClient("test_api_key")
    
    # Test sending a template email
    response = client.send_template_email(
        to_email="recipient@example.com",
        template_id="d-12345abcdef",
        dynamic_data={"name": "Test Recipient", "company": "Test Company"}
    )
    
    # Assert that SendGridAPIClient.send was called
    mock_client.send.assert_called_once()
    
    # Check the response
    assert response["status"] == "success"
    assert response["message"] == "Template email sent successfully"
    assert response["status_code"] == 202


@mock.patch('sendgrid.SendGridAPIClient')
def test_send_template_email_failure(mock_sendgrid):
    """Tests error handling when template email sending fails"""
    # Mock the SendGridAPIClient.send method to raise an exception
    mock_client = mock_sendgrid.return_value
    mock_client.send.side_effect = Exception("Failed to send template email")
    
    # Create a client
    client = SendGridClient("test_api_key")
    
    # Test sending a template email
    response = client.send_template_email(
        to_email="recipient@example.com",
        template_id="d-12345abcdef",
        dynamic_data={"name": "Test Recipient"}
    )
    
    # Check the response
    assert response["status"] == "error"
    assert response["message"] == "Failed to send template email"


def test_create_attachment():
    """Tests creation of email attachments"""
    # Create a client
    client = SendGridClient("test_api_key")
    
    # Test data
    file_content = b"Test file content"
    filename = "test.txt"
    mime_type = "text/plain"
    
    # Create an attachment
    attachment = client.create_attachment(file_content, filename, mime_type)
    
    # Check the attachment
    assert attachment.file_name == filename
    assert attachment.file_type == mime_type
    assert attachment.disposition == "attachment"
    assert attachment.file_content == base64.b64encode(file_content).decode()


@mock.patch('sendgrid.SendGridAPIClient')
def test_get_email_stats(mock_sendgrid):
    """Tests retrieval of email sending statistics"""
    # Mock the SendGridAPIClient stats method
    mock_client = mock_sendgrid.return_value
    mock_client.client.stats.get.return_value = MockResponse(
        200, 
        json.dumps([{"date": "2022-01-01", "stats": [{"metrics": {"opens": 10, "clicks": 5}}]}])
    )
    
    # Create a client
    client = SendGridClient("test_api_key")
    
    # Test getting email stats
    response = client.get_email_stats(
        start_date="2022-01-01",
        end_date="2022-01-31",
        aggregated_by="day"
    )
    
    # Assert that client.stats.get was called with correct parameters
    mock_client.client.stats.get.assert_called_once()
    call_args = mock_client.client.stats.get.call_args[1]
    query_params = call_args["query_params"]
    assert query_params["start_date"] == "2022-01-01"
    assert query_params["end_date"] == "2022-01-31"
    assert query_params["aggregated_by"] == "day"
    
    # Check the response
    assert response["status"] == "success"
    assert response["message"] == "Statistics retrieved successfully"
    assert "data" in response


@mock.patch('sendgrid.SendGridAPIClient')
def test_get_email_stats_failure(mock_sendgrid):
    """Tests error handling when retrieving email statistics fails"""
    # Mock the SendGridAPIClient stats method to raise an exception
    mock_client = mock_sendgrid.return_value
    mock_client.client.stats.get.side_effect = Exception("Failed to retrieve statistics")
    
    # Create a client
    client = SendGridClient("test_api_key")
    
    # Test getting email stats
    response = client.get_email_stats(start_date="2022-01-01")
    
    # Check the response
    assert response["status"] == "error"
    assert response["message"] == "Failed to retrieve statistics"


def test_sendgrid_exception():
    """Tests the SendGridException class"""
    # Create an exception with test data
    message = "Test error message"
    status_code = 400
    response_body = {"errors": [{"message": "Invalid API key"}]}
    
    exception = SendGridException(message, status_code, response_body)
    
    # Check the exception attributes
    assert str(exception) == message
    assert exception.status_code == status_code
    assert exception.response_body == response_body