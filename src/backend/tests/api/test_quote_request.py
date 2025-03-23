import pytest  # pytest ^7.3.1
from fastapi.testclient import TestClient  # fastapi.testclient ^0.95.0
import json  # json standard library
import uuid  # uuid standard library
from unittest.mock import patch  # unittest.mock standard library

from app.api.v1.schemas.quote_request import QuoteRequestSchema, ServiceInterestEnum, BudgetRangeEnum, ProjectTimelineEnum  # src/backend/app/api/v1/schemas/quote_request.py
from app.services.form_processing_service import process_quote_request  # src/backend/app/services/form_processing_service.py
from app.core.exceptions import ValidationException, SecurityException, ProcessingException  # src/backend/app/core/exceptions.py
from app.security.captcha import validate_captcha_token  # src/backend/app/security/captcha.py

QUOTE_REQUEST_ENDPOINT = "/api/v1/quote-request"
VALID_QUOTE_REQUEST_DATA = {
    "first_name": "Test",
    "last_name": "User",
    "email": "test@example.com",
    "phone": "+1234567890",
    "company": "Test Company",
    "job_title": "Test Manager",
    "service_interests": ["DATA_COLLECTION", "AI_MODEL_DEVELOPMENT"],
    "project_description": "Test project description",
    "project_timeline": "WITHIN_3_MONTHS",
    "budget_range": "BETWEEN_50K_100K",
    "referral_source": "Website",
    "marketing_consent": True,
    "captcha_token": "valid_token"
}


@pytest.fixture
def valid_quote_request_data():
    """Fixture that provides valid quote request data for tests"""
    return {
        "first_name": "Test",
        "last_name": "User",
        "email": "test@example.com",
        "phone": "+1234567890",
        "company": "Test Company",
        "job_title": "Test Manager",
        "service_interests": ["DATA_COLLECTION", "AI_MODEL_DEVELOPMENT"],
        "project_description": "Test project description",
        "project_timeline": "WITHIN_3_MONTHS",
        "budget_range": "BETWEEN_50K_100K",
        "referral_source": "Website",
        "marketing_consent": True,
        "captcha_token": "valid_token"
    }


@pytest.mark.parametrize("mock_return_value", [True])
@patch("app.security.captcha.validate_captcha_token")
def test_quote_request_valid_submission(mock_validate_captcha_token, client: TestClient, valid_quote_request_data: dict):
    """Tests successful quote request submission"""
    mock_validate_captcha_token.return_value = True
    mock_process_quote_request_return_value = uuid.uuid4()

    @patch("app.services.form_processing_service.process_quote_request")
    def run_test(mock_process_quote_request):
        mock_process_quote_request.return_value = mock_process_quote_request_return_value
        response = client.post(QUOTE_REQUEST_ENDPOINT, json=valid_quote_request_data)
        assert response.status_code == 200
        response_json = response.json()
        assert response_json["success"] is True
        assert "message" in response_json
        assert "submission_id" in response_json
        mock_process_quote_request.assert_called_once_with(valid_quote_request_data)
    run_test()


@pytest.mark.parametrize(
    "field,value,expected_status_code,expected_error",
    [
        ("email", "invalid-email", 400, "Invalid email format"),
        ("phone", "invalid-phone", 400, "Phone number can only contain digits, spaces, and characters: + - ( ) ."),
        ("service_interests", [], 400, "At least one service interest must be selected"),
        ("first_name", "", 400, "First name is required"),
        ("last_name", "", 400, "Last name is required"),
        ("company", "", 400, "Company name is required"),
        ("project_timeline", "INVALID_TIMELINE", 400, "Invalid value"),
        ("budget_range", "INVALID_BUDGET", 400, "Invalid value"),
    ],
)
def test_quote_request_invalid_data(client: TestClient, valid_quote_request_data: dict, field: str, value: any, expected_status_code: int, expected_error: str):
    """Tests quote request submission with invalid data"""
    data = valid_quote_request_data.copy()
    data[field] = value
    response = client.post(QUOTE_REQUEST_ENDPOINT, json=data)
    assert response.status_code == expected_status_code
    response_json = response.json()
    assert response_json["success"] is False
    assert expected_error in response_json["message"]


@pytest.mark.parametrize(
    "field",
    ["first_name", "last_name", "email", "company", "service_interests", "project_description", "project_timeline", "budget_range", "captcha_token"],
)
def test_quote_request_missing_required_fields(client: TestClient, valid_quote_request_data: dict, field: str):
    """Tests quote request submission with missing required fields"""
    data = valid_quote_request_data.copy()
    del data[field]
    response = client.post(QUOTE_REQUEST_ENDPOINT, json=data)
    assert response.status_code in [400, 422]
    response_json = response.json()
    assert response_json["success"] is False
    assert field in response_json["message"]


@patch("app.security.captcha.validate_captcha_token")
def test_quote_request_captcha_failure(mock_validate_captcha_token, client: TestClient, valid_quote_request_data: dict):
    """Tests quote request submission with CAPTCHA verification failure"""
    mock_validate_captcha_token.return_value = False
    response = client.post(QUOTE_REQUEST_ENDPOINT, json=valid_quote_request_data)
    assert response.status_code == 400
    response_json = response.json()
    assert response_json["success"] is False
    assert "CAPTCHA" in response_json["message"]


@patch("app.security.captcha.validate_captcha_token")
@patch("app.services.form_processing_service.process_quote_request")
def test_quote_request_processing_exception(mock_process_quote_request, mock_validate_captcha_token, client: TestClient, valid_quote_request_data: dict):
    """Tests quote request submission when processing exception occurs"""
    mock_validate_captcha_token.return_value = True
    mock_process_quote_request.side_effect = ProcessingException(message="Processing error")
    response = client.post(QUOTE_REQUEST_ENDPOINT, json=valid_quote_request_data)
    assert response.status_code == 422
    response_json = response.json()
    assert response_json["success"] is False
    assert "Processing error" in response_json["message"]


@patch("app.security.captcha.validate_captcha_token")
@patch("app.services.form_processing_service.process_quote_request")
def test_quote_request_validation_exception(mock_process_quote_request, mock_validate_captcha_token, client: TestClient, valid_quote_request_data: dict):
    """Tests quote request submission when validation exception occurs"""
    mock_validate_captcha_token.return_value = True
    mock_process_quote_request.side_effect = ValidationException(message="Validation error")
    response = client.post(QUOTE_REQUEST_ENDPOINT, json=valid_quote_request_data)
    assert response.status_code == 400
    response_json = response.json()
    assert response_json["success"] is False
    assert "Validation error" in response_json["message"]


@patch("app.security.captcha.validate_captcha_token")
@patch("app.services.form_processing_service.process_quote_request")
def test_quote_request_security_exception(mock_process_quote_request, mock_validate_captcha_token, client: TestClient, valid_quote_request_data: dict):
    """Tests quote request submission when security exception occurs"""
    mock_validate_captcha_token.return_value = True
    mock_process_quote_request.side_effect = SecurityException(message="Security error")
    response = client.post(QUOTE_REQUEST_ENDPOINT, json=valid_quote_request_data)
    assert response.status_code == 400
    response_json = response.json()
    assert response_json["success"] is False
    assert "Security error" in response_json["message"]


@patch("app.security.captcha.validate_captcha_token")
@patch("app.services.form_processing_service.process_quote_request")
def test_quote_request_unexpected_exception(mock_process_quote_request, mock_validate_captcha_token, client: TestClient, valid_quote_request_data: dict):
    """Tests quote request submission when unexpected exception occurs"""
    mock_validate_captcha_token.return_value = True
    mock_process_quote_request.side_effect = Exception(message="Unexpected error")
    response = client.post(QUOTE_REQUEST_ENDPOINT, json=valid_quote_request_data)
    assert response.status_code == 500
    response_json = response.json()
    assert response_json["success"] is False
    assert "Internal server error" in response_json["message"]


@pytest.mark.parametrize(
    "service_interests,expected_status_code",
    [
        ([], 400),
        (["INVALID_SERVICE"], 400),
        (["DATA_COLLECTION"], 200),
        (["DATA_COLLECTION", "AI_MODEL_DEVELOPMENT"], 200),
    ],
)
def test_quote_request_service_interest_validation(client: TestClient, valid_quote_request_data: dict, service_interests: list, expected_status_code: int):
    """Tests validation of service interests in quote request"""
    data = valid_quote_request_data.copy()
    data["service_interests"] = service_interests

    @patch("app.security.captcha.validate_captcha_token")
    def run_test(mock_validate_captcha_token):
        mock_validate_captcha_token.return_value = True

        @patch("app.services.form_processing_service.process_quote_request")
        def run_test2(mock_process_quote_request):
            mock_process_quote_request.return_value = uuid.uuid4()
            response = client.post(QUOTE_REQUEST_ENDPOINT, json=data)
            assert response.status_code == expected_status_code
            response_json = response.json()
            if expected_status_code == 400:
                assert "At least one service interest must be selected" in response_json["message"]
        run_test2()
    run_test()


@pytest.mark.parametrize(
    "budget_range,expected_status_code",
    [
        ("INVALID_BUDGET", 400),
        ("UNDER_10K", 200),
        ("BETWEEN_10K_50K", 200),
        ("BETWEEN_50K_100K", 200),
        ("BETWEEN_100K_500K", 200),
        ("OVER_500K", 200),
        ("NOT_SPECIFIED", 200),
    ],
)
def test_quote_request_budget_range_validation(client: TestClient, valid_quote_request_data: dict, budget_range: str, expected_status_code: int):
    """Tests validation of budget range in quote request"""
    data = valid_quote_request_data.copy()
    data["budget_range"] = budget_range

    @patch("app.security.captcha.validate_captcha_token")
    def run_test(mock_validate_captcha_token):
        mock_validate_captcha_token.return_value = True

        @patch("app.services.form_processing_service.process_quote_request")
        def run_test2(mock_process_quote_request):
            mock_process_quote_request.return_value = uuid.uuid4()
            response = client.post(QUOTE_REQUEST_ENDPOINT, json=data)
            assert response.status_code == expected_status_code
            response_json = response.json()
            if expected_status_code == 400:
                assert "Invalid value" in response_json["message"]
        run_test2()
    run_test()


@pytest.mark.parametrize(
    "project_timeline,expected_status_code",
    [
        ("INVALID_TIMELINE", 400),
        ("IMMEDIATELY", 200),
        ("WITHIN_1_MONTH", 200),
        ("WITHIN_3_MONTHS", 200),
        ("WITHIN_6_MONTHS", 200),
        ("FUTURE_PLANNING", 200),
    ],
)
def test_quote_request_project_timeline_validation(client: TestClient, valid_quote_request_data: dict, project_timeline: str, expected_status_code: int):
    """Tests validation of project timeline in quote request"""
    data = valid_quote_request_data.copy()
    data["project_timeline"] = project_timeline

    @patch("app.security.captcha.validate_captcha_token")
    def run_test(mock_validate_captcha_token):
        mock_validate_captcha_token.return_value = True

        @patch("app.services.form_processing_service.process_quote_request")
        def run_test2(mock_process_quote_request):
            mock_process_quote_request.return_value = uuid.uuid4()
            response = client.post(QUOTE_REQUEST_ENDPOINT, json=data)
            assert response.status_code == expected_status_code
            response_json = response.json()
            if expected_status_code == 400:
                assert "Invalid value" in response_json["message"]
        run_test2()
    run_test()