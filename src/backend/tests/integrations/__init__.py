"""
Initialization module for the integration tests package in the IndiVillage backend application.

This module provides utilities and base classes for testing integrations with 
external services like Contentful, HubSpot, AWS S3, and SendGrid.
"""

import json
import pytest
from unittest.mock import Mock, patch, MagicMock  # unittest.mock version standard library

from tests import setup_test_environment

# Define integration test marker
INTEGRATION_TEST_MARKER = pytest.mark.integration

def pytest_configure(config):
    """
    Pytest hook that runs before test collection to configure integration test markers.
    
    Args:
        config (pytest.Config): The pytest configuration object
    """
    # Register integration test marker
    config.addinivalue_line("markers", 
                           "integration: mark test as an integration test with external services")
    # Configure any integration test-specific settings

def create_mock_response(data, status_code=200):
    """
    Creates a standardized mock response object for external API calls.
    
    Args:
        data (dict): The response data to include in the mock
        status_code (int): The HTTP status code to include in the mock
        
    Returns:
        Mock: Mock response object with the specified data and status code
    """
    mock_response = Mock()
    mock_response.status_code = status_code
    mock_response.json = lambda: data
    mock_response.text = json.dumps(data)
    return mock_response

@INTEGRATION_TEST_MARKER
class IntegrationTestBase:
    """
    Base class for integration tests providing common setup and utility methods.
    """
    
    def __init__(self):
        """
        Initializes the IntegrationTestBase class.
        """
        # Initialize any common attributes
        self.mocks = {}
        
    def setup_method(self, method):
        """
        Setup method that runs before each test method.
        
        Args:
            method (function): The test method being run
        """
        # Set up common test fixtures
        self.mocks = {}
        # Initialize mocks for external services
        
    def teardown_method(self, method):
        """
        Teardown method that runs after each test method.
        
        Args:
            method (function): The test method being run
        """
        # Clean up any resources created during the test
        # Reset any mocks or patches
        for mock_name, mock_patch in self.mocks.items():
            if hasattr(mock_patch, 'stop'):
                mock_patch.stop()
        
    def mock_external_service(self, service_name):
        """
        Creates a standardized mock for an external service.
        
        Args:
            service_name (str): The name of the service to mock
            
        Returns:
            Mock: Configured mock for the specified service
        """
        # Create appropriate mock based on service_name
        mock = MagicMock()
        
        # Configure common mock behaviors for the service
        if service_name == 'contentful':
            # Configure contentful-specific mock behavior
            pass
        elif service_name == 'hubspot':
            # Configure hubspot-specific mock behavior
            pass
        elif service_name == 's3':
            # Configure s3-specific mock behavior
            pass
        elif service_name == 'sendgrid':
            # Configure sendgrid-specific mock behavior
            pass
        else:
            raise ValueError(f"Unknown service: {service_name}")
            
        # Store the mock for cleanup in teardown
        self.mocks[service_name] = mock
        
        return mock