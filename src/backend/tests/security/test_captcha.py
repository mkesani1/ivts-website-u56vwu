import pytest
from unittest.mock import patch, MagicMock
import json
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from app.security.captcha import (
    verify_captcha,
    validate_captcha_token,
    require_captcha,
    CaptchaVerifier
)
from app.core.exceptions import SecurityException
from app.core.config import settings


class MockResponse:
    """Mock response class for simulating HTTP responses in tests"""
    
    def __init__(self, json_data, status_code):
        self._json_data = json_data
        self.status_code = status_code
        
    def json(self):
        return self._json_data


@pytest.mark.parametrize('score', [0.5, 0.7, 0.9])
def test_verify_captcha_success(score):
    """Tests successful verification of a valid captcha token"""
    # Mock the requests.post function to return a successful response with the given score
    with patch('requests.post') as mock_post:
        mock_post.return_value = MockResponse(
            {'success': True, 'score': score, 'action': 'submit'}, 200
        )
        
        result = verify_captcha('test_token', '127.0.0.1')
        
        # Assert that the result contains success=True
        assert result['success'] is True
        # Assert that the result contains the expected score
        assert result['score'] == score
        
        # Verify that requests.post was called with the correct parameters
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert args[0] == 'https://www.google.com/recaptcha/api/siteverify'
        assert kwargs['data']['secret'] == settings.RECAPTCHA_SECRET_KEY
        assert kwargs['data']['response'] == 'test_token'
        assert kwargs['data']['remoteip'] == '127.0.0.1'


def test_verify_captcha_failure():
    """Tests failure verification of an invalid captcha token"""
    # Mock the requests.post function to return a failure response
    with patch('requests.post') as mock_post:
        mock_post.return_value = MockResponse(
            {'success': False, 'error-codes': ['invalid-input-response']}, 200
        )
        
        result = verify_captcha('invalid_token', '127.0.0.1')
        
        # Assert that the result contains success=False
        assert result['success'] is False
        
        # Verify that requests.post was called with the correct parameters
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert args[0] == 'https://www.google.com/recaptcha/api/siteverify'
        assert kwargs['data']['response'] == 'invalid_token'


def test_verify_captcha_missing_token():
    """Tests that SecurityException is raised when token is missing"""
    with pytest.raises(SecurityException) as excinfo:
        verify_captcha(None, '127.0.0.1')
    
    # Verify that the exception message mentions missing token
    assert "CAPTCHA verification failed" in str(excinfo.value)
    assert excinfo.value.details.get('reason') == "No token provided"


def test_verify_captcha_request_error():
    """Tests handling of request errors during captcha verification"""
    # Mock the requests.post function to raise an exception
    with patch('requests.post') as mock_post:
        mock_post.side_effect = Exception("Connection error")
        
        result = verify_captcha('test_token', '127.0.0.1')
        
        # Assert that the result contains success=False
        assert result['success'] is False
        # Assert that the result contains an error message
        assert "Connection error" in result['error']


@pytest.mark.parametrize('score,threshold,expected', [
    (0.9, 0.5, True),   # High score, should pass
    (0.5, 0.5, True),   # Equal to threshold, should pass
    (0.4, 0.5, False),  # Below threshold, should fail
])
def test_validate_captcha_token_success(score, threshold, expected):
    """Tests successful validation of a captcha token with score above threshold"""
    # Mock the verify_captcha function to return a successful response with the given score
    with patch('app.security.captcha.verify_captcha') as mock_verify:
        mock_verify.return_value = {'success': True, 'score': score}
        
        result = validate_captcha_token('test_token', '127.0.0.1', threshold)
        
        # Assert that the result matches the expected outcome based on score and threshold
        assert result is expected
        
        # Verify that verify_captcha was called with the correct parameters
        mock_verify.assert_called_once_with('test_token', '127.0.0.1')


def test_validate_captcha_token_failure():
    """Tests failure validation when captcha verification fails"""
    # Mock the verify_captcha function to return a failure response
    with patch('app.security.captcha.verify_captcha') as mock_verify:
        mock_verify.return_value = {'success': False, 'error-codes': ['invalid-input-response']}
        
        result = validate_captcha_token('invalid_token', '127.0.0.1', 0.5)
        
        # Assert that the result is False
        assert result is False
        
        # Verify that verify_captcha was called with the correct parameters
        mock_verify.assert_called_once_with('invalid_token', '127.0.0.1')


def test_captcha_verifier_init():
    """Tests initialization of CaptchaVerifier with custom and default values"""
    # Test with custom values
    custom_verifier = CaptchaVerifier(
        secret_key="custom_secret",
        site_key="custom_site_key",
        verify_url="https://custom.verify.url",
        score_threshold=0.7
    )
    
    assert custom_verifier._secret_key == "custom_secret"
    assert custom_verifier._site_key == "custom_site_key"
    assert custom_verifier._verify_url == "https://custom.verify.url"
    assert custom_verifier._score_threshold == 0.7
    
    # Test with default values
    default_verifier = CaptchaVerifier()
    
    assert default_verifier._secret_key == settings.RECAPTCHA_SECRET_KEY
    assert default_verifier._site_key == settings.RECAPTCHA_SITE_KEY
    assert default_verifier._verify_url == "https://www.google.com/recaptcha/api/siteverify"
    assert default_verifier._score_threshold == 0.5


def test_captcha_verifier_verify():
    """Tests the verify method of CaptchaVerifier"""
    verifier = CaptchaVerifier(
        secret_key="test_secret",
        site_key="test_site_key"
    )
    
    # Mock the requests.post function to return a successful response
    with patch('requests.post') as mock_post:
        mock_post.return_value = MockResponse(
            {'success': True, 'score': 0.8}, 200
        )
        
        result = verifier.verify('test_token', '127.0.0.1')
        
        # Assert that the result contains success=True
        assert result['success'] is True
        assert result['score'] == 0.8
        
        # Verify that requests.post was called with the correct parameters
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert kwargs['data']['secret'] == "test_secret"
        assert kwargs['data']['response'] == 'test_token'


@pytest.mark.parametrize('score,threshold,expected', [
    (0.9, 0.5, True),   # High score, should pass
    (0.5, 0.5, True),   # Equal to threshold, should pass
    (0.4, 0.5, False),  # Below threshold, should fail
])
def test_captcha_verifier_validate(score, threshold, expected):
    """Tests the validate method of CaptchaVerifier"""
    verifier = CaptchaVerifier()
    
    # Create a CaptchaVerifier instance with a mocked verify method
    verifier.verify = MagicMock(return_value={'success': True, 'score': score})
    
    # Call the validate method with a test token, IP address, and threshold
    result = verifier.validate('test_token', '127.0.0.1', threshold)
    
    # Assert that the result matches the expected outcome based on score and threshold
    assert result is expected
    
    # Verify that verify was called with the correct parameters
    verifier.verify.assert_called_once_with('test_token', '127.0.0.1')


def test_captcha_verifier_get_site_key():
    """Tests the get_site_key method of CaptchaVerifier"""
    # Create a CaptchaVerifier instance with a custom site key
    verifier = CaptchaVerifier(site_key="test_site_key")
    
    # Call the get_site_key method
    site_key = verifier.get_site_key()
    
    # Assert that the returned value matches the custom site key
    assert site_key == "test_site_key"


def test_require_captcha_decorator_success():
    """Tests the require_captcha decorator with successful validation"""
    # Create a mock FastAPI app with an endpoint decorated with require_captcha
    app = FastAPI()
    
    @app.post("/protected")
    @require_captcha(threshold=0.5)
    async def protected_endpoint(request: Request):
        return {"message": "Success"}
    
    # Mock the validate_captcha_token function to return True
    with patch('app.security.captcha.validate_captcha_token', return_value=True):
        client = TestClient(app)
        response = client.post(
            "/protected",
            json={"captcha_token": "valid_token", "data": "test"}
        )
        
        # Assert that the response status code is 200
        assert response.status_code == 200
        # Assert that the response contains the expected data
        assert response.json() == {"message": "Success"}


def test_require_captcha_decorator_failure():
    """Tests the require_captcha decorator with failed validation"""
    # Create a mock FastAPI app with an endpoint decorated with require_captcha
    app = FastAPI()
    
    @app.post("/protected")
    @require_captcha(threshold=0.5)
    async def protected_endpoint(request: Request):
        return {"message": "Success"}
    
    # Mock the validate_captcha_token function to return False
    with patch('app.security.captcha.validate_captcha_token', return_value=False):
        client = TestClient(app)
        response = client.post(
            "/protected",
            json={"captcha_token": "invalid_token", "data": "test"}
        )
        
        # Assert that the response status code is 403
        assert response.status_code == 403
        # Assert that the response contains an error message about captcha verification
        assert "CAPTCHA verification failed" in response.json().get("detail", "")


def test_require_captcha_decorator_missing_token():
    """Tests the require_captcha decorator with missing captcha token"""
    # Create a mock FastAPI app with an endpoint decorated with require_captcha
    app = FastAPI()
    
    @app.post("/protected")
    @require_captcha(threshold=0.5)
    async def protected_endpoint(request: Request):
        return {"message": "Success"}
    
    client = TestClient(app)
    response = client.post(
        "/protected",
        json={"data": "test"}  # No captcha token
    )
    
    # Assert that the response status code is 403
    assert response.status_code == 403
    # Assert that the response contains an error message about missing captcha token
    assert "CAPTCHA verification failed" in response.json().get("detail", "")


def test_integration_with_contact_endpoint():
    """Integration test for captcha verification with contact form endpoint"""
    # Create a test client for the application
    app = FastAPI()
    
    @app.post("/api/v1/contact")
    @require_captcha()
    async def contact_endpoint(request: Request):
        return {"success": True, "message": "Contact form submitted successfully"}
    
    # Mock the validate_captcha_token function to return True
    with patch('app.security.captcha.validate_captcha_token', return_value=True):
        client = TestClient(app)
        response = client.post(
            "/api/v1/contact",
            json={
                "name": "Test User",
                "email": "test@example.com",
                "message": "Test message",
                "captcha_token": "valid_token"
            }
        )
        
        # Assert that the response status code is 200
        assert response.status_code == 200
        # Assert that the response indicates successful submission
        assert response.json()["success"] is True


def test_integration_with_demo_request_endpoint():
    """Integration test for captcha verification with demo request endpoint"""
    app = FastAPI()
    
    @app.post("/api/v1/demo-request")
    @require_captcha()
    async def demo_request_endpoint(request: Request):
        return {"success": True, "message": "Demo request submitted successfully"}
    
    # Mock the validate_captcha_token function to return True
    with patch('app.security.captcha.validate_captcha_token', return_value=True):
        client = TestClient(app)
        response = client.post(
            "/api/v1/demo-request",
            json={
                "firstName": "Test",
                "lastName": "User",
                "email": "test@example.com",
                "company": "Test Company",
                "jobTitle": "Tester",
                "phone": "1234567890",
                "serviceInterest": ["Data Collection"],
                "projectDescription": "Test project",
                "captcha_token": "valid_token"
            }
        )
        
        # Assert that the response status code is 200
        assert response.status_code == 200
        # Assert that the response indicates successful submission
        assert response.json()["success"] is True


def test_integration_with_quote_request_endpoint():
    """Integration test for captcha verification with quote request endpoint"""
    app = FastAPI()
    
    @app.post("/api/v1/quote-request")
    @require_captcha()
    async def quote_request_endpoint(request: Request):
        return {"success": True, "message": "Quote request submitted successfully"}
    
    # Mock the validate_captcha_token function to return True
    with patch('app.security.captcha.validate_captcha_token', return_value=True):
        client = TestClient(app)
        response = client.post(
            "/api/v1/quote-request",
            json={
                "firstName": "Test",
                "lastName": "User",
                "email": "test@example.com",
                "company": "Test Company",
                "jobTitle": "Tester",
                "phone": "1234567890",
                "serviceInterest": ["Data Collection"],
                "projectDetails": "Test project",
                "captcha_token": "valid_token"
            }
        )
        
        # Assert that the response status code is 200
        assert response.status_code == 200
        # Assert that the response indicates successful submission
        assert response.json()["success"] is True


def test_integration_with_upload_request_endpoint():
    """Integration test for captcha verification with file upload request endpoint"""
    app = FastAPI()
    
    @app.post("/api/v1/upload/request", status_code=201)
    @require_captcha()
    async def upload_request_endpoint(request: Request):
        return {
            "uploadUrl": "https://s3.example.com/upload/12345",
            "uploadId": "12345"
        }
    
    # Mock the validate_captcha_token function to return True
    with patch('app.security.captcha.validate_captcha_token', return_value=True):
        client = TestClient(app)
        response = client.post(
            "/api/v1/upload/request",
            json={
                "fileName": "test.csv",
                "fileSize": 1024,
                "fileType": "text/csv",
                "captcha_token": "valid_token"
            }
        )
        
        # Assert that the response status code is 201
        assert response.status_code == 201
        # Assert that the response contains upload URL and ID
        response_data = response.json()
        assert "uploadUrl" in response_data
        assert "uploadId" in response_data