"""
Rate limiting implementation for the IndiVillage backend application.

This module provides mechanisms to limit request rates based on IP address,
user identity, or custom keys. It supports different rate limiting strategies
with configurable limits, windows, and storage backends.
"""

import time
import typing
import enum
import hashlib
from typing import Dict, Optional, Tuple, Any, Union

from ..core.config import settings, REDIS_URL, ENVIRONMENT
from ..cache.redis_cache import RedisCache
from ..core.exceptions import RateLimitException
from ..core.logging import get_logger

# Configure logger
logger = get_logger(__name__)

# Default rate limiting settings
DEFAULT_RATE_LIMIT = 100
DEFAULT_WINDOW_SECONDS = 3600
KEY_PREFIX = "rate_limit:"


def generate_rate_limit_key(identifier: str, endpoint: Optional[str] = None) -> str:
    """
    Generates a unique key for rate limiting based on identifier and endpoint.
    
    Args:
        identifier: The base identifier (IP, user ID, etc.)
        endpoint: Optional endpoint to scope the rate limit
        
    Returns:
        Unique key for rate limiting storage
    """
    if endpoint:
        # Create a more secure key by hashing the combined values
        combined = f"{identifier}:{endpoint}"
        hashed = hashlib.md5(combined.encode('utf-8')).hexdigest()
        return f"{KEY_PREFIX}{hashed}"
    
    # No endpoint, just use the identifier directly with prefix
    return f"{KEY_PREFIX}{identifier}"


class RateLimitStrategy(enum.Enum):
    """
    Enumeration of rate limiting strategies.
    
    - FIXED_WINDOW: Simple counting within a fixed time window
    - SLIDING_WINDOW: Time-weighted counting for smoother transitions
    - TOKEN_BUCKET: Token replenishment over time
    """
    FIXED_WINDOW = 1
    SLIDING_WINDOW = 2
    TOKEN_BUCKET = 3


class RateLimitExceeded(RateLimitException):
    """
    Exception raised when a rate limit is exceeded.
    
    Includes information needed for rate limit headers in HTTP responses.
    """
    
    def __init__(self, message: str, limit: int, reset_time: int):
        """
        Initializes the rate limit exception.
        
        Args:
            message: Human-readable error message
            limit: The rate limit that was exceeded
            reset_time: Unix timestamp when the limit resets
        """
        super().__init__(message=message, details={
            "limit": limit,
            "reset_time": reset_time
        })
        self.limit = limit
        self.reset_time = reset_time


class RateLimiter:
    """
    Rate limiting implementation with multiple strategies and storage backends.
    
    Provides methods for rate limiting by IP address, user ID, or custom keys,
    with support for different strategies and configurable limits.
    """
    
    def __init__(self, redis_url: Optional[str] = None, 
                 default_strategy: RateLimitStrategy = RateLimitStrategy.FIXED_WINDOW):
        """
        Initializes the rate limiter with Redis cache backend.
        
        Args:
            redis_url: Redis connection URL (uses settings.REDIS_URL if not provided)
            default_strategy: Default rate limiting strategy to use
        """
        # Initialize Redis cache for storing rate limit counters
        self._cache = RedisCache(redis_url or settings.REDIS_URL)
        
        # Set default strategy
        self._default_strategy = default_strategy
        
        # Initialize endpoint-specific limits dictionary
        self._endpoint_limits: Dict[str, Tuple[int, int]] = {}
        
        logger.info(f"Rate limiter initialized with default strategy: {default_strategy.name}")
    
    def limit_by_ip(self, ip_address: str, endpoint: str, 
                    limit: Optional[int] = None, 
                    window_seconds: Optional[int] = None) -> Tuple[bool, int, int]:
        """
        Apply rate limiting based on IP address.
        
        Args:
            ip_address: The client IP address
            endpoint: The API endpoint being accessed
            limit: Maximum requests allowed in the time window
            window_seconds: Time window in seconds
            
        Returns:
            Tuple of (is_allowed, remaining_requests, reset_time)
        """
        # Generate a unique rate limit key for this IP and endpoint
        key = generate_rate_limit_key(ip_address, endpoint)
        
        # Get endpoint-specific limits if configured, otherwise use provided or defaults
        if limit is None or window_seconds is None:
            endpoint_limit, endpoint_window = self.get_endpoint_limits(endpoint)
            limit = limit or endpoint_limit
            window_seconds = window_seconds or endpoint_window
        
        logger.debug(f"Checking rate limit for IP {ip_address} on endpoint {endpoint}: {limit}/{window_seconds}s")
        
        # Check the rate limit
        return self._check_rate_limit(key, limit, window_seconds, self._default_strategy)
    
    def limit_by_user(self, user_id: str, endpoint: str, 
                      limit: Optional[int] = None, 
                      window_seconds: Optional[int] = None) -> Tuple[bool, int, int]:
        """
        Apply rate limiting based on user identifier.
        
        Args:
            user_id: The user identifier
            endpoint: The API endpoint being accessed
            limit: Maximum requests allowed in the time window
            window_seconds: Time window in seconds
            
        Returns:
            Tuple of (is_allowed, remaining_requests, reset_time)
        """
        # Generate a unique rate limit key for this user and endpoint
        key = generate_rate_limit_key(user_id, endpoint)
        
        # Get endpoint-specific limits if configured, otherwise use provided or defaults
        if limit is None or window_seconds is None:
            endpoint_limit, endpoint_window = self.get_endpoint_limits(endpoint)
            limit = limit or endpoint_limit
            window_seconds = window_seconds or endpoint_window
        
        logger.debug(f"Checking rate limit for user {user_id} on endpoint {endpoint}: {limit}/{window_seconds}s")
        
        # Check the rate limit
        return self._check_rate_limit(key, limit, window_seconds, self._default_strategy)
    
    def limit_by_key(self, key: str, limit: Optional[int] = None, 
                    window_seconds: Optional[int] = None) -> Tuple[bool, int, int]:
        """
        Apply rate limiting based on a custom key.
        
        Args:
            key: The custom rate limit key
            limit: Maximum requests allowed in the time window
            window_seconds: Time window in seconds
            
        Returns:
            Tuple of (is_allowed, remaining_requests, reset_time)
        """
        # Format the key with prefix
        formatted_key = f"{KEY_PREFIX}{key}"
        
        # Use provided limits or defaults
        actual_limit = limit or DEFAULT_RATE_LIMIT
        actual_window = window_seconds or DEFAULT_WINDOW_SECONDS
        
        logger.debug(f"Checking rate limit for custom key {key}: {actual_limit}/{actual_window}s")
        
        # Check the rate limit
        return self._check_rate_limit(formatted_key, actual_limit, actual_window, self._default_strategy)
    
    def _check_rate_limit(self, key: str, limit: int, window_seconds: int, 
                         strategy: RateLimitStrategy) -> Tuple[bool, int, int]:
        """
        Internal method to check if a request is within rate limits.
        
        Args:
            key: The rate limit key
            limit: Maximum requests allowed
            window_seconds: Time window in seconds
            strategy: Rate limiting strategy to apply
            
        Returns:
            Tuple of (is_allowed, remaining_requests, reset_time)
        """
        # Get current count from cache
        current_count = self._cache.get(key)
        current_time = int(time.time())
        
        if current_count is None:
            # First request, initialize counter
            self._cache.set(key, 1, window_seconds)
            return True, limit - 1, current_time + window_seconds
        
        # Apply the appropriate rate limiting strategy
        new_count, remaining, reset_time = self._apply_strategy(
            key, current_count, limit, window_seconds, strategy
        )
        
        # Check if the rate limit has been exceeded
        if new_count > limit:
            logger.warning(f"Rate limit exceeded for key {key}: {new_count}/{limit}")
            return False, 0, reset_time
        
        return True, remaining, reset_time
    
    def _apply_strategy(self, key: str, current_count: Union[int, Dict[str, Any]], 
                       limit: int, window_seconds: int, 
                       strategy: RateLimitStrategy) -> Tuple[int, int, int]:
        """
        Apply the specified rate limiting strategy.
        
        Args:
            key: The rate limit key
            current_count: Current request count or data structure
            limit: Maximum requests allowed
            window_seconds: Time window in seconds
            strategy: Rate limiting strategy to apply
            
        Returns:
            Tuple of (new_count, remaining_requests, reset_time)
        """
        current_time = int(time.time())
        
        if strategy == RateLimitStrategy.FIXED_WINDOW:
            # Simple counter with fixed expiration
            new_count = self._cache.increment(key, 1)
            ttl = self._cache.get_ttl(key)
            
            # If TTL is negative, set a new expiration
            if ttl < 0:
                self._cache.set(key, new_count, window_seconds)
                ttl = window_seconds
            
            reset_time = current_time + ttl
            remaining = max(0, limit - new_count)
            
            return new_count, remaining, reset_time
            
        elif strategy == RateLimitStrategy.SLIDING_WINDOW:
            # For sliding window, we need to store timestamps of requests
            # This implementation is simplified for compatibility with Redis
            
            # Current count is assumed to be a dictionary with count and window_start
            if isinstance(current_count, dict):
                window_start = current_count.get('window_start', current_time - window_seconds)
                count = current_count.get('count', 0)
            else:
                # Initialize if it's not the expected format
                window_start = current_time - window_seconds
                count = current_count if isinstance(current_count, int) else 0
            
            # Calculate weight of previous window based on overlap
            elapsed = current_time - window_start
            if elapsed >= window_seconds:
                # Outside previous window, start fresh
                new_count = 1
                window_start = current_time
            else:
                # Inside previous window, weight by time
                weight = 1 - (elapsed / window_seconds)
                new_count = int(count * weight) + 1
            
            # Store updated values
            self._cache.set(key, {
                'count': new_count,
                'window_start': window_start
            }, window_seconds * 2)  # Store for twice the window for overlap
            
            reset_time = window_start + window_seconds
            remaining = max(0, limit - new_count)
            
            return new_count, remaining, reset_time
            
        elif strategy == RateLimitStrategy.TOKEN_BUCKET:
            # Token bucket implementation
            # Current count is assumed to be a dictionary with tokens and last_refill
            if isinstance(current_count, dict):
                tokens = current_count.get('tokens', limit)
                last_refill = current_count.get('last_refill', current_time)
            else:
                # Initialize if it's not the expected format
                tokens = limit - 1  # Start with limit-1 tokens (one used for this request)
                last_refill = current_time
            
            # Calculate token refill
            elapsed = current_time - last_refill
            refill_rate = limit / window_seconds  # Tokens per second
            refill_tokens = elapsed * refill_rate
            
            # Add refilled tokens, up to the limit
            tokens = min(limit, tokens + refill_tokens)
            
            # Use one token for this request
            tokens -= 1
            
            # Store updated values
            self._cache.set(key, {
                'tokens': tokens,
                'last_refill': current_time
            }, window_seconds * 2)  # Store for twice the window just in case
            
            # Calculate time until tokens are fully refilled
            time_to_refill = (limit - tokens) / refill_rate if tokens < limit else 0
            reset_time = current_time + int(time_to_refill)
            
            # Calculate remaining requests (same as tokens)
            remaining = max(0, int(tokens))
            
            # If tokens are negative, rate limit exceeded
            new_count = limit - int(tokens)
            
            return new_count, remaining, reset_time
        
        # Fallback to fixed window for unsupported strategies
        logger.warning(f"Unsupported strategy {strategy}, falling back to fixed window")
        new_count = self._cache.increment(key, 1)
        ttl = self._cache.get_ttl(key)
        reset_time = current_time + (ttl if ttl > 0 else window_seconds)
        remaining = max(0, limit - new_count)
        
        return new_count, remaining, reset_time
    
    def configure_endpoint(self, endpoint: str, limit: int, window_seconds: int) -> None:
        """
        Configure rate limits for a specific endpoint.
        
        Args:
            endpoint: The API endpoint
            limit: Maximum requests allowed
            window_seconds: Time window in seconds
        """
        self._endpoint_limits[endpoint] = (limit, window_seconds)
        logger.info(f"Configured rate limit for endpoint {endpoint}: {limit}/{window_seconds}s")
    
    def get_endpoint_limits(self, endpoint: str) -> Tuple[int, int]:
        """
        Get configured rate limits for an endpoint.
        
        Args:
            endpoint: The API endpoint
            
        Returns:
            Tuple of (rate_limit, window_seconds)
        """
        # Check if endpoint has specific configuration
        if endpoint in self._endpoint_limits:
            return self._endpoint_limits[endpoint]
        
        # Return default limits
        return DEFAULT_RATE_LIMIT, DEFAULT_WINDOW_SECONDS
    
    def reset_limits(self, key: str) -> bool:
        """
        Reset rate limits for a specific key.
        
        Args:
            key: The rate limit key to reset
            
        Returns:
            True if successful, False otherwise
        """
        formatted_key = f"{KEY_PREFIX}{key}" if not key.startswith(KEY_PREFIX) else key
        success = self._cache.delete(formatted_key)
        
        if success:
            logger.info(f"Reset rate limits for key {key}")
        else:
            logger.warning(f"Failed to reset rate limits for key {key}")
            
        return success
    
    def get_headers(self, limit: int, remaining: int, reset_time: int) -> Dict[str, str]:
        """
        Generate rate limit headers for HTTP responses.
        
        Args:
            limit: The rate limit
            remaining: Remaining requests
            reset_time: Unix timestamp when the limit resets
            
        Returns:
            Dictionary of rate limit headers
        """
        return {
            "X-RateLimit-Limit": str(limit),
            "X-RateLimit-Remaining": str(remaining),
            "X-RateLimit-Reset": str(reset_time),
            "X-RateLimit-Policy": f"{limit};w={reset_time - int(time.time())}"
        }