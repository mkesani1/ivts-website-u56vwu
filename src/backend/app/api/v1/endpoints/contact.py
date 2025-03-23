from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException, Request  # fastapi ^0.95.0
from uuid import UUID  # standard library
from ..schemas.contact import ContactSchema, ContactResponseSchema, ContactErrorSchema  # src/backend/app/api/v1/schemas/contact.py
from ....services.form_processing_service import form_processing_service  # src/backend/app/services/form_processing_service.py
from ....security.captcha import require_captcha  # src/backend/app/security/captcha.py
from ....core.exceptions import ValidationException, SecurityException  # src/backend/app/core/exceptions.py
from ...errors import APIValidationError  # src/backend/app/api/errors.py
from ....core.logging import get_logger  # src/backend/app/core/logging.py

# Initialize logger
logger = get_logger(__name__)

# Create API router instance
router = APIRouter(prefix="/contact", tags=["contact"])


@router.post("/", response_model=ContactResponseSchema, status_code=200)
@require_captcha(threshold=0.5)
async def submit_contact_form(contact_data: ContactSchema, request: Request) -> ContactResponseSchema:
    """
    API endpoint for submitting contact form data.

    This endpoint receives contact form data, validates it, and processes it
    using the form processing service. It also integrates reCAPTCHA verification
    to prevent spam submissions.

    Args:
        contact_data (ContactSchema): The contact form data to submit.
        request (fastapi.Request): The incoming request object.

    Returns:
        ContactResponseSchema: A JSON response indicating the success or failure
                                of the submission.
    """
    logger.info("Attempting to submit contact form")

    try:
        # Extract client IP address from request
        client_ip = request.client.host if request.client else "unknown"

        # Generate a trace ID for request tracking
        trace_id = logger.extra.get("request_id", "N/A")

        # Process the contact form submission
        result = await form_processing_service.process_contact_form(
            form_data=contact_data.dict(),
            client_ip=client_ip,
            trace_id=trace_id
        )

        # If successful, return ContactResponseSchema with success=True, message, and submission_id
        submission_id: UUID = result["submission_id"]
        return ContactResponseSchema(
            success=True,
            message="Contact form submitted successfully",
            submission_id=submission_id
        )

    except ValidationException as e:
        # Catch ValidationException and return appropriate error response
        logger.warning(f"Validation error: {e.message}", extra={"details": e.details})
        raise APIValidationError(message=e.message, details=e.details) from e

    except SecurityException as e:
        # Catch SecurityException and return appropriate error response
        logger.warning(f"Security error: {e.message}", extra={"details": e.details})
        raise HTTPException(status_code=403, detail=e.message) from e

    except Exception as e:
        # Catch any other exceptions, log the error, and return a generic error response
        logger.error(f"An unexpected error occurred: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="An unexpected error occurred") from e

# Export the router
__all__ = ["router"]