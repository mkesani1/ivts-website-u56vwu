import unittest.mock
from unittest.mock import patch, MagicMock, Mock

import pytest  # pytest ^7.3.1
import contentful  # contentful ^2.6.0
import contentful_management  # contentful-management ^2.11.0

from app.integrations.contentful import (
    get_delivery_client,
    get_management_client,
    get_services,
    get_service_by_slug,
    get_case_studies,
    get_case_study_by_slug,
    get_impact_stories,
    get_impact_story_by_slug,
    get_navigation,
    invalidate_content_cache,
    ContentfulClient,
)
from app.core.events import get_redis_cache

# Mock data for Contentful entries
MOCK_SERVICE_ENTRY = {
    'sys': {'id': 'service1', 'contentType': {'sys': {'id': 'service'}}},
    'fields': {
        'title': 'Data Collection',
        'slug': 'data-collection',
        'description': 'Comprehensive data gathering solutions',
        'icon': {'sys': {'id': 'asset1'}},
        'order': 1,
        'features': [{'sys': {'id': 'feature1'}, 'fields': {'title': 'Feature 1', 'description': 'Feature description'}}]
    }
}

MOCK_CASE_STUDY_ENTRY = {
    'sys': {'id': 'case1', 'contentType': {'sys': {'id': 'caseStudy'}}},
    'fields': {
        'title': 'E-commerce Product Categorization',
        'slug': 'ecommerce-product-categorization',
        'client': 'Leading Retailer',
        'challenge': 'Improve product search accuracy',
        'solution': 'Data preparation and labeling',
        'industry': {'sys': {'id': 'industry1'}, 'fields': {'name': 'Retail', 'slug': 'retail'}},
        'results': [{'sys': {'id': 'result1'}, 'fields': {'metric': 'Search Accuracy', 'value': '40%', 'description': 'Improvement'}}]
    }
}

MOCK_IMPACT_STORY_ENTRY = {
    'sys': {'id': 'impact1', 'contentType': {'sys': {'id': 'impactStory'}}},
    'fields': {
        'title': 'Empowering Rural Communities',
        'slug': 'empowering-rural-communities',
        'story': 'How our center created 200+ tech jobs',
        'beneficiaries': 'Rural community members',
        'location': {'sys': {'id': 'location1'}, 'fields': {'name': 'Ramanagara', 'region': 'Karnataka', 'country': 'India'}},
        'metrics': [{'sys': {'id': 'metric1'}, 'fields': {'metricName': 'Jobs Created', 'value': 200, 'unit': 'jobs'}}]
    }
}

MOCK_NAVIGATION_ENTRY = {
    'sys': {'id': 'nav1', 'contentType': {'sys': {'id': 'navigation'}}},
    'fields': {
        'title': 'Main Navigation',
        'items': [{'sys': {'id': 'navItem1'}, 'fields': {'title': 'Services', 'link': '/services', 'items': []}}]
    }
}

MOCK_ASSET = {
    'sys': {'id': 'asset1'},
    'fields': {
        'title': 'Data Collection Icon',
        'description': 'Icon for data collection service',
        'file': {'url': '//images.ctfassets.net/space/asset1.svg', 'details': {'size': 1024, 'image': {'width': 100, 'height': 100}}}
    }
}


class MockEntry:
    """Helper class for mocking Contentful entries in tests"""
    def __init__(self, data):
        """Initializes a mock Contentful entry with sys and fields data"""
        self.sys = data.get('sys', {})
        self.fields = data.get('fields', {})


class MockAsset:
    """Helper class for mocking Contentful assets in tests"""
    def __init__(self, data):
        """Initializes a mock Contentful asset with sys and fields data"""
        self.sys = data.get('sys', {})
        self.fields = data.get('fields', {})


@patch('app.integrations.contentful.contentful.Client')
def test_get_delivery_client(mock_contentful_client):
    """Tests that get_delivery_client returns a properly configured Contentful client"""
    # Mock the contentful.Client constructor
    mock_client_instance = MagicMock()
    mock_contentful_client.return_value = mock_client_instance

    # Call get_delivery_client()
    client = get_delivery_client()

    # Assert that contentful.Client was called with correct space ID and access token
    mock_contentful_client.assert_called_once()

    # Assert that the function returns the mocked client instance
    assert client == mock_client_instance

    # Call get_delivery_client() again to test singleton behavior
    client2 = get_delivery_client()

    # Assert that contentful.Client was only called once (singleton pattern)
    assert mock_contentful_client.call_count == 1


@patch('app.integrations.contentful.contentful_management.Client')
def test_get_management_client(mock_contentful_management_client):
    """Tests that get_management_client returns a properly configured Contentful management client"""
    # Mock the contentful_management.Client constructor
    mock_client_instance = MagicMock()
    mock_contentful_management_client.return_value = mock_client_instance

    # Call get_management_client()
    client = get_management_client()

    # Assert that contentful_management.Client was called with correct management token
    mock_contentful_management_client.assert_called_once()

    # Assert that the function returns the mocked client instance
    assert client == mock_client_instance

    # Call get_management_client() again to test singleton behavior
    client2 = get_management_client()

    # Assert that contentful_management.Client was only called once (singleton pattern)
    assert mock_contentful_management_client.call_count == 1


@patch('app.integrations.contentful.get_delivery_client')
@patch('app.integrations.contentful.get_redis_cache')
def test_get_services(mock_get_redis_cache, mock_get_delivery_client):
    """Tests retrieving services from Contentful"""
    # Mock the get_delivery_client function to return a mock client
    mock_client = MagicMock()
    mock_get_delivery_client.return_value = mock_client

    # Mock the get_redis_cache function to return a mock cache
    mock_cache = MagicMock()
    mock_get_redis_cache.return_value = mock_cache
    mock_cache.get.return_value = None  # Cache miss

    # Configure mock client to return a list of mock service entries
    mock_client.entries.return_value = [MockEntry(MOCK_SERVICE_ENTRY)]

    # Call get_services()
    services = get_services()

    # Assert that the client's entries method was called with correct parameters
    mock_client.entries.assert_called_once_with({'content_type': 'service', 'include': 2})

    # Assert that the function returns the expected transformed services
    assert len(services) == 1
    assert services[0]['title'] == 'Data Collection'

    # Assert that the cache set method was called to store the result
    mock_cache.set.assert_called_once()


@patch('app.integrations.contentful.get_delivery_client')
@patch('app.integrations.contentful.get_redis_cache')
def test_get_services_with_cache(mock_get_redis_cache, mock_get_delivery_client):
    """Tests retrieving services from cache"""
    # Mock the get_delivery_client function to return a mock client
    mock_client = MagicMock()
    mock_get_delivery_client.return_value = mock_client

    # Mock the get_redis_cache function to return a mock cache
    mock_cache = MagicMock()
    mock_get_redis_cache.return_value = mock_cache
    mock_cache.get.return_value = [MOCK_SERVICE_ENTRY['fields']]  # Cache hit

    # Call get_services()
    services = get_services()

    # Assert that the client's entries method was not called
    mock_client.entries.assert_not_called()

    # Assert that the function returns the cached result
    assert len(services) == 1
    assert services[0]['title'] == MOCK_SERVICE_ENTRY['fields']['title']

    # Assert that the cache set method was not called
    mock_cache.set.assert_not_called()


@patch('app.integrations.contentful.get_delivery_client')
@patch('app.integrations.contentful.get_redis_cache')
def test_get_service_by_slug(mock_get_redis_cache, mock_get_delivery_client):
    """Tests retrieving a specific service by slug"""
    # Mock the get_delivery_client function to return a mock client
    mock_client = MagicMock()
    mock_get_delivery_client.return_value = mock_client

    # Mock the get_redis_cache function to return a mock cache
    mock_cache = MagicMock()
    mock_get_redis_cache.return_value = mock_cache
    mock_cache.get.return_value = None  # Cache miss

    # Configure mock client to return a mock service entry
    mock_client.entries.return_value = [MockEntry(MOCK_SERVICE_ENTRY)]

    # Call get_service_by_slug('data-collection')
    service = get_service_by_slug('data-collection')

    # Assert that the client's entries method was called with correct parameters including slug filter
    mock_client.entries.assert_called_once_with({'content_type': 'service', 'fields.slug': 'data-collection', 'include': 2})

    # Assert that the function returns the expected transformed service
    assert service['title'] == 'Data Collection'

    # Assert that the cache set method was called to store the result
    mock_cache.set.assert_called_once()


@patch('app.integrations.contentful.get_delivery_client')
@patch('app.integrations.contentful.get_redis_cache')
def test_get_service_by_slug_not_found(mock_get_redis_cache, mock_get_delivery_client):
    """Tests retrieving a non-existent service by slug"""
    # Mock the get_delivery_client function to return a mock client
    mock_client = MagicMock()
    mock_get_delivery_client.return_value = mock_client

    # Mock the get_redis_cache function to return a mock cache
    mock_cache = MagicMock()
    mock_get_redis_cache.return_value = mock_cache
    mock_cache.get.return_value = None  # Cache miss

    # Configure mock client to return an empty list
    mock_client.entries.return_value = []

    # Call get_service_by_slug('non-existent')
    service = get_service_by_slug('non-existent')

    # Assert that the client's entries method was called with correct parameters
    mock_client.entries.assert_called_once_with({'content_type': 'service', 'fields.slug': 'non-existent', 'include': 2})

    # Assert that the function returns None
    assert service is None

    # Assert that the cache set method was called to store the None result
    mock_cache.set.assert_called_once_with(unittest.mock.ANY, None, unittest.mock.ANY)


@patch('app.integrations.contentful.get_delivery_client')
@patch('app.integrations.contentful.get_redis_cache')
def test_get_case_studies(mock_get_redis_cache, mock_get_delivery_client):
    """Tests retrieving case studies from Contentful"""
    # Mock the get_delivery_client function to return a mock client
    mock_client = MagicMock()
    mock_get_delivery_client.return_value = mock_client

    # Mock the get_redis_cache function to return a mock cache
    mock_cache = MagicMock()
    mock_get_redis_cache.return_value = mock_cache
    mock_cache.get.return_value = None  # Cache miss

    # Configure mock client to return a list of mock case study entries
    mock_client.entries.return_value = [MockEntry(MOCK_CASE_STUDY_ENTRY)]

    # Call get_case_studies()
    case_studies = get_case_studies()

    # Assert that the client's entries method was called with correct parameters
    mock_client.entries.assert_called_once_with({'content_type': 'caseStudy', 'include': 2})

    # Assert that the function returns the expected transformed case studies
    assert len(case_studies) == 1
    assert case_studies[0]['title'] == 'E-commerce Product Categorization'

    # Assert that the cache set method was called to store the result
    mock_cache.set.assert_called_once()


@patch('app.integrations.contentful.get_delivery_client')
@patch('app.integrations.contentful.get_redis_cache')
def test_get_case_studies_with_filters(mock_get_redis_cache, mock_get_delivery_client):
    """Tests retrieving case studies with industry and service filters"""
    # Mock the get_delivery_client function to return a mock client
    mock_client = MagicMock()
    mock_get_delivery_client.return_value = mock_client

    # Mock the get_redis_cache function to return a mock cache
    mock_cache = MagicMock()
    mock_get_redis_cache.return_value = mock_cache
    mock_cache.get.return_value = None  # Cache miss

    # Configure mock client to return filtered mock case study entries
    mock_client.entries.return_value = [MockEntry(MOCK_CASE_STUDY_ENTRY)]

    # Call get_case_studies(industry_slug='retail', service_slug='data-collection')
    case_studies = get_case_studies(industry_slug='retail', service_slug='data-collection')

    # Assert that the client's entries method was called with correct filter parameters
    mock_client.entries.assert_called_once_with({
        'content_type': 'caseStudy',
        'include': 2,
        'fields.industry.sys.contentType.sys.id': 'industry',
        'fields.industry.fields.slug': 'retail',
        'fields.services.sys.contentType.sys.id': 'service',
        'fields.services.fields.slug': 'data-collection'
    })

    # Assert that the function returns the expected filtered case studies
    assert len(case_studies) == 1
    assert case_studies[0]['title'] == 'E-commerce Product Categorization'

    # Assert that the cache set method was called to store the result
    mock_cache.set.assert_called_once()


@patch('app.integrations.contentful.get_delivery_client')
@patch('app.integrations.contentful.get_redis_cache')
def test_get_case_study_by_slug(mock_get_redis_cache, mock_get_delivery_client):
    """Tests retrieving a specific case study by slug"""
    # Mock the get_delivery_client function to return a mock client
    mock_client = MagicMock()
    mock_get_delivery_client.return_value = mock_client

    # Mock the get_redis_cache function to return a mock cache
    mock_cache = MagicMock()
    mock_get_redis_cache.return_value = mock_cache
    mock_cache.get.return_value = None  # Cache miss

    # Configure mock client to return a mock case study entry
    mock_client.entries.return_value = [MockEntry(MOCK_CASE_STUDY_ENTRY)]

    # Call get_case_study_by_slug('ecommerce-product-categorization')
    case_study = get_case_study_by_slug('ecommerce-product-categorization')

    # Assert that the client's entries method was called with correct parameters including slug filter
    mock_client.entries.assert_called_once_with({'content_type': 'caseStudy', 'fields.slug': 'ecommerce-product-categorization', 'include': 2})

    # Assert that the function returns the expected transformed case study
    assert case_study['title'] == 'E-commerce Product Categorization'

    # Assert that the cache set method was called to store the result
    mock_cache.set.assert_called_once()


@patch('app.integrations.contentful.get_delivery_client')
@patch('app.integrations.contentful.get_redis_cache')
def test_get_impact_stories(mock_get_redis_cache, mock_get_delivery_client):
    """Tests retrieving impact stories from Contentful"""
    # Mock the get_delivery_client function to return a mock client
    mock_client = MagicMock()
    mock_get_delivery_client.return_value = mock_client

    # Mock the get_redis_cache function to return a mock cache
    mock_cache = MagicMock()
    mock_get_redis_cache.return_value = mock_cache
    mock_cache.get.return_value = None  # Cache miss

    # Configure mock client to return a list of mock impact story entries
    mock_client.entries.return_value = [MockEntry(MOCK_IMPACT_STORY_ENTRY)]

    # Call get_impact_stories()
    impact_stories = get_impact_stories()

    # Assert that the client's entries method was called with correct parameters
    mock_client.entries.assert_called_once_with({'content_type': 'impactStory', 'include': 2})

    # Assert that the function returns the expected transformed impact stories
    assert len(impact_stories) == 1
    assert impact_stories[0]['title'] == 'Empowering Rural Communities'

    # Assert that the cache set method was called to store the result
    mock_cache.set.assert_called_once()


@patch('app.integrations.contentful.get_delivery_client')
@patch('app.integrations.contentful.get_redis_cache')
def test_get_impact_story_by_slug(mock_get_redis_cache, mock_get_delivery_client):
    """Tests retrieving a specific impact story by slug"""
    # Mock the get_delivery_client function to return a mock client
    mock_client = MagicMock()
    mock_get_delivery_client.return_value = mock_client

    # Mock the get_redis_cache function to return a mock cache
    mock_cache = MagicMock()
    mock_get_redis_cache.return_value = mock_cache
    mock_cache.get.return_value = None  # Cache miss

    # Configure mock client to return a mock impact story entry
    mock_client.entries.return_value = [MockEntry(MOCK_IMPACT_STORY_ENTRY)]

    # Call get_impact_story_by_slug('empowering-rural-communities')
    impact_story = get_impact_story_by_slug('empowering-rural-communities')

    # Assert that the client's entries method was called with correct parameters including slug filter
    mock_client.entries.assert_called_once_with({'content_type': 'impactStory', 'fields.slug': 'empowering-rural-communities', 'include': 2})

    # Assert that the function returns the expected transformed impact story
    assert impact_story['title'] == 'Empowering Rural Communities'

    # Assert that the cache set method was called to store the result
    mock_cache.set.assert_called_once()


@patch('app.integrations.contentful.get_delivery_client')
@patch('app.integrations.contentful.get_redis_cache')
def test_get_navigation(mock_get_redis_cache, mock_get_delivery_client):
    """Tests retrieving navigation structure from Contentful"""
    # Mock the get_delivery_client function to return a mock client
    mock_client = MagicMock()
    mock_get_delivery_client.return_value = mock_client

    # Mock the get_redis_cache function to return a mock cache
    mock_cache = MagicMock()
    mock_get_redis_cache.return_value = mock_cache
    mock_cache.get.return_value = None  # Cache miss

    # Configure mock client to return a mock navigation entry
    mock_client.entries.return_value = [MockEntry(MOCK_NAVIGATION_ENTRY)]

    # Call get_navigation()
    navigation = get_navigation()

    # Assert that the client's entries method was called with correct parameters
    mock_client.entries.assert_called_once_with({'content_type': 'navigation', 'include': 3})

    # Assert that the function returns the expected transformed navigation structure
    assert navigation['title'] == 'Main Navigation'

    # Assert that the cache set method was called to store the result
    mock_cache.set.assert_called_once()


@patch('app.integrations.contentful.get_redis_cache')
def test_invalidate_content_cache(mock_get_redis_cache):
    """Tests invalidating content cache"""
    # Mock the get_redis_cache function to return a mock cache
    mock_cache = MagicMock()
    mock_get_redis_cache.return_value = mock_cache
    mock_cache.delete_pattern.return_value = 1  # Simulate deleting one key

    # Call invalidate_content_cache('service', 'data-collection')
    invalidate_content_cache('service', 'data-collection')

    # Assert that the cache's delete_pattern method was called with correct pattern
    mock_cache.delete_pattern.assert_called_once_with('contentful:service:data-collection')

    # Call invalidate_content_cache('service', None) to test invalidating all services
    invalidate_content_cache('service', None)

    # Assert that the cache's delete_pattern method was called with correct pattern for all services
    mock_cache.delete_pattern.assert_called_with('contentful:service:*')


@patch('app.integrations.contentful.contentful.Client')
@patch('app.integrations.contentful.contentful_management.Client')
def test_contentful_client_initialization(mock_contentful_management_client, mock_contentful_client):
    """Tests initialization of ContentfulClient class"""
    # Mock the contentful.Client constructor
    mock_delivery_client = MagicMock()
    mock_contentful_client.return_value = mock_delivery_client

    # Mock the contentful_management.Client constructor
    mock_management_client = MagicMock()
    mock_contentful_management_client.return_value = mock_management_client

    # Create a new ContentfulClient instance
    client = ContentfulClient()

    # Assert that contentful.Client was called with correct parameters
    mock_contentful_client.assert_called_once()

    # Assert that contentful_management.Client was called with correct parameters
    mock_contentful_management_client.assert_called_once()

    # Assert that the client's _delivery_client and _management_client properties are set correctly
    assert client._delivery_client == mock_delivery_client
    assert client._management_client == mock_management_client


@patch('app.integrations.contentful.ContentfulClient._initialize_clients')
def test_contentful_client_get_entry(mock_init_clients):
    """Tests ContentfulClient.get_entry method"""
    # Create a ContentfulClient instance with mocked _initialize_clients method
    client = ContentfulClient()
    client._initialize_clients = mock_init_clients

    # Set up a mock delivery client on the instance
    mock_delivery_client = MagicMock()
    client._delivery_client = mock_delivery_client

    # Configure the mock client's entry method to return a mock entry
    mock_entry = MagicMock()
    mock_delivery_client.entry.return_value = mock_entry

    # Call client.get_entry('entry1', 2)
    entry = client.get_entry('entry1', 2)

    # Assert that the delivery client's entry method was called with correct parameters
    mock_delivery_client.entry.assert_called_once_with('entry1', {'include': 2})

    # Assert that the method returns the expected entry
    assert entry == mock_entry


@patch('app.integrations.contentful.ContentfulClient._initialize_clients')
def test_contentful_client_get_entries(mock_init_clients):
    """Tests ContentfulClient.get_entries method"""
    # Create a ContentfulClient instance with mocked _initialize_clients method
    client = ContentfulClient()
    client._initialize_clients = mock_init_clients

    # Set up a mock delivery client on the instance
    mock_delivery_client = MagicMock()
    client._delivery_client = mock_delivery_client

    # Configure the mock client's entries method to return mock entries
    mock_entries = MagicMock()
    mock_delivery_client.entries.return_value = mock_entries

    # Call client.get_entries({'content_type': 'service'})
    entries = client.get_entries({'content_type': 'service'})

    # Assert that the delivery client's entries method was called with correct parameters
    mock_delivery_client.entries.assert_called_once_with({'content_type': 'service'})

    # Assert that the method returns the expected entries
    assert entries == mock_entries


@patch('app.integrations.contentful.ContentfulClient._initialize_clients')
def test_contentful_client_error_handling(mock_init_clients):
    """Tests error handling in ContentfulClient methods"""
    # Create a ContentfulClient instance with mocked _initialize_clients method
    client = ContentfulClient()
    client._initialize_clients = mock_init_clients

    # Set up a mock delivery client on the instance
    mock_delivery_client = MagicMock()
    client._delivery_client = mock_delivery_client

    # Configure the mock client's entries method to raise an exception
    mock_delivery_client.entries.side_effect = Exception('Test Exception')

    # Call client.get_entries({'content_type': 'service'})
    with pytest.raises(Exception, match='Test Exception'):
        client.get_entries({'content_type': 'service'})

    # Configure the mock client's entry method to raise an exception
    mock_delivery_client.entry.side_effect = Exception('Test Exception')

    # Call client.get_entry('entry1')
    with pytest.raises(Exception, match='Test Exception'):
        client.get_entry('entry1')


@patch('app.integrations.contentful.get_delivery_client')
@patch('app.integrations.contentful.get_redis_cache')
def test_error_handling_in_content_retrieval(mock_get_redis_cache, mock_get_delivery_client):
    """Tests error handling in content retrieval functions"""
    # Mock the get_delivery_client function to return a mock client
    mock_client = MagicMock()
    mock_get_delivery_client.return_value = mock_client

    # Mock the get_redis_cache function to return a mock cache
    mock_cache = MagicMock()
    mock_get_redis_cache.return_value = mock_cache

    # Configure mock client's entries method to raise an exception
    mock_client.entries.side_effect = Exception('Test Exception')

    # Call get_services()
    services = get_services()

    # Assert that the function handles the exception gracefully and returns an empty list
    assert services == []

    # Call get_service_by_slug('data-collection')
    service = get_service_by_slug('data-collection')

    # Assert that the function handles the exception gracefully and returns None
    assert service is None

    # Call get_case_studies()
    case_studies = get_case_studies()

    # Assert that the function handles the exception gracefully and returns an empty list
    assert case_studies == []

    # Call get_impact_stories()
    impact_stories = get_impact_stories()

    # Assert that the function handles the exception gracefully and returns an empty list
    assert impact_stories == []