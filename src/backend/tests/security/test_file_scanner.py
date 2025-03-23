import os
import tempfile
from unittest.mock import patch, MagicMock

import pytest

from app.security.file_scanner import (
    FileScanner, ScanResult, scan_file,
    SCAN_RESULT_CLEAN, SCAN_RESULT_INFECTED, 
    SCAN_RESULT_ERROR, SCAN_RESULT_UNSUPPORTED
)
from app.integrations.aws_s3 import S3Client
from app.utils.file_utils import validate_file_type, get_file_extension, create_temp_file


def test_scan_result_initialization():
    """Tests the initialization of ScanResult class with different statuses"""
    # Create a ScanResult with SCAN_RESULT_CLEAN status
    file_path = "/tmp/test_file.txt"
    clean_result = ScanResult(SCAN_RESULT_CLEAN, file_path)
    
    # Verify that the status is set correctly
    assert clean_result.status == SCAN_RESULT_CLEAN
    assert clean_result.file_path == file_path
    
    # Verify that is_clean() returns True
    assert clean_result.is_clean() is True
    
    # Verify that is_infected() returns False
    assert clean_result.is_infected() is False
    
    # Create a ScanResult with SCAN_RESULT_INFECTED status
    infected_result = ScanResult(SCAN_RESULT_INFECTED, file_path)
    
    # Verify that the status is set correctly
    assert infected_result.status == SCAN_RESULT_INFECTED
    
    # Verify that is_clean() returns False
    assert infected_result.is_clean() is False
    
    # Verify that is_infected() returns True
    assert infected_result.is_infected() is True
    
    # Create a ScanResult with SCAN_RESULT_ERROR status
    error_result = ScanResult(SCAN_RESULT_ERROR, file_path)
    
    # Verify that is_error() returns True
    assert error_result.is_error() is True
    
    # Create a ScanResult with SCAN_RESULT_UNSUPPORTED status
    unsupported_result = ScanResult(SCAN_RESULT_UNSUPPORTED, file_path)
    
    # Verify that is_unsupported() returns True
    assert unsupported_result.is_unsupported() is True


def test_scan_result_to_dict():
    """Tests the to_dict method of ScanResult class"""
    # Create a ScanResult with test data
    file_path = "/tmp/test_file.txt"
    details = {"message": "Test details", "scanner": "Test scanner"}
    scan_result = ScanResult(SCAN_RESULT_CLEAN, file_path, details)
    
    # Call to_dict() method
    result_dict = scan_result.to_dict()
    
    # Verify that the returned dictionary contains all expected keys
    assert isinstance(result_dict, dict)
    assert "status" in result_dict
    assert "file_path" in result_dict
    assert "details" in result_dict
    assert "timestamp" in result_dict
    
    # Verify that the values in the dictionary match the ScanResult attributes
    assert result_dict["status"] == SCAN_RESULT_CLEAN
    assert result_dict["file_path"] == file_path
    assert result_dict["details"] == details


def test_file_scanner_initialization():
    """Tests the initialization of FileScanner class"""
    # Create a FileScanner instance
    scanner = FileScanner()
    
    # Verify that the _s3_client attribute is initialized
    assert hasattr(scanner, "_s3_client")
    assert isinstance(scanner._s3_client, S3Client)
    
    # Verify that the _scan_cache attribute is initialized as an empty dictionary
    assert hasattr(scanner, "_scan_cache")
    assert scanner._scan_cache == {}


@patch('app.security.file_scanner.scan_file_with_clamd')
def test_scan_file_clean(mock_scan_file_with_clamd):
    """Tests scanning a clean file"""
    # Mock scan_file_with_clamd to return a clean result
    mock_scan_file_with_clamd.return_value = {
        "status": SCAN_RESULT_CLEAN,
        "details": {"message": "No threats detected", "scanner": "ClamAV daemon"},
        "timestamp": "2023-01-01T00:00:00"
    }
    
    # Create a temporary test file
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(b"Test file content")
        temp_file_path = temp_file.name
    
    try:
        # Call scan_file function with the test file
        result = scan_file(temp_file_path)
        
        # Verify that scan_file_with_clamd was called with correct parameters
        mock_scan_file_with_clamd.assert_called_once_with(temp_file_path)
        
        # Verify that the returned result has SCAN_RESULT_CLEAN status
        assert result["status"] == SCAN_RESULT_CLEAN
        
        # Verify that the returned result contains the correct file path
        assert "message" in result["details"]
        assert "No threats detected" in result["details"]["message"]
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)


@patch('app.security.file_scanner.scan_file_with_clamd')
def test_scan_file_infected(mock_scan_file_with_clamd):
    """Tests scanning an infected file"""
    # Mock scan_file_with_clamd to return an infected result
    mock_scan_file_with_clamd.return_value = {
        "status": SCAN_RESULT_INFECTED,
        "details": {"threat": "Test.Virus", "scanner": "ClamAV daemon"},
        "timestamp": "2023-01-01T00:00:00"
    }
    
    # Create a temporary test file
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(b"Test file with virus signature")
        temp_file_path = temp_file.name
    
    try:
        # Call scan_file function with the test file
        result = scan_file(temp_file_path)
        
        # Verify that scan_file_with_clamd was called with correct parameters
        mock_scan_file_with_clamd.assert_called_once_with(temp_file_path)
        
        # Verify that the returned result has SCAN_RESULT_INFECTED status
        assert result["status"] == SCAN_RESULT_INFECTED
        
        # Verify that the returned result contains the correct file path and threat details
        assert "threat" in result["details"]
        assert result["details"]["threat"] == "Test.Virus"
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)


@patch('app.security.file_scanner.scan_file_with_clamd')
@patch('app.security.file_scanner.scan_file_with_command')
def test_scan_file_error(mock_scan_file_with_command, mock_scan_file_with_clamd):
    """Tests scanning with an error condition"""
    # Mock scan_file_with_clamd to raise an exception
    mock_scan_file_with_clamd.side_effect = Exception("ClamAV error")
    
    # Mock scan_file_with_command to also raise an exception
    mock_scan_file_with_command.side_effect = Exception("Command error")
    
    # Create a temporary test file
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(b"Test file content")
        temp_file_path = temp_file.name
    
    try:
        # Call scan_file function with the test file
        result = scan_file(temp_file_path)
        
        # Verify that both scanning methods were attempted
        mock_scan_file_with_clamd.assert_called_once_with(temp_file_path)
        mock_scan_file_with_command.assert_called_once_with(temp_file_path)
        
        # Verify that the returned result has SCAN_RESULT_ERROR status
        assert result["status"] == SCAN_RESULT_ERROR
        
        # Verify that the returned result contains error details
        assert "error" in result["details"]
        assert "Scanning failed" in result["details"]["error"]
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)


@patch('app.security.file_scanner.scan_file_with_clamd')
@patch('app.security.file_scanner.scan_file_with_command')
def test_scan_file_fallback(mock_scan_file_with_command, mock_scan_file_with_clamd):
    """Tests fallback to command-line scanner when daemon fails"""
    # Mock scan_file_with_clamd to raise an exception
    mock_scan_file_with_clamd.side_effect = Exception("ClamAV daemon error")
    
    # Mock scan_file_with_command to return a clean result
    mock_scan_file_with_command.return_value = {
        "status": SCAN_RESULT_CLEAN,
        "details": {"message": "No threats detected", "scanner": "clamscan"},
        "timestamp": "2023-01-01T00:00:00"
    }
    
    # Create a temporary test file
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(b"Test file content")
        temp_file_path = temp_file.name
    
    try:
        # Call scan_file function with the test file
        result = scan_file(temp_file_path)
        
        # Verify that scan_file_with_clamd was called and failed
        mock_scan_file_with_clamd.assert_called_once_with(temp_file_path)
        
        # Verify that scan_file_with_command was called as fallback
        mock_scan_file_with_command.assert_called_once_with(temp_file_path)
        
        # Verify that the returned result has SCAN_RESULT_CLEAN status
        assert result["status"] == SCAN_RESULT_CLEAN
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)


@patch('app.security.file_scanner.is_file_type_supported')
def test_scan_file_unsupported(mock_is_file_type_supported):
    """Tests scanning an unsupported file type"""
    # Mock is_file_type_supported to return False
    mock_is_file_type_supported.return_value = False
    
    # Create a temporary test file
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(b"Test file content")
        temp_file_path = temp_file.name
    
    try:
        # Call scan_file function with the test file
        result = scan_file(temp_file_path)
        
        # Verify that is_file_type_supported was called with correct parameters
        mock_is_file_type_supported.assert_called_once_with(temp_file_path)
        
        # Verify that the returned result has SCAN_RESULT_UNSUPPORTED status
        assert result["status"] == SCAN_RESULT_UNSUPPORTED
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)


@patch('app.security.file_scanner.scan_file')
def test_file_scanner_scan_file(mock_scan_file):
    """Tests the scan_file method of FileScanner class"""
    # Mock scan_file to return a clean result
    expected_result = {
        "status": SCAN_RESULT_CLEAN,
        "details": {"message": "No threats detected"},
        "timestamp": "2023-01-01T00:00:00"
    }
    mock_scan_file.return_value = expected_result
    
    # Create a FileScanner instance
    scanner = FileScanner()
    
    # Create a temporary test file
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(b"Test file content")
        temp_file_path = temp_file.name
    
    try:
        # Call scanner.scan_file with the test file
        result = scanner.scan_file(temp_file_path)
        
        # Verify that scan_file was called with correct parameters
        mock_scan_file.assert_called_once_with(temp_file_path)
        
        # Verify that the returned result matches the expected result
        assert result == expected_result
        
        # Call scanner.scan_file again with the same file
        mock_scan_file.reset_mock()
        result2 = scanner.scan_file(temp_file_path)
        
        # Verify that scan_file was called only once (cached result used)
        mock_scan_file.assert_not_called()
        assert result2 == expected_result
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)


@patch('app.security.file_scanner.scan_file')
@patch('tempfile.mkdtemp')
@patch('os.path.join')
def test_file_scanner_scan_s3_file(mock_os_path_join, mock_mkdtemp, mock_scan_file):
    """Tests the scan_s3_file method of FileScanner class"""
    # Mock scan_file to return a clean result
    expected_result = {
        "status": SCAN_RESULT_CLEAN,
        "details": {"message": "No threats detected"},
        "timestamp": "2023-01-01T00:00:00"
    }
    mock_scan_file.return_value = expected_result
    
    # Mock tempfile.mkdtemp to return a test directory
    test_dir = "/tmp/test_dir"
    mock_mkdtemp.return_value = test_dir
    
    # Mock os.path.join to return a test file path
    test_file_path = "/tmp/test_dir/test_file.txt"
    mock_os_path_join.return_value = test_file_path
    
    # Create a FileScanner instance with mocked S3Client
    mock_s3_client = MagicMock()
    mock_s3_client.download_file.return_value = True
    scanner = FileScanner()
    scanner._s3_client = mock_s3_client
    
    # Call scanner.scan_s3_file with test object key and bucket
    object_key = "test/test_file.txt"
    bucket_name = "test-bucket"
    result = scanner.scan_s3_file(object_key, bucket_name)
    
    # Verify that S3Client.download_file was called with correct parameters
    mock_s3_client.download_file.assert_called_once_with(
        object_key=object_key,
        download_path=test_file_path,
        bucket_name=bucket_name
    )
    
    # Verify that scan_file was called with the correct file path
    mock_scan_file.assert_called_once_with(test_file_path)
    
    # Verify that the returned result matches the expected result
    assert result == expected_result
    
    # Call scanner.scan_s3_file again with the same parameters
    mock_s3_client.download_file.reset_mock()
    mock_scan_file.reset_mock()
    result2 = scanner.scan_s3_file(object_key, bucket_name)
    
    # Verify that download_file and scan_file were called only once (cached result used)
    mock_s3_client.download_file.assert_not_called()
    mock_scan_file.assert_not_called()
    assert result2 == expected_result


@patch('app.security.file_scanner.scan_file')
@patch('tempfile.mkdtemp')
@patch('os.path.join')
def test_file_scanner_scan_s3_file_infected(mock_os_path_join, mock_mkdtemp, mock_scan_file):
    """Tests the scan_s3_file method with an infected file"""
    # Mock scan_file to return an infected result
    infected_result = {
        "status": SCAN_RESULT_INFECTED,
        "details": {"threat": "Test.Virus", "scanner": "ClamAV daemon"},
        "timestamp": "2023-01-01T00:00:00"
    }
    mock_scan_file.return_value = infected_result
    
    # Mock tempfile.mkdtemp to return a test directory
    test_dir = "/tmp/test_dir"
    mock_mkdtemp.return_value = test_dir
    
    # Mock os.path.join to return a test file path
    test_file_path = "/tmp/test_dir/infected_file.txt"
    mock_os_path_join.return_value = test_file_path
    
    # Create a FileScanner instance with mocked S3Client
    mock_s3_client = MagicMock()
    mock_s3_client.download_file.return_value = True
    scanner = FileScanner()
    scanner._s3_client = mock_s3_client
    
    # Mock scanner.handle_infected_file method
    scanner.handle_infected_file = MagicMock()
    scanner.handle_infected_file.return_value = {
        "status": "quarantined",
        "details": {
            "threat_name": "Test.Virus",
            "scanner": "ClamAV daemon",
            "detection_time": "2023-01-01T00:00:00"
        }
    }
    
    # Call scanner.scan_s3_file with test object key and bucket
    object_key = "test/infected_file.txt"
    bucket_name = "test-bucket"
    result = scanner.scan_s3_file(object_key, bucket_name)
    
    # Verify that S3Client.download_file was called with correct parameters
    mock_s3_client.download_file.assert_called_once_with(
        object_key=object_key,
        download_path=test_file_path,
        bucket_name=bucket_name
    )
    
    # Verify that scan_file was called with the correct file path
    mock_scan_file.assert_called_once_with(test_file_path)
    
    # Verify that handle_infected_file was called with correct parameters
    scanner.handle_infected_file.assert_called_once_with(
        file_path=test_file_path,
        object_key=object_key,
        bucket_name=bucket_name,
        scan_result=infected_result
    )
    
    # Verify that the returned result has SCAN_RESULT_INFECTED status
    assert result["status"] == SCAN_RESULT_INFECTED


@patch('app.security.file_scanner.scan_file')
def test_file_scanner_clear_cache(mock_scan_file):
    """Tests the clear_cache method of FileScanner class"""
    # Mock scan_file to return a clean result
    expected_result = {
        "status": SCAN_RESULT_CLEAN,
        "details": {"message": "No threats detected"},
        "timestamp": "2023-01-01T00:00:00"
    }
    mock_scan_file.return_value = expected_result
    
    # Create a FileScanner instance
    scanner = FileScanner()
    
    # Create a temporary test file
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(b"Test file content")
        temp_file_path = temp_file.name
    
    try:
        # Call scanner.scan_file with the test file
        scanner.scan_file(temp_file_path)
        
        # Verify that the result is cached
        assert temp_file_path in scanner._scan_cache
        
        # Call scanner.clear_cache()
        scanner.clear_cache()
        
        # Verify that the cache is empty
        assert scanner._scan_cache == {}
        
        # Call scanner.scan_file again with the same file
        mock_scan_file.reset_mock()
        scanner.scan_file(temp_file_path)
        
        # Verify that scan_file was called again (cache was cleared)
        mock_scan_file.assert_called_once_with(temp_file_path)
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)


@patch('app.security.file_scanner.scan_file')
def test_file_scanner_is_file_clean(mock_scan_file):
    """Tests the is_file_clean method of FileScanner class"""
    # Mock scan_file to return a clean result
    mock_scan_file.return_value = {
        "status": SCAN_RESULT_CLEAN,
        "details": {"message": "No threats detected"},
        "timestamp": "2023-01-01T00:00:00"
    }
    
    # Create a FileScanner instance
    scanner = FileScanner()
    
    # Create a temporary test file
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(b"Test file content")
        clean_file_path = temp_file.name
    
    try:
        # Call scanner.is_file_clean with the test file
        result = scanner.is_file_clean(clean_file_path)
        
        # Verify that scan_file was called with correct parameters
        mock_scan_file.assert_called_with(clean_file_path)
        
        # Verify that is_file_clean returns True
        assert result is True
        
        # Mock scan_file to return an infected result
        mock_scan_file.return_value = {
            "status": SCAN_RESULT_INFECTED,
            "details": {"threat": "Test.Virus"},
            "timestamp": "2023-01-01T00:00:00"
        }
        
        # Call scanner.is_file_clean with another test file
        with tempfile.NamedTemporaryFile(delete=False) as temp_file2:
            temp_file2.write(b"Infected file content")
            infected_file_path = temp_file2.name
            
            result = scanner.is_file_clean(infected_file_path)
            
            # Verify that is_file_clean returns False
            assert result is False
            
            # Clean up second test file
            if os.path.exists(infected_file_path):
                os.unlink(infected_file_path)
                
    finally:
        # Clean up the temporary files
        if os.path.exists(clean_file_path):
            os.unlink(clean_file_path)


@patch.object(FileScanner, 'scan_s3_file')
def test_file_scanner_is_s3_file_clean(mock_scan_s3_file):
    """Tests the is_s3_file_clean method of FileScanner class"""
    # Create a FileScanner instance
    scanner = FileScanner()
    
    # Mock scanner.scan_s3_file to return a clean result
    mock_scan_s3_file.return_value = {
        "status": SCAN_RESULT_CLEAN,
        "details": {"message": "No threats detected"},
        "timestamp": "2023-01-01T00:00:00"
    }
    
    # Call scanner.is_s3_file_clean with test object key and bucket
    result = scanner.is_s3_file_clean("test/clean_file.txt", "test-bucket")
    
    # Verify that scan_s3_file was called with correct parameters
    mock_scan_s3_file.assert_called_with("test/clean_file.txt", "test-bucket")
    
    # Verify that is_s3_file_clean returns True
    assert result is True
    
    # Mock scanner.scan_s3_file to return an infected result
    mock_scan_s3_file.return_value = {
        "status": SCAN_RESULT_INFECTED,
        "details": {"threat": "Test.Virus"},
        "timestamp": "2023-01-01T00:00:00"
    }
    
    # Call scanner.is_s3_file_clean with different parameters
    result = scanner.is_s3_file_clean("test/infected_file.txt", "test-bucket")
    
    # Verify that is_s3_file_clean returns False
    assert result is False


def test_file_scanner_handle_infected_file():
    """Tests the handle_infected_file method of FileScanner class"""
    # Create a FileScanner instance with mocked S3Client
    mock_s3_client = MagicMock()
    mock_s3_client.move_to_quarantine.return_value = True
    scanner = FileScanner()
    scanner._s3_client = mock_s3_client
    
    # Create a test scan result with infected status
    scan_result = {
        "status": SCAN_RESULT_INFECTED,
        "details": {"threat": "Test.Virus", "scanner": "ClamAV"},
        "timestamp": "2023-01-01T00:00:00"
    }
    
    # Call scanner.handle_infected_file with test parameters
    file_path = "/tmp/infected_file.txt"
    object_key = "test/infected_file.txt"
    bucket_name = "test-bucket"
    
    result = scanner.handle_infected_file(file_path, object_key, bucket_name, scan_result)
    
    # Verify that S3Client.move_to_quarantine was called with correct parameters
    mock_s3_client.move_to_quarantine.assert_called_once_with(
        source_key=object_key,
        source_bucket=bucket_name
    )
    
    # Verify that the method returns the expected result
    assert result["status"] == "quarantined"
    assert "detection_time" in result["details"]
    assert result["details"]["threat_name"] == "Test.Virus"


@patch('app.security.file_scanner.scan_file')
def test_file_scanner_get_scan_result(mock_scan_file):
    """Tests the get_scan_result method of FileScanner class"""
    # Mock scan_file to return a clean result
    expected_result = {
        "status": SCAN_RESULT_CLEAN,
        "details": {"message": "No threats detected"},
        "timestamp": "2023-01-01T00:00:00"
    }
    mock_scan_file.return_value = expected_result
    
    # Create a FileScanner instance
    scanner = FileScanner()
    
    # Create a temporary test file
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(b"Test file content")
        temp_file_path = temp_file.name
    
    try:
        # Call scanner.scan_file with the test file
        scanner.scan_file(temp_file_path)
        
        # Call scanner.get_scan_result with the same file path
        result = scanner.get_scan_result(temp_file_path)
        
        # Verify that get_scan_result returns the cached result
        assert result == expected_result
        
        # Call scanner.get_scan_result with a non-existent file path
        result = scanner.get_scan_result("/tmp/nonexistent.txt")
        
        # Verify that get_scan_result returns None
        assert result is None
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)


@patch('clamd.ClamdNetworkSocket')
def test_scan_file_with_clamd(mock_clamd_network_socket):
    """Tests the scan_file_with_clamd function"""
    # Import the function to test
    from app.security.file_scanner import scan_file_with_clamd
    
    # Mock ClamdNetworkSocket instance
    mock_clamd_instance = MagicMock()
    mock_clamd_network_socket.return_value = mock_clamd_instance
    
    # Create a temporary test file
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(b"Test file content")
        temp_file_path = temp_file.name
    
    try:
        # Mock instream method to return a clean result
        mock_clamd_instance.scan.return_value = {temp_file_path: ('OK',)}
        
        # Call scan_file_with_clamd
        result = scan_file_with_clamd(temp_file_path)
        
        # Verify that ClamdNetworkSocket was initialized correctly
        mock_clamd_network_socket.assert_called_once()
        
        # Verify that scan was called with the test file
        mock_clamd_instance.scan.assert_called_once_with(temp_file_path)
        
        # Verify that the returned result has SCAN_RESULT_CLEAN status
        assert result["status"] == SCAN_RESULT_CLEAN
        assert "No threats detected" in result["details"]["message"]
        
        # Mock instream to return an infected result
        mock_clamd_instance.scan.return_value = {temp_file_path: ('FOUND', 'Test.Virus')}
        
        # Call scan_file_with_clamd again
        result = scan_file_with_clamd(temp_file_path)
        
        # Verify that the returned result has SCAN_RESULT_INFECTED status
        assert result["status"] == SCAN_RESULT_INFECTED
        assert result["details"]["threat"] == "Test.Virus"
        
        # Mock instream to raise an exception
        mock_clamd_instance.scan.side_effect = Exception("ClamAV error")
        
        # Call scan_file_with_clamd again
        with pytest.raises(Exception):
            scan_file_with_clamd(temp_file_path)
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)


@patch('subprocess.run')
def test_scan_file_with_command(mock_subprocess_run):
    """Tests the scan_file_with_command function"""
    # Import the function to test
    from app.security.file_scanner import scan_file_with_command
    
    # Create a temporary test file
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(b"Test file content")
        temp_file_path = temp_file.name
    
    try:
        # Mock subprocess.run to return a clean result
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = "OK"
        mock_subprocess_run.return_value = mock_process
        
        # Call scan_file_with_command
        result = scan_file_with_command(temp_file_path)
        
        # Verify that subprocess.run was called with correct command
        mock_subprocess_run.assert_called_once()
        
        # Verify that the returned result has SCAN_RESULT_CLEAN status
        assert result["status"] == SCAN_RESULT_CLEAN
        
        # Mock subprocess.run to return an infected result
        mock_process.returncode = 1
        mock_process.stdout = "File infected: Test.Virus FOUND"
        
        # Call scan_file_with_command again
        result = scan_file_with_command(temp_file_path)
        
        # Verify that the returned result has SCAN_RESULT_INFECTED status
        assert result["status"] == SCAN_RESULT_INFECTED
        
        # Mock subprocess.run to raise an exception
        mock_subprocess_run.side_effect = Exception("Command error")
        
        # Call scan_file_with_command again
        with pytest.raises(Exception):
            scan_file_with_command(temp_file_path)
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)


@patch('app.utils.file_utils.get_file_extension')
@patch('magic.from_file')
def test_is_file_type_supported(mock_magic_from_file, mock_get_file_extension):
    """Tests the is_file_type_supported function"""
    # Import the function to test
    from app.security.file_scanner import is_file_type_supported
    
    # Create a temporary test file
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(b"Test file content")
        temp_file_path = temp_file.name
    
    try:
        # Mock get_file_extension to return a supported extension
        mock_get_file_extension.return_value = "csv"
        
        # Mock magic.from_file to return a supported MIME type
        mock_magic_from_file.return_value = "text/csv"
        
        # Call is_file_type_supported
        result = is_file_type_supported(temp_file_path)
        
        # Verify that get_file_extension was called with the test file
        mock_get_file_extension.assert_called_with(temp_file_path)
        
        # Verify that magic.from_file was called with the test file
        mock_magic_from_file.assert_called_with(temp_file_path, mime=True)
        
        # Verify that the function returns True for supported file
        assert result is True
        
        # Mock get_file_extension to return an unsupported extension
        mock_get_file_extension.return_value = "exe"
        
        # Call is_file_type_supported again
        result = is_file_type_supported(temp_file_path)
        
        # Verify that the function returns False for unsupported extension
        assert result is False
        
        # Mock get_file_extension to return a supported extension
        mock_get_file_extension.return_value = "csv"
        
        # Mock magic.from_file to return an unsupported MIME type
        mock_magic_from_file.return_value = "application/x-executable"
        
        # Call is_file_type_supported again
        result = is_file_type_supported(temp_file_path)
        
        # Verify that the function returns False for unsupported MIME type
        assert result is False
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)


def test_parse_scan_result():
    """Tests the parse_scan_result function"""
    # Import the function to test
    from app.security.file_scanner import parse_scan_result
    
    # Call parse_scan_result with a clean result string
    result = parse_scan_result("File clean: OK")
    
    # Verify that the returned result has SCAN_RESULT_CLEAN status
    assert result["status"] == SCAN_RESULT_CLEAN
    
    # Call parse_scan_result with an infected result string
    result = parse_scan_result("File infected: Test.Virus FOUND")
    
    # Verify that the returned result has SCAN_RESULT_INFECTED status
    assert result["status"] == SCAN_RESULT_INFECTED
    
    # Verify that the virus name is correctly extracted
    assert "threat" in result["details"]
    
    # Call parse_scan_result with an error result string
    result = parse_scan_result("Error scanning file")
    
    # Verify that the returned result has SCAN_RESULT_ERROR status
    assert result["status"] == SCAN_RESULT_ERROR
    
    # Call parse_scan_result with an empty string
    result = parse_scan_result("")
    
    # Verify that the returned result has SCAN_RESULT_ERROR status
    assert result["status"] == SCAN_RESULT_ERROR


def test_handle_infected_file():
    """Tests the handle_infected_file function"""
    # Import the function to test
    from app.security.file_scanner import handle_infected_file
    
    # Mock quarantine_file to return a success result
    with patch('app.integrations.aws_s3.quarantine_file') as mock_quarantine_file:
        mock_quarantine_file.return_value = True
        
        # Create a test scan result with infected status
        scan_result = {
            "status": SCAN_RESULT_INFECTED,
            "details": {"threat": "Test.Virus", "scanner": "ClamAV"},
            "timestamp": "2023-01-01T00:00:00"
        }
        
        # Call handle_infected_file with test parameters
        file_path = "/tmp/infected_file.txt"
        object_key = "test/infected_file.txt"
        bucket_name = "test-bucket"
        
        result = handle_infected_file(file_path, object_key, bucket_name, scan_result)
        
        # Verify that quarantine_file was called with correct parameters
        mock_quarantine_file.assert_called_once()
        call_args = mock_quarantine_file.call_args[1]
        assert call_args["object_key"] == object_key
        assert call_args["source_bucket"] == bucket_name
        
        # Verify that the function returns the expected result
        assert result["status"] == "quarantined"
        assert "threat_name" in result["details"]
        assert result["details"]["threat_name"] == "Test.Virus"


@pytest.mark.integration
def test_integration_file_scanner():
    """Integration test for FileScanner with real files"""
    # Skip test if INTEGRATION_TESTS environment variable is not set
    if os.environ.get("INTEGRATION_TESTS") != "1":
        pytest.skip("Integration tests not enabled (set INTEGRATION_TESTS=1 to run)")
    
    # Create a FileScanner instance
    scanner = FileScanner()
    
    # Create a temporary clean test file
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(b"This is a clean test file")
        clean_file_path = temp_file.name
    
    # Create a temporary test file with EICAR test signature
    eicar_test_string = (
        b"X5O!P%@AP[4\\PZX54(P^)7CC)7}"
        b"$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*"
    )
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(eicar_test_string)
        eicar_file_path = temp_file.name
    
    try:
        # Call scanner.scan_file with the clean file
        clean_result = scanner.scan_file(clean_file_path)
        
        # Verify that the result has SCAN_RESULT_CLEAN status
        assert clean_result["status"] == SCAN_RESULT_CLEAN
        
        # Call scanner.scan_file with the EICAR test file
        infected_result = scanner.scan_file(eicar_file_path)
        
        # Verify that the result has SCAN_RESULT_INFECTED status
        assert infected_result["status"] == SCAN_RESULT_INFECTED
    finally:
        # Clean up the temporary files
        if os.path.exists(clean_file_path):
            os.unlink(clean_file_path)
        if os.path.exists(eicar_file_path):
            os.unlink(eicar_file_path)