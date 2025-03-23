"""
Core error handling module for the IndiVillage backend application.

This module provides standardized error handling functions, error response formatting,
and exception handlers for various error types. It ensures consistent error responses
across the application while maintaining security by not exposing sensitive information.
"""

from typing import Dict, Any, Optional, Union, Type
import traceback

from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi import HTTPException

from .logging import get_logger
from .exceptions import (
    BaseAppException,
    ValidationException,
    NotFoundException,
    IntegrationException,
)

# Initialize logger
logger = get_logger(__name__)

# Standard error messages for HTTP status codes
ERROR_MESSAGES = {
    "400": "Bad Request",
    "401": "Unauthorized",
    "403": "Forbidden",
    "404": "Not Found",
    "422": "Validation Error",
    "429": "Too Many Requests",
    "500": "Internal Server Error",
    "502": "Bad Gateway",
    "503": "Service Unavailable",
}


def format_error_response(
    message: str, status_code: int, details: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Formats an error response with consistent structure.
    
    Args:
        message: Error message to include in the response
        status_code: HTTP status code
        details: Additional error details
        
    Returns:
        Formatted error response dictionary
    """
    response = {
        "error": {
            "message": message or ERROR_MESSAGES.get(str(status_code), "Unknown Error"),
            "status_code": status_code,
        }
    }
    
    # Add error details if provided
    if details:
        response["error"]["details"] = details
        
    return response


def create_error_response(
    message: str, status_code: int, details: Optional[Dict[str, Any]] = None
) -> JSONResponse:
    """
    Creates a JSONResponse with formatted error details.
    
    Args:
        message: Error message to include in the response
        status_code: HTTP status code
        details: Additional error details
        
    Returns:
        JSON response with error details and appropriate status code
    """
    content = format_error_response(message, status_code, details)
    return JSONResponse(content=content, status_code=status_code)


def log_error(
    message: str,
    status_code: int,
    details: Optional[Dict[str, Any]] = None,
    exc: Optional[Exception] = None,
    request: Optional[Request] = None,
) -> None:
    """
    Logs an error with appropriate severity based on status code.
    
    Args:
        message: Error message to log
        status_code: HTTP status code to determine log level
        details: Additional error details
        exc: Exception object if available
        request: FastAPI Request object if available
    """
    # Determine log level based on status code
    log_level = "error" if status_code >= 500 else "warning"
    
    # Extract request information if available
    request_info = {}
    if request:
        request_info = {
            "path": request.url.path,
            "method": request.method,
            "client": request.client.host if request.client else "unknown",
        }
        
    # Create log context with all available information
    log_context = {
        "status_code": status_code,
        "request": request_info,
    }
    
    if details:
        log_context["details"] = details
        
    # Extract and format exception traceback if available
    if exc:
        log_context["exception_type"] = type(exc).__name__
        log_context["traceback"] = "".join(traceback.format_exception(
            type(exc), exc, exc.__traceback__
        ))
        
    # Log with appropriate level
    if log_level == "error":
        logger.error(message, extra=log_context)
    else:
        logger.warning(message, extra=log_context)


def handle_exception(request: Request, exc: Exception) -> JSONResponse:
    """
    Generic exception handler that formats and logs errors.
    
    Args:
        request: FastAPI Request object
        exc: Exception that was raised
        
    Returns:
        JSON response with error details and appropriate status code
    """
    # Extract information from BaseAppException
    if isinstance(exc, BaseAppException):
        message = exc.message
        status_code = exc.status_code
        details = exc.details
    else:
        # Generic error for unexpected exceptions
        message = "An unexpected error occurred"
        status_code = 500
        details = {}
        
    # Log the error
    log_error(message, status_code, details, exc, request)
    
    # Return formatted error response
    return create_error_response(message, status_code, details)


def validation_exception_handler(request: Request, exc: ValidationException) -> JSONResponse:
    """
    Handles validation exceptions.
    
    Args:
        request: FastAPI Request object
        exc: ValidationException that was raised
        
    Returns:
        JSON response with validation error details
    """
    log_error(
        f"Validation error: {exc.message}",
        exc.status_code,
        exc.details,
        exc,
        request
    )
    return handle_exception(request, exc)


def not_found_exception_handler(request: Request, exc: NotFoundException) -> JSONResponse:
    """
    Handles not found exceptions.
    
    Args:
        request: FastAPI Request object
        exc: NotFoundException that was raised
        
    Returns:
        JSON response with not found error details
    """
    log_error(
        f"Resource not found: {exc.message}",
        exc.status_code,
        exc.details,
        exc,
        request
    )
    return handle_exception(request, exc)


def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Handles HTTP exceptions from FastAPI.
    
    Args:
        request: FastAPI Request object
        exc: HTTPException that was raised
        
    Returns:
        JSON response with HTTP error details
    """
    message = str(exc.detail)
    status_code = exc.status_code
    headers = getattr(exc, "headers", None)
    details = {"headers": headers} if headers else None
    
    log_error(
        f"HTTP exception: {message}",
        status_code,
        details,
        exc,
        request
    )
    
    return create_error_response(message, status_code, details)


def integration_exception_handler(request: Request, exc: IntegrationException) -> JSONResponse:
    """
    Handles integration exceptions for external service errors.
    
    Args:
        request: FastAPI Request object
        exc: IntegrationException that was raised
        
    Returns:
        JSON response with integration error details
    """
    service_info = exc.details.get("service", "external service") if exc.details else "external service"
    log_error(
        f"Integration error with {service_info}: {exc.message}",
        exc.status_code,
        exc.details,
        exc,
        request
    )
    return handle_exception(request, exc)


def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handles any unhandled exceptions.
    
    Args:
        request: FastAPI Request object
        exc: Exception that was raised
        
    Returns:
        JSON response with generic error details
    """
    # Log the full error with traceback
    log_error(
        f"Unhandled exception: {str(exc)}",
        500,
        {},
        exc,
        request
    )
    
    # Create a sanitized error message that doesn't expose implementation details
    return create_error_response(
        "An unexpected error occurred. Our technical team has been notified.",
        500
    )


def request_validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Handles Pydantic validation errors from request body validation.
    
    Args:
        request: FastAPI Request object
        exc: RequestValidationError that was raised
        
    Returns:
        JSON response with validation error details
    """
    # Extract validation error details
    details = {"errors": []}
    for error in exc.errors():
        error_entry = {
            "location": error.get("loc", []),
            "message": error.get("msg", ""),
            "type": error.get("type", "")
        }
        details["errors"].append(error_entry)
    
    log_error(
        "Request validation error",
        422,
        details,
        exc,
        request
    )
    
    return create_error_response(
        "Validation error: The request data is invalid",
        422,
        details
    )