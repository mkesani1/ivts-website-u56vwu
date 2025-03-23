"""
Core input validation module for the IndiVillage backend application.

Provides comprehensive validation functions and classes for securing user inputs
across various forms and API endpoints. Implements validation strategies for
different data types, sanitization of inputs, and protection against common
security vulnerabilities like XSS and injection attacks.
"""

import re
import html
from typing import Dict, List, Optional, Any, Callable, TypeVar, Union
from datetime import datetime

import email_validator  # version: 1.3.0
import phonenumbers  # version: 8.13.0
import bleach  # version: 5.0.1
from pydantic import BaseModel  # version: 1.10.0
import validators  # version: 0.20.0

from app.core.exceptions import ValidationException
from app.core.config import settings
from app.core.logging import logger
from app.security.captcha import validate_captcha_token

# Regular expression patterns
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
URL_REGEX = re.compile(r'^https?:\/\/(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&\/=]*)$')
PHONE_REGEX = re.compile(r'^\+?[0-9\s\-\(\)]{8,20}$')
DATE_FORMAT_REGEX = re.compile(r'^\d{4}-\d{2}-\d{2}$')
TIME_FORMAT_REGEX = re.compile(r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$')

# HTML sanitization settings
ALLOWED_HTML_TAGS = ['p', 'br', 'strong', 'em', 'u', 'ul', 'ol', 'li', 'span', 'a']
ALLOWED_HTML_ATTRIBUTES = {'a': ['href', 'title', 'target']}


def validate_email(email: str) -> bool:
    """
    Validates an email address format.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if email is valid, False otherwise
    """
    if not email:
        return False
    
    try:
        # Use email_validator for comprehensive validation
        email_validator.validate_email(email)
        return True
    except email_validator.EmailNotValidError:
        logger.warning(f"Invalid email format: {email}")
        return False


def validate_phone(phone: str, region: str = "US") -> bool:
    """
    Validates a phone number format using the phonenumbers library.
    
    Args:
        phone: Phone number to validate
        region: Region/country code for phone number validation
        
    Returns:
        True if phone number is valid, False otherwise
    """
    if not phone:
        # Phone number is optional in most cases
        return True
    
    try:
        # Parse the phone number
        parsed_number = phonenumbers.parse(phone, region)
        
        # Check if the number is valid for the given region
        if not phonenumbers.is_valid_number(parsed_number):
            logger.warning(f"Invalid phone number for region {region}: {phone}")
            return False
        
        return True
    except phonenumbers.NumberParseException:
        logger.warning(f"Could not parse phone number: {phone}")
        return False


def validate_url(url: str) -> bool:
    """
    Validates a URL format.
    
    Args:
        url: URL to validate
        
    Returns:
        True if URL is valid, False otherwise
    """
    if not url:
        return False
    
    # Use validators.url for comprehensive URL validation
    if validators.url(url):
        return True
    
    logger.warning(f"Invalid URL format: {url}")
    return False


def validate_date_format(date_str: str) -> bool:
    """
    Validates a date string in YYYY-MM-DD format.
    
    Args:
        date_str: Date string to validate
        
    Returns:
        True if date format is valid, False otherwise
    """
    if not date_str:
        # Date is optional in most cases
        return True
    
    if not DATE_FORMAT_REGEX.match(date_str):
        logger.warning(f"Invalid date format: {date_str}")
        return False
    
    try:
        # Attempt to parse the date
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        logger.warning(f"Invalid date value: {date_str}")
        return False


def validate_time_format(time_str: str) -> bool:
    """
    Validates a time string in HH:MM format.
    
    Args:
        time_str: Time string to validate
        
    Returns:
        True if time format is valid, False otherwise
    """
    if not time_str:
        # Time is optional in most cases
        return True
    
    if not TIME_FORMAT_REGEX.match(time_str):
        logger.warning(f"Invalid time format: {time_str}")
        return False
    
    try:
        # Attempt to parse the time
        datetime.strptime(time_str, "%H:%M")
        return True
    except ValueError:
        logger.warning(f"Invalid time value: {time_str}")
        return False


def sanitize_input(text: str, allow_html: bool = False) -> str:
    """
    Sanitizes user input to prevent XSS attacks.
    
    Args:
        text: Text to sanitize
        allow_html: Whether to allow specific HTML tags
        
    Returns:
        Sanitized text
    """
    if text is None:
        return ""
    
    if not allow_html:
        # Escape all HTML
        return html.escape(text)
    
    # Allow specific HTML tags and attributes
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
        filename: Name of the file to validate
        
    Returns:
        True if file extension is allowed, False otherwise
    """
    if not filename:
        return False
    
    # Get the extension
    try:
        extension = filename.rsplit('.', 1)[1].lower()
    except IndexError:
        logger.warning(f"No file extension found in: {filename}")
        return False
    
    # Get allowed extensions from settings
    allowed_extensions = settings.ALLOWED_UPLOAD_EXTENSIONS.split(',')
    allowed_extensions = [ext.strip().lower() for ext in allowed_extensions]
    
    if extension not in allowed_extensions:
        logger.warning(f"File extension not allowed: {extension}")
        return False
    
    return True


def validate_file_size(file_size: int) -> bool:
    """
    Validates if a file size is within allowed limits.
    
    Args:
        file_size: Size of the file in bytes
        
    Returns:
        True if file size is within limits, False otherwise
    """
    if file_size is None or file_size < 0:
        return False
    
    # Convert MB to bytes
    max_size_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    
    if file_size > max_size_bytes:
        logger.warning(f"File size exceeds maximum allowed ({settings.MAX_UPLOAD_SIZE_MB}MB): {file_size} bytes")
        return False
    
    return True


def validate_mime_type(mime_type: str, filename: str) -> bool:
    """
    Validates if a MIME type is consistent with file extension.
    
    Args:
        mime_type: MIME type to validate
        filename: Name of the file
        
    Returns:
        True if MIME type is consistent with extension, False otherwise
    """
    if not mime_type or not filename:
        return False
    
    try:
        extension = filename.rsplit('.', 1)[1].lower()
    except IndexError:
        logger.warning(f"No file extension found in: {filename}")
        return False
    
    # Define mapping of extensions to expected MIME types
    mime_type_mapping = {
        'csv': ['text/csv', 'application/csv', 'application/vnd.ms-excel'],
        'json': ['application/json', 'text/json'],
        'xml': ['application/xml', 'text/xml'],
        'jpg': ['image/jpeg'],
        'jpeg': ['image/jpeg'],
        'png': ['image/png'],
        'tiff': ['image/tiff'],
        'mp3': ['audio/mpeg', 'audio/mp3'],
        'wav': ['audio/wav', 'audio/x-wav']
    }
    
    # Check if the extension is in our mapping
    if extension in mime_type_mapping:
        expected_mime_types = mime_type_mapping[extension]
        
        if mime_type.lower() not in expected_mime_types:
            logger.warning(f"MIME type '{mime_type}' doesn't match expected types for .{extension}")
            return False
    
    return True


def validate_required_fields(data: Dict, required_fields: List[str]) -> tuple:
    """
    Validates that all required fields are present in a data dictionary.
    
    Args:
        data: Dictionary containing form data
        required_fields: List of required field names
        
    Returns:
        Tuple of (bool, dict) - Success status and missing fields dictionary
    """
    missing_fields = {}
    
    for field in required_fields:
        if field not in data or data[field] is None or data[field] == "":
            missing_fields[field] = "This field is required"
    
    if missing_fields:
        return False, missing_fields
    
    return True, {}


def validate_field_length(value: str, min_length: int = None, max_length: int = None) -> tuple:
    """
    Validates that a field's length is within specified limits.
    
    Args:
        value: String value to validate
        min_length: Minimum allowed length
        max_length: Maximum allowed length
        
    Returns:
        Tuple of (bool, str) - Success status and error message if any
    """
    if value is None:
        return True, ""
    
    if min_length and len(value) < min_length:
        return False, f"Must be at least {min_length} characters"
    
    if max_length and len(value) > max_length:
        return False, f"Must be at most {max_length} characters"
    
    return True, ""


def validate_enum_value(value: str, allowed_values: List[str]) -> tuple:
    """
    Validates that a value is one of the allowed enum values.
    
    Args:
        value: Value to validate
        allowed_values: List of allowed values
        
    Returns:
        Tuple of (bool, str) - Success status and error message if any
    """
    if value is None:
        return True, ""
    
    if value not in allowed_values:
        return False, f"Must be one of: {', '.join(allowed_values)}"
    
    return True, ""


def validate_captcha(token: str, remote_ip: str) -> bool:
    """
    Validates a CAPTCHA token from a request.
    
    Args:
        token: CAPTCHA token to validate
        remote_ip: IP address of the client
        
    Returns:
        True if CAPTCHA is valid, False otherwise
    """
    if not token:
        logger.warning("Missing CAPTCHA token")
        return False
    
    # Use the captcha module's validation function
    valid = validate_captcha_token(token, remote_ip)
    
    if not valid:
        logger.warning(f"CAPTCHA validation failed for token from IP: {remote_ip}")
    
    return valid


def validate_contact_form(data: Dict) -> tuple:
    """
    Validates contact form data.
    
    Args:
        data: Dictionary containing form data
        
    Returns:
        Tuple of (bool, dict) - Success status and validation errors dictionary
    """
    errors = {}
    
    # Define required fields
    required_fields = ["name", "email", "message"]
    
    # Validate required fields
    valid, missing = validate_required_fields(data, required_fields)
    if not valid:
        errors.update(missing)
    
    # Validate email format
    if "email" in data and data["email"]:
        if not validate_email(data["email"]):
            errors["email"] = "Please enter a valid email address"
    
    # Validate phone format (if provided)
    if "phone" in data and data["phone"]:
        if not validate_phone(data["phone"]):
            errors["phone"] = "Please enter a valid phone number"
    
    # Validate field lengths
    for field, (min_len, max_len) in {
        "name": (2, 100),
        "email": (5, 100),
        "company": (0, 100),
        "message": (10, 1000)
    }.items():
        if field in data and data[field]:
            valid, error = validate_field_length(data[field], min_len, max_len)
            if not valid:
                errors[field] = error
    
    # Return validation result
    if errors:
        return False, errors
    
    return True, {}


def validate_demo_request_form(data: Dict) -> tuple:
    """
    Validates demo request form data.
    
    Args:
        data: Dictionary containing form data
        
    Returns:
        Tuple of (bool, dict) - Success status and validation errors dictionary
    """
    errors = {}
    
    # Define required fields
    required_fields = ["first_name", "last_name", "email", "company", "service_interests"]
    
    # Validate required fields
    valid, missing = validate_required_fields(data, required_fields)
    if not valid:
        errors.update(missing)
    
    # Validate email format
    if "email" in data and data["email"]:
        if not validate_email(data["email"]):
            errors["email"] = "Please enter a valid email address"
    
    # Validate phone format (if provided)
    if "phone" in data and data["phone"]:
        if not validate_phone(data["phone"]):
            errors["phone"] = "Please enter a valid phone number"
    
    # Validate date format (if provided)
    if "preferred_date" in data and data["preferred_date"]:
        if not validate_date_format(data["preferred_date"]):
            errors["preferred_date"] = "Please use YYYY-MM-DD format"
    
    # Validate time format (if provided)
    if "preferred_time" in data and data["preferred_time"]:
        if not validate_time_format(data["preferred_time"]):
            errors["preferred_time"] = "Please use HH:MM format"
    
    # Validate field lengths
    for field, (min_len, max_len) in {
        "first_name": (2, 50),
        "last_name": (2, 50),
        "email": (5, 100),
        "company": (2, 100),
        "job_title": (0, 100),
        "project_description": (0, 2000)
    }.items():
        if field in data and data[field]:
            valid, error = validate_field_length(data[field], min_len, max_len)
            if not valid:
                errors[field] = error
    
    # Validate service interests
    if "service_interests" in data and data["service_interests"]:
        allowed_services = ["data_collection", "data_preparation", "ai_model_development", "human_in_the_loop"]
        
        if isinstance(data["service_interests"], list):
            for service in data["service_interests"]:
                valid, error = validate_enum_value(service, allowed_services)
                if not valid:
                    errors["service_interests"] = error
                    break
        else:
            valid, error = validate_enum_value(data["service_interests"], allowed_services)
            if not valid:
                errors["service_interests"] = error
    
    # Return validation result
    if errors:
        return False, errors
    
    return True, {}


def validate_quote_request_form(data: Dict) -> tuple:
    """
    Validates quote request form data.
    
    Args:
        data: Dictionary containing form data
        
    Returns:
        Tuple of (bool, dict) - Success status and validation errors dictionary
    """
    errors = {}
    
    # Define required fields
    required_fields = ["first_name", "last_name", "email", "company", "service_interests", "project_description"]
    
    # Validate required fields
    valid, missing = validate_required_fields(data, required_fields)
    if not valid:
        errors.update(missing)
    
    # Validate email format
    if "email" in data and data["email"]:
        if not validate_email(data["email"]):
            errors["email"] = "Please enter a valid email address"
    
    # Validate phone format (if provided)
    if "phone" in data and data["phone"]:
        if not validate_phone(data["phone"]):
            errors["phone"] = "Please enter a valid phone number"
    
    # Validate field lengths
    for field, (min_len, max_len) in {
        "first_name": (2, 50),
        "last_name": (2, 50),
        "email": (5, 100),
        "company": (2, 100),
        "job_title": (0, 100),
        "project_description": (20, 5000)
    }.items():
        if field in data and data[field]:
            valid, error = validate_field_length(data[field], min_len, max_len)
            if not valid:
                errors[field] = error
    
    # Validate service interests
    if "service_interests" in data and data["service_interests"]:
        allowed_services = ["data_collection", "data_preparation", "ai_model_development", "human_in_the_loop"]
        
        if isinstance(data["service_interests"], list):
            for service in data["service_interests"]:
                valid, error = validate_enum_value(service, allowed_services)
                if not valid:
                    errors["service_interests"] = error
                    break
        else:
            valid, error = validate_enum_value(data["service_interests"], allowed_services)
            if not valid:
                errors["service_interests"] = error
    
    # Validate budget range
    if "budget_range" in data and data["budget_range"]:
        allowed_ranges = ["under_10k", "10k_50k", "50k_100k", "100k_500k", "over_500k"]
        valid, error = validate_enum_value(data["budget_range"], allowed_ranges)
        if not valid:
            errors["budget_range"] = error
    
    # Validate project timeline
    if "project_timeline" in data and data["project_timeline"]:
        allowed_timelines = ["immediate", "1_3_months", "3_6_months", "6_12_months", "beyond_12_months"]
        valid, error = validate_enum_value(data["project_timeline"], allowed_timelines)
        if not valid:
            errors["project_timeline"] = error
    
    # Return validation result
    if errors:
        return False, errors
    
    return True, {}


def validate_upload_request_form(data: Dict) -> tuple:
    """
    Validates file upload request form data.
    
    Args:
        data: Dictionary containing form data
        
    Returns:
        Tuple of (bool, dict) - Success status and validation errors dictionary
    """
    errors = {}
    
    # Define required fields
    required_fields = ["name", "email", "service_interest"]
    
    # Validate required fields
    valid, missing = validate_required_fields(data, required_fields)
    if not valid:
        errors.update(missing)
    
    # Validate email format
    if "email" in data and data["email"]:
        if not validate_email(data["email"]):
            errors["email"] = "Please enter a valid email address"
    
    # Validate phone format (if provided)
    if "phone" in data and data["phone"]:
        if not validate_phone(data["phone"]):
            errors["phone"] = "Please enter a valid phone number"
    
    # Validate service interest
    if "service_interest" in data and data["service_interest"]:
        allowed_services = ["data_collection", "data_preparation", "ai_model_development", "human_in_the_loop", "not_sure"]
        valid, error = validate_enum_value(data["service_interest"], allowed_services)
        if not valid:
            errors["service_interest"] = error
    
    # Validate field lengths
    for field, (min_len, max_len) in {
        "name": (2, 100),
        "email": (5, 100),
        "company": (0, 100),
        "description": (0, 2000)
    }.items():
        if field in data and data[field]:
            valid, error = validate_field_length(data[field], min_len, max_len)
            if not valid:
                errors[field] = error
    
    # Return validation result
    if errors:
        return False, errors
    
    return True, {}


def validate_file_metadata(metadata: Dict) -> tuple:
    """
    Validates file metadata for uploads.
    
    Args:
        metadata: Dictionary containing file metadata
        
    Returns:
        Tuple of (bool, dict) - Success status and validation errors dictionary
    """
    errors = {}
    
    # Define required fields
    required_fields = ["filename", "size", "mime_type"]
    
    # Validate required fields
    valid, missing = validate_required_fields(metadata, required_fields)
    if not valid:
        errors.update(missing)
    
    # Validate file extension
    if "filename" in metadata and metadata["filename"]:
        if not validate_file_extension(metadata["filename"]):
            errors["filename"] = "File type not allowed"
    
    # Validate file size
    if "size" in metadata and metadata["size"]:
        try:
            size = int(metadata["size"])
            if not validate_file_size(size):
                errors["size"] = f"File size exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE_MB}MB"
        except (ValueError, TypeError):
            errors["size"] = "Invalid file size"
    
    # Validate MIME type
    if all(k in metadata for k in ["mime_type", "filename"]) and metadata["mime_type"] and metadata["filename"]:
        if not validate_mime_type(metadata["mime_type"], metadata["filename"]):
            errors["mime_type"] = "MIME type does not match file extension"
    
    # Return validation result
    if errors:
        return False, errors
    
    return True, {}


class InputValidator:
    """
    Class for validating and sanitizing user input.
    
    This class provides a reusable interface for input validation functions
    across the application.
    """
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Validates an email address format.
        
        Args:
            email: Email address to validate
            
        Returns:
            True if email is valid, False otherwise
        """
        return validate_email(email)
    
    @staticmethod
    def validate_phone(phone: str, region: str = "US") -> bool:
        """
        Validates a phone number format.
        
        Args:
            phone: Phone number to validate
            region: Region/country code for phone number validation
            
        Returns:
            True if phone number is valid, False otherwise
        """
        return validate_phone(phone, region)
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """
        Validates a URL format.
        
        Args:
            url: URL to validate
            
        Returns:
            True if URL is valid, False otherwise
        """
        return validate_url(url)
    
    @staticmethod
    def validate_date_format(date_str: str) -> bool:
        """
        Validates a date string in YYYY-MM-DD format.
        
        Args:
            date_str: Date string to validate
            
        Returns:
            True if date format is valid, False otherwise
        """
        return validate_date_format(date_str)
    
    @staticmethod
    def validate_time_format(time_str: str) -> bool:
        """
        Validates a time string in HH:MM format.
        
        Args:
            time_str: Time string to validate
            
        Returns:
            True if time format is valid, False otherwise
        """
        return validate_time_format(time_str)
    
    @staticmethod
    def sanitize_input(text: str, allow_html: bool = False) -> str:
        """
        Sanitizes user input to prevent XSS attacks.
        
        Args:
            text: Text to sanitize
            allow_html: Whether to allow specific HTML tags
            
        Returns:
            Sanitized text
        """
        return sanitize_input(text, allow_html)
    
    @staticmethod
    def validate_file_extension(filename: str) -> bool:
        """
        Validates if a file extension is allowed.
        
        Args:
            filename: Name of the file to validate
            
        Returns:
            True if file extension is allowed, False otherwise
        """
        return validate_file_extension(filename)
    
    @staticmethod
    def validate_file_size(file_size: int) -> bool:
        """
        Validates if a file size is within allowed limits.
        
        Args:
            file_size: Size of the file in bytes
            
        Returns:
            True if file size is within limits, False otherwise
        """
        return validate_file_size(file_size)
    
    @staticmethod
    def validate_mime_type(mime_type: str, filename: str) -> bool:
        """
        Validates if a MIME type is consistent with file extension.
        
        Args:
            mime_type: MIME type to validate
            filename: Name of the file
            
        Returns:
            True if MIME type is consistent with extension, False otherwise
        """
        return validate_mime_type(mime_type, filename)
    
    @staticmethod
    def validate_captcha(token: str, remote_ip: str) -> bool:
        """
        Validates a CAPTCHA token from a request.
        
        Args:
            token: CAPTCHA token to validate
            remote_ip: IP address of the client
            
        Returns:
            True if CAPTCHA is valid, False otherwise
        """
        return validate_captcha(token, remote_ip)
    
    @classmethod
    def validate_form_data(cls, data: Dict, form_type: str) -> tuple:
        """
        Validates form data against specified rules.
        
        Args:
            data: Form data to validate
            form_type: Type of form ("contact", "demo_request", "quote_request", "upload_request")
            
        Returns:
            Tuple of (bool, validation_errors_dict)
        """
        if form_type == "contact":
            return validate_contact_form(data)
        elif form_type == "demo_request":
            return validate_demo_request_form(data)
        elif form_type == "quote_request":
            return validate_quote_request_form(data)
        elif form_type == "upload_request":
            return validate_upload_request_form(data)
        else:
            logger.warning(f"Unknown form type: {form_type}")
            return False, {"form_type": "Unknown form type"}


class ValidationDecorator:
    """
    Decorator class for adding validation to API endpoints.
    
    This class provides decorators that can be applied to API endpoint functions
    to automatically validate incoming request data before processing.
    """
    
    @staticmethod
    def validate_request_data(schema_class: BaseModel):
        """
        Decorator for validating request data against a schema.
        
        Args:
            schema_class: Pydantic model class to validate against
            
        Returns:
            Decorated function
        """
        def decorator(func):
            async def wrapper(request, *args, **kwargs):
                # Extract request data (either JSON or form data)
                try:
                    if request.method in ["POST", "PUT", "PATCH"]:
                        try:
                            data = await request.json()
                        except:
                            # If not JSON, try form data
                            form = await request.form()
                            data = {key: value for key, value in form.items()}
                    else:
                        # For GET requests, use query parameters
                        data = dict(request.query_params)
                except Exception as e:
                    logger.error(f"Error extracting request data: {str(e)}")
                    raise ValidationException("Invalid request format", details={"error": str(e)})
                
                # Validate against the schema
                try:
                    validated_data = schema_class(**data)
                    # Convert to dict for passing to the function
                    validated_dict = validated_data.dict()
                    # Call the original function with validated data
                    return await func(request, validated_data=validated_dict, *args, **kwargs)
                except Exception as e:
                    logger.error(f"Validation error: {str(e)}")
                    raise ValidationException("Validation failed", details={"errors": str(e)})
            
            return wrapper
        
        return decorator
    
    @staticmethod
    def validate_form_submission(form_type: str):
        """
        Decorator for validating form submissions.
        
        Args:
            form_type: Type of form to validate
            
        Returns:
            Decorated function
        """
        def decorator(func):
            async def wrapper(request, *args, **kwargs):
                # Extract request data (either JSON or form data)
                try:
                    if request.method in ["POST", "PUT", "PATCH"]:
                        try:
                            data = await request.json()
                        except:
                            # If not JSON, try form data
                            form = await request.form()
                            data = {key: value for key, value in form.items()}
                    else:
                        # For GET requests, use query parameters
                        data = dict(request.query_params)
                except Exception as e:
                    logger.error(f"Error extracting request data: {str(e)}")
                    raise ValidationException("Invalid request format", details={"error": str(e)})
                
                # Validate the form submission
                valid, errors = InputValidator.validate_form_data(data, form_type)
                
                if not valid:
                    logger.warning(f"Form validation failed for {form_type}")
                    raise ValidationException("Form validation failed", details={"errors": errors})
                
                # Call the original function with validated data
                return await func(request, validated_data=data, *args, **kwargs)
            
            return wrapper
        
        return decorator
    
    @staticmethod
    def require_captcha():
        """
        Decorator for requiring CAPTCHA verification.
        
        Returns:
            Decorated function
        """
        def decorator(func):
            async def wrapper(request, *args, **kwargs):
                # Extract request data (either JSON or form data)
                try:
                    if request.method in ["POST", "PUT", "PATCH"]:
                        try:
                            data = await request.json()
                        except:
                            # If not JSON, try form data
                            form = await request.form()
                            data = {key: value for key, value in form.items()}
                    else:
                        # For GET requests, use query parameters
                        data = dict(request.query_params)
                except Exception:
                    data = {}
                
                # Extract CAPTCHA token
                token = data.get("captcha_token", data.get("g-recaptcha-response"))
                
                # Extract client IP
                client_host = request.client.host if hasattr(request, 'client') and request.client else "unknown"
                
                # Validate CAPTCHA
                if not validate_captcha(token, client_host):
                    logger.warning(f"CAPTCHA validation failed for request from {client_host}")
                    raise ValidationException("CAPTCHA validation failed")
                
                # Call the original function
                return await func(request, *args, **kwargs)
            
            return wrapper
        
        return decorator