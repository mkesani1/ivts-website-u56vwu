import json
import datetime
from typing import Dict, List, Optional, Any, Union

from ..core.logging import get_logger  # Import get_logger function from ..core.logging - version: N/A
from ..core.events import get_redis_cache  # Import get_redis_cache function from ..core.events - version: N/A
from ..cache.decorators import cached  # Import cached decorator from ..cache.decorators - version: N/A
from ..integrations.contentful import ContentfulClient  # Import ContentfulClient class from ..integrations.contentful - version: N/A
from ..integrations.contentful import get_service_by_slug, get_services, get_case_studies, get_case_study_by_slug, get_impact_stories, get_impact_story_by_slug, get_navigation, get_page_by_slug, invalidate_content_cache  # Import functions from ..integrations.contentful - version: N/A

# Initialize logger for this module
logger = get_logger(__name__)

# Constants for cache configuration
CONTENT_CACHE_TTL = 3600  # Time-to-live for cached content in seconds
CONTENT_CACHE_PREFIX = 'content:'  # Prefix for cache keys to avoid collisions


def get_all_services() -> List[Dict[str, Any]]:
    """
    Retrieves all services with caching.

    Returns:
        List[Dict[str, Any]]: List of service objects
    """
    # Call get_services() from contentful integration
    try:
        services = get_services()
        return services
    except Exception as e:
        # Log any errors that occur during retrieval
        logger.error(f"Error retrieving all services: {e}")
        # Return the list of services or empty list on error
        return []


def get_service(slug: str) -> Optional[Dict[str, Any]]:
    """
    Retrieves a specific service by slug with caching.

    Args:
        slug (str): Service slug

    Returns:
        Optional[Dict[str, Any]]: Service object or None if not found
    """
    # Validate slug parameter
    if not isinstance(slug, str):
        logger.error(f"Invalid slug type: {type(slug)}")
        return None

    # Call get_service_by_slug(slug) from contentful integration
    try:
        service = get_service_by_slug(slug)
        return service
    except Exception as e:
        # Log any errors that occur during retrieval
        logger.error(f"Error retrieving service by slug: {e}")
        # Return the service object or None if not found or on error
        return None


def get_all_case_studies(industry_slug: str = None, service_slug: str = None) -> List[Dict[str, Any]]:
    """
    Retrieves all case studies with optional filtering by industry or service.

    Args:
        industry_slug (str, optional): Industry slug. Defaults to None.
        service_slug (str, optional): Service slug. Defaults to None.

    Returns:
        List[Dict[str, Any]]: List of case study objects
    """
    # Call get_case_studies(industry_slug, service_slug) from contentful integration
    try:
        case_studies = get_case_studies(industry_slug, service_slug)
        return case_studies
    except Exception as e:
        # Log any errors that occur during retrieval
        logger.error(f"Error retrieving all case studies: {e}")
        # Return the list of case studies or empty list on error
        return []


def get_case_study(slug: str) -> Optional[Dict[str, Any]]:
    """
    Retrieves a specific case study by slug with caching.

    Args:
        slug (str): Case study slug

    Returns:
        Optional[Dict[str, Any]]: Case study object or None if not found
    """
    # Validate slug parameter
    if not isinstance(slug, str):
        logger.error(f"Invalid slug type: {type(slug)}")
        return None

    # Call get_case_study_by_slug(slug) from contentful integration
    try:
        case_study = get_case_study_by_slug(slug)
        return case_study
    except Exception as e:
        # Log any errors that occur during retrieval
        logger.error(f"Error retrieving case study by slug: {e}")
        # Return the case study object or None if not found or on error
        return None


def get_all_impact_stories() -> List[Dict[str, Any]]:
    """
    Retrieves all impact stories with caching.

    Returns:
        List[Dict[str, Any]]: List of impact story objects
    """
    # Call get_impact_stories() from contentful integration
    try:
        impact_stories = get_impact_stories()
        return impact_stories
    except Exception as e:
        # Log any errors that occur during retrieval
        logger.error(f"Error retrieving all impact stories: {e}")
        # Return the list of impact stories or empty list on error
        return []


def get_impact_story(slug: str) -> Optional[Dict[str, Any]]:
    """
    Retrieves a specific impact story by slug with caching.

    Args:
        slug (str): Impact story slug

    Returns:
        Optional[Dict[str, Any]]: Impact story object or None if not found
    """
    # Validate slug parameter
    if not isinstance(slug, str):
        logger.error(f"Invalid slug type: {type(slug)}")
        return None

    # Call get_impact_story_by_slug(slug) from contentful integration
    try:
        impact_story = get_impact_story_by_slug(slug)
        return impact_story
    except Exception as e:
        # Log any errors that occur during retrieval
        logger.error(f"Error retrieving impact story by slug: {e}")
        # Return the impact story object or None if not found or on error
        return None


def get_site_navigation() -> Dict[str, Any]:
    """
    Retrieves the website navigation structure with caching.

    Returns:
        Dict[str, Any]]: Navigation structure object
    """
    # Call get_navigation() from contentful integration
    try:
        navigation = get_navigation()
        return navigation
    except Exception as e:
        # Log any errors that occur during retrieval
        logger.error(f"Error retrieving site navigation: {e}")
        # Return the navigation object or empty dict on error
        return {}


def get_page(slug: str) -> Optional[Dict[str, Any]]:
    """
    Retrieves a specific page by slug with caching.

    Args:
        slug (str): Page slug

    Returns:
        Optional[Dict[str, Any]]: Page object or None if not found
    """
    # Validate slug parameter
    if not isinstance(slug, str):
        logger.error(f"Invalid slug type: {type(slug)}")
        return None

    # Call get_page_by_slug(slug) from contentful integration
    try:
        page = get_page_by_slug(slug)
        return page
    except Exception as e:
        # Log any errors that occur during retrieval
        logger.error(f"Error retrieving page by slug: {e}")
        # Return the page object or None if not found or on error
        return None


def refresh_content(content_type: str, slug: str = None) -> bool:
    """
    Refreshes content cache for specific content type or entry.

    Args:
        content_type (str): Type of content (service, case_study, impact_story, navigation, page)
        slug (str, optional): Slug of the content entry. Defaults to None.

    Returns:
        bool: True if cache was successfully refreshed
    """
    # Validate content_type parameter (must be one of: service, case_study, impact_story, navigation, page)
    allowed_content_types = ["service", "case_study", "impact_story", "navigation", "page"]
    if content_type not in allowed_content_types:
        logger.error(f"Invalid content type: {content_type}")
        return False

    # Call invalidate_content_cache(content_type, slug) from contentful integration
    try:
        invalidate_content_cache(content_type, slug)
        logger.info(f"Successfully invalidated cache for content type: {content_type}, slug: {slug}")
        # Log cache invalidation result
        return True
    except Exception as e:
        logger.error(f"Error refreshing content: {e}")
        # Return False if not successful
        return False


def get_related_services(case_study: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Retrieves services related to a case study.

    Args:
        case_study (Dict[str, Any]): Case study object

    Returns:
        List[Dict[str, Any]]: List of related service objects
    """
    # Extract service IDs from case_study object
    service_ids = [service['id'] for service in case_study.get('services', [])]

    # Get all services using get_all_services()
    all_services = get_all_services()

    # Filter services to include only those related to the case study
    related_services = [service for service in all_services if service['id'] in service_ids]

    # Return the filtered list of services
    return related_services


def get_related_case_studies(service: Dict[str, Any], limit: int = 5) -> List[Dict[str, Any]]:
    """
    Retrieves case studies related to a service.

    Args:
        service (Dict[str, Any]): Service object
        limit (int, optional): Maximum number of case studies to return. Defaults to 5.

    Returns:
        List[Dict[str, Any]]: List of related case study objects
    """
    # Get all case studies for the service using get_all_case_studies(service_slug=service['slug'])
    all_case_studies = get_all_case_studies(service_slug=service['slug'])

    # If limit is provided, return only the specified number of case studies
    if limit and len(all_case_studies) > limit:
        return all_case_studies[:limit]

    # Return the list of related case studies
    return all_case_studies


def get_content_cache_key(content_type: str, slug: str = None) -> str:
    """
    Generates a cache key for content items.

    Args:
        content_type (str): Type of content (service, case_study, impact_story, navigation, page)
        slug (str, optional): Slug of the content entry. Defaults to None.

    Returns:
        str: Cache key string
    """
    # Combine CONTENT_CACHE_PREFIX with content_type
    cache_key = CONTENT_CACHE_PREFIX + content_type

    # If slug is provided, append it to the key
    if slug:
        cache_key += ":" + slug

    # Return the complete cache key
    return cache_key


class ContentService:
    """
    Service class for accessing and managing content from Contentful CMS.
    """

    def __init__(self):
        """
        Initializes the ContentService with a Contentful client.
        """
        # Initialize _contentful_client as a new ContentfulClient instance
        self._contentful_client = ContentfulClient()
        # Log successful initialization
        logger.info("ContentService initialized successfully")

    def get_services(self) -> List[Dict[str, Any]]:
        """
        Retrieves all services.

        Returns:
            List[Dict[str, Any]]: List of service objects
        """
        # Call get_all_services() function
        services = get_all_services()
        # Return the list of services
        return services

    def get_service_by_slug(self, slug: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a specific service by slug.

        Args:
            slug (str): Service slug

        Returns:
            Optional[Dict[str, Any]]: Service object or None if not found
        """
        # Call get_service(slug) function
        service = get_service(slug)
        # Return the service object
        return service

    def get_case_studies(self, industry_slug: str = None, service_slug: str = None) -> List[Dict[str, Any]]:
        """
        Retrieves case studies with optional filtering.

        Args:
            industry_slug (str, optional): Industry slug. Defaults to None.
            service_slug (str, optional): Service slug. Defaults to None.

        Returns:
            List[Dict[str, Any]]: List of case study objects
        """
        # Call get_all_case_studies(industry_slug, service_slug) function
        case_studies = get_all_case_studies(industry_slug, service_slug)
        # Return the list of case studies
        return case_studies

    def get_case_study_by_slug(self, slug: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a specific case study by slug.

        Args:
            slug (str): Case study slug

        Returns:
            Optional[Dict[str, Any]]: Case study object or None if not found
        """
        # Call get_case_study(slug) function
        case_study = get_case_study(slug)
        # Return the case study object
        return case_study

    def get_impact_stories(self) -> List[Dict[str, Any]]:
        """
        Retrieves all impact stories.

        Returns:
            List[Dict[str, Any]]: List of impact story objects
        """
        # Call get_all_impact_stories() function
        impact_stories = get_all_impact_stories()
        # Return the list of impact stories
        return impact_stories

    def get_impact_story_by_slug(self, slug: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a specific impact story by slug.

        Args:
            slug (str): Impact story slug

        Returns:
            Optional[Dict[str, Any]]: Impact story object or None if not found
        """
        # Call get_impact_story(slug) function
        impact_story = get_impact_story(slug)
        # Return the impact story object
        return impact_story

    def get_navigation(self) -> Dict[str, Any]:
        """
        Retrieves the website navigation structure.

        Returns:
            Dict[str, Any]]: Navigation structure object
        """
        # Call get_site_navigation() function
        navigation = get_site_navigation()
        # Return the navigation object
        return navigation

    def get_page_by_slug(self, slug: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a specific page by slug.

        Args:
            slug (str): Page slug

        Returns:
            Optional[Dict[str, Any]]: Page object or None if not found
        """
        # Call get_page(slug) function
        page = get_page(slug)
        # Return the page object
        return page

    def refresh_content_cache(self, content_type: str, slug: str = None) -> bool:
        """
        Refreshes content cache for specific content type or entry.

        Args:
            content_type (str): Type of content (service, case_study, impact_story, navigation, page)
            slug (str, optional): Slug of the content entry. Defaults to None.

        Returns:
            bool: True if cache was successfully refreshed
        """
        # Call refresh_content(content_type, slug) function
        result = refresh_content(content_type, slug)
        # Return the result
        return result

    def get_related_services_for_case_study(self, case_study: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Retrieves services related to a case study.

        Args:
            case_study (Dict[str, Any]): Case study object

        Returns:
            List[Dict[str, Any]]: List of related service objects
        """
        # Call get_related_services(case_study) function
        services = get_related_services(case_study)
        # Return the list of related services
        return services

    def get_related_case_studies_for_service(self, service: Dict[str, Any], limit: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieves case studies related to a service.

        Args:
            service (Dict[str, Any]): Service object
            limit (int, optional): Maximum number of case studies to return. Defaults to 5.

        Returns:
            List[Dict[str, Any]]: List of related case study objects
        """
        # Call get_related_case_studies(service, limit) function
        case_studies = get_related_case_studies(service, limit)
        # Return the list of related case studies
        return case_studies

# Example usage (not part of the service class)
# if __name__ == "__main__":
#     content_service = ContentService()
#     services = content_service.get_services()
#     print(f"Services: {services}")