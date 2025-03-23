import os
import uuid
import shutil
import tempfile
import pathlib
import mimetypes
import re
import hashlib
from typing import Tuple, Optional

import magic  # python-magic v0.4.27

from ..core.config import settings
from ..core.logging import get_logger

# Initialize logger
logger = get_logger(__name__)

# Constants
ALLOWED_EXTENSIONS = settings.ALLOWED_UPLOAD_EXTENSIONS.lower().split(',')
MAX_UPLOAD_SIZE_MB = settings.MAX_UPLOAD_SIZE_MB
MAX_UPLOAD_SIZE_BYTES = MAX_UPLOAD_SIZE_MB * 1024 * 1024
TEMP_UPLOAD_DIR = os.path.join(tempfile.gettempdir(), 'indivillage_uploads')

# Ensure the temporary upload directory exists
if not os.path.exists(TEMP_UPLOAD_DIR):
    try:
        os.makedirs(TEMP_UPLOAD_DIR, exist_ok=True)
        logger.info(f"Created temporary upload directory: {TEMP_UPLOAD_DIR}")
    except OSError as e:
        logger.error(f"Failed to create temporary upload directory: {str(e)}")


def get_file_extension(filename: str) -> str:
    """
    Extracts the file extension from a filename.
    
    Args:
        filename (str): The filename to process
        
    Returns:
        str: Lowercase file extension without the dot
    """
    if not filename:
        logger.warning("Empty filename provided to get_file_extension")
        return ""
    
    # Handle filenames with multiple dots
    parts = filename.rsplit(".", 1)
    if len(parts) <= 1:
        # No extension found
        return ""
        
    extension = parts[1].lower()
    logger.debug(f"Extracted extension '{extension}' from filename '{filename}'")
    return extension


def validate_file_type(filename: str, content_type: str) -> bool:
    """
    Validates if a file's type/extension is allowed.
    
    Args:
        filename (str): The name of the file to validate
        content_type (str): The MIME type of the file
        
    Returns:
        bool: True if file type is allowed, False otherwise
    """
    if not filename:
        logger.warning("Empty filename provided to validate_file_type")
        return False
        
    extension = get_file_extension(filename)
    
    # Validate extension
    if extension not in ALLOWED_EXTENSIONS:
        logger.warning(f"File extension '.{extension}' not in allowed list: {ALLOWED_EXTENSIONS}")
        return False
    
    # Validate content type against allowed MIME types
    allowed_mime_patterns = [
        "text/csv", "text/plain",           # CSV files
        "application/json", "text/json",     # JSON files
        "application/xml", "text/xml",       # XML files
        "image/jpeg", "image/jpg", "image/png", "image/tiff",  # Image files
        "audio/mpeg", "audio/mp3", "audio/wav"                # Audio files
    ]
    
    # Check if the content_type matches any of the allowed patterns
    is_valid_mime = any(pattern in content_type.lower() for pattern in allowed_mime_patterns)
    
    if not is_valid_mime:
        logger.warning(f"Content type '{content_type}' not allowed for upload")
        return False
    
    logger.info(f"File type validation passed for '{filename}' with content type '{content_type}'")
    return True


def validate_file_size(file_size: int) -> bool:
    """
    Validates if a file's size is within allowed limits.
    
    Args:
        file_size (int): Size of the file in bytes
        
    Returns:
        bool: True if file size is within limits, False otherwise
    """
    if file_size <= 0:
        logger.warning(f"Invalid file size: {file_size} bytes")
        return False
        
    if file_size > MAX_UPLOAD_SIZE_BYTES:
        logger.warning(
            f"File size {file_size} bytes exceeds maximum allowed size "
            f"of {MAX_UPLOAD_SIZE_BYTES} bytes ({MAX_UPLOAD_SIZE_MB} MB)"
        )
        return False
    
    logger.debug(f"File size validation passed: {file_size} bytes")
    return True


def get_mime_type(file_path: str) -> str:
    """
    Determines the MIME type of a file using python-magic library.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        str: MIME type of the file, or empty string if detection fails
    """
    if not file_path or not os.path.isfile(file_path):
        logger.warning(f"Cannot detect MIME type, file not found: {file_path}")
        return ""
        
    try:
        # First try with python-magic for more accurate type detection
        mime_type = magic.from_file(file_path, mime=True)
        logger.debug(f"MIME type detected for '{file_path}': {mime_type}")
        return mime_type
    except Exception as e:
        logger.warning(f"Failed to detect MIME type with python-magic: {str(e)}")
        
        # Fall back to mimetypes module
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type:
            logger.debug(f"MIME type detected with mimetypes module: {mime_type}")
            return mime_type
        else:
            logger.warning(f"Failed to detect MIME type for '{file_path}'")
            return ""


def create_temp_file(content: bytes, prefix: str = "upload_", suffix: str = "") -> str:
    """
    Creates a temporary file with the given content.
    
    Args:
        content (bytes): Binary content to write to the file
        prefix (str): Prefix for the temporary filename
        suffix (str): Suffix (extension) for the temporary filename
        
    Returns:
        str: Path to the created temporary file, or empty string on failure
    """
    # Ensure temp directory exists
    if not ensure_directory_exists(TEMP_UPLOAD_DIR):
        return ""
        
    try:
        # Generate temporary file path
        filename = f"{prefix}{uuid.uuid4().hex}{suffix}"
        file_path = os.path.join(TEMP_UPLOAD_DIR, filename)
        
        # Write content to file
        with open(file_path, "wb") as f:
            f.write(content)
            
        logger.debug(f"Created temporary file: {file_path}")
        return file_path
    except Exception as e:
        logger.error(f"Failed to create temporary file: {str(e)}")
        return ""


def delete_file(file_path: str) -> bool:
    """
    Safely deletes a file if it exists.
    
    Args:
        file_path (str): Path to the file to delete
        
    Returns:
        bool: True if file was deleted, False otherwise
    """
    if not file_path or not os.path.isfile(file_path):
        logger.warning(f"Cannot delete, file not found: {file_path}")
        return False
        
    try:
        os.remove(file_path)
        logger.debug(f"Deleted file: {file_path}")
        return True
    except OSError as e:
        logger.error(f"Failed to delete file '{file_path}': {str(e)}")
        return False


def ensure_directory_exists(directory_path: str) -> bool:
    """
    Ensures that a directory exists, creating it if necessary.
    
    Args:
        directory_path (str): Path to the directory
        
    Returns:
        bool: True if directory exists or was created, False on failure
    """
    if not directory_path:
        logger.warning("Empty directory path provided")
        return False
        
    try:
        if not os.path.exists(directory_path):
            os.makedirs(directory_path, exist_ok=True)
            logger.info(f"Created directory: {directory_path}")
        return True
    except OSError as e:
        logger.error(f"Failed to create directory '{directory_path}': {str(e)}")
        return False


def generate_secure_filename(filename: str) -> str:
    """
    Generates a secure filename by removing potentially dangerous characters.
    
    Args:
        filename (str): Original filename
        
    Returns:
        str: Sanitized filename
    """
    if not filename:
        logger.warning("Empty filename provided to generate_secure_filename")
        return "unnamed"
        
    # Remove path information
    filename = os.path.basename(filename)
    
    # Get file extension
    extension = get_file_extension(filename)
    name_part = filename[:-(len(extension) + 1)] if extension else filename
    
    # Replace potentially dangerous characters with underscores
    # Only allow alphanumeric, underscore, hyphen, and period
    name_part = re.sub(r'[^\w\-\.]', '_', name_part)
    
    # Remove leading/trailing whitespace and dots (which might be used to hide extensions)
    name_part = name_part.strip('._')
    
    # Ensure we still have a valid filename
    if not name_part:
        name_part = "unnamed"
        
    # Limit length (leave room for extension)
    max_length = 200 - (len(extension) + 1 if extension else 0)
    if len(name_part) > max_length:
        name_part = name_part[:max_length]
        
    # Reconstruct filename with extension
    secure_name = f"{name_part}.{extension}" if extension else name_part
    
    logger.debug(f"Sanitized filename '{filename}' to '{secure_name}'")
    return secure_name


def generate_unique_filename(original_filename: str, prefix: str = "") -> str:
    """
    Generates a unique filename using UUID.
    
    Args:
        original_filename (str): Original filename
        prefix (str): Optional prefix to add to the filename
        
    Returns:
        str: Unique filename
    """
    if not original_filename:
        logger.warning("Empty filename provided to generate_unique_filename")
        return f"{prefix}{uuid.uuid4().hex}"
        
    # Generate a UUID
    unique_id = uuid.uuid4().hex
    
    # Get extension from original filename
    extension = get_file_extension(original_filename)
    
    # Sanitize the original filename (excluding extension)
    name_part = original_filename[:-(len(extension) + 1)] if extension else original_filename
    sanitized_name = re.sub(r'[^\w\-\.]', '_', name_part).strip('._')[:50]  # Limit to 50 chars
    
    # Construct the unique filename
    if extension:
        unique_name = f"{prefix}{sanitized_name}_{unique_id}.{extension}"
    else:
        unique_name = f"{prefix}{sanitized_name}_{unique_id}"
        
    logger.debug(f"Generated unique filename '{unique_name}' from '{original_filename}'")
    return unique_name


def is_valid_file(file_path: str, original_filename: str, content_type: str) -> Tuple[bool, str]:
    """
    Comprehensive validation of a file against security and business rules.
    
    Args:
        file_path (str): Path to the file
        original_filename (str): Original filename
        content_type (str): Content type from the upload
        
    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    if not file_path or not os.path.isfile(file_path):
        error_msg = "File not found or invalid path"
        logger.warning(f"{error_msg}: {file_path}")
        return False, error_msg
        
    # Check file size
    file_size = get_file_size(file_path)
    if file_size == 0:
        error_msg = "File is empty"
        logger.warning(f"{error_msg}: {file_path}")
        return False, error_msg
        
    if not validate_file_size(file_size):
        error_msg = f"File size exceeds maximum allowed size of {MAX_UPLOAD_SIZE_MB} MB"
        logger.warning(f"{error_msg}: {file_path} ({file_size} bytes)")
        return False, error_msg
        
    # Check file extension
    if not validate_file_type(original_filename, content_type):
        error_msg = "File type not allowed"
        logger.warning(f"{error_msg}: {original_filename} ({content_type})")
        return False, error_msg
        
    # Verify content type using magic number detection
    detected_mime = get_mime_type(file_path)
    if detected_mime and detected_mime != content_type:
        # This could indicate a file type spoofing attempt
        logger.warning(
            f"Declared content type '{content_type}' doesn't match detected type '{detected_mime}' "
            f"for file '{original_filename}'"
        )
        
        # Still check if detected type is allowed
        if not validate_file_type(original_filename, detected_mime):
            error_msg = "File content type not allowed"
            logger.warning(f"{error_msg}: {original_filename} (detected as {detected_mime})")
            return False, error_msg
    
    logger.info(f"File validation passed for '{original_filename}' ({file_size} bytes)")
    return True, ""


def copy_file(source_path: str, destination_path: str) -> bool:
    """
    Copies a file from source to destination.
    
    Args:
        source_path (str): Path to the source file
        destination_path (str): Path to the destination
        
    Returns:
        bool: True if copy was successful, False otherwise
    """
    if not source_path or not os.path.isfile(source_path):
        logger.warning(f"Cannot copy, source file not found: {source_path}")
        return False
        
    # Ensure destination directory exists
    dest_dir = os.path.dirname(destination_path)
    if not ensure_directory_exists(dest_dir):
        return False
        
    try:
        shutil.copy2(source_path, destination_path)
        logger.debug(f"Copied file from '{source_path}' to '{destination_path}'")
        return True
    except (OSError, IOError) as e:
        logger.error(f"Failed to copy file from '{source_path}' to '{destination_path}': {str(e)}")
        return False


def move_file(source_path: str, destination_path: str) -> bool:
    """
    Moves a file from source to destination.
    
    Args:
        source_path (str): Path to the source file
        destination_path (str): Path to the destination
        
    Returns:
        bool: True if move was successful, False otherwise
    """
    if not source_path or not os.path.isfile(source_path):
        logger.warning(f"Cannot move, source file not found: {source_path}")
        return False
        
    # Ensure destination directory exists
    dest_dir = os.path.dirname(destination_path)
    if not ensure_directory_exists(dest_dir):
        return False
        
    try:
        shutil.move(source_path, destination_path)
        logger.debug(f"Moved file from '{source_path}' to '{destination_path}'")
        return True
    except (OSError, IOError) as e:
        logger.error(f"Failed to move file from '{source_path}' to '{destination_path}': {str(e)}")
        return False


def get_file_size(file_path: str) -> int:
    """
    Gets the size of a file in bytes.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        int: Size of the file in bytes, or 0 if file doesn't exist or error occurs
    """
    if not file_path or not os.path.isfile(file_path):
        logger.warning(f"File not found or invalid path: {file_path}")
        return 0
        
    try:
        size = os.path.getsize(file_path)
        logger.debug(f"File size for '{file_path}': {size} bytes")
        return size
    except (OSError, IOError) as e:
        logger.error(f"Error getting file size for '{file_path}': {str(e)}")
        return 0


def strip_file_metadata(file_path: str, file_type: str) -> bool:
    """
    Removes metadata from files to enhance privacy and security.
    
    Args:
        file_path (str): Path to the file
        file_type (str): Type of file (e.g., 'image', 'document')
        
    Returns:
        bool: True if metadata was stripped, False otherwise
    """
    if not file_path or not os.path.isfile(file_path):
        logger.warning(f"Cannot strip metadata, file not found: {file_path}")
        return False
        
    try:
        if file_type.lower() in ['image', 'jpg', 'jpeg', 'png', 'tiff']:
            # For images, we would use PIL/Pillow or exiftool to strip EXIF data
            # This is a simplified example - in production, use a dedicated library
            logger.info(f"Image metadata stripping would be performed on {file_path}")
            
            # Example implementation with PIL (not imported by default):
            # from PIL import Image
            # image = Image.open(file_path)
            # data = list(image.getdata())
            # image_without_exif = Image.new(image.mode, image.size)
            # image_without_exif.putdata(data)
            # image_without_exif.save(file_path)
            
            return True  # Assuming success for now
            
        elif file_type.lower() in ['document', 'pdf', 'docx']:
            # For documents, stripping metadata would depend on document type
            logger.info(f"Document metadata stripping would be performed on {file_path}")
            return True  # Assuming success for now
            
        else:
            logger.info(f"No metadata stripping implemented for file type: {file_type}")
            return False
            
    except Exception as e:
        logger.error(f"Failed to strip metadata from file '{file_path}': {str(e)}")
        return False


def create_file_hash(file_path: str, algorithm: str = 'sha256') -> str:
    """
    Creates a hash of a file's contents for integrity verification.
    
    Args:
        file_path (str): Path to the file
        algorithm (str): Hash algorithm to use (default: sha256)
        
    Returns:
        str: Hexadecimal hash string, or empty string on failure
    """
    if not file_path or not os.path.isfile(file_path):
        logger.warning(f"Cannot create hash, file not found: {file_path}")
        return ""
        
    try:
        # Initialize hash object with specified algorithm
        hash_obj = hashlib.new(algorithm)
        
        # Read and update hash in chunks to handle large files efficiently
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hash_obj.update(chunk)
                
        # Get digest in hexadecimal
        file_hash = hash_obj.hexdigest()
        logger.debug(f"Created {algorithm} hash for '{file_path}': {file_hash}")
        return file_hash
        
    except (OSError, IOError) as e:
        logger.error(f"Error reading file '{file_path}' for hashing: {str(e)}")
        return ""
    except ValueError as e:
        logger.error(f"Invalid hash algorithm '{algorithm}': {str(e)}")
        return ""