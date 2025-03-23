import redis  # redis ^4.5.4
import pickle
import json
import time
from typing import Any, Optional

from ..core.config import settings
from ..core.logging import get_logger

logger = get_logger(__name__)
DEFAULT_TTL = 3600  # 1 hour default TTL
REDIS_KEY_PREFIX = 'indivillage:'


def serialize_data(data: Any) -> bytes:
    """
    Serializes data for storage in Redis.
    
    First tries to serialize as JSON for simple types, falls back to pickle for
    complex objects. This approach provides better interoperability for simple
    data structures while still supporting complex Python objects.
    
    Args:
        data: Data to serialize
        
    Returns:
        bytes: Serialized data as bytes
    """
    try:
        # Try to serialize as JSON (more interoperable)
        serialized = json.dumps(data)
        # Prefix with 'json:' to identify format during deserialization
        return f"json:{serialized}".encode('utf-8')
    except (TypeError, OverflowError):
        # Fall back to pickle for complex objects
        logger.debug("JSON serialization failed, using pickle")
        return pickle.dumps(data)


def deserialize_data(data: Optional[bytes]) -> Any:
    """
    Deserializes data retrieved from Redis.
    
    Handles both JSON and pickle serialized data by checking the prefix.
    
    Args:
        data: Serialized data as bytes
        
    Returns:
        Any: Deserialized Python object
    """
    if data is None:
        return None
    
    try:
        # Try to check if data was serialized as JSON (starts with 'json:')
        if data.startswith(b'json:'):
            # Remove the 'json:' prefix and parse JSON
            json_data = data[5:].decode('utf-8')
            return json.loads(json_data)
        
        # Otherwise, assume it's pickle serialized
        return pickle.loads(data)
    except Exception as e:
        logger.error(f"Deserialization error: {str(e)}")
        return None


class RedisCache:
    """
    Redis cache implementation with serialization and TTL support.
    
    Provides a wrapper around Redis client with methods for storing,
    retrieving, and invalidating cached data. Supports serialization
    and deserialization of complex Python objects and implements
    configurable TTL for cache entries.
    """
    
    def __init__(self, redis_url: Optional[str] = None):
        """
        Initializes the Redis cache with connection settings.
        
        Args:
            redis_url: Redis connection URL, uses settings.REDIS_URL if not provided
        """
        self._url = redis_url or settings.REDIS_URL
        self._client = None
        self._connected = False
        
        # Initialize connection
        self._connect()
        logger.info(f"Redis cache initialized: connected={self._connected}")
    
    def _connect(self) -> bool:
        """
        Establishes connection to Redis server.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            if not self._url:
                logger.warning("Redis URL not provided, cache will not be functional")
                return False
            
            # Create Redis client
            self._client = redis.Redis.from_url(self._url, decode_responses=False)
            
            # Test connection
            self._client.ping()
            self._connected = True
            logger.debug(f"Connected to Redis at {self._url}")
            return True
        except Exception as e:
            self._connected = False
            logger.error(f"Redis connection error: {str(e)}")
            return False
    
    def _format_key(self, key: str) -> str:
        """
        Formats a cache key with prefix.
        
        Args:
            key: Original cache key
            
        Returns:
            str: Formatted cache key with prefix
        """
        return f"{REDIS_KEY_PREFIX}{key}"
    
    def get(self, key: str) -> Any:
        """
        Retrieves a value from cache by key.
        
        Args:
            key: Cache key
            
        Returns:
            Any: Cached value or None if not found
        """
        # Check if Redis is connected
        if not self._connected and not self._connect():
            logger.warning("Redis not connected, get operation failed")
            return None
        
        try:
            start_time = time.time()
            formatted_key = self._format_key(key)
            data = self._client.get(formatted_key)
            
            if data is not None:
                # Cache hit
                value = deserialize_data(data)
                logger.debug(f"Cache hit for key '{key}'")
                return value
            else:
                # Cache miss
                logger.debug(f"Cache miss for key '{key}'")
                return None
        except Exception as e:
            logger.error(f"Error retrieving from cache: {str(e)}")
            return None
        finally:
            elapsed = (time.time() - start_time) * 1000
            logger.debug(f"Cache get operation completed in {elapsed:.2f}ms")
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Stores a value in cache with optional TTL.
        
        Args:
            key: Cache key
            value: Value to store
            ttl: Time to live in seconds, uses DEFAULT_TTL if not provided
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Check if Redis is connected
        if not self._connected and not self._connect():
            logger.warning("Redis not connected, set operation failed")
            return False
        
        try:
            start_time = time.time()
            formatted_key = self._format_key(key)
            data = serialize_data(value)
            
            # Use provided TTL or default
            ttl_seconds = ttl if ttl is not None else DEFAULT_TTL
            
            # Store data in Redis with TTL
            result = self._client.setex(formatted_key, ttl_seconds, data)
            logger.debug(f"Cache set for key '{key}' with TTL {ttl_seconds}s")
            return result
        except Exception as e:
            logger.error(f"Error setting cache: {str(e)}")
            return False
        finally:
            elapsed = (time.time() - start_time) * 1000
            logger.debug(f"Cache set operation completed in {elapsed:.2f}ms")
    
    def delete(self, key: str) -> bool:
        """
        Deletes a value from cache by key.
        
        Args:
            key: Cache key
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Check if Redis is connected
        if not self._connected and not self._connect():
            logger.warning("Redis not connected, delete operation failed")
            return False
        
        try:
            formatted_key = self._format_key(key)
            result = self._client.delete(formatted_key)
            logger.debug(f"Cache delete for key '{key}'")
            return bool(result)
        except Exception as e:
            logger.error(f"Error deleting from cache: {str(e)}")
            return False
    
    def delete_pattern(self, pattern: str) -> int:
        """
        Deletes all keys matching a pattern.
        
        Args:
            pattern: Key pattern to match
            
        Returns:
            int: Number of keys deleted
        """
        # Check if Redis is connected
        if not self._connected and not self._connect():
            logger.warning("Redis not connected, delete_pattern operation failed")
            return 0
        
        try:
            formatted_pattern = self._format_key(pattern)
            keys = self._client.keys(formatted_pattern)
            
            if not keys:
                logger.debug(f"No keys found matching pattern '{pattern}'")
                return 0
            
            # Delete all matching keys
            count = self._client.delete(*keys)
            logger.debug(f"Deleted {count} keys matching pattern '{pattern}'")
            return count
        except Exception as e:
            logger.error(f"Error deleting keys by pattern: {str(e)}")
            return 0
    
    def exists(self, key: str) -> bool:
        """
        Checks if a key exists in the cache.
        
        Args:
            key: Cache key
            
        Returns:
            bool: True if key exists, False otherwise
        """
        # Check if Redis is connected
        if not self._connected and not self._connect():
            logger.warning("Redis not connected, exists operation failed")
            return False
        
        try:
            formatted_key = self._format_key(key)
            return bool(self._client.exists(formatted_key))
        except Exception as e:
            logger.error(f"Error checking key existence: {str(e)}")
            return False
    
    def ttl(self, key: str) -> int:
        """
        Gets the remaining TTL for a key.
        
        Args:
            key: Cache key
            
        Returns:
            int: Remaining TTL in seconds, -1 if no TTL, -2 if key doesn't exist
        """
        # Check if Redis is connected
        if not self._connected and not self._connect():
            logger.warning("Redis not connected, ttl operation failed")
            return -2
        
        try:
            formatted_key = self._format_key(key)
            return self._client.ttl(formatted_key)
        except Exception as e:
            logger.error(f"Error getting TTL: {str(e)}")
            return -2
    
    def flush(self) -> int:
        """
        Flushes all keys from the cache with the application prefix.
        
        Returns:
            int: Number of keys flushed
        """
        # Check if Redis is connected
        if not self._connected and not self._connect():
            logger.warning("Redis not connected, flush operation failed")
            return 0
        
        try:
            # Get all keys with application prefix
            keys = self._client.keys(f"{REDIS_KEY_PREFIX}*")
            
            if not keys:
                logger.debug("No keys to flush")
                return 0
            
            # Delete all keys
            count = self._client.delete(*keys)
            logger.info(f"Flushed {count} keys from cache")
            return count
        except Exception as e:
            logger.error(f"Error flushing cache: {str(e)}")
            return 0
    
    def health_check(self) -> bool:
        """
        Performs a health check on the Redis connection.
        
        Returns:
            bool: True if Redis is healthy, False otherwise
        """
        try:
            if not self._connected:
                return self._connect()
            
            # Try to ping Redis
            self._client.ping()
            logger.debug("Redis health check: OK")
            return True
        except Exception as e:
            self._connected = False
            logger.error(f"Redis health check failed: {str(e)}")
            return False