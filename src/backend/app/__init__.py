"""
Initialization module for the IndiVillage backend application package.

This module sets up the application package, initializes core components,
and provides the main application factory function. It serves as the entry point
for application initialization and configuration.
"""

from fastapi import FastAPI  # fastapi v0.95.0
from typing import Any

from .core.config import settings
from .core.logging import get_logger
from .extensions import initialize_extensions

# Initialize logger for this module
logger = get_logger(__name__)

# Application version
__version__ = "1.0.0"


def initialize_app(app: FastAPI) -> bool:
    """
    Initializes the application components and extensions.

    Args:
        app: The FastAPI application instance

    Returns:
        bool: True if initialization was successful, False otherwise
    """
    logger.info("Initializing application components and extensions...")
    
    try:
        # Initialize application extensions
        success = initialize_extensions()
        
        if success:
            logger.info("Application initialization completed successfully")
        else:
            logger.warning("Application initialization completed with some issues")
        
        return success
    except Exception as e:
        logger.error(f"Error during application initialization: {str(e)}", exc_info=True)
        return False