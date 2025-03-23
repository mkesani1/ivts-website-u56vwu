"""
Initialization file for the API endpoints package that exports all endpoint routers for the IndiVillage.com backend.
This file serves as a central point for organizing and exposing all API endpoint modules to be included in the v1 API router.
"""

# Import the APIRouter from FastAPI
from fastapi import APIRouter

# Import internal modules for different API endpoints
from .services import services_router  # Import the services router to expose service-related endpoints
from .case_studies import case_studies_router  # Import the case studies router to expose case study-related endpoints
from .impact_stories import impact_stories_router  # Import the impact stories router to expose impact story-related endpoints
from .contact import router as contact_router  # Import the contact router to expose contact form endpoints
from .demo_request import demo_request_router  # Import the demo request router to expose demo request form endpoints
from .quote_request import quote_request_router  # Import the quote request router to expose quote request form endpoints
from .uploads import router as uploads_router  # Import the uploads router to expose file upload endpoints

# Import logging utility for endpoint package logging
from app.core.logging import get_logger

# Initialize logger for this module
logger = get_logger(__name__)

# __all__ defines the public API of the module
__all__ = [
    "services_router",
    "case_studies_router",
    "impact_stories_router",
    "contact_router",
    "demo_request_router",
    "quote_request_router",
    "uploads_router",
]