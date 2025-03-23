"""
Utility module providing validation functions for various types of user input data.

This module contains reusable validation logic used across the application for
form submissions, file uploads, and API requests. It implements validation for
common data types like email addresses, phone numbers, URLs, and dates, as well
as sanitization functions to prevent security vulnerabilities.
"""

import re
import html
import datetime
from typing import Dict, List, Tuple, Optional, Any

# Third-party imports
from email_validator import validate_email as email_validator, EmailNotValidError  # email-validator v1.3.0
import phonenumbers  # phonenumbers v8.13.0
import bleach  # bleach v5.0.1
import validators  # validators v0.20.0

# Internal imports
from app.core.exceptions import ValidationException
from app.core.logging import logger
from app.core.config import settings

# Regular expression patterns
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
URL_REGEX = re.compile(r'^https?:\/\/(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&\/=]*)$')
DATE_FORMAT_REGEX = re.compile(r'^\d{4}-\d{2}-\d{2}$')
TIME_FORMAT_REGEX = re.compile(r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$')

# HTML sanitization settings
ALLOWED_HTML_TAGS = ['p', 'br', 'strong', 'em', 'u', 'ul', 'ol', 'li', 'span', 'a']
ALLOWED_HTML_ATTRIBUTES = {'a': ['href', 'title', 'target']}


def validate_email(email: str) -> bool:
    """
    Validates an email address format.
    
    Args:
        email: The email address to validate
        
    Returns:
        bool: True if email is valid, False otherwise
    """
    if not email:
        return False
    
    try:
        # Use email_validator for comprehensive validation
        email_validator(email)
        return True
    except EmailNotValidError:
        logger.warning(f"Invalid email format: {email}")
        return False


def validate_phone(phone: str, region: str = "US") -> bool:
    """
    Validates a phone number format using the phonenumbers library.
    
    Args:
        phone: The phone number to validate
        region: The region code for the phone number (default: US)
        
    Returns:
        bool: True if phone number is valid, False otherwise
    """
    if not phone:
        # Phone is typically optional, so empty is valid
        return True
    
    try:
        phone_number = phonenumbers.parse(phone, region)
        is_valid = phonenumbers.is_valid_number(phone_number)
        
        if not is_valid:
            logger.warning(f"Invalid phone number: {phone}")
            
        return is_valid
    except phonenumbers.NumberParseException:
        logger.warning(f"Could not parse phone number: {phone}")
        return False


def validate_url(url: str) -> bool:
    """
    Validates a URL format.
    
    Args:
        url: The URL to validate
        
    Returns:
        bool: True if URL is valid, False otherwise
    """
    if not url:
        return False
    
    is_valid = validators.url(url)
    
    if not is_valid:
        logger.warning(f"Invalid URL format: {url}")
        
    return bool(is_valid)


def validate_date_format(date_str: str) -> bool:
    """
    Validates a date string in YYYY-MM-DD format.
    
    Args:
        date_str: The date string to validate
        
    Returns:
        bool: True if date format is valid, False otherwise
    """
    if not date_str:
        # Date is often optional
        return True
    
    if not DATE_FORMAT_REGEX.match(date_str):
        logger.warning(f"Invalid date format: {date_str}")
        return False
    
    try:
        datetime.datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        logger.warning(f"Invalid date value: {date_str}")
        return False


def validate_time_format(time_str: str) -> bool:
    """
    Validates a time string in HH:MM format.
    
    Args:
        time_str: The time string to validate
        
    Returns:
        bool: True if time format is valid, False otherwise
    """
    if not time_str:
        # Time is often optional
        return True
    
    if not TIME_FORMAT_REGEX.match(time_str):
        logger.warning(f"Invalid time format: {time_str}")
        return False
    
    try:
        datetime.datetime.strptime(time_str, "%H:%M")
        return True
    except ValueError:
        logger.warning(f"Invalid time value: {time_str}")
        return False


def sanitize_input(text: str, allow_html: bool = False) -> str:
    """
    Sanitizes user input to prevent XSS attacks.
    
    Args:
        text: The text to sanitize
        allow_html: Whether to allow a limited set of HTML tags
        
    Returns:
        str: Sanitized text
    """
    if text is None:
        return ""
    
    if not allow_html:
        return html.escape(text)
    
    # If HTML is allowed, use bleach to sanitize
    return bleach.clean(
        text,
        tags=ALLOWED_HTML_TAGS,
        attributes=ALLOWED_HTML_ATTRIBUTES,
        strip=True
    )


def validate_file_extension(filename: str) -> bool:
    """
    Validates if a file extension is allowed.
    
    Args:
        filename: The name of the file to validate
        
    Returns:
        bool: True if file extension is allowed, False otherwise
    """
    if not filename:
        return False
    
    # Extract extension from filename
    _, extension = os.path.splitext(filename)
    
    # Remove the dot and convert to lowercase
    extension = extension[1:].lower() if extension else ""
    
    # Get allowed extensions from settings
    allowed_extensions = settings.ALLOWED_UPLOAD_EXTENSIONS.split(",")
    
    is_valid = extension in allowed_extensions
    
    if not is_valid:
        logger.warning(f"Invalid file extension: {extension}")
        
    return is_valid


def validate_file_size(file_size: int) -> bool:
    """
    Validates if a file size is within allowed limits.
    
    Args:
        file_size: The size of the file in bytes
        
    Returns:
        bool: True if file size is within limits, False otherwise
    """
    if file_size is None or file_size < 0:
        return False
    
    # Convert MB to bytes
    max_size_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    
    is_valid = file_size <= max_size_bytes
    
    if not is_valid:
        logger.warning(f"File size exceeds limit: {file_size} bytes")
        
    return is_valid


def validate_mime_type(mime_type: str, filename: str) -> bool:
    """
    Validates if a MIME type is consistent with file extension.
    
    Args:
        mime_type: The MIME type to validate
        filename: The filename to check against
        
    Returns:
        bool: True if MIME type is consistent with extension, False otherwise
    """
    if not mime_type or not filename:
        return False
    
    # Extract extension from filename
    _, extension = os.path.splitext(filename)
    extension = extension[1:].lower() if extension else ""
    
    # Define mapping of extensions to expected MIME types
    mime_map = {
        "csv": ["text/csv", "application/csv"],
        "json": ["application/json"],
        "xml": ["application/xml", "text/xml"],
        "jpg": ["image/jpeg"],
        "jpeg": ["image/jpeg"],
        "png": ["image/png"],
        "tiff": ["image/tiff"],
        "mp3": ["audio/mpeg"],
        "wav": ["audio/wav", "audio/x-wav"],
    }
    
    # Check if the extension is in our mapping
    if extension in mime_map:
        is_valid = mime_type in mime_map[extension]
        
        if not is_valid:
            logger.warning(f"MIME type {mime_type} doesn't match extension {extension}")
            
        return is_valid
    
    # If we don't have a mapping for this extension, return True (less strict)
    return True


def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> Tuple[bool, Dict[str, str]]:
    """
    Validates that all required fields are present in a data dictionary.
    
    Args:
        data: The data dictionary to validate
        required_fields: List of field names that are required
        
    Returns:
        tuple: (bool, dict) - Success status and missing fields dictionary
    """
    missing_fields = {}
    
    for field in required_fields:
        if field not in data or data[field] is None or data[field] == "":
            missing_fields[field] = "This field is required"
    
    return len(missing_fields) == 0, missing_fields


def validate_field_length(value: str, min_length: Optional[int] = None, max_length: Optional[int] = None) -> Tuple[bool, str]:
    """
    Validates that a field's length is within specified limits.
    
    Args:
        value: The string value to validate
        min_length: Minimum length (if applicable)
        max_length: Maximum length (if applicable)
        
    Returns:
        tuple: (bool, str) - Success status and error message if any
    """
    if value is None:
        return True, ""
    
    if min_length is not None and len(value) < min_length:
        return False, f"Must be at least {min_length} characters"
    
    if max_length is not None and len(value) > max_length:
        return False, f"Must be no more than {max_length} characters"
    
    return True, ""


def validate_enum_value(value: str, allowed_values: List[str]) -> Tuple[bool, str]:
    """
    Validates that a value is one of the allowed enum values.
    
    Args:
        value: The value to validate
        allowed_values: List of allowed values
        
    Returns:
        tuple: (bool, str) - Success status and error message if any
    """
    if value is None:
        return True, ""
    
    if value not in allowed_values:
        return False, f"Must be one of: {', '.join(allowed_values)}"
    
    return True, ""


class InputValidator:
    """
    Class for validating and sanitizing user input.
    """
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Validates an email address format.
        
        Args:
            email: The email address to validate
            
        Returns:
            bool: True if email is valid, False otherwise
        """
        return validate_email(email)
    
    @staticmethod
    def validate_phone(phone: str, region: str = "US") -> bool:
        """
        Validates a phone number format.
        
        Args:
            phone: The phone number to validate
            region: The region code for the phone number (default: US)
            
        Returns:
            bool: True if phone number is valid, False otherwise
        """
        return validate_phone(phone, region)
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """
        Validates a URL format.
        
        Args:
            url: The URL to validate
            
        Returns:
            bool: True if URL is valid, False otherwise
        """
        return validate_url(url)
    
    @staticmethod
    def validate_date_format(date_str: str) -> bool:
        """
        Validates a date string in YYYY-MM-DD format.
        
        Args:
            date_str: The date string to validate
            
        Returns:
            bool: True if date format is valid, False otherwise
        """
        return validate_date_format(date_str)
    
    @staticmethod
    def validate_time_format(time_str: str) -> bool:
        """
        Validates a time string in HH:MM format.
        
        Args:
            time_str: The time string to validate
            
        Returns:
            bool: True if time format is valid, False otherwise
        """
        return validate_time_format(time_str)
    
    @staticmethod
    def sanitize_input(text: str, allow_html: bool = False) -> str:
        """
        Sanitizes user input to prevent XSS attacks.
        
        Args:
            text: The text to sanitize
            allow_html: Whether to allow a limited set of HTML tags
            
        Returns:
            str: Sanitized text
        """
        return sanitize_input(text, allow_html)
    
    @classmethod
    def validate_form_data(cls, data: Dict[str, Any], 
                          required_fields: List[str] = None, 
                          field_lengths: Dict[str, Dict[str, int]] = None,
                          enum_fields: Dict[str, List[str]] = None) -> Tuple[bool, Dict[str, str]]:
        """
        Validates form data against specified rules.
        
        Args:
            data: The form data to validate
            required_fields: List of required field names
            field_lengths: Dictionary mapping field names to min/max length requirements
            enum_fields: Dictionary mapping field names to allowed values
            
        Returns:
            tuple: (bool, dict) - Success status and validation errors dictionary
        """
        errors = {}
        
        # Validate required fields
        if required_fields:
            is_valid, missing = validate_required_fields(data, required_fields)
            if not is_valid:
                errors.update(missing)
        
        # Validate field lengths
        if field_lengths:
            for field, limits in field_lengths.items():
                if field in data and data[field] is not None:
                    min_length = limits.get("min")
                    max_length = limits.get("max")
                    is_valid, error = validate_field_length(data[field], min_length, max_length)
                    if not is_valid:
                        errors[field] = error
        
        # Validate enum fields
        if enum_fields:
            for field, allowed_values in enum_fields.items():
                if field in data and data[field] is not None:
                    is_valid, error = validate_enum_value(data[field], allowed_values)
                    if not is_valid:
                        errors[field] = error
        
        # Validate email field if present
        if "email" in data and data["email"]:
            if not cls.validate_email(data["email"]):
                errors["email"] = "Invalid email format"
        
        # Validate phone field if present
        if "phone" in data and data["phone"]:
            if not cls.validate_phone(data["phone"]):
                errors["phone"] = "Invalid phone number format"
        
        # Validate date fields if present
        if "preferred_date" in data and data["preferred_date"]:
            if not cls.validate_date_format(data["preferred_date"]):
                errors["preferred_date"] = "Invalid date format (use YYYY-MM-DD)"
        
        # Validate time fields if present
        if "preferred_time" in data and data["preferred_time"]:
            if not cls.validate_time_format(data["preferred_time"]):
                errors["preferred_time"] = "Invalid time format (use HH:MM)"
        
        return len(errors) == 0, errors