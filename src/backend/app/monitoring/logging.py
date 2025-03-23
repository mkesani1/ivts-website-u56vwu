import logging
import typing
import datetime
import json
import functools

from ..core.logging import get_logger, ContextualLogger
from ..core.config import settings
from ..utils.logging_utils import mask_sensitive_data, enrich_log_context

# Logger name constants
MONITORING_LOGGER_NAME = "monitoring"
METRICS_LOGGER_NAME = "monitoring.metrics"
TRACING_LOGGER_NAME = "monitoring.tracing"
PERFORMANCE_LOGGER_NAME = "monitoring.performance"
ALERT_LOGGER_NAME = "monitoring.alerts"
DEFAULT_MONITORING_LOG_LEVEL = logging.INFO

def get_monitoring_logger(name=None, context=None):
    """
    Returns a specialized logger for monitoring components with appropriate context
    
    Args:
        name (str): Optional name to append to the base monitoring logger name
        context (dict): Additional context to include in all log entries
        
    Returns:
        ContextualLogger: Configured monitoring logger with context
    """
    logger_name = MONITORING_LOGGER_NAME
    if name:
        logger_name = f"{MONITORING_LOGGER_NAME}.{name}"
    
    base_logger = get_logger(logger_name)
    
    # Create default monitoring context
    default_context = {
        "component": name or "monitoring",
        "timestamp": datetime.datetime.utcnow().isoformat()
    }
    
    # Merge with provided context
    merged_context = default_context
    if context:
        merged_context.update(context)
    
    # Enrich context with standard metadata
    enriched_context = enrich_log_context(merged_context)
    
    return ContextualLogger(base_logger, enriched_context)

def get_metrics_logger(context=None):
    """
    Returns a specialized logger for metrics collection with appropriate context
    
    Args:
        context (dict): Additional context to include in all log entries
        
    Returns:
        ContextualLogger: Configured metrics logger with context
    """
    metrics_context = {"component_type": "metrics"}
    if context:
        metrics_context.update(context)
    
    return get_monitoring_logger(METRICS_LOGGER_NAME.split(".")[-1], metrics_context)

def get_tracing_logger(context=None):
    """
    Returns a specialized logger for distributed tracing with appropriate context
    
    Args:
        context (dict): Additional context to include in all log entries
        
    Returns:
        ContextualLogger: Configured tracing logger with context
    """
    tracing_context = {"component_type": "tracing"}
    if context:
        tracing_context.update(context)
    
    return get_monitoring_logger(TRACING_LOGGER_NAME.split(".")[-1], tracing_context)

def get_performance_logger(context=None):
    """
    Returns a specialized logger for performance monitoring with appropriate context
    
    Args:
        context (dict): Additional context to include in all log entries
        
    Returns:
        ContextualLogger: Configured performance logger with context
    """
    performance_context = {"component_type": "performance"}
    if context:
        performance_context.update(context)
    
    return get_monitoring_logger(PERFORMANCE_LOGGER_NAME.split(".")[-1], performance_context)

def get_alert_logger(context=None):
    """
    Returns a specialized logger for system alerts with appropriate context
    
    Args:
        context (dict): Additional context to include in all log entries
        
    Returns:
        ContextualLogger: Configured alert logger with context
    """
    alert_context = {"component_type": "alert"}
    if context:
        alert_context.update(context)
    
    return get_monitoring_logger(ALERT_LOGGER_NAME.split(".")[-1], alert_context)

def configure_monitoring_loggers(log_level=None):
    """
    Configures all monitoring loggers with appropriate log levels and handlers
    
    Args:
        log_level (str): Optional log level to use, defaults to settings.LOG_LEVEL or INFO
    """
    # Determine log level
    level = log_level or settings.LOG_LEVEL or DEFAULT_MONITORING_LOG_LEVEL
    if isinstance(level, str):
        level = getattr(logging, level.upper(), DEFAULT_MONITORING_LOG_LEVEL)
    
    # Configure main monitoring logger
    monitoring_logger = get_logger(MONITORING_LOGGER_NAME)
    monitoring_logger.setLevel(level)
    
    # Configure specialized loggers
    metrics_logger = get_logger(METRICS_LOGGER_NAME)
    metrics_logger.setLevel(level)
    
    tracing_logger = get_logger(TRACING_LOGGER_NAME)
    tracing_logger.setLevel(level)
    
    performance_logger = get_logger(PERFORMANCE_LOGGER_NAME)
    performance_logger.setLevel(level)
    
    alert_logger = get_logger(ALERT_LOGGER_NAME)
    alert_logger.setLevel(level)
    
    # Log initialization
    monitoring_logger.info(f"Monitoring loggers initialized with level {logging.getLevelName(level)}")

def log_metric(name, value, unit=None, metric_type="gauge", dimensions=None, context=None):
    """
    Logs a metric event with appropriate context and formatting
    
    Args:
        name (str): Metric name
        value (float): Metric value
        unit (str): Optional unit of measurement
        metric_type (str): Type of metric (gauge, counter, timer, etc.)
        dimensions (dict): Optional dimensions for the metric
        context (dict): Additional context to include
    """
    logger = get_metrics_logger()
    
    # Create metric data structure
    metric_data = {
        "metric_name": name,
        "metric_value": value,
        "metric_type": metric_type
    }
    
    if unit:
        metric_data["unit"] = unit
        
    if dimensions:
        metric_data["dimensions"] = dimensions
    
    # Mask any sensitive data
    metric_data = mask_sensitive_data(metric_data)
    
    # Create combined context
    combined_context = metric_data
    if context:
        combined_context.update(context)
    
    # Log the metric
    logger.info(f"METRIC: {name}={value}{' '+unit if unit else ''}", extra=combined_context)

def log_trace(trace_id, span_id, parent_span_id=None, name=None, event_type="span", attributes=None, context=None):
    """
    Logs a trace event with appropriate context and formatting
    
    Args:
        trace_id (str): Trace identifier
        span_id (str): Span identifier
        parent_span_id (str): Optional parent span identifier
        name (str): Optional span/operation name
        event_type (str): Type of trace event (span, annotation, etc.)
        attributes (dict): Optional span attributes
        context (dict): Additional context to include
    """
    logger = get_tracing_logger()
    
    # Create trace data structure
    trace_data = {
        "trace_id": trace_id,
        "span_id": span_id,
        "event_type": event_type
    }
    
    if parent_span_id:
        trace_data["parent_span_id"] = parent_span_id
        
    if name:
        trace_data["name"] = name
        
    if attributes:
        trace_data["attributes"] = attributes
    
    # Mask any sensitive data
    trace_data = mask_sensitive_data(trace_data)
    
    # Create combined context
    combined_context = trace_data
    if context:
        combined_context.update(context)
    
    # Log the trace
    logger.info(f"TRACE: {trace_id}/{span_id}", extra=combined_context)

def log_performance(operation, duration, success=True, attributes=None, context=None):
    """
    Logs a performance event with appropriate context and formatting
    
    Args:
        operation (str): Operation or method name
        duration (float): Duration in milliseconds
        success (bool): Whether the operation succeeded
        attributes (dict): Optional attributes for additional details
        context (dict): Additional context to include
    """
    logger = get_performance_logger()
    
    # Create performance data structure
    perf_data = {
        "operation": operation,
        "duration_ms": duration,
        "success": success
    }
    
    if attributes:
        perf_data["attributes"] = attributes
    
    # Mask any sensitive data
    perf_data = mask_sensitive_data(perf_data)
    
    # Create combined context
    combined_context = perf_data
    if context:
        combined_context.update(context)
    
    # Log the performance data
    logger.info(f"PERF: {operation} took {duration}ms", extra=combined_context)

def log_alert(alert_name, severity, message, details=None, context=None):
    """
    Logs a system alert with appropriate context and formatting
    
    Args:
        alert_name (str): Alert identifier
        severity (str): Alert severity (critical, error, warning, info)
        message (str): Alert message
        details (dict): Optional alert details
        context (dict): Additional context to include
    """
    logger = get_alert_logger()
    
    # Create alert data structure
    alert_data = {
        "alert_name": alert_name,
        "severity": severity,
        "message": message
    }
    
    if details:
        alert_data["details"] = details
    
    # Mask any sensitive data
    alert_data = mask_sensitive_data(alert_data)
    
    # Create combined context
    combined_context = alert_data
    if context:
        combined_context.update(context)
    
    # Determine log level based on severity
    log_level = logging.INFO
    if severity.lower() == "critical":
        log_level = logging.CRITICAL
    elif severity.lower() == "error":
        log_level = logging.ERROR
    elif severity.lower() == "warning":
        log_level = logging.WARNING
    
    # Log the alert at the appropriate level
    if log_level == logging.CRITICAL:
        logger.critical(f"ALERT: {alert_name} - {message}", extra=combined_context)
    elif log_level == logging.ERROR:
        logger.error(f"ALERT: {alert_name} - {message}", extra=combined_context)
    elif log_level == logging.WARNING:
        logger.warning(f"ALERT: {alert_name} - {message}", extra=combined_context)
    else:
        logger.info(f"ALERT: {alert_name} - {message}", extra=combined_context)

class MonitoringLogFilter(logging.Filter):
    """
    Log filter that adds monitoring-specific context to log records
    """
    
    def __init__(self, component_type):
        """
        Initializes the monitoring log filter
        
        Args:
            component_type (str): The type of monitoring component (metrics, tracing, performance, alert)
        """
        super().__init__()
        self.component_type = component_type
    
    def filter(self, record):
        """
        Adds monitoring context to the log record
        
        Args:
            record (logging.LogRecord): The log record
            
        Returns:
            bool: Always returns True to include the record
        """
        # Add component type
        record.component_type = self.component_type
        
        # Add timestamp if not present
        if not hasattr(record, "timestamp"):
            record.timestamp = datetime.datetime.utcnow().isoformat()
            
        # Add environment if not present
        if not hasattr(record, "environment"):
            record.environment = settings.ENVIRONMENT
        
        # Always include the record
        return True

class PerformanceLoggingContext:
    """
    Context manager for logging performance of code blocks
    """
    
    def __init__(self, operation, attributes=None, context=None):
        """
        Initializes the performance logging context
        
        Args:
            operation (str): Name of the operation being measured
            attributes (dict): Optional attributes for additional context
            context (dict): Additional logging context
        """
        self.operation = operation
        self.attributes = attributes or {}
        self.context = context or {}
        self.start_time = None
    
    def __enter__(self):
        """
        Enter the context manager and start timing
        
        Returns:
            PerformanceLoggingContext: Self reference
        """
        self.start_time = datetime.datetime.now()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit the context manager, calculate duration, and log performance
        
        Args:
            exc_type: Exception type if an exception occurred
            exc_val: Exception value if an exception occurred
            exc_tb: Exception traceback if an exception occurred
            
        Returns:
            bool: False to allow exception propagation
        """
        end_time = datetime.datetime.now()
        duration_ms = (end_time - self.start_time).total_seconds() * 1000
        success = exc_type is None
        
        log_performance(
            self.operation,
            duration_ms,
            success,
            self.attributes,
            self.context
        )
        
        # Don't suppress exceptions
        return False

class log_performance_decorator:
    """
    Decorator for logging performance of function calls
    """
    
    def __init__(self, operation=None, attributes=None, context=None):
        """
        Initializes the performance logging decorator
        
        Args:
            operation (str): Optional operation name (defaults to function name)
            attributes (dict): Optional attributes for additional context
            context (dict): Additional logging context
        """
        self.operation = operation
        self.attributes = attributes or {}
        self.context = context or {}
    
    def __call__(self, func):
        """
        Wraps the function with performance logging
        
        Args:
            func: The function to wrap
            
        Returns:
            callable: Wrapped function with performance logging
        """
        operation = self.operation or func.__name__
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with PerformanceLoggingContext(operation, self.attributes, self.context):
                return func(*args, **kwargs)
        
        return wrapper