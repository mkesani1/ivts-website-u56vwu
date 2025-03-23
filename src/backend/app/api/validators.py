"""
API-specific validators module for the IndiVillage backend application.

Provides FastAPI-specific validation utilities, decorators, and middleware for validating
API requests. This module extends the core validation functionality with API-specific
validation patterns and integrates with FastAPI's dependency injection system.
"""

from typing import Dict, List, Any, Optional, Callable, Type, TypeVar, Union, Generic
from fastapi import Depends, Query, Path, Body, Request
from pydantic import BaseModel, ValidationError, validator

from .errors import APIValidationError
from app.core.exceptions import ValidationException
from app.core.logging import get_logger
from app.security.input_validation import InputValidator, ValidationDecorator

# Initialize logger
logger = get_logger(__name__)


async def validate_request_body(request: Request, model_class: Type[BaseModel]) -> BaseModel:
    """
    Validates request body against a Pydantic model.
    
    Args:
        request: FastAPI request object
        model_class: Pydantic model class for validation
        
    Returns:
        Validated model instance
        
    Raises:
        APIValidationError: If validation fails
    """
    try:
        # Extract JSON body from request
        body_data = await request.json()
        
        # Validate body using the provided model class
        validated_model = model_class(**body_data)
        return validated_model
    except ValidationError as e:
        # Log validation error
        logger.warning(
            f"Request body validation failed for {model_class.__name__}",
            extra={"errors": e.errors(), "request_path": request.url.path}
        )
        # Raise API-specific validation error
        raise APIValidationError(
            message="Request body validation failed",
            details={"errors": e.errors()}
        )
    except Exception as e:
        # Log unexpected error
        logger.error(
            f"Unexpected error validating request body: {str(e)}",
            extra={"model": model_class.__name__, "request_path": request.url.path}
        )
        # Raise API-specific validation error
        raise APIValidationError(
            message="Failed to parse request body",
            details={"error": str(e)}
        )


def validate_query_params(request: Request, model_class: Type[BaseModel]) -> BaseModel:
    """
    Validates query parameters against a Pydantic model.
    
    Args:
        request: FastAPI request object
        model_class: Pydantic model class for validation
        
    Returns:
        Validated model instance
        
    Raises:
        APIValidationError: If validation fails
    """
    try:
        # Extract query parameters from request
        query_params = dict(request.query_params)
        
        # Validate query parameters using the provided model class
        validated_model = model_class(**query_params)
        return validated_model
    except ValidationError as e:
        # Log validation error
        logger.warning(
            f"Query parameter validation failed for {model_class.__name__}",
            extra={"errors": e.errors(), "request_path": request.url.path}
        )
        # Raise API-specific validation error
        raise APIValidationError(
            message="Query parameter validation failed",
            details={"errors": e.errors()}
        )
    except Exception as e:
        # Log unexpected error
        logger.error(
            f"Unexpected error validating query parameters: {str(e)}",
            extra={"model": model_class.__name__, "request_path": request.url.path}
        )
        # Raise API-specific validation error
        raise APIValidationError(
            message="Failed to parse query parameters",
            details={"error": str(e)}
        )


def validate_path_params(request: Request, model_class: Type[BaseModel]) -> BaseModel:
    """
    Validates path parameters against a Pydantic model.
    
    Args:
        request: FastAPI request object
        model_class: Pydantic model class for validation
        
    Returns:
        Validated model instance
        
    Raises:
        APIValidationError: If validation fails
    """
    try:
        # Extract path parameters from request
        path_params = dict(request.path_params)
        
        # Validate path parameters using the provided model class
        validated_model = model_class(**path_params)
        return validated_model
    except ValidationError as e:
        # Log validation error
        logger.warning(
            f"Path parameter validation failed for {model_class.__name__}",
            extra={"errors": e.errors(), "request_path": request.url.path}
        )
        # Raise API-specific validation error
        raise APIValidationError(
            message="Path parameter validation failed",
            details={"errors": e.errors()}
        )
    except Exception as e:
        # Log unexpected error
        logger.error(
            f"Unexpected error validating path parameters: {str(e)}",
            extra={"model": model_class.__name__, "request_path": request.url.path}
        )
        # Raise API-specific validation error
        raise APIValidationError(
            message="Failed to parse path parameters",
            details={"error": str(e)}
        )


def validate_form_data(form_data: Dict[str, Any], form_type: str) -> Dict[str, Any]:
    """
    Validates form data against a specific form type.
    
    Args:
        form_data: Form data dictionary to validate
        form_type: Type of form ("contact", "demo_request", "quote_request", etc.)
        
    Returns:
        Validated form data
        
    Raises:
        APIValidationError: If validation fails
    """
    try:
        # Use InputValidator from security module to validate form data
        valid, errors = InputValidator.validate_form_data(form_data, form_type)
        
        if not valid:
            # Log validation error
            logger.warning(
                f"Form validation failed for {form_type}",
                extra={"errors": errors}
            )
            # Raise API-specific validation error
            raise APIValidationError(
                message=f"{form_type.replace('_', ' ').title()} form validation failed",
                details={"errors": errors}
            )
        
        # Return validated form data
        return form_data
    except ValidationException as e:
        # Log validation error
        logger.warning(
            f"Form validation failed for {form_type}: {e.message}",
            extra={"details": e.details}
        )
        # Convert to API-specific validation error
        raise APIValidationError(
            message=e.message,
            details=e.details
        )
    except Exception as e:
        # Log unexpected error
        logger.error(
            f"Unexpected error validating form data: {str(e)}",
            extra={"form_type": form_type}
        )
        # Raise API-specific validation error
        raise APIValidationError(
            message="Failed to validate form data",
            details={"error": str(e)}
        )


class RequestValidator:
    """
    Class for validating FastAPI requests.
    """
    
    @staticmethod
    async def validate_body(request: Request, model_class: Type[BaseModel]) -> BaseModel:
        """
        Validates request body against a Pydantic model.
        
        Args:
            request: FastAPI request object
            model_class: Pydantic model class for validation
            
        Returns:
            Validated model instance
        """
        return await validate_request_body(request, model_class)
    
    @staticmethod
    def validate_query(request: Request, model_class: Type[BaseModel]) -> BaseModel:
        """
        Validates query parameters against a Pydantic model.
        
        Args:
            request: FastAPI request object
            model_class: Pydantic model class for validation
            
        Returns:
            Validated model instance
        """
        return validate_query_params(request, model_class)
    
    @staticmethod
    def validate_path(request: Request, model_class: Type[BaseModel]) -> BaseModel:
        """
        Validates path parameters against a Pydantic model.
        
        Args:
            request: FastAPI request object
            model_class: Pydantic model class for validation
            
        Returns:
            Validated model instance
        """
        return validate_path_params(request, model_class)
    
    @staticmethod
    def validate_form(form_data: Dict[str, Any], form_type: str) -> Dict[str, Any]:
        """
        Validates form data against a specific form type.
        
        Args:
            form_data: Form data dictionary to validate
            form_type: Type of form
            
        Returns:
            Validated form data
        """
        return validate_form_data(form_data, form_type)


class APIValidationDecorator:
    """
    Decorator class for adding validation to FastAPI endpoints.
    """
    
    @staticmethod
    def validate_request_body(model_class: Type[BaseModel]) -> Callable:
        """
        Decorator for validating request body against a Pydantic model.
        
        Args:
            model_class: Pydantic model class for validation
            
        Returns:
            Decorated function
        """
        def decorator(func):
            async def wrapper(request: Request, *args, **kwargs):
                # Validate request body
                validated_data = await RequestValidator.validate_body(request, model_class)
                # Call the original function with validated data
                return await func(request, validated_data=validated_data.dict(), *args, **kwargs)
            return wrapper
        return decorator
    
    @staticmethod
    def validate_query_params(model_class: Type[BaseModel]) -> Callable:
        """
        Decorator for validating query parameters against a Pydantic model.
        
        Args:
            model_class: Pydantic model class for validation
            
        Returns:
            Decorated function
        """
        def decorator(func):
            async def wrapper(request: Request, *args, **kwargs):
                # Validate query parameters
                validated_data = RequestValidator.validate_query(request, model_class)
                # Call the original function with validated data
                return await func(request, validated_query=validated_data.dict(), *args, **kwargs)
            return wrapper
        return decorator
    
    @staticmethod
    def validate_path_params(model_class: Type[BaseModel]) -> Callable:
        """
        Decorator for validating path parameters against a Pydantic model.
        
        Args:
            model_class: Pydantic model class for validation
            
        Returns:
            Decorated function
        """
        def decorator(func):
            async def wrapper(request: Request, *args, **kwargs):
                # Validate path parameters
                validated_data = RequestValidator.validate_path(request, model_class)
                # Call the original function with validated data
                return await func(request, validated_path=validated_data.dict(), *args, **kwargs)
            return wrapper
        return decorator
    
    @staticmethod
    def validate_form_submission(form_type: str) -> Callable:
        """
        Decorator for validating form submissions.
        
        Args:
            form_type: Type of form
            
        Returns:
            Decorated function
        """
        def decorator(func):
            async def wrapper(request: Request, *args, **kwargs):
                # Extract form data from request (JSON or form data)
                try:
                    if request.method in ["POST", "PUT", "PATCH"]:
                        try:
                            form_data = await request.json()
                        except:
                            # If not JSON, try form data
                            form = await request.form()
                            form_data = {key: value for key, value in form.items()}
                    else:
                        # For GET requests, use query parameters
                        form_data = dict(request.query_params)
                except Exception as e:
                    logger.error(f"Error extracting form data: {str(e)}")
                    raise APIValidationError(
                        message="Invalid form submission format",
                        details={"error": str(e)}
                    )
                
                # Validate form data
                validated_data = RequestValidator.validate_form(form_data, form_type)
                # Call the original function with validated data
                return await func(request, validated_data=validated_data, *args, **kwargs)
            return wrapper
        return decorator
    
    @staticmethod
    def require_captcha() -> Callable:
        """
        Decorator for requiring CAPTCHA verification.
        
        Returns:
            Decorated function
        """
        # Use ValidationDecorator from security module
        return ValidationDecorator.require_captcha()


T = TypeVar('T', bound=BaseModel)

class Validator(Generic[T]):
    """
    Generic validator dependency for FastAPI dependency injection.
    """
    
    def __init__(self, model_class: Type[T]):
        """
        Initializes the Validator with a model class.
        
        Args:
            model_class: Pydantic model class for validation
        """
        self.model_class = model_class
    
    async def __call__(self, request: Request) -> T:
        """
        Makes the validator callable for FastAPI dependency injection.
        
        Args:
            request: FastAPI request object
            
        Returns:
            Validated model instance
        """
        try:
            # Determine request type and extract data accordingly
            if request.method in ["POST", "PUT", "PATCH"]:
                content_type = request.headers.get("content-type", "").lower()
                
                if "application/json" in content_type:
                    # JSON data
                    data = await request.json()
                elif "multipart/form-data" in content_type or "application/x-www-form-urlencoded" in content_type:
                    # Form data
                    form = await request.form()
                    data = {key: value for key, value in form.items()}
                else:
                    # Default to JSON attempt
                    try:
                        data = await request.json()
                    except:
                        data = dict(request.query_params)
            else:
                # GET, DELETE, etc.
                data = dict(request.query_params)
            
            # Validate data against model
            validated_model = self.model_class(**data)
            return validated_model
            
        except ValidationError as e:
            # Log validation error
            logger.warning(
                f"Validation failed for {self.model_class.__name__}",
                extra={"errors": e.errors(), "request_path": request.url.path}
            )
            # Raise API-specific validation error
            raise APIValidationError(
                message="Validation failed",
                details={"errors": e.errors()}
            )
        except Exception as e:
            # Log unexpected error
            logger.error(
                f"Unexpected error in validator: {str(e)}",
                extra={"model": self.model_class.__name__, "request_path": request.url.path}
            )
            # Raise API-specific validation error
            raise APIValidationError(
                message="Validation error occurred",
                details={"error": str(e)}
            )