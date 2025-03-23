"""
Initialization file for the API package that serves as the entry point for all API-related functionality in the IndiVillage.com backend.
This file exports the main API router and essential API utilities for use throughout the application.
"""

# loguru - version: 0.6.0
from loguru import logger

# Internal imports
from .routes import api_router, include_api_routes  # Import the main API router for exporting
from .errors import APIError, APIValidationError, APINotFoundError, handle_api_error  # Import API error class for exception handling
from .validators import validate_request_body, validate_query_params, APIValidator  # Import request body validation function

# Bind logger with module name
logger = logger.bind(module='api')


def init_api():
    """
    Initializes the API module and sets up all routes
    """
    logger.info("Initializing API module")
    include_api_routes()  # Call include_api_routes to set up all API routes
    logger.info("Successfully initialized API")


# Initialize the API when this module is imported
init_api()

# Export the main API router for registration in the FastAPI application
__all__ = [
    "api_router",
    "APIError",
    "APIValidationError",
    "APINotFoundError",
    "handle_api_error",
    "validate_request_body",
    "validate_query_params",
    "APIValidator",
    "init_api"
]