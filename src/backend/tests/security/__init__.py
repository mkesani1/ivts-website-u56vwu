"""
Initialization module for the IndiVillage backend security testing package.

This module provides common imports, utilities, and test data that are shared across
all security test modules, including tests for CAPTCHA verification, file scanning,
and input validation.
"""

import os
import io
import pytest
from unittest.mock import MagicMock, patch

from tests import setup_test_environment
from app.core.exceptions import SecurityException, ValidationException

# Set up the testing environment
setup_test_environment()

# Define common test constants
SECURITY_TEST_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_FILES_DIR = os.path.join(SECURITY_TEST_DIR, 'test_files')

# CAPTCHA test tokens
VALID_CAPTCHA_TOKEN = "valid_recaptcha_token"
INVALID_CAPTCHA_TOKEN = "invalid_recaptcha_token"

# Network test constants
MOCK_IP_ADDRESS = "127.0.0.1"

# Form test data
VALID_FORM_DATA = {
    "name": "Test User",
    "email": "test@example.com",
    "message": "This is a test message."
}

INVALID_FORM_DATA = {
    "name": "",
    "email": "invalid-email",
    "message": ""
}


def create_test_file(content, filename=None, directory=TEST_FILES_DIR):
    """
    Creates a temporary test file with specified content for security testing.
    
    Args:
        content (str): The content to write to the test file
        filename (str, optional): The name of the file to create. If None, a unique name is generated.
        directory (str, optional): The directory to create the file in. Defaults to TEST_FILES_DIR.
        
    Returns:
        str: Path to the created test file
    """
    # Create directory if it doesn't exist
    os.makedirs(directory, exist_ok=True)
    
    # Generate a unique filename if not provided
    if filename is None:
        import uuid
        filename = f"test_file_{uuid.uuid4().hex}.txt"
    
    file_path = os.path.join(directory, filename)
    
    # Write content to the file
    with open(file_path, 'w') as f:
        f.write(content)
    
    return file_path


def create_test_file_with_size(size_bytes, filename=None, directory=TEST_FILES_DIR):
    """
    Creates a test file with a specific size for testing file size validation.
    
    Args:
        size_bytes (int): The size of the file to create in bytes
        filename (str, optional): The name of the file to create. If None, a unique name is generated.
        directory (str, optional): The directory to create the file in. Defaults to TEST_FILES_DIR.
        
    Returns:
        str: Path to the created test file
    """
    # Create directory if it doesn't exist
    os.makedirs(directory, exist_ok=True)
    
    # Generate a unique filename if not provided
    if filename is None:
        import uuid
        filename = f"test_file_{uuid.uuid4().hex}.bin"
    
    file_path = os.path.join(directory, filename)
    
    # Create a file with random data of the specified size
    with open(file_path, 'wb') as f:
        f.write(os.urandom(size_bytes))
    
    return file_path


def cleanup_test_files(directory=TEST_FILES_DIR):
    """
    Removes test files created during testing.
    
    Args:
        directory (str, optional): The directory containing test files to clean up.
                                   Defaults to TEST_FILES_DIR.
    """
    # Check if directory exists
    if not os.path.exists(directory):
        return
    
    # Iterate through files in the directory
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            # Remove the file
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f"Error cleaning up file {file_path}: {e}")


def create_mock_request(headers=None, form_data=None, query_params=None, json_data=None, remote_addr=MOCK_IP_ADDRESS):
    """
    Creates a mock HTTP request object for testing security components.
    
    Args:
        headers (dict, optional): HTTP headers for the request. Defaults to empty dict.
        form_data (dict, optional): Form data for the request. Defaults to empty dict.
        query_params (dict, optional): Query parameters for the request. Defaults to empty dict.
        json_data (dict, optional): JSON body for the request. Defaults to empty dict.
        remote_addr (str, optional): IP address for the request. Defaults to MOCK_IP_ADDRESS.
        
    Returns:
        object: Mock request object with specified attributes
    """
    # Create default values
    headers = headers or {}
    form_data = form_data or {}
    query_params = query_params or {}
    json_data = json_data or {}
    
    # Create a mock object
    mock_request = MagicMock()
    
    # Set attributes
    mock_request.headers = headers
    mock_request.form = form_data
    mock_request.args = query_params
    mock_request.json = MagicMock(return_value=json_data)
    mock_request.remote_addr = remote_addr
    
    return mock_request


class MockResponse:
    """
    Mock HTTP response class for testing security API interactions.
    """
    
    def __init__(self, json_data, status_code=200):
        """
        Initialize the mock response with JSON data and status code.
        
        Args:
            json_data (dict): The JSON response data
            status_code (int): The HTTP status code
        """
        self.json_data = json_data
        self.status_code = status_code
    
    def json(self):
        """
        Return the JSON data of the response.
        
        Returns:
            dict: The JSON data
        """
        return self.json_data
    
    def raise_for_status(self):
        """
        Simulate the raise_for_status method of requests.Response.
        
        Raises:
            HTTPError: If the status code is >= 400
        """
        if self.status_code >= 400:
            from requests.exceptions import HTTPError
            raise HTTPError(f"HTTP Error: {self.status_code}")