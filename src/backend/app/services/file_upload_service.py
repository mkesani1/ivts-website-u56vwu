# src/backend/app/services/file_upload_service.py
import os
import uuid
import datetime
import typing
from typing import Dict, Tuple

from sqlalchemy.orm import Session  # sqlalchemy v1.4.0

from ..core.config import settings  # Import application configuration settings for file uploads
from ..core.logging import get_logger  # Import logging functionality for file upload operations
from ..utils.file_utils import (  # Import utility functions for file operations
    validate_file_type,
    validate_file_size,
    generate_secure_filename,
    generate_unique_filename,
)
from ..integrations.aws_s3 import (  # Import S3 client for file storage operations
    S3Client,
    generate_presigned_post,
    generate_object_key,
)
from ..security.file_scanner import (  # Import file scanner for security checks
    FileScanner,
    SCAN_RESULT_CLEAN,
    SCAN_RESULT_INFECTED,
)
from ..api.v1.models.file_upload import (  # Import database model for file uploads
    FileUpload,
    UploadStatus,
)
from ..services.file_processing_service import FileProcessingService  # Import service for processing uploaded files
from ..services.email_service import EmailService  # Import service for sending email notifications
from ..db.session import SessionLocal  # Import database session factory

# Initialize logger
logger = get_logger(__name__)

# Global constants for file upload settings
MAX_UPLOAD_SIZE_MB = settings.MAX_UPLOAD_SIZE_MB  # Maximum upload size in MB
ALLOWED_EXTENSIONS = settings.ALLOWED_UPLOAD_EXTENSIONS.split(
    ","
)  # Allowed file extensions
UPLOAD_EXPIRATION_SECONDS = 3600  # Presigned URL expiration time in seconds


def create_upload_record(
    upload_data: Dict, Session: SessionLocal
) -> FileUpload:
    """Creates a new file upload record in the database

    Args:
        upload_data (Dict): Dictionary containing upload data
        Session (db_session): Database session

    Returns:
        FileUpload: Newly created file upload record
    """
    try:
        # Create a new FileUpload instance with upload_data
        file_upload = FileUpload(**upload_data)
        # Set initial status to UploadStatus.PENDING
        file_upload.status = UploadStatus.PENDING
        # Set created_at timestamp to current time
        file_upload.created_at = datetime.datetime.utcnow()

        # Add record to database session
        Session.add(file_upload)
        # Commit session to save record
        Session.commit()
        # Refresh the instance to load any database-generated values
        Session.refresh(file_upload)

        # Log creation of upload record
        logger.info(f"Created new upload record with ID: {file_upload.id}")

        # Return the created FileUpload instance
        return file_upload
    except Exception as e:
        logger.error(f"Error creating upload record: {str(e)}", exc_info=True)
        Session.rollback()
        raise


def generate_presigned_upload_url(
    filename: str, content_type: str, upload_id: uuid.UUID
) -> Dict:
    """Generates a presigned URL for direct file upload to S3

    Args:
        filename (str): Filename of the file to be uploaded
        content_type (str): Content type of the file
        upload_id (uuid.UUID): Unique identifier for the upload

    Returns:
        Dict: Dictionary with presigned URL, fields, and expiration
    """
    try:
        # Generate a secure object key using generate_object_key
        object_key = generate_object_key(
            filename, prefix=f"uploads/{str(upload_id)}"
        )
        # Call generate_presigned_post to get presigned URL and fields
        response = generate_presigned_post(object_key, content_type)
        # Calculate expiration timestamp
        expiration = datetime.datetime.utcnow() + datetime.timedelta(
            seconds=UPLOAD_EXPIRATION_SECONDS
        )

        # Return dictionary with presigned URL, fields, object key, and expiration
        return {
            "url": response["url"],
            "fields": response["fields"],
            "object_key": object_key,
            "expiration": expiration.isoformat(),
        }
    except Exception as e:
        logger.error(f"Error generating presigned URL: {str(e)}", exc_info=True)
        raise


def validate_upload_request(filename: str, content_type: str, size: int) -> Tuple[bool, str]:
    """Validates a file upload request

    Args:
        filename (str): Filename of the file to be uploaded
        content_type (str): Content type of the file
        size (int): Size of the file in bytes

    Returns:
        Tuple[bool, str]: (bool, str) - Validation result and error message if any
    """
    # Validate file size using validate_file_size
    if not validate_file_size(size):
        return False, f"File size exceeds the limit of {MAX_UPLOAD_SIZE_MB} MB"

    # Validate file type using validate_file_type
    if not validate_file_type(filename, content_type):
        return False, "Invalid file type"

    # If validation passes, return (True, '')
    return True, ""


def complete_upload(upload_id: uuid.UUID, object_key: str, Session: SessionLocal) -> Dict:
    """Marks an upload as complete and initiates security scanning

    Args:
        upload_id (uuid.UUID): Unique identifier for the upload
        object_key (str): S3 object key for the uploaded file
        Session (db_session): Database session

    Returns:
        Dict: Upload completion status and next steps
    """
    try:
        # Retrieve the upload record from database
        file_upload = Session.query(FileUpload).filter(FileUpload.id == upload_id).first()

        if not file_upload:
            logger.warning(f"Upload record not found for ID: {upload_id}")
            return {"status": "error", "message": "Upload record not found"}

        # Update upload status to UploadStatus.UPLOADED
        file_upload.update_status(UploadStatus.UPLOADED)
        # Update storage_path with the S3 object key
        file_upload.storage_path = object_key
        # Commit database changes
        Session.commit()

        logger.info(f"Upload completed successfully for ID: {upload_id}")

        # Initiate asynchronous security scanning
        scan_uploaded_file(upload_id, Session)

        # Return completion status dictionary
        return {"status": "success", "message": "Upload completed, initiating security scan"}
    except Exception as e:
        logger.error(f"Error completing upload: {str(e)}", exc_info=True)
        Session.rollback()
        return {"status": "error", "message": f"Error completing upload: {str(e)}"}


def scan_uploaded_file(upload_id: uuid.UUID, Session: SessionLocal) -> Dict:
    """Performs security scanning on an uploaded file

    Args:
        upload_id (uuid.UUID): Unique identifier for the upload
        Session (db_session): Database session

    Returns:
        Dict: Scan results with status and details
    """
    try:
        # Retrieve the upload record from database
        file_upload = Session.query(FileUpload).filter(FileUpload.id == upload_id).first()

        if not file_upload:
            logger.warning(f"Upload record not found for ID: {upload_id}")
            return {"status": "error", "message": "Upload record not found"}

        # Update upload status to UploadStatus.SCANNING
        file_upload.update_status(UploadStatus.SCANNING)
        # Commit database changes
        Session.commit()

        logger.info(f"Initiating security scan for upload ID: {upload_id}")

        # Initialize FileScanner
        scanner = FileScanner()
        # Scan the file in S3 using scanner.scan_s3_file
        scan_result = scanner.scan_s3_file(file_upload.storage_path, settings.AWS_S3_UPLOAD_BUCKET_NAME)

        # If scan result is clean, update status to UploadStatus.PROCESSING
        if scan_result["status"] == SCAN_RESULT_CLEAN:
            file_upload.update_status(UploadStatus.PROCESSING)
            logger.info(f"File scan clean for upload ID: {upload_id}, initiating file processing")
            initiate_file_processing(upload_id, Session)
        # If scan result is infected, update status to UploadStatus.QUARANTINED
        elif scan_result["status"] == SCAN_RESULT_INFECTED:
            file_upload.update_status(UploadStatus.QUARANTINED)
            logger.warning(f"File scan infected for upload ID: {upload_id}, file quarantined")

        # Commit database changes
        Session.commit()

        # Return scan results dictionary
        return scan_result
    except Exception as e:
        logger.error(f"Error scanning uploaded file: {str(e)}", exc_info=True)
        Session.rollback()
        return {"status": "error", "message": f"Error scanning file: {str(e)}"}


def get_upload_status(upload_id: uuid.UUID, Session: SessionLocal) -> Dict:
    """Gets the current status of a file upload

    Args:
        upload_id (uuid.UUID): Unique identifier for the upload
        Session (db_session): Database session

    Returns:
        Dict: Upload status information
    """
    try:
        # Retrieve the upload record from database
        file_upload = Session.query(FileUpload).filter(FileUpload.id == upload_id).first()

        if not file_upload:
            logger.warning(f"Upload record not found for ID: {upload_id}")
            return {"status": "error", "message": "Upload record not found"}

        # Create status response dictionary with upload details
        status_info = file_upload.to_dict()

        # If processing is complete, include analysis results
        if file_upload.is_processing_complete() and file_upload.analysis_result:
            status_info["analysis_results"] = file_upload.analysis_result.to_dict()

        # Return the status information dictionary
        return status_info
    except Exception as e:
        logger.error(f"Error getting upload status: {str(e)}", exc_info=True)
        return {"status": "error", "message": f"Error getting upload status: {str(e)}"}


def delete_upload(upload_id: uuid.UUID, Session: SessionLocal) -> bool:
    """Deletes an upload and associated files

    Args:
        upload_id (uuid.UUID): Unique identifier for the upload
        Session (db_session): Database session

    Returns:
        bool: True if deletion was successful, False otherwise
    """
    try:
        # Retrieve the upload record from database
        file_upload = Session.query(FileUpload).filter(FileUpload.id == upload_id).first()

        if not file_upload:
            logger.warning(f"Upload record not found for ID: {upload_id}")
            return False

        # Initialize S3 client
        s3_client = S3Client()
        # Delete file from S3 storage
        s3_client.delete_file(file_upload.storage_path, settings.AWS_S3_UPLOAD_BUCKET_NAME)

        # Delete upload record from database
        Session.delete(file_upload)
        # Commit database changes
        Session.commit()

        logger.info(f"Deleted upload record and file for ID: {upload_id}")

        # Return True if successful, False otherwise
        return True
    except Exception as e:
        logger.error(f"Error deleting upload: {str(e)}", exc_info=True)
        Session.rollback()
        return False


def initiate_file_processing(upload_id: uuid.UUID, Session: SessionLocal) -> Dict:
    """Initiates processing of an uploaded file

    Args:
        upload_id (uuid.UUID): Unique identifier for the upload
        Session (db_session): Database session

    Returns:
        Dict: Processing initiation status
    """
    try:
        # Retrieve the upload record from database
        file_upload = Session.query(FileUpload).filter(FileUpload.id == upload_id).first()

        if not file_upload:
            logger.warning(f"Upload record not found for ID: {upload_id}")
            return {"status": "error", "message": "Upload record not found"}

        # Check if file is ready for processing
        if not file_upload.is_ready_for_processing():
            logger.warning(f"File is not ready for processing, status: {file_upload.status}")
            return {"status": "error", "message": "File is not ready for processing"}

        # Initialize FileProcessingService
        processing_service = FileProcessingService()
        # Call processing_service.process_file to start processing
        processing_service.process_file(upload_id, Session)

        logger.info(f"File processing initiated for upload ID: {upload_id}")

        # Return processing initiation status dictionary
        return {"status": "success", "message": "File processing initiated"}
    except Exception as e:
        logger.error(f"Error initiating file processing: {str(e)}", exc_info=True)
        return {"status": "error", "message": f"Error initiating file processing: {str(e)}"}


def send_upload_notifications(upload_id: uuid.UUID, notification_type: str, additional_data: Dict, Session: SessionLocal) -> bool:
    """Sends email notifications for upload events

    Args:
        upload_id (uuid.UUID): Unique identifier for the upload
        notification_type (str): Type of notification (confirmation, complete, failed)
        additional_data (Dict): Additional data for the notification
        Session (db_session): Database session

    Returns:
        bool: True if notification was sent successfully, False otherwise
    """
    try:
        # Retrieve the upload record from database
        file_upload = Session.query(FileUpload).filter(FileUpload.id == upload_id).first()

        if not file_upload:
            logger.warning(f"Upload record not found for ID: {upload_id}")
            return False

        # Initialize EmailService
        email_service = EmailService()

        # Determine notification type and prepare data
        if notification_type == "confirmation":
            # Send upload confirmation email
            email_service.send_upload_confirmation(
                to_email=additional_data.get("email"),
                name=additional_data.get("name"),
                upload_data=file_upload.to_dict()
            )
        elif notification_type == "complete":
            # Send upload complete notification
            email_service.send_upload_complete(
                to_email=additional_data.get("email"),
                name=additional_data.get("name"),
                upload_data=file_upload.to_dict(),
                processing_results=additional_data.get("processing_results")
            )
        elif notification_type == "failed":
            # Send upload failed notification
            email_service.send_upload_failed(
                to_email=additional_data.get("email"),
                name=additional_data.get("name"),
                upload_data=file_upload.to_dict(),
                error_message=additional_data.get("error_message")
            )
        else:
            logger.warning(f"Invalid notification type: {notification_type}")
            return False

        logger.info(f"Sent '{notification_type}' email notification for upload ID: {upload_id}")

        # Return True if email was sent successfully, False otherwise
        return True
    except Exception as e:
        logger.error(f"Error sending upload notification: {str(e)}", exc_info=True)
        return False


class FileUploadService:
    """Service class for managing file uploads in the application"""

    def __init__(self, Session: SessionLocal):
        """Initializes the FileUploadService with necessary dependencies

        Args:
            Session (db_session): Database session
        """
        # Initialize S3 client for storage operations
        self._s3_client = S3Client()
        # Initialize file scanner for security checks
        self._file_scanner = FileScanner()
        # Initialize processing service for file analysis
        self._processing_service = FileProcessingService()
        # Initialize email service for notifications
        self._email_service = EmailService()
        # Store database session for data operations
        self.Session = Session

        logger.info("FileUploadService initialized")

    def create_upload(self, upload_data: Dict, filename: str, content_type: str, size: int) -> Dict:
        """Creates a new file upload record and generates presigned upload URL

        Args:
            upload_data (Dict): Dictionary containing upload metadata
            filename (str): Filename of the file to be uploaded
            content_type (str): Content type of the file
            size (int): Size of the file in bytes

        Returns:
            Dict: Upload creation response with presigned URL and upload ID
        """
        try:
            # Validate upload request using validate_upload_request
            is_valid, error_message = self.validate_upload_request(filename, content_type, size)
            if not is_valid:
                logger.warning(f"Upload validation failed: {error_message}")
                return {"status": "error", "message": error_message}

            # Create upload record using create_upload_record
            file_upload = create_upload_record(upload_data, self.Session)

            # Generate presigned upload URL using generate_presigned_upload_url
            presigned_data = generate_presigned_upload_url(filename, content_type, file_upload.id)

            # Send upload confirmation email
            self.send_upload_notifications(
                upload_id=file_upload.id,
                notification_type="confirmation",
                additional_data={"email": upload_data.get("email"), "name": upload_data.get("name")}
            )

            # Return response with upload ID and presigned URL information
            return {
                "status": "success",
                "upload_id": str(file_upload.id),
                "upload_url": presigned_data["url"],
                "upload_fields": presigned_data["fields"],
                "object_key": presigned_data["object_key"],
                "expiration": presigned_data["expiration"],
            }
        except Exception as e:
            logger.error(f"Error creating upload: {str(e)}", exc_info=True)
            return {"status": "error", "message": f"Error creating upload: {str(e)}"}

    def complete_upload(self, upload_id: uuid.UUID, object_key: str) -> Dict:
        """Marks an upload as complete and initiates security scanning

        Args:
            upload_id (uuid.UUID): Unique identifier for the upload
            object_key (str): S3 object key for the uploaded file

        Returns:
            Dict: Upload completion status and next steps
        """
        try:
            # Call complete_upload function with upload_id and object_key
            return complete_upload(upload_id, object_key, self.Session)
        except Exception as e:
            logger.error(f"Error completing upload: {str(e)}", exc_info=True)
            return {"status": "error", "message": f"Error completing upload: {str(e)}"}

    def get_upload_status(self, upload_id: uuid.UUID) -> Dict:
        """Gets the current status of a file upload

        Args:
            upload_id (uuid.UUID): Unique identifier for the upload

        Returns:
            Dict: Upload status information
        """
        try:
            # Call get_upload_status function with upload_id
            return get_upload_status(upload_id, self.Session)
        except Exception as e:
            logger.error(f"Error getting upload status: {str(e)}", exc_info=True)
            return {"status": "error", "message": f"Error getting upload status: {str(e)}"}

    def delete_upload(self, upload_id: uuid.UUID) -> bool:
        """Deletes an upload and associated files

        Args:
            upload_id (uuid.UUID): Unique identifier for the upload

        Returns:
            bool: True if deletion was successful, False otherwise
        """
        try:
            # Call delete_upload function with upload_id
            return delete_upload(upload_id, self.Session)
        except Exception as e:
            logger.error(f"Error deleting upload: {str(e)}", exc_info=True)
            return False

    def scan_uploaded_file(self, upload_id: uuid.UUID) -> Dict:
        """Performs security scanning on an uploaded file

        Args:
            upload_id (uuid.UUID): Unique identifier for the upload

        Returns:
            Dict: Scan results with status and details
        """
        try:
            # Call scan_uploaded_file function with upload_id
            return scan_uploaded_file(upload_id, self.Session)
        except Exception as e:
            logger.error(f"Error scanning uploaded file: {str(e)}", exc_info=True)
            return {"status": "error", "message": f"Error scanning file: {str(e)}"}

    def initiate_file_processing(self, upload_id: uuid.UUID) -> Dict:
        """Initiates processing of an uploaded file

        Args:
            upload_id (uuid.UUID): Unique identifier for the upload

        Returns:
            Dict: Processing initiation status
        """
        try:
            # Call initiate_file_processing function with upload_id
            return initiate_file_processing(upload_id, self.Session)
        except Exception as e:
            logger.error(f"Error initiating file processing: {str(e)}", exc_info=True)
            return {"status": "error", "message": f"Error initiating file processing: {str(e)}"}

    def send_upload_notifications(self, upload_id: uuid.UUID, notification_type: str, additional_data: Dict) -> bool:
        """Sends email notifications for upload events

        Args:
            upload_id (uuid.UUID): Unique identifier for the upload
            notification_type (str): Type of notification (confirmation, complete, failed)
            additional_data (Dict): Additional data for the notification

        Returns:
            bool: True if notification was sent successfully, False otherwise
        """
        try:
            # Call send_upload_notifications function with parameters
            return send_upload_notifications(upload_id, notification_type, additional_data, self.Session)
        except Exception as e:
            logger.error(f"Error sending upload notification: {str(e)}", exc_info=True)
            return False

    def validate_upload_request(self, filename: str, content_type: str, size: int) -> Tuple[bool, str]:
        """Validates a file upload request

        Args:
            filename (str): Filename of the file to be uploaded
            content_type (str): Content type of the file
            size (int): Size of the file in bytes

        Returns:
            Tuple[bool, str]: (bool, str) - Validation result and error message if any
        """
        try:
            # Call validate_upload_request function with parameters
            return validate_upload_request(filename, content_type, size)
        except Exception as e:
            logger.error(f"Error validating upload request: {str(e)}", exc_info=True)
            return False, f"Error validating upload request: {str(e)}"

    def get_allowed_file_types(self) -> list:
        """Returns the list of allowed file types for upload

        Returns:
            list: List of allowed file extensions
        """
        # Return the ALLOWED_EXTENSIONS list
        return ALLOWED_EXTENSIONS

    def get_max_upload_size(self) -> int:
        """Returns the maximum allowed upload size in MB

        Returns:
            int: Maximum upload size in MB
        """
        # Return the MAX_UPLOAD_SIZE_MB value
        return MAX_UPLOAD_SIZE_MB