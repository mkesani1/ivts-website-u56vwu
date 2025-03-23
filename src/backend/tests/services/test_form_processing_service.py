# Standard library imports
import uuid
from unittest.mock import MagicMock

# Third-party imports
import pytest  # pytest version: ^7.3.1

# Local application imports
from app.api.v1.models.form_submission import FormSubmission, FormType, FormStatus
from app.core.exceptions import ValidationException, ProcessingException
from app.services.form_processing_service import FormProcessingService  # FormProcessingService class
# Import the functions to be tested
from app.services.form_processing_service import process_contact_form  # process_contact_form function
from app.services.form_processing_service import process_demo_request  # process_demo_request function
from app.services.form_processing_service import process_quote_request  # process_quote_request function

@pytest.fixture
def setup_form_processing_service():
    """
    Pytest fixture that sets up a FormProcessingService instance with mocked dependencies.
    """
    # Create mock instances for SecurityService, CRMService, EmailService, and AnalyticsService
    mock_security_service = MagicMock()
    mock_crm_service = MagicMock()
    mock_email_service = MagicMock()
    mock_analytics_service = MagicMock()

    # Create a FormProcessingService instance
    form_service = FormProcessingService()

    # Replace the service's dependencies with the mocks
    form_service._security_service = mock_security_service
    form_service._crm_service = mock_crm_service
    form_service._email_service = mock_email_service
    form_service._analytics_service = mock_analytics_service

    # Return the service instance with mocked dependencies
    return form_service

@pytest.fixture
def mock_db_session():
    """
    Pytest fixture that creates a mock database session.
    """
    # Create a MagicMock instance for the database session
    mock_session = MagicMock()

    # Configure the mock to return appropriate values for common methods
    mock_session.add.return_value = None
    mock_session.commit.return_value = None
    mock_session.refresh.return_value = None

    # Return the mock session
    return mock_session

def test_process_contact_form_success(setup_form_processing_service, mock_db_session):
    """
    Tests successful processing of a contact form submission.
    """
    # Arrange
    form_service = setup_form_processing_service
    test_data = {"name": "John Doe", "email": "john.doe@example.com", "message": "Hello"}
    submission_id = uuid.uuid4()

    # Mock the SecurityService to validate the form data successfully
    form_service._security_service.validate_form.return_value = (True, {})

    # Mock the database session to return a new FormSubmission instance
    form_service._db_session = mock_db_session
    form_service._db_session.add.return_value = None
    form_service._db_session.commit.return_value = None

    # Mock the EmailService to send confirmation email successfully
    form_service._email_service.send_contact_confirmation.return_value = {"status": "success"}

    # Mock the CRMService to sync with CRM successfully
    form_service._crm_service.sync_form_submission.return_value = {"success": True, "submission_id": submission_id}

    # Mock the AnalyticsService to track the form submission successfully
    form_service._analytics_service.track_form_submission.return_value = True

    # Act
    result = form_service.process_contact_form(test_data)

    # Assert
    assert result["success"] is True
    assert result["submission_id"] == submission_id

    # Verify that all expected methods were called with correct parameters
    form_service._security_service.validate_form.assert_called_once_with(test_data, "contact")
    form_service._email_service.send_contact_confirmation.assert_called_once()
    form_service._crm_service.sync_form_submission.assert_called_once_with(submission_id)
    form_service._analytics_service.track_form_submission.assert_called_once_with("contact", True, test_data)

def test_process_contact_form_validation_error(setup_form_processing_service):
    """
    Tests handling of validation errors during contact form processing.
    """
    # Arrange
    form_service = setup_form_processing_service
    test_data = {"name": "", "email": "invalid-email", "message": ""}

    # Mock the SecurityService to raise ValidationException
    form_service._security_service.validate_form.return_value = (False, {"name": "Name is required"})

    # Act
    result = form_service.process_contact_form(test_data)

    # Assert
    assert result["success"] is False
    assert "Name is required" in result["message"]

    # Verify that no database, email, or CRM operations were performed
    form_service._email_service.send_contact_confirmation.assert_not_called()
    form_service._crm_service.sync_form_submission.assert_not_called()
    form_service._analytics_service.track_form_submission.assert_not_called()

def test_process_demo_request_success(setup_form_processing_service, mock_db_session):
    """
    Tests successful processing of a demo request form submission.
    """
    # Arrange
    form_service = setup_form_processing_service
    test_data = {"first_name": "John", "last_name": "Doe", "email": "john.doe@example.com", "company": "Example"}
    submission_id = uuid.uuid4()

    # Mock the SecurityService to validate the form data successfully
    form_service._security_service.validate_form.return_value = (True, {})

    # Mock the database session to return a new FormSubmission instance
    form_service._db_session = mock_db_session
    form_service._db_session.add.return_value = None
    form_service._db_session.commit.return_value = None

    # Mock the EmailService to send demo request confirmation email successfully
    form_service._email_service.send_demo_request_confirmation.return_value = {"status": "success"}

    # Mock the CRMService to sync with CRM successfully
    form_service._crm_service.sync_form_submission.return_value = {"success": True, "submission_id": submission_id}

    # Mock the AnalyticsService to track the demo request successfully
    form_service._analytics_service.track_form_submission.return_value = True

    # Act
    result = form_service.process_demo_request(test_data)

    # Assert
    assert result["success"] is True
    assert result["submission_id"] == submission_id

    # Verify that all expected methods were called with correct parameters
    form_service._security_service.validate_form.assert_called_once_with(test_data, "demo_request")
    form_service._email_service.send_demo_request_confirmation.assert_called_once()
    form_service._crm_service.sync_form_submission.assert_called_once_with(submission_id)
    form_service._analytics_service.track_form_submission.assert_called_once_with("demo_request", True, test_data)

def test_process_demo_request_db_error(setup_form_processing_service, mock_db_session):
    """
    Tests handling of database errors during demo request processing.
    """
    # Arrange
    form_service = setup_form_processing_service
    test_data = {"first_name": "John", "last_name": "Doe", "email": "john.doe@example.com", "company": "Example"}

    # Mock the SecurityService to validate the form data successfully
    form_service._security_service.validate_form.return_value = (True, {})

    # Mock the database session to raise an exception during commit
    form_service._db_session = mock_db_session
    form_service._db_session.commit.side_effect = Exception("Database error")

    # Act
    result = form_service.process_demo_request(test_data)

    # Assert
    assert result["success"] is False
    assert "Database error" in result["message"]

    # Verify that no email or CRM operations were performed
    form_service._email_service.send_demo_request_confirmation.assert_not_called()
    form_service._crm_service.sync_form_submission.assert_not_called()
    form_service._analytics_service.track_form_submission.assert_not_called()

def test_process_quote_request_success(setup_form_processing_service, mock_db_session):
    """
    Tests successful processing of a quote request form submission.
    """
    # Arrange
    form_service = setup_form_processing_service
    test_data = {"first_name": "John", "last_name": "Doe", "email": "john.doe@example.com", "company": "Example"}
    submission_id = uuid.uuid4()

    # Mock the SecurityService to validate the form data successfully
    form_service._security_service.validate_form.return_value = (True, {})

    # Mock the database session to return a new FormSubmission instance
    form_service._db_session = mock_db_session
    form_service._db_session.add.return_value = None
    form_service._db_session.commit.return_value = None

    # Mock the EmailService to send quote request confirmation email successfully
    form_service._email_service.send_quote_request_confirmation.return_value = {"status": "success"}

    # Mock the CRMService to sync with CRM successfully
    form_service._crm_service.sync_form_submission.return_value = {"success": True, "submission_id": submission_id}

    # Mock the AnalyticsService to track the quote request successfully
    form_service._analytics_service.track_form_submission.return_value = True

    # Act
    result = form_service.process_quote_request(test_data)

    # Assert
    assert result["success"] is True
    assert result["submission_id"] == submission_id

    # Verify that all expected methods were called with correct parameters
    form_service._security_service.validate_form.assert_called_once_with(test_data, "quote_request")
    form_service._email_service.send_quote_request_confirmation.assert_called_once()
    form_service._crm_service.sync_form_submission.assert_called_once_with(submission_id)
    form_service._analytics_service.track_form_submission.assert_called_once_with("quote_request", True, test_data)

def test_process_quote_request_email_error(setup_form_processing_service, mock_db_session):
    """
    Tests handling of email errors during quote request processing.
    """
    # Arrange
    form_service = setup_form_processing_service
    test_data = {"first_name": "John", "last_name": "Doe", "email": "john.doe@example.com", "company": "Example"}
    submission_id = uuid.uuid4()

    # Mock the SecurityService to validate the form data successfully
    form_service._security_service.validate_form.return_value = (True, {})

    # Mock the database session to return a new FormSubmission instance
    form_service._db_session = mock_db_session
    form_service._db_session.add.return_value = None
    form_service._db_session.commit.return_value = None

    # Mock the EmailService to raise an exception during email sending
    form_service._email_service.send_quote_request_confirmation.side_effect = Exception("Email error")

    # Act
    result = form_service.process_quote_request(test_data)

    # Assert
    assert result["success"] is False
    assert "Email error" in result["message"]

    # Verify that the form submission was still created and saved to the database
    form_service._security_service.validate_form.assert_called_once_with(test_data, "quote_request")
    form_service._email_service.send_quote_request_confirmation.assert_called_once()
    form_service._crm_service.sync_form_submission.assert_not_called()
    form_service._analytics_service.track_form_submission.assert_not_called()

def test_process_quote_request_crm_error(setup_form_processing_service, mock_db_session):
    """
    Tests handling of CRM errors during quote request processing.
    """
    # Arrange
    form_service = setup_form_processing_service
    test_data = {"first_name": "John", "last_name": "Doe", "email": "john.doe@example.com", "company": "Example"}
    submission_id = uuid.uuid4()

    # Mock the SecurityService to validate the form data successfully
    form_service._security_service.validate_form.return_value = (True, {})

    # Mock the database session to return a new FormSubmission instance
    form_service._db_session = mock_db_session
    form_service._db_session.add.return_value = None
    form_service._db_session.commit.return_value = None

    # Mock the EmailService to send quote request confirmation email successfully
    form_service._email_service.send_quote_request_confirmation.return_value = {"status": "success"}

    # Mock the CRMService to raise an exception during CRM sync
    form_service._crm_service.sync_form_submission.side_effect = Exception("CRM error")

    # Act
    result = form_service.process_quote_request(test_data)

    # Assert
    assert result["success"] is False
    assert "CRM error" in result["message"]

    # Verify that the form submission was still created and saved to the database
    form_service._security_service.validate_form.assert_called_once_with(test_data, "quote_request")
    form_service._email_service.send_quote_request_confirmation.assert_called_once()
    form_service._crm_service.sync_form_submission.assert_called_once()
    form_service._analytics_service.track_form_submission.assert_not_called()

def test_get_form_submission(setup_form_processing_service, mock_db_session):
    """
    Tests retrieving a form submission by ID.
    """
    # Arrange
    form_service = setup_form_processing_service
    submission_id = uuid.uuid4()
    test_submission = FormSubmission(id=submission_id, user_id=uuid.uuid4(), form_type=FormType.CONTACT, data="{}", status=FormStatus.PENDING)

    # Mock the database session to return a form submission with the test ID
    form_service._db_session = mock_db_session
    form_service._db_session.query.return_value.filter.return_value.first.return_value = test_submission

    # Act
    result = form_service.get_form_submission(submission_id)

    # Assert
    assert result["id"] == str(submission_id)

    # Verify that the database query was called with the correct ID
    form_service._db_session.query.return_value.filter.assert_called_with(FormSubmission.id == submission_id)

def test_get_form_submission_not_found(setup_form_processing_service, mock_db_session):
    """
    Tests handling of non-existent form submission ID.
    """
    # Arrange
    form_service = setup_form_processing_service
    submission_id = uuid.uuid4()

    # Mock the database session to return None for the query
    form_service._db_session = mock_db_session
    form_service._db_session.query.return_value.filter.return_value.first.return_value = None

    # Act
    result = form_service.get_form_submission(submission_id)

    # Assert
    assert result is None

    # Verify that the database query was called with the correct ID
    form_service._db_session.query.return_value.filter.assert_called_with(FormSubmission.id == submission_id)

def test_get_form_submissions(setup_form_processing_service, mock_db_session):
    """
    Tests retrieving multiple form submissions with filtering.
    """
    # Arrange
    form_service = setup_form_processing_service
    test_submissions = [
        FormSubmission(id=uuid.uuid4(), user_id=uuid.uuid4(), form_type=FormType.CONTACT, data="{}", status=FormStatus.PENDING),
        FormSubmission(id=uuid.uuid4(), user_id=uuid.uuid4(), form_type=FormType.DEMO_REQUEST, data="{}", status=FormStatus.COMPLETED)
    ]

    # Mock the database session to return a list of form submissions
    form_service._db_session = mock_db_session
    form_service._db_session.query.return_value.filter.return_value.all.return_value = test_submissions

    # Act
    result = form_service.get_form_submissions(form_type=FormType.CONTACT)

    # Assert
    assert len(result) == 2

    # Verify that the database query was called with the correct filters
    form_service._db_session.query.return_value.filter.assert_called()

def test_update_form_submission_status(setup_form_processing_service, mock_db_session):
    """
    Tests updating the status of a form submission.
    """
    # Arrange
    form_service = setup_form_processing_service
    submission_id = uuid.uuid4()
    new_status = FormStatus.PROCESSING
    test_submission = FormSubmission(id=submission_id, user_id=uuid.uuid4(), form_type=FormType.CONTACT, data="{}", status=FormStatus.PENDING)

    # Mock the database session to return a form submission with the test ID
    form_service._db_session = mock_db_session
    form_service._db_session.query.return_value.filter.return_value.first.return_value = test_submission

    # Act
    result = form_service.update_form_submission_status(submission_id, new_status)

    # Assert
    assert result["success"] is True

    # Verify that the form submission's update_status method was called with the new status
    assert test_submission.status == new_status

    # Verify that the database session was committed
    form_service._db_session.commit.assert_called_once()

def test_create_form_submission(setup_form_processing_service, mock_db_session):
    """
    Tests creating a new form submission record.
    """
    # Arrange
    form_service = setup_form_processing_service
    test_data = {"name": "John Doe", "email": "john.doe@example.com", "message": "Hello"}
    form_type = FormType.CONTACT

    # Mock the database session
    form_service._db_session = mock_db_session

    # Act
    result = form_service.create_form_submission(test_data, form_type)

    # Assert
    # Verify that a FormSubmission instance was created with the correct attributes
    form_service._db_session.add.assert_called()
    form_service._db_session.commit.assert_called()