import os
import tempfile
import uuid
from unittest import mock

import pytest  # version: ^7.3.1
import boto3  # version: ^1.26.0
from botocore.exceptions import ClientError  # version: ^1.29.0

from app.integrations.aws_s3 import S3Client, generate_object_key
from app.core.config import settings
from app.utils.file_utils import create_temp_file

# Test constants
TEST_FILE_CONTENT = "Test file content for S3 integration tests"
TEST_BUCKET_NAME = settings.AWS_S3_UPLOAD_BUCKET_NAME
TEST_PROCESSED_BUCKET_NAME = settings.AWS_S3_PROCESSED_BUCKET_NAME
TEST_QUARANTINE_BUCKET_NAME = settings.AWS_S3_QUARANTINE_BUCKET_NAME


@pytest.fixture
def setup_s3_client():
    """
    Fixture to create an S3Client instance for testing.
    
    Returns:
        S3Client: Configured S3Client instance for testing
    """
    # Create client with test credentials
    client = S3Client()
    return client


@pytest.fixture
def create_test_file():
    """
    Fixture to create a temporary test file for S3 operations.
    
    Returns:
        str: Path to the created temporary file
    """
    # Create a temporary file with test content
    temp_file_path = create_temp_file(TEST_FILE_CONTENT.encode(), prefix="test_", suffix=".txt")
    
    # Yield the file path for use in tests
    yield temp_file_path
    
    # Clean up the temporary file after tests
    if os.path.exists(temp_file_path):
        os.remove(temp_file_path)


@pytest.fixture
def mock_s3_client():
    """
    Fixture to create a mocked S3Client for isolated testing.
    
    Returns:
        mock.MagicMock: Mocked S3Client instance
    """
    # Create a MagicMock for S3Client
    mock_client = mock.MagicMock(spec=S3Client)
    
    # Configure common mock returns
    mock_client.generate_presigned_post.return_value = {
        "url": "https://test-bucket.s3.amazonaws.com",
        "fields": {
            "key": "test-object-key",
            "AWSAccessKeyId": "test-access-key",
            "x-amz-server-side-encryption": "AES256"
        }
    }
    mock_client.generate_presigned_url.return_value = "https://test-bucket.s3.amazonaws.com/test-object-key?signature=test"
    mock_client.upload_file.return_value = True
    mock_client.download_file.return_value = True
    mock_client.delete_file.return_value = True
    mock_client.copy_file.return_value = True
    mock_client.move_to_quarantine.return_value = True
    mock_client.check_file_exists.return_value = True
    mock_client.get_file_size.return_value = len(TEST_FILE_CONTENT)
    mock_client.get_file_metadata.return_value = {"custom-meta": "test-value"}
    
    return mock_client


def test_generate_presigned_post(setup_s3_client):
    """
    Tests generating a presigned POST URL for direct file upload.
    """
    s3_client = setup_s3_client
    
    # Generate a unique object key for testing
    object_key = generate_object_key("test_file.txt", prefix="test/")
    
    # Call the method to test
    response = s3_client.generate_presigned_post(
        object_key=object_key,
        content_type="text/plain",
        expiration=3600,
        bucket_name=TEST_BUCKET_NAME
    )
    
    # Assertions
    assert response is not None
    assert "url" in response
    assert "fields" in response
    assert "key" in response["fields"]
    assert response["fields"]["key"] == object_key
    assert "x-amz-server-side-encryption" in response["fields"]
    assert response["fields"]["x-amz-server-side-encryption"] == "AES256"


def test_generate_presigned_url(setup_s3_client):
    """
    Tests generating a presigned URL for downloading a file.
    """
    s3_client = setup_s3_client
    
    # Generate a unique object key for testing
    object_key = generate_object_key("test_file.txt", prefix="test/")
    
    # Call the method to test
    url = s3_client.generate_presigned_url(
        object_key=object_key,
        bucket_name=TEST_PROCESSED_BUCKET_NAME,
        expiration=3600
    )
    
    # Assertions
    assert url is not None
    assert isinstance(url, str)
    assert TEST_PROCESSED_BUCKET_NAME in url
    assert object_key in url
    assert "AWSAccessKeyId" in url or "X-Amz-Credential" in url


def test_upload_file(setup_s3_client, create_test_file):
    """
    Tests uploading a file to S3 with server-side encryption.
    """
    s3_client = setup_s3_client
    test_file_path = create_test_file
    
    # Generate a unique object key for testing
    object_key = generate_object_key("test_upload.txt", prefix="test/")
    
    # Call the method to test
    result = s3_client.upload_file(
        file_path=test_file_path,
        object_key=object_key,
        bucket_name=TEST_BUCKET_NAME,
        metadata={"test-key": "test-value"}
    )
    
    # Assertions
    assert result is True
    
    # Verify the file exists in S3
    exists = s3_client.check_file_exists(
        object_key=object_key,
        bucket_name=TEST_BUCKET_NAME
    )
    assert exists is True
    
    # Clean up: delete the uploaded file
    s3_client.delete_file(
        object_key=object_key,
        bucket_name=TEST_BUCKET_NAME
    )


def test_download_file(setup_s3_client, create_test_file):
    """
    Tests downloading a file from S3 to local filesystem.
    """
    s3_client = setup_s3_client
    test_file_path = create_test_file
    
    # Generate a unique object key for testing
    object_key = generate_object_key("test_download.txt", prefix="test/")
    
    # First, upload the test file
    upload_result = s3_client.upload_file(
        file_path=test_file_path,
        object_key=object_key,
        bucket_name=TEST_BUCKET_NAME
    )
    assert upload_result is True
    
    # Create a temporary download path
    download_path = os.path.join(tempfile.gettempdir(), f"s3_test_download_{uuid.uuid4().hex}.txt")
    
    # Call the method to test
    result = s3_client.download_file(
        object_key=object_key,
        download_path=download_path,
        bucket_name=TEST_BUCKET_NAME
    )
    
    # Assertions
    assert result is True
    
    # Verify the downloaded file exists and has correct content
    assert os.path.exists(download_path)
    with open(download_path, "r") as f:
        content = f.read()
    assert content == TEST_FILE_CONTENT
    
    # Clean up: delete the uploaded file from S3 and the downloaded file
    s3_client.delete_file(
        object_key=object_key,
        bucket_name=TEST_BUCKET_NAME
    )
    if os.path.exists(download_path):
        os.remove(download_path)


def test_delete_file(setup_s3_client, create_test_file):
    """
    Tests deleting a file from S3.
    """
    s3_client = setup_s3_client
    test_file_path = create_test_file
    
    # Generate a unique object key for testing
    object_key = generate_object_key("test_delete.txt", prefix="test/")
    
    # First, upload the test file
    upload_result = s3_client.upload_file(
        file_path=test_file_path,
        object_key=object_key,
        bucket_name=TEST_BUCKET_NAME
    )
    assert upload_result is True
    
    # Verify the file exists in S3 using check_file_exists
    exists_before = s3_client.check_file_exists(
        object_key=object_key,
        bucket_name=TEST_BUCKET_NAME
    )
    assert exists_before is True
    
    # Call the method to test
    result = s3_client.delete_file(
        object_key=object_key,
        bucket_name=TEST_BUCKET_NAME
    )
    
    # Assertions
    assert result is True
    
    # Verify the file no longer exists in S3 using check_file_exists
    exists_after = s3_client.check_file_exists(
        object_key=object_key,
        bucket_name=TEST_BUCKET_NAME
    )
    assert exists_after is False


def test_copy_file(setup_s3_client, create_test_file):
    """
    Tests copying a file from one S3 location to another.
    """
    s3_client = setup_s3_client
    test_file_path = create_test_file
    
    # Generate unique source and destination object keys
    source_key = generate_object_key("test_source.txt", prefix="test/source/")
    destination_key = generate_object_key("test_destination.txt", prefix="test/destination/")
    
    # First, upload the test file to the source location
    upload_result = s3_client.upload_file(
        file_path=test_file_path,
        object_key=source_key,
        bucket_name=TEST_BUCKET_NAME
    )
    assert upload_result is True
    
    # Call the method to test
    result = s3_client.copy_file(
        source_key=source_key,
        destination_key=destination_key,
        source_bucket=TEST_BUCKET_NAME,
        destination_bucket=TEST_PROCESSED_BUCKET_NAME
    )
    
    # Assertions
    assert result is True
    
    # Verify both source and destination files exist in S3
    source_exists = s3_client.check_file_exists(
        object_key=source_key,
        bucket_name=TEST_BUCKET_NAME
    )
    destination_exists = s3_client.check_file_exists(
        object_key=destination_key,
        bucket_name=TEST_PROCESSED_BUCKET_NAME
    )
    
    assert source_exists is True
    assert destination_exists is True
    
    # Clean up by deleting both files from S3
    s3_client.delete_file(
        object_key=source_key,
        bucket_name=TEST_BUCKET_NAME
    )
    s3_client.delete_file(
        object_key=destination_key,
        bucket_name=TEST_PROCESSED_BUCKET_NAME
    )


def test_move_to_quarantine(setup_s3_client, create_test_file):
    """
    Tests moving a file to the quarantine bucket for security isolation.
    """
    s3_client = setup_s3_client
    test_file_path = create_test_file
    
    # Generate a unique object key for testing
    object_key = generate_object_key("test_quarantine.txt", prefix="test/")
    
    # First, upload the test file
    upload_result = s3_client.upload_file(
        file_path=test_file_path,
        object_key=object_key,
        bucket_name=TEST_BUCKET_NAME
    )
    assert upload_result is True
    
    # Call the method to test
    result = s3_client.move_to_quarantine(
        source_key=object_key,
        source_bucket=TEST_BUCKET_NAME
    )
    
    # Assertions
    assert result is True
    
    # Verify the file no longer exists in the original bucket
    source_exists = s3_client.check_file_exists(
        object_key=object_key,
        bucket_name=TEST_BUCKET_NAME
    )
    assert source_exists is False
    
    # Verify the file exists in the quarantine bucket
    quarantine_key = f"quarantine/{os.path.basename(object_key)}"
    quarantine_exists = s3_client.check_file_exists(
        object_key=quarantine_key,
        bucket_name=TEST_QUARANTINE_BUCKET_NAME
    )
    assert quarantine_exists is True
    
    # Clean up by deleting the file from the quarantine bucket
    s3_client.delete_file(
        object_key=quarantine_key,
        bucket_name=TEST_QUARANTINE_BUCKET_NAME
    )


def test_check_file_exists(setup_s3_client, create_test_file):
    """
    Tests checking if a file exists in S3.
    """
    s3_client = setup_s3_client
    test_file_path = create_test_file
    
    # Generate a unique object key for testing
    object_key = generate_object_key("test_exists.txt", prefix="test/")
    
    # Check that a non-existent file returns False
    exists_before = s3_client.check_file_exists(
        object_key=object_key,
        bucket_name=TEST_BUCKET_NAME
    )
    assert exists_before is False
    
    # Upload the test file
    upload_result = s3_client.upload_file(
        file_path=test_file_path,
        object_key=object_key,
        bucket_name=TEST_BUCKET_NAME
    )
    assert upload_result is True
    
    # Check that the existing file returns True
    exists_after = s3_client.check_file_exists(
        object_key=object_key,
        bucket_name=TEST_BUCKET_NAME
    )
    assert exists_after is True
    
    # Clean up by deleting the file from S3
    s3_client.delete_file(
        object_key=object_key,
        bucket_name=TEST_BUCKET_NAME
    )


def test_get_file_size(setup_s3_client, create_test_file):
    """
    Tests getting the size of a file in S3.
    """
    s3_client = setup_s3_client
    test_file_path = create_test_file
    
    # Generate a unique object key for testing
    object_key = generate_object_key("test_size.txt", prefix="test/")
    
    # Get the size of the local test file
    local_size = os.path.getsize(test_file_path)
    
    # Upload test file to S3 using upload_file
    upload_result = s3_client.upload_file(
        file_path=test_file_path,
        object_key=object_key,
        bucket_name=TEST_BUCKET_NAME
    )
    assert upload_result is True
    
    # Call get_file_size with the object key
    s3_size = s3_client.get_file_size(
        object_key=object_key,
        bucket_name=TEST_BUCKET_NAME
    )
    
    # Assert that the returned size matches the local file size
    assert s3_size == local_size
    
    # Clean up by deleting the file from S3
    s3_client.delete_file(
        object_key=object_key,
        bucket_name=TEST_BUCKET_NAME
    )


def test_get_file_metadata(setup_s3_client, create_test_file):
    """
    Tests getting the metadata of a file in S3.
    """
    s3_client = setup_s3_client
    test_file_path = create_test_file
    
    # Generate a unique object key for testing
    object_key = generate_object_key("test_metadata.txt", prefix="test/")
    
    # Custom metadata to include with the file
    custom_metadata = {
        "test-meta-key": "test-meta-value",
        "content-owner": "integration-tests"
    }
    
    # Upload test file to S3 with custom metadata using upload_file
    upload_result = s3_client.upload_file(
        file_path=test_file_path,
        object_key=object_key,
        bucket_name=TEST_BUCKET_NAME,
        metadata=custom_metadata
    )
    assert upload_result is True
    
    # Call get_file_metadata with the object key
    metadata = s3_client.get_file_metadata(
        object_key=object_key,
        bucket_name=TEST_BUCKET_NAME
    )
    
    # Assert that the returned metadata contains the custom metadata
    assert metadata is not None
    assert isinstance(metadata, dict)
    
    for key, value in custom_metadata.items():
        assert key in metadata
        assert metadata[key] == value
    
    # Clean up by deleting the file from S3
    s3_client.delete_file(
        object_key=object_key,
        bucket_name=TEST_BUCKET_NAME
    )


def test_generate_object_key():
    """
    Tests generating a unique object key for S3 storage.
    """
    # Define test filename and prefix
    filename = "test file.txt"
    prefix = "uploads/"
    
    # Call generate_object_key with the test parameters
    object_key = generate_object_key(filename, prefix)
    
    # Assert that the generated key contains the prefix
    assert object_key.startswith(prefix)
    
    # Assert that the generated key contains a sanitized version of the filename
    assert "test_file.txt" in object_key
    
    # Assert that the generated key contains a UUID for uniqueness
    # UUID part should be 32 characters long
    assert len(object_key.split("/")[-1].split("_")[0]) == 32


@mock.patch('boto3.client')
def test_s3_client_with_mocks(mock_boto_client):
    """
    Tests S3Client using mocked boto3 clients.
    """
    # Configure the mocked boto3.client to return a mock S3 client
    mock_s3 = mock.MagicMock()
    mock_boto_client.return_value = mock_s3
    
    # Configure mock responses for S3 operations
    mock_s3.generate_presigned_post.return_value = {
        "url": "https://mock-bucket.s3.amazonaws.com",
        "fields": {"key": "mock-key"}
    }
    mock_s3.generate_presigned_url.return_value = "https://mock-url"
    mock_s3.head_object.return_value = {
        "ContentLength": 100,
        "Metadata": {"test-key": "test-value"}
    }
    
    # Create an S3Client instance with the mocked boto3
    client = S3Client()
    
    # Test generate_presigned_post
    post_result = client.generate_presigned_post("test-key", "text/plain")
    assert "url" in post_result
    assert "fields" in post_result
    mock_s3.generate_presigned_post.assert_called_once()
    
    # Test generate_presigned_url
    url_result = client.generate_presigned_url("test-key")
    assert url_result == "https://mock-url"
    mock_s3.generate_presigned_url.assert_called_once()
    
    # Test check_file_exists
    client.check_file_exists("test-key")
    mock_s3.head_object.assert_called_once()
    
    # Test get_file_size
    size_result = client.get_file_size("test-key")
    assert size_result == 100
    
    # Test get_file_metadata
    metadata_result = client.get_file_metadata("test-key")
    assert metadata_result == {"test-key": "test-value"}