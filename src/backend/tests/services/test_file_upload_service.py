# src/backend/tests/services/test_file_upload_service.py
import unittest.mock
import uuid
from datetime import datetime
import os
import tempfile

import pytest  # pytest v7.3.1
from unittest.mock import patch
from uuid import uuid4

from app.services.file_upload_service import FileUploadService
from app.api.v1.models.file_upload import FileUpload
from app.api.v1.models.file_upload import UploadStatus
from app.integrations.aws_s3 import S3Client
from app.security.file_scanner import FileScanner
from app.security.file_scanner import SCAN_RESULT_CLEAN
from app.security.file_scanner import SCAN_RESULT_INFECTED


class TestFileUploadService:
    """Test class for the FileUploadService"""

    def __init__(self):
        """Sets up the test environment"""
        # Initialize test variables and mocks
        pass

    def setup_method(self, method):
        """Set up method called before each test"""
        # Create a mock database session
        self.mock_session = unittest.mock.MagicMock()
        # Create a FileUploadService instance with the mock session
        self.service = FileUploadService(self.mock_session)
        # Set up common test data and mocks
        self.upload_data = {
            "user_id": uuid4(),
            "filename": "test.csv",
            "size": 1024,
            "mime_type": "text/csv",
        }

    def test_create_upload(self):
        """Tests the create_upload method"""
        # Mock validate_upload_request to return (True, '')
        with patch.object(
            self.service, "validate_upload_request", return_value=(True, "")
        ) as mock_validate, patch(
            "app.services.file_upload_service.create_upload_record"
        ) as mock_create, patch(
            "app.services.file_upload_service.generate_presigned_upload_url"
        ) as mock_generate, patch(
            "app.services.file_upload_service.send_upload_notifications"
        ) as mock_send:
            # Mock create_upload_record to return a mock FileUpload
            mock_file_upload = unittest.mock.MagicMock(spec=FileUpload)
            mock_create.return_value = mock_file_upload
            # Mock generate_presigned_upload_url to return a mock URL response
            mock_generate.return_value = {"url": "mock_url", "fields": {}}
            # Mock send_upload_notifications to return True
            mock_send.return_value = True

            # Call service.create_upload with test data
            result = self.service.create_upload(
                self.upload_data,
                self.upload_data["filename"],
                self.upload_data["mime_type"],
                self.upload_data["size"],
            )

            # Assert that validate_upload_request was called with correct parameters
            mock_validate.assert_called_once_with(
                self.upload_data["filename"],
                self.upload_data["mime_type"],
                self.upload_data["size"],
            )
            # Assert that create_upload_record was called with correct data
            mock_create.assert_called_once_with(self.upload_data, self.mock_session)
            # Assert that generate_presigned_upload_url was called with correct parameters
            mock_generate.assert_called_once_with(
                self.upload_data["filename"],
                self.upload_data["mime_type"],
                mock_file_upload.id,
            )
            # Assert that send_upload_notifications was called with 'confirmation' type
            mock_send.assert_called_once_with(
                upload_id=mock_file_upload.id,
                notification_type="confirmation",
                additional_data={
                    "email": self.upload_data.get("email"),
                    "name": self.upload_data.get("name"),
                },
            )
            # Assert that the method returns a dictionary with upload_id and presigned URL information
            assert result["status"] == "success"
            assert "upload_id" in result
            assert "upload_url" in result

    def test_create_upload_validation_failure(self):
        """Tests the create_upload method with validation failure"""
        # Mock validate_upload_request to return (False, 'Validation error')
        with patch.object(
            self.service,
            "validate_upload_request",
            return_value=(False, "Validation error"),
        ) as mock_validate, patch(
            "app.services.file_upload_service.create_upload_record"
        ) as mock_create, patch(
            "app.services.file_upload_service.generate_presigned_upload_url"
        ) as mock_generate, patch(
            "app.services.file_upload_service.send_upload_notifications"
        ) as mock_send:
            # Call service.create_upload with test data
            result = self.service.create_upload(
                self.upload_data,
                self.upload_data["filename"],
                self.upload_data["mime_type"],
                self.upload_data["size"],
            )

            # Assert that validate_upload_request was called with correct parameters
            mock_validate.assert_called_once_with(
                self.upload_data["filename"],
                self.upload_data["mime_type"],
                self.upload_data["size"],
            )
            # Assert that create_upload_record was not called
            mock_create.assert_not_called()
            # Assert that generate_presigned_upload_url was not called
            mock_generate.assert_not_called()
            # Assert that send_upload_notifications was not called
            mock_send.assert_not_called()
            # Assert that the method returns a dictionary with error status and message
            assert result["status"] == "error"
            assert "message" in result

    def test_complete_upload(self):
        """Tests the complete_upload method"""
        # Mock the complete_upload function to return a success result
        with patch(
            "app.services.file_upload_service.complete_upload", return_value={"status": "success"}
        ) as mock_complete:
            test_upload_id = uuid4()
            test_object_key = "test_object_key"
            # Call service.complete_upload with test upload_id and object_key
            result = self.service.complete_upload(test_upload_id, test_object_key)

            # Assert that complete_upload was called with correct parameters
            mock_complete.assert_called_once_with(
                test_upload_id, test_object_key, self.mock_session
            )
            # Assert that the method returns the expected result
            assert result["status"] == "success"

    def test_get_upload_status(self):
        """Tests the get_upload_status method"""
        # Mock the get_upload_status function to return a status dictionary
        with patch(
            "app.services.file_upload_service.get_upload_status",
            return_value={"status": "success", "upload_status": "UPLOADED"},
        ) as mock_get_status:
            test_upload_id = uuid4()
            # Call service.get_upload_status with test upload_id
            result = self.service.get_upload_status(test_upload_id)

            # Assert that get_upload_status was called with correct parameters
            mock_get_status.assert_called_once_with(test_upload_id, self.mock_session)
            # Assert that the method returns the expected status dictionary
            assert result["status"] == "success"
            assert result["upload_status"] == "UPLOADED"

    def test_delete_upload(self):
        """Tests the delete_upload method"""
        # Mock the delete_upload function to return True
        with patch(
            "app.services.file_upload_service.delete_upload", return_value=True
        ) as mock_delete:
            test_upload_id = uuid4()
            # Call service.delete_upload with test upload_id
            result = self.service.delete_upload(test_upload_id)

            # Assert that delete_upload was called with correct parameters
            mock_delete.assert_called_once_with(test_upload_id, self.mock_session)
            # Assert that the method returns True
            assert result is True

    def test_scan_uploaded_file(self):
        """Tests the scan_uploaded_file method"""
        # Mock the scan_uploaded_file function to return a scan result
        with patch(
            "app.services.file_upload_service.scan_uploaded_file",
            return_value={"status": "clean"},
        ) as mock_scan:
            test_upload_id = uuid4()
            # Call service.scan_uploaded_file with test upload_id
            result = self.service.scan_uploaded_file(test_upload_id)

            # Assert that scan_uploaded_file was called with correct parameters
            mock_scan.assert_called_once_with(test_upload_id, self.mock_session)
            # Assert that the method returns the expected scan result
            assert result["status"] == "clean"

    def test_initiate_file_processing(self):
        """Tests the initiate_file_processing method"""
        # Mock the initiate_file_processing function to return a processing result
        with patch(
            "app.services.file_upload_service.initiate_file_processing",
            return_value={"status": "processing"},
        ) as mock_initiate:
            test_upload_id = uuid4()
            # Call service.initiate_file_processing with test upload_id
            result = self.service.initiate_file_processing(test_upload_id)

            # Assert that initiate_file_processing was called with correct parameters
            mock_initiate.assert_called_once_with(test_upload_id, self.mock_session)
            # Assert that the method returns the expected processing result
            assert result["status"] == "processing"

    def test_send_upload_notifications(self):
        """Tests the send_upload_notifications method"""
        # Mock the send_upload_notifications function to return True
        with patch(
            "app.services.file_upload_service.send_upload_notifications", return_value=True
        ) as mock_send:
            test_upload_id = uuid4()
            test_notification_type = "confirmation"
            test_additional_data = {"email": "test@example.com", "name": "Test User"}
            # Call service.send_upload_notifications with test parameters
            result = self.service.send_upload_notifications(
                test_upload_id, test_notification_type, test_additional_data
            )

            # Assert that send_upload_notifications was called with correct parameters
            mock_send.assert_called_once_with(
                test_upload_id, test_notification_type, test_additional_data, self.mock_session
            )
            # Assert that the method returns True
            assert result is True

    def test_validate_upload_request(self):
        """Tests the validate_upload_request method"""
        # Mock the validate_upload_request function to return a validation result
        with patch(
            "app.services.file_upload_service.validate_upload_request",
            return_value=(True, ""),
        ) as mock_validate:
            test_filename = "test.csv"
            test_content_type = "text/csv"
            test_size = 1024
            # Call service.validate_upload_request with test parameters
            result, _ = self.service.validate_upload_request(
                test_filename, test_content_type, test_size
            )

            # Assert that validate_upload_request was called with correct parameters
            mock_validate.assert_called_once_with(test_filename, test_content_type, test_size)
            # Assert that the method returns the expected validation result
            assert result is True

    def test_get_allowed_file_types(self):
        """Tests the get_allowed_file_types method"""
        # Call service.get_allowed_file_types
        result = self.service.get_allowed_file_types()

        # Assert that the method returns the expected list of allowed file extensions
        assert isinstance(result, list)

    def test_get_max_upload_size(self):
        """Tests the get_max_upload_size method"""
        # Call service.get_max_upload_size
        result = self.service.get_max_upload_size()

        # Assert that the method returns the expected maximum upload size
        assert isinstance(result, int)


@pytest.mark.parametrize(
    "upload_data",
    [{"user_id": uuid4(), "filename": "test.csv", "size": 1024, "mime_type": "text/csv"}],
)
def test_create_upload_record(upload_data):
    """Tests the create_upload_record function"""
    # Create a mock database session
    mock_session = unittest.mock.MagicMock()

    # Call create_upload_record with upload data and mock session
    file_upload = FileUploadService.create_upload_record(upload_data, mock_session)

    # Assert that a FileUpload object was created with correct attributes
    assert isinstance(file_upload, FileUpload)
    assert file_upload.user_id == upload_data["user_id"]
    assert file_upload.filename == upload_data["filename"]
    assert file_upload.size == upload_data["size"]
    assert file_upload.mime_type == upload_data["mime_type"]

    # Assert that the object was added to the session
    mock_session.add.assert_called_once_with(file_upload)
    # Assert that session.commit was called
    mock_session.commit.assert_called_once()
    # Assert that the function returns the created FileUpload object
    assert file_upload is not None


def test_generate_presigned_upload_url():
    """Tests the generate_presigned_upload_url function"""
    # Mock the generate_object_key function to return a predictable key
    with patch(
        "app.services.file_upload_service.generate_object_key",
        return_value="test_object_key",
    ) as mock_object_key, patch(
        "app.services.file_upload_service.generate_presigned_post",
        return_value={"url": "mock_url", "fields": {}},
    ) as mock_presigned:
        # Mock the generate_presigned_post function to return a mock response
        test_filename = "test.csv"
        test_content_type = "text/csv"
        test_upload_id = uuid4()

        # Call generate_presigned_upload_url with test parameters
        result = FileUploadService.generate_presigned_upload_url(
            test_filename, test_content_type, test_upload_id
        )

        # Assert that generate_object_key was called with correct parameters
        mock_object_key.assert_called_once_with(
            test_filename, prefix=f"uploads/{str(test_upload_id)}"
        )
        # Assert that generate_presigned_post was called with correct parameters
        mock_presigned.assert_called_once_with(
            "test_object_key", test_content_type
        )
        # Assert that the function returns the expected dictionary with URL, fields, and expiration
        assert result["url"] == "mock_url"
        assert result["fields"] == {}
        assert "expiration" in result


def test_validate_upload_request_valid():
    """Tests the validate_upload_request function with valid input"""
    # Mock validate_file_size to return True
    with patch(
        "app.services.file_upload_service.validate_file_size", return_value=True
    ) as mock_size, patch(
        "app.services.file_upload_service.validate_file_type", return_value=True
    ) as mock_type:
        # Mock validate_file_type to return True
        test_filename = "test.csv"
        test_content_type = "text/csv"
        test_size = 1024

        # Call validate_upload_request with valid parameters
        is_valid, error_message = FileUploadService.validate_upload_request(
            test_filename, test_content_type, test_size
        )

        # Assert that validate_file_size was called with correct size
        mock_size.assert_called_once_with(test_size)
        # Assert that validate_file_type was called with correct filename and content_type
        mock_type.assert_called_once_with(test_filename, test_content_type)
        # Assert that the function returns (True, '')
        assert is_valid is True
        assert error_message == ""


def test_validate_upload_request_invalid_size():
    """Tests the validate_upload_request function with invalid file size"""
    # Mock validate_file_size to return False
    with patch(
        "app.services.file_upload_service.validate_file_size", return_value=False
    ) as mock_size, patch(
        "app.services.file_upload_service.validate_file_type"
    ) as mock_type:
        # Call validate_upload_request with invalid size
        test_filename = "test.csv"
        test_content_type = "text/csv"
        test_size = 1024
        is_valid, error_message = FileUploadService.validate_upload_request(
            test_filename, test_content_type, test_size
        )

        # Assert that validate_file_size was called with correct size
        mock_size.assert_called_once_with(test_size)
        # Assert that validate_file_type was not called
        mock_type.assert_not_called()
        # Assert that the function returns (False, error_message) with size error message
        assert is_valid is False
        assert "File size exceeds" in error_message


def test_validate_upload_request_invalid_type():
    """Tests the validate_upload_request function with invalid file type"""
    # Mock validate_file_size to return True
    with patch(
        "app.services.file_upload_service.validate_file_size", return_value=True
    ) as mock_size, patch(
        "app.services.file_upload_service.validate_file_type", return_value=False
    ) as mock_type:
        # Mock validate_file_type to return False
        test_filename = "test.csv"
        test_content_type = "text/csv"
        test_size = 1024

        # Call validate_upload_request with invalid file type
        is_valid, error_message = FileUploadService.validate_upload_request(
            test_filename, test_content_type, test_size
        )

        # Assert that validate_file_size was called with correct size
        mock_size.assert_called_once_with(test_size)
        # Assert that validate_file_type was called with correct filename and content_type
        mock_type.assert_called_once_with(test_filename, test_content_type)
        # Assert that the function returns (False, error_message) with type error message
        assert is_valid is False
        assert "Invalid file type" in error_message


def test_complete_upload():
    """Tests the complete_upload function"""
    # Create a mock database session
    mock_session = unittest.mock.MagicMock()
    # Create a mock FileUpload object
    mock_file_upload = unittest.mock.MagicMock(spec=FileUpload)
    # Mock session.query to return a query that returns the mock FileUpload
    mock_session.query.return_value.filter.return_value.first.return_value = (
        mock_file_upload
    )
    test_upload_id = uuid4()
    test_object_key = "test_object_key"

    # Call complete_upload with upload_id, object_key, and mock session
    result = FileUploadService.complete_upload(
        test_upload_id, test_object_key, mock_session
    )

    # Assert that FileUpload.update_status was called with UploadStatus.UPLOADED
    mock_file_upload.update_status.assert_called_once_with(UploadStatus.UPLOADED)
    # Assert that FileUpload.storage_path was set to object_key
    assert mock_file_upload.storage_path == test_object_key
    # Assert that session.commit was called
    mock_session.commit.assert_called_once()
    # Assert that the function returns a dictionary with success status
    assert result["status"] == "success"


def test_scan_uploaded_file_clean():
    """Tests the scan_uploaded_file function with clean result"""
    # Create a mock database session
    mock_session = unittest.mock.MagicMock()
    # Create a mock FileUpload object
    mock_file_upload = unittest.mock.MagicMock(spec=FileUpload)
    # Mock session.query to return a query that returns the mock FileUpload
    mock_session.query.return_value.filter.return_value.first.return_value = (
        mock_file_upload
    )
    # Mock FileScanner.scan_s3_file to return a clean scan result
    with patch(
        "app.services.file_upload_service.FileScanner.scan_s3_file",
        return_value={"status": SCAN_RESULT_CLEAN},
    ) as mock_scan:
        test_upload_id = uuid4()
        # Call scan_uploaded_file with upload_id and mock session
        result = FileUploadService.scan_uploaded_file(test_upload_id, mock_session)

        # Assert that FileUpload.update_status was called with UploadStatus.SCANNING and then UploadStatus.PROCESSING
        assert mock_file_upload.update_status.call_count == 2
        mock_file_upload.update_status.assert_has_calls(
            [
                unittest.mock.call(UploadStatus.SCANNING),
                unittest.mock.call(UploadStatus.PROCESSING),
            ]
        )
        # Assert that session.commit was called twice
        assert mock_session.commit.call_count == 2
        # Assert that the function returns a dictionary with clean status
        assert result["status"] == "clean"


def test_scan_uploaded_file_infected():
    """Tests the scan_uploaded_file function with infected result"""
    # Create a mock database session
    mock_session = unittest.mock.MagicMock()
    # Create a mock FileUpload object
    mock_file_upload = unittest.mock.MagicMock(spec=FileUpload)
    # Mock session.query to return a query that returns the mock FileUpload
    mock_session.query.return_value.filter.return_value.first.return_value = (
        mock_file_upload
    )
    # Mock FileScanner.scan_s3_file to return an infected scan result
    with patch(
        "app.services.file_upload_service.FileScanner.scan_s3_file",
        return_value={"status": SCAN_RESULT_INFECTED},
    ) as mock_scan:
        test_upload_id = uuid4()
        # Call scan_uploaded_file with upload_id and mock session
        result = FileUploadService.scan_uploaded_file(test_upload_id, mock_session)

        # Assert that FileUpload.update_status was called with UploadStatus.SCANNING and then UploadStatus.QUARANTINED
        assert mock_file_upload.update_status.call_count == 2
        mock_file_upload.update_status.assert_has_calls(
            [
                unittest.mock.call(UploadStatus.SCANNING),
                unittest.mock.call(UploadStatus.QUARANTINED),
            ]
        )
        # Assert that session.commit was called twice
        assert mock_session.commit.call_count == 2
        # Assert that the function returns a dictionary with infected status
        assert result["status"] == "infected"


def test_get_upload_status():
    """Tests the get_upload_status function"""
    # Create a mock database session
    mock_session = unittest.mock.MagicMock()
    # Create a mock FileUpload object with known attributes
    mock_file_upload = unittest.mock.MagicMock(spec=FileUpload)
    mock_file_upload.id = uuid4()
    mock_file_upload.filename = "test.csv"
    mock_file_upload.status = UploadStatus.UPLOADED
    # Mock session.query to return a query that returns the mock FileUpload
    mock_session.query.return_value.filter.return_value.first.return_value = (
        mock_file_upload
    )
    test_upload_id = uuid4()

    # Call get_upload_status with upload_id and mock session
    result = FileUploadService.get_upload_status(test_upload_id, mock_session)

    # Assert that the function returns a dictionary with correct upload status information
    assert result["id"] == str(mock_file_upload.id)
    assert result["filename"] == mock_file_upload.filename
    assert result["status"] == mock_file_upload.status.value


def test_delete_upload():
    """Tests the delete_upload function"""
    # Create a mock database session
    mock_session = unittest.mock.MagicMock()
    # Create a mock FileUpload object with storage_path
    mock_file_upload = unittest.mock.MagicMock(spec=FileUpload)
    mock_file_upload.storage_path = "test_storage_path"
    # Mock session.query to return a query that returns the mock FileUpload
    mock_session.query.return_value.filter.return_value.first.return_value = (
        mock_file_upload
    )
    # Mock S3Client.delete_file to return True
    with patch(
        "app.services.file_upload_service.S3Client.delete_file", return_value=True
    ) as mock_delete:
        test_upload_id = uuid4()
        # Call delete_upload with upload_id and mock session
        result = FileUploadService.delete_upload(test_upload_id, mock_session)

        # Assert that S3Client.delete_file was called with correct parameters
        mock_delete.assert_called_once_with(mock_file_upload.storage_path, None)
        # Assert that session.delete was called with the FileUpload object
        mock_session.delete.assert_called_once_with(mock_file_upload)
        # Assert that session.commit was called
        mock_session.commit.assert_called_once()
        # Assert that the function returns True
        assert result is True


def test_initiate_file_processing():
    """Tests the initiate_file_processing function"""
    # Create a mock database session
    mock_session = unittest.mock.MagicMock()
    # Create a mock FileUpload object that is ready for processing
    mock_file_upload = unittest.mock.MagicMock(spec=FileUpload)
    mock_file_upload.is_ready_for_processing.return_value = True
    # Mock session.query to return a query that returns the mock FileUpload
    mock_session.query.return_value.filter.return_value.first.return_value = (
        mock_file_upload
    )
    # Mock FileProcessingService.process_file to return a success result
    with patch(
        "app.services.file_upload_service.FileProcessingService.process_file",
        return_value={"status": "success"},
    ) as mock_process:
        test_upload_id = uuid4()
        # Call initiate_file_processing with upload_id and mock session
        result = FileUploadService.initiate_file_processing(test_upload_id, mock_session)

        # Assert that FileProcessingService.process_file was called with upload_id
        mock_process.assert_called_once_with(test_upload_id, mock_session)
        # Assert that the function returns a dictionary with processing initiated status
        assert result["status"] == "success"


@pytest.mark.parametrize(
    "notification_type", ["confirmation", "complete", "failed"]
)
def test_send_upload_notifications(notification_type):
    """Tests the send_upload_notifications function"""
    # Create a mock database session
    mock_session = unittest.mock.MagicMock()
    # Create a mock FileUpload object with user information
    mock_file_upload = unittest.mock.MagicMock(spec=FileUpload)
    mock_file_upload.user_id = uuid4()
    mock_file_upload.filename = "test.csv"
    mock_file_upload.size = 1024
    mock_file_upload.mime_type = "text/csv"
    # Mock session.query to return a query that returns the mock FileUpload
    mock_session.query.return_value.filter.return_value.first.return_value = (
        mock_file_upload
    )
    # Mock EmailService.send_* methods to return True
    with patch(
        "app.services.file_upload_service.EmailService.send_upload_confirmation",
        return_value=True,
    ) as mock_confirmation, patch(
        "app.services.file_upload_service.EmailService.send_upload_complete",
        return_value=True,
    ) as mock_complete, patch(
        "app.services.file_upload_service.EmailService.send_upload_failed",
        return_value=True,
    ) as mock_failed:
        test_upload_id = uuid4()
        test_additional_data = {"email": "test@example.com", "name": "Test User"}

        # Call send_upload_notifications with upload_id, notification_type, and mock session
        result = FileUploadService.send_upload_notifications(
            test_upload_id, notification_type, test_additional_data
        )

        # Assert that the appropriate EmailService method was called based on notification_type
        if notification_type == "confirmation":
            mock_confirmation.assert_called_once()
            mock_complete.assert_not_called()
            mock_failed.assert_not_called()
        elif notification_type == "complete":
            mock_confirmation.assert_not_called()
            mock_complete.assert_called_once()
            mock_failed.assert_not_called()
        elif notification_type == "failed":
            mock_confirmation.assert_not_called()
            mock_complete.assert_not_called()
            mock_failed.assert_called_once()

        # Assert that the function returns True
        assert result is True