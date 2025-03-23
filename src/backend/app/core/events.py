"""
Core event handling module for the IndiVillage backend application.

This module manages application lifecycle events such as startup and shutdown,
registers event handlers, and provides access to shared resources like Redis cache.
It ensures proper initialization and cleanup of resources during the application lifecycle.
"""

import fastapi  # fastapi v0.95.0
import asyncio  # standard library
import contextlib  # standard library

from .config import settings  # Import application settings
from .logging import get_logger  # Import logger factory function
from ..cache.redis_cache import RedisCache  # Import Redis cache implementation
from ..extensions import initialize_extensions  # Import extensions initialization function

# Initialize logger for this module
logger = get_logger(__name__)

# Global Redis cache instance
_redis_cache = None


def get_redis_cache() -> RedisCache:
    """
    Returns the Redis cache instance, initializing it if necessary.
    
    This function provides a singleton-like access to the Redis cache,
    ensuring that only one instance is created and reused across the application.
    
    Returns:
        RedisCache: Initialized Redis cache instance
    """
    global _redis_cache
    
    if _redis_cache is None:
        # Initialize Redis cache if not already initialized
        logger.info("Initializing Redis cache instance")
        _redis_cache = RedisCache(settings.REDIS_URL)
    
    return _redis_cache


def startup_event_handler(app: fastapi.FastAPI) -> None:
    """
    Handles application startup events, initializing required resources.
    
    This function is called when the FastAPI application starts up.
    It initializes resources like Redis cache and other application extensions.
    
    Args:
        app (fastapi.FastAPI): The FastAPI application instance
    """
    logger.info("Application startup event triggered")
    
    # Initialize Redis cache
    get_redis_cache()
    
    # Initialize all application extensions
    logger.info("Initializing application extensions")
    initialize_extensions()
    
    logger.info("Application startup completed successfully")


def shutdown_event_handler(app: fastapi.FastAPI) -> None:
    """
    Handles application shutdown events, cleaning up resources.
    
    This function is called when the FastAPI application is shutting down.
    It ensures proper cleanup of resources like Redis connections.
    
    Args:
        app (fastapi.FastAPI): The FastAPI application instance
    """
    logger.info("Application shutdown event triggered")
    
    # Cleanup resources if needed
    # Redis client doesn't require explicit closing
    
    logger.info("Application shutdown completed successfully")


def register_event_handlers(app: fastapi.FastAPI) -> None:
    """
    Registers all event handlers with the FastAPI application.
    
    This function should be called during application setup to register
    the startup and shutdown event handlers.
    
    Args:
        app (fastapi.FastAPI): The FastAPI application instance
    """
    logger.info("Registering application event handlers")
    
    # Register startup event handler
    app.on_event("startup")(startup_event_handler)
    
    # Register shutdown event handler
    app.on_event("shutdown")(shutdown_event_handler)
    
    logger.info("Event handlers registered successfully")