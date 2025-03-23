"""
Tests for the HubSpot CRM integration.

This module contains tests for the HubSpotClient class and process_form_submission function,
including tests for contact operations, deal creation, activity logging, and error handling.
"""

import pytest
import requests
import json
from unittest.mock import patch, MagicMock

from app.integrations.hubspot import HubSpotClient, process_form_submission, HUBSPOT_API_BASE_URL
from app.core.exceptions import IntegrationException
from app.api.v1.models.form_submission import FormType

# Mock constants
MOCK_API_KEY = "test-api-key"
MOCK_CONTACT_ID = "1234-5678-9012"
MOCK_DEAL_ID = "5678-9012-3456"
MOCK_ACTIVITY_ID = "9012-3456-7890"


def test_hubspot_client_initialization():
    """Tests that the HubSpotClient initializes correctly with API key"""
    client = HubSpotClient(MOCK_API_KEY)
    assert client.api_key == MOCK_API_KEY
    assert client.base_url == HUBSPOT_API_BASE_URL
    assert client.headers["Authorization"] == f"Bearer {MOCK_API_KEY}"
    assert client.headers["Content-Type"] == "application/json"


def test_hubspot_client_initialization_without_api_key():
    """Tests that HubSpotClient raises an exception when initialized without API key"""
    with pytest.raises(IntegrationException) as excinfo:
        HubSpotClient(None)
    assert "API key not configured" in str(excinfo.value)


@patch("app.integrations.hubspot.HubSpotClient._make_request")
def test_find_contact_by_email_found(mock_make_request):
    """Tests that find_contact_by_email returns contact when found"""
    # Create a mock response with a contact
    mock_response = {
        "results": [{
            "id": MOCK_CONTACT_ID,
            "properties": {
                "email": "test@example.com",
                "firstname": "Test",
                "lastname": "User"
            }
        }]
    }
    mock_make_request.return_value = mock_response
    
    # Initialize client and call find_contact_by_email
    client = HubSpotClient(MOCK_API_KEY)
    contact = client.find_contact_by_email("test@example.com")
    
    # Verify the request was made correctly
    mock_make_request.assert_called_once_with(
        method="POST",
        endpoint="/crm/v3/objects/contacts/search",
        data={
            "filterGroups": [{
                "filters": [{
                    "propertyName": "email",
                    "operator": "EQ",
                    "value": "test@example.com"
                }]
            }]
        }
    )
    
    # Verify the response was processed correctly
    assert contact["id"] == MOCK_CONTACT_ID
    assert contact["properties"]["email"] == "test@example.com"


@patch("app.integrations.hubspot.HubSpotClient._make_request")
def test_find_contact_by_email_not_found(mock_make_request):
    """Tests that find_contact_by_email returns None when contact not found"""
    # Create a mock response with no contacts
    mock_response = {"results": []}
    mock_make_request.return_value = mock_response
    
    # Initialize client and call find_contact_by_email
    client = HubSpotClient(MOCK_API_KEY)
    contact = client.find_contact_by_email("test@example.com")
    
    # Verify the request was made correctly
    mock_make_request.assert_called_once_with(
        method="POST",
        endpoint="/crm/v3/objects/contacts/search",
        data={
            "filterGroups": [{
                "filters": [{
                    "propertyName": "email",
                    "operator": "EQ",
                    "value": "test@example.com"
                }]
            }]
        }
    )
    
    # Verify the response was processed correctly
    assert contact is None


@patch("app.integrations.hubspot.HubSpotClient._make_request")
def test_create_contact(mock_make_request):
    """Tests that create_contact correctly creates a contact in HubSpot"""
    # Create a mock response
    mock_response = {
        "id": MOCK_CONTACT_ID,
        "properties": {
            "email": "test@example.com",
            "firstname": "Test",
            "lastname": "User"
        }
    }
    mock_make_request.return_value = mock_response
    
    # Initialize client and call create_contact
    client = HubSpotClient(MOCK_API_KEY)
    contact_data = {
        "email": "test@example.com",
        "firstname": "Test",
        "lastname": "User"
    }
    contact = client.create_contact(contact_data)
    
    # Verify the request was made correctly
    mock_make_request.assert_called_once()
    call_args = mock_make_request.call_args[1]
    assert call_args["method"] == "POST"
    assert call_args["endpoint"] == "/crm/v3/objects/contacts"
    
    # Verify the response was processed correctly
    assert contact["id"] == MOCK_CONTACT_ID
    assert contact["properties"]["email"] == "test@example.com"
    assert contact["properties"]["firstname"] == "Test"
    assert contact["properties"]["lastname"] == "User"


@patch("app.integrations.hubspot.HubSpotClient._make_request")
def test_update_contact(mock_make_request):
    """Tests that update_contact correctly updates a contact in HubSpot"""
    # Create a mock response
    mock_response = {
        "id": MOCK_CONTACT_ID,
        "properties": {
            "email": "test@example.com",
            "firstname": "Updated",
            "lastname": "User"
        }
    }
    mock_make_request.return_value = mock_response
    
    # Initialize client and call update_contact
    client = HubSpotClient(MOCK_API_KEY)
    contact_data = {
        "firstname": "Updated"
    }
    contact = client.update_contact(MOCK_CONTACT_ID, contact_data)
    
    # Verify the request was made correctly
    mock_make_request.assert_called_once()
    call_args = mock_make_request.call_args[1]
    assert call_args["method"] == "PATCH"
    assert call_args["endpoint"] == f"/crm/v3/objects/contacts/{MOCK_CONTACT_ID}"
    
    # Verify the response was processed correctly
    assert contact["id"] == MOCK_CONTACT_ID
    assert contact["properties"]["firstname"] == "Updated"


@patch("app.integrations.hubspot.HubSpotClient._make_request")
def test_create_deal(mock_make_request):
    """Tests that create_deal correctly creates a deal in HubSpot"""
    # Create a mock response
    mock_response = {
        "id": MOCK_DEAL_ID,
        "properties": {
            "dealname": "Company Name - Demo Request",
            "dealstage": "presentationscheduled"
        }
    }
    mock_make_request.return_value = mock_response
    
    # Initialize client and call create_deal
    client = HubSpotClient(MOCK_API_KEY)
    # Mock the associate_deal_with_contact method
    client.associate_deal_with_contact = MagicMock(return_value=True)
    
    deal_data = {
        "company": "Company Name",
        "service_interest": "AI Model Development"
    }
    deal = client.create_deal(MOCK_CONTACT_ID, deal_data, FormType.DEMO_REQUEST)
    
    # Verify the request was made correctly
    mock_make_request.assert_called_once()
    call_args = mock_make_request.call_args[1]
    assert call_args["method"] == "POST"
    assert call_args["endpoint"] == "/crm/v3/objects/deals"
    
    # Verify associate_deal_with_contact was called
    client.associate_deal_with_contact.assert_called_once_with(MOCK_DEAL_ID, MOCK_CONTACT_ID)
    
    # Verify the response was processed correctly
    assert deal["id"] == MOCK_DEAL_ID
    assert deal["properties"]["dealname"] == "Company Name - Demo Request"
    assert deal["properties"]["dealstage"] == "presentationscheduled"


@patch("app.integrations.hubspot.HubSpotClient._make_request")
def test_associate_deal_with_contact(mock_make_request):
    """Tests that associate_deal_with_contact correctly associates a deal with a contact"""
    # Create a mock response
    mock_response = {}  # Successful association returns empty response
    mock_make_request.return_value = mock_response
    
    # Initialize client and call associate_deal_with_contact
    client = HubSpotClient(MOCK_API_KEY)
    result = client.associate_deal_with_contact(MOCK_DEAL_ID, MOCK_CONTACT_ID)
    
    # Verify the request was made correctly
    mock_make_request.assert_called_once_with(
        method="PUT",
        endpoint=f"/crm/v3/objects/deals/{MOCK_DEAL_ID}/associations/contacts/{MOCK_CONTACT_ID}/deal_to_contact"
    )
    
    # Verify the result
    assert result is True


@patch("app.integrations.hubspot.HubSpotClient._make_request")
def test_log_activity(mock_make_request):
    """Tests that log_activity correctly logs an activity in HubSpot"""
    # Create a mock response
    mock_response = {
        "id": MOCK_ACTIVITY_ID,
        "engagement": {
            "type": "note"
        },
        "associations": {
            "contactIds": [MOCK_CONTACT_ID]
        },
        "metadata": {
            "hs_note_body": "Test activity"
        }
    }
    mock_make_request.return_value = mock_response
    
    # Initialize client and call log_activity
    client = HubSpotClient(MOCK_API_KEY)
    activity_data = {
        "message": "Test activity"
    }
    activity = client.log_activity(MOCK_CONTACT_ID, "note", activity_data)
    
    # Verify the request was made correctly
    mock_make_request.assert_called_once()
    call_args = mock_make_request.call_args[1]
    assert call_args["method"] == "POST"
    assert call_args["endpoint"] == "/engagements/v1/engagements"
    
    # Verify the response was processed correctly
    assert activity["id"] == MOCK_ACTIVITY_ID
    assert activity["engagement"]["type"] == "note"
    assert MOCK_CONTACT_ID in activity["associations"]["contactIds"]


@patch("app.integrations.hubspot.HubSpotClient._make_request")
def test_get_contact(mock_make_request):
    """Tests that get_contact correctly retrieves a contact from HubSpot"""
    # Create a mock response
    mock_response = {
        "id": MOCK_CONTACT_ID,
        "properties": {
            "email": "test@example.com",
            "firstname": "Test",
            "lastname": "User"
        }
    }
    mock_make_request.return_value = mock_response
    
    # Initialize client and call get_contact
    client = HubSpotClient(MOCK_API_KEY)
    contact = client.get_contact(MOCK_CONTACT_ID)
    
    # Verify the request was made correctly
    mock_make_request.assert_called_once_with(
        method="GET",
        endpoint=f"/crm/v3/objects/contacts/{MOCK_CONTACT_ID}"
    )
    
    # Verify the response was processed correctly
    assert contact["id"] == MOCK_CONTACT_ID
    assert contact["properties"]["email"] == "test@example.com"
    assert contact["properties"]["firstname"] == "Test"
    assert contact["properties"]["lastname"] == "User"


@patch("app.integrations.hubspot.HubSpotClient._make_request")
def test_get_deal(mock_make_request):
    """Tests that get_deal correctly retrieves a deal from HubSpot"""
    # Create a mock response
    mock_response = {
        "id": MOCK_DEAL_ID,
        "properties": {
            "dealname": "Company Name - Demo Request",
            "dealstage": "presentationscheduled"
        }
    }
    mock_make_request.return_value = mock_response
    
    # Initialize client and call get_deal
    client = HubSpotClient(MOCK_API_KEY)
    deal = client.get_deal(MOCK_DEAL_ID)
    
    # Verify the request was made correctly
    mock_make_request.assert_called_once_with(
        method="GET",
        endpoint=f"/crm/v3/objects/deals/{MOCK_DEAL_ID}"
    )
    
    # Verify the response was processed correctly
    assert deal["id"] == MOCK_DEAL_ID
    assert deal["properties"]["dealname"] == "Company Name - Demo Request"
    assert deal["properties"]["dealstage"] == "presentationscheduled"


@patch("time.sleep")
def test_handle_rate_limit(mock_sleep):
    """Tests that handle_rate_limit correctly handles rate limiting"""
    client = HubSpotClient(MOCK_API_KEY)
    client.handle_rate_limit(5)
    mock_sleep.assert_called_once_with(5)


@patch("requests.request")
def test_make_request_success(mock_request):
    """Tests that _make_request correctly handles successful API responses"""
    # Create a mock response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"id": "test-id", "properties": {"name": "Test"}}
    mock_request.return_value = mock_response
    
    # Initialize client and call _make_request
    client = HubSpotClient(MOCK_API_KEY)
    result = client._make_request("GET", "/test", {}, {})
    
    # Verify the request was made correctly
    mock_request.assert_called_once_with(
        method="GET",
        url=f"{HUBSPOT_API_BASE_URL}/test",
        headers=client.headers,
        params={},
        json={}
    )
    
    # Verify the response was processed correctly
    assert result["id"] == "test-id"
    assert result["properties"]["name"] == "Test"


@patch("requests.request")
@patch("app.integrations.hubspot.HubSpotClient.handle_rate_limit")
def test_make_request_rate_limit(mock_handle_rate_limit, mock_request):
    """Tests that _make_request correctly handles rate limiting responses"""
    # Create rate limit response
    rate_limit_response = MagicMock()
    rate_limit_response.status_code = 429
    rate_limit_response.headers = {"Retry-After": "5"}
    
    # Create success response for second call
    success_response = MagicMock()
    success_response.status_code = 200
    success_response.json.return_value = {"id": "test-id", "properties": {"name": "Test"}}
    
    # Setup mock to return rate limit response first, then success response
    mock_request.side_effect = [rate_limit_response, success_response]
    
    # Initialize client and call _make_request
    client = HubSpotClient(MOCK_API_KEY)
    result = client._make_request("GET", "/test", {}, {})
    
    # Verify handle_rate_limit was called with retry-after value
    mock_handle_rate_limit.assert_called_once_with(5)
    
    # Verify the request was made twice
    assert mock_request.call_count == 2
    
    # Verify the response was processed correctly
    assert result["id"] == "test-id"
    assert result["properties"]["name"] == "Test"


@patch("requests.request")
def test_make_request_error(mock_request):
    """Tests that _make_request correctly handles error responses"""
    # Create error response
    error_response = MagicMock()
    error_response.status_code = 400
    error_response.json.return_value = {"message": "Invalid request"}
    mock_request.return_value = error_response
    
    # Initialize client and call _make_request
    client = HubSpotClient(MOCK_API_KEY)
    
    # Verify the error is raised
    with pytest.raises(IntegrationException) as excinfo:
        client._make_request("GET", "/test", {}, {})
    
    # Verify the error message
    assert "Invalid request to HubSpot API" in str(excinfo.value)
    
    # Verify the request was made correctly
    mock_request.assert_called_once_with(
        method="GET",
        url=f"{HUBSPOT_API_BASE_URL}/test",
        headers=client.headers,
        params={},
        json={}
    )


@patch("app.integrations.hubspot.HubSpotClient")
def test_process_form_submission_new_contact(mock_hubspot_client):
    """Tests that process_form_submission correctly processes a form submission for a new contact"""
    # Create mock HubSpotClient instance
    mock_client = MagicMock()
    mock_hubspot_client.return_value = mock_client
    
    # Configure mock methods
    mock_client.find_contact_by_email.return_value = None  # No existing contact
    mock_client.create_contact.return_value = {"id": MOCK_CONTACT_ID}
    mock_client.create_deal.return_value = {"id": MOCK_DEAL_ID}
    mock_client.log_activity.return_value = {"id": MOCK_ACTIVITY_ID}
    
    # Create form data
    form_data = {
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User",
        "company": "Test Company",
        "message": "Test message"
    }
    
    # Call process_form_submission
    result = process_form_submission(form_data, FormType.DEMO_REQUEST)
    
    # Verify the client was called correctly
    mock_client.find_contact_by_email.assert_called_once_with("test@example.com")
    mock_client.create_contact.assert_called_once()
    mock_client.create_deal.assert_called_once_with(MOCK_CONTACT_ID, mock_client.create_contact.return_value, FormType.DEMO_REQUEST)
    mock_client.log_activity.assert_called_once_with(MOCK_CONTACT_ID, "note", {"message": "Form submission of type DEMO_REQUEST", "form_data": form_data})
    
    # Verify the result
    assert result["success"] is True
    assert result["contact_id"] == MOCK_CONTACT_ID
    assert result["deal_id"] == MOCK_DEAL_ID
    assert result["form_type"] == "DEMO_REQUEST"


@patch("app.integrations.hubspot.HubSpotClient")
def test_process_form_submission_existing_contact(mock_hubspot_client):
    """Tests that process_form_submission correctly processes a form submission for an existing contact"""
    # Create mock HubSpotClient instance
    mock_client = MagicMock()
    mock_hubspot_client.return_value = mock_client
    
    # Configure mock methods
    mock_client.find_contact_by_email.return_value = {"id": MOCK_CONTACT_ID}  # Existing contact
    mock_client.update_contact.return_value = {"id": MOCK_CONTACT_ID, "properties": {"email": "test@example.com"}}
    mock_client.create_deal.return_value = {"id": MOCK_DEAL_ID}
    mock_client.log_activity.return_value = {"id": MOCK_ACTIVITY_ID}
    
    # Create form data
    form_data = {
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User",
        "company": "Test Company",
        "message": "Test message"
    }
    
    # Call process_form_submission
    result = process_form_submission(form_data, FormType.QUOTE_REQUEST)
    
    # Verify the client was called correctly
    mock_client.find_contact_by_email.assert_called_once_with("test@example.com")
    
    # Check that update_contact was called with the contact ID
    update_call_args = mock_client.update_contact.call_args[0]
    assert update_call_args[0] == MOCK_CONTACT_ID  # First arg should be contact_id
    
    # Check that create_deal was called with the contact ID and form type
    deal_call_args = mock_client.create_deal.call_args[0]
    assert deal_call_args[0] == MOCK_CONTACT_ID  # First arg should be contact_id
    assert deal_call_args[2] == FormType.QUOTE_REQUEST  # Third arg should be form_type
    
    # Verify the result
    assert result["success"] is True
    assert result["contact_id"] == MOCK_CONTACT_ID
    assert result["deal_id"] == MOCK_DEAL_ID
    assert result["form_type"] == "QUOTE_REQUEST"


@patch("app.integrations.hubspot.HubSpotClient")
def test_process_form_submission_error_handling(mock_hubspot_client):
    """Tests that process_form_submission correctly handles errors during processing"""
    # Create mock HubSpotClient instance
    mock_client = MagicMock()
    mock_hubspot_client.return_value = mock_client
    
    # Configure mock methods to raise an exception
    mock_client.find_contact_by_email.side_effect = IntegrationException("Test error")
    
    # Create form data
    form_data = {
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User"
    }
    
    # Verify the error is raised
    with pytest.raises(IntegrationException) as excinfo:
        process_form_submission(form_data, FormType.CONTACT)
    
    # Verify the error message
    assert "Test error" in str(excinfo.value)
    
    # Verify the client was called correctly
    mock_client.find_contact_by_email.assert_called_once_with("test@example.com")