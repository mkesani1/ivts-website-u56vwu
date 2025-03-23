import pytest
from unittest.mock import patch, MagicMock, Mock
import uuid

from app.services.crm_service import (
    CRMService, 
    sync_form_submission_to_crm, 
    update_contact_with_file_upload,
    prepare_file_upload_data
)
from app.integrations.hubspot import HubSpotClient, process_form_submission
from app.core.exceptions import IntegrationException
from app.api.v1.models.form_submission import FormSubmission, FormType, FormStatus
from app.api.v1.models.file_upload import FileUpload, UploadStatus


@pytest.fixture
def test_form_submission():
    """Creates a test form submission for testing."""
    form = FormSubmission()
    form.id = uuid.uuid4()
    form.form_type = FormType.DEMO_REQUEST
    form.status = FormStatus.PENDING
    form.set_data({
        "first_name": "Test",
        "last_name": "User",
        "email": "test@example.com",
        "company": "Test Company",
        "message": "This is a test message"
    })
    return form


@pytest.fixture
def test_file_upload():
    """Creates a test file upload for testing."""
    upload = FileUpload()
    upload.id = uuid.uuid4()
    upload.filename = "test_file.csv"
    upload.size = 1024
    upload.mime_type = "text/csv"
    upload.status = UploadStatus.COMPLETED
    upload.storage_path = f"uploads/{upload.id}.csv"
    
    # Create a mock user
    user = Mock()
    user.id = uuid.uuid4()
    user.email = "test@example.com"
    user.name = "Test User"
    user.company = "Test Company"
    
    upload.user = user
    return upload


def test_crm_service_init():
    """Tests the initialization of the CRM service."""
    service = CRMService()
    assert service._logger is not None
    assert service._hubspot_client is None  # Should be initialized on first use


@patch('app.services.crm_service.process_form_submission')
def test_sync_form_submission_success(mock_process_form, test_db, test_form_submission):
    """Tests successful synchronization of a form submission with CRM."""
    # Mock the process_form_submission function
    mock_process_form.return_value = {
        "success": True,
        "contact_id": "123456789",
        "deal_id": "987654321"
    }
    
    # Add form submission to test database
    test_db.add(test_form_submission)
    test_db.commit()
    
    # Call the function under test
    result = sync_form_submission_to_crm(test_form_submission.id)
    
    # Assertions
    mock_process_form.assert_called_once()
    assert result["success"] is True
    assert result["contact_id"] == "123456789"
    assert result["deal_id"] == "987654321"
    assert result["submission_id"] == str(test_form_submission.id)
    
    # Check if form submission was updated in the database
    updated_submission = test_db.query(FormSubmission).filter(FormSubmission.id == test_form_submission.id).first()
    assert updated_submission.status == FormStatus.COMPLETED
    assert updated_submission.crm_id == "123456789"


def test_sync_form_submission_not_found(test_db):
    """Tests handling of non-existent form submission ID."""
    non_existent_id = uuid.uuid4()
    
    # Call the function under test
    result = sync_form_submission_to_crm(non_existent_id)
    
    # Assertions
    assert result["success"] is False
    assert "Form submission not found" in result["error"]


@patch('app.services.crm_service.process_form_submission')
def test_sync_form_submission_integration_error(mock_process_form, test_db, test_form_submission):
    """Tests handling of integration errors during form submission synchronization."""
    # Mock the process_form_submission function to raise an IntegrationException
    mock_process_form.side_effect = IntegrationException("Test integration error")
    
    # Add form submission to test database
    test_db.add(test_form_submission)
    test_db.commit()
    
    # Call the function under test
    result = sync_form_submission_to_crm(test_form_submission.id)
    
    # Assertions
    assert result["success"] is False
    assert "Test integration error" in result["error"]
    
    # Check if form submission status was updated to FAILED
    updated_submission = test_db.query(FormSubmission).filter(FormSubmission.id == test_form_submission.id).first()
    assert updated_submission.status == FormStatus.FAILED


@patch('app.services.crm_service.HubSpotClient')
def test_update_contact_with_file_upload_success(mock_hubspot_client, test_db, test_file_upload):
    """Tests successful update of a CRM contact with file upload information."""
    # Create mock HubSpotClient instance
    mock_client_instance = MagicMock()
    mock_hubspot_client.return_value = mock_client_instance
    
    # Mock client methods
    mock_client_instance.find_contact_by_email.return_value = {"id": "123456789"}
    mock_client_instance.update_contact.return_value = {"id": "123456789"}
    mock_client_instance.log_activity.return_value = {"id": "activity123"}
    
    # Add file upload to test database
    test_db.add(test_file_upload)
    test_db.commit()
    
    # Create mock processing results
    processing_results = {
        "summary": "Test analysis summary",
        "rows_processed": 100,
        "columns_found": ["id", "name", "value"]
    }
    
    # Call the function under test
    result = update_contact_with_file_upload(test_file_upload.id, processing_results)
    
    # Assertions
    mock_client_instance.find_contact_by_email.assert_called_once_with(test_file_upload.user.email)
    mock_client_instance.update_contact.assert_called_once()
    mock_client_instance.log_activity.assert_called_once()
    
    assert result["success"] is True
    assert result["contact_id"] == "123456789"
    assert result["upload_id"] == str(test_file_upload.id)


def test_update_contact_with_file_upload_not_found(test_db):
    """Tests handling of non-existent file upload ID."""
    non_existent_id = uuid.uuid4()
    processing_results = {"summary": "Test analysis"}
    
    # Call the function under test
    result = update_contact_with_file_upload(non_existent_id, processing_results)
    
    # Assertions
    assert result["success"] is False
    assert "File upload not found" in result["error"]


@patch('app.services.crm_service.HubSpotClient')
def test_update_contact_with_file_upload_create_contact(mock_hubspot_client, test_db, test_file_upload):
    """Tests creation of a new contact when the contact doesn't exist in CRM."""
    # Create mock HubSpotClient instance
    mock_client_instance = MagicMock()
    mock_hubspot_client.return_value = mock_client_instance
    
    # Mock client methods - no existing contact found
    mock_client_instance.find_contact_by_email.return_value = None
    mock_client_instance.create_contact.return_value = {"id": "new_contact_123"}
    mock_client_instance.log_activity.return_value = {"id": "activity123"}
    
    # Add file upload to test database
    test_db.add(test_file_upload)
    test_db.commit()
    
    # Create mock processing results
    processing_results = {
        "summary": "Test analysis summary",
        "rows_processed": 100,
        "columns_found": ["id", "name", "value"]
    }
    
    # Call the function under test
    result = update_contact_with_file_upload(test_file_upload.id, processing_results)
    
    # Assertions
    mock_client_instance.find_contact_by_email.assert_called_once_with(test_file_upload.user.email)
    mock_client_instance.create_contact.assert_called_once()
    mock_client_instance.log_activity.assert_called_once()
    
    assert result["success"] is True
    assert result["contact_id"] == "new_contact_123"
    assert result["upload_id"] == str(test_file_upload.id)


@patch('app.services.crm_service.HubSpotClient')
def test_update_contact_with_file_upload_integration_error(mock_hubspot_client, test_db, test_file_upload):
    """Tests handling of integration errors during contact update with file upload."""
    # Create mock HubSpotClient instance
    mock_client_instance = MagicMock()
    mock_hubspot_client.return_value = mock_client_instance
    
    # Mock client methods to raise an exception
    mock_client_instance.find_contact_by_email.side_effect = IntegrationException("Test integration error")
    
    # Add file upload to test database
    test_db.add(test_file_upload)
    test_db.commit()
    
    # Create mock processing results
    processing_results = {
        "summary": "Test analysis summary"
    }
    
    # Call the function under test
    result = update_contact_with_file_upload(test_file_upload.id, processing_results)
    
    # Assertions
    assert result["success"] is False
    assert "Test integration error" in result["error"]


@patch('app.services.crm_service.HubSpotClient')
def test_crm_service_get_contact(mock_hubspot_client):
    """Tests retrieving a contact from the CRM system."""
    # Create mock HubSpotClient instance
    mock_client_instance = MagicMock()
    mock_hubspot_client.return_value = mock_client_instance
    
    # Mock the get_contact method
    mock_client_instance.get_contact.return_value = {"id": "123456789", "properties": {"email": "test@example.com"}}
    
    # Create CRM service and call the method
    service = CRMService()
    contact = service.get_contact("123456789")
    
    # Assertions
    mock_client_instance.get_contact.assert_called_once_with("123456789")
    assert contact["id"] == "123456789"
    assert contact["properties"]["email"] == "test@example.com"


@patch('app.services.crm_service.HubSpotClient')
def test_crm_service_get_deal(mock_hubspot_client):
    """Tests retrieving a deal from the CRM system."""
    # Create mock HubSpotClient instance
    mock_client_instance = MagicMock()
    mock_hubspot_client.return_value = mock_client_instance
    
    # Mock the get_deal method
    mock_client_instance.get_deal.return_value = {"id": "987654321", "properties": {"dealname": "Test Deal"}}
    
    # Create CRM service and call the method
    service = CRMService()
    deal = service.get_deal("987654321")
    
    # Assertions
    mock_client_instance.get_deal.assert_called_once_with("987654321")
    assert deal["id"] == "987654321"
    assert deal["properties"]["dealname"] == "Test Deal"


@patch('app.services.crm_service.HubSpotClient')
def test_crm_service_log_activity(mock_hubspot_client):
    """Tests logging an activity on a contact in the CRM system."""
    # Create mock HubSpotClient instance
    mock_client_instance = MagicMock()
    mock_hubspot_client.return_value = mock_client_instance
    
    # Mock the log_activity method
    mock_client_instance.log_activity.return_value = {"id": "activity123"}
    
    # Create activity data
    activity_data = {
        "message": "Test activity",
        "details": "This is a test activity"
    }
    
    # Create CRM service and call the method
    service = CRMService()
    result = service.log_activity("123456789", "note", activity_data)
    
    # Assertions
    mock_client_instance.log_activity.assert_called_once_with("123456789", "note", activity_data)
    assert result["id"] == "activity123"


@patch('app.services.crm_service.HubSpotClient')
def test_crm_service_find_contact_by_email(mock_hubspot_client):
    """Tests finding a contact by email in the CRM system."""
    # Create mock HubSpotClient instance
    mock_client_instance = MagicMock()
    mock_hubspot_client.return_value = mock_client_instance
    
    # Mock the find_contact_by_email method
    mock_client_instance.find_contact_by_email.return_value = {"id": "123456789", "properties": {"email": "test@example.com"}}
    
    # Create CRM service and call the method
    service = CRMService()
    contact = service.find_contact_by_email("test@example.com")
    
    # Assertions
    mock_client_instance.find_contact_by_email.assert_called_once_with("test@example.com")
    assert contact["id"] == "123456789"
    assert contact["properties"]["email"] == "test@example.com"


@patch('app.services.crm_service.HubSpotClient')
def test_crm_service_create_contact(mock_hubspot_client):
    """Tests creating a new contact in the CRM system."""
    # Create mock HubSpotClient instance
    mock_client_instance = MagicMock()
    mock_hubspot_client.return_value = mock_client_instance
    
    # Mock the create_contact method
    mock_client_instance.create_contact.return_value = {"id": "new_contact_123"}
    
    # Create contact data
    contact_data = {
        "firstname": "Test",
        "lastname": "User",
        "email": "test@example.com",
        "company": "Test Company"
    }
    
    # Create CRM service and call the method
    service = CRMService()
    result = service.create_contact(contact_data)
    
    # Assertions
    mock_client_instance.create_contact.assert_called_once_with(contact_data)
    assert result["id"] == "new_contact_123"


@patch('app.services.crm_service.HubSpotClient')
def test_crm_service_update_contact(mock_hubspot_client):
    """Tests updating an existing contact in the CRM system."""
    # Create mock HubSpotClient instance
    mock_client_instance = MagicMock()
    mock_hubspot_client.return_value = mock_client_instance
    
    # Mock the update_contact method
    mock_client_instance.update_contact.return_value = {"id": "123456789"}
    
    # Create contact data
    contact_data = {
        "firstname": "Updated",
        "lastname": "User",
        "company": "Updated Company"
    }
    
    # Create CRM service and call the method
    service = CRMService()
    result = service.update_contact("123456789", contact_data)
    
    # Assertions
    mock_client_instance.update_contact.assert_called_once_with("123456789", contact_data)
    assert result["id"] == "123456789"


@patch('app.services.crm_service.HubSpotClient')
def test_crm_service_create_deal(mock_hubspot_client):
    """Tests creating a new deal in the CRM system."""
    # Create mock HubSpotClient instance
    mock_client_instance = MagicMock()
    mock_hubspot_client.return_value = mock_client_instance
    
    # Mock the create_deal method
    mock_client_instance.create_deal.return_value = {"id": "new_deal_123"}
    
    # Create deal data
    deal_data = {
        "dealname": "Test Deal",
        "amount": "1000",
        "pipeline": "default"
    }
    
    # Create CRM service and call the method
    service = CRMService()
    result = service.create_deal("123456789", deal_data, FormType.QUOTE_REQUEST)
    
    # Assertions
    mock_client_instance.create_deal.assert_called_once_with("123456789", deal_data, FormType.QUOTE_REQUEST)
    assert result["id"] == "new_deal_123"


def test_prepare_file_upload_data(test_file_upload):
    """Tests preparation of file upload data for CRM integration."""
    # Create mock processing results
    processing_results = {
        "summary": "Test analysis summary",
        "rows_processed": 100,
        "columns_found": ["id", "name", "value"]
    }
    
    # Call the function
    result = prepare_file_upload_data(test_file_upload, processing_results)
    
    # Assertions
    assert result["sample_file_name"] == test_file_upload.filename
    assert "sample_file_size" in result
    assert result["sample_file_type"] == test_file_upload.mime_type
    assert result["sample_analysis_summary"] == "Test analysis summary"
    assert "sample_upload_date" in result
    assert "lead_source" in result and result["lead_source"] == "Website File Upload"