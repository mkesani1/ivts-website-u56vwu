# typing
from typing import Dict, List, Optional

# fastapi
from fastapi import FastAPI, Request, Response  # fastapi ^0.95.0

# starlette.middleware.base
from starlette.middleware.base import BaseHTTPMiddleware  # starlette.middleware.base ^0.26.1

# starlette.responses
from starlette.responses import Response  # starlette.responses ^0.26.1

# typing
from typing import Dict, List, Optional  # typing standard library

# Internal imports
from ..core.config import settings  # Import application configuration settings
from ..core.logging import get_logger  # Import logging utility for security-related logging
from ..core.exceptions import SecurityException  # Import security exception for handling security-related errors
from ..services.security_service import SecurityService  # Import security service for security-related functionality

# Initialize logger
logger = get_logger(__name__)

# Initialize security service
security_service = SecurityService()

# Define default CSP directives
DEFAULT_CSP_DIRECTIVES = {
    "default-src": "'self'",
    "script-src": "'self' https://www.google.com/recaptcha/ https://www.gstatic.com/recaptcha/",
    "style-src": "'self' 'unsafe-inline' https://fonts.googleapis.com",
    "img-src": "'self' data: https://www.google.com",
    "font-src": "'self' https://fonts.gstatic.com",
    "connect-src": "'self'",
    "frame-src": "'self' https://www.google.com/recaptcha/",
    "object-src": "'none'"
}


def setup_security_middleware(app: FastAPI) -> None:
    """
    Configures and applies security middleware to the FastAPI application.

    Args:
        app (fastapi.FastAPI): The FastAPI application instance.

    Returns:
        None: Function performs side effects only.
    """
    # Add SecurityMiddleware to the application
    app.add_middleware(SecurityMiddleware)
    # Log successful security middleware configuration
    logger.info("Security middleware configured for the application")


def get_csp_header(directives: Dict[str, str]) -> str:
    """
    Generates Content Security Policy header value from directives.

    Args:
        directives (Dict[str, str]): Dictionary of CSP directives.

    Returns:
        str: Formatted CSP header value.
    """
    # Initialize empty list for CSP directive strings
    csp_strings = []
    # For each directive in directives, format as 'directive-name source-list'
    for directive, source_list in directives.items():
        csp_strings.append(f"{directive} {source_list}")
    # Join all directive strings with semicolons
    csp_header = "; ".join(csp_strings)
    # Return the complete CSP header value
    return csp_header


def get_security_headers() -> Dict[str, str]:
    """
    Generates security headers for HTTP responses.

    Returns:
        Dict[str, str]: Dictionary of security headers.
    """
    # Get CSP directives from settings or use DEFAULT_CSP_DIRECTIVES
    csp_directives = settings.CSP_DIRECTIVES if hasattr(settings, 'CSP_DIRECTIVES') else DEFAULT_CSP_DIRECTIVES
    # Generate CSP header value using get_csp_header
    csp_header_value = get_csp_header(csp_directives)
    # Create dictionary with standard security headers
    headers = {
        "Content-Security-Policy": csp_header_value,
        "X-XSS-Protection": "1; mode=block",
        "X-Frame-Options": "DENY",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": "geolocation=(), microphone=(), camera=()"
    }
    # Return the headers dictionary
    return headers


class SecurityMiddleware(BaseHTTPMiddleware):
    """
    Middleware that adds security headers to HTTP responses.
    """

    def __init__(self, app):
        """
        Initialize the middleware with the ASGI application.

        Args:
            app (starlette.types.ASGIApp): The ASGI application instance.
        """
        # Call parent class constructor with app parameter
        super().__init__(app)
        # Store app reference
        self.app = app
        # Initialize security_headers using get_security_headers
        self.security_headers = get_security_headers()
        # Log middleware initialization
        logger.info("SecurityMiddleware initialized")

    async def dispatch(self, request: Request, call_next):
        """
        Process the request and add security headers to the response.

        Args:
            request (starlette.requests.Request): The incoming HTTP request.
            call_next (callable): The next middleware or endpoint in the chain.

        Returns:
            starlette.responses.Response: Response with added security headers.
        """
        # Call next middleware to get the response
        response = await call_next(request)
        # Add security headers to the response
        self.add_security_headers(response)
        # Return the modified response
        return response

    def add_security_headers(self, response: Response):
        """
        Adds security headers to an HTTP response.

        Args:
            response (starlette.responses.Response): The HTTP response object.

        Returns:
            None: Function modifies response in place.
        """
        # For each security header, add it to the response headers
        for header, value in self.security_headers.items():
            try:
                response.headers[header] = value
            except Exception as e:
                logger.error(f"Failed to set header {header}: {str(e)}")