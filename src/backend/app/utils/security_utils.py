"""
Security utilities module for the IndiVillage backend application.

This module provides various security-related utility functions and classes including:
- Secure token generation
- Data encryption and decryption
- Secure hash generation and verification
- HMAC generation and verification
- Secure filename generation
- Sensitive data masking
- Password security validation
- And more security-related utilities
"""

import os
import base64
import hashlib
import hmac
import secrets
import typing
import json
import uuid
import time
from typing import Dict, List, Optional, Tuple, Any, Union

from cryptography.fernet import Fernet  # cryptography v39.0.0

from app.core.config import settings
from app.core.exceptions import SecurityException
from app.core.logging import logger

# Constants
ENCODING = "utf-8"
TOKEN_BYTES_LENGTH = 32
HASH_ALGORITHM = "sha256"


def generate_secure_token(length: int = TOKEN_BYTES_LENGTH) -> str:
    """
    Generates a cryptographically secure random token.
    
    Args:
        length: Length of the token in bytes (default: 32)
        
    Returns:
        Secure random token string as URL-safe base64
    """
    # Generate random bytes
    token_bytes = secrets.token_bytes(length)
    
    # Encode to URL-safe base64 string
    token_string = base64.urlsafe_b64encode(token_bytes).decode(ENCODING)
    
    # Remove padding characters
    token_string = token_string.rstrip('=')
    
    logger.debug(f"Generated secure token of length {length}")
    return token_string


def encrypt_data(data: str) -> str:
    """
    Encrypts sensitive data using Fernet symmetric encryption.
    
    Args:
        data: The data to encrypt
        
    Returns:
        Encrypted data as a base64 string
    """
    try:
        # Ensure data is in bytes
        if isinstance(data, str):
            data_bytes = data.encode(ENCODING)
        else:
            data_bytes = data
        
        # Get encryption key with fallback to SECRET_KEY if ENCRYPTION_KEY not available
        encryption_key = getattr(settings, "ENCRYPTION_KEY", None)
        if not encryption_key:
            # Derive a key from SECRET_KEY
            key_bytes = settings.SECRET_KEY.encode(ENCODING)
            hashed_key = hashlib.sha256(key_bytes).digest()
            encryption_key = base64.urlsafe_b64encode(hashed_key)
        elif isinstance(encryption_key, str):
            encryption_key = encryption_key.encode(ENCODING)
        
        # Initialize Fernet cipher with encryption key
        cipher = Fernet(encryption_key)
        
        # Encrypt the data
        encrypted_bytes = cipher.encrypt(data_bytes)
        
        # Return as base64 string
        return encrypted_bytes.decode(ENCODING)
    except Exception as e:
        logger.error(f"Encryption error: {str(e)}")
        raise SecurityException(f"Failed to encrypt data: {str(e)}")


def decrypt_data(encrypted_data: str) -> str:
    """
    Decrypts data that was encrypted with encrypt_data.
    
    Args:
        encrypted_data: The encrypted data to decrypt
        
    Returns:
        Decrypted data as a string
    """
    try:
        # Ensure encrypted_data is in bytes
        if isinstance(encrypted_data, str):
            encrypted_bytes = encrypted_data.encode(ENCODING)
        else:
            encrypted_bytes = encrypted_data
        
        # Get encryption key with fallback to SECRET_KEY if ENCRYPTION_KEY not available
        encryption_key = getattr(settings, "ENCRYPTION_KEY", None)
        if not encryption_key:
            # Derive a key from SECRET_KEY
            key_bytes = settings.SECRET_KEY.encode(ENCODING)
            hashed_key = hashlib.sha256(key_bytes).digest()
            encryption_key = base64.urlsafe_b64encode(hashed_key)
        elif isinstance(encryption_key, str):
            encryption_key = encryption_key.encode(ENCODING)
        
        # Initialize Fernet cipher with encryption key
        cipher = Fernet(encryption_key)
        
        # Decrypt the data
        decrypted_bytes = cipher.decrypt(encrypted_bytes)
        
        # Convert to string
        return decrypted_bytes.decode(ENCODING)
    except Exception as e:
        logger.error(f"Decryption error: {str(e)}")
        raise SecurityException(f"Failed to decrypt data: {str(e)}")


def hash_data(data: str, salt: str = "") -> str:
    """
    Creates a secure hash of the provided data.
    
    Args:
        data: The data to hash
        salt: Optional salt to add to the data before hashing
        
    Returns:
        Hexadecimal digest of the hashed data
    """
    # Ensure data is in bytes
    if isinstance(data, str):
        data_bytes = data.encode(ENCODING)
    else:
        data_bytes = data
    
    # If salt is provided, combine with data
    if salt:
        salt_bytes = salt.encode(ENCODING) if isinstance(salt, str) else salt
        data_bytes = salt_bytes + data_bytes
    
    # Get the hash algorithm with fallback
    algorithm = getattr(settings, "SECURITY_ALGORITHM", HASH_ALGORITHM)
    
    # Create hash
    hash_obj = hashlib.new(algorithm)
    hash_obj.update(data_bytes)
    
    # Return hexadecimal digest
    return hash_obj.hexdigest()


def verify_hash(data: str, hash_value: str, salt: str = "") -> bool:
    """
    Verifies if data matches a previously generated hash.
    
    Args:
        data: The data to verify
        hash_value: The hash value to check against
        salt: Optional salt used in the original hash
        
    Returns:
        True if hash matches data, False otherwise
    """
    # Generate hash of the data using the same salt
    generated_hash = hash_data(data, salt)
    
    # Compare hashes
    return generated_hash == hash_value


def generate_hmac(data: str, key: str = None) -> str:
    """
    Generates an HMAC for data integrity verification.
    
    Args:
        data: The data to generate HMAC for
        key: The key to use for HMAC (uses SECRET_KEY if not provided)
        
    Returns:
        Hexadecimal digest of the HMAC
    """
    # Ensure data is in bytes
    if isinstance(data, str):
        data_bytes = data.encode(ENCODING)
    else:
        data_bytes = data
    
    # Use provided key or default to SECRET_KEY
    key_bytes = (key or settings.SECRET_KEY).encode(ENCODING)
    
    # Get the hash algorithm with fallback
    algorithm = getattr(settings, "SECURITY_ALGORITHM", HASH_ALGORITHM)
    
    # Create HMAC
    hmac_obj = hmac.new(key_bytes, data_bytes, algorithm)
    
    # Return hexadecimal digest
    return hmac_obj.hexdigest()


def verify_hmac(data: str, hmac_value: str, key: str = None) -> bool:
    """
    Verifies if data matches a previously generated HMAC.
    
    Args:
        data: The data to verify
        hmac_value: The HMAC value to check against
        key: The key used in the original HMAC (uses SECRET_KEY if not provided)
        
    Returns:
        True if HMAC matches data, False otherwise
    """
    # Generate HMAC of the data using the same key
    generated_hmac = generate_hmac(data, key)
    
    # Use constant-time comparison to prevent timing attacks
    return hmac.compare_digest(generated_hmac, hmac_value)


def generate_secure_filename(original_filename: str) -> str:
    """
    Generates a secure filename for uploaded files.
    
    Args:
        original_filename: The original filename
        
    Returns:
        Secure filename with original extension
    """
    # Extract file extension from original filename
    _, extension = os.path.splitext(original_filename)
    
    # Generate a random UUID for the filename
    secure_name = str(uuid.uuid4())
    
    # Combine UUID with original extension
    secure_filename = f"{secure_name}{extension}"
    
    logger.debug(f"Generated secure filename: {secure_filename}")
    return secure_filename


def mask_sensitive_data(data: str, mask_char: str = "*", visible_chars: int = 4) -> str:
    """
    Masks sensitive data for logging and display purposes.
    
    Args:
        data: The sensitive data to mask
        mask_char: Character to use for masking
        visible_chars: Number of characters to leave visible at each end
        
    Returns:
        Masked string with only some characters visible
    """
    if not data:
        return ""
    
    # Ensure visible_chars is reasonable
    visible_chars = min(visible_chars, len(data) // 2)
    
    if len(data) <= visible_chars * 2:
        # If data is too short, mask all but the first and last characters
        return data[0] + mask_char * (len(data) - 2) + data[-1]
    
    # Mask the middle portion of the string
    prefix = data[:visible_chars]
    suffix = data[-visible_chars:]
    masked_length = len(data) - (visible_chars * 2)
    
    return prefix + (mask_char * masked_length) + suffix


def sanitize_security_log(log_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitizes sensitive data in logs to prevent data exposure.
    
    Args:
        log_data: The log data to sanitize
        
    Returns:
        Sanitized log data safe for logging
    """
    # Create a copy of the log_data to avoid modifying the original
    sanitized_data = log_data.copy()
    
    # List of sensitive field names (case-insensitive)
    sensitive_fields = [
        "password", "token", "key", "secret", "credential", "auth",
        "apikey", "api_key", "authorization", "cookie", "session"
    ]
    
    # Iterate through the log data and mask sensitive fields
    for key in sanitized_data:
        key_lower = key.lower()
        
        # Check if the key contains any sensitive field names
        is_sensitive = any(field in key_lower for field in sensitive_fields)
        
        if is_sensitive and sanitized_data[key]:
            if isinstance(sanitized_data[key], str):
                sanitized_data[key] = mask_sensitive_data(sanitized_data[key])
            elif isinstance(sanitized_data[key], dict):
                sanitized_data[key] = sanitize_security_log(sanitized_data[key])
            else:
                sanitized_data[key] = "[REDACTED]"
    
    return sanitized_data


def is_secure_password(password: str) -> Tuple[bool, str]:
    """
    Checks if a password meets security requirements.
    
    Args:
        password: The password to check
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check password length
    if len(password) < 12:
        return False, "Password must be at least 12 characters long"
    
    # Check for uppercase letters
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    
    # Check for lowercase letters
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"
    
    # Check for digits
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one digit"
    
    # Check for special characters
    special_chars = "!@#$%^&*()-_=+[]{}|;:'\",.<>/?"
    if not any(c in special_chars for c in password):
        return False, "Password must contain at least one special character"
    
    return True, ""


def generate_key() -> str:
    """
    Generates a cryptographic key for encryption.
    
    Returns:
        Base64-encoded key suitable for Fernet encryption
    """
    # Generate a Fernet key
    key = Fernet.generate_key()
    
    # Return as string
    key_str = key.decode(ENCODING)
    
    logger.info("Generated new encryption key")
    return key_str


class DataEncryptor:
    """
    Class for encrypting and decrypting sensitive data.
    """
    
    def __init__(self, encryption_key: str = None):
        """
        Initializes the DataEncryptor with encryption key.
        
        Args:
            encryption_key: Key to use for encryption (uses ENCRYPTION_KEY from settings if not provided)
        """
        # Use provided key or get from settings with fallback
        if encryption_key:
            if isinstance(encryption_key, str):
                key = encryption_key.encode(ENCODING)
            else:
                key = encryption_key
        else:
            key = getattr(settings, "ENCRYPTION_KEY", None)
            if not key:
                # Derive a key from SECRET_KEY
                key_bytes = settings.SECRET_KEY.encode(ENCODING)
                hashed_key = hashlib.sha256(key_bytes).digest()
                key = base64.urlsafe_b64encode(hashed_key)
            elif isinstance(key, str):
                key = key.encode(ENCODING)
        
        # Initialize Fernet cipher
        self._cipher = Fernet(key)
        
        logger.debug("DataEncryptor initialized")
    
    def encrypt(self, data: str) -> str:
        """
        Encrypts data using Fernet symmetric encryption.
        
        Args:
            data: The data to encrypt
            
        Returns:
            Encrypted data as a base64 string
        """
        try:
            # Ensure data is in bytes
            if isinstance(data, str):
                data_bytes = data.encode(ENCODING)
            else:
                data_bytes = data
            
            # Encrypt the data
            encrypted_bytes = self._cipher.encrypt(data_bytes)
            
            # Return as string
            return encrypted_bytes.decode(ENCODING)
        except Exception as e:
            logger.error(f"Encryption error: {str(e)}")
            raise SecurityException(f"Failed to encrypt data: {str(e)}")
    
    def decrypt(self, encrypted_data: str) -> str:
        """
        Decrypts data that was encrypted with encrypt.
        
        Args:
            encrypted_data: The encrypted data to decrypt
            
        Returns:
            Decrypted data as a string
        """
        try:
            # Ensure encrypted_data is in bytes
            if isinstance(encrypted_data, str):
                encrypted_bytes = encrypted_data.encode(ENCODING)
            else:
                encrypted_bytes = encrypted_data
            
            # Decrypt the data
            decrypted_bytes = self._cipher.decrypt(encrypted_bytes)
            
            # Return as string
            return decrypted_bytes.decode(ENCODING)
        except Exception as e:
            logger.error(f"Decryption error: {str(e)}")
            raise SecurityException(f"Failed to decrypt data: {str(e)}")
    
    def rotate_key(self, encrypted_data: str, new_key: str, update_instance: bool = False) -> str:
        """
        Rotates the encryption key and re-encrypts data.
        
        Args:
            encrypted_data: The data encrypted with the old key
            new_key: The new encryption key
            update_instance: Whether to update this instance with the new key
            
        Returns:
            Data re-encrypted with the new key
        """
        try:
            # First decrypt with the current key
            decrypted_data = self.decrypt(encrypted_data)
            
            # Create a new cipher with the new key
            if isinstance(new_key, str):
                new_key_bytes = new_key.encode(ENCODING)
            else:
                new_key_bytes = new_key
                
            new_cipher = Fernet(new_key_bytes)
            
            # Encrypt the data with the new key
            new_encrypted_bytes = new_cipher.encrypt(decrypted_data.encode(ENCODING))
            new_encrypted_str = new_encrypted_bytes.decode(ENCODING)
            
            # Optionally update this instance's cipher
            if update_instance:
                self._cipher = new_cipher
                logger.info("Encryption key rotated and instance updated")
            else:
                logger.info("Encryption key rotated for data")
            
            return new_encrypted_str
        except Exception as e:
            logger.error(f"Key rotation error: {str(e)}")
            raise SecurityException(f"Failed to rotate encryption key: {str(e)}")


class TokenManager:
    """
    Class for managing secure tokens with expiration.
    """
    
    def __init__(self):
        """
        Initializes the TokenManager.
        """
        logger.debug("TokenManager initialized")
    
    def generate_token(self, payload: Dict[str, Any], expires_in_seconds: int = None) -> str:
        """
        Generates a secure token with optional expiration.
        
        Args:
            payload: The data to include in the token
            expires_in_seconds: Token expiration time in seconds
            
        Returns:
            Secure token string
        """
        try:
            # Create a copy of the payload
            token_payload = payload.copy()
            
            # Add expiration timestamp if specified
            if expires_in_seconds is not None:
                expiration_time = int(time.time()) + expires_in_seconds
                token_payload["exp"] = expiration_time
            
            # Add token ID
            token_payload["jti"] = str(uuid.uuid4())
            
            # Serialize to JSON
            token_data = json.dumps(token_payload)
            
            # Encrypt the token data
            encrypted_token = encrypt_data(token_data)
            
            logger.debug(f"Generated token with payload: {sanitize_security_log(token_payload)}")
            return encrypted_token
        except Exception as e:
            logger.error(f"Token generation error: {str(e)}")
            raise SecurityException(f"Failed to generate token: {str(e)}")
    
    def validate_token(self, token: str) -> Dict[str, Any]:
        """
        Validates a token and returns its payload.
        
        Args:
            token: The token to validate
            
        Returns:
            Token payload if valid
            
        Raises:
            SecurityException: If token is invalid or expired
        """
        try:
            # Decrypt the token
            decrypted_token = decrypt_data(token)
            
            # Parse the JSON payload
            payload = json.loads(decrypted_token)
            
            # Check expiration
            if "exp" in payload:
                current_time = int(time.time())
                if payload["exp"] < current_time:
                    logger.warning(f"Token expired: {payload.get('jti', 'unknown')}")
                    raise SecurityException("Token has expired")
            
            logger.debug(f"Token validated: {payload.get('jti', 'unknown')}")
            return payload
        except json.JSONDecodeError:
            logger.error("Token validation failed: Invalid token format")
            raise SecurityException("Invalid token format")
        except Exception as e:
            logger.error(f"Token validation error: {str(e)}")
            raise SecurityException(f"Invalid token: {str(e)}")
    
    def refresh_token(self, token: str, expires_in_seconds: int) -> str:
        """
        Refreshes a token with a new expiration time.
        
        Args:
            token: The token to refresh
            expires_in_seconds: New expiration time in seconds
            
        Returns:
            New token with updated expiration
        """
        try:
            # Validate the existing token
            payload = self.validate_token(token)
            
            # Remove existing expiration
            if "exp" in payload:
                del payload["exp"]
            
            # Generate a new token with updated expiration
            new_token = self.generate_token(payload, expires_in_seconds)
            
            logger.debug(f"Token refreshed: {payload.get('jti', 'unknown')}")
            return new_token
        except Exception as e:
            logger.error(f"Token refresh error: {str(e)}")
            raise SecurityException(f"Failed to refresh token: {str(e)}")