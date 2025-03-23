from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from starlette.status import HTTP_429_TOO_MANY_REQUESTS
from typing import Dict, List, Optional, Callable
import time
import re

from ..core.config import settings
from ..cache.redis_cache import RedisCache
from ..core.logging import get_logger

# Initialize logger
logger = get_logger(__name__)

# Initialize Redis cache for storing rate limit counters
redis_cache = RedisCache()

# Enable rate limiting only in non-development environments
RATE_LIMIT_ENABLED = settings.ENVIRONMENT != 'development'

# Default rate limits for different API categories
DEFAULT_RATE_LIMITS = {
    "public": {
        "requests": 60,     # 60 requests
        "window": 60,       # per 1 minute
        "burst": 10         # with 10 burst allowance
    },
    "authenticated": {
        "requests": 300,    # 300 requests
        "window": 60,       # per 1 minute
        "burst": 50         # with 50 burst allowance
    },
    "upload": {
        "requests": 10,     # 10 requests
        "window": 60,       # per 1 minute
        "burst": 5          # with 5 burst allowance
    },
    "admin": {
        "requests": 600,    # 600 requests
        "window": 60,       # per 1 minute
        "burst": 100        # with 100 burst allowance
    }
}

# Redis key prefix for rate limit counters
RATE_LIMIT_KEY_PREFIX = 'rate_limit:'


def setup_rate_limiting(app: FastAPI) -> None:
    """
    Configures and applies rate limiting middleware to the FastAPI application.
    
    Args:
        app: FastAPI application instance
    """
    if RATE_LIMIT_ENABLED:
        # Add rate limiting middleware to the application
        app.add_middleware(
            RateLimitMiddleware,
            rate_limits=DEFAULT_RATE_LIMITS,
            excluded_paths=[
                # Exclude health check and documentation endpoints
                r"^/health$",
                r"^/docs$",
                r"^/redoc$",
                r"^/openapi.json$"
            ]
        )
        logger.info("Rate limiting middleware configured and enabled")
    else:
        logger.warning("Rate limiting is disabled in development environment")


def configure_endpoint_limits(limits_config: Dict) -> None:
    """
    Configures custom rate limits for specific endpoints or patterns.
    
    Args:
        limits_config: Dictionary with endpoint patterns and rate limit configurations
        
    Example:
        configure_endpoint_limits({
            r"^/api/v1/uploads": {
                "requests": 5,
                "window": 60,
                "burst": 2
            }
        })
    """
    # Validate configuration format
    for pattern, config in limits_config.items():
        if not isinstance(pattern, str):
            raise ValueError("Endpoint pattern must be a string")
        
        if not isinstance(config, dict):
            raise ValueError("Rate limit configuration must be a dictionary")
            
        if "requests" not in config or "window" not in config:
            raise ValueError("Rate limit configuration must include 'requests' and 'window'")
    
    # Update global rate limits with custom configuration
    global DEFAULT_RATE_LIMITS
    DEFAULT_RATE_LIMITS.update(limits_config)
    
    logger.info(f"Custom rate limits configured for {len(limits_config)} endpoints")


def get_client_ip(request: Request) -> str:
    """
    Extracts the client IP address from the request.
    
    Args:
        request: The request object
        
    Returns:
        Client IP address as string
    """
    # Check for X-Forwarded-For header (when behind proxy/load balancer)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # The first IP in the list is the client IP
        return forwarded_for.split(",")[0].strip()
    
    # Otherwise use the direct client address
    return request.client.host if request.client else "unknown"


def get_rate_limit_key(client_ip: str, endpoint: str) -> str:
    """
    Generates a unique key for rate limiting based on client IP and endpoint.
    
    Args:
        client_ip: Client IP address
        endpoint: API endpoint path
        
    Returns:
        Formatted rate limit key
    """
    return f"{RATE_LIMIT_KEY_PREFIX}{client_ip}:{endpoint}"


def determine_limit_category(request: Request) -> str:
    """
    Determines the rate limit category for a request based on path and authentication.
    
    Args:
        request: The request object
        
    Returns:
        Rate limit category (public, authenticated, upload, admin)
    """
    # Check for upload endpoints
    if re.match(r"^/api/v1/uploads", request.url.path):
        return "upload"
    
    # Check for admin endpoints
    if re.match(r"^/api/v1/admin", request.url.path):
        return "admin"
    
    # Check for authenticated requests
    auth_header = request.headers.get("Authorization")
    if auth_header:
        return "authenticated"
    
    # Default to public category
    return "public"


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware that implements rate limiting for API requests.
    
    Tracks request rates based on client IP and enforces configured
    rate limits to prevent abuse and ensure system stability.
    """
    
    def __init__(
        self, 
        app: "FastAPI", 
        rate_limits: Dict = None,
        excluded_paths: List[str] = None
    ):
        """
        Initialize the middleware with the ASGI application and rate limit configuration.
        
        Args:
            app: The ASGI application
            rate_limits: Rate limit configuration dictionary
            excluded_paths: List of path patterns to exclude from rate limiting
        """
        super().__init__(app)
        self.app = app
        self.rate_limits = rate_limits or DEFAULT_RATE_LIMITS
        self.excluded_paths = excluded_paths or [
            r"^/health$",
            r"^/docs$",
            r"^/redoc$",
            r"^/openapi.json$"
        ]
        logger.debug(f"Rate limit middleware initialized with {len(self.rate_limits)} categories")
    
    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        """
        Process the request and apply rate limiting.
        
        Args:
            request: The request object
            call_next: The next middleware in the chain
            
        Returns:
            The response or rate limit exceeded response
        """
        # Check if rate limiting should be applied to this request
        if not self.should_apply_rate_limit(request):
            return await call_next(request)
        
        # Extract client IP
        client_ip = get_client_ip(request)
        
        # Determine rate limit category based on request
        category = determine_limit_category(request)
        
        # Get rate limit configuration for this category
        limit_config = self.rate_limits.get(category, self.rate_limits["public"])
        
        # Create a rate limit key based on IP and path
        rate_limit_key = get_rate_limit_key(client_ip, request.url.path)
        
        # Check if rate limit is exceeded
        if self.check_rate_limit(rate_limit_key, limit_config):
            logger.warning(f"Rate limit exceeded for {client_ip} on {request.url.path} ({category})")
            return self.create_rate_limit_response(rate_limit_key, limit_config)
        
        # Increment request count
        self.increment_request_count(rate_limit_key, limit_config)
        
        # Process the request normally
        response = await call_next(request)
        
        # Add rate limit headers to response
        limit = limit_config["requests"] + limit_config.get("burst", 0)
        response.headers["X-RateLimit-Limit"] = str(limit)
        
        return response
    
    def should_apply_rate_limit(self, request: Request) -> bool:
        """
        Determines if rate limiting should be applied to a request.
        
        Args:
            request: The request object
            
        Returns:
            True if rate limiting should be applied, False otherwise
        """
        # Don't apply rate limiting to excluded paths
        for pattern in self.excluded_paths:
            if re.match(pattern, request.url.path):
                return False
        
        # Don't apply rate limiting to OPTIONS requests (CORS preflight)
        if request.method == "OPTIONS":
            return False
        
        return True
    
    def check_rate_limit(self, key: str, limit_config: Dict) -> bool:
        """
        Checks if a request exceeds the rate limit.
        
        Args:
            key: Rate limit key
            limit_config: Rate limit configuration
            
        Returns:
            True if limit is exceeded, False otherwise
        """
        # Get current request count from Redis
        current_count = redis_cache.get(key)
        if current_count is None:
            current_count = 0
        
        # Get rate limit parameters
        max_requests = limit_config["requests"]
        burst_allowance = limit_config.get("burst", 0)
        total_allowed = max_requests + burst_allowance
        
        # Check if current count exceeds the limit
        return current_count >= total_allowed
    
    def increment_request_count(self, key: str, limit_config: Dict) -> int:
        """
        Increments the request counter for rate limiting.
        
        Args:
            key: Rate limit key
            limit_config: Rate limit configuration
            
        Returns:
            New request count
        """
        # Get current count
        current_count = redis_cache.get(key)
        if current_count is None:
            current_count = 0
        
        # Increment count
        new_count = current_count + 1
        
        # Store in Redis with TTL equal to the rate limit window
        window = limit_config["window"]
        redis_cache.set(key, new_count, ttl=window)
        
        return new_count
    
    def create_rate_limit_response(self, key: str, limit_config: Dict) -> JSONResponse:
        """
        Creates a response for rate limit exceeded.
        
        Args:
            key: Rate limit key
            limit_config: Rate limit configuration
            
        Returns:
            JSON response with appropriate status code and headers
        """
        # Get remaining TTL for the rate limit
        remaining_ttl = redis_cache.ttl(key)
        if remaining_ttl < 0:
            remaining_ttl = limit_config["window"]
        
        # Create the response
        response = JSONResponse(
            status_code=HTTP_429_TOO_MANY_REQUESTS,
            content={
                "detail": "Rate limit exceeded. Please try again later.",
                "error": "too_many_requests",
                "retry_after": remaining_ttl
            }
        )
        
        # Add rate limit headers
        response.headers["Retry-After"] = str(remaining_ttl)
        response.headers["X-RateLimit-Limit"] = str(limit_config["requests"] + limit_config.get("burst", 0))
        response.headers["X-RateLimit-Reset"] = str(int(time.time()) + remaining_ttl)
        
        return response