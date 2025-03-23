# src/backend/app/middlewares/__init__.py
from fastapi import FastAPI  # fastapi v0.95.0

from .cors_middleware import setup_cors  # Import CORS middleware setup function
from .error_handler import setup_error_handlers  # Import error handler setup function
from .request_logger import RequestLoggerMiddleware  # Import request logging middleware class
from .rate_limiter import setup_rate_limiting, configure_endpoint_limits  # Import rate limiting middleware setup function
from .security_middleware import setup_security_middleware  # Import security middleware setup function
from app.core.logging import get_logger  # Import logging utility

# Initialize logger
logger = get_logger(__name__)


def setup_middlewares(app: FastAPI) -> None:
    """
    Configures and applies all middleware components to the FastAPI application

    Args:
        app (fastapi.FastAPI): The FastAPI application instance

    Returns:
        None: Function performs side effects only
    """
    # Set up CORS middleware
    setup_cors(app)
    logger.debug("CORS middleware setup completed")

    # Set up error handlers
    setup_error_handlers(app)
    logger.debug("Error handlers setup completed")

    # Add request logger middleware
    app.add_middleware(RequestLoggerMiddleware)
    logger.debug("Request logger middleware added")

    # Set up rate limiting middleware
    setup_rate_limiting(app)
    logger.debug("Rate limiting middleware setup completed")

    # Set up security middleware
    setup_security_middleware(app)
    logger.debug("Security middleware setup completed")

    logger.info("All middlewares setup completed")


__all__ = [
    "setup_cors",
    "setup_error_handlers",
    "RequestLoggerMiddleware",
    "setup_rate_limiting",
    "configure_endpoint_limits",
    "setup_security_middleware",
    "setup_middlewares"
]