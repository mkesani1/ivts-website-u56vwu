import pytest
import os
import tempfile
import shutil
import uuid
from unittest import mock

import magic  # python-magic v0.4.27

from app.utils.file_utils import (
    validate_file_type,
    validate_file_size,
    get_file_extension,
    get_mime_type,
    create_temp_file,
    delete_file,
    ensure_directory_exists,
    generate_secure_filename,
    generate_unique_filename,
    is_valid_file,
    copy_file,
    move_file,
    get_file_size,
    strip_file_metadata,
    create_file_hash,
    ALLOWED_EXTENSIONS,
    MAX_UPLOAD_SIZE_BYTES
)


def test_validate_file_type_valid():
    """Tests that validate_file_type correctly identifies valid file types"""
    # Test cases with valid file types
    valid_cases = [
        ("test.csv", "text/csv"),
        ("data.json", "application/json"),
        ("file.xml", "application/xml"),
        ("image.jpg", "image/jpeg"),
        ("photo.png", "image/png"),
        ("scan.tiff", "image/tiff"),
        ("recording.mp3", "audio/mpeg"),
        ("sound.wav", "audio/wav"),
        ("test.txt", "text/plain"),  # For CSV files
        ("data.json", "text/json"),  # Alternative JSON MIME type
    ]
    
    for filename, content_type in valid_cases:
        assert validate_file_type(filename, content_type) is True, f"Should accept {filename} with {content_type}"


def test_validate_file_type_invalid():
    """Tests that validate_file_type correctly rejects invalid file types"""
    # Test cases with invalid file types
    invalid_cases = [
        # Invalid extensions
        ("test.exe", "application/octet-stream"),
        ("script.php", "text/x-php"),
        ("document.pdf", "application/pdf"),
        ("archive.zip", "application/zip"),
        
        # Mismatched content types
        ("data.csv", "application/pdf"),
        ("image.jpg", "application/javascript"),
        
        # Empty or None values
        ("", "text/plain"),
        (None, "text/plain"),
        ("test.csv", ""),
        ("test.csv", None),
    ]
    
    for filename, content_type in invalid_cases:
        assert validate_file_type(filename, content_type) is False, f"Should reject {filename} with {content_type}"


def test_validate_file_size_valid():
    """Tests that validate_file_size correctly accepts files within size limits"""
    # Test cases with valid file sizes
    valid_sizes = [
        1,                      # Minimum valid size
        1024,                   # 1 KB
        1024 * 1024,            # 1 MB
        10 * 1024 * 1024,       # 10 MB
        MAX_UPLOAD_SIZE_BYTES,  # Maximum allowed size
    ]
    
    for size in valid_sizes:
        assert validate_file_size(size) is True, f"Should accept size of {size} bytes"


def test_validate_file_size_invalid():
    """Tests that validate_file_size correctly rejects files exceeding size limits"""
    # Test cases with invalid file sizes
    invalid_sizes = [
        0,                         # Empty file
        -1,                        # Negative size
        MAX_UPLOAD_SIZE_BYTES + 1, # Exceeds maximum by 1 byte
        100 * 1024 * 1024,         # 100 MB
    ]
    
    for size in invalid_sizes:
        assert validate_file_size(size) is False, f"Should reject size of {size} bytes"


def test_get_file_extension():
    """Tests that get_file_extension correctly extracts file extensions"""
    # Test cases: filename and expected extension
    test_cases = [
        ("test.csv", "csv"),
        ("data.json", "json"),
        ("image.jpg", "jpg"),
        ("document.PDF", "pdf"),  # Test case conversion
        ("file.with.multiple.dots.txt", "txt"),  # Multiple dots
        ("noextension", ""),  # No extension
        (".hiddenfile", "hiddenfile"),  # Hidden file
        ("", ""),  # Empty string
        (None, ""),  # None value
    ]
    
    for filename, expected in test_cases:
        assert get_file_extension(filename) == expected, f"Failed for filename: {filename}"


def test_get_mime_type():
    """Tests that get_mime_type correctly identifies MIME types"""
    # Create temporary test files with different content
    temp_dir = tempfile.mkdtemp()
    try:
        # Create a text file
        text_file = os.path.join(temp_dir, "test.txt")
        with open(text_file, "w") as f:
            f.write("Sample text content")
        
        # Create a CSV file
        csv_file = os.path.join(temp_dir, "test.csv")
        with open(csv_file, "w") as f:
            f.write("Name,Age\nJohn,30\nJane,25")
        
        # Create a JSON file
        json_file = os.path.join(temp_dir, "test.json")
        with open(json_file, "w") as f:
            f.write('{"name": "John", "age": 30}')
        
        # Test MIME type detection
        assert "text/" in get_mime_type(text_file).lower(), f"Failed to detect text file: {text_file}"
        assert "text/" in get_mime_type(csv_file).lower(), f"Failed to detect CSV file: {csv_file}"
        assert "json" in get_mime_type(json_file).lower() or "text/" in get_mime_type(json_file).lower(), \
            f"Failed to detect JSON file: {json_file}"
        
        # Test nonexistent file
        assert get_mime_type("nonexistent_file.txt") == "", "Should return empty string for nonexistent file"
        
    finally:
        # Clean up temporary directory
        shutil.rmtree(temp_dir)


@mock.patch('magic.from_file')
def test_get_mime_type_with_mock(mock_from_file):
    """Tests get_mime_type with mocked magic library"""
    # Set up mock return value
    mock_from_file.return_value = "text/csv"
    
    # Test with a dummy path
    mime_type = get_mime_type("/path/to/file.csv")
    
    # Verify results
    assert mime_type == "text/csv", "Should return the mocked MIME type"
    mock_from_file.assert_called_once_with("/path/to/file.csv", mime=True)
    
    # Test exception handling
    mock_from_file.side_effect = Exception("Simulated error")
    mime_type = get_mime_type("/path/to/file.csv")
    
    # Should fall back to mimetypes module or return empty string
    assert mime_type == "" or mime_type is not None, "Should handle exceptions gracefully"


def test_create_temp_file():
    """Tests that create_temp_file correctly creates temporary files"""
    # Test data
    test_content = b"Test file content"
    prefix = "test_prefix_"
    suffix = ".txt"
    
    try:
        # Create temporary file
        temp_path = create_temp_file(test_content, prefix, suffix)
        
        # Verify the file exists
        assert os.path.exists(temp_path), "Temporary file should exist"
        assert os.path.isfile(temp_path), "Path should point to a file"
        
        # Verify the file name format
        filename = os.path.basename(temp_path)
        assert filename.startswith(prefix), f"Filename should start with '{prefix}'"
        assert filename.endswith(suffix), f"Filename should end with '{suffix}'"
        
        # Verify the content
        with open(temp_path, "rb") as f:
            content = f.read()
        assert content == test_content, "File content should match the input"
        
    finally:
        # Clean up
        if 'temp_path' in locals() and os.path.exists(temp_path):
            os.remove(temp_path)


def test_delete_file():
    """Tests that delete_file correctly deletes files"""
    # Create a temporary file
    fd, temp_path = tempfile.mkstemp()
    os.close(fd)
    
    try:
        # Verify the file exists
        assert os.path.exists(temp_path), "Temporary file should exist initially"
        
        # Delete the file
        result = delete_file(temp_path)
        
        # Verify the result and file deletion
        assert result is True, "delete_file should return True for successful deletion"
        assert not os.path.exists(temp_path), "File should no longer exist after deletion"
        
    finally:
        # Ensure cleanup if the test fails
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_delete_file_nonexistent():
    """Tests that delete_file handles nonexistent files gracefully"""
    # Generate a path that doesn't exist
    nonexistent_path = f"/tmp/nonexistent_file_{uuid.uuid4()}.txt"
    
    # Attempt to delete the nonexistent file
    result = delete_file(nonexistent_path)
    
    # Verify the result
    assert result is False, "delete_file should return False for nonexistent files"


def test_ensure_directory_exists():
    """Tests that ensure_directory_exists creates directories as needed"""
    # Generate a path to a temporary directory
    temp_dir = os.path.join(tempfile.gettempdir(), f"test_dir_{uuid.uuid4()}")
    
    try:
        # Verify the directory doesn't exist initially
        assert not os.path.exists(temp_dir), "Test directory should not exist initially"
        
        # Create the directory
        result = ensure_directory_exists(temp_dir)
        
        # Verify the result and directory creation
        assert result is True, "ensure_directory_exists should return True"
        assert os.path.exists(temp_dir), "Directory should exist after creation"
        assert os.path.isdir(temp_dir), "Path should point to a directory"
        
    finally:
        # Clean up
        if os.path.exists(temp_dir):
            os.rmdir(temp_dir)


def test_ensure_directory_exists_already_exists():
    """Tests that ensure_directory_exists handles existing directories gracefully"""
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Verify the directory exists
        assert os.path.exists(temp_dir), "Temporary directory should exist"
        
        # Call ensure_directory_exists on the existing directory
        result = ensure_directory_exists(temp_dir)
        
        # Verify the result
        assert result is True, "ensure_directory_exists should return True for existing directories"
        assert os.path.exists(temp_dir), "Directory should still exist"
        
    finally:
        # Clean up
        if os.path.exists(temp_dir):
            os.rmdir(temp_dir)


def test_generate_secure_filename():
    """Tests that generate_secure_filename sanitizes filenames correctly"""
    # Test cases: input filename and expected sanitized output
    test_cases = [
        # Basic case
        ("test.txt", "test.txt"),
        
        # Special characters
        ("test!@#$%^&*.txt", "test_____.txt"),
        
        # Path traversal attempts
        ("../../../etc/passwd", "etc_passwd"),
        ("..\\..\\Windows\\System32\\cmd.exe", "Windows_System32_cmd.exe"),
        
        # Spaces and non-ASCII characters
        ("file with spaces.txt", "file_with_spaces.txt"),
        ("résumé.pdf", "r_sum_.pdf"),
        
        # Leading/trailing dots
        (".hidden.txt", "hidden.txt"),
        ("document.txt.", "document.txt"),
        
        # Very long filenames
        ("a" * 300 + ".txt", "a" * 200 + ".txt"),
        
        # Empty or None values
        ("", "unnamed"),
        (None, "unnamed"),
    ]
    
    for original, expected in test_cases:
        result = generate_secure_filename(original)
        assert result == expected, f"Failed for '{original}', got '{result}' instead of '{expected}'"


@mock.patch('uuid.uuid4')
def test_generate_unique_filename(mock_uuid4):
    """Tests that generate_unique_filename creates unique filenames"""
    # Set up mock UUID
    mock_uuid = "abcdef1234567890"
    mock_uuid4.return_value = type('MockUUID', (), {'hex': mock_uuid})
    
    # Test cases
    original_filename = "test.txt"
    prefix = "upload_"
    
    # Generate unique filename
    result = generate_unique_filename(original_filename, prefix)
    
    # Verify the result
    expected = f"{prefix}test_{mock_uuid}.txt"
    assert result == expected, f"Expected '{expected}', got '{result}'"
    
    # Verify mock was called
    mock_uuid4.assert_called_once()
    
    # Test with no prefix
    result = generate_unique_filename(original_filename)
    expected = f"test_{mock_uuid}.txt"
    assert result == expected, f"Expected '{expected}', got '{result}'"


def test_is_valid_file():
    """Tests that is_valid_file performs comprehensive file validation"""
    # Create temporary files for testing
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Create a valid file (small CSV)
        valid_file = os.path.join(temp_dir, "valid.csv")
        with open(valid_file, "w") as f:
            f.write("header1,header2\nvalue1,value2")
        
        # Create a file that's too large
        large_file = os.path.join(temp_dir, "large.csv")
        with open(large_file, "wb") as f:
            # Write a file slightly larger than the maximum size
            f.write(b"0" * (MAX_UPLOAD_SIZE_BYTES + 1000))
        
        # Test valid file
        is_valid, error = is_valid_file(valid_file, "valid.csv", "text/csv")
        assert is_valid is True, f"Should accept valid file, got error: {error}"
        assert error == "", "Error message should be empty for valid files"
        
        # Test file that's too large
        is_valid, error = is_valid_file(large_file, "large.csv", "text/csv")
        assert is_valid is False, "Should reject file that's too large"
        assert "size exceeds" in error.lower(), f"Error should mention size limit, got: {error}"
        
        # Test invalid file type
        is_valid, error = is_valid_file(valid_file, "invalid.exe", "application/octet-stream")
        assert is_valid is False, "Should reject file with invalid type"
        assert "type not allowed" in error.lower(), f"Error should mention file type, got: {error}"
        
        # Test nonexistent file
        is_valid, error = is_valid_file("/nonexistent/path.csv", "nonexistent.csv", "text/csv")
        assert is_valid is False, "Should reject nonexistent file"
        assert "not found" in error.lower(), f"Error should mention file not found, got: {error}"
        
    finally:
        # Clean up
        shutil.rmtree(temp_dir)


def test_copy_file():
    """Tests that copy_file correctly copies files"""
    # Create source file
    source_dir = tempfile.mkdtemp()
    dest_dir = tempfile.mkdtemp()
    
    try:
        # Create source file with content
        source_path = os.path.join(source_dir, "source.txt")
        with open(source_path, "w") as f:
            f.write("Test content")
        
        # Define destination path
        dest_path = os.path.join(dest_dir, "destination.txt")
        
        # Copy the file
        result = copy_file(source_path, dest_path)
        
        # Verify the result
        assert result is True, "copy_file should return True for successful copy"
        assert os.path.exists(dest_path), "Destination file should exist after copying"
        
        # Verify the content
        with open(dest_path, "r") as f:
            content = f.read()
        assert content == "Test content", "Destination file should have the same content as source"
        
        # Verify source file still exists
        assert os.path.exists(source_path), "Source file should still exist after copying"
        
    finally:
        # Clean up
        shutil.rmtree(source_dir)
        shutil.rmtree(dest_dir)


def test_move_file():
    """Tests that move_file correctly moves files"""
    # Create source and destination directories
    source_dir = tempfile.mkdtemp()
    dest_dir = tempfile.mkdtemp()
    
    try:
        # Create source file with content
        source_path = os.path.join(source_dir, "source.txt")
        with open(source_path, "w") as f:
            f.write("Test content")
        
        # Define destination path
        dest_path = os.path.join(dest_dir, "destination.txt")
        
        # Move the file
        result = move_file(source_path, dest_path)
        
        # Verify the result
        assert result is True, "move_file should return True for successful move"
        assert os.path.exists(dest_path), "Destination file should exist after moving"
        assert not os.path.exists(source_path), "Source file should no longer exist after moving"
        
        # Verify the content
        with open(dest_path, "r") as f:
            content = f.read()
        assert content == "Test content", "Destination file should have the same content as source"
        
    finally:
        # Clean up
        shutil.rmtree(source_dir)
        shutil.rmtree(dest_dir)


def test_get_file_size():
    """Tests that get_file_size correctly calculates file sizes"""
    # Create temporary files with known sizes
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Create files of different sizes
        sizes = [0, 1024, 10240]  # 0 bytes, 1KB, 10KB
        file_paths = []
        
        for size in sizes:
            file_path = os.path.join(temp_dir, f"file_{size}.dat")
            with open(file_path, "wb") as f:
                f.write(b"0" * size)
            file_paths.append((file_path, size))
        
        # Test each file
        for file_path, expected_size in file_paths:
            size = get_file_size(file_path)
            assert size == expected_size, f"Expected size {expected_size}, got {size} for {file_path}"
        
        # Test nonexistent file
        assert get_file_size("/nonexistent/path.txt") == 0, "Should return 0 for nonexistent file"
        
    finally:
        # Clean up
        shutil.rmtree(temp_dir)


@mock.patch('app.utils.file_utils.strip_file_metadata')
def test_strip_file_metadata(mock_strip_metadata):
    """Tests that strip_file_metadata removes metadata from files"""
    # Set up mock to return True
    mock_strip_metadata.return_value = True
    
    # Create a test file
    fd, temp_path = tempfile.mkstemp()
    os.close(fd)
    
    try:
        # Call the function with different file types
        result = strip_file_metadata(temp_path, "image")
        
        # Verify the mock was called correctly
        mock_strip_metadata.assert_called_with(temp_path, "image")
        
        # Verify the result
        assert result is True, "Should return True when metadata stripping is successful"
        
    finally:
        # Clean up
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_create_file_hash():
    """Tests that create_file_hash generates correct file hashes"""
    # Create a test file with known content
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Create test file
        test_file = os.path.join(temp_dir, "test.txt")
        test_content = b"This is a test file for hashing."
        with open(test_file, "wb") as f:
            f.write(test_content)
        
        # Generate hashes with different algorithms
        sha256_hash = create_file_hash(test_file, "sha256")
        md5_hash = create_file_hash(test_file, "md5")
        
        # Verify hashes are not empty
        assert sha256_hash, "SHA-256 hash should not be empty"
        assert md5_hash, "MD5 hash should not be empty"
        
        # Verify hashes are different
        assert sha256_hash != md5_hash, "Different algorithms should produce different hashes"
        
        # Verify hash length is correct for SHA-256 (64 hex characters)
        assert len(sha256_hash) == 64, f"SHA-256 hash should be 64 characters, got {len(sha256_hash)}"
        
        # Verify hash is in hexadecimal format
        assert all(c in "0123456789abcdef" for c in sha256_hash.lower()), "Hash should be in hexadecimal format"
        
        # Test nonexistent file
        assert create_file_hash("/nonexistent/path.txt") == "", "Should return empty string for nonexistent file"
        
        # Test invalid algorithm
        assert create_file_hash(test_file, "invalid_algorithm") == "", "Should return empty string for invalid algorithm"
        
    finally:
        # Clean up
        shutil.rmtree(temp_dir)