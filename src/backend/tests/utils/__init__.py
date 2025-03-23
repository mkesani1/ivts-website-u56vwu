"""
Initialization module for the utils test package of IndiVillage backend application.

This module provides common imports and utilities for testing the utility functions 
of the backend application. It enables test discovery and shared functionality
across utility test modules.

Typical usage:
    from tests.utils import some_fixture, some_helper_function
"""

import pytest  # pytest 7.3.1

__version__ = "1.0.0"

# Common test fixtures and utilities for utility functions can be defined here
# to be shared across multiple test modules

# Example of a shared fixture (uncomment and modify as needed):
# @pytest.fixture
# def sample_data():
#     """Provide sample data for utility function tests."""
#     return {
#         "key1": "value1",
#         "key2": "value2"
#     }