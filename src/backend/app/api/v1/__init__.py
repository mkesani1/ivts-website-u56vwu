"""
Initialization file for the v1 API package that configures and exports the v1 API router.
This file serves as the central point for organizing all v1 API endpoints and provides functions to set up the routing structure for the IndiVillage.com backend.
"""

# FastAPI - ^0.95.0
from fastapi import APIRouter

# Internal imports
from .endpoints.services import services_router
from .endpoints.case_studies import case_studies_router
from .endpoints.impact_stories import impact_stories_router
from .endpoints.contact import contact_router
from .endpoints.demo_request import demo_request_router
from .endpoints.quote_request import quote_request_router
from .endpoints.uploads import uploads_router
from app.core.logging import get_logger

# Initialize logger
logger = get_logger(__name__)

# Create API router instance
api_router = APIRouter(prefix="/v1")


def setup_v1_routes():
    """
    Sets up all v1 API routes by including all endpoint routers
    """
    logger.info("Initializing v1 API routes")

    # Include the services_router with prefix '/services'
    api_router.include_router(services_router, prefix="/services")
    logger.debug("Included services router")

    # Include the case_studies_router with prefix '/case-studies'
    api_router.include_router(case_studies_router, prefix="/case-studies")
    logger.debug("Included case studies router")

    # Include the impact_stories_router with prefix '/impact-stories'
    api_router.include_router(impact_stories_router, prefix="/impact-stories")
    logger.debug("Included impact stories router")

    # Include the contact_router with prefix '/contact'
    api_router.include_router(contact_router, prefix="/contact")
    logger.debug("Included contact router")

    # Include the demo_request_router with prefix '/demo-request'
    api_router.include_router(demo_request_router, prefix="/demo-request")
    logger.debug("Included demo request router")

    # Include the quote_request_router with prefix '/quote-request'
    api_router.include_router(quote_request_router, prefix="/quote-request")
    logger.debug("Included quote request router")

    # Include the uploads_router with prefix '/uploads'
    api_router.include_router(uploads_router, prefix="/uploads")
    logger.debug("Included uploads router")

    logger.info("Successfully set up all v1 API routes")


# Set up v1 API routes
setup_v1_routes()

# Export the router
__all__ = ["api_router", "setup_v1_routes"]