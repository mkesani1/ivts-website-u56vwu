"""
Core exceptions module for the IndiVillage backend application.

This module defines a hierarchy of custom exception classes used throughout 
the application for consistent error handling, reporting, and API responses.
These exceptions help to provide meaningful and standardized error messages
to clients while maintaining security by not exposing sensitive information.
"""

from typing import Dict, Optional, Any


class BaseAppException(Exception):
    """
    Base exception class for all application-specific exceptions.
    
    All custom exceptions in the application should inherit from this class
    to ensure consistent error handling and response formatting.
    """
    
    def __init__(self, message: str, status_code: int, details: Optional[Dict[str, Any]] = None):
        """
        Initialize the base exception with message, status code, and optional details.
        
        Args:
            message: Human-readable error message
            status_code: HTTP status code to be returned in API responses
            details: Additional error details that can be included in the response
        """
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details or {}


class ValidationException(BaseAppException):
    """
    Exception raised for validation errors in input data.
    
    Used when request data fails validation rules, such as invalid formats,
    missing required fields, or values outside acceptable ranges.
    """
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """
        Initialize validation exception with message and validation error details.
        
        Args:
            message: Human-readable validation error message
            details: Specific validation errors, typically field-by-field
        """
        super().__init__(message=message, status_code=422, details=details)


class NotFoundException(BaseAppException):
    """
    Exception raised when a requested resource is not found.
    
    Used when a client requests a resource that doesn't exist,
    such as an invalid ID or path.
    """
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """
        Initialize not found exception with message and error details.
        
        Args:
            message: Human-readable not found error message
            details: Additional context about the missing resource
        """
        super().__init__(message=message, status_code=404, details=details)


class AuthenticationException(BaseAppException):
    """
    Exception raised for authentication errors.
    
    Used when a client fails to authenticate, such as invalid credentials,
    expired tokens, or missing authentication information.
    """
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """
        Initialize authentication exception with message and error details.
        
        Args:
            message: Human-readable authentication error message
            details: Additional context about the authentication failure
        """
        super().__init__(message=message, status_code=401, details=details)


class AuthorizationException(BaseAppException):
    """
    Exception raised for authorization errors (permission denied).
    
    Used when an authenticated client lacks the necessary permissions
    to access a resource or perform an operation.
    """
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """
        Initialize authorization exception with message and error details.
        
        Args:
            message: Human-readable authorization error message
            details: Additional context about the permission issue
        """
        super().__init__(message=message, status_code=403, details=details)


class SecurityException(BaseAppException):
    """
    Exception raised for security-related errors.
    
    Used for security policy violations, suspicious activities,
    or potential security threats detected during request processing.
    """
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """
        Initialize security exception with message and error details.
        
        Args:
            message: Human-readable security error message
            details: Additional context about the security issue
        """
        super().__init__(message=message, status_code=403, details=details)


class IntegrationException(BaseAppException):
    """
    Exception raised for errors in external service integrations.
    
    Used when there are issues communicating with external services
    like CRM systems, email providers, or third-party APIs.
    """
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None, status_code: int = 502):
        """
        Initialize integration exception with message, error details, and optional status code.
        
        Args:
            message: Human-readable integration error message
            details: Additional context about the integration failure
            status_code: HTTP status code (defaults to 502 Bad Gateway)
        """
        super().__init__(message=message, status_code=status_code, details=details)


class RateLimitException(BaseAppException):
    """
    Exception raised when rate limits are exceeded.
    
    Used when a client makes too many requests within a given time period,
    exceeding the allowed rate limits for an endpoint or resource.
    """
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """
        Initialize rate limit exception with message and error details.
        
        Args:
            message: Human-readable rate limit error message
            details: Additional context about the rate limiting
        """
        super().__init__(message=message, status_code=429, details=details)


class ConfigurationException(BaseAppException):
    """
    Exception raised for configuration errors.
    
    Used when there are issues with application configuration, such as
    missing environment variables or invalid configuration values.
    """
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """
        Initialize configuration exception with message and error details.
        
        Args:
            message: Human-readable configuration error message
            details: Additional context about the configuration issue
        """
        super().__init__(message=message, status_code=500, details=details)


class DatabaseException(BaseAppException):
    """
    Exception raised for database-related errors.
    
    Used when there are issues with database operations, such as
    connection failures, query errors, or constraint violations.
    """
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """
        Initialize database exception with message and error details.
        
        Args:
            message: Human-readable database error message
            details: Additional context about the database issue
        """
        super().__init__(message=message, status_code=500, details=details)


class FileUploadException(BaseAppException):
    """
    Exception raised for file upload errors.
    
    Used when there are issues with file uploads, such as invalid file types,
    exceeding size limits, or storage problems.
    """
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None, status_code: int = 400):
        """
        Initialize file upload exception with message, error details, and optional status code.
        
        Args:
            message: Human-readable file upload error message
            details: Additional context about the upload issue
            status_code: HTTP status code (defaults to 400 Bad Request)
        """
        super().__init__(message=message, status_code=status_code, details=details)


class FileProcessingException(BaseAppException):
    """
    Exception raised for file processing errors.
    
    Used when there are issues processing uploaded files, such as
    parsing errors, invalid content, or processing failures.
    """
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """
        Initialize file processing exception with message and error details.
        
        Args:
            message: Human-readable file processing error message
            details: Additional context about the processing issue
        """
        super().__init__(message=message, status_code=500, details=details)


class CacheException(BaseAppException):
    """
    Exception raised for caching-related errors.
    
    Used when there are issues with the caching system, such as
    connection failures, key errors, or serialization problems.
    """
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """
        Initialize cache exception with message and error details.
        
        Args:
            message: Human-readable cache error message
            details: Additional context about the caching issue
        """
        super().__init__(message=message, status_code=500, details=details)