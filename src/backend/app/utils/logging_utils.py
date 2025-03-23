import logging
import typing
import re
import json
import datetime
import functools
import inspect

from ..core.logging import get_logger, get_request_id
from ..core.config import settings

# Global logger for this module
logger = get_logger(__name__)

# Patterns for identifying sensitive data that should be masked in logs
SENSITIVE_PATTERNS = [
    re.compile(r'password', re.IGNORECASE),
    re.compile(r'secret', re.IGNORECASE),
    re.compile(r'token', re.IGNORECASE),
    re.compile(r'key', re.IGNORECASE),
    re.compile(r'auth', re.IGNORECASE),
    re.compile(r'credit_?card', re.IGNORECASE),
    re.compile(r'\b(?:\d[ -]*?){13,16}\b'),  # Credit card number pattern
    re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')  # Email pattern
]

# Replacement string for masked sensitive data
MASK_REPLACEMENT = '*****'


def mask_sensitive_data(data):
    """
    Masks sensitive data in log messages and structured data.
    
    Args:
        data: The data to mask (str, dict, list, etc.)
        
    Returns:
        The masked data of the same type as the input
    """
    if data is None:
        return None
    
    # Handle strings
    if isinstance(data, str):
        masked = data
        for pattern in SENSITIVE_PATTERNS:
            masked = pattern.sub(MASK_REPLACEMENT, masked)
        return masked
    
    # Handle dictionaries
    elif isinstance(data, dict):
        masked_dict = {}
        for key, value in data.items():
            # Check if key suggests sensitive data
            key_str = str(key).lower() if hasattr(key, 'lower') else str(key).lower()
            if any(pattern.search(key_str) for pattern in SENSITIVE_PATTERNS):
                masked_dict[key] = MASK_REPLACEMENT
            else:
                masked_dict[key] = mask_sensitive_data(value)
        return masked_dict
    
    # Handle lists or tuples
    elif isinstance(data, (list, tuple)):
        return type(data)(mask_sensitive_data(item) for item in data)
    
    # Return other types as is
    return data


def enrich_log_context(context=None, additional_context=None):
    """
    Enriches log context with standard metadata.
    
    Args:
        context (dict): Base context dictionary
        additional_context (dict): Additional context to include
        
    Returns:
        dict: Enriched context dictionary
    """
    # Initialize context if None
    enriched_context = context.copy() if context else {}
    
    # Add standard fields
    enriched_context.update({
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "environment": settings.ENVIRONMENT,
        "service": settings.PROJECT_NAME,
    })
    
    # Add request_id if available
    try:
        request_id = get_request_id()
        if request_id:
            enriched_context["request_id"] = request_id
    except Exception:
        # Fail silently if request_id is not available
        pass
    
    # Add additional context if provided
    if additional_context:
        enriched_context.update(additional_context)
    
    # Mask sensitive data
    return mask_sensitive_data(enriched_context)


def get_context_logger(name, context=None):
    """
    Returns a logger with predefined context.
    
    Args:
        name (str): Logger name
        context (dict): Context dictionary to add to all log entries
        
    Returns:
        ContextLogger: Logger with predefined context
    """
    base_logger = get_logger(name)
    return ContextLogger(base_logger, context)


def log_function_call(func):
    """
    Decorator to log function calls with arguments and results.
    
    Args:
        func (callable): The function to decorate
        
    Returns:
        callable: Wrapped function with logging
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Get logger for the function's module
        func_logger = get_logger(func.__module__)
        
        # Prepare arguments for logging (mask sensitive data)
        safe_args = mask_sensitive_data(args)
        safe_kwargs = mask_sensitive_data(kwargs)
        
        # Log function call
        func_logger.debug(
            f"Calling {func.__name__}",
            extra={
                "function": func.__name__,
                "module": func.__module__,
                "args": str(safe_args),
                "kwargs": str(safe_kwargs)
            }
        )
        
        try:
            # Call the function
            result = func(*args, **kwargs)
            
            # Mask sensitive data in result before logging
            safe_result = mask_sensitive_data(result)
            
            # Log successful completion
            func_logger.debug(
                f"Completed {func.__name__}",
                extra={
                    "function": func.__name__,
                    "module": func.__module__,
                    "result": str(safe_result)
                }
            )
            
            return result
        except Exception as e:
            # Log the error
            func_logger.error(
                f"Error in {func.__name__}: {str(e)}",
                extra={
                    "function": func.__name__,
                    "module": func.__module__,
                    "error": str(e),
                    "error_type": type(e).__name__
                },
                exc_info=True
            )
            # Re-raise the exception
            raise
    
    return wrapper


def format_exception(exc, include_traceback=False):
    """
    Formats exception information for logging.
    
    Args:
        exc (Exception): The exception to format
        include_traceback (bool): Whether to include traceback information
        
    Returns:
        dict: Formatted exception information
    """
    if exc is None:
        return None
    
    # Extract basic exception information
    exc_type = type(exc).__name__
    exc_msg = str(exc)
    exc_module = type(exc).__module__
    
    # Create the base exception info
    exc_info = {
        "type": exc_type,
        "message": exc_msg,
        "module": exc_module
    }
    
    # Add traceback if requested
    if include_traceback:
        import traceback
        exc_info["traceback"] = traceback.format_exc()
    
    return exc_info


def create_audit_log(action, entity_type, entity_id, changes=None, user_id=None):
    """
    Creates a standardized audit log entry.
    
    Args:
        action (str): The action performed (e.g., "create", "update", "delete")
        entity_type (str): The type of entity affected (e.g., "user", "file")
        entity_id (str): The ID of the affected entity
        changes (dict): Dictionary of changes made
        user_id (str): ID of the user who performed the action
        
    Returns:
        dict: Audit log entry
    """
    audit_log = {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "action": action,
        "entity_type": entity_type,
        "entity_id": entity_id,
    }
    
    if user_id:
        audit_log["user_id"] = user_id
    
    if changes:
        audit_log["changes"] = mask_sensitive_data(changes)
    
    return audit_log


def log_with_context(logger, level, msg, context=None, exc_info=None):
    """
    Logs a message with additional context.
    
    Args:
        logger (logging.Logger): The logger to use
        level (int): The log level
        msg (str): The log message
        context (dict): Additional context
        exc_info (Exception): Exception information
    """
    # Enrich context with standard metadata
    enriched_context = enrich_log_context(context)
    
    # Add exception information if provided
    if exc_info:
        enriched_context["exception"] = format_exception(exc_info, include_traceback=True)
    
    # Log the message with enriched context
    logger.log(level, msg, extra=enriched_context)


def setup_module_logger(module_name, log_level="INFO", propagate=True):
    """
    Sets up a logger for a module with specific configuration.
    
    Args:
        module_name (str): The module name
        log_level (str): The log level
        propagate (bool): Whether to propagate to parent loggers
        
    Returns:
        logging.Logger: Configured logger
    """
    logger = get_logger(module_name)
    logger.setLevel(getattr(logging, log_level.upper()))
    logger.propagate = propagate
    return logger


class ContextLogger:
    """
    Logger wrapper that adds contextual information to log entries.
    """
    
    def __init__(self, logger, context=None):
        """
        Initializes the ContextLogger with a logger and context.
        
        Args:
            logger (logging.Logger): The logger instance
            context (dict): The context dictionary
        """
        self._logger = logger
        self._context = context or {}
    
    def debug(self, msg, extra=None):
        """
        Logs a debug message with context.
        
        Args:
            msg (str): The message to log
            extra (dict): Additional context
        """
        context = self._context.copy()
        if extra:
            context.update(extra)
        log_with_context(self._logger, logging.DEBUG, msg, context)
    
    def info(self, msg, extra=None):
        """
        Logs an info message with context.
        
        Args:
            msg (str): The message to log
            extra (dict): Additional context
        """
        context = self._context.copy()
        if extra:
            context.update(extra)
        log_with_context(self._logger, logging.INFO, msg, context)
    
    def warning(self, msg, extra=None):
        """
        Logs a warning message with context.
        
        Args:
            msg (str): The message to log
            extra (dict): Additional context
        """
        context = self._context.copy()
        if extra:
            context.update(extra)
        log_with_context(self._logger, logging.WARNING, msg, context)
    
    def error(self, msg, extra=None, exc_info=None):
        """
        Logs an error message with context.
        
        Args:
            msg (str): The message to log
            extra (dict): Additional context
            exc_info (Exception): Exception information
        """
        context = self._context.copy()
        if extra:
            context.update(extra)
        log_with_context(self._logger, logging.ERROR, msg, context, exc_info)
    
    def critical(self, msg, extra=None, exc_info=None):
        """
        Logs a critical message with context.
        
        Args:
            msg (str): The message to log
            extra (dict): Additional context
            exc_info (Exception): Exception information
        """
        context = self._context.copy()
        if extra:
            context.update(extra)
        log_with_context(self._logger, logging.CRITICAL, msg, context, exc_info)
    
    def with_context(self, additional_context):
        """
        Creates a new ContextLogger with additional context.
        
        Args:
            additional_context (dict): Additional context
            
        Returns:
            ContextLogger: New logger with combined context
        """
        new_context = {**self._context, **additional_context}
        return ContextLogger(self._logger, new_context)
    
    def bind(self, **kwargs):
        """
        Adds key-value pairs to the logger context.
        
        Args:
            **kwargs: Key-value pairs to add to context
            
        Returns:
            ContextLogger: Self reference with updated context
        """
        self._context.update(kwargs)
        return self


class SensitiveDataFilter(logging.Filter):
    """
    Log filter that masks sensitive data in log records.
    """
    
    def __init__(self):
        """
        Initializes the SensitiveDataFilter.
        """
        super().__init__()
    
    def filter(self, record):
        """
        Filters log record by masking sensitive data.
        
        Args:
            record (logging.LogRecord): The log record
            
        Returns:
            bool: Always returns True to include the record
        """
        # Mask message if present
        if hasattr(record, 'msg') and isinstance(record.msg, str):
            record.msg = mask_sensitive_data(record.msg)
        
        # Mask args if present
        if hasattr(record, 'args') and record.args:
            args_list = list(record.args)
            for i, arg in enumerate(args_list):
                args_list[i] = mask_sensitive_data(arg)
            record.args = tuple(args_list)
        
        # Always include the record
        return True


class LogMetrics:
    """
    Utility class for tracking and reporting logging metrics.
    """
    
    def __init__(self):
        """
        Initializes the LogMetrics tracker.
        """
        self._counters = {
            'DEBUG': 0,
            'INFO': 0,
            'WARNING': 0,
            'ERROR': 0,
            'CRITICAL': 0
        }
        
        self._levels = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
    
    def increment(self, level):
        """
        Increments the counter for a specific log level.
        
        Args:
            level (int): The log level
        """
        # Convert numeric level to level name if needed
        if isinstance(level, int):
            for name, num_level in self._levels.items():
                if num_level == level:
                    level = name
                    break
        
        # Increment the counter if level is valid
        if level in self._counters:
            self._counters[level] += 1
    
    def get_metrics(self):
        """
        Returns the current logging metrics.
        
        Returns:
            dict: Log count metrics by level
        """
        metrics = self._counters.copy()
        metrics['TOTAL'] = sum(self._counters.values())
        return metrics
    
    def reset(self):
        """
        Resets all log counters to zero.
        """
        for level in self._counters:
            self._counters[level] = 0


class LoggingContext:
    """
    Context manager for temporarily changing log levels.
    """
    
    def __init__(self, logger, level):
        """
        Initializes the logging context.
        
        Args:
            logger (logging.Logger): The logger instance
            level (int): The temporary log level
        """
        self._logger = logger
        self._temp_level = level
        self._original_level = None
    
    def __enter__(self):
        """
        Enters the context and changes the log level.
        
        Returns:
            LoggingContext: Self reference
        """
        self._original_level = self._logger.level
        self._logger.setLevel(self._temp_level)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exits the context and restores the original log level.
        
        Args:
            exc_type (type): Exception type
            exc_val (Exception): Exception value
            exc_tb (traceback): Exception traceback
            
        Returns:
            bool: False to allow exception propagation
        """
        self._logger.setLevel(self._original_level)
        return False  # Don't suppress exceptions