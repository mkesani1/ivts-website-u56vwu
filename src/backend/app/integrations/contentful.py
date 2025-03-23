"""
Integration module for Contentful CMS.

This module provides functions to fetch and manage content from Contentful headless CMS for the
IndiVillage website. It handles content retrieval, caching, and transformation for various content
types including services, case studies, impact stories, and navigation structures.
"""

import json
import datetime
from typing import Dict, List, Optional, Any, Union

import contentful  # contentful ^2.6.0
import contentful_management  # contentful-management ^2.11.0

from ..core.config import settings
from ..core.logging import get_logger
from ..core.events import get_redis_cache
from ..cache.decorators import cached

# Initialize logger
logger = get_logger(__name__)

# Cache configuration
CACHE_TTL = 3600  # Default TTL for cached content (1 hour)
CONTENT_CACHE_PREFIX = 'contentful:'

# Global client instances for singleton pattern
_delivery_client = None
_management_client = None


def get_delivery_client() -> contentful.Client:
    """
    Returns a singleton instance of the Contentful Delivery API client.
    
    Returns:
        contentful.Client: Initialized Contentful Delivery API client
    
    Raises:
        RuntimeError: If CONTENTFUL_SPACE_ID or CONTENTFUL_ACCESS_TOKEN is not configured
    """
    global _delivery_client
    
    if _delivery_client is None:
        # Validate required settings
        if not settings.CONTENTFUL_SPACE_ID or not settings.CONTENTFUL_ACCESS_TOKEN:
            logger.error("Contentful credentials not configured")
            raise RuntimeError(
                "Contentful Delivery API requires CONTENTFUL_SPACE_ID and CONTENTFUL_ACCESS_TOKEN"
            )
        
        # Initialize the client
        logger.info("Initializing Contentful Delivery API client")
        _delivery_client = contentful.Client(
            space_id=settings.CONTENTFUL_SPACE_ID,
            access_token=settings.CONTENTFUL_ACCESS_TOKEN,
            environment=settings.ENVIRONMENT or 'master',
            max_rate_limit_retries=3
        )
    
    return _delivery_client


def get_management_client() -> contentful_management.Client:
    """
    Returns a singleton instance of the Contentful Management API client.
    
    Returns:
        contentful_management.Client: Initialized Contentful Management API client
    
    Raises:
        RuntimeError: If CONTENTFUL_MANAGEMENT_TOKEN is not configured
    """
    global _management_client
    
    if _management_client is None:
        # Validate required settings
        if not settings.CONTENTFUL_MANAGEMENT_TOKEN:
            logger.error("Contentful management token not configured")
            raise RuntimeError("Contentful Management API requires CONTENTFUL_MANAGEMENT_TOKEN")
        
        # Initialize the client
        logger.info("Initializing Contentful Management API client")
        _management_client = contentful_management.Client(
            settings.CONTENTFUL_MANAGEMENT_TOKEN
        )
    
    return _management_client


@cached(ttl=CACHE_TTL)
def get_services() -> List[Dict[str, Any]]:
    """
    Retrieves all services from Contentful.
    
    Returns:
        List[Dict[str, Any]]: List of service entries
    """
    try:
        logger.info("Retrieving all services from Contentful")
        client = get_delivery_client()
        
        # Query services with include level 2 to get linked entries
        entries = client.entries({
            'content_type': 'service',
            'include': 2
        })
        
        # Transform entries to standardized format
        services = [_transform_service_entry(entry) for entry in entries]
        
        # Sort services by order field
        services.sort(key=lambda x: x.get('order', 999))
        
        logger.info(f"Retrieved {len(services)} services from Contentful")
        return services
    except Exception as e:
        logger.error(f"Error retrieving services from Contentful: {str(e)}", exc_info=True)
        return []


@cached(ttl=CACHE_TTL)
def get_service_by_slug(slug: str) -> Optional[Dict[str, Any]]:
    """
    Retrieves a specific service by its slug.
    
    Args:
        slug: Service slug identifier
        
    Returns:
        Dict[str, Any]: Service data or None if not found
    """
    try:
        logger.info(f"Retrieving service with slug '{slug}' from Contentful")
        client = get_delivery_client()
        
        # Query services with the specific slug
        entries = client.entries({
            'content_type': 'service',
            'fields.slug': slug,
            'include': 2  # Include linked entries up to 2 levels deep
        })
        
        # Check if any service was found
        if entries and len(entries) > 0:
            service = _transform_service_entry(entries[0])
            logger.info(f"Retrieved service '{service.get('title')}' with slug '{slug}'")
            return service
        
        logger.warning(f"No service found with slug '{slug}'")
        return None
    except Exception as e:
        logger.error(f"Error retrieving service by slug '{slug}': {str(e)}", exc_info=True)
        return None


@cached(ttl=CACHE_TTL)
def get_case_studies(industry_slug: str = None, service_slug: str = None) -> List[Dict[str, Any]]:
    """
    Retrieves all case studies, optionally filtered by industry or service.
    
    Args:
        industry_slug: Optional industry slug to filter by
        service_slug: Optional service slug to filter by
        
    Returns:
        List[Dict[str, Any]]: List of case study entries
    """
    try:
        logger.info("Retrieving case studies from Contentful")
        client = get_delivery_client()
        
        # Base query parameters
        query_params = {
            'content_type': 'caseStudy',
            'include': 2  # Include linked entries up to 2 levels deep
        }
        
        # Add industry filter if provided
        if industry_slug:
            logger.info(f"Filtering case studies by industry slug '{industry_slug}'")
            query_params['fields.industry.sys.contentType.sys.id'] = 'industry'
            query_params['fields.industry.fields.slug'] = industry_slug
        
        # Add service filter if provided
        if service_slug:
            logger.info(f"Filtering case studies by service slug '{service_slug}'")
            query_params['fields.services.sys.contentType.sys.id'] = 'service'
            query_params['fields.services.fields.slug'] = service_slug
        
        # Execute query
        entries = client.entries(query_params)
        
        # Transform entries to standardized format
        case_studies = [_transform_case_study_entry(entry) for entry in entries]
        
        logger.info(f"Retrieved {len(case_studies)} case studies from Contentful")
        return case_studies
    except Exception as e:
        logger.error(f"Error retrieving case studies from Contentful: {str(e)}", exc_info=True)
        return []


@cached(ttl=CACHE_TTL)
def get_case_study_by_slug(slug: str) -> Optional[Dict[str, Any]]:
    """
    Retrieves a specific case study by its slug.
    
    Args:
        slug: Case study slug identifier
        
    Returns:
        Dict[str, Any]: Case study data or None if not found
    """
    try:
        logger.info(f"Retrieving case study with slug '{slug}' from Contentful")
        client = get_delivery_client()
        
        # Query case studies with the specific slug
        entries = client.entries({
            'content_type': 'caseStudy',
            'fields.slug': slug,
            'include': 2  # Include linked entries up to 2 levels deep
        })
        
        # Check if any case study was found
        if entries and len(entries) > 0:
            case_study = _transform_case_study_entry(entries[0])
            logger.info(f"Retrieved case study '{case_study.get('title')}' with slug '{slug}'")
            return case_study
        
        logger.warning(f"No case study found with slug '{slug}'")
        return None
    except Exception as e:
        logger.error(f"Error retrieving case study by slug '{slug}': {str(e)}", exc_info=True)
        return None


@cached(ttl=CACHE_TTL)
def get_impact_stories() -> List[Dict[str, Any]]:
    """
    Retrieves all impact stories from Contentful.
    
    Returns:
        List[Dict[str, Any]]: List of impact story entries
    """
    try:
        logger.info("Retrieving impact stories from Contentful")
        client = get_delivery_client()
        
        # Query impact stories
        entries = client.entries({
            'content_type': 'impactStory',
            'include': 2  # Include linked entries up to 2 levels deep
        })
        
        # Transform entries to standardized format
        impact_stories = [_transform_impact_story_entry(entry) for entry in entries]
        
        logger.info(f"Retrieved {len(impact_stories)} impact stories from Contentful")
        return impact_stories
    except Exception as e:
        logger.error(f"Error retrieving impact stories from Contentful: {str(e)}", exc_info=True)
        return []


@cached(ttl=CACHE_TTL)
def get_impact_story_by_slug(slug: str) -> Optional[Dict[str, Any]]:
    """
    Retrieves a specific impact story by its slug.
    
    Args:
        slug: Impact story slug identifier
        
    Returns:
        Dict[str, Any]: Impact story data or None if not found
    """
    try:
        logger.info(f"Retrieving impact story with slug '{slug}' from Contentful")
        client = get_delivery_client()
        
        # Query impact stories with the specific slug
        entries = client.entries({
            'content_type': 'impactStory',
            'fields.slug': slug,
            'include': 2  # Include linked entries up to 2 levels deep
        })
        
        # Check if any impact story was found
        if entries and len(entries) > 0:
            impact_story = _transform_impact_story_entry(entries[0])
            logger.info(f"Retrieved impact story '{impact_story.get('title')}' with slug '{slug}'")
            return impact_story
        
        logger.warning(f"No impact story found with slug '{slug}'")
        return None
    except Exception as e:
        logger.error(f"Error retrieving impact story by slug '{slug}': {str(e)}", exc_info=True)
        return None


@cached(ttl=CACHE_TTL)
def get_navigation() -> Dict[str, Any]:
    """
    Retrieves the main navigation structure from Contentful.
    
    Returns:
        Dict[str, Any]: Navigation structure data
    """
    try:
        logger.info("Retrieving navigation structure from Contentful")
        client = get_delivery_client()
        
        # Query navigation entries
        entries = client.entries({
            'content_type': 'navigation',
            'include': 3  # Include deeply nested items
        })
        
        # Check if any navigation was found
        if entries and len(entries) > 0:
            navigation = _transform_navigation_entry(entries[0])
            logger.info(f"Retrieved navigation structure with {len(navigation.get('items', []))} items")
            return navigation
        
        logger.warning("No navigation structure found in Contentful")
        return {}
    except Exception as e:
        logger.error(f"Error retrieving navigation from Contentful: {str(e)}", exc_info=True)
        return {}


@cached(ttl=CACHE_TTL)
def get_page_by_slug(slug: str) -> Optional[Dict[str, Any]]:
    """
    Retrieves a specific page by its slug.
    
    Args:
        slug: Page slug identifier
        
    Returns:
        Dict[str, Any]: Page data or None if not found
    """
    try:
        logger.info(f"Retrieving page with slug '{slug}' from Contentful")
        client = get_delivery_client()
        
        # Query pages with the specific slug
        entries = client.entries({
            'content_type': 'page',
            'fields.slug': slug,
            'include': 3  # Include deeply nested content
        })
        
        # Check if any page was found
        if entries and len(entries) > 0:
            page = _transform_page_entry(entries[0])
            logger.info(f"Retrieved page '{page.get('title')}' with slug '{slug}'")
            return page
        
        logger.warning(f"No page found with slug '{slug}'")
        return None
    except Exception as e:
        logger.error(f"Error retrieving page by slug '{slug}': {str(e)}", exc_info=True)
        return None


def invalidate_content_cache(content_type: str, slug: str = None) -> bool:
    """
    Invalidates the cache for specific content or content type.
    
    Args:
        content_type: Type of content (e.g., 'service', 'caseStudy')
        slug: Optional specific slug to invalidate
        
    Returns:
        bool: True if cache was invalidated successfully
    """
    try:
        logger.info(f"Invalidating cache for content type '{content_type}'" + 
                   (f" with slug '{slug}'" if slug else ""))
        
        cache = get_redis_cache()
        if not cache:
            logger.warning("Cache not available, skipping invalidation")
            return False
        
        # Construct cache key pattern
        if slug:
            pattern = _get_cache_key(content_type, slug)
        else:
            pattern = _get_cache_key(content_type, "*")
        
        # Delete matching cache entries
        deleted_count = cache.delete_pattern(pattern)
        
        logger.info(f"Invalidated {deleted_count} cache entries")
        return True
    except Exception as e:
        logger.error(f"Error invalidating cache: {str(e)}", exc_info=True)
        return False


def _transform_service_entry(entry: contentful.Entry) -> Dict[str, Any]:
    """
    Transforms a Contentful service entry into a standardized format.
    
    Args:
        entry: Contentful Entry object
        
    Returns:
        Dict[str, Any]: Transformed service data
    """
    if not entry or not hasattr(entry, 'fields'):
        return {}
    
    try:
        # Extract basic fields
        result = {
            'id': entry.sys.get('id', ''),
            'title': entry.fields.get('title', ''),
            'slug': entry.fields.get('slug', ''),
            'description': entry.fields.get('description', ''),
            'icon': entry.fields.get('icon', ''),
            'order': entry.fields.get('order', 999),
            'content_type': 'service'
        }
        
        # Extract and transform features
        features = []
        if 'features' in entry.fields and entry.fields['features']:
            for feature in entry.fields['features']:
                features.append({
                    'title': feature.fields.get('title', ''),
                    'description': feature.fields.get('description', '')
                })
        result['features'] = features
        
        # Extract related case studies
        case_studies = []
        if 'caseStudies' in entry.fields and entry.fields['caseStudies']:
            for case_study in entry.fields['caseStudies']:
                case_studies.append({
                    'id': case_study.sys.get('id', ''),
                    'title': case_study.fields.get('title', ''),
                    'slug': case_study.fields.get('slug', '')
                })
        result['case_studies'] = case_studies
        
        # Extract media assets
        media = []
        if 'media' in entry.fields and entry.fields['media']:
            for asset in entry.fields['media']:
                if hasattr(asset, 'fields'):
                    media.append(_transform_asset(asset))
        result['media'] = media
        
        return result
    except Exception as e:
        logger.error(f"Error transforming service entry: {str(e)}", exc_info=True)
        return {'id': entry.sys.get('id', ''), 'error': str(e)}


def _transform_case_study_entry(entry: contentful.Entry) -> Dict[str, Any]:
    """
    Transforms a Contentful case study entry into a standardized format.
    
    Args:
        entry: Contentful Entry object
        
    Returns:
        Dict[str, Any]: Transformed case study data
    """
    if not entry or not hasattr(entry, 'fields'):
        return {}
    
    try:
        # Extract basic fields
        result = {
            'id': entry.sys.get('id', ''),
            'title': entry.fields.get('title', ''),
            'slug': entry.fields.get('slug', ''),
            'client': entry.fields.get('client', ''),
            'challenge': entry.fields.get('challenge', ''),
            'solution': entry.fields.get('solution', ''),
            'content_type': 'caseStudy'
        }
        
        # Extract industry if present
        if 'industry' in entry.fields and entry.fields['industry']:
            industry = entry.fields['industry']
            result['industry'] = {
                'id': industry.sys.get('id', ''),
                'name': industry.fields.get('name', ''),
                'slug': industry.fields.get('slug', '')
            }
        
        # Extract and transform results
        results = []
        if 'results' in entry.fields and entry.fields['results']:
            for result_item in entry.fields['results']:
                results.append({
                    'metric': result_item.fields.get('metric', ''),
                    'value': result_item.fields.get('value', ''),
                    'description': result_item.fields.get('description', '')
                })
        result['results'] = results
        
        # Extract related services
        services = []
        if 'services' in entry.fields and entry.fields['services']:
            for service in entry.fields['services']:
                services.append({
                    'id': service.sys.get('id', ''),
                    'title': service.fields.get('title', ''),
                    'slug': service.fields.get('slug', '')
                })
        result['services'] = services
        
        # Extract media assets
        media = []
        if 'media' in entry.fields and entry.fields['media']:
            for asset in entry.fields['media']:
                if hasattr(asset, 'fields'):
                    media.append(_transform_asset(asset))
        result['media'] = media
        
        return result
    except Exception as e:
        logger.error(f"Error transforming case study entry: {str(e)}", exc_info=True)
        return {'id': entry.sys.get('id', ''), 'error': str(e)}


def _transform_impact_story_entry(entry: contentful.Entry) -> Dict[str, Any]:
    """
    Transforms a Contentful impact story entry into a standardized format.
    
    Args:
        entry: Contentful Entry object
        
    Returns:
        Dict[str, Any]: Transformed impact story data
    """
    if not entry or not hasattr(entry, 'fields'):
        return {}
    
    try:
        # Extract basic fields
        result = {
            'id': entry.sys.get('id', ''),
            'title': entry.fields.get('title', ''),
            'slug': entry.fields.get('slug', ''),
            'story': entry.fields.get('story', ''),
            'beneficiaries': entry.fields.get('beneficiaries', ''),
            'content_type': 'impactStory'
        }
        
        # Extract location if present
        if 'location' in entry.fields and entry.fields['location']:
            location = entry.fields['location']
            result['location'] = {
                'id': location.sys.get('id', ''),
                'name': location.fields.get('name', ''),
                'region': location.fields.get('region', ''),
                'country': location.fields.get('country', '')
            }
        
        # Extract and transform metrics
        metrics = []
        if 'metrics' in entry.fields and entry.fields['metrics']:
            for metric in entry.fields['metrics']:
                metrics.append({
                    'name': metric.fields.get('metricName', ''),
                    'value': metric.fields.get('value', ''),
                    'unit': metric.fields.get('unit', '')
                })
        result['metrics'] = metrics
        
        # Extract media assets
        media = []
        if 'media' in entry.fields and entry.fields['media']:
            for asset in entry.fields['media']:
                if hasattr(asset, 'fields'):
                    media.append(_transform_asset(asset))
        result['media'] = media
        
        return result
    except Exception as e:
        logger.error(f"Error transforming impact story entry: {str(e)}", exc_info=True)
        return {'id': entry.sys.get('id', ''), 'error': str(e)}


def _transform_navigation_entry(entry: contentful.Entry) -> Dict[str, Any]:
    """
    Transforms a Contentful navigation entry into a standardized format.
    
    Args:
        entry: Contentful Entry object
        
    Returns:
        Dict[str, Any]: Transformed navigation data
    """
    if not entry or not hasattr(entry, 'fields'):
        return {}
    
    try:
        # Extract basic fields
        result = {
            'id': entry.sys.get('id', ''),
            'title': entry.fields.get('title', ''),
            'content_type': 'navigation'
        }
        
        # Extract and transform navigation items
        items = []
        if 'items' in entry.fields and entry.fields['items']:
            for item in entry.fields['items']:
                nav_item = {
                    'title': item.fields.get('title', ''),
                    'url': item.fields.get('url', ''),
                    'is_external': item.fields.get('isExternal', False)
                }
                
                # Handle reference to page if present
                if 'page' in item.fields and item.fields['page']:
                    page = item.fields['page']
                    nav_item['page'] = {
                        'id': page.sys.get('id', ''),
                        'title': page.fields.get('title', ''),
                        'slug': page.fields.get('slug', '')
                    }
                
                # Handle nested items recursively
                children = []
                if 'children' in item.fields and item.fields['children']:
                    for child in item.fields['children']:
                        child_item = {
                            'title': child.fields.get('title', ''),
                            'url': child.fields.get('url', ''),
                            'is_external': child.fields.get('isExternal', False)
                        }
                        
                        # Handle reference to page if present
                        if 'page' in child.fields and child.fields['page']:
                            child_page = child.fields['page']
                            child_item['page'] = {
                                'id': child_page.sys.get('id', ''),
                                'title': child_page.fields.get('title', ''),
                                'slug': child_page.fields.get('slug', '')
                            }
                        
                        children.append(child_item)
                
                nav_item['children'] = children
                items.append(nav_item)
        
        result['items'] = items
        return result
    except Exception as e:
        logger.error(f"Error transforming navigation entry: {str(e)}", exc_info=True)
        return {'id': entry.sys.get('id', ''), 'error': str(e)}


def _transform_page_entry(entry: contentful.Entry) -> Dict[str, Any]:
    """
    Transforms a Contentful page entry into a standardized format.
    
    Args:
        entry: Contentful Entry object
        
    Returns:
        Dict[str, Any]: Transformed page data
    """
    if not entry or not hasattr(entry, 'fields'):
        return {}
    
    try:
        # Extract basic fields
        result = {
            'id': entry.sys.get('id', ''),
            'title': entry.fields.get('title', ''),
            'slug': entry.fields.get('slug', ''),
            'metaDescription': entry.fields.get('metaDescription', ''),
            'content_type': 'page'
        }
        
        # Extract and transform content sections
        sections = []
        if 'sections' in entry.fields and entry.fields['sections']:
            for section in entry.fields['sections']:
                section_type = section.sys.get('contentType', {}).get('sys', {}).get('id', 'unknown')
                section_data = {'type': section_type}
                
                # Extract common fields
                if hasattr(section, 'fields'):
                    section_data.update({
                        'id': section.sys.get('id', ''),
                        'title': section.fields.get('title', '')
                    })
                    
                    # Handle content field based on section type
                    if section_type == 'textSection':
                        section_data['content'] = section.fields.get('content', '')
                    elif section_type == 'imageSection':
                        section_data['image'] = _transform_asset(section.fields.get('image')) if 'image' in section.fields else {}
                        section_data['caption'] = section.fields.get('caption', '')
                    elif section_type == 'heroSection':
                        section_data['heading'] = section.fields.get('heading', '')
                        section_data['subheading'] = section.fields.get('subheading', '')
                        section_data['background'] = _transform_asset(section.fields.get('background')) if 'background' in section.fields else {}
                        section_data['ctaText'] = section.fields.get('ctaText', '')
                        section_data['ctaUrl'] = section.fields.get('ctaUrl', '')
                    # Add more section types as needed
                
                sections.append(section_data)
        
        result['sections'] = sections
        
        # Extract media assets
        media = []
        if 'media' in entry.fields and entry.fields['media']:
            for asset in entry.fields['media']:
                if hasattr(asset, 'fields'):
                    media.append(_transform_asset(asset))
        result['media'] = media
        
        return result
    except Exception as e:
        logger.error(f"Error transforming page entry: {str(e)}", exc_info=True)
        return {'id': entry.sys.get('id', ''), 'error': str(e)}


def _transform_asset(asset: contentful.Asset) -> Dict[str, Any]:
    """
    Transforms a Contentful asset into a standardized format.
    
    Args:
        asset: Contentful Asset object
        
    Returns:
        Dict[str, Any]: Transformed asset data
    """
    if not asset or not hasattr(asset, 'fields'):
        return {}
    
    try:
        result = {
            'id': asset.sys.get('id', ''),
            'title': asset.fields.get('title', ''),
            'description': asset.fields.get('description', ''),
            'url': asset.url() if hasattr(asset, 'url') and callable(asset.url) else '',
            'contentType': asset.fields.get('file', {}).get('contentType', '')
        }
        
        # Extract image dimensions if available
        if result['contentType'] and result['contentType'].startswith('image/'):
            file_details = asset.fields.get('file', {}).get('details', {})
            image_details = file_details.get('image', {})
            result['width'] = image_details.get('width')
            result['height'] = image_details.get('height')
        
        return result
    except Exception as e:
        logger.error(f"Error transforming asset: {str(e)}", exc_info=True)
        return {'id': asset.sys.get('id', '') if hasattr(asset, 'sys') else '', 'error': str(e)}


def _get_cache_key(content_type: str, slug: str = None) -> str:
    """
    Generates a cache key for Contentful content.
    
    Args:
        content_type: Type of content (e.g., 'service', 'caseStudy')
        slug: Optional specific slug to include in key
        
    Returns:
        str: Cache key string
    """
    if slug:
        return f"{CONTENT_CACHE_PREFIX}{content_type}:{slug}"
    return f"{CONTENT_CACHE_PREFIX}{content_type}"


class ContentfulClient:
    """
    Client class for interacting with Contentful APIs.
    
    Provides an object-oriented interface for accessing Contentful content
    with shared configuration and error handling.
    """
    
    def __init__(self):
        """
        Initializes the ContentfulClient with delivery and management clients.
        """
        self._delivery_client = None
        self._management_client = None
        self._initialize_clients()
    
    def _initialize_clients(self) -> None:
        """
        Initializes Contentful API clients.
        """
        try:
            # Initialize delivery client
            if settings.CONTENTFUL_SPACE_ID and settings.CONTENTFUL_ACCESS_TOKEN:
                self._delivery_client = contentful.Client(
                    space_id=settings.CONTENTFUL_SPACE_ID,
                    access_token=settings.CONTENTFUL_ACCESS_TOKEN,
                    environment=settings.ENVIRONMENT or 'master',
                    max_rate_limit_retries=3
                )
            
            # Initialize management client if token is provided
            if settings.CONTENTFUL_MANAGEMENT_TOKEN:
                self._management_client = contentful_management.Client(
                    settings.CONTENTFUL_MANAGEMENT_TOKEN
                )
            
            logger.info("Contentful clients initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing Contentful clients: {str(e)}", exc_info=True)
            raise
    
    def get_delivery_client(self) -> contentful.Client:
        """
        Returns the Contentful Delivery API client.
        
        Returns:
            contentful.Client: Contentful Delivery API client
            
        Raises:
            RuntimeError: If client initialization failed
        """
        if self._delivery_client is None:
            self._initialize_clients()
            
        if self._delivery_client is None:
            raise RuntimeError("Contentful Delivery API client not initialized")
            
        return self._delivery_client
    
    def get_management_client(self) -> contentful_management.Client:
        """
        Returns the Contentful Management API client.
        
        Returns:
            contentful_management.Client: Contentful Management API client
            
        Raises:
            ValueError: If management token is not configured
        """
        if self._management_client is None:
            self._initialize_clients()
            
        if self._management_client is None:
            raise ValueError("Contentful Management API client not initialized. Check CONTENTFUL_MANAGEMENT_TOKEN setting.")
            
        return self._management_client
    
    def get_entry(self, entry_id: str, include_level: int = 2) -> Optional[contentful.Entry]:
        """
        Retrieves a single entry by ID.
        
        Args:
            entry_id: The entry ID
            include_level: Level of linked entries to include
            
        Returns:
            contentful.Entry: Contentful entry or None if not found
        """
        try:
            client = self.get_delivery_client()
            return client.entry(entry_id, {'include': include_level})
        except Exception as e:
            logger.error(f"Error retrieving entry {entry_id}: {str(e)}", exc_info=True)
            return None
    
    def get_entries(self, query: Dict[str, Any]) -> contentful.Array:
        """
        Retrieves entries based on query parameters.
        
        Args:
            query: Query parameters dictionary
            
        Returns:
            contentful.Array: Array of Contentful entries
        """
        try:
            client = self.get_delivery_client()
            return client.entries(query)
        except Exception as e:
            logger.error(f"Error retrieving entries: {str(e)}", exc_info=True)
            raise
    
    def get_asset(self, asset_id: str) -> Optional[contentful.Asset]:
        """
        Retrieves a single asset by ID.
        
        Args:
            asset_id: The asset ID
            
        Returns:
            contentful.Asset: Contentful asset or None if not found
        """
        try:
            client = self.get_delivery_client()
            return client.asset(asset_id)
        except Exception as e:
            logger.error(f"Error retrieving asset {asset_id}: {str(e)}", exc_info=True)
            return None
    
    def get_assets(self, query: Dict[str, Any]) -> contentful.Array:
        """
        Retrieves assets based on query parameters.
        
        Args:
            query: Query parameters dictionary
            
        Returns:
            contentful.Array: Array of Contentful assets
        """
        try:
            client = self.get_delivery_client()
            return client.assets(query)
        except Exception as e:
            logger.error(f"Error retrieving assets: {str(e)}", exc_info=True)
            raise
    
    def create_entry(self, content_type_id: str, fields: Dict[str, Any]) -> Dict[str, Any]:
        """
        Creates a new entry using the Management API.
        
        Args:
            content_type_id: The content type ID
            fields: Entry fields dictionary
            
        Returns:
            Dict[str, Any]: Created entry data
        """
        try:
            client = self.get_management_client()
            space = client.spaces().find(settings.CONTENTFUL_SPACE_ID)
            environment = space.environments().find(settings.ENVIRONMENT or 'master')
            
            # Create entry
            entry = environment.entries().create(
                content_type_id,
                {
                    'fields': fields
                }
            )
            
            # Publish entry
            entry.publish()
            
            return {
                'id': entry.id,
                'content_type': content_type_id,
                'created_at': entry.created_at,
                'updated_at': entry.updated_at
            }
        except Exception as e:
            logger.error(f"Error creating entry: {str(e)}", exc_info=True)
            raise
    
    def update_entry(self, entry_id: str, fields: Dict[str, Any]) -> Dict[str, Any]:
        """
        Updates an existing entry using the Management API.
        
        Args:
            entry_id: The entry ID to update
            fields: Updated entry fields
            
        Returns:
            Dict[str, Any]: Updated entry data
        """
        try:
            client = self.get_management_client()
            space = client.spaces().find(settings.CONTENTFUL_SPACE_ID)
            environment = space.environments().find(settings.ENVIRONMENT or 'master')
            
            # Get existing entry
            entry = environment.entries().find(entry_id)
            
            # Update fields
            for field_name, field_value in fields.items():
                entry.fields(field_name, field_value)
            
            # Save and publish
            entry.save()
            entry.publish()
            
            return {
                'id': entry.id,
                'content_type': entry.content_type.id,
                'updated_at': entry.updated_at
            }
        except Exception as e:
            logger.error(f"Error updating entry {entry_id}: {str(e)}", exc_info=True)
            raise
    
    def delete_entry(self, entry_id: str) -> bool:
        """
        Deletes an entry using the Management API.
        
        Args:
            entry_id: The entry ID to delete
            
        Returns:
            bool: True if deletion was successful
        """
        try:
            client = self.get_management_client()
            space = client.spaces().find(settings.CONTENTFUL_SPACE_ID)
            environment = space.environments().find(settings.ENVIRONMENT or 'master')
            
            # Get existing entry
            entry = environment.entries().find(entry_id)
            
            # Unpublish if published
            if entry.is_published:
                entry.unpublish()
            
            # Delete entry
            entry.delete()
            
            return True
        except Exception as e:
            logger.error(f"Error deleting entry {entry_id}: {str(e)}", exc_info=True)
            raise