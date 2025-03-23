"""
Distributed tracing module for the IndiVillage backend application.

This module provides functionality to create, manage, and correlate trace spans
across different components of the system, enabling visibility into request flows
and performance bottlenecks.
"""

import time
import uuid
import datetime
import typing
import functools
import contextvars
import inspect
import json
import asyncio

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

import opentelemetry  # opentelemetry-api ^1.15.0
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.resource import ResourceAttributes  # opentelemetry-semantic-conventions ^0.36b0
from opentelemetry.exporter.otlp.proto.grpc import OTLPSpanExporter  # opentelemetry-exporter-otlp-proto-grpc ^1.15.0
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

from ..core.config import settings
from ..core.logging import get_logger, get_request_id
from .metrics import record_metric

# Initialize logger
logger = get_logger(__name__)

# Configuration from settings
TRACING_ENABLED = getattr(settings, 'TRACING_ENABLED', True)
TRACE_SAMPLE_RATE = getattr(settings, 'TRACE_SAMPLE_RATE', 0.1)
OTLP_ENDPOINT = getattr(settings, 'OTLP_ENDPOINT', None)

# Context variable to store the current span
current_span = contextvars.ContextVar('current_span', default=None)

# Global tracer instance
tracer = None


class SpanEvent:
    """
    Class representing an event within a tracing span.
    """
    
    def __init__(self, name: str, attributes: typing.Optional[dict] = None, 
                 timestamp: typing.Optional[datetime.datetime] = None):
        """
        Initializes a new span event.
        
        Args:
            name: The name of the event
            attributes: Optional attributes for the event
            timestamp: Optional timestamp for the event (defaults to now)
        """
        self.name = name
        self.attributes = attributes or {}
        self.timestamp = timestamp or datetime.datetime.utcnow()
    
    def to_dict(self) -> dict:
        """
        Converts the event to a dictionary representation.
        
        Returns:
            Dictionary representation of the event
        """
        return {
            'name': self.name,
            'attributes': self.attributes,
            'timestamp': self.timestamp.isoformat()
        }


class Span:
    """
    Class representing a tracing span with additional utility methods.
    """
    
    def __init__(self, otel_span: trace.Span, name: str):
        """
        Initializes a new span.
        
        Args:
            otel_span: The OpenTelemetry span object
            name: The name of the span
        """
        self._otel_span = otel_span
        self.name = name
        
        # Extract span context information
        span_context = otel_span.get_span_context()
        self.id = format(span_context.span_id, '016x') if span_context else str(uuid.uuid4())
        self.trace_id = format(span_context.trace_id, '032x') if span_context else str(uuid.uuid4())
        self.parent_id = None  # Will be set if available
        
        # Additional properties
        self.attributes = {}
        self.events = []
        self.start_time = time.time()
        self.end_time = None
        self.is_recording = True
    
    def add_event(self, name: str, attributes: typing.Optional[dict] = None) -> None:
        """
        Adds an event to the span.
        
        Args:
            name: The name of the event
            attributes: Optional attributes for the event
        """
        if not self.is_recording:
            logger.warning(f"Cannot add event '{name}' to span '{self.name}' as it is no longer recording")
            return
        
        # Create and store the event
        event = SpanEvent(name, attributes)
        self.events.append(event)
        
        # Add event to the OpenTelemetry span
        self._otel_span.add_event(name, attributes)
    
    def add_attribute(self, key: str, value: typing.Any) -> None:
        """
        Adds an attribute to the span.
        
        Args:
            key: The attribute key
            value: The attribute value
        """
        if not self.is_recording:
            logger.warning(f"Cannot add attribute '{key}' to span '{self.name}' as it is no longer recording")
            return
        
        # Store the attribute
        self.attributes[key] = value
        
        # Add attribute to the OpenTelemetry span
        self._otel_span.set_attribute(key, value)
    
    def end(self, attributes: typing.Optional[dict] = None) -> None:
        """
        Ends the span.
        
        Args:
            attributes: Optional attributes to add before ending
        """
        if not self.is_recording:
            logger.warning(f"Cannot end span '{self.name}' as it is already ended")
            return
        
        # Add any final attributes
        if attributes:
            for key, value in attributes.items():
                self.add_attribute(key, value)
        
        # Set end time and record duration metric
        self.end_time = time.time()
        duration_ms = self.get_duration_ms()
        if duration_ms is not None:
            record_metric(
                name="span.duration", 
                value=duration_ms, 
                unit="Milliseconds", 
                dimensions={"span_name": self.name},
                trace_id=self.trace_id
            )
        
        # End the OpenTelemetry span
        self._otel_span.end()
        self.is_recording = False
    
    def record_exception(self, exception: Exception, 
                         attributes: typing.Optional[dict] = None) -> None:
        """
        Records an exception in the span.
        
        Args:
            exception: The exception to record
            attributes: Optional attributes for the exception event
        """
        if not self.is_recording:
            logger.warning(f"Cannot record exception in span '{self.name}' as it is no longer recording")
            return
        
        # Add error attribute and event
        self.add_attribute("error", True)
        
        # Create event attributes
        error_attrs = {
            "exception.type": exception.__class__.__name__,
            "exception.message": str(exception)
        }
        
        # Add any additional attributes
        if attributes:
            error_attrs.update(attributes)
        
        # Add event to span
        self.add_event("exception", error_attrs)
        
        # Record exception in the OpenTelemetry span
        self._otel_span.record_exception(exception)
    
    def get_duration_ms(self) -> typing.Optional[float]:
        """
        Calculates the span duration in milliseconds.
        
        Returns:
            Duration in milliseconds or None if span is still active
        """
        if self.end_time is None:
            return None
        
        return (self.end_time - self.start_time) * 1000.0
    
    def to_dict(self) -> dict:
        """
        Converts the span to a dictionary representation.
        
        Returns:
            Dictionary representation of the span
        """
        result = {
            'id': self.id,
            'trace_id': self.trace_id,
            'name': self.name,
            'attributes': self.attributes,
            'events': [event.to_dict() for event in self.events],
            'start_time': self.start_time,
        }
        
        # Add parent_id if available
        if self.parent_id:
            result['parent_id'] = self.parent_id
        
        # Add end_time and duration if available
        if self.end_time:
            result['end_time'] = self.end_time
            result['duration_ms'] = self.get_duration_ms()
        
        return result
    
    def to_json(self) -> str:
        """
        Converts the span to a JSON string.
        
        Returns:
            JSON string representation of the span
        """
        return json.dumps(self.to_dict())


def setup_tracing(app_config: dict = None) -> None:
    """
    Initializes the distributed tracing system with appropriate configuration.
    
    Args:
        app_config: Application configuration options
    """
    global tracer, TRACING_ENABLED, TRACE_SAMPLE_RATE, OTLP_ENDPOINT
    
    # Check if tracing is enabled in the configuration
    if app_config and 'TRACING_ENABLED' in app_config:
        TRACING_ENABLED = app_config['TRACING_ENABLED']
    
    if not TRACING_ENABLED:
        logger.info("Tracing is disabled. Not setting up tracing system.")
        return
    
    # Update configuration from app_config if provided
    if app_config:
        if 'TRACE_SAMPLE_RATE' in app_config:
            TRACE_SAMPLE_RATE = app_config['TRACE_SAMPLE_RATE']
        if 'OTLP_ENDPOINT' in app_config:
            OTLP_ENDPOINT = app_config['OTLP_ENDPOINT']
    
    # Create a resource identifying the service
    resource = Resource.create({
        ResourceAttributes.SERVICE_NAME: settings.PROJECT_NAME,
        ResourceAttributes.SERVICE_VERSION: "1.0.0",  # TODO: Read from app version
        ResourceAttributes.DEPLOYMENT_ENVIRONMENT: settings.ENVIRONMENT,
    })
    
    # Create a TracerProvider with the resource
    provider = TracerProvider(resource=resource)
    
    # Set up the appropriate exporter
    if OTLP_ENDPOINT:
        # Use OTLP exporter if endpoint is configured
        otlp_exporter = OTLPSpanExporter(endpoint=OTLP_ENDPOINT)
        provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
        logger.info(f"Added OTLP exporter with endpoint {OTLP_ENDPOINT}")
    else:
        # Use console exporter as fallback
        console_exporter = ConsoleSpanExporter()
        provider.add_span_processor(BatchSpanProcessor(console_exporter))
        logger.info("Added console exporter for tracing (no OTLP endpoint configured)")
    
    # Set global tracer provider
    trace.set_tracer_provider(provider)
    
    # Initialize the global tracer
    tracer = trace.get_tracer(settings.PROJECT_NAME)
    
    logger.info(f"Tracing system initialized with sample rate {TRACE_SAMPLE_RATE}")


def get_tracer() -> trace.Tracer:
    """
    Returns the configured tracer instance.
    
    Returns:
        Configured tracer instance
    """
    global tracer
    
    # Initialize tracer if not already initialized
    if tracer is None:
        setup_tracing()
    
    return tracer


def start_span(name: str, attributes: typing.Optional[dict] = None, 
               parent_span_id: typing.Optional[str] = None) -> Span:
    """
    Starts a new tracing span.
    
    Args:
        name: The name of the span
        attributes: Optional attributes for the span
        parent_span_id: Optional parent span ID
        
    Returns:
        New span object
    """
    if not TRACING_ENABLED:
        return None
    
    # Get the tracer
    span_tracer = get_tracer()
    
    # Start a new span
    otel_span = span_tracer.start_span(name)
    span = Span(otel_span, name)
    
    # Set the parent span ID if provided
    if parent_span_id:
        span.parent_id = parent_span_id
    
    # Add attributes if provided
    if attributes:
        for key, value in attributes.items():
            span.add_attribute(key, value)
    
    # Set as current span
    current_span.set(span)
    
    logger.debug(f"Started span '{name}' with trace_id={span.trace_id}, span_id={span.id}")
    return span


def end_span(span: typing.Optional[Span] = None, 
             attributes: typing.Optional[dict] = None) -> None:
    """
    Ends the current or specified span.
    
    Args:
        span: The span to end, or None to use current span
        attributes: Optional attributes to add before ending
    """
    if not TRACING_ENABLED:
        return
    
    # Get the span to end (current span if none specified)
    target_span = span or current_span.get()
    
    if target_span:
        # Add attributes if provided
        if attributes:
            for key, value in attributes.items():
                target_span.add_attribute(key, value)
        
        # End the span
        target_span.end()
        
        # If ending the current span, reset the context variable
        if span is None or span == current_span.get():
            current_span.set(None)
        
        logger.debug(f"Ended span '{target_span.name}' with trace_id={target_span.trace_id}, span_id={target_span.id}")


def add_span_event(name: str, attributes: typing.Optional[dict] = None, 
                   span: typing.Optional[Span] = None) -> bool:
    """
    Adds an event to the current or specified span.
    
    Args:
        name: The event name
        attributes: Optional event attributes
        span: The span to add event to, or None to use current span
        
    Returns:
        True if event was added, False otherwise
    """
    if not TRACING_ENABLED:
        return False
    
    # Get the target span (current span if none specified)
    target_span = span or current_span.get()
    
    if target_span and target_span.is_recording:
        target_span.add_event(name, attributes)
        return True
    
    return False


def add_span_attribute(key: str, value: typing.Any, 
                       span: typing.Optional[Span] = None) -> bool:
    """
    Adds an attribute to the current or specified span.
    
    Args:
        key: The attribute key
        value: The attribute value
        span: The span to add attribute to, or None to use current span
        
    Returns:
        True if attribute was added, False otherwise
    """
    if not TRACING_ENABLED:
        return False
    
    # Get the target span (current span if none specified)
    target_span = span or current_span.get()
    
    if target_span and target_span.is_recording:
        target_span.add_attribute(key, value)
        return True
    
    return False


def get_current_span() -> typing.Optional[Span]:
    """
    Returns the current active span from context.
    
    Returns:
        Current span or None if no active span
    """
    if not TRACING_ENABLED:
        return None
    
    return current_span.get()


def get_current_trace_id() -> typing.Optional[str]:
    """
    Returns the current trace ID for correlation.
    
    Returns:
        Current trace ID or None if no active trace
    """
    if not TRACING_ENABLED:
        return None
    
    span = current_span.get()
    if span:
        return span.trace_id
    
    return None


def trace(name: typing.Optional[str] = None, 
          attributes: typing.Optional[dict] = None):
    """
    Decorator for tracing function execution.
    
    Args:
        name: Optional name for the span (defaults to function name)
        attributes: Optional span attributes
        
    Returns:
        Decorated function with tracing
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Skip tracing if disabled
            if not TRACING_ENABLED:
                return func(*args, **kwargs)
            
            # Get span name (function name if not specified)
            span_name = name or f"{func.__module__}.{func.__name__}"
            
            # Prepare span attributes
            span_attrs = attributes.copy() if attributes else {}
            span_attrs.update({
                "function": func.__name__,
                "module": func.__module__,
            })
            
            # Add argument info if not too complex
            try:
                # Only include simple types in attributes
                arg_info = {}
                for i, arg in enumerate(args):
                    if isinstance(arg, (str, int, float, bool)) or arg is None:
                        arg_info[f"arg_{i}"] = str(arg)
                
                # Add kwargs (simple types only)
                for key, value in kwargs.items():
                    if isinstance(value, (str, int, float, bool)) or value is None:
                        arg_info[f"kwarg_{key}"] = str(value)
                
                if arg_info:
                    span_attrs["arguments"] = json.dumps(arg_info)
            except Exception:
                # If serializing args fails, skip it
                pass
            
            # Start span
            span = start_span(span_name, span_attrs)
            
            try:
                # Execute function
                result = func(*args, **kwargs)
                
                # Add success attribute
                if span:
                    span.add_attribute("success", True)
                
                return result
            except Exception as e:
                # Record exception in span
                if span:
                    span.record_exception(e)
                    span.add_attribute("success", False)
                
                # Re-raise the exception
                raise
            finally:
                # End span
                if span:
                    end_span(span)
        
        return wrapper
    
    # Handle case where decorator is used without parentheses
    if callable(name):
        func = name
        name = None
        return decorator(func)
    
    return decorator


def trace_async(name: typing.Optional[str] = None, 
                attributes: typing.Optional[dict] = None):
    """
    Decorator for tracing async function execution.
    
    Args:
        name: Optional name for the span (defaults to function name)
        attributes: Optional span attributes
        
    Returns:
        Decorated async function with tracing
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Skip tracing if disabled
            if not TRACING_ENABLED:
                return await func(*args, **kwargs)
            
            # Get span name (function name if not specified)
            span_name = name or f"{func.__module__}.{func.__name__}"
            
            # Prepare span attributes
            span_attrs = attributes.copy() if attributes else {}
            span_attrs.update({
                "function": func.__name__,
                "module": func.__module__,
                "async": True,
            })
            
            # Add argument info if not too complex
            try:
                # Only include simple types in attributes
                arg_info = {}
                for i, arg in enumerate(args):
                    if isinstance(arg, (str, int, float, bool)) or arg is None:
                        arg_info[f"arg_{i}"] = str(arg)
                
                # Add kwargs (simple types only)
                for key, value in kwargs.items():
                    if isinstance(value, (str, int, float, bool)) or value is None:
                        arg_info[f"kwarg_{key}"] = str(value)
                
                if arg_info:
                    span_attrs["arguments"] = json.dumps(arg_info)
            except Exception:
                # If serializing args fails, skip it
                pass
            
            # Start span
            span = start_span(span_name, span_attrs)
            
            try:
                # Execute function
                result = await func(*args, **kwargs)
                
                # Add success attribute
                if span:
                    span.add_attribute("success", True)
                
                return result
            except Exception as e:
                # Record exception in span
                if span:
                    span.record_exception(e)
                    span.add_attribute("success", False)
                
                # Re-raise the exception
                raise
            finally:
                # End span
                if span:
                    end_span(span)
        
        return wrapper
    
    # Handle case where decorator is used without parentheses
    if callable(name):
        func = name
        name = None
        return decorator(func)
    
    return decorator


def create_span_from_request(request: Request) -> typing.Optional[Span]:
    """
    Creates a span from an HTTP request.
    
    Args:
        request: The HTTP request
        
    Returns:
        New span for the request
    """
    if not TRACING_ENABLED:
        return None
    
    # Extract trace context from request headers if present
    # This is a simplified implementation - a real-world version would use OpenTelemetry's propagation
    # to extract context from standard headers like traceparent/tracestate
    
    # Create span name from request path
    span_name = f"HTTP {request.method} {request.url.path}"
    
    # Create attributes from request
    attributes = {
        "http.method": request.method,
        "http.url": str(request.url),
        "http.path": request.url.path,
        "http.host": request.url.hostname,
        "http.scheme": request.url.scheme,
    }
    
    # Add query parameters if present
    if request.query_params:
        attributes["http.query_string"] = str(request.query_params)
    
    # Add selected headers (avoiding sensitive ones)
    safe_headers = {
        "user-agent": request.headers.get("user-agent", ""),
        "accept": request.headers.get("accept", ""),
        "content-type": request.headers.get("content-type", ""),
        "content-length": request.headers.get("content-length", ""),
    }
    attributes["http.request.headers"] = json.dumps(safe_headers)
    
    # Create the span
    span = start_span(span_name, attributes)
    
    # Store request ID correlation
    request_id = get_request_id()
    if request_id:
        span.add_attribute("request_id", request_id)
    
    # Store span in request state
    request.state.span = span
    
    return span


class TraceMiddleware(BaseHTTPMiddleware):
    """
    Middleware for tracing HTTP requests and responses.
    """
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """
        Process the request, create a span, and trace the response.
        
        Args:
            request: The HTTP request
            call_next: The next middleware or handler
            
        Returns:
            The HTTP response
        """
        if not TRACING_ENABLED:
            return await call_next(request)
        
        # Create a span for the request
        span = create_span_from_request(request)
        
        # Process the request with the span as current context
        try:
            # Set the span as current in this context
            token = current_span.set(span)
            
            # Process the request
            start_time = time.time()
            response = await call_next(request)
            duration_ms = (time.time() - start_time) * 1000.0
            
            # Add response information to the span
            if span:
                span.add_attribute("http.status_code", response.status_code)
                if "content-type" in response.headers:
                    span.add_attribute("http.response.content_type", response.headers["content-type"])
                span.add_attribute("http.response_time_ms", duration_ms)
                
                # Record success based on status code
                is_success = 200 <= response.status_code < 500
                span.add_attribute("success", is_success)
                
                # Record metrics for the request
                record_metric(
                    name="http.request_duration",
                    value=duration_ms,
                    unit="Milliseconds",
                    dimensions={
                        "path": request.url.path,
                        "method": request.method,
                        "status_code": str(response.status_code)
                    },
                    trace_id=span.trace_id
                )
            
            return response
        except Exception as exc:
            # Record the exception in the span
            if span:
                span.record_exception(exc)
                span.add_attribute("success", False)
            
            # Re-raise the exception
            raise
        finally:
            # Always end the span
            if span:
                end_span(span)
            
            # Reset the context variable
            current_span.reset(token)


class TracingContextManager:
    """
    Context manager for creating and managing spans.
    """
    
    def __init__(self, name: str, attributes: typing.Optional[dict] = None):
        """
        Initializes the tracing context.
        
        Args:
            name: The span name
            attributes: Optional span attributes
        """
        self.name = name
        self.attributes = attributes or {}
        self.span = None
    
    def __enter__(self) -> typing.Optional[Span]:
        """
        Enter the context manager and start a span.
        
        Returns:
            The created span
        """
        self.span = start_span(self.name, self.attributes)
        return self.span
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        """
        Exit the context manager and end the span.
        
        Args:
            exc_type: Exception type if an exception occurred
            exc_val: Exception value if an exception occurred
            exc_tb: Exception traceback if an exception occurred
            
        Returns:
            False to allow exception propagation
        """
        if self.span:
            # Record exception if one occurred
            if exc_val is not None:
                self.span.record_exception(exc_val)
                self.span.add_attribute("success", False)
            else:
                self.span.add_attribute("success", True)
            
            # End the span
            end_span(self.span)
        
        # Don't suppress the exception
        return False