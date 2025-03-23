# src/backend/app/api/v1/endpoints/demo_request.py
import uuid
from typing import Dict, Any

from pydantic import ValidationError  # pydantic v1.10.0
from fastapi import APIRouter, Depends, HTTPException, Request  # fastapi v0.95.0

from ...services.form_processing_service import form_processing_service
from ...security.captcha import require_captcha
from ...core.exceptions import ValidationException, SecurityException, ProcessingException
from ...core.logging import get_logger
from ..schemas.demo_request import (
    DemoRequestSchema,
    DemoRequestResponseSchema,
    DemoRequestErrorSchema
)

# Initialize logger for this module
logger = get_logger(__name__)

# Create API router instance
demo_request_router = APIRouter()


@demo_request_router.post(
    '/',
    response_model=DemoRequestResponseSchema,
    responses={
        400: {'model': DemoRequestErrorSchema},
        422: {'model': DemoRequestErrorSchema},
        500: {'model': DemoRequestErrorSchema}
    }
)
@require_captcha(threshold=0.5)
async def submit_demo_request(form_data: Dict[str, Any], request: Request) -> Dict[str, Any]:
    """
    Handles demo request form submissions.

    This endpoint receives demo request data, validates it, and processes
    the submission using the form processing service. It returns a success
    response with a submission ID or an error response with details.

    Args:
        form_data (DemoRequestSchema): Validated demo request form data
        request (Request): The incoming request object

    Returns:
        Dict[str, Any]: Response containing success status, message, and
                         submission ID or error details
    """
    trace_id = str(uuid.uuid4())

    logger.info(f"Incoming demo request", extra={"trace_id": trace_id})

    client_ip = request.client.host

    try:
        # Process the demo request using the form processing service
        submission_result = await form_processing_service.process_demo_request(form_data, client_ip)

        # Return success response with submission ID
        return {
            "success": True,
            "message": "Your demo request has been successfully submitted. Our team will contact you shortly.",
            "submission_id": submission_result["submission_id"]
        }

    except ValidationException as e:
        # Handle validation errors and return 400 Bad Request
        logger.warning(f"Validation error processing demo request: {str(e)}", extra={"trace_id": trace_id})
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "message": "There was an error processing your demo request due to validation errors.",
                "errors": e.details
            }
        )

    except SecurityException as e:
        # Handle security-related errors (e.g., CAPTCHA failure)
        logger.warning(f"Security error processing demo request: {str(e)}", extra={"trace_id": trace_id})
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "message": "There was an error processing your demo request due to security reasons.",
                "errors": {"security": [e.message]}
            }
        )

    except ProcessingException as e:
        # Handle processing errors and return 422 Unprocessable Entity
        logger.error(f"Processing error for demo request: {str(e)}", extra={"trace_id": trace_id})
        raise HTTPException(
            status_code=422,
            detail={
                "success": False,
                "message": "There was an error processing your demo request.",
                "errors": {"processing": [e.message]}
            }
        )

    except Exception as e:
        # Handle any other exceptions and return 500 Internal Server Error
        logger.exception(f"Unexpected error processing demo request: {str(e)}", extra={"trace_id": trace_id})
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "message": "An unexpected error occurred while processing your demo request.",
                "errors": {"error": [str(e)]}
            }
        )

# Export the router
__all__ = ["demo_request_router"]