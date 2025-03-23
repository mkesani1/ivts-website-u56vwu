import time
import logging
import typing
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp, Receive, Scope, Send
from starlette.datastructures import Headers
import fastapi

from ..core.logging import get_logger, get_request_id, RequestIdFilter
from ..utils.logging_utils import mask_sensitive_data
from ..monitoring.logging import log_performance
from ..core.config import settings

# Initialize logger
logger = get_logger(__name__)

# Paths that should be excluded from logging
EXCLUDED_PATHS = ['/health', '/metrics', '/docs', '/redoc', '/openapi.json']


def get_client_ip(headers: Headers, scope: dict) -> str:
    """
    Extracts the client IP address from request headers or connection info.
    
    Args:
        headers: Request headers
        scope: ASGI scope dictionary
        
    Returns:
        Client IP address as string
    """
    # Try X-Forwarded-For header first (common for proxied requests)
    forwarded_for = headers.get('X-Forwarded-For')
    if forwarded_for:
        # X-Forwarded-For can be a comma-separated list; the client is the first one
        return forwarded_for.split(',')[0].strip()
    
    # Try X-Real-IP header next (used by some proxies)
    real_ip = headers.get('X-Real-IP')
    if real_ip:
        return real_ip
    
    # Fall back to the client address from the scope
    if scope.get('client'):
        return scope['client'][0]
    
    # If all else fails, return unknown
    return 'unknown'


def should_log_path(path: str) -> bool:
    """
    Determines if the request path should be logged based on exclusion rules.
    
    Args:
        path: The request path
        
    Returns:
        True if the path should be logged, False otherwise
    """
    for excluded_path in EXCLUDED_PATHS:
        if path.startswith(excluded_path):
            return False
    return True


def extract_request_data(scope: dict, request_headers: dict) -> dict:
    """
    Extracts relevant data from the request for logging purposes.
    
    Args:
        scope: ASGI scope dictionary
        request_headers: Request headers dictionary
        
    Returns:
        Dictionary containing request data for logging
    """
    # Extract method and path
    method = scope.get('method', '')
    path = scope.get('path', '')
    
    # Extract query parameters
    query_string = scope.get('query_string', b'').decode('utf-8', errors='replace')
    
    # Get client IP
    headers = Headers(scope=scope)
    client_ip = get_client_ip(headers, scope)
    
    # Extract useful headers
    user_agent = request_headers.get('user-agent', '')
    content_length = request_headers.get('content-length', '')
    content_type = request_headers.get('content-type', '')
    referer = request_headers.get('referer', '')
    
    # Create request data dictionary
    request_data = {
        'method': method,
        'path': path,
        'query_string': query_string,
        'client_ip': client_ip,
        'user_agent': user_agent,
        'content_length': content_length,
        'content_type': content_type,
        'referer': referer,
    }
    
    return request_data


class RequestLoggerMiddleware:
    """
    Middleware that logs HTTP requests and responses with timing information.
    
    This middleware logs details about each HTTP request and response, including:
    - Request method, path, headers, client IP
    - Response status code
    - Request processing time
    - Correlation IDs for request tracing
    
    It also sends performance metrics for monitoring and ensures sensitive data is masked.
    """
    
    def __init__(self, app: ASGIApp):
        """
        Initialize the request logger middleware.
        
        Args:
            app: The ASGI application
        """
        self.app = app
        self.logger = get_logger(__name__)
        # Set the log level from settings
        log_level = getattr(logging, settings.LOG_LEVEL, logging.INFO)
        self.logger.setLevel(log_level)
    
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """
        Process the ASGI request and log request/response details.
        
        Args:
            scope: ASGI connection scope
            receive: ASGI receive function
            send: ASGI send function
        """
        # Only process HTTP requests
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Generate a unique request ID for correlation
        request_id = get_request_id()
        
        # Add the request ID to the scope for use by other components
        if "state" not in scope:
            scope["state"] = {}
        scope["state"]["request_id"] = request_id
        
        # Extract request headers
        headers = Headers(scope=scope)
        request_headers = dict(headers.items())
        
        # Check if path should be logged
        path = scope.get("path", "")
        if not should_log_path(path):
            # Skip logging for excluded paths
            await self.app(scope, receive, send)
            return
        
        # Extract request data for logging
        request_data = extract_request_data(scope, request_headers)
        
        # Record request start time
        start_time = time.time()
        
        # Create a wrapped send function to capture response data
        wrapped_send = self._create_wrapped_send(send, request_data, request_id, start_time)
        
        # Add request ID to logger context
        log_filter = RequestIdFilter(request_id)
        self.logger.addFilter(log_filter)
        
        # Log request start (mask sensitive data)
        masked_request_data = mask_sensitive_data(request_data)
        self.logger.info(
            f"Request started: {masked_request_data['method']} {masked_request_data['path']}",
            extra={
                "request_id": request_id,
                "request_data": masked_request_data,
                "event_type": "request_start"
            }
        )
        
        # Process the request with the wrapped send function
        try:
            await self.app(scope, receive, wrapped_send)
        finally:
            # Calculate request duration
            duration = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            # Get status code (added by wrapped_send)
            status_code = request_data.get("status_code", 0)
            
            # Log request completion
            self.logger.info(
                f"Request completed: {masked_request_data['method']} {masked_request_data['path']} {status_code} in {duration:.2f}ms",
                extra={
                    "request_id": request_id,
                    "status_code": status_code,
                    "duration_ms": duration,
                    "event_type": "request_end"
                }
            )
            
            # Log performance metrics
            log_performance(
                operation=f"http_request_{masked_request_data['method'].lower()}",
                duration=duration,
                success=(200 <= status_code < 500),
                attributes={
                    "path": masked_request_data['path'],
                    "method": masked_request_data['method'],
                    "status_code": status_code
                },
                context={
                    "request_id": request_id,
                    "environment": settings.ENVIRONMENT,
                    "service": settings.PROJECT_NAME
                }
            )
            
            # Remove the request ID filter
            self.logger.removeFilter(log_filter)
    
    def _create_wrapped_send(self, send: Send, request_data: dict, request_id: str, start_time: float) -> Send:
        """
        Creates a wrapped send function that captures response data for logging.
        
        Args:
            send: Original ASGI send function
            request_data: Dictionary with request data to be updated with response info
            request_id: Unique request identifier
            start_time: Request start time
            
        Returns:
            Wrapped send function
        """
        async def wrapped_send(message):
            # Capture response status when the start message is sent
            if message["type"] == "http.response.start":
                status_code = message.get("status", 0)
                headers = dict(Headers(raw=message.get("headers", [])).items())
                
                # Store status code in request_data for later logging
                request_data["status_code"] = status_code
                request_data["response_headers"] = headers
                
                # Calculate duration at this point (response headers sent)
                current_duration = (time.time() - start_time) * 1000
                request_data["headers_sent_ms"] = current_duration
            
            # Pass the message to the original send function
            await send(message)
        
        return wrapped_send