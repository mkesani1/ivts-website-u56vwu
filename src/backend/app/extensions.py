"""
Extensions module for the IndiVillage backend application.

This module initializes and manages application extensions and external service integrations,
including database connections, Redis caching, S3 file storage, and HubSpot CRM integration.
It provides a centralized place for accessing these services throughout the application.
"""

from typing import Optional

from .core.config import settings
from .core.logging import get_logger
from .cache.redis_cache import RedisCache
from .db.session import engine, close_engine
from .integrations.aws_s3 import S3Client
from .integrations.hubspot import HubSpotClient

# Initialize logger
logger = get_logger(__name__)

# Initialize global extension instances
db = engine
redis_cache: Optional[RedisCache] = None
s3_client: Optional[S3Client] = None
hubspot_client: Optional[HubSpotClient] = None


def initialize_extensions() -> bool:
    """
    Initializes all application extensions and external service integrations.
    
    This function should be called during application startup to ensure
    all required services are properly configured and connected.
    
    Returns:
        bool: True if all extensions initialized successfully, False otherwise
    """
    global redis_cache, s3_client, hubspot_client
    
    logger.info("Initializing application extensions...")
    success = True
    
    # Initialize Redis cache if enabled
    if settings.REDIS_URL:
        try:
            redis_cache = RedisCache(settings.REDIS_URL)
            logger.info("Redis cache initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Redis cache: {str(e)}", exc_info=True)
            success = False
    else:
        logger.info("Redis cache not configured, skipping initialization")
    
    # Initialize S3 client
    try:
        s3_client = S3Client(
            region=settings.AWS_REGION,
            access_key=settings.AWS_ACCESS_KEY_ID,
            secret_key=settings.AWS_SECRET_ACCESS_KEY
        )
        logger.info("S3 client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize S3 client: {str(e)}", exc_info=True)
        success = False
    
    # Initialize HubSpot client if API key is provided
    if settings.HUBSPOT_API_KEY:
        try:
            hubspot_client = HubSpotClient(settings.HUBSPOT_API_KEY)
            logger.info("HubSpot client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize HubSpot client: {str(e)}", exc_info=True)
            success = False
    else:
        logger.info("HubSpot API key not configured, skipping initialization")
    
    # Verify database connection
    try:
        # Test database connection by executing a simple query
        with db.connect() as conn:
            conn.execute("SELECT 1")
        logger.info("Database connection verified successfully")
    except Exception as e:
        logger.error(f"Failed to verify database connection: {str(e)}", exc_info=True)
        success = False
    
    if success:
        logger.info("All extensions initialized successfully")
    else:
        logger.warning("Some extensions failed to initialize")
    
    return success


def get_redis_cache() -> Optional[RedisCache]:
    """
    Returns the initialized Redis cache instance.
    
    Returns:
        RedisCache: Initialized Redis cache instance or None if not enabled
    """
    if redis_cache is None:
        logger.warning("Redis cache requested but not initialized")
    
    return redis_cache


def get_s3_client() -> Optional[S3Client]:
    """
    Returns the initialized S3 client instance.
    
    Returns:
        S3Client: Initialized S3 client instance
    """
    if s3_client is None:
        logger.warning("S3 client requested but not initialized")
    
    return s3_client


def get_hubspot_client() -> Optional[HubSpotClient]:
    """
    Returns the initialized HubSpot client instance.
    
    Returns:
        HubSpotClient: Initialized HubSpot client instance
    """
    if hubspot_client is None:
        logger.warning("HubSpot client requested but not initialized")
    
    return hubspot_client


def cleanup_extensions() -> None:
    """
    Cleans up and closes all extension connections.
    
    This function should be called during application shutdown to ensure
    proper resource cleanup and connection handling.
    """
    logger.info("Cleaning up application extensions...")
    
    # Close database connections
    try:
        close_engine()
        logger.info("Database connections closed successfully")
    except Exception as e:
        logger.error(f"Error closing database connections: {str(e)}", exc_info=True)
    
    # Clean up Redis connections if initialized
    global redis_cache
    if redis_cache is not None:
        try:
            # Redis client doesn't require explicit closing, but we release the reference
            redis_cache = None
            logger.info("Redis connections released")
        except Exception as e:
            logger.error(f"Error cleaning up Redis connections: {str(e)}", exc_info=True)
    
    # Note: S3 and HubSpot clients don't require explicit cleanup
    # but we can set them to None to help with garbage collection
    global s3_client, hubspot_client
    s3_client = None
    hubspot_client = None
    
    logger.info("Extensions cleanup completed")