# src/backend/app/api/v1/endpoints/uploads.py
import uuid
import typing

from sqlalchemy.orm import Session  # sqlalchemy v1.4.0
from fastapi import APIRouter, Depends, HTTPException, status, Request  # fastapi v0.85.0

from ...services.file_upload_service import FileUploadService  # Service for handling file uploads
from ...services.file_processing_service import FileProcessingService  # Service for processing uploaded files
from ...db.session import get_db  # Database session dependency
from ...security.captcha import validate_captcha_token, require_captcha  # CAPTCHA validation functions
from ...core.exceptions import SecurityException  # Exception for security-related errors
from ...core.logging import get_logger  # Logger for upload operations
from ...core.config import settings  # Application configuration settings
from ..schemas.upload import (  # Schemas for upload request and response
    UploadRequestSchema,
    UploadResponseSchema,
    UploadStatusSchema,
    UploadCompleteSchema,
    FileMetadataSchema,
    ProcessingRequestSchema,
    ProcessingResponseSchema,
)

# Initialize router
router = APIRouter(prefix="/uploads", tags=["uploads"])

# Initialize logger
logger = get_logger(__name__)


@router.post("/request", response_model=UploadResponseSchema, status_code=status.HTTP_201_CREATED)
@require_captcha(threshold=0.5)
async def request_upload(
    upload_request: UploadRequestSchema,
    request: Request,
    db_session: Session = Depends(get_db),
) -> UploadResponseSchema:
    """Endpoint to request a file upload URL and create an upload record"""
    try:
        # Log the upload request
        logger.info(f"Received upload request from {request.client.host}")

        # Extract file metadata from request (filename, content_type, size)
        filename = request.headers.get("X-Filename")
        content_type = request.headers.get("Content-Type")
        size_str = request.headers.get("Content-Length")

        if not filename or not content_type or not size_str:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing required headers (X-Filename, Content-Type, Content-Length)",
            )

        try:
            size = int(size_str)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Content-Length"
            )

        # Validate file metadata
        file_metadata = FileMetadataSchema(filename=filename, content_type=content_type, size=size)

        # Create FileUploadService instance with database session
        upload_service = FileUploadService(Session=db_session)

        # Call upload_service.create_upload with user data and file metadata
        upload_data = upload_request.dict()
        upload_response = upload_service.create_upload(upload_data, filename, content_type, size)

        if upload_response["status"] == "error":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=upload_response["message"]
            )

        # Return UploadResponseSchema with presigned URL and upload details
        return UploadResponseSchema(
            upload_id=uuid.UUID(upload_response["upload_id"]),
            presigned_url=upload_response["upload_url"],
            presigned_fields=upload_response["upload_fields"],
            expires_at=upload_response["expiration"],
            status="pending",
        )
    except HTTPException as http_exception:
        # Re-raise HTTP exceptions
        raise http_exception
    except SecurityException as security_exception:
        # Handle security exceptions
        logger.warning(f"Security exception: {security_exception.message}")
        raise HTTPException(
            status_code=security_exception.status_code, detail=security_exception.message
        )
    except Exception as e:
        # Handle exceptions and return appropriate HTTP error responses
        logger.error(f"Error requesting upload: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {str(e)}"
        )


@router.post("/complete", status_code=status.HTTP_200_OK)
async def complete_upload(
    upload_complete: UploadCompleteSchema,
    db_session: Session = Depends(get_db),
) -> dict:
    """Endpoint to mark an upload as complete and initiate processing"""
    try:
        # Log the upload completion request
        logger.info(f"Received upload completion request for ID: {upload_complete.upload_id}")

        # Parse upload_id from request
        upload_id = upload_complete.upload_id

        # Create FileUploadService instance with database session
        upload_service = FileUploadService(Session=db_session)

        # Retrieve upload status
        upload_status = upload_service.get_upload_status(upload_id)

        if upload_status["status"] == "error":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=upload_status["message"]
            )

        # Call upload_service.complete_upload with upload_id and object_key
        object_key = upload_status["storage_path"]
        completion_status = upload_service.complete_upload(upload_id, object_key)

        if completion_status["status"] == "error":
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=completion_status["message"]
            )

        # Return completion status and next steps
        return {"status": "success", "message": "Upload completed, initiating security scan"}
    except HTTPException as http_exception:
        # Re-raise HTTP exceptions
        raise http_exception
    except Exception as e:
        # Handle exceptions and return appropriate HTTP error responses
        logger.error(f"Error completing upload: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {str(e)}"
        )


@router.get("/status/{upload_id}", response_model=UploadStatusSchema, status_code=status.HTTP_200_OK)
async def get_upload_status(
    upload_id: uuid.UUID,
    db_session: Session = Depends(get_db),
) -> UploadStatusSchema:
    """Endpoint to check the status of an upload"""
    try:
        # Log the upload status request
        logger.info(f"Received upload status request for ID: {upload_id}")

        # Create FileUploadService instance with database session
        upload_service = FileUploadService(Session=db_session)

        # Call upload_service.get_upload_status with upload_id
        upload_status = upload_service.get_upload_status(upload_id)

        if upload_status["status"] == "error":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=upload_status["message"]
            )

        # Return UploadStatusSchema with current status
        return UploadStatusSchema(
            upload_id=uuid.UUID(upload_status["id"]),
            filename=upload_status["filename"],
            status=upload_status["status"],
            created_at=upload_status["created_at"],
            processed_at=upload_status.get("processed_at"),
            analysis_result=upload_status.get("analysis_result"),
        )
    except HTTPException as http_exception:
        # Re-raise HTTP exceptions
        raise http_exception
    except Exception as e:
        # Handle exceptions and return appropriate HTTP error responses
        logger.error(f"Error getting upload status: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {str(e)}"
        )


@router.delete("/{upload_id}", status_code=status.HTTP_200_OK)
async def delete_upload(
    upload_id: uuid.UUID,
    db_session: Session = Depends(get_db),
) -> dict:
    """Endpoint to delete an upload and associated files"""
    try:
        # Log the upload deletion request
        logger.info(f"Received upload deletion request for ID: {upload_id}")

        # Create FileUploadService instance with database session
        upload_service = FileUploadService(Session=db_session)

        # Call upload_service.delete_upload with upload_id
        deletion_status = upload_service.delete_upload(upload_id)

        if not deletion_status:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Upload record not found"
            )

        # Return deletion status response
        return {"status": "success", "message": "Upload deleted successfully"}
    except HTTPException as http_exception:
        # Re-raise HTTP exceptions
        raise http_exception
    except Exception as e:
        # Handle exceptions and return appropriate HTTP error responses
        logger.error(f"Error deleting upload: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {str(e)}"
        )


@router.post("/process", response_model=ProcessingResponseSchema, status_code=status.HTTP_202_ACCEPTED)
async def request_processing(
    processing_request: ProcessingRequestSchema,
    db_session: Session = Depends(get_db),
) -> ProcessingResponseSchema:
    """Endpoint to request processing of an uploaded file"""
    try:
        # Log the processing request
        logger.info(f"Received processing request for ID: {processing_request.upload_id}")

        # Extract upload_id and processing_options from request
        upload_id = processing_request.upload_id
        processing_options = processing_request.processing_options

        # Create FileProcessingService instance with database session
        processing_service = FileProcessingService()

        # Call processing_service.process_file with upload_id
        processing_response = processing_service.process_file(upload_id, db_session, processing_options)

        # Return ProcessingResponseSchema with job ID and status
        return ProcessingResponseSchema(
            job_id=processing_response["job_id"],
            status=processing_response["status"],
            estimated_completion=processing_response["estimated_completion"],
        )
    except HTTPException as http_exception:
        # Re-raise HTTP exceptions
        raise http_exception
    except Exception as e:
        # Handle exceptions and return appropriate HTTP error responses
        logger.error(f"Error requesting file processing: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {str(e)}"
        )


@router.get("/results/{upload_id}", status_code=status.HTTP_200_OK)
async def get_processing_results(
    upload_id: uuid.UUID,
    db_session: Session = Depends(get_db),
) -> dict:
    """Endpoint to get the results of file processing"""
    try:
        # Log the processing results request
        logger.info(f"Received processing results request for ID: {upload_id}")

        # Create FileProcessingService instance with database session
        processing_service = FileProcessingService()

        # Call processing_service.get_processing_results with upload_id
        processing_results = processing_service.get_processing_results(upload_id, db_session)

        # Return processing results or status
        return processing_results
    except HTTPException as http_exception:
        # Re-raise HTTP exceptions
        raise http_exception
    except Exception as e:
        # Handle exceptions and return appropriate HTTP error responses
        logger.error(f"Error getting processing results: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {str(e)}"
        )


@router.get("/allowed-types", status_code=status.HTTP_200_OK)
async def get_allowed_file_types(
    db_session: Session = Depends(get_db),
) -> dict:
    """Endpoint to get the list of allowed file types for upload"""
    try:
        # Log the request for allowed file types
        logger.info("Received request for allowed file types")

        # Create FileUploadService instance with database session
        upload_service = FileUploadService(Session=db_session)

        # Get allowed file types from upload_service.get_allowed_file_types()
        allowed_types = upload_service.get_allowed_file_types()

        # Get maximum upload size from upload_service.get_max_upload_size()
        max_size_mb = upload_service.get_max_upload_size()

        # Return dictionary with allowed_types and max_size_mb
        return {"allowed_types": allowed_types, "max_size_mb": max_size_mb}
    except Exception as e:
        # Handle exceptions and return appropriate HTTP error responses
        logger.error(f"Error getting allowed file types: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {str(e)}"
        )