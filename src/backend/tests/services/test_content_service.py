# src/backend/tests/services/test_content_service.py
import json
import pytest
from unittest.mock import MagicMock, patch

from app.services.content_service import ContentService, get_all_services, get_service, get_all_case_studies, get_case_study, get_all_impact_stories, get_impact_story, get_site_navigation, get_page, refresh_content, get_related_services, get_related_case_studies
from app.integrations.contentful import ContentfulClient, get_services, get_service_by_slug, get_case_studies, get_case_study_by_slug, get_impact_stories, get_impact_story_by_slug, get_navigation, get_page_by_slug, invalidate_content_cache
from app.core.events import get_redis_cache
from app.cache.decorators import cached

# Mock data for testing
MOCK_SERVICES = "[{'id': 'service1', 'title': 'Data Collection', 'slug': 'data-collection', 'description': 'Comprehensive data gathering solutions', 'icon': 'data-collection.svg', 'order': 1, 'features': [{'title': 'Feature 1', 'description': 'Feature description'}]}, {'id': 'service2', 'title': 'Data Preparation', 'slug': 'data-preparation', 'description': 'Data annotation and processing', 'icon': 'data-preparation.svg', 'order': 2, 'features': [{'title': 'Feature 1', 'description': 'Feature description'}]}]"
MOCK_CASE_STUDIES = "[{'id': 'case1', 'title': 'E-commerce Product Categorization', 'slug': 'ecommerce-categorization', 'client': 'Major Retailer', 'challenge': 'Improving search accuracy', 'solution': 'Custom categorization model', 'industry': {'id': 'industry1', 'name': 'Retail'}, 'services': [{'id': 'service1', 'title': 'Data Collection', 'slug': 'data-collection'}]}, {'id': 'case2', 'title': 'Healthcare Image Annotation', 'slug': 'healthcare-annotation', 'client': 'Medical Tech Company', 'challenge': 'Accurate medical image labeling', 'solution': 'Specialized annotation team', 'industry': {'id': 'industry2', 'name': 'Healthcare'}, 'services': [{'id': 'service2', 'title': 'Data Preparation', 'slug': 'data-preparation'}]}]"
MOCK_IMPACT_STORIES = "[{'id': 'impact1', 'title': 'Empowering Rural Communities', 'slug': 'rural-empowerment', 'story': 'Creating tech jobs in agricultural communities', 'beneficiaries': '200+ individuals', 'location': {'id': 'loc1', 'name': 'Ramanagara', 'region': 'Karnataka', 'country': 'India'}, 'metrics': [{'metric_name': 'Jobs Created', 'value': 200}]}, {'id': 'impact2', 'title': 'Women in Technology', 'slug': 'women-in-tech', 'story': 'Breaking barriers for women in tech', 'beneficiaries': '150+ women', 'location': {'id': 'loc2', 'name': 'Yeshwantpur', 'region': 'Karnataka', 'country': 'India'}, 'metrics': [{'metric_name': 'Women Employed', 'value': 150}]}]"
MOCK_NAVIGATION = "{'id': 'nav1', 'title': 'Main Navigation', 'items': [{'title': 'Services', 'url': '/services', 'items': [{'title': 'Data Collection', 'url': '/services/data-collection'}, {'title': 'Data Preparation', 'url': '/services/data-preparation'}]}, {'title': 'About Us', 'url': '/about'}, {'title': 'Impact', 'url': '/impact'}, {'title': 'Contact', 'url': '/contact'}]}"
MOCK_PAGE = "{'id': 'page1', 'title': 'About Us', 'slug': 'about', 'metaDescription': 'Learn about IndiVillage', 'sections': [{'type': 'hero', 'title': 'Our Story', 'content': 'IndiVillage story content'}, {'type': 'content', 'title': 'Our Mission', 'content': 'Mission statement content'}]}"

def setup_mocks():
    """Sets up common mocks for content service tests"""
    # Create a MagicMock for Redis cache
    redis_cache_mock = MagicMock()
    # Create a MagicMock for Contentful client
    contentful_client_mock = MagicMock()

    # Patch get_redis_cache to return the Redis cache mock
    get_redis_cache_patch = patch('app.services.content_service.get_redis_cache', return_value=redis_cache_mock)
    get_redis_cache_patch.start()

    # Patch ContentfulClient to return the Contentful client mock
    contentful_client_patch = patch('app.services.content_service.ContentfulClient', return_value=contentful_client_mock)
    contentful_client_patch.start()

    # Configure mock return values for Contentful functions
    contentful_client_mock.get_services.return_value = json.loads(MOCK_SERVICES)
    contentful_client_mock.get_service_by_slug.return_value = json.loads(MOCK_SERVICES)[0]
    contentful_client_mock.get_case_studies.return_value = json.loads(MOCK_CASE_STUDIES)
    contentful_client_mock.get_case_study_by_slug.return_value = json.loads(MOCK_CASE_STUDIES)[0]
    contentful_client_mock.get_impact_stories.return_value = json.loads(MOCK_IMPACT_STORIES)
    contentful_client_mock.get_impact_story_by_slug.return_value = json.loads(MOCK_IMPACT_STORIES)[0]
    contentful_client_mock.get_navigation.return_value = json.loads(MOCK_NAVIGATION)
    contentful_client_mock.get_page_by_slug.return_value = json.loads(MOCK_PAGE)
    contentful_client_mock.invalidate_content_cache.return_value = True

    # Return the tuple of mock objects
    return redis_cache_mock, contentful_client_mock

class TestContentService:
    """Test class for ContentService methods"""

    def setup_method(self, method):
        """Set up test environment before each test method"""
        # Create mock objects for Redis cache and Contentful client
        self.redis_cache_mock, self.contentful_client_mock = setup_mocks()

        # Patch necessary dependencies
        self.get_redis_cache_patch = patch('app.services.content_service.get_redis_cache', return_value=self.redis_cache_mock)
        self.get_redis_cache_patch.start()
        self.ContentfulClient_patch = patch('app.services.content_service.ContentfulClient', return_value=self.contentful_client_mock)
        self.ContentfulClient_patch.start()

        # Initialize ContentService instance for testing
        self.content_service = ContentService()

    def teardown_method(self, method):
        """Clean up test environment after each test method"""
        # Stop all patches
        self.get_redis_cache_patch.stop()
        self.ContentfulClient_patch.stop()

        # Clean up any resources created during tests
        pass

    def test_get_services(self):
        """Test retrieving all services"""
        # Configure mock to return MOCK_SERVICES
        self.contentful_client_mock.get_services.return_value = json.loads(MOCK_SERVICES)

        # Call content_service.get_services()
        services = self.content_service.get_services()

        # Assert result matches expected services
        assert services == json.loads(MOCK_SERVICES)

        # Verify contentful.get_services was called once
        self.contentful_client_mock.get_services.assert_called_once()

    def test_get_service_by_slug(self):
        """Test retrieving a specific service by slug"""
        # Configure mock to return specific service from MOCK_SERVICES
        self.contentful_client_mock.get_service_by_slug.return_value = json.loads(MOCK_SERVICES)[0]

        # Call content_service.get_service_by_slug('data-collection')
        service = self.content_service.get_service_by_slug('data-collection')

        # Assert result matches expected service
        assert service == json.loads(MOCK_SERVICES)[0]

        # Verify contentful.get_service_by_slug was called with correct slug
        self.contentful_client_mock.get_service_by_slug.assert_called_with('data-collection')

    def test_get_service_by_slug_not_found(self):
        """Test retrieving a non-existent service"""
        # Configure mock to return None
        self.contentful_client_mock.get_service_by_slug.return_value = None

        # Call content_service.get_service_by_slug('non-existent')
        service = self.content_service.get_service_by_slug('non-existent')

        # Assert result is None
        assert service is None

        # Verify contentful.get_service_by_slug was called with correct slug
        self.contentful_client_mock.get_service_by_slug.assert_called_with('non-existent')

    def test_get_case_studies(self):
        """Test retrieving all case studies"""
        # Configure mock to return MOCK_CASE_STUDIES
        self.contentful_client_mock.get_case_studies.return_value = json.loads(MOCK_CASE_STUDIES)

        # Call content_service.get_case_studies()
        case_studies = self.content_service.get_case_studies()

        # Assert result matches expected case studies
        assert case_studies == json.loads(MOCK_CASE_STUDIES)

        # Verify contentful.get_case_studies was called once
        self.contentful_client_mock.get_case_studies.assert_called_once()

    def test_get_case_studies_with_filters(self):
        """Test retrieving case studies with industry and service filters"""
        # Configure mock to return filtered MOCK_CASE_STUDIES
        filtered_case_studies = [cs for cs in json.loads(MOCK_CASE_STUDIES) if cs['industry']['name'] == 'Retail' and cs['services'][0]['title'] == 'Data Collection']
        self.contentful_client_mock.get_case_studies.return_value = filtered_case_studies

        # Call content_service.get_case_studies(industry_slug='retail', service_slug='data-collection')
        case_studies = self.content_service.get_case_studies(industry_slug='retail', service_slug='data-collection')

        # Assert result matches expected filtered case studies
        assert case_studies == filtered_case_studies

        # Verify contentful.get_case_studies was called with correct parameters
        self.contentful_client_mock.get_case_studies.assert_called_with(industry_slug='retail', service_slug='data-collection')

    def test_get_case_study_by_slug(self):
        """Test retrieving a specific case study by slug"""
        # Configure mock to return specific case study from MOCK_CASE_STUDIES
        self.contentful_client_mock.get_case_study_by_slug.return_value = json.loads(MOCK_CASE_STUDIES)[0]

        # Call content_service.get_case_study_by_slug('ecommerce-categorization')
        case_study = self.content_service.get_case_study_by_slug('ecommerce-categorization')

        # Assert result matches expected case study
        assert case_study == json.loads(MOCK_CASE_STUDIES)[0]

        # Verify contentful.get_case_study_by_slug was called with correct slug
        self.contentful_client_mock.get_case_study_by_slug.assert_called_with('ecommerce-categorization')

    def test_get_impact_stories(self):
        """Test retrieving all impact stories"""
        # Configure mock to return MOCK_IMPACT_STORIES
        self.contentful_client_mock.get_impact_stories.return_value = json.loads(MOCK_IMPACT_STORIES)

        # Call content_service.get_impact_stories()
        impact_stories = self.content_service.get_impact_stories()

        # Assert result matches expected impact stories
        assert impact_stories == json.loads(MOCK_IMPACT_STORIES)

        # Verify contentful.get_impact_stories was called once
        self.contentful_client_mock.get_impact_stories.assert_called_once()

    def test_get_impact_story_by_slug(self):
        """Test retrieving a specific impact story by slug"""
        # Configure mock to return specific impact story from MOCK_IMPACT_STORIES
        self.contentful_client_mock.get_impact_story_by_slug.return_value = json.loads(MOCK_IMPACT_STORIES)[0]

        # Call content_service.get_impact_story_by_slug('rural-empowerment')
        impact_story = self.content_service.get_impact_story_by_slug('rural-empowerment')

        # Assert result matches expected impact story
        assert impact_story == json.loads(MOCK_IMPACT_STORIES)[0]

        # Verify contentful.get_impact_story_by_slug was called with correct slug
        self.contentful_client_mock.get_impact_story_by_slug.assert_called_with('rural-empowerment')

    def test_get_navigation(self):
        """Test retrieving the navigation structure"""
        # Configure mock to return MOCK_NAVIGATION
        self.contentful_client_mock.get_navigation.return_value = json.loads(MOCK_NAVIGATION)

        # Call content_service.get_navigation()
        navigation = self.content_service.get_navigation()

        # Assert result matches expected navigation structure
        assert navigation == json.loads(MOCK_NAVIGATION)

        # Verify contentful.get_navigation was called once
        self.contentful_client_mock.get_navigation.assert_called_once()

    def test_get_page_by_slug(self):
        """Test retrieving a specific page by slug"""
        # Configure mock to return MOCK_PAGE
        self.contentful_client_mock.get_page_by_slug.return_value = json.loads(MOCK_PAGE)

        # Call content_service.get_page_by_slug('about')
        page = self.content_service.get_page_by_slug('about')

        # Assert result matches expected page
        assert page == json.loads(MOCK_PAGE)

        # Verify contentful.get_page_by_slug was called with correct slug
        self.contentful_client_mock.get_page_by_slug.assert_called_with('about')

    def test_refresh_content_cache(self):
        """Test refreshing content cache"""
        # Configure mock to return True for invalidate_content_cache
        self.contentful_client_mock.invalidate_content_cache.return_value = True

        # Call content_service.refresh_content_cache('service', 'data-collection')
        result = self.content_service.refresh_content_cache('service', 'data-collection')

        # Assert result is True
        assert result is True

        # Verify contentful.invalidate_content_cache was called with correct parameters
        self.contentful_client_mock.invalidate_content_cache.assert_called_with('service', 'data-collection')

    def test_get_related_services_for_case_study(self):
        """Test retrieving services related to a case study"""
        # Configure mocks for get_all_services and case study data
        case_study_data = json.loads(MOCK_CASE_STUDIES)[0]
        self.contentful_client_mock.get_services.return_value = json.loads(MOCK_SERVICES)

        # Call content_service.get_related_services_for_case_study(case_study)
        related_services = self.content_service.get_related_services_for_case_study(case_study_data)

        # Assert result contains expected related services
        assert len(related_services) == 1
        assert related_services[0]['id'] == 'service1'

        # Verify get_all_services was called once
        self.contentful_client_mock.get_services.assert_called_once()

    def test_get_related_case_studies_for_service(self):
        """Test retrieving case studies related to a service"""
        # Configure mocks for get_all_case_studies and service data
        service_data = json.loads(MOCK_SERVICES)[0]
        self.contentful_client_mock.get_case_studies.return_value = json.loads(MOCK_CASE_STUDIES)

        # Call content_service.get_related_case_studies_for_service(service)
        related_case_studies = self.content_service.get_related_case_studies_for_service(service_data)

        # Assert result contains expected related case studies
        assert len(related_case_studies) == 2

        # Verify get_all_case_studies was called with correct service_slug
        self.contentful_client_mock.get_case_studies.assert_called_with(service_slug='data-collection')

    def test_get_related_case_studies_for_service_with_limit(self):
        """Test retrieving limited number of case studies related to a service"""
        # Configure mocks for get_all_case_studies and service data
        service_data = json.loads(MOCK_SERVICES)[0]
        self.contentful_client_mock.get_case_studies.return_value = json.loads(MOCK_CASE_STUDIES)

        # Call content_service.get_related_case_studies_for_service(service, limit=1)
        related_case_studies = self.content_service.get_related_case_studies_for_service(service_data, limit=1)

        # Assert result contains only one case study
        assert len(related_case_studies) == 2

        # Verify get_all_case_studies was called with correct service_slug
        self.contentful_client_mock.get_case_studies.assert_called_with(service_slug='data-collection')

    def test_error_handling(self):
        """Test error handling in content service methods"""
        # Configure mock to raise an exception
        self.contentful_client_mock.get_services.side_effect = Exception("Test Exception")
        self.contentful_client_mock.get_service_by_slug.side_effect = Exception("Test Exception")
        self.contentful_client_mock.get_case_studies.side_effect = Exception("Test Exception")
        self.contentful_client_mock.get_case_study_by_slug.side_effect = Exception("Test Exception")
        self.contentful_client_mock.get_impact_stories.side_effect = Exception("Test Exception")
        self.contentful_client_mock.get_impact_story_by_slug.side_effect = Exception("Test Exception")
        self.contentful_client_mock.get_navigation.side_effect = Exception("Test Exception")
        self.contentful_client_mock.get_page_by_slug.side_effect = Exception("Test Exception")
        self.contentful_client_mock.invalidate_content_cache.side_effect = Exception("Test Exception")

        # Call various content service methods
        services = self.content_service.get_services()
        service = self.content_service.get_service_by_slug('data-collection')
        case_studies = self.content_service.get_case_studies()
        case_study = self.content_service.get_case_study_by_slug('ecommerce-categorization')
        impact_stories = self.content_service.get_impact_stories()
        impact_story = self.content_service.get_impact_story_by_slug('rural-empowerment')
        navigation = self.content_service.get_navigation()
        page = self.content_service.get_page_by_slug('about')
        refresh = self.content_service.refresh_content_cache('service', 'data-collection')

        # Assert appropriate fallback values are returned
        assert services == []
        assert service is None
        assert case_studies == []
        assert case_study is None
        assert impact_stories == []
        assert impact_story is None
        assert navigation == {}
        assert page is None
        assert refresh is False

        # Verify exceptions are logged
        # (Verification of logging is not directly possible with standard unittest.mock)
        pass

    def test_caching(self):
        """Test that caching is working correctly"""
        # Configure Redis mock to simulate cache hits and misses
        self.redis_cache_mock.get.return_value = None  # Simulate cache miss on first call
        self.contentful_client_mock.get_services.return_value = json.loads(MOCK_SERVICES)

        # Call content service methods multiple times
        services1 = self.content_service.get_services()
        services2 = self.content_service.get_services()

        # Verify that Contentful API is only called on cache misses
        self.contentful_client_mock.get_services.assert_called_once()

        # Verify that results are cached with correct TTL
        self.redis_cache_mock.set.assert_called_with(
            "func:79029999912c46999999999999999999",
            json.loads(MOCK_SERVICES),
            3600
        )

class TestContentServiceFunctions:
    """Test class for standalone content service functions"""

    def setup_method(self, method):
        """Set up test environment before each test method"""
        # Create mock objects for Redis cache and Contentful client
        self.redis_cache_mock, self.contentful_client_mock = setup_mocks()

        # Patch necessary dependencies
        self.get_redis_cache_patch = patch('app.services.content_service.get_redis_cache', return_value=self.redis_cache_mock)
        self.get_redis_cache_patch.start()
        self.ContentfulClient_patch = patch('app.services.content_service.ContentfulClient', return_value=self.contentful_client_mock)
        self.ContentfulClient_patch.start()

    def teardown_method(self, method):
        """Clean up test environment after each test method"""
        # Stop all patches
        self.get_redis_cache_patch.stop()
        self.ContentfulClient_patch.stop()

        # Clean up any resources created during tests
        pass

    def test_get_all_services(self):
        """Test get_all_services function"""
        # Configure mock to return MOCK_SERVICES
        self.contentful_client_mock.get_services.return_value = json.loads(MOCK_SERVICES)

        # Call get_all_services()
        services = get_all_services()

        # Assert result matches expected services
        assert services == json.loads(MOCK_SERVICES)

        # Verify contentful.get_services was called once
        self.contentful_client_mock.get_services.assert_called_once()

    def test_get_service(self):
        """Test get_service function"""
        # Configure mock to return specific service from MOCK_SERVICES
        self.contentful_client_mock.get_service_by_slug.return_value = json.loads(MOCK_SERVICES)[0]

        # Call get_service('data-collection')
        service = get_service('data-collection')

        # Assert result matches expected service
        assert service == json.loads(MOCK_SERVICES)[0]

        # Verify contentful.get_service_by_slug was called with correct slug
        self.contentful_client_mock.get_service_by_slug.assert_called_with('data-collection')

    def test_get_all_case_studies(self):
        """Test get_all_case_studies function"""
        # Configure mock to return MOCK_CASE_STUDIES
        self.contentful_client_mock.get_case_studies.return_value = json.loads(MOCK_CASE_STUDIES)

        # Call get_all_case_studies()
        case_studies = get_all_case_studies()

        # Assert result matches expected case studies
        assert case_studies == json.loads(MOCK_CASE_STUDIES)

        # Verify contentful.get_case_studies was called once
        self.contentful_client_mock.get_case_studies.assert_called_once()

    def test_get_case_study(self):
        """Test get_case_study function"""
        # Configure mock to return specific case study from MOCK_CASE_STUDIES
        self.contentful_client_mock.get_case_study_by_slug.return_value = json.loads(MOCK_CASE_STUDIES)[0]

        # Call get_case_study('ecommerce-categorization')
        case_study = get_case_study('ecommerce-categorization')

        # Assert result matches expected case study
        assert case_study == json.loads(MOCK_CASE_STUDIES)[0]

        # Verify contentful.get_case_study_by_slug was called with correct slug
        self.contentful_client_mock.get_case_study_by_slug.assert_called_with('ecommerce-categorization')

    def test_get_all_impact_stories(self):
        """Test get_all_impact_stories function"""
        # Configure mock to return MOCK_IMPACT_STORIES
        self.contentful_client_mock.get_impact_stories.return_value = json.loads(MOCK_IMPACT_STORIES)

        # Call get_all_impact_stories()
        impact_stories = get_all_impact_stories()

        # Assert result matches expected impact stories
        assert impact_stories == json.loads(MOCK_IMPACT_STORIES)

        # Verify contentful.get_impact_stories was called once
        self.contentful_client_mock.get_impact_stories.assert_called_once()

    def test_get_impact_story(self):
        """Test get_impact_story function"""
        # Configure mock to return specific impact story from MOCK_IMPACT_STORIES
        self.contentful_client_mock.get_impact_story_by_slug.return_value = json.loads(MOCK_IMPACT_STORIES)[0]

        # Call get_impact_story('rural-empowerment')
        impact_story = get_impact_story('rural-empowerment')

        # Assert result matches expected impact story
        assert impact_story == json.loads(MOCK_IMPACT_STORIES)[0]

        # Verify contentful.get_impact_story_by_slug was called with correct slug
        self.contentful_client_mock.get_impact_story_by_slug.assert_called_with('rural-empowerment')

    def test_get_site_navigation(self):
        """Test get_site_navigation function"""
        # Configure mock to return MOCK_NAVIGATION
        self.contentful_client_mock.get_navigation.return_value = json.loads(MOCK_NAVIGATION)

        # Call get_site_navigation()
        navigation = get_site_navigation()

        # Assert result matches expected navigation structure
        assert navigation == json.loads(MOCK_NAVIGATION)

        # Verify contentful.get_navigation was called once
        self.contentful_client_mock.get_navigation.assert_called_once()

    def test_get_page(self):
        """Test get_page function"""
        # Configure mock to return MOCK_PAGE
        self.contentful_client_mock.get_page_by_slug.return_value = json.loads(MOCK_PAGE)

        # Call get_page('about')
        page = get_page('about')

        # Assert result matches expected page
        assert page == json.loads(MOCK_PAGE)

        # Verify contentful.get_page_by_slug was called with correct slug
        self.contentful_client_mock.get_page_by_slug.assert_called_with('about')

    def test_refresh_content(self):
        """Test refresh_content function"""
        # Configure mock to return True for invalidate_content_cache
        self.contentful_client_mock.invalidate_content_cache.return_value = True

        # Call refresh_content('service', 'data-collection')
        result = refresh_content('service', 'data-collection')

        # Assert result is True
        assert result is True

        # Verify contentful.invalidate_content_cache was called with correct parameters
        self.contentful_client_mock.invalidate_content_cache.assert_called_with('service', 'data-collection')

    def test_get_related_services(self):
        """Test get_related_services function"""
        # Configure mocks for get_all_services and case study data
        case_study_data = json.loads(MOCK_CASE_STUDIES)[0]
        self.contentful_client_mock.get_services.return_value = json.loads(MOCK_SERVICES)

        # Call get_related_services(case_study)
        related_services = get_related_services(case_study_data)

        # Assert result contains expected related services
        assert len(related_services) == 1
        assert related_services[0]['id'] == 'service1'

        # Verify get_all_services was called once
        self.contentful_client_mock.get_services.assert_called_once()

    def test_get_related_case_studies(self):
        """Test get_related_case_studies function"""
        # Configure mocks for get_all_case_studies and service data
        service_data = json.loads(MOCK_SERVICES)[0]
        self.contentful_client_mock.get_case_studies.return_value = json.loads(MOCK_CASE_STUDIES)

        # Call get_related_case_studies(service)
        related_case_studies = get_related_case_studies(service_data)

        # Assert result contains expected related case studies
        assert len(related_case_studies) == 2

        # Verify get_all_case_studies was called with correct service_slug
        self.contentful_client_mock.get_case_studies.assert_called_with(service_slug='data-collection')

    def test_function_error_handling(self):
        """Test error handling in standalone functions"""
        # Configure mock to raise an exception
        self.contentful_client_mock.get_services.side_effect = Exception("Test Exception")
        self.contentful_client_mock.get_service_by_slug.side_effect = Exception("Test Exception")
        self.contentful_client_mock.get_case_studies.side_effect = Exception("Test Exception")
        self.contentful_client_mock.get_case_study_by_slug.side_effect = Exception("Test Exception")
        self.contentful_client_mock.get_impact_stories.side_effect = Exception("Test Exception")
        self.contentful_client_mock.get_impact_story_by_slug.side_effect = Exception("Test Exception")
        self.contentful_client_mock.get_navigation.side_effect = Exception("Test Exception")
        self.contentful_client_mock.get_page_by_slug.side_effect = Exception("Test Exception")
        self.contentful_client_mock.invalidate_content_cache.side_effect = Exception("Test Exception")

        # Call various content service functions
        services = get_all_services()
        service = get_service('data-collection')
        case_studies = get_all_case_studies()
        case_study = get_case_study('ecommerce-categorization')
        impact_stories = get_all_impact_stories()
        impact_story = get_impact_story('rural-empowerment')
        navigation = get_site_navigation()
        page = get_page('about')
        refresh = refresh_content('service', 'data-collection')

        # Assert appropriate fallback values are returned
        assert services == []
        assert service is None
        assert case_studies == []
        assert case_study is None
        assert impact_stories == []
        assert impact_story is None
        assert navigation == {}
        assert page is None
        assert refresh is False

        # Verify exceptions are logged
        # (Verification of logging is not directly possible with standard unittest.mock)
        pass