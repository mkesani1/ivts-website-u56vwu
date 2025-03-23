"""
Core security module for the IndiVillage backend application.

This module provides fundamental security functionality including password hashing,
JWT token generation and validation, secure random token creation, and other
essential security utilities that serve as the foundation for the application's
security infrastructure.
"""

from datetime import datetime, timedelta
from typing import Dict, Optional, Any, Union

import secrets
from jose import jwt, JWTError  # python-jose ^3.3.0
from passlib.context import CryptContext  # passlib ^1.7.4

from .config import settings
from .exceptions import AuthenticationException, SecurityException
from .logging import logger

# Initialize password hashing context with Argon2 (recommended by OWASP)
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain password against a hashed password.
    
    Args:
        plain_password: The plain text password to verify
        hashed_password: The hashed password to compare against
        
    Returns:
        bool: True if the password matches the hash, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Generates a secure hash of a password using Argon2id.
    
    Args:
        password: The plain text password to hash
        
    Returns:
        str: The hashed password
    """
    return pwd_context.hash(password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[int] = None) -> str:
    """
    Creates a JWT access token with specified data and expiration.
    
    Args:
        data: The data to encode in the token
        expires_delta: Optional custom expiration time in minutes
        
    Returns:
        str: Encoded JWT token
    """
    to_encode = data.copy()
    expire = get_token_expiration(expires_delta)
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Dict[str, Any]:
    """
    Decodes and validates a JWT access token.
    
    Args:
        token: The JWT token to decode
        
    Returns:
        Dict[str, Any]: Decoded token payload
        
    Raises:
        AuthenticationException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError as e:
        logger.error(f"Failed to validate token: {str(e)}")
        raise AuthenticationException("Could not validate credentials")


def is_token_expired(token_data: Dict[str, Any]) -> bool:
    """
    Checks if a JWT token has expired.
    
    Args:
        token_data: The decoded token data
        
    Returns:
        bool: True if token is expired, False otherwise
    """
    expiration = token_data.get("exp")
    if expiration is None:
        return True
    
    current_time = datetime.utcnow().timestamp()
    return current_time > expiration


def get_token_expiration(expires_delta: Optional[int] = None) -> datetime:
    """
    Calculates token expiration time based on current time and delta.
    
    Args:
        expires_delta: Optional custom expiration time in minutes
        
    Returns:
        datetime: Expiration datetime
    """
    if expires_delta:
        expire = datetime.utcnow() + timedelta(minutes=expires_delta)
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return expire


def generate_secure_token(length: int = 32) -> str:
    """
    Generates a cryptographically secure random token.
    
    Args:
        length: The desired length of the token (default: 32)
        
    Returns:
        str: Secure random token
    """
    token = secrets.token_urlsafe(length)
    # Ensure the length is correct (token_urlsafe can generate longer tokens)
    return token[:length]


def validate_password_strength(password: str) -> bool:
    """
    Validates password strength against security requirements.
    
    Requirements:
    - At least 12 characters
    - Contains at least one uppercase letter
    - Contains at least one lowercase letter
    - Contains at least one digit
    - Contains at least one special character
    
    Args:
        password: The password to validate
        
    Returns:
        bool: True if password meets strength requirements, False otherwise
    """
    if len(password) < 12:
        return False
    
    # Check for uppercase letters
    if not any(char.isupper() for char in password):
        return False
    
    # Check for lowercase letters
    if not any(char.islower() for char in password):
        return False
    
    # Check for digits
    if not any(char.isdigit() for char in password):
        return False
    
    # Check for special characters
    special_chars = "!@#$%^&*()-_=+[]{}|;:,.<>?/~"
    if not any(char in special_chars for char in password):
        return False
    
    return True


def sanitize_auth_log(auth_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitizes authentication data for logging to prevent sensitive data exposure.
    
    Args:
        auth_data: The authentication data to sanitize
        
    Returns:
        Dict[str, Any]: Sanitized authentication data safe for logging
    """
    sanitized = auth_data.copy()
    
    # List of sensitive fields to mask
    sensitive_fields = ["password", "token", "refresh_token", "secret", "api_key"]
    
    for field in sensitive_fields:
        if field in sanitized:
            sanitized[field] = "********"
    
    return sanitized


class PasswordManager:
    """
    Manages password operations including hashing, verification, and strength validation.
    """
    
    def __init__(self):
        """
        Initializes the PasswordManager with configured hashing context.
        """
        # Using the global pwd_context initialized with Argon2id
        pass
    
    def hash_password(self, password: str) -> str:
        """
        Hashes a password using the configured algorithm.
        
        Args:
            password: The plain text password to hash
            
        Returns:
            str: The hashed password
        """
        return get_password_hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verifies a password against a hash.
        
        Args:
            plain_password: The plain text password to verify
            hashed_password: The hashed password to compare against
            
        Returns:
            bool: True if password matches hash, False otherwise
        """
        return verify_password(plain_password, hashed_password)
    
    def validate_strength(self, password: str) -> bool:
        """
        Validates password strength.
        
        Args:
            password: The password to validate
            
        Returns:
            bool: True if password meets strength requirements, False otherwise
        """
        return validate_password_strength(password)
    
    def needs_rehash(self, hashed_password: str) -> bool:
        """
        Checks if a password hash needs to be upgraded.
        
        Args:
            hashed_password: The hashed password to check
            
        Returns:
            bool: True if hash needs upgrading, False otherwise
        """
        return pwd_context.needs_update(hashed_password)


class TokenManager:
    """
    Manages JWT token operations including creation, validation, and expiration.
    """
    
    def __init__(self):
        """
        Initializes the TokenManager.
        """
        # Using settings from configuration
        pass
    
    def create_token(self, data: Dict[str, Any], expires_delta: Optional[int] = None) -> str:
        """
        Creates a JWT token with the specified data and expiration.
        
        Args:
            data: The data to encode in the token
            expires_delta: Optional custom expiration time in minutes
            
        Returns:
            str: Encoded JWT token
        """
        return create_access_token(data, expires_delta)
    
    def decode_token(self, token: str) -> Dict[str, Any]:
        """
        Decodes and validates a JWT token.
        
        Args:
            token: The JWT token to decode
            
        Returns:
            Dict[str, Any]: Decoded token payload
        """
        return decode_access_token(token)
    
    def is_expired(self, token_data: Dict[str, Any]) -> bool:
        """
        Checks if a token has expired.
        
        Args:
            token_data: The decoded token data
            
        Returns:
            bool: True if token is expired, False otherwise
        """
        return is_token_expired(token_data)
    
    def get_expiration(self, expires_delta: Optional[int] = None) -> datetime:
        """
        Calculates token expiration time.
        
        Args:
            expires_delta: Optional custom expiration time in minutes
            
        Returns:
            datetime: Expiration datetime
        """
        return get_token_expiration(expires_delta)
    
    def refresh_token(self, token: str, expires_delta: Optional[int] = None) -> str:
        """
        Creates a new token based on an existing token's data.
        
        Args:
            token: The existing token to refresh
            expires_delta: Optional custom expiration time in minutes
            
        Returns:
            str: New JWT token
        """
        # Decode the existing token
        payload = self.decode_token(token)
        
        # Remove the expiration claim if it exists
        if "exp" in payload:
            del payload["exp"]
        
        # Create a new token with the updated payload
        return self.create_token(payload, expires_delta)