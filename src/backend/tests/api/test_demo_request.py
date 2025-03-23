# Third-party imports
import json  # json v2.0.9
import uuid  # uuid v1.30
from datetime import datetime  # datetime v3.11
from unittest.mock import patch  # unittest.mock v3.8

import pytest  # pytest v7.3.1
from fastapi.testclient import TestClient  # fastapi v0.95.0

# Internal imports
from app.api.v1.schemas.demo_request import DemoRequestSchema, ServiceInterestEnum, TimeZoneEnum
from app.core.exceptions import SecurityException, ValidationException, ProcessingException
from app.security.captcha import validate_captcha_token
from app.services.form_processing_service import process_demo_request

# Define the API endpoint for demo requests
DEMO_REQUEST_ENDPOINT = "/api/v1/demo-request"

# Define valid demo request data for testing
VALID_DEMO_REQUEST_DATA = {
    "first_name": "Test",
    "last_name": "User",
    "email": "test@example.com",
    "phone": "+1234567890",
    "company": "Test Company",
    "job_title": "Test Manager",
    "service_interests": ["DATA_COLLECTION", "AI_MODEL_DEVELOPMENT"],
    "preferred_date": "2023-12-01",
    "preferred_time": "10:00",
    "time_zone": "UTC",
    "project_details": "Test project details",
    "referral_source": "Website",
    "marketing_consent": True,
    "captcha_token": "valid_token"
}


@pytest.fixture
def valid_demo_request_data() -> dict:
    """Fixture that provides valid demo request data for tests

    Returns:
        dict: Valid demo request data
    """
    # Return a dictionary with valid demo request data including all required fields
    # Include first_name, last_name, email, phone, company, job_title
    # Include service_interests as a list of valid ServiceInterestEnum values
    # Include preferred_date, preferred_time, time_zone
    # Include project_details, referral_source, marketing_consent
    # Include a dummy captcha_token
    return VALID_DEMO_REQUEST_DATA


@pytest.mark.parametrize("mock_return_value", [True])
@patch("app.security.captcha.validate_captcha_token")
def test_demo_request_valid_submission(client: TestClient, valid_demo_request_data: dict, mock_validate_captcha_token):
    """Tests successful demo request submission

    Args:
        client (TestClient): FastAPI test client
        valid_demo_request_data (dict): Valid demo request data
    """
    # Mock validate_captcha_token to return True
    mock_validate_captcha_token.return_value = True

    # Mock process_demo_request to return a success response with a UUID
    submission_id = uuid.uuid4()
    with patch("app.services.form_processing_service.process_demo_request") as mock_process_demo_request:
        mock_process_demo_request.return_value = {"success": True, "submission_id": submission_id}

        # Send POST request to demo request endpoint with valid data
        response = client.post(DEMO_REQUEST_ENDPOINT, json=valid_demo_request_data)

        # Assert response status code is 200
        assert response.status_code == 200

        # Assert response JSON contains success=True
        assert response.json()["success"] is True

        # Assert response JSON contains a message
        assert "message" in response.json()

        # Assert response JSON contains a submission_id
        assert "submission_id" in response.json()

        # Verify process_demo_request was called with correct arguments
        mock_process_demo_request.assert_called_once_with(valid_demo_request_data)


@pytest.mark.parametrize(
    "field,value,expected_status_code,expected_error",
    [
        ("email", "invalid-email", 400, "Invalid email format"),
        ("phone", "invalid-phone", 400, "Invalid phone number format"),
        ("service_interests", [], 400, "At least one service interest must be selected"),
        ("first_name", "", 400, "First name is required"),
        ("last_name", "", 400, "Last name is required"),
        ("company", "", 400, "Company name is required"),
    ],
)
def test_demo_request_invalid_data(client: TestClient, valid_demo_request_data: dict, field, value, expected_status_code, expected_error):
    """Tests demo request submission with invalid data

    Args:
        client (TestClient): FastAPI test client
        valid_demo_request_data (dict): Valid demo request data
        field (str): Field to modify
        value (str): Invalid value for the field
        expected_status_code (int): Expected HTTP status code
        expected_error (str): Expected error message
    """
    # Create a copy of valid_demo_request_data
    invalid_data = valid_demo_request_data.copy()

    # Modify the specified field with the invalid value
    invalid_data[field] = value

    # Send POST request to demo request endpoint with invalid data
    response = client.post(DEMO_REQUEST_ENDPOINT, json=invalid_data)

    # Assert response status code matches expected_status_code
    assert response.status_code == expected_status_code

    # Assert response JSON contains success=False
    assert response.json()["success"] is False

    # Assert response JSON contains an error message that includes expected_error
    assert expected_error in response.json()["message"]


@pytest.mark.parametrize("field", ["first_name", "last_name", "email", "company", "service_interests", "captcha_token"])
def test_demo_request_missing_required_fields(client: TestClient, valid_demo_request_data: dict, field):
    """Tests demo request submission with missing required fields

    Args:
        client (TestClient): FastAPI test client
        valid_demo_request_data (dict): Valid demo request data
        field (str): Field to remove
    """
    # Create a copy of valid_demo_request_data
    incomplete_data = valid_demo_request_data.copy()

    # Remove the specified required field
    del incomplete_data[field]

    # Send POST request to demo request endpoint with incomplete data
    response = client.post(DEMO_REQUEST_ENDPOINT, json=incomplete_data)

    # Assert response status code is 400 or 422
    assert response.status_code in [400, 422]

    # Assert response JSON contains success=False
    assert response.json()["success"] is False

    # Assert response JSON contains an error message about the missing field
    assert field in response.json()["message"].lower()


@patch("app.security.captcha.validate_captcha_token")
def test_demo_request_captcha_failure(client: TestClient, valid_demo_request_data: dict, mock_validate_captcha_token):
    """Tests demo request submission with CAPTCHA verification failure

    Args:
        client (TestClient): FastAPI test client
        valid_demo_request_data (dict): Valid demo request data
    """
    # Mock validate_captcha_token to return False
    mock_validate_captcha_token.return_value = False

    # Send POST request to demo request endpoint with valid data
    response = client.post(DEMO_REQUEST_ENDPOINT, json=valid_demo_request_data)

    # Assert response status code is 400
    assert response.status_code == 400

    # Assert response JSON contains success=False
    assert response.json()["success"] is False

    # Assert response JSON contains an error message about CAPTCHA verification
    assert "captcha" in response.json()["message"].lower()


@patch("app.security.captcha.validate_captcha_token")
@patch("app.services.form_processing_service.process_demo_request")
def test_demo_request_processing_exception(client: TestClient, valid_demo_request_data: dict, mock_process_demo_request, mock_validate_captcha_token):
    """Tests demo request submission when processing exception occurs

    Args:
        client (TestClient): FastAPI test client
        valid_demo_request_data (dict): Valid demo request data
    """
    # Mock validate_captcha_token to return True
    mock_validate_captcha_token.return_value = True

    # Mock process_demo_request to raise ProcessingException with error message
    mock_process_demo_request.side_effect = ProcessingException(message="Processing failed")

    # Send POST request to demo request endpoint with valid data
    response = client.post(DEMO_REQUEST_ENDPOINT, json=valid_demo_request_data)

    # Assert response status code is 422
    assert response.status_code == 422

    # Assert response JSON contains success=False
    assert response.json()["success"] is False

    # Assert response JSON contains the error message from the exception
    assert "processing failed" in response.json()["message"].lower()


@patch("app.security.captcha.validate_captcha_token")
@patch("app.services.form_processing_service.process_demo_request")
def test_demo_request_validation_exception(client: TestClient, valid_demo_request_data: dict, mock_process_demo_request, mock_validate_captcha_token):
    """Tests demo request submission when validation exception occurs

    Args:
        client (TestClient): FastAPI test client
        valid_demo_request_data (dict): Valid demo request data
    """
    # Mock validate_captcha_token to return True
    mock_validate_captcha_token.return_value = True

    # Mock process_demo_request to raise ValidationException with error message
    mock_process_demo_request.side_effect = ValidationException(message="Validation failed")

    # Send POST request to demo request endpoint with valid data
    response = client.post(DEMO_REQUEST_ENDPOINT, json=valid_demo_request_data)

    # Assert response status code is 400
    assert response.status_code == 400

    # Assert response JSON contains success=False
    assert response.json()["success"] is False

    # Assert response JSON contains the error message from the exception
    assert "validation failed" in response.json()["message"].lower()


@patch("app.security.captcha.validate_captcha_token")
@patch("app.services.form_processing_service.process_demo_request")
def test_demo_request_security_exception(client: TestClient, valid_demo_request_data: dict, mock_process_demo_request, mock_validate_captcha_token):
    """Tests demo request submission when security exception occurs

    Args:
        client (TestClient): FastAPI test client
        valid_demo_request_data (dict): Valid demo request data
    """
    # Mock validate_captcha_token to return True
    mock_validate_captcha_token.return_value = True

    # Mock process_demo_request to raise SecurityException with error message
    mock_process_demo_request.side_effect = SecurityException(message="Security check failed")

    # Send POST request to demo request endpoint with valid data
    response = client.post(DEMO_REQUEST_ENDPOINT, json=valid_demo_request_data)

    # Assert response status code is 400
    assert response.status_code == 400

    # Assert response JSON contains success=False
    assert response.json()["success"] is False

    # Assert response JSON contains the error message from the exception
    assert "security check failed" in response.json()["message"].lower()


@patch("app.security.captcha.validate_captcha_token")
@patch("app.services.form_processing_service.process_demo_request")
def test_demo_request_unexpected_exception(client: TestClient, valid_demo_request_data: dict, mock_process_demo_request, mock_validate_captcha_token):
    """Tests demo request submission when unexpected exception occurs

    Args:
        client (TestClient): FastAPI test client
        valid_demo_request_data (dict): Valid demo request data
    """
    # Mock validate_captcha_token to return True
    mock_validate_captcha_token.return_value = True

    # Mock process_demo_request to raise Exception with error message
    mock_process_demo_request.side_effect = Exception(message="Unexpected error")

    # Send POST request to demo request endpoint with valid data
    response = client.post(DEMO_REQUEST_ENDPOINT, json=valid_demo_request_data)

    # Assert response status code is 500
    assert response.status_code == 500

    # Assert response JSON contains success=False
    assert response.json()["success"] is False

    # Assert response JSON contains a generic error message
    assert "internal server error" in response.json()["message"].lower()