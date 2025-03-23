"""
Cache module for the IndiVillage backend application.

This module provides caching functionality for performance optimization,
with a Redis-based implementation and decorators for easy integration.
Key components include:

- RedisCache: Redis-based cache implementation with serialization
- cached: Decorator for function-level caching with configurable TTL
- invalidate_cache: Decorator for cache invalidation
- clear_cache: Manual cache clearing utility
- generate_cache_key: Utility for generating consistent cache keys
"""

# Version of the cache module
__version__ = "1.0.0"

# Import from internal modules
from .redis_cache import RedisCache
from .decorators import (
    cached,
    invalidate_cache,
    clear_cache,
    generate_cache_key
)

# Expose these components as part of the public API
__all__ = [
    'RedisCache',
    'cached',
    'invalidate_cache',
    'clear_cache',
    'generate_cache_key',
]