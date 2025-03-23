"""
API Tests Package for IndiVillage.com Backend Application.

This package contains test modules for the backend API endpoints.
It provides common imports, utilities, and fixtures that are
shared across API test modules.
"""

import pytest

# API prefix for constructing endpoint URLs
API_PREFIX = '/api/v1'

def get_api_url(endpoint):
    """
    Constructs a full API URL path by combining the API prefix with the provided endpoint.
    
    Args:
        endpoint (str): The API endpoint path, with or without a leading slash
        
    Returns:
        str: Full API URL path
    
    Example:
        >>> get_api_url('/services')
        '/api/v1/services'
        >>> get_api_url('form-submission')
        '/api/v1/form-submission'
    """
    # Remove leading slash from endpoint if present
    if endpoint.startswith('/'):
        endpoint = endpoint[1:]
    
    # Combine API_PREFIX with endpoint
    return f"{API_PREFIX}/{endpoint}"