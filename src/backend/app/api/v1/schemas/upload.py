"""
Pydantic schemas for file upload functionality in the IndiVillage.com application.

Defines data models for upload requests, responses, status checks, and file metadata validation.
These schemas ensure proper validation of user inputs and consistent API responses for the file
upload feature.
"""

from datetime import datetime
import typing
import uuid

from pydantic import BaseModel, Field, validator, constr, conint  # pydantic v1.10.0

# Internal imports
from app.utils.validation_utils import validate_file_extension, validate_file_size, validate_mime_type
from app.api.v1.models.file_upload import UploadStatus
from app.core.config import settings

# Service interest choices
SERVICE_CHOICES = ["Data Collection", "Data Preparation", "AI Model Development", "Human-in-the-Loop", "Not sure (need consultation)"]

# File upload configuration
MAX_UPLOAD_SIZE_MB = settings.MAX_UPLOAD_SIZE_MB
ALLOWED_EXTENSIONS = settings.ALLOWED_UPLOAD_EXTENSIONS.split(",")


class FileMetadataSchema(BaseModel):
    """Schema for validating file metadata during upload requests."""
    filename: str
    content_type: str
    size: int

    @validator('filename')
    def validate_filename(cls, v):
        """Validates that the filename has an allowed extension."""
        if not validate_file_extension(v):
            raise ValueError(f"File extension not allowed. Allowed extensions: {', '.join(ALLOWED_EXTENSIONS)}")
        return v

    @validator('size')
    def validate_size(cls, v):
        """Validates that the file size is within allowed limits."""
        if not validate_file_size(v):
            max_size_bytes = MAX_UPLOAD_SIZE_MB * 1024 * 1024
            raise ValueError(f"File size exceeds the maximum allowed size of {MAX_UPLOAD_SIZE_MB}MB ({max_size_bytes} bytes)")
        return v

    @validator('content_type')
    def validate_content_type(cls, v, values):
        """Validates that the content type is consistent with the filename."""
        if 'filename' not in values:
            return v
        
        if not validate_mime_type(v, values['filename']):
            raise ValueError(f"Content type '{v}' does not match the expected type for the file extension")
        return v


class UploadRequestSchema(BaseModel):
    """Schema for file upload request data."""
    name: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., min_length=5, max_length=100)
    company: str = Field(..., min_length=2, max_length=100)
    phone: str = Field(None, max_length=20)
    service_interest: str
    description: str = Field(None, max_length=1000)
    captcha_token: str = Field(...)

    @validator('service_interest')
    def validate_service_interest(cls, v):
        """Validates that the service interest is one of the allowed choices."""
        if v not in SERVICE_CHOICES:
            raise ValueError(f"Service interest must be one of: {', '.join(SERVICE_CHOICES)}")
        return v

    @validator('email')
    def validate_email(cls, v):
        """Validates that the email is in a valid format."""
        # Pydantic's email validation will handle this automatically
        return v


class UploadResponseSchema(BaseModel):
    """Schema for file upload response data."""
    upload_id: uuid.UUID
    presigned_url: str
    presigned_fields: dict
    expires_at: datetime
    status: str


class UploadStatusSchema(BaseModel):
    """Schema for file upload status response."""
    upload_id: uuid.UUID
    filename: str
    status: str
    created_at: datetime
    processed_at: typing.Optional[datetime] = None
    analysis_result: typing.Optional[dict] = None


class UploadCompleteSchema(BaseModel):
    """Schema for upload completion notification."""
    upload_id: uuid.UUID
    success: bool
    message: str
    metadata: typing.Optional[dict] = None


class ProcessingRequestSchema(BaseModel):
    """Schema for requesting file processing."""
    upload_id: uuid.UUID
    processing_options: typing.Optional[dict] = None


class ProcessingResponseSchema(BaseModel):
    """Schema for file processing response."""
    job_id: uuid.UUID
    status: str
    estimated_completion: datetime


class ProcessingResultSchema(BaseModel):
    """Schema for file processing results."""
    upload_id: uuid.UUID
    status: str
    summary: dict
    details: typing.Optional[dict] = None
    completed_at: datetime