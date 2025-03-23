# typing
from typing import Dict, Any

# FastAPI
from fastapi import APIRouter, Request  # fastapi version: ^0.95.0
from fastapi.responses import JSONResponse

# UUID
import uuid  # uuid version: standard library

# Internal imports
from ..schemas.quote_request import QuoteRequestSchema, QuoteRequestResponseSchema, QuoteRequestErrorSchema
from ....services.form_processing_service import form_processing_service
from ....security.captcha import require_captcha
from ....core.exceptions import ValidationException, SecurityException, ProcessingException
from ....core.logging import get_logger

# Initialize logger
logger = get_logger(__name__)

# Define API router for quote requests
quote_request_router = APIRouter(tags=["quote-request"])


@quote_request_router.post(
    "/",
    response_model=QuoteRequestResponseSchema,
    responses={
        400: {"model": QuoteRequestErrorSchema},
        422: {"model": QuoteRequestErrorSchema},
        500: {"model": QuoteRequestErrorSchema}
    },
    description="API endpoint for submitting quote request form data"
)
@require_captcha(threshold=0.5)
async def submit_quote_request(
    quote_data: QuoteRequestSchema,
    request: Request
) -> QuoteRequestResponseSchema:
    """
    API endpoint for submitting quote request form data.

    This endpoint receives quote request form data, validates it,
    verifies the CAPTCHA token, and processes the submission using
    the form processing service.

    Args:
        quote_data (QuoteRequestSchema): The quote request form data
        request (Request): The incoming request object

    Returns:
        QuoteRequestResponseSchema: Success response with submission ID

    Raises:
        ValidationException: If the form data fails validation
        SecurityException: If the CAPTCHA verification fails
        ProcessingException: If there is an error processing the form submission
    """
    trace_id = uuid.uuid4()
    logger.info(f"Attempting quote request form submission with trace ID: {trace_id}")

    client_ip = request.client.host

    try:
        # Process the quote request form submission
        result = form_processing_service.process_quote_request(
            form_data=quote_data.dict(),
            client_ip=client_ip,
            trace_id=trace_id
        )

        # If successful, return QuoteRequestResponseSchema with success=True, message, and submission_id
        return QuoteRequestResponseSchema(
            success=True,
            message="Quote request submitted successfully",
            submission_id=result["submission_id"]
        )

    except ValidationException as e:
        logger.warning(f"Validation error for quote request: {e.message}", extra={"trace_id": trace_id, "errors": e.details})
        raise ValidationException(message=e.message, details=e.details)

    except SecurityException as e:
        logger.warning(f"Security error for quote request: {e.message}", extra={"trace_id": trace_id, "error": e.details})
        raise SecurityException(message=e.message, details=e.details)

    except ProcessingException as e:
        logger.error(f"Processing error for quote request: {e.message}", extra={"trace_id": trace_id, "error": e.details})
        raise ProcessingException(message=e.message, details=e.details)

    except Exception as e:
        logger.exception(f"Unexpected error for quote request: {str(e)}", extra={"trace_id": trace_id})
        return JSONResponse(
            status_code=500,
            content=QuoteRequestErrorSchema(
                success=False,
                message="Internal server error",
                errors={"error": "Unexpected error"}
            ).dict()
        )