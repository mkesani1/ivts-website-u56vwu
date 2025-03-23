import pytest
from unittest.mock import patch, MagicMock
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from pydantic import BaseModel  # version: 1.10.0

from app.security.input_validation import (
    validate_email, validate_phone, validate_url, validate_date_format, validate_time_format,
    sanitize_input, validate_file_extension, validate_file_size, validate_mime_type,
    validate_required_fields, validate_field_length, validate_enum_value,
    validate_contact_form, validate_demo_request_form, validate_quote_request_form,
    validate_upload_request_form, validate_file_metadata,
    InputValidator, ValidationDecorator
)
from app.core.exceptions import ValidationException
from app.core.config import settings


@pytest.mark.parametrize('email,expected', [
    ('test@example.com', True),
    ('user.name@domain.co.uk', True),
    ('invalid-email', False),
    ('', False),
    (None, False)
])
def test_validate_email(email, expected):
    """Tests the validate_email function with various email formats."""
    assert validate_email(email) == expected


@pytest.mark.parametrize('phone,region,expected', [
    ('+1 (555) 123-4567', 'US', True),
    ('+44 20 7946 0958', 'GB', True),
    ('invalid-phone', 'US', False),
    ('', 'US', True),  # Optional, so empty is valid
    (None, 'US', True)  # Optional, so None is valid
])
def test_validate_phone(phone, region, expected):
    """Tests the validate_phone function with various phone number formats."""
    assert validate_phone(phone, region) == expected


@pytest.mark.parametrize('url,expected', [
    ('https://example.com', True),
    ('http://subdomain.example.co.uk/path', True),
    ('invalid-url', False),
    ('', False),
    (None, False)
])
def test_validate_url(url, expected):
    """Tests the validate_url function with various URL formats."""
    assert validate_url(url) == expected


@pytest.mark.parametrize('date_str,expected', [
    ('2023-05-15', True),
    ('2023-13-01', False),  # Invalid month
    ('05/15/2023', False),  # Wrong format
    ('', True),  # Optional, so empty is valid
    (None, True)  # Optional, so None is valid
])
def test_validate_date_format(date_str, expected):
    """Tests the validate_date_format function with various date formats."""
    assert validate_date_format(date_str) == expected


@pytest.mark.parametrize('time_str,expected', [
    ('14:30', True),
    ('09:45', True),
    ('24:00', False),  # Invalid hour
    ('9:5', False),    # Wrong format
    ('', True),        # Optional, so empty is valid
    (None, True)       # Optional, so None is valid
])
def test_validate_time_format(time_str, expected):
    """Tests the validate_time_format function with various time formats."""
    assert validate_time_format(time_str) == expected


def test_sanitize_input():
    """Tests the sanitize_input function with various input strings."""
    # Test with plain text
    assert sanitize_input("Hello World") == "Hello World"
    
    # Test with HTML and allow_html=False (default)
    html_input = "<script>alert('XSS')</script><p>Hello World</p>"
    assert sanitize_input(html_input) == "&lt;script&gt;alert('XSS')&lt;/script&gt;&lt;p&gt;Hello World&lt;/p&gt;"
    
    # Test with HTML and allow_html=True
    allowed_html = "<p>Paragraph</p><strong>Bold</strong><script>alert('XSS')</script>"
    sanitized = sanitize_input(allowed_html, allow_html=True)
    assert "<p>Paragraph</p>" in sanitized
    assert "<strong>Bold</strong>" in sanitized
    assert "<script>" not in sanitized
    
    # Test with None
    assert sanitize_input(None) == ""


@pytest.mark.parametrize('filename,expected', [
    ('document.pdf', True),
    ('data.csv', True),
    ('image.jpg', True),
    ('script.exe', False),
    ('', False),
    (None, False)
])
def test_validate_file_extension(filename, expected):
    """Tests the validate_file_extension function with various file extensions."""
    with patch('app.security.input_validation.settings') as mock_settings:
        mock_settings.ALLOWED_UPLOAD_EXTENSIONS = "pdf,csv,json,xml,jpg,jpeg,png,tiff,mp3,wav"
        assert validate_file_extension(filename) == expected


@pytest.mark.parametrize('file_size,max_size_mb,expected', [
    (1024 * 1024, 2, True),         # 1MB with 2MB limit
    (3 * 1024 * 1024, 2, False),    # 3MB with 2MB limit
    (0, 2, True),                    # Empty file
    (-1, 2, False),                  # Invalid size
    (None, 2, False)                 # None size
])
def test_validate_file_size(file_size, max_size_mb, expected):
    """Tests the validate_file_size function with various file sizes."""
    with patch('app.security.input_validation.settings') as mock_settings:
        mock_settings.MAX_UPLOAD_SIZE_MB = max_size_mb
        assert validate_file_size(file_size) == expected


@pytest.mark.parametrize('mime_type,filename,expected', [
    ('application/pdf', 'document.pdf', True),
    ('text/csv', 'data.csv', True),
    ('image/jpeg', 'photo.jpg', True),
    ('application/octet-stream', 'document.pdf', False),  # Mismatch
    ('', 'document.pdf', False),                          # Empty mime type
    (None, 'document.pdf', False),                        # None mime type
    ('application/pdf', '', False),                       # Empty filename
    ('application/pdf', None, False)                      # None filename
])
def test_validate_mime_type(mime_type, filename, expected):
    """Tests the validate_mime_type function with various MIME types and filenames."""
    assert validate_mime_type(mime_type, filename) == expected


def test_validate_required_fields():
    """Tests the validate_required_fields function with various data dictionaries."""
    # Test with all required fields present
    data = {'name': 'John', 'email': 'john@example.com', 'message': 'Hello'}
    required_fields = ['name', 'email', 'message']
    valid, errors = validate_required_fields(data, required_fields)
    assert valid is True
    assert errors == {}
    
    # Test with missing required fields
    data = {'name': 'John', 'message': 'Hello'}
    valid, errors = validate_required_fields(data, required_fields)
    assert valid is False
    assert 'email' in errors
    
    # Test with empty required fields
    data = {'name': 'John', 'email': '', 'message': 'Hello'}
    valid, errors = validate_required_fields(data, required_fields)
    assert valid is False
    assert 'email' in errors


@pytest.mark.parametrize('value,min_length,max_length,expected', [
    ('test', 2, 10, (True, '')),                                    # Valid
    ('test', 5, 10, (False, 'Field must be at least 5 characters')),  # Too short
    ('test', 2, 3, (False, 'Field must be at most 3 characters')),    # Too long
    ('', 1, 10, (False, 'Field must be at least 1 characters')),      # Empty but required
    (None, 1, 10, (True, ''))                                       # None is skipped
])
def test_validate_field_length(value, min_length, max_length, expected):
    """Tests the validate_field_length function with various field values and length constraints."""
    assert validate_field_length(value, min_length, max_length) == expected


@pytest.mark.parametrize('value,allowed_values,expected', [
    ('option1', ['option1', 'option2', 'option3'], (True, '')),                                   
    ('option4', ['option1', 'option2', 'option3'], (False, 'Value must be one of: option1, option2, option3')),
    (None, ['option1', 'option2', 'option3'], (True, ''))                                         
])
def test_validate_enum_value(value, allowed_values, expected):
    """Tests the validate_enum_value function with various values and allowed values lists."""
    assert validate_enum_value(value, allowed_values) == expected


def test_validate_contact_form():
    """Tests the validate_contact_form function with various form data."""
    # Test with valid data
    valid_data = {
        'name': 'John Doe',
        'email': 'john@example.com',
        'message': 'This is a test message.',
        'company': 'Test Company',
        'phone': '+1 (555) 123-4567'
    }
    is_valid, errors = validate_contact_form(valid_data)
    assert is_valid is True
    assert errors == {}
    
    # Test with missing required fields
    invalid_data = {
        'name': 'John Doe',
        'company': 'Test Company'
    }
    is_valid, errors = validate_contact_form(invalid_data)
    assert is_valid is False
    assert 'email' in errors
    assert 'message' in errors
    
    # Test with invalid email
    invalid_email_data = {
        'name': 'John Doe',
        'email': 'invalid-email',
        'message': 'This is a test message.',
        'company': 'Test Company'
    }
    is_valid, errors = validate_contact_form(invalid_email_data)
    assert is_valid is False
    assert 'email' in errors
    
    # Test with field length violations
    invalid_length_data = {
        'name': 'J',  # Too short
        'email': 'john@example.com',
        'message': 'Hi',  # Too short
        'company': 'Test Company'
    }
    is_valid, errors = validate_contact_form(invalid_length_data)
    assert is_valid is False
    assert 'name' in errors
    assert 'message' in errors


def test_validate_demo_request_form():
    """Tests the validate_demo_request_form function with various form data."""
    # Test with valid data
    valid_data = {
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john@example.com',
        'company': 'Test Company',
        'job_title': 'Manager',
        'phone': '+1 (555) 123-4567',
        'service_interests': ['data_collection', 'data_preparation'],
        'preferred_date': '2023-05-20',
        'preferred_time': '14:30',
        'project_description': 'We need assistance with data collection.'
    }
    is_valid, errors = validate_demo_request_form(valid_data)
    assert is_valid is True
    assert errors == {}
    
    # Test with missing required fields
    invalid_data = {
        'first_name': 'John',
        'last_name': 'Doe',
        'company': 'Test Company'
    }
    is_valid, errors = validate_demo_request_form(invalid_data)
    assert is_valid is False
    assert 'email' in errors
    assert 'service_interests' in errors
    
    # Test with invalid email
    invalid_email_data = {
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'invalid-email',
        'company': 'Test Company',
        'service_interests': ['data_collection']
    }
    is_valid, errors = validate_demo_request_form(invalid_email_data)
    assert is_valid is False
    assert 'email' in errors
    
    # Test with invalid date format
    invalid_date_data = {
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john@example.com',
        'company': 'Test Company',
        'service_interests': ['data_collection'],
        'preferred_date': '05/20/2023'  # Wrong format
    }
    is_valid, errors = validate_demo_request_form(invalid_date_data)
    assert is_valid is False
    assert 'preferred_date' in errors
    
    # Test with invalid service interests
    invalid_services_data = {
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john@example.com',
        'company': 'Test Company',
        'service_interests': ['invalid_service']
    }
    is_valid, errors = validate_demo_request_form(invalid_services_data)
    assert is_valid is False
    assert 'service_interests' in errors


def test_validate_quote_request_form():
    """Tests the validate_quote_request_form function with various form data."""
    # Test with valid data
    valid_data = {
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john@example.com',
        'company': 'Test Company',
        'job_title': 'Manager',
        'phone': '+1 (555) 123-4567',
        'service_interests': ['data_collection', 'data_preparation'],
        'project_description': 'We need assistance with data collection and preparation for our AI project.',
        'budget_range': '10k_50k',
        'project_timeline': '3_6_months'
    }
    is_valid, errors = validate_quote_request_form(valid_data)
    assert is_valid is True
    assert errors == {}
    
    # Test with missing required fields
    invalid_data = {
        'first_name': 'John',
        'last_name': 'Doe',
        'company': 'Test Company'
    }
    is_valid, errors = validate_quote_request_form(invalid_data)
    assert is_valid is False
    assert 'email' in errors
    assert 'service_interests' in errors
    assert 'project_description' in errors
    
    # Test with invalid email
    invalid_email_data = {
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'invalid-email',
        'company': 'Test Company',
        'service_interests': ['data_collection'],
        'project_description': 'A detailed project description with sufficient length.'
    }
    is_valid, errors = validate_quote_request_form(invalid_email_data)
    assert is_valid is False
    assert 'email' in errors
    
    # Test with invalid budget range
    invalid_budget_data = {
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john@example.com',
        'company': 'Test Company',
        'service_interests': ['data_collection'],
        'project_description': 'A detailed project description with sufficient length.',
        'budget_range': 'invalid_range'
    }
    is_valid, errors = validate_quote_request_form(invalid_budget_data)
    assert is_valid is False
    assert 'budget_range' in errors
    
    # Test with invalid project timeline
    invalid_timeline_data = {
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john@example.com',
        'company': 'Test Company',
        'service_interests': ['data_collection'],
        'project_description': 'A detailed project description with sufficient length.',
        'project_timeline': 'invalid_timeline'
    }
    is_valid, errors = validate_quote_request_form(invalid_timeline_data)
    assert is_valid is False
    assert 'project_timeline' in errors


def test_validate_upload_request_form():
    """Tests the validate_upload_request_form function with various form data."""
    # Test with valid data
    valid_data = {
        'name': 'John Doe',
        'email': 'john@example.com',
        'company': 'Test Company',
        'phone': '+1 (555) 123-4567',
        'service_interest': 'data_preparation',
        'description': 'We have a dataset that needs preparation for AI model training.'
    }
    is_valid, errors = validate_upload_request_form(valid_data)
    assert is_valid is True
    assert errors == {}
    
    # Test with missing required fields
    invalid_data = {
        'name': 'John Doe',
        'company': 'Test Company'
    }
    is_valid, errors = validate_upload_request_form(invalid_data)
    assert is_valid is False
    assert 'email' in errors
    assert 'service_interest' in errors
    
    # Test with invalid email
    invalid_email_data = {
        'name': 'John Doe',
        'email': 'invalid-email',
        'company': 'Test Company',
        'service_interest': 'data_preparation'
    }
    is_valid, errors = validate_upload_request_form(invalid_email_data)
    assert is_valid is False
    assert 'email' in errors
    
    # Test with invalid service interest
    invalid_service_data = {
        'name': 'John Doe',
        'email': 'john@example.com',
        'company': 'Test Company',
        'service_interest': 'invalid_service'
    }
    is_valid, errors = validate_upload_request_form(invalid_service_data)
    assert is_valid is False
    assert 'service_interest' in errors


def test_validate_file_metadata():
    """Tests the validate_file_metadata function with various metadata dictionaries."""
    # Mock the validation functions
    with patch('app.security.input_validation.validate_file_extension') as mock_extension, \
         patch('app.security.input_validation.validate_file_size') as mock_size, \
         patch('app.security.input_validation.validate_mime_type') as mock_mime:
        
        # Test with valid metadata
        mock_extension.return_value = True
        mock_size.return_value = True
        mock_mime.return_value = True
        
        valid_metadata = {
            'filename': 'test.csv',
            'size': 1024 * 1024,  # 1 MB
            'mime_type': 'text/csv'
        }
        is_valid, errors = validate_file_metadata(valid_metadata)
        assert is_valid is True
        assert errors == {}
        
        # Test with missing required fields
        invalid_metadata = {
            'filename': 'test.csv'
        }
        is_valid, errors = validate_file_metadata(invalid_metadata)
        assert is_valid is False
        assert 'size' in errors
        assert 'mime_type' in errors
        
        # Test with invalid file extension
        mock_extension.return_value = False
        mock_size.return_value = True
        mock_mime.return_value = True
        
        invalid_ext_metadata = {
            'filename': 'test.exe',
            'size': 1024 * 1024,
            'mime_type': 'application/octet-stream'
        }
        is_valid, errors = validate_file_metadata(invalid_ext_metadata)
        assert is_valid is False
        assert 'filename' in errors
        
        # Test with invalid file size
        mock_extension.return_value = True
        mock_size.return_value = False
        mock_mime.return_value = True
        
        invalid_size_metadata = {
            'filename': 'test.csv',
            'size': 100 * 1024 * 1024,  # 100 MB
            'mime_type': 'text/csv'
        }
        is_valid, errors = validate_file_metadata(invalid_size_metadata)
        assert is_valid is False
        assert 'size' in errors
        
        # Test with invalid MIME type
        mock_extension.return_value = True
        mock_size.return_value = True
        mock_mime.return_value = False
        
        invalid_mime_metadata = {
            'filename': 'test.csv',
            'size': 1024 * 1024,
            'mime_type': 'application/octet-stream'  # Mismatch with .csv
        }
        is_valid, errors = validate_file_metadata(invalid_mime_metadata)
        assert is_valid is False
        assert 'mime_type' in errors


def test_input_validator_class_methods():
    """Tests the static methods of the InputValidator class."""
    # Test validate_email
    assert InputValidator.validate_email('test@example.com') is True
    assert InputValidator.validate_email('invalid-email') is False
    
    # Test validate_phone
    assert InputValidator.validate_phone('+1 (555) 123-4567', 'US') is True
    assert InputValidator.validate_phone('invalid-phone', 'US') is False
    
    # Test validate_url
    assert InputValidator.validate_url('https://example.com') is True
    assert InputValidator.validate_url('invalid-url') is False
    
    # Test validate_date_format
    assert InputValidator.validate_date_format('2023-05-15') is True
    assert InputValidator.validate_date_format('05/15/2023') is False
    
    # Test validate_time_format
    assert InputValidator.validate_time_format('14:30') is True
    assert InputValidator.validate_time_format('24:00') is False
    
    # Test sanitize_input
    assert InputValidator.sanitize_input('<script>alert("XSS")</script>') == '&lt;script&gt;alert("XSS")&lt;/script&gt;'
    
    # Test validate_file_extension
    with patch('app.security.input_validation.settings') as mock_settings:
        mock_settings.ALLOWED_UPLOAD_EXTENSIONS = "pdf,csv,json,xml,jpg,jpeg,png"
        assert InputValidator.validate_file_extension('test.pdf') is True
        assert InputValidator.validate_file_extension('test.exe') is False
    
    # Test validate_file_size
    with patch('app.security.input_validation.settings') as mock_settings:
        mock_settings.MAX_UPLOAD_SIZE_MB = 50
        assert InputValidator.validate_file_size(10 * 1024 * 1024) is True  # 10 MB
        assert InputValidator.validate_file_size(100 * 1024 * 1024) is False  # 100 MB
    
    # Test validate_mime_type
    assert InputValidator.validate_mime_type('application/pdf', 'test.pdf') is True
    assert InputValidator.validate_mime_type('text/plain', 'test.pdf') is False


def test_input_validator_validate_form_data():
    """Tests the validate_form_data method of the InputValidator class."""
    # Test contact form validation
    with patch('app.security.input_validation.validate_contact_form') as mock_contact:
        mock_contact.return_value = (True, {})
        test_data = {'name': 'Test User', 'email': 'test@example.com', 'message': 'Hello'}
        is_valid, errors = InputValidator.validate_form_data(test_data, 'contact')
        mock_contact.assert_called_once_with(test_data)
        assert is_valid is True
        assert errors == {}
    
    # Test demo request form validation
    with patch('app.security.input_validation.validate_demo_request_form') as mock_demo:
        mock_demo.return_value = (True, {})
        test_data = {'first_name': 'Test', 'last_name': 'User', 'email': 'test@example.com'}
        is_valid, errors = InputValidator.validate_form_data(test_data, 'demo_request')
        mock_demo.assert_called_once_with(test_data)
        assert is_valid is True
        assert errors == {}
    
    # Test quote request form validation
    with patch('app.security.input_validation.validate_quote_request_form') as mock_quote:
        mock_quote.return_value = (True, {})
        test_data = {'first_name': 'Test', 'last_name': 'User', 'email': 'test@example.com'}
        is_valid, errors = InputValidator.validate_form_data(test_data, 'quote_request')
        mock_quote.assert_called_once_with(test_data)
        assert is_valid is True
        assert errors == {}
    
    # Test upload request form validation
    with patch('app.security.input_validation.validate_upload_request_form') as mock_upload:
        mock_upload.return_value = (True, {})
        test_data = {'name': 'Test User', 'email': 'test@example.com'}
        is_valid, errors = InputValidator.validate_form_data(test_data, 'upload_request')
        mock_upload.assert_called_once_with(test_data)
        assert is_valid is True
        assert errors == {}
    
    # Test with invalid form type
    with pytest.raises(ValueError):
        InputValidator.validate_form_data({}, 'invalid_form_type')


def test_validation_decorator_validate_request_data():
    """Tests the validate_request_data decorator of the ValidationDecorator class."""
    # Create a Pydantic model for testing
    class TestSchema(BaseModel):
        name: str
        email: str
        age: int
    
    # Create a test function with the decorator
    @ValidationDecorator.validate_request_data(TestSchema)
    async def test_function(request, validated_data):
        return validated_data
    
    # Create a mock request with valid data
    mock_request = MagicMock()
    mock_request.method = "POST"
    mock_request.json.return_value = {"name": "Test User", "email": "test@example.com", "age": 30}
    
    # Test with valid data
    import asyncio
    result = asyncio.run(test_function(mock_request))
    assert result["name"] == "Test User"
    assert result["email"] == "test@example.com"
    assert result["age"] == 30
    
    # Test with invalid data
    mock_request.json.return_value = {"name": "Test User", "email": "invalid-email"}
    with pytest.raises(ValidationException):
        asyncio.run(test_function(mock_request))
    
    # Test with missing required fields
    mock_request.json.return_value = {"name": "Test User"}
    with pytest.raises(ValidationException):
        asyncio.run(test_function(mock_request))


def test_validation_decorator_validate_form_submission():
    """Tests the validate_form_submission decorator of the ValidationDecorator class."""
    # Mock InputValidator.validate_form_data
    with patch('app.security.input_validation.InputValidator.validate_form_data') as mock_validate:
        mock_validate.return_value = (True, {})
        
        # Create a test function with the decorator
        @ValidationDecorator.validate_form_submission('contact')
        async def test_function(request, validated_data):
            return validated_data
        
        # Create a mock request with form data
        mock_request = MagicMock()
        mock_request.method = "POST"
        test_data = {"name": "Test User", "email": "test@example.com", "message": "Hello"}
        mock_request.json.return_value = test_data
        
        # Test with valid data
        import asyncio
        result = asyncio.run(test_function(mock_request))
        mock_validate.assert_called_once_with(test_data, 'contact')
        assert result == test_data
        
        # Test with invalid data
        mock_validate.reset_mock()
        mock_validate.return_value = (False, {"email": "Invalid email format"})
        
        with pytest.raises(ValidationException):
            asyncio.run(test_function(mock_request))
        mock_validate.assert_called_once_with(test_data, 'contact')


def test_integration_with_fastapi_endpoint():
    """Integration test for validation with FastAPI endpoints."""
    # Create a test FastAPI application
    app = FastAPI()
    
    # Add a test endpoint with ValidationDecorator
    @app.post("/api/test/contact")
    @ValidationDecorator.validate_form_submission('contact')
    async def contact_endpoint(request: Request, validated_data: dict):
        return {"status": "success", "data": validated_data}
    
    # Create a test client
    client = TestClient(app)
    
    # Mock InputValidator.validate_form_data
    with patch('app.security.input_validation.InputValidator.validate_form_data') as mock_validate:
        # Test with valid data
        mock_validate.return_value = (True, {})
        test_data = {"name": "Test User", "email": "test@example.com", "message": "Hello"}
        
        response = client.post("/api/test/contact", json=test_data)
        assert response.status_code == 200
        assert response.json()["status"] == "success"
        assert response.json()["data"] == test_data
        
        # Test with invalid data
        mock_validate.return_value = (False, {"email": "Invalid email format"})
        
        response = client.post("/api/test/contact", json=test_data)
        assert response.status_code == 422  # HTTP 422 Unprocessable Entity
        assert "errors" in response.json()