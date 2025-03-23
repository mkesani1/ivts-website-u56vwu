"""
Cache decorator module for the IndiVillage backend application.

This module provides function-level caching decorators and utilities that use Redis
for improved performance. It includes decorators for simple caching, cache invalidation,
cache statistics tracking, and timing, as well as utilities for cache key generation
and management.
"""

import functools
import typing
import hashlib
import json
import inspect
import time

from ..core.events import get_redis_cache
from ..core.logging import get_logger

# Initialize logger for this module
logger = get_logger(__name__)

# Default time-to-live for cached items (1 hour)
DEFAULT_CACHE_TTL = 3600

# Prefix for function cache keys
CACHE_PREFIX = 'func:'


def generate_cache_key(func, args, kwargs, prefix=CACHE_PREFIX):
    """
    Generates a unique cache key based on function name and arguments.
    
    Args:
        func: The function for which to generate a cache key
        args: Positional arguments to the function
        kwargs: Keyword arguments to the function
        prefix: Cache key prefix (default: CACHE_PREFIX)
        
    Returns:
        str: Unique cache key string
    """
    # Get function name and module for the function identifier
    func_name = func.__name__
    module_name = func.__module__
    
    # Handle non-serializable arguments by converting to strings
    def serialize_arg(arg):
        try:
            # Try to use repr for a more accurate string representation
            return repr(arg)
        except:
            # Fall back to basic string conversion
            return str(arg)
    
    # Create a dictionary with function identifier and serialized arguments
    key_dict = {
        'func': f"{module_name}.{func_name}",
        'args': [serialize_arg(arg) for arg in args],
        'kwargs': {k: serialize_arg(v) for k, v in kwargs.items()}
    }
    
    # Serialize the dictionary to JSON and generate hash
    try:
        key_json = json.dumps(key_dict, sort_keys=True)
    except TypeError:
        # If JSON serialization fails, create a simpler key
        key_str = f"{module_name}.{func_name}:{hash(func)}:{len(args)}:{len(kwargs)}"
        key_json = key_str
    
    # Generate MD5 hash of the key string
    key_hash = hashlib.md5(key_json.encode()).hexdigest()
    
    # Return the prefixed key
    return f"{prefix}{key_hash}"


def cached(ttl=DEFAULT_CACHE_TTL, key_prefix=CACHE_PREFIX):
    """
    Decorator that caches function results in Redis.
    
    Args:
        ttl: Time-to-live in seconds (default: DEFAULT_CACHE_TTL)
        key_prefix: Cache key prefix (default: CACHE_PREFIX)
        
    Returns:
        callable: Decorated function
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get Redis cache instance
            cache = get_redis_cache()
            if not cache:
                # If cache is not available, just execute the function
                logger.warning(f"Cache not available, executing {func.__name__} without caching")
                return func(*args, **kwargs)
            
            # Generate cache key
            cache_key = generate_cache_key(func, args, kwargs, key_prefix)
            
            # Try to get result from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {func.__name__} with key {cache_key}")
                return cached_result
            
            # Cache miss, execute function
            logger.debug(f"Cache miss for {func.__name__} with key {cache_key}")
            result = func(*args, **kwargs)
            
            # Store result in cache
            cache.set(cache_key, result, ttl)
            logger.debug(f"Cached result for {func.__name__} with key {cache_key}, TTL: {ttl}s")
            
            return result
        return wrapper
    return decorator


def invalidate_cache(pattern):
    """
    Decorator that invalidates cache entries after function execution.
    
    Args:
        pattern: Cache key pattern to invalidate
        
    Returns:
        callable: Decorated function
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Execute the original function first
            result = func(*args, **kwargs)
            
            # Get Redis cache instance
            cache = get_redis_cache()
            if not cache:
                logger.warning(f"Cache not available, can't invalidate pattern {pattern}")
                return result
            
            # Invalidate cache entries
            count = cache.delete_pattern(pattern)
            logger.info(f"Invalidated {count} cache entries with pattern {pattern}")
            
            return result
        return wrapper
    return decorator


def clear_cache(pattern):
    """
    Utility function to manually clear cache entries by pattern.
    
    Args:
        pattern: Cache key pattern to clear
        
    Returns:
        int: Number of cache entries cleared
    """
    cache = get_redis_cache()
    if not cache:
        logger.warning(f"Cache not available, can't clear pattern {pattern}")
        return 0
    
    count = cache.delete_pattern(pattern)
    logger.info(f"Cleared {count} cache entries with pattern {pattern}")
    
    return count


def cache_stats():
    """
    Decorator that logs cache hit/miss statistics for a function.
    
    Returns:
        callable: Decorated function
    """
    def decorator(func):
        # Initialize hit/miss counters
        hit_count = 0
        miss_count = 0
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal hit_count, miss_count
            
            # Get Redis cache instance
            cache = get_redis_cache()
            if not cache:
                # If cache is not available, just execute the function
                logger.warning(f"Cache not available, executing {func.__name__} without caching")
                return func(*args, **kwargs)
            
            # Generate cache key
            cache_key = generate_cache_key(func, args, kwargs)
            
            # Check if result exists in cache
            result = cache.get(cache_key)
            if result is not None:
                # Cache hit
                hit_count += 1
                hit_ratio = hit_count / (hit_count + miss_count) * 100 if (hit_count + miss_count) > 0 else 0
                logger.info(f"Cache hit for {func.__name__}: hits={hit_count}, misses={miss_count}, ratio={hit_ratio:.2f}%")
                return result
            
            # Cache miss
            miss_count += 1
            hit_ratio = hit_count / (hit_count + miss_count) * 100 if (hit_count + miss_count) > 0 else 0
            logger.info(f"Cache miss for {func.__name__}: hits={hit_count}, misses={miss_count}, ratio={hit_ratio:.2f}%")
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, DEFAULT_CACHE_TTL)
            
            return result
        
        return wrapper
    return decorator


def timed_cache(ttl=DEFAULT_CACHE_TTL):
    """
    Decorator that combines caching with execution time measurement.
    
    Args:
        ttl: Time-to-live in seconds (default: DEFAULT_CACHE_TTL)
        
    Returns:
        callable: Decorated function
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get Redis cache instance
            cache = get_redis_cache()
            if not cache:
                # If cache is not available, just execute the function with timing
                logger.warning(f"Cache not available, executing {func.__name__} without caching")
                start_time = time.time()
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                logger.info(f"Executed {func.__name__} in {execution_time:.4f}s (no caching)")
                return result
            
            # Generate cache key
            cache_key = generate_cache_key(func, args, kwargs)
            
            # Try to get result from cache
            result = cache.get(cache_key)
            if result is not None:
                logger.debug(f"Cache hit for {func.__name__} with key {cache_key}")
                return result
            
            # Cache miss, execute function with timing
            logger.debug(f"Cache miss for {func.__name__} with key {cache_key}")
            start_time = time.time()
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # Store result in cache
            cache.set(cache_key, result, ttl)
            logger.info(f"Executed {func.__name__} in {execution_time:.4f}s and cached with TTL: {ttl}s")
            
            return result
        return wrapper
    return decorator


class CacheKey:
    """
    Utility class for generating and managing cache keys.
    """
    
    def __init__(self, prefix=CACHE_PREFIX):
        """
        Initializes the CacheKey with a prefix.
        
        Args:
            prefix: Cache key prefix (default: CACHE_PREFIX)
        """
        self.prefix = prefix
    
    def generate(self, base_key, params):
        """
        Generates a cache key for the given parameters.
        
        Args:
            base_key: Base key string
            params: Parameters to include in the key
            
        Returns:
            str: Generated cache key
        """
        # Serialize params to a stable representation
        if isinstance(params, dict):
            # Convert dict values to strings for stable serialization
            try:
                params_str = json.dumps({k: str(v) for k, v in params.items()}, sort_keys=True)
            except:
                params_str = str(hash(str(params)))
        else:
            # Convert other types to string
            params_str = str(params)
        
        # Combine base_key with serialized params and hash
        combined = f"{base_key}:{params_str}"
        key_hash = hashlib.md5(combined.encode()).hexdigest()
        
        # Return the prefixed key
        return f"{self.prefix}{key_hash}"
    
    def for_function(self, func, args, kwargs):
        """
        Generates a cache key for a function call.
        
        Args:
            func: The function being called
            args: Positional arguments
            kwargs: Keyword arguments
            
        Returns:
            str: Generated cache key
        """
        # Get function name and module
        func_name = func.__name__
        module_name = func.__module__
        func_id = f"{module_name}.{func_name}"
        
        # Create params from args and kwargs
        params = {
            'args': [str(arg) for arg in args],
            'kwargs': {k: str(v) for k, v in kwargs.items()}
        }
        
        # Generate and return the key
        return self.generate(func_id, params)
    
    def pattern_for_prefix(self, specific_prefix):
        """
        Generates a pattern for matching all keys with a specific prefix.
        
        Args:
            specific_prefix: Specific prefix to match
            
        Returns:
            str: Pattern for matching keys
        """
        # Combine class prefix with specific prefix and add wildcard
        return f"{self.prefix}{specific_prefix}*"