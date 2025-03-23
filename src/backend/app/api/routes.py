"""
Central router configuration for the IndiVillage.com backend API.
This file defines the main API router, includes versioned API routes, and provides functions to register all API endpoints. It serves as the entry point for all API requests and organizes the routing structure.
"""

# FastAPI - ^0.95.0
from fastapi import APIRouter

# Internal imports
from app.api.v1 import api_router as v1_router  # Import the v1 API router
from app.api.v1 import setup_v1_routes  # Import function to set up v1 API routes
from app.core.config import settings  # Import application settings
from app.core.logging import get_logger  # Import logging utility

# Initialize logger
logger = get_logger(__name__)

# Create API router instance
api_router = APIRouter(prefix=settings.API_PREFIX)


def include_api_routes():
    """
    Includes all API routes from different versions into the main API router
    """
    logger.info("Initializing API routes")

    # Call setup_v1_routes() to set up all v1 API routes
    setup_v1_routes()

    # Include the v1_router in the main api_router
    api_router.include_router(v1_router)
    logger.info("Included v1 API routes")

    logger.info("Successfully included all API routes")


def get_api_router():
    """
    Returns the configured API router for use in the main application

    Returns:
        APIRouter: Configured API router with all endpoints included
    """
    # Call include_api_routes() to ensure all routes are included
    include_api_routes()

    # Return the configured api_router
    return api_router


def setup_health_check():
    """
    Sets up a health check endpoint for monitoring and load balancers
    """
    # Add a GET endpoint at /health that returns a simple status message
    @api_router.get("/health")
    async def health_check():
        return {"status": "ok"}

    logger.info("Added health check endpoint")


def setup_api_docs():
    """
    Configures API documentation endpoints and settings
    """
    # Add a GET endpoint at /docs-info that returns API documentation information
    @api_router.get("/docs-info")
    async def docs_info():
        return {
            "title": settings.PROJECT_NAME,
            "description": "API documentation for IndiVillage AI Services",
            "version": "1.0.0"
        }

    logger.info("Configured API documentation")


# Set up health check endpoint
setup_health_check()

# Configure API documentation
setup_api_docs()

# Export the main API router for registration in the FastAPI application
__all__ = ["api_router", "include_api_routes", "get_api_router"]