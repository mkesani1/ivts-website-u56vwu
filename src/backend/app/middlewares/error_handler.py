from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi import HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from starlette.requests import Request
from starlette.responses import Response

from ..core.logging import get_logger
from ..core.errors import (
    handle_exception,
    validation_exception_handler,
    http_exception_handler,
    request_validation_error_handler,
    integration_exception_handler,
    generic_exception_handler,
    not_found_exception_handler,
)
from ..core.exceptions import (
    BaseAppException,
    ValidationException,
    NotFoundException,
    IntegrationException,
)

# Initialize logger
logger = get_logger(__name__)

class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """
    Middleware that catches exceptions during request processing and handles them appropriately.
    
    This middleware intercepts all exceptions raised during request processing and transforms
    them into consistent, client-friendly error responses while ensuring sensitive
    information is not exposed.
    """
    
    def __init__(self, app: ASGIApp):
        """
        Initialize the middleware with the ASGI application
        
        Args:
            app: The ASGI application
        """
        super().__init__(app)
        self.app = app
        
    async def dispatch(self, request: Request, call_next):
        """
        Process the request and catch any exceptions that occur
        
        Args:
            request: The incoming request
            call_next: The next middleware or route handler
            
        Returns:
            The response from the application or an error response
        """
        try:
            # Process the request
            return await call_next(request)
        except BaseAppException as exc:
            # Handle application-specific exceptions
            return handle_exception(request, exc)
        except HTTPException as exc:
            # Handle FastAPI HTTP exceptions
            return http_exception_handler(request, exc)
        except RequestValidationError as exc:
            # Handle request validation errors
            return request_validation_error_handler(request, exc)
        except Exception as exc:
            # Handle all other exceptions with a generic handler
            # This ensures no sensitive information is leaked
            return generic_exception_handler(request, exc)


def setup_error_handlers(app: FastAPI):
    """
    Registers all exception handlers with the FastAPI application
    
    This function sets up centralized error handling for the application by registering
    appropriate handlers for different types of exceptions. This ensures consistent
    error responses across all endpoints.
    
    Args:
        app: The FastAPI application instance
    """
    # Register application-specific exception handlers
    app.add_exception_handler(BaseAppException, handle_exception)
    app.add_exception_handler(ValidationException, validation_exception_handler)
    app.add_exception_handler(NotFoundException, not_found_exception_handler)
    app.add_exception_handler(IntegrationException, integration_exception_handler)
    
    # Register FastAPI exception handlers
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, request_validation_error_handler)
    
    # Register catch-all exception handler
    app.add_exception_handler(Exception, generic_exception_handler)
    
    logger.info("Error handlers registered successfully")