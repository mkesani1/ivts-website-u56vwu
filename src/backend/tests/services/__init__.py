"""
IndiVillage Backend Services Test Package

This package contains unit tests for the service layer of the IndiVillage backend application.
It provides common utilities, fixtures, and imports for testing service modules.

The service tests focus on business logic, data transformations, and error handling,
with appropriate mocking of external dependencies and database interactions.

Usage:
    from src.backend.tests.services import BaseServiceTestCase, mock_database_session

Tests should follow the pattern of:
    1. Setting up test data and expectations
    2. Mocking external dependencies
    3. Calling the service under test
    4. Asserting the expected outcomes
"""

import pytest
from unittest import mock

# List of exported components for this package
__all__ = [
    # Will be populated as test utilities are added
]