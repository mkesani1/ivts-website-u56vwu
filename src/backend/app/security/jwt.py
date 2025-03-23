"""
JWT (JSON Web Token) implementation for the IndiVillage backend application.

This module provides functionality for creating, validating, and refreshing JWT
tokens used for authentication and authorization. It implements secure token
handling with proper expiration, payload validation, and error handling.
"""

from datetime import datetime, timedelta
from typing import Dict, Optional, Any, Union
import uuid

from jose import jwt, JWTError  # python-jose ^3.3.0

from app.core.config import settings
from app.core.exceptions import AuthenticationException, SecurityException
from app.core.logging import logger
from app.api.v1.models.user import User

# Constants for token types
TOKEN_TYPE_ACCESS = "access"
TOKEN_TYPE_REFRESH = "refresh"

# Algorithm used for token signing (from settings)
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES


def create_jwt_token(
    data: Dict[str, Any], expires_delta: Optional[int] = None, token_type: str = TOKEN_TYPE_ACCESS
) -> str:
    """
    Creates a JWT token with the specified data and expiration.
    
    Args:
        data: Dictionary containing the data to encode in the token
        expires_delta: Optional expiration time in minutes (overrides default)
        token_type: Type of token (access or refresh)
        
    Returns:
        Encoded JWT token as a string
    """
    to_encode = data.copy()
    
    # Add token type to payload
    to_encode["token_type"] = token_type
    
    # Add a unique token ID
    to_encode["jti"] = str(uuid.uuid4())
    
    # Calculate expiration time
    if expires_delta:
        expire = datetime.utcnow() + timedelta(minutes=expires_delta)
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Add expiration time to payload
    to_encode["exp"] = expire
    
    # Add issued at time
    to_encode["iat"] = datetime.utcnow()
    
    # Encode the token
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt


def create_access_token(data: Dict[str, Any], expires_delta: Optional[int] = None) -> str:
    """
    Creates a JWT access token with the specified data and expiration.
    
    Args:
        data: The data to encode in the token
        expires_delta: Optional custom expiration time in minutes
        
    Returns:
        Encoded JWT access token
    """
    return create_jwt_token(data, expires_delta, TOKEN_TYPE_ACCESS)


def create_refresh_token(data: Dict[str, Any], expires_delta: Optional[int] = None) -> str:
    """
    Creates a JWT refresh token with the specified data and longer expiration.
    
    Args:
        data: The data to encode in the token
        expires_delta: Optional custom expiration time in minutes
        
    Returns:
        Encoded JWT refresh token
    """
    # If no specific expiration provided, use a longer one for refresh tokens (e.g., 24h)
    if expires_delta is None:
        expires_delta = ACCESS_TOKEN_EXPIRE_MINUTES * 24  # 24 hours by default
        
    return create_jwt_token(data, expires_delta, TOKEN_TYPE_REFRESH)


def decode_jwt_token(token: str) -> Dict[str, Any]:
    """
    Decodes and validates a JWT token.
    
    Args:
        token: JWT token to decode
        
    Returns:
        Decoded token payload
        
    Raises:
        AuthenticationException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[ALGORITHM]
        )
        return payload
    except JWTError as e:
        logger.error(f"Failed to validate token: {str(e)}")
        raise AuthenticationException("Could not validate credentials")


def verify_token_type(payload: Dict[str, Any], expected_type: str) -> bool:
    """
    Verifies that a token is of the expected type.
    
    Args:
        payload: Decoded token payload
        expected_type: Expected token type (access or refresh)
        
    Returns:
        True if token is of expected type, False otherwise
    """
    token_type = payload.get("token_type")
    return token_type == expected_type


def is_token_expired(payload: Dict[str, Any]) -> bool:
    """
    Checks if a JWT token has expired.
    
    Args:
        payload: Decoded token payload
        
    Returns:
        True if token is expired, False otherwise
    """
    expiration = payload.get("exp")
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
        Expiration datetime
    """
    if expires_delta:
        expire = datetime.utcnow() + timedelta(minutes=expires_delta)
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return expire


def refresh_access_token(refresh_token: str) -> str:
    """
    Creates a new access token from a valid refresh token.
    
    Args:
        refresh_token: The refresh token to use
        
    Returns:
        New access token
        
    Raises:
        AuthenticationException: If refresh token is invalid or expired
    """
    # Decode the refresh token
    payload = decode_jwt_token(refresh_token)
    
    # Verify it's a refresh token
    if not verify_token_type(payload, TOKEN_TYPE_REFRESH):
        logger.warning("Attempted to use non-refresh token for refresh operation")
        raise AuthenticationException("Invalid token type for refresh operation")
    
    # Check if token is expired
    if is_token_expired(payload):
        logger.warning("Attempted to use expired refresh token")
        raise AuthenticationException("Refresh token has expired")
    
    # Create a copy of the payload for the new access token
    new_payload = payload.copy()
    
    # Remove refresh token specific claims
    if "token_type" in new_payload:
        del new_payload["token_type"]
    if "jti" in new_payload:
        del new_payload["jti"]
    if "exp" in new_payload:
        del new_payload["exp"]
    if "iat" in new_payload:
        del new_payload["iat"]
    
    # Create a new access token
    return create_access_token(new_payload)


class JWTHandler:
    """
    Class for handling JWT token operations including creation, validation, and refreshing.
    """
    
    def __init__(self):
        """
        Initializes the JWTHandler with settings from configuration.
        """
        pass
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[int] = None) -> str:
        """
        Creates a JWT access token for a user.
        
        Args:
            data: The data to encode in the token
            expires_delta: Optional custom expiration time in minutes
            
        Returns:
            Encoded JWT access token
        """
        return create_access_token(data, expires_delta)
    
    def create_refresh_token(self, data: Dict[str, Any], expires_delta: Optional[int] = None) -> str:
        """
        Creates a JWT refresh token for a user.
        
        Args:
            data: The data to encode in the token
            expires_delta: Optional custom expiration time in minutes
            
        Returns:
            Encoded JWT refresh token
        """
        return create_refresh_token(data, expires_delta)
    
    def create_tokens(self, data: Dict[str, Any]) -> Dict[str, str]:
        """
        Creates both access and refresh tokens for a user.
        
        Args:
            data: The data to encode in the tokens
            
        Returns:
            Dictionary containing access_token and refresh_token
        """
        access_token = self.create_access_token(data)
        refresh_token = self.create_refresh_token(data)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token
        }
    
    def decode_token(self, token: str) -> Dict[str, Any]:
        """
        Decodes and validates a JWT token.
        
        Args:
            token: The JWT token to decode
            
        Returns:
            Decoded token payload
        """
        return decode_jwt_token(token)
    
    def validate_access_token(self, token: str) -> Dict[str, Any]:
        """
        Validates that a token is a valid access token.
        
        Args:
            token: The token to validate
            
        Returns:
            Decoded token payload if valid
            
        Raises:
            AuthenticationException: If token is invalid, expired, or wrong type
        """
        payload = self.decode_token(token)
        
        # Verify it's an access token
        if not verify_token_type(payload, TOKEN_TYPE_ACCESS):
            logger.warning("Attempted to use non-access token for authentication")
            raise AuthenticationException("Invalid token type")
        
        # Check if token is expired
        if is_token_expired(payload):
            logger.warning("Attempted to use expired access token")
            raise AuthenticationException("Token has expired")
        
        return payload
    
    def validate_refresh_token(self, token: str) -> Dict[str, Any]:
        """
        Validates that a token is a valid refresh token.
        
        Args:
            token: The token to validate
            
        Returns:
            Decoded token payload if valid
            
        Raises:
            AuthenticationException: If token is invalid, expired, or wrong type
        """
        payload = self.decode_token(token)
        
        # Verify it's a refresh token
        if not verify_token_type(payload, TOKEN_TYPE_REFRESH):
            logger.warning("Attempted to use non-refresh token for refresh operation")
            raise AuthenticationException("Invalid token type for refresh operation")
        
        # Check if token is expired
        if is_token_expired(payload):
            logger.warning("Attempted to use expired refresh token")
            raise AuthenticationException("Refresh token has expired")
        
        return payload
    
    def refresh_token(self, refresh_token: str) -> str:
        """
        Refreshes an access token using a valid refresh token.
        
        Args:
            refresh_token: The refresh token
            
        Returns:
            New access token
        """
        return refresh_access_token(refresh_token)
    
    def get_user_id_from_token(self, payload: Dict[str, Any]) -> str:
        """
        Extracts the user ID from a validated token.
        
        Args:
            payload: Decoded token payload
            
        Returns:
            User ID from token
            
        Raises:
            AuthenticationException: If user ID is not found in token
        """
        user_id = payload.get("sub")
        if not user_id:
            raise AuthenticationException("User ID not found in token")
        return user_id