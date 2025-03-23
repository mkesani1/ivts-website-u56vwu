"""
Test module for the contact form API endpoint in the IndiVillage backend application.

This module contains unit and integration tests to verify the functionality, validation,
error handling, and security features of the contact form submission process.
"""

import pytest
from fastapi.testclient import TestClient  # fastapi 0.95.0
import json  # stdlib
from unittest.mock import patch, MagicMock  # stdlib
from sqlalchemy.orm import Session  # sqlalchemy 1.4.41

from app.api.v1.schemas.contact import ContactSchema, ContactResponseSchema
from app.core.exceptions import ValidationException, SecurityException
from app.api.v1.models.form_submission import FormSubmission, FormType

# Test data constants
VALID_CONTACT_DATA = {
    'name': 'John Doe',
    'email': 'john.doe@example.com',
    'company': 'Example Corp',
    'phone': '+1234567890',
    'message': 'This is a test message',
    'captcha_token': 'valid_token'
}

INVALID_CONTACT_DATA = {
    'name': '',
    'email': 'invalid-email',
    'company': 'Example Corp',
    'phone': '+1234567890',
    'message': 'This is a test message',
    'captcha_token': 'valid_token'
}


class MockProcessContactForm:
    """Fixture class for mocking the process_contact_form function"""
    
    def __init__(self, return_value):
        """Initialize the mock with a return value or exception to raise"""
        self.return_value = return_value
    
    def __call__(self, form_data, client_ip, trace_id):
        """Mock implementation of process_contact_form"""
        if isinstance(self.return_value, Exception):
            raise self.return_value
        return self.return_value


@pytest.fixture
def mock_process_contact_form(request):
    """Fixture for mocking the process_contact_form function"""
    # Configure the mock based on the parameter provided
    mock = MockProcessContactForm(request.param)
    
    # Use patch to replace the actual function with our mock
    with patch('app.api.v1.services.contact.process_contact_form', mock):
        yield mock


@pytest.mark.parametrize('mock_process_contact_form', [
    {'success': True, 'message': 'Contact form submitted successfully', 'submission_id': 'test-uuid'}
], indirect=True)
def test_contact_form_valid_submission(client, mock_process_contact_form):
    """Tests successful contact form submission with valid data"""
    # Set up mock for validate_captcha_token to return True
    with patch('app.api.v1.services.security.validate_captcha_token', return_value=True):
        # Create a POST request to /api/v1/contact/ with VALID_CONTACT_DATA
        response = client.post(
            "/api/v1/contact/",
            json=VALID_CONTACT_DATA
        )
        
        # Assert response status code is 200
        assert response.status_code == 200
        
        # Parse the response JSON
        data = response.json()
        
        # Assert response JSON contains success=True
        assert data['success'] is True
        
        # Assert response JSON contains expected message
        assert data['message'] == 'Contact form submitted successfully'
        
        # Assert response JSON contains submission_id
        assert 'submission_id' in data
        
        # Verify process_contact_form was called with correct arguments
        # Note: In a real test case, we would verify the mock was called with correct arguments
        # but for simplicity, we just check the response reflects our mocked return value


def test_contact_form_invalid_data(client):
    """Tests contact form submission with invalid data"""
    # Set up mock for validate_captcha_token to return True
    with patch('app.api.v1.services.security.validate_captcha_token', return_value=True):
        # Create a POST request to /api/v1/contact/ with INVALID_CONTACT_DATA
        response = client.post(
            "/api/v1/contact/",
            json=INVALID_CONTACT_DATA
        )
        
        # Assert response status code is 422
        assert response.status_code == 422
        
        # Parse the response JSON
        data = response.json()
        
        # Assert response JSON contains success=False
        assert data['success'] is False
        
        # Assert response JSON contains validation error messages
        assert 'errors' in data
        
        # Assert error message for email field indicates invalid format
        assert 'email' in data['errors']
        assert 'invalid' in data['errors']['email'].lower()
        
        # Assert error message for name field indicates required field
        assert 'name' in data['errors']
        assert 'required' in data['errors']['name'].lower() or 'empty' in data['errors']['name'].lower()


def test_contact_form_missing_captcha(client):
    """Tests contact form submission with missing CAPTCHA token"""
    # Create a copy of VALID_CONTACT_DATA without captcha_token
    data = VALID_CONTACT_DATA.copy()
    data.pop('captcha_token')
    
    # Create a POST request to /api/v1/contact/ with the modified data
    response = client.post(
        "/api/v1/contact/",
        json=data
    )
    
    # Assert response status code is 403
    assert response.status_code == 403
    
    # Parse the response JSON
    data = response.json()
    
    # Assert response JSON contains success=False
    assert data['success'] is False
    
    # Assert response JSON contains error message about missing CAPTCHA
    assert 'captcha' in data['message'].lower()


def test_contact_form_invalid_captcha(client):
    """Tests contact form submission with invalid CAPTCHA token"""
    # Set up mock for validate_captcha_token to return False
    with patch('app.api.v1.services.security.validate_captcha_token', return_value=False):
        # Create a POST request to /api/v1/contact/ with VALID_CONTACT_DATA
        response = client.post(
            "/api/v1/contact/",
            json=VALID_CONTACT_DATA
        )
        
        # Assert response status code is 403
        assert response.status_code == 403
        
        # Parse the response JSON
        data = response.json()
        
        # Assert response JSON contains success=False
        assert data['success'] is False
        
        # Assert response JSON contains error message about invalid CAPTCHA
        assert 'captcha' in data['message'].lower()


@pytest.mark.parametrize('mock_process_contact_form', [
    ValidationException('Processing error')
], indirect=True)
def test_contact_form_processing_error(client, mock_process_contact_form):
    """Tests contact form submission when processing service raises an exception"""
    # Set up mock for validate_captcha_token to return True
    with patch('app.api.v1.services.security.validate_captcha_token', return_value=True):
        # Create a POST request to /api/v1/contact/ with VALID_CONTACT_DATA
        response = client.post(
            "/api/v1/contact/",
            json=VALID_CONTACT_DATA
        )
        
        # Assert response status code is 422
        assert response.status_code == 422
        
        # Parse the response JSON
        data = response.json()
        
        # Assert response JSON contains success=False
        assert data['success'] is False
        
        # Assert response JSON contains error message from the exception
        assert 'Processing error' in data['message']


@pytest.mark.parametrize('mock_process_contact_form', [
    SecurityException('Security error')
], indirect=True)
def test_contact_form_security_error(client, mock_process_contact_form):
    """Tests contact form submission when security service raises an exception"""
    # Set up mock for validate_captcha_token to return True
    with patch('app.api.v1.services.security.validate_captcha_token', return_value=True):
        # Create a POST request to /api/v1/contact/ with VALID_CONTACT_DATA
        response = client.post(
            "/api/v1/contact/",
            json=VALID_CONTACT_DATA
        )
        
        # Assert response status code is 403
        assert response.status_code == 403
        
        # Parse the response JSON
        data = response.json()
        
        # Assert response JSON contains success=False
        assert data['success'] is False
        
        # Assert response JSON contains error message from the exception
        assert 'Security error' in data['message']


@pytest.mark.parametrize('mock_process_contact_form', [
    Exception('Unexpected error')
], indirect=True)
def test_contact_form_unexpected_error(client, mock_process_contact_form):
    """Tests contact form submission when an unexpected error occurs"""
    # Set up mock for validate_captcha_token to return True
    with patch('app.api.v1.services.security.validate_captcha_token', return_value=True):
        # Create a POST request to /api/v1/contact/ with VALID_CONTACT_DATA
        response = client.post(
            "/api/v1/contact/",
            json=VALID_CONTACT_DATA
        )
        
        # Assert response status code is 500
        assert response.status_code == 500
        
        # Parse the response JSON
        data = response.json()
        
        # Assert response JSON contains success=False
        assert data['success'] is False
        
        # Assert response JSON contains a generic error message (not the specific exception message)
        assert 'unexpected error' in data['message'].lower()
        # Ensure specific error message is not exposed for security reasons
        assert 'Unexpected error' not in data['message']


def test_contact_form_integration(client, test_db):
    """Integration test for contact form submission that verifies database record creation
    
    Note: This test requires the test_db fixture which should provide an SQLAlchemy session
    for database operations during testing.
    """
    # Set up mock for validate_captcha_token to return True
    with patch('app.api.v1.services.security.validate_captcha_token', return_value=True):
        # Set up mocks for CRM and email services to prevent external calls
        with patch('app.api.v1.services.crm.add_contact_to_crm'):
            with patch('app.api.v1.services.notification.send_email'):
                # Create a POST request to /api/v1/contact/ with VALID_CONTACT_DATA
                response = client.post(
                    "/api/v1/contact/",
                    json=VALID_CONTACT_DATA
                )
                
                # Assert response status code is 200
                assert response.status_code == 200
                
                # Assert response JSON contains success=True
                assert response.json()['success'] is True
                
                # Get the submission_id from the response
                submission_id = response.json()['submission_id']
                
                # Query the database for FormSubmission records
                form_submission = test_db.query(FormSubmission).filter_by(id=submission_id).first()
                
                # Assert a record was created with FormType.CONTACT
                assert form_submission is not None
                assert form_submission.form_type == FormType.CONTACT
                
                # Assert the record contains the submitted data
                form_data = form_submission.get_data()
                assert form_data.get('name') == VALID_CONTACT_DATA['name']
                assert form_data.get('email') == VALID_CONTACT_DATA['email']
                assert form_data.get('company') == VALID_CONTACT_DATA['company']
                
                # Assert the record has the correct client IP address
                # Note: In a test client, this will typically be '127.0.0.1' or similar
                assert form_submission.ip_address is not None