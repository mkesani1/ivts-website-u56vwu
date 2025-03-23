"""
CAPTCHA verification module for the IndiVillage backend application.

This module provides utilities for integrating with Google's reCAPTCHA service
to protect forms and API endpoints from spam and automated attacks.
"""

import json
import functools
from typing import Dict, Any, Callable, Optional

import requests  # version: 2.31.0
from fastapi import Request  # version: 0.95.0
from starlette.requests import Request as StarletteRequest  # version: 0.26.1

from ..core.config import settings
from ..core.exceptions import SecurityException
from ..core.logging import get_logger
from ..utils.logging_utils import log_function_call

# Initialize logger
logger = get_logger(__name__)

# Constants
RECAPTCHA_VERIFY_URL = "https://www.google.com/recaptcha/api/siteverify"
CAPTCHA_SCORE_THRESHOLD = 0.5


@log_function_call
def verify_captcha(token: str, remote_ip: str) -> Dict[str, Any]:
    """
    Verifies a reCAPTCHA token with Google's reCAPTCHA API.
    
    Args:
        token: The reCAPTCHA token to verify
        remote_ip: IP address of the client for verification
        
    Returns:
        Dict containing verification result with success status and score
        
    Raises:
        SecurityException: If no token is provided
    """
    if not token:
        logger.warning("CAPTCHA verification failed: No token provided")
        raise SecurityException("CAPTCHA verification failed", details={"reason": "No token provided"})
    
    # Prepare request payload
    payload = {
        "secret": settings.RECAPTCHA_SECRET_KEY,
        "response": token,
        "remoteip": remote_ip
    }
    
    try:
        # Send verification request to Google
        response = requests.post(RECAPTCHA_VERIFY_URL, data=payload)
        result = response.json()
        
        # Log verification result
        if result.get("success", False):
            logger.info(
                "CAPTCHA verification successful",
                extra={"score": result.get("score"), "remote_ip": remote_ip}
            )
        else:
            logger.warning(
                "CAPTCHA verification failed",
                extra={"error_codes": result.get("error-codes", []), "remote_ip": remote_ip}
            )
        
        return result
    except Exception as e:
        logger.error(f"CAPTCHA verification error: {str(e)}", exc_info=True)
        # Return a failed verification result
        return {"success": False, "error": str(e)}


@log_function_call
def validate_captcha_token(token: str, remote_ip: str, threshold: float = CAPTCHA_SCORE_THRESHOLD) -> bool:
    """
    Validates a reCAPTCHA token and checks if the score meets the threshold.
    
    Args:
        token: The reCAPTCHA token to validate
        remote_ip: IP address of the client for verification
        threshold: Score threshold for validation (0.0 to 1.0)
        
    Returns:
        True if token is valid and score meets threshold, False otherwise
    """
    # Get verification result
    result = verify_captcha(token, remote_ip)
    
    # Check if verification was successful
    if not result.get("success", False):
        logger.warning("CAPTCHA validation failed: Verification unsuccessful")
        return False
    
    # For reCAPTCHA v3, check the score against threshold
    score = result.get("score", 0)
    if score < threshold:
        logger.warning(
            "CAPTCHA validation failed: Score below threshold",
            extra={"score": score, "threshold": threshold, "remote_ip": remote_ip}
        )
        return False
    
    logger.info(
        "CAPTCHA validation successful",
        extra={"score": score, "threshold": threshold, "remote_ip": remote_ip}
    )
    return True


def require_captcha(threshold: float = CAPTCHA_SCORE_THRESHOLD):
    """
    Decorator for FastAPI endpoints that require CAPTCHA verification.
    
    Args:
        threshold: Score threshold for validation (0.0 to 1.0)
        
    Returns:
        Decorator function for FastAPI endpoints
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Find the request object in args
            request = None
            for arg in args:
                if isinstance(arg, (Request, StarletteRequest)):
                    request = arg
                    break
            
            if not request:
                logger.error("CAPTCHA verification failed: No request object found")
                raise SecurityException("CAPTCHA verification failed", details={"reason": "Internal server error"})
            
            # Get client IP address
            client_host = request.client.host if hasattr(request, 'client') and request.client else "unknown"
            
            # Try to get the token from various possible locations
            captcha_token = None
            
            # Check if request has JSON body
            if request.method != "GET":
                try:
                    body = await request.json()
                    captcha_token = body.get("captcha_token", body.get("g-recaptcha-response"))
                except Exception:
                    # If request has form data
                    try:
                        form = await request.form()
                        captcha_token = form.get("captcha_token", form.get("g-recaptcha-response"))
                    except Exception:
                        pass
            
            # If not found in body or form, check query parameters
            if not captcha_token:
                captcha_token = request.query_params.get("captcha_token", request.query_params.get("g-recaptcha-response"))
            
            # If still not found, check headers
            if not captcha_token:
                captcha_token = request.headers.get("X-Captcha-Token")
            
            # Validate the CAPTCHA token
            if not captcha_token or not validate_captcha_token(captcha_token, client_host, threshold):
                logger.warning(
                    "CAPTCHA verification failed for API endpoint",
                    extra={"endpoint": request.url.path, "method": request.method, "remote_ip": client_host}
                )
                raise SecurityException("CAPTCHA verification failed", details={"reason": "Invalid or missing CAPTCHA"})
            
            # If validation passed, call the original function
            logger.info(
                "CAPTCHA verification successful for API endpoint",
                extra={"endpoint": request.url.path, "method": request.method, "remote_ip": client_host}
            )
            return await func(*args, **kwargs)
        
        return wrapper
    
    return decorator


class CaptchaVerifier:
    """
    Class for handling reCAPTCHA verification.
    
    This class provides methods for verifying reCAPTCHA tokens and validating
    them against configurable thresholds.
    """
    
    def __init__(
        self,
        secret_key: str = None,
        site_key: str = None,
        verify_url: str = None,
        score_threshold: float = None
    ):
        """
        Initializes the CaptchaVerifier with configuration settings.
        
        Args:
            secret_key: reCAPTCHA secret key (defaults to settings.RECAPTCHA_SECRET_KEY)
            site_key: reCAPTCHA site key for frontend use (defaults to settings.RECAPTCHA_SITE_KEY)
            verify_url: reCAPTCHA verification URL (defaults to RECAPTCHA_VERIFY_URL)
            score_threshold: Default score threshold (defaults to CAPTCHA_SCORE_THRESHOLD)
        """
        self._secret_key = secret_key or settings.RECAPTCHA_SECRET_KEY
        self._site_key = site_key or settings.RECAPTCHA_SITE_KEY
        self._verify_url = verify_url or RECAPTCHA_VERIFY_URL
        self._score_threshold = score_threshold or CAPTCHA_SCORE_THRESHOLD
    
    @log_function_call
    def verify(self, token: str, remote_ip: str) -> Dict[str, Any]:
        """
        Verifies a reCAPTCHA token.
        
        Args:
            token: The reCAPTCHA token to verify
            remote_ip: IP address of the client for verification
            
        Returns:
            Dict containing verification result with success status and score
            
        Raises:
            SecurityException: If no token is provided
        """
        if not token:
            logger.warning("CAPTCHA verification failed: No token provided")
            raise SecurityException("CAPTCHA verification failed", details={"reason": "No token provided"})
        
        # Prepare request payload
        payload = {
            "secret": self._secret_key,
            "response": token,
            "remoteip": remote_ip
        }
        
        try:
            # Send verification request to Google
            response = requests.post(self._verify_url, data=payload)
            result = response.json()
            
            # Log verification result
            if result.get("success", False):
                logger.info(
                    "CAPTCHA verification successful",
                    extra={"score": result.get("score"), "remote_ip": remote_ip}
                )
            else:
                logger.warning(
                    "CAPTCHA verification failed",
                    extra={"error_codes": result.get("error-codes", []), "remote_ip": remote_ip}
                )
            
            return result
        except Exception as e:
            logger.error(f"CAPTCHA verification error: {str(e)}", exc_info=True)
            # Return a failed verification result
            return {"success": False, "error": str(e)}
    
    @log_function_call
    def validate(self, token: str, remote_ip: str, threshold: float = None) -> bool:
        """
        Validates a reCAPTCHA token and checks if the score meets the threshold.
        
        Args:
            token: The reCAPTCHA token to validate
            remote_ip: IP address of the client for verification
            threshold: Score threshold for validation (0.0 to 1.0),
                       defaults to self._score_threshold
            
        Returns:
            True if token is valid and score meets threshold, False otherwise
        """
        # Use provided threshold or default to instance threshold
        threshold = threshold if threshold is not None else self._score_threshold
        
        # Get verification result
        result = self.verify(token, remote_ip)
        
        # Check if verification was successful
        if not result.get("success", False):
            logger.warning("CAPTCHA validation failed: Verification unsuccessful")
            return False
        
        # For reCAPTCHA v3, check the score against threshold
        score = result.get("score", 0)
        if score < threshold:
            logger.warning(
                "CAPTCHA validation failed: Score below threshold",
                extra={"score": score, "threshold": threshold, "remote_ip": remote_ip}
            )
            return False
        
        logger.info(
            "CAPTCHA validation successful",
            extra={"score": score, "threshold": threshold, "remote_ip": remote_ip}
        )
        return True
    
    def get_site_key(self) -> str:
        """
        Returns the reCAPTCHA site key for frontend use.
        
        Returns:
            The reCAPTCHA site key
        """
        return self._site_key