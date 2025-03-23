"""
Initialization module for the IndiVillage backend testing package.

This module sets up the testing environment, configures pytest, and provides
common utilities and fixtures that are shared across test modules.
"""

import os
import sys
import pytest

# Define the testing environment
TEST_ENV = 'testing'

def setup_test_environment():
    """
    Sets up the testing environment by configuring environment variables and paths.
    
    This function ensures that all tests run in a consistent environment
    with the correct settings and paths configured.
    """
    # Set environment variables for testing
    os.environ["ENVIRONMENT"] = TEST_ENV
    os.environ["TESTING"] = "True"
    
    # Ensure the project root is in the Python path
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    # Configure test-specific environment variables
    # Using in-memory SQLite database for testing
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    # Disable authentication for testing
    os.environ["DISABLE_AUTH"] = "True"
    # Set debug log level for testing
    os.environ["LOG_LEVEL"] = "DEBUG"

def pytest_configure(config):
    """
    Pytest hook that runs before test collection to configure the test environment.
    
    Args:
        config (pytest.Config): The pytest configuration object
    """
    # Set up the test environment
    setup_test_environment()
    
    # Register custom markers
    config.addinivalue_line("markers", "unit: mark test as a unit test")
    config.addinivalue_line("markers", "integration: mark test as an integration test")
    config.addinivalue_line("markers", "api: mark test as an API test")
    config.addinivalue_line("markers", "slow: mark test as a slow test")
    config.addinivalue_line("markers", "security: mark test as a security test")

def pytest_collection_modifyitems(config, items):
    """
    Pytest hook that runs after test collection to modify test items.
    
    Args:
        config (pytest.Config): The pytest configuration object
        items (List[pytest.Item]): List of collected test items
    """
    # Apply default markers based on module location
    for item in items:
        # Mark tests in unit/ directory as unit tests
        if "unit" in item.nodeid:
            item.add_marker(pytest.mark.unit)
        # Mark tests in integration/ directory as integration tests
        elif "integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        # Mark tests in api/ directory as api tests
        elif "api" in item.nodeid:
            item.add_marker(pytest.mark.api)