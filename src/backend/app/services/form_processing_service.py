# typing
from typing import Dict, List, Optional, Any, Union, Tuple
# datetime
import datetime
# functools
import functools

# Import application configuration settings
from ..core.config import settings
# Import logger for security-related logging
from ..utils.logging_utils import get_component_logger
# Import security exception for handling security-related errors
from ..core.exceptions import SecurityException
# Import authentication exception for handling authentication errors
from ..core.exceptions import AuthenticationException
# Import password management functionality
from ..core.security import PasswordManager
# Import token management functionality
from ..core.security import TokenManager
# Import JWT handling functionality
from ..security.jwt import JWTHandler
# Import input validation functionality
from ..security.input_validation import InputValidator
# Import file scanning functionality
from ..security.file_scanner import FileScanner
# Import rate limiting functionality
from ..security.rate_limiting import RateLimiter
# Import rate limiting strategy enum
from ..security.rate_limiting import RateLimitStrategy
# Import CAPTCHA verification functionality
from ..security.captcha import CaptchaVerifier

# Define default rate limit
DEFAULT_RATE_LIMIT = 100
# Define default rate limit window
DEFAULT_RATE_WINDOW = 3600
# Define CAPTCHA score threshold
CAPTCHA_SCORE_THRESHOLD = 0.5

# Initialize logger for the security service
logger = get_component_logger('security_service')

def sanitize_user_input(text: str, allow_html: bool) -> str:
    """Sanitizes user input to prevent XSS and other injection attacks

    Args:
        text (str): text
        allow_html (bool): allow_html

    Returns:
        str: Sanitized text safe for use in the application
    """
    # Call InputValidator.sanitize_input with the provided text and allow_html flag
    input_validator = InputValidator()
    sanitized_text = input_validator.sanitize_input(text, allow_html)
    # Return the sanitized text
    return sanitized_text


def validate_form_submission(form_data: Dict[str, Any], form_type: str) -> Tuple[bool, Dict[str, str]]:
    """Validates a form submission against the appropriate validation rules

    Args:
        form_data (Dict[str, Any]): form_data
        form_type (str): form_type

    Returns:
        Tuple[bool, Dict[str, str]]: Validation result (success, errors)
    """
    # Call InputValidator.validate_form_data with form_data and form_type
    input_validator = InputValidator()
    success, errors = input_validator.validate_form_data(form_data, form_type)
    # Return the validation result tuple (success, errors)
    return success, errors


def verify_captcha_response(token: str, remote_ip: str, threshold: float) -> bool:
    """Verifies a CAPTCHA response token against the reCAPTCHA service

    Args:
        token (str): token
        remote_ip (str): remote_ip
        threshold (float): threshold

    Returns:
        bool: True if CAPTCHA verification passes, False otherwise
    """
    # Initialize CaptchaVerifier if not already initialized
    captcha_verifier = CaptchaVerifier()
    # Call captcha_verifier.validate with token, remote_ip, and threshold
    is_valid = captcha_verifier.validate(token, remote_ip, threshold)
    # Return the validation result
    return is_valid


def check_rate_limit(identifier: str, endpoint: str, limit: int, window_seconds: int) -> Tuple[bool, Dict[str, str]]:
    """Checks if a request is within rate limits

    Args:
        identifier (str): identifier
        endpoint (str): endpoint
        limit (int): limit
        window_seconds (int): window_seconds

    Returns:
        Tuple[bool, Dict[str, str]]: Rate limit check result (allowed, headers)
    """
    # Initialize RateLimiter if not already initialized
    rate_limiter = RateLimiter()
    # Call rate_limiter.limit_by_ip or limit_by_user based on identifier type
    try:
        is_allowed, remaining, reset_time = rate_limiter.limit_by_ip(identifier, endpoint, limit, window_seconds)
    except Exception as e:
        logger.error(f"Rate limiting check failed: {str(e)}")
        return False, {}
    # Get rate limit headers using rate_limiter.get_headers
    headers = rate_limiter.get_headers(limit, remaining, reset_time)
    # Return tuple with allowed status and headers
    return is_allowed, headers


def scan_uploaded_file(file_path: str) -> Dict[str, Any]:
    """Scans an uploaded file for security threats

    Args:
        file_path (str): file_path

    Returns:
        Dict[str, Any]: Scan result with status and details
    """
    # Initialize FileScanner if not already initialized
    file_scanner = FileScanner()
    # Call file_scanner.scan_file with file_path
    scan_result = file_scanner.scan_file(file_path)
    # Return the scan result
    return scan_result


def scan_s3_file(object_key: str, bucket_name: str) -> Dict[str, Any]:
    """Scans a file stored in S3 for security threats

    Args:
        object_key (str): object_key
        bucket_name (str): bucket_name

    Returns:
        Dict[str, Any]: Scan result with status and details
    """
    # Initialize FileScanner if not already initialized
    file_scanner = FileScanner()
    # Call file_scanner.scan_s3_file with object_key and bucket_name
    scan_result = file_scanner.scan_s3_file(object_key, bucket_name)
    # Return the scan result
    return scan_result


def validate_file_upload(filename: str, file_size: int, mime_type: str) -> Tuple[bool, Dict[str, str]]:
    """Validates a file upload for security and compliance

    Args:
        filename (str): filename
        file_size (int): file_size
        mime_type (str): mime_type

    Returns:
        Tuple[bool, Dict[str, str]]: Validation result (success, errors)
    """
    # Validate file extension using InputValidator.validate_file_extension
    input_validator = InputValidator()
    is_valid_extension = input_validator.validate_file_extension(filename)
    # Validate file size using InputValidator.validate_file_size
    is_valid_size = input_validator.validate_file_size(file_size)
    # Validate MIME type consistency
    is_valid_mime = input_validator.validate_mime_type(mime_type, filename)

    errors = {}
    if not is_valid_extension:
        errors["filename"] = "Invalid file extension"
    if not is_valid_size:
        errors["file_size"] = "File size exceeds the limit"
    if not is_valid_mime:
        errors["mime_type"] = "MIME type does not match file extension"

    # Return validation result tuple (success, errors)
    if errors:
        return False, errors
    else:
        return True, {}


def hash_password(password: str) -> str:
    """Hashes a password securely

    Args:
        password (str): password

    Returns:
        str: Securely hashed password
    """
    # Initialize PasswordManager if not already initialized
    password_manager = PasswordManager()
    # Call password_manager.hash_password with password
    hashed_password = password_manager.hash_password(password)
    # Return the hashed password
    return hashed_password


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a password against a hash

    Args:
        plain_password (str): plain_password
        hashed_password (str): hashed_password

    Returns:
        bool: True if password matches hash, False otherwise
    """
    # Initialize PasswordManager if not already initialized
    password_manager = PasswordManager()
    # Call password_manager.verify_password with plain_password and hashed_password
    is_valid = password_manager.verify_password(plain_password, hashed_password)
    # Return the verification result
    return is_valid


def validate_password_strength(password: str) -> bool:
    """Validates password strength against security requirements

    Args:
        password (str): password

    Returns:
        bool: True if password meets strength requirements, False otherwise
    """
    # Initialize PasswordManager if not already initialized
    password_manager = PasswordManager()
    # Call password_manager.validate_strength with password
    is_strong = password_manager.validate_strength(password)
    # Return the validation result
    return is_strong


def create_auth_tokens(user_data: Dict[str, Any]) -> Dict[str, str]:
    """Creates authentication tokens for a user

    Args:
        user_data (Dict[str, Any]): user_data

    Returns:
        Dict[str, str]: Dictionary containing access_token and refresh_token
    """
    # Initialize JWTHandler if not already initialized
    jwt_handler = JWTHandler()
    # Call jwt_handler.create_access_token for access token
    tokens = jwt_handler.create_tokens(user_data)
    # Return dictionary with both tokens
    return tokens


def validate_auth_token(token: str) -> Dict[str, Any]:
    """Validates an authentication token

    Args:
        token (str): token

    Returns:
        Dict[str, Any]: Decoded token payload if valid
    """
    # Initialize JWTHandler if not already initialized
    jwt_handler = JWTHandler()
    # Call jwt_handler.validate_access_token with token
    try:
        payload = jwt_handler.validate_access_token(token)
        # Return the decoded payload if valid
        return payload
    except AuthenticationException as e:
        # Catch and log any authentication exceptions
        logger.error(f"Authentication failed: {str(e)}")
        raise


class SecurityService:
    """Comprehensive security service that coordinates various security components"""

    def __init__(self):
        """Initializes the SecurityService with all required components"""
        # Initialize PasswordManager for password operations
        self._password_manager = PasswordManager()
        # Initialize JWTHandler for JWT token operations
        self._jwt_handler = JWTHandler()
        # Initialize InputValidator for input validation
        self._input_validator = InputValidator()
        # Initialize FileScanner for file scanning
        self._file_scanner = FileScanner()
        # Initialize RateLimiter for rate limiting
        self._rate_limiter = RateLimiter()
        # Initialize CaptchaVerifier for CAPTCHA verification
        self._captcha_verifier = CaptchaVerifier()
        # Log service initialization
        logger.info("SecurityService initialized")

    def sanitize_input(self, text: str, allow_html: bool) -> str:
        """Sanitizes user input to prevent XSS and other injection attacks

        Args:
            text (str): text
            allow_html (bool): allow_html

        Returns:
            str: Sanitized text safe for use in the application
        """
        # Call self._input_validator.sanitize_input with text and allow_html
        sanitized_text = self._input_validator.sanitize_input(text, allow_html)
        # Return the sanitized text
        return sanitized_text

    def validate_form(self, form_data: Dict[str, Any], form_type: str) -> Tuple[bool, Dict[str, str]]:
        """Validates a form submission against the appropriate validation rules

        Args:
            form_data (Dict[str, Any]): form_data
            form_type (str): form_type

        Returns:
            Tuple[bool, Dict[str, str]]: Validation result (success, errors)
        """
        # Call self._input_validator.validate_form_data with form_data and form_type
        success, errors = self._input_validator.validate_form_data(form_data, form_type)
        # Return the validation result tuple (success, errors)
        return success, errors

    def verify_captcha(self, token: str, remote_ip: str, threshold: float = CAPTCHA_SCORE_THRESHOLD) -> bool:
        """Verifies a CAPTCHA response token against the reCAPTCHA service

        Args:
            token (str): token
            remote_ip (str): remote_ip
            threshold (float): threshold

        Returns:
            bool: True if CAPTCHA verification passes, False otherwise
        """
        # Call self._captcha_verifier.validate with token, remote_ip, and threshold
        is_valid = self._captcha_verifier.validate(token, remote_ip, threshold)
        # Return the validation result
        return is_valid

    def check_rate_limit(self, identifier: str, endpoint: str, limit: int = DEFAULT_RATE_LIMIT, window_seconds: int = DEFAULT_RATE_WINDOW) -> Tuple[bool, Dict[str, str]]:
        """Checks if a request is within rate limits

        Args:
            identifier (str): identifier
            endpoint (str): endpoint
            limit (int): limit
            window_seconds (int): window_seconds

        Returns:
            Tuple[bool, Dict[str, str]]: Rate limit check result (allowed, headers)
        """
        # Call self._rate_limiter.limit_by_ip or limit_by_user based on identifier type
        try:
            is_allowed, remaining, reset_time = self._rate_limiter.limit_by_ip(identifier, endpoint, limit, window_seconds)
        except Exception as e:
            logger.error(f"Rate limiting check failed: {str(e)}")
            return False, {}
        # Get rate limit headers using self._rate_limiter.get_headers
        headers = self._rate_limiter.get_headers(limit, remaining, reset_time)
        # Return tuple with allowed status and headers
        return is_allowed, headers

    def scan_file(self, file_path: str) -> Dict[str, Any]:
        """Scans a file for security threats

        Args:
            file_path (str): file_path

        Returns:
            Dict[str, Any]: Scan result with status and details
        """
        # Call self._file_scanner.scan_file with file_path
        scan_result = self._file_scanner.scan_file(file_path)
        # Return the scan result
        return scan_result

    def scan_s3_file(self, object_key: str, bucket_name: str) -> Dict[str, Any]:
        """Scans a file stored in S3 for security threats

        Args:
            object_key (str): object_key
            bucket_name (str): bucket_name

        Returns:
            Dict[str, Any]: Scan result with status and details
        """
        # Call self._file_scanner.scan_s3_file with object_key and bucket_name
        scan_result = self._file_scanner.scan_s3_file(object_key, bucket_name)
        # Return the scan result
        return scan_result

    def validate_file(self, filename: str, file_size: int, mime_type: str) -> Tuple[bool, Dict[str, str]]:
        """Validates a file upload for security and compliance

        Args:
            filename (str): filename
            file_size (int): file_size
            mime_type (str): mime_type

        Returns:
            Tuple[bool, Dict[str, str]]: Validation result (success, errors)
        """
        # Validate file extension using self._input_validator.validate_file_extension
        is_valid_extension = self._input_validator.validate_file_extension(filename)
        # Validate file size using self._input_validator.validate_file_size
        is_valid_size = self._input_validator.validate_file_size(file_size)
        # Validate MIME type consistency
        is_valid_mime = self._input_validator.validate_mime_type(mime_type, filename)

        errors = {}
        if not is_valid_extension:
            errors["filename"] = "Invalid file extension"
        if not is_valid_size:
            errors["file_size"] = "File size exceeds the limit"
        if not is_valid_mime:
            errors["mime_type"] = "MIME type does not match file extension"

        # Return validation result tuple (success, errors)
        if errors:
            return False, errors
        else:
            return True, {}

    def hash_password(self, password: str) -> str:
        """Hashes a password securely

        Args:
            password (str): password

        Returns:
            str: Securely hashed password
        """
        # Call self._password_manager.hash_password with password
        hashed_password = self._password_manager.hash_password(password)
        # Return the hashed password
        return hashed_password

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verifies a password against a hash

        Args:
            plain_password (str): plain_password
            hashed_password (str): hashed_password

        Returns:
            bool: True if password matches hash, False otherwise
        """
        # Call self._password_manager.verify_password with plain_password and hashed_password
        is_valid = self._password_manager.verify_password(plain_password, hashed_password)
        # Return the verification result
        return is_valid

    def validate_password_strength(self, password: str) -> bool:
        """Validates password strength against security requirements

        Args:
            password (str): password

        Returns:
            bool: True if password meets strength requirements, False otherwise
        """
        # Call self._password_manager.validate_strength with password
        is_strong = self._password_manager.validate_strength(password)
        # Return the validation result
        return is_strong

    def create_auth_tokens(self, user_data: Dict[str, Any]) -> Dict[str, str]:
        """Creates authentication tokens for a user

        Args:
            user_data (Dict[str, Any]): user_data

        Returns:
            Dict[str, str]: Dictionary containing access_token and refresh_token
        """
        # Call self._jwt_handler.create_access_token for access token
        access_token = self._jwt_handler.create_access_token(user_data)
        # Call self._jwt_handler.create_refresh_token for refresh token
        refresh_token = self._jwt_handler.create_refresh_token(user_data)
        # Return dictionary with both tokens
        return {
            "access_token": access_token,
            "refresh_token": refresh_token
        }

    def validate_auth_token(self, token: str) -> Dict[str, Any]:
        """Validates an authentication token

        Args:
            token (str): token

        Returns:
            Dict[str, Any]: Decoded token payload if valid
        """
        # Call self._jwt_handler.validate_access_token with token
        try:
            payload = self._jwt_handler.validate_access_token(token)
            # Return the decoded payload if valid
            return payload
        except AuthenticationException as e:
            # Catch and log any authentication exceptions
            logger.error(f"Authentication failed: {str(e)}")
            raise

    def get_security_headers(self) -> Dict[str, str]:
        """Gets security headers for HTTP responses

        Returns:
            Dict[str, str]: Dictionary of security headers
        """
        # Create dictionary with standard security headers
        headers = {
            "Content-Security-Policy": "default-src 'self'",
            "X-XSS-Protection": "1; mode=block",
            "X-Frame-Options": "DENY",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()"
        }
        # Return the headers dictionary
        return headers

    def get_captcha_site_key(self) -> str:
        """Gets the reCAPTCHA site key for frontend use

        Returns:
            str: reCAPTCHA site key
        """
        # Return self._captcha_verifier.get_site_key()
        return self._captcha_verifier.get_site_key()