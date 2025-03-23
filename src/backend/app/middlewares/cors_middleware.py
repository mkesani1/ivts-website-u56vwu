from fastapi import FastAPI  # fastapi v0.95.0
from fastapi.middleware.cors import CORSMiddleware  # fastapi v0.95.0

from app.core.config import settings, get_allowed_origins
from app.core.logging import get_logger

# Set up module logger
logger = get_logger(__name__)

def setup_cors(app: FastAPI) -> None:
    """
    Configures and applies CORS middleware to the FastAPI application
    
    This function sets up Cross-Origin Resource Sharing policies for the application,
    allowing controlled access from specified origins while maintaining security.
    It configures allowed origins, methods, headers, and credential policies.
    
    Args:
        app (fastapi.FastAPI): The FastAPI application instance
        
    Returns:
        None: Function performs side effects only
    """
    # Get allowed origins from settings
    allowed_origins = settings.get_allowed_origins()
    
    # Log configured origins for debugging
    logger.info(f"Configuring CORS middleware with allowed origins: {allowed_origins}")
    
    # Add CORSMiddleware to the application with appropriate configuration
    app.add_middleware(
        CORSMiddleware,
        # Configure allowed origins from settings
        allow_origins=allowed_origins,
        # Allow credentials for authenticated requests
        allow_credentials=True,
        # Set allowed methods (GET, POST, PUT, DELETE, OPTIONS)
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        # Set allowed headers including Content-Type, Authorization, and X-API-Key
        allow_headers=["Content-Type", "Authorization", "X-API-Key", "Accept", "Origin"],
    )
    
    # Log successful CORS middleware configuration
    logger.info("CORS middleware successfully configured")

def get_cors_config() -> dict:
    """
    Returns the CORS configuration dictionary for use in testing or external configuration
    
    This function retrieves the complete CORS configuration as a dictionary,
    which can be useful for testing, documentation, or external configuration.
    
    Returns:
        dict: CORS configuration dictionary with all settings
    """
    # Get allowed origins from settings
    allowed_origins = settings.get_allowed_origins()
    
    # Create configuration dictionary with all CORS settings
    cors_config = {
        "allow_origins": allowed_origins,
        "allow_credentials": True,
        "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "X-API-Key", "Accept", "Origin"],
    }
    
    # Return the complete configuration dictionary
    return cors_config