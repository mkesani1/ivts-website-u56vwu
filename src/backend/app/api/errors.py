"""
API-specific error handling module for the IndiVillage backend application.

This module defines custom API error classes, error response formatting, and exception 
handlers for API endpoints. It extends the core error handling functionality with 
API-specific error types and handling mechanisms.
"""

from typing import Dict, Any, Optional, Type

from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.exceptions import (
    BaseAppException,
    ValidationException,
    NotFoundException,
)
from app.core.errors import format_error_response
from app.core.logging import get_logger

# Initialize logger
logger = get_logger(__name__)


class APIError(BaseAppException):
    """
    Base class for all API-specific errors.
    """
    
    def __init__(self, message: str, status_code: int, details: Optional[Dict[str, Any]] = None):
        """
        Initialize the API error with message, status code, and optional details.
        
        Args:
            message: Human-readable error message
            status_code: HTTP status code to be returned in API responses
            details: Additional error details that can be included in the response
        """
        super().__init__(message, status_code, details)
        self.message = message
        self.status_code = status_code
        self.details = details or {}
    
    def to_response(self) -> JSONResponse:
        """
        Convert the API error to a JSONResponse.
        
        Returns:
            JSONResponse with formatted error details and appropriate status code
        """
        content = format_error_response(self.message, self.status_code, self.details)
        return JSONResponse(content=content, status_code=self.status_code)


class APIValidationError(APIError):
    """
    API-specific validation error for handling request validation failures.
    """
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """
        Initialize API validation error with message and validation error details.
        
        Args:
            message: Human-readable validation error message
            details: Specific validation errors, typically field-by-field
        """
        super().__init__(message=message, status_code=422, details=details)


class APINotFoundError(APIError):
    """
    API-specific not found error for handling resource not found errors.
    """
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """
        Initialize API not found error with message and error details.
        
        Args:
            message: Human-readable not found error message
            details: Additional context about the missing resource
        """
        super().__init__(message=message, status_code=404, details=details)


class APIAuthenticationError(APIError):
    """
    API-specific authentication error for handling authentication failures.
    """
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """
        Initialize API authentication error with message and error details.
        
        Args:
            message: Human-readable authentication error message
            details: Additional context about the authentication failure
        """
        super().__init__(message=message, status_code=401, details=details)


class APIAuthorizationError(APIError):
    """
    API-specific authorization error for handling permission denied errors.
    """
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """
        Initialize API authorization error with message and error details.
        
        Args:
            message: Human-readable authorization error message
            details: Additional context about the permission issue
        """
        super().__init__(message=message, status_code=403, details=details)


class APIRateLimitError(APIError):
    """
    API-specific rate limit error for handling rate limit exceeded errors.
    """
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """
        Initialize API rate limit error with message and error details.
        
        Args:
            message: Human-readable rate limit error message
            details: Additional context about the rate limiting
        """
        super().__init__(message=message, status_code=429, details=details)


class APIServerError(APIError):
    """
    API-specific server error for handling internal server errors.
    """
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """
        Initialize API server error with message and error details.
        
        Args:
            message: Human-readable server error message
            details: Additional context about the server error
        """
        super().__init__(message=message, status_code=500, details=details)


def handle_api_error(request: Request, exc: APIError) -> JSONResponse:
    """
    Generic handler for API errors that formats and returns appropriate JSON responses.
    
    Args:
        request: FastAPI Request object
        exc: APIError exception that was raised
        
    Returns:
        JSON response with error details and appropriate status code
    """
    # Extract error details
    message = exc.message
    status_code = exc.status_code
    details = exc.details
    
    # Log the API error with request path and client info
    logger.error(
        f"API error: {message}",
        extra={
            "status_code": status_code,
            "request_path": request.url.path,
            "request_method": request.method,
            "client_host": request.client.host if request.client else "unknown",
            "details": details
        }
    )
    
    # Return the formatted JSON response
    return exc.to_response()