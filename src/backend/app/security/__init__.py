"""
Initialization module for the security package that exports key security components for use throughout the IndiVillage backend application. This module centralizes security-related functionality including input validation, CAPTCHA verification, file scanning, rate limiting, and JWT authentication.
"""

from .input_validation import (
    validate_form_data,  # Import form validation function
    validate_contact_form,  # Import contact form validation function
    validate_demo_request_form,  # Import demo request form validation function
    validate_quote_request_form,  # Import quote request form validation function
    validate_upload_request,  # Import upload request validation function
    validate_file_metadata,  # Import file metadata validation function
    validate_file_content,  # Import file content validation function
    RequestValidator,  # Import request validation class
    InputSanitizer,  # Import input sanitization class
)
from .captcha import (
    verify_captcha,  # Import CAPTCHA verification function
    validate_captcha_token,  # Import CAPTCHA token validation function
    require_captcha,  # Import CAPTCHA requirement decorator
    CaptchaVerifier,  # Import CAPTCHA verification class
)
from .file_scanner import (
    FileScanner,  # Import file scanning class
    scan_file,  # Import file scanning function
    quarantine_file,  # Import file quarantine function
    is_high_risk_file,  # Import high risk file check function
    SCAN_RESULT_CLEAN,  # Import clean scan result constant
    SCAN_RESULT_INFECTED,  # Import infected scan result constant
    SCAN_RESULT_ERROR,  # Import error scan result constant
)
from .rate_limiting import (
    RateLimiter,  # Import rate limiting class
    RateLimitExceeded,  # Import rate limit exceeded exception
    get_client_ip,  # Import client IP extraction function
)
from .jwt import (
    get_current_user,  # Import current user extraction function
    get_current_active_user,  # Import active user verification function
    get_current_admin_user,  # Import admin user verification function
    create_user_token,  # Import user token creation function
    JWTBearer,  # Import JWT bearer authentication class
    JWTAuthMiddleware,  # Import JWT authentication middleware
)

__all__ = [
    "validate_form_data",
    "validate_contact_form",
    "validate_demo_request_form",
    "validate_quote_request_form",
    "validate_upload_request",
    "validate_file_metadata",
    "validate_file_content",
    "RequestValidator",
    "InputSanitizer",
    "verify_captcha",
    "validate_captcha_token",
    "require_captcha",
    "CaptchaVerifier",
    "FileScanner",
    "scan_file",
    "quarantine_file",
    "is_high_risk_file",
    "SCAN_RESULT_CLEAN",
    "SCAN_RESULT_INFECTED",
    "SCAN_RESULT_ERROR",
    "RateLimiter",
    "RateLimitExceeded",
    "get_client_ip",
    "get_current_user",
    "get_current_active_user",
    "get_current_admin_user",
    "create_user_token",
    "JWTBearer",
    "JWTAuthMiddleware",
]