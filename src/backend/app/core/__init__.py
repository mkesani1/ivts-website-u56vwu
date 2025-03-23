"""
Core module for the IndiVillage backend application.

This module serves as the central access point for core application services
including configuration, logging, error handling, security, and event management.
It provides initialization functionality and exports essential components needed
throughout the application.
"""

__version__ = "0.1.0"

# Import from config module
from .config import settings, load_env_vars

# Import from logging module
from .logging import (
    setup_logging, 
    get_logger, 
    log_request, 
    log_response, 
    log_error, 
    get_request_id
)

# Import from exceptions module
from .exceptions import (
    BaseAppException,
    ValidationException,
    AuthenticationException,
    AuthorizationException,
    NotFoundException,
    ConflictException,
    RateLimitException,
    FileUploadException,
    FileProcessingException,
    SecurityException,
    IntegrationException,
    DatabaseException,
    ServerException
)

# Import from errors module
from .errors import (
    handle_exception,
    validation_exception_handler,
    not_found_exception_handler,
    http_exception_handler,
    integration_exception_handler,
    generic_exception_handler
)

# Import from security module
from .security import (
    verify_password,
    get_password_hash,
    validate_password,
    create_access_token,
    decode_access_token,
    generate_secure_token
)

# Import from events module
from .events import (
    register_event_handlers,
    get_redis_cache
)

# Initialize logger for this module
logger = get_logger(__name__)

def init_app(app):
    """
    Initializes the core components of the application.
    
    This function performs the following initialization steps:
    1. Loads environment variables
    2. Sets up logging configuration
    3. Registers event handlers
    4. Registers exception handlers
    5. Logs successful initialization
    
    Args:
        app: The FastAPI application instance
    
    Returns:
        None: Function performs side effects only
    """
    # Load environment variables
    load_env_vars()
    
    # Set up logging
    setup_logging()
    
    # Register event handlers
    register_event_handlers(app)
    
    # Register exception handlers
    app.add_exception_handler(ValidationException, validation_exception_handler)
    app.add_exception_handler(NotFoundException, not_found_exception_handler)
    app.add_exception_handler(IntegrationException, integration_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
    
    # Log successful initialization
    logger.info("Core components initialized successfully")