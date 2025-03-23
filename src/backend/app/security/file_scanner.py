import os
import subprocess
import tempfile
import typing
import uuid
import datetime
import socket
import clamd  # clamd v1.0.2
import magic  # python-magic v0.4.27

from ..core.config import settings
from ..core.logging import get_logger
from ..utils.file_utils import validate_file_type, get_file_extension
from ..integrations.aws_s3 import S3Client, quarantine_file

# Initialize logger
logger = get_logger(__name__)

# Constants for scan results
SCAN_RESULT_CLEAN = "CLEAN"
SCAN_RESULT_INFECTED = "INFECTED"
SCAN_RESULT_ERROR = "ERROR"
SCAN_RESULT_UNSUPPORTED = "UNSUPPORTED"

# Scan timeout in seconds
SCAN_TIMEOUT = 60

# ClamAV daemon connection settings
CLAMD_HOST = settings.CLAMD_HOST if hasattr(settings, 'CLAMD_HOST') else 'localhost'
CLAMD_PORT = settings.CLAMD_PORT if hasattr(settings, 'CLAMD_PORT') else 3310

# Fallback AV command if ClamAV daemon is not available
FALLBACK_AV_COMMAND = settings.FALLBACK_AV_COMMAND if hasattr(settings, 'FALLBACK_AV_COMMAND') else 'clamscan'


def scan_file(file_path: str) -> dict:
    """
    Scans a file for viruses and other security threats.
    
    Args:
        file_path (str): Path to the file to scan
        
    Returns:
        dict: Scan result with status and details
    """
    # Validate that file exists
    if not os.path.isfile(file_path):
        logger.error(f"Cannot scan non-existent file: {file_path}")
        return {
            "status": SCAN_RESULT_ERROR,
            "details": {"error": "File not found"},
            "timestamp": datetime.datetime.now().isoformat()
        }
    
    # Check if file type is supported for scanning
    if not is_file_type_supported(file_path):
        logger.warning(f"Unsupported file type for scanning: {file_path}")
        return {
            "status": SCAN_RESULT_UNSUPPORTED,
            "details": {"error": "File type not supported for scanning"},
            "timestamp": datetime.datetime.now().isoformat()
        }
    
    # Try to scan with ClamAV daemon first
    try:
        scan_result = scan_file_with_clamd(file_path)
        logger.info(f"ClamAV daemon scan completed for {file_path}: {scan_result['status']}")
        return scan_result
    except Exception as e:
        logger.warning(f"ClamAV daemon scan failed, falling back to command-line scanner: {str(e)}")
        
        # Fall back to command-line scanner
        try:
            scan_result = scan_file_with_command(file_path)
            logger.info(f"Command-line scan completed for {file_path}: {scan_result['status']}")
            return scan_result
        except Exception as e:
            logger.error(f"All scan methods failed for {file_path}: {str(e)}")
            return {
                "status": SCAN_RESULT_ERROR,
                "details": {"error": f"Scanning failed: {str(e)}"},
                "timestamp": datetime.datetime.now().isoformat()
            }


def scan_file_with_clamd(file_path: str) -> dict:
    """
    Scans a file using ClamAV daemon.
    
    Args:
        file_path (str): Path to the file to scan
        
    Returns:
        dict: Scan result with status and details
    """
    try:
        # Initialize ClamAV daemon client
        clamav = clamd.ClamdNetworkSocket(host=CLAMD_HOST, port=CLAMD_PORT, timeout=SCAN_TIMEOUT)
        
        # Test connection to daemon
        clamav.ping()
        
        # Scan the file with timeout protection
        scan_result = clamav.scan(file_path)
        
        # Parse the scan result
        if file_path in scan_result:
            scan_details = scan_result[file_path]
            if scan_details[0] == 'OK':
                return {
                    "status": SCAN_RESULT_CLEAN,
                    "details": {"message": "No threats detected", "scanner": "ClamAV daemon"},
                    "timestamp": datetime.datetime.now().isoformat()
                }
            else:
                # Infected - format: ('FOUND', 'virus name')
                virus_name = scan_details[1] if len(scan_details) > 1 else "Unknown threat"
                return {
                    "status": SCAN_RESULT_INFECTED,
                    "details": {
                        "threat": virus_name,
                        "scanner": "ClamAV daemon"
                    },
                    "timestamp": datetime.datetime.now().isoformat()
                }
        else:
            # Try alternative result format for different ClamAV versions
            # Some versions return {'/path/to/file': ('FOUND', 'Virus.Name')}
            # Others might return {'stream': ('FOUND', 'Virus.Name')}
            for key, value in scan_result.items():
                if isinstance(value, tuple) and len(value) >= 1:
                    if value[0] == 'OK':
                        return {
                            "status": SCAN_RESULT_CLEAN,
                            "details": {"message": "No threats detected", "scanner": "ClamAV daemon"},
                            "timestamp": datetime.datetime.now().isoformat()
                        }
                    elif value[0] == 'FOUND' or 'FOUND' in value[0]:
                        virus_name = value[1] if len(value) > 1 else "Unknown threat"
                        return {
                            "status": SCAN_RESULT_INFECTED,
                            "details": {
                                "threat": virus_name,
                                "scanner": "ClamAV daemon"
                            },
                            "timestamp": datetime.datetime.now().isoformat()
                        }
        
        # If we reach here, couldn't parse the result
        logger.warning(f"Unexpected ClamAV scan result format: {scan_result}")
        return {
            "status": SCAN_RESULT_ERROR,
            "details": {"error": "Invalid scan result format", "raw_result": str(scan_result)},
            "timestamp": datetime.datetime.now().isoformat()
        }
    except (ConnectionRefusedError, clamd.ConnectionError, socket.error) as e:
        logger.error(f"Failed to connect to ClamAV daemon: {str(e)}")
        raise
    except clamd.ClamdError as e:
        logger.error(f"ClamAV daemon error: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error scanning with ClamAV daemon: {str(e)}")
        raise


def scan_file_with_command(file_path: str) -> dict:
    """
    Scans a file using command-line antivirus scanner.
    
    Args:
        file_path (str): Path to the file to scan
        
    Returns:
        dict: Scan result with status and details
    """
    try:
        # Construct the command
        command = [FALLBACK_AV_COMMAND, file_path]
        
        # Execute the command with timeout
        process = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=SCAN_TIMEOUT
        )
        
        # Parse the output based on return code
        if process.returncode == 0:
            # Exit code 0 means no virus found
            return {
                "status": SCAN_RESULT_CLEAN,
                "details": {
                    "message": "No threats detected",
                    "scanner": FALLBACK_AV_COMMAND
                },
                "timestamp": datetime.datetime.now().isoformat()
            }
        elif process.returncode == 1:
            # Exit code 1 means virus found
            # Try to extract virus name from output
            output = process.stdout or process.stderr or ""
            virus_info = "Unknown threat"
            
            # Look for common patterns in ClamAV output
            if "FOUND" in output:
                # Try to extract the virus name (format varies by scanner)
                lines = output.splitlines()
                for line in lines:
                    if "FOUND" in line:
                        parts = line.split("FOUND")
                        if len(parts) > 1:
                            virus_info = parts[1].strip()
                            break
            
            return {
                "status": SCAN_RESULT_INFECTED,
                "details": {
                    "threat": virus_info,
                    "scanner": FALLBACK_AV_COMMAND,
                    "command_output": output
                },
                "timestamp": datetime.datetime.now().isoformat()
            }
        else:
            # Other exit codes indicate errors
            return {
                "status": SCAN_RESULT_ERROR,
                "details": {
                    "error": f"Scanner returned code {process.returncode}",
                    "output": (process.stdout or process.stderr or "").strip(),
                    "scanner": FALLBACK_AV_COMMAND
                },
                "timestamp": datetime.datetime.now().isoformat()
            }
    except subprocess.TimeoutExpired:
        logger.warning(f"Command-line scan timed out after {SCAN_TIMEOUT}s for {file_path}")
        return {
            "status": SCAN_RESULT_ERROR,
            "details": {
                "error": f"Scan timed out after {SCAN_TIMEOUT} seconds",
                "scanner": FALLBACK_AV_COMMAND
            },
            "timestamp": datetime.datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error executing command-line scan: {str(e)}")
        raise


def is_file_type_supported(file_path: str) -> bool:
    """
    Checks if a file type is supported for scanning.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        bool: True if file type is supported, False otherwise
    """
    # Get file extension
    extension = get_file_extension(file_path)
    
    # Check extension against allowed extensions
    if not extension:
        logger.warning(f"No file extension found for {file_path}")
        return False
    
    # List of supported extensions for scanning
    supported_extensions = [
        'csv', 'json', 'xml', 'jpg', 'jpeg', 'png', 'tiff', 'mp3', 'wav',
        'txt', 'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'zip'
    ]
    
    if extension.lower() not in supported_extensions:
        logger.warning(f"File extension not supported for scanning: {extension}")
        return False
    
    # Additional validation using file type detection
    try:
        # Check actual content type using magic
        mime_type = magic.from_file(file_path, mime=True)
        
        # List of supported MIME type patterns
        supported_mime_patterns = [
            "text/", "image/", "audio/", "application/json", 
            "application/xml", "application/pdf", "application/msword",
            "application/vnd.openxmlformats-officedocument",
            "application/vnd.ms-", "application/zip"
        ]
        
        # Check if MIME type matches any supported pattern
        is_mime_supported = any(mime_type.startswith(pattern) for pattern in supported_mime_patterns)
        
        if not is_mime_supported:
            logger.warning(f"File MIME type not supported for scanning: {mime_type}")
            return False
        
        return True
    except Exception as e:
        logger.warning(f"Error detecting file type: {str(e)}")
        return False


def parse_scan_result(result_text: str) -> dict:
    """
    Parses raw scan results into a standardized format.
    
    Args:
        result_text (str): Raw scan result text
        
    Returns:
        dict: Parsed scan result with status and details
    """
    if not result_text:
        return {
            "status": SCAN_RESULT_ERROR,
            "details": {"error": "Empty scan result"},
            "timestamp": datetime.datetime.now().isoformat()
        }
    
    # Check for known patterns in scan results
    result_text = result_text.lower()
    
    if "infected" in result_text or "found" in result_text:
        # Try to extract virus name - this would need to be adapted to actual output format
        threat_info = "Unknown threat"
        return {
            "status": SCAN_RESULT_INFECTED,
            "details": {"threat": threat_info},
            "timestamp": datetime.datetime.now().isoformat()
        }
    elif "clean" in result_text or "ok" in result_text:
        return {
            "status": SCAN_RESULT_CLEAN,
            "details": {"message": "No threats detected"},
            "timestamp": datetime.datetime.now().isoformat()
        }
    else:
        return {
            "status": SCAN_RESULT_ERROR,
            "details": {"error": "Could not parse scan result", "raw_result": result_text},
            "timestamp": datetime.datetime.now().isoformat()
        }


def handle_infected_file(file_path: str, object_key: str, bucket_name: str, scan_result: dict) -> dict:
    """
    Handles an infected file by quarantining it.
    
    Args:
        file_path (str): Path to the infected file
        object_key (str): S3 object key for the file
        bucket_name (str): S3 bucket name
        scan_result (dict): Scan result details
    
    Returns:
        dict: Result of quarantine operation
    """
    logger.warning(
        f"Infected file detected: {file_path} - {scan_result.get('details', {}).get('threat', 'Unknown threat')}"
    )
    
    # Prepare threat information
    threat_info = {
        "detection_time": datetime.datetime.now().isoformat(),
        "threat_name": scan_result.get("details", {}).get("threat", "Unknown threat"),
        "scanner": scan_result.get("details", {}).get("scanner", "Unknown scanner"),
        "original_location": f"{bucket_name}/{object_key}"
    }
    
    # Quarantine the file in S3
    quarantine_result = quarantine_file(
        object_key=object_key,
        source_bucket=bucket_name,
        metadata=threat_info
    )
    
    return {
        "status": "quarantined" if quarantine_result else "quarantine_failed",
        "details": threat_info,
        "timestamp": datetime.datetime.now().isoformat()
    }


class ScanResult:
    """
    Class representing the result of a file scan.
    """
    
    def __init__(self, status: str, file_path: str, details: dict = None):
        """
        Initializes a new scan result.
        
        Args:
            status (str): Scan status (CLEAN, INFECTED, ERROR, UNSUPPORTED)
            file_path (str): Path to the scanned file
            details (dict): Additional details about the scan result
        """
        self.status = status
        self.file_path = file_path
        self.details = details or {}
        self.timestamp = datetime.datetime.now()
    
    def to_dict(self) -> dict:
        """
        Converts the scan result to a dictionary.
        
        Returns:
            dict: Dictionary representation of scan result
        """
        return {
            "status": self.status,
            "file_path": self.file_path,
            "details": self.details,
            "timestamp": self.timestamp.isoformat()
        }
    
    def is_clean(self) -> bool:
        """
        Checks if the scan result indicates a clean file.
        
        Returns:
            bool: True if status is CLEAN, False otherwise
        """
        return self.status == SCAN_RESULT_CLEAN
    
    def is_infected(self) -> bool:
        """
        Checks if the scan result indicates an infected file.
        
        Returns:
            bool: True if status is INFECTED, False otherwise
        """
        return self.status == SCAN_RESULT_INFECTED
    
    def is_error(self) -> bool:
        """
        Checks if the scan result indicates an error.
        
        Returns:
            bool: True if status is ERROR, False otherwise
        """
        return self.status == SCAN_RESULT_ERROR
        
    def is_unsupported(self) -> bool:
        """
        Checks if the scan result indicates an unsupported file.
        
        Returns:
            bool: True if status is UNSUPPORTED, False otherwise
        """
        return self.status == SCAN_RESULT_UNSUPPORTED


class FileScanner:
    """
    Class for scanning files for security threats.
    """
    
    def __init__(self):
        """
        Initializes the FileScanner with necessary dependencies.
        """
        self._s3_client = S3Client()
        self._scan_cache = {}  # Cache scan results to avoid redundant scans
        logger.info("FileScanner initialized")
    
    def scan_file(self, file_path: str) -> dict:
        """
        Scans a file for security threats.
        
        Args:
            file_path (str): Path to the file to scan
            
        Returns:
            dict: Scan result with status and details
        """
        # Check cache first
        if file_path in self._scan_cache:
            logger.debug(f"Returning cached scan result for {file_path}")
            return self._scan_cache[file_path]
        
        # Perform the scan
        result = scan_file(file_path)
        
        # Cache the result
        self._scan_cache[file_path] = result
        
        return result
    
    def scan_s3_file(self, object_key: str, bucket_name: str) -> dict:
        """
        Scans a file stored in S3.
        
        Args:
            object_key (str): S3 object key
            bucket_name (str): S3 bucket name
            
        Returns:
            dict: Scan result with status and details
        """
        # Check cache first using a cache key that includes bucket and object key
        cache_key = f"s3:{bucket_name}/{object_key}"
        if cache_key in self._scan_cache:
            logger.debug(f"Returning cached scan result for {cache_key}")
            return self._scan_cache[cache_key]
        
        # Create a temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file.close()
        
        try:
            # Download the file from S3
            download_success = self._s3_client.download_file(
                object_key=object_key,
                download_path=temp_file.name,
                bucket_name=bucket_name
            )
            
            if not download_success:
                error_result = {
                    "status": SCAN_RESULT_ERROR,
                    "details": {"error": "Failed to download file from S3"},
                    "timestamp": datetime.datetime.now().isoformat()
                }
                self._scan_cache[cache_key] = error_result
                return error_result
            
            # Scan the downloaded file
            scan_result = self.scan_file(temp_file.name)
            
            # If the file is infected, quarantine it in S3
            if scan_result["status"] == SCAN_RESULT_INFECTED:
                self.handle_infected_file(
                    file_path=temp_file.name,
                    object_key=object_key,
                    bucket_name=bucket_name,
                    scan_result=scan_result
                )
            
            # Cache the result
            self._scan_cache[cache_key] = scan_result
            
            return scan_result
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_file.name):
                os.unlink(temp_file.name)
    
    def clear_cache(self):
        """
        Clears the scan result cache.
        """
        self._scan_cache.clear()
        logger.debug("Scan cache cleared")
    
    def is_file_clean(self, file_path: str) -> bool:
        """
        Checks if a file is clean (free from threats).
        
        Args:
            file_path (str): Path to the file
            
        Returns:
            bool: True if file is clean, False otherwise
        """
        result = self.scan_file(file_path)
        return result["status"] == SCAN_RESULT_CLEAN
    
    def is_s3_file_clean(self, object_key: str, bucket_name: str) -> bool:
        """
        Checks if a file in S3 is clean.
        
        Args:
            object_key (str): S3 object key
            bucket_name (str): S3 bucket name
            
        Returns:
            bool: True if file is clean, False otherwise
        """
        result = self.scan_s3_file(object_key, bucket_name)
        return result["status"] == SCAN_RESULT_CLEAN
    
    def handle_infected_file(self, file_path: str, object_key: str, bucket_name: str, scan_result: dict) -> dict:
        """
        Handles an infected file by quarantining it.
        
        Args:
            file_path (str): Path to the infected file
            object_key (str): S3 object key for the file
            bucket_name (str): S3 bucket name
            scan_result (dict): Scan result details
        
        Returns:
            dict: Result of quarantine operation
        """
        return handle_infected_file(file_path, object_key, bucket_name, scan_result)
    
    def get_scan_result(self, file_path: str) -> dict:
        """
        Gets the scan result for a previously scanned file.
        
        Args:
            file_path (str): Path to the file
            
        Returns:
            dict: Cached scan result or None if not in cache
        """
        return self._scan_cache.get(file_path)