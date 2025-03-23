"""Initialization module for the integrations package that exports client classes and functions
for external service integrations used by the IndiVillage website. This module provides a
centralized access point for AWS S3, Contentful CMS, HubSpot CRM, SendGrid email service,
and Google Analytics integrations.
"""

from .aws_s3 import S3Client, generate_presigned_post, generate_presigned_url  # version: boto3
from .contentful import ContentfulClient, get_services, get_case_studies, get_impact_stories  # version: contentful
from .hubspot import HubSpotClient, process_form_submission  # version: hubspot3
from .sendgrid import SendGridClient  # version: sendgrid
from .google_analytics import GoogleAnalyticsClient, track_form_submission, track_file_upload  # version: google-analytics-data
from ..core.config import settings  # Import application settings
from ..core.logging import get_logger  # Import logging configuration

# Initialize logger
logger = get_logger(__name__)

# Initialize S3 client
s3_client = S3Client()

# Initialize Contentful client
contentful_client = ContentfulClient()

# Initialize HubSpot client
hubspot_client = HubSpotClient()

# Initialize SendGrid client
sendgrid_client = SendGridClient()

# Initialize Google Analytics client
analytics_client = GoogleAnalyticsClient(
    settings.GOOGLE_ANALYTICS_TRACKING_ID,
    settings.GOOGLE_ANALYTICS_4_MEASUREMENT_ID,
    settings.GOOGLE_ANALYTICS_4_API_SECRET
)

# Export all the integration components
__all__ = [
    "S3Client",
    "generate_presigned_post",
    "generate_presigned_url",
    "ContentfulClient",
    "get_services",
    "get_case_studies",
    "get_impact_stories",
    "HubSpotClient",
    "process_form_submission",
    "SendGridClient",
    "GoogleAnalyticsClient",
    "track_form_submission",
    "track_file_upload",
    "s3_client",
    "contentful_client",
    "hubspot_client",
    "sendgrid_client",
    "analytics_client",
]


def get_service_by_slug(slug: str):
    """
    Retrieves a service from Contentful by its slug.

    Args:
        slug (str): The slug of the service to retrieve.

    Returns:
        The service data as a dictionary, or None if not found.
    """
    try:
        client = ContentfulClient()
        entries = client.get_entries({
            'content_type': 'service',
            'fields.slug': slug,
            'include': 2
        })
        if entries and len(entries) > 0:
            return entries[0].fields
        return None
    except Exception as e:
        logger.error(f"Error retrieving service by slug: {e}")
        return None


def get_case_study_by_slug(slug: str):
    """
    Retrieves a case study from Contentful by its slug.

    Args:
        slug (str): The slug of the case study to retrieve.

    Returns:
        The case study data as a dictionary, or None if not found.
    """
    try:
        client = ContentfulClient()
        entries = client.get_entries({
            'content_type': 'caseStudy',
            'fields.slug': slug,
            'include': 2
        })
        if entries and len(entries) > 0:
            return entries[0].fields
        return None
    except Exception as e:
        logger.error(f"Error retrieving case study by slug: {e}")
        return None


def get_impact_story_by_slug(slug: str):
    """
    Retrieves an impact story from Contentful by its slug.

    Args:
        slug (str): The slug of the impact story to retrieve.

    Returns:
        The impact story data as a dictionary, or None if not found.
    """
    try:
        client = ContentfulClient()
        entries = client.get_entries({
            'content_type': 'impactStory',
            'fields.slug': slug,
            'include': 2
        })
        if entries and len(entries) > 0:
            return entries[0].fields
        return None
    except Exception as e:
        logger.error(f"Error retrieving impact story by slug: {e}")
        return None


def track_demo_request(service_interest: str, success: bool, request_data: dict = None,
                      client_id: str = None) -> bool:
    """
    Tracks a demo request event in Google Analytics.

    Args:
        service_interest (str): The service of interest for the demo.
        success (bool): Whether the demo request was successful.
        request_data (dict, optional): Additional data about the request. Defaults to None.
        client_id (str, optional): The client ID. Defaults to None.

    Returns:
        bool: True if the event was tracked successfully, False otherwise.
    """
    return analytics_client.track_event(
        category="demo",
        action="request",
        label=service_interest,
        value=1 if success else 0,
        client_id=client_id,
        additional_params=request_data
    )


def track_quote_request(service_interest: str, success: bool, request_data: dict = None,
                       client_id: str = None) -> bool:
    """
    Tracks a quote request event in Google Analytics.

    Args:
        service_interest (str): The service of interest for the quote.
        success (bool): Whether the quote request was successful.
        request_data (dict, optional): Additional data about the request. Defaults to None.
        client_id (str, optional): The client ID. Defaults to None.

    Returns:
        bool: True if the event was tracked successfully, False otherwise.
    """
    return analytics_client.track_event(
        category="quote",
        action="request",
        label=service_interest,
        value=1 if success else 0,
        client_id=client_id,
        additional_params=request_data
    )


def get_navigation():
    """
    Retrieves the navigation structure from Contentful.

    Returns:
        The navigation data as a dictionary, or None if not found.
    """
    try:
        client = ContentfulClient()
        entries = client.get_entries({
            'content_type': 'navigation',
            'include': 3
        })
    except Exception as e:
        logger.error(f"Error retrieving navigation: {e}")
        return None
    if entries and len(entries) > 0:
        return entries[0].fields
    return None