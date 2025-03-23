import logging
import logging.config
import logging.handlers
import typing
import os
import sys
import json
import datetime
import uuid

from ..core.config import settings

# Default logging configuration
DEFAULT_LOG_LEVEL = logging.INFO
DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Log record attributes to exclude from JSON output
LOG_RECORD_ATTRS_TO_IGNORE = [
    "args", "asctime", "created", "exc_info", "exc_text", "filename",
    "funcName", "id", "levelname", "levelno", "lineno", "module", "msecs",
    "message", "msg", "name", "pathname", "process", "processName",
    "relativeCreated", "stack_info", "thread", "threadName"
]

# Flag to track if logging has been initialized
LOGGER_INITIALIZED = False


class JsonFormatter(logging.Formatter):
    """
    Custom log formatter that outputs logs in JSON format for structured logging
    """
    def __init__(self, fmt=None, datefmt=None):
        """
        Initializes the JSON formatter with format string
        
        Args:
            fmt (str): Format string (not used for JSON but required by parent)
            datefmt (str): Date format string for timestamps
        """
        super().__init__(fmt, datefmt)
        self.fmt = fmt
        self.datefmt = datefmt
    
    def format(self, record):
        """
        Formats the log record as a JSON string
        
        Args:
            record (logging.LogRecord): The log record to format
            
        Returns:
            str: JSON formatted log entry
        """
        # Create a base log object
        log_object = {
            "timestamp": datetime.datetime.fromtimestamp(record.created).strftime(
                self.datefmt or DEFAULT_DATE_FORMAT
            ),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "environment": settings.ENVIRONMENT,
            "service": settings.PROJECT_NAME,
        }
        
        # Add request_id if available
        if hasattr(record, "request_id"):
            log_object["request_id"] = record.request_id
            
        # Add exception info if present
        if record.exc_info:
            log_object["exception"] = self.formatException(record.exc_info)
            
        # Add any extra attributes from the record
        for key, value in record.__dict__.items():
            if key not in LOG_RECORD_ATTRS_TO_IGNORE:
                log_object[key] = value
                
        return json.dumps(log_object)

    def add_fields(self, log_record, record, message_dict):
        """
        Adds additional fields to the log record
        
        Args:
            log_record (dict): The log record dictionary
            record (logging.LogRecord): The log record
            message_dict (dict): Additional message dictionary
        """
        # Add standard fields
        log_record["timestamp"] = datetime.datetime.utcnow().strftime(
            self.datefmt or DEFAULT_DATE_FORMAT
        )
        log_record["level"] = record.levelname
        log_record["name"] = record.name
        log_record["message"] = record.getMessage()
        
        # Add any extra fields from message_dict
        if message_dict:
            for key, value in message_dict.items():
                log_record[key] = value
                
        # Add any extra attributes from the record
        for key, value in record.__dict__.items():
            if key not in LOG_RECORD_ATTRS_TO_IGNORE:
                log_record[key] = value


class RequestIdFilter(logging.Filter):
    """
    Log filter that adds request ID to all log records
    """
    def __init__(self, request_id=None):
        """
        Initializes the request ID filter
        
        Args:
            request_id (str): The request ID to use, or None to generate one
        """
        super().__init__()
        self.request_id = request_id or str(uuid.uuid4())
        
    def filter(self, record):
        """
        Adds request ID to the log record
        
        Args:
            record (logging.LogRecord): The log record
            
        Returns:
            bool: Always returns True to include the record
        """
        record.request_id = self.request_id
        return True


class ContextualLogger:
    """
    Logger wrapper that adds contextual information to all log entries
    """
    def __init__(self, logger, context=None):
        """
        Initializes the contextual logger with a base logger and context
        
        Args:
            logger (logging.Logger): The base logger instance
            context (dict): The context dictionary to add to all log entries
        """
        self._logger = logger
        self.context = context or {}
        
    def debug(self, msg, extra=None):
        """
        Logs a message with DEBUG level with context
        
        Args:
            msg (str): The message to log
            extra (dict): Extra context to add to this log entry
        """
        merged_extra = {**self.context}
        if extra:
            merged_extra.update(extra)
        self._logger.debug(msg, extra=merged_extra)
        
    def info(self, msg, extra=None):
        """
        Logs a message with INFO level with context
        
        Args:
            msg (str): The message to log
            extra (dict): Extra context to add to this log entry
        """
        merged_extra = {**self.context}
        if extra:
            merged_extra.update(extra)
        self._logger.info(msg, extra=merged_extra)
        
    def warning(self, msg, extra=None):
        """
        Logs a message with WARNING level with context
        
        Args:
            msg (str): The message to log
            extra (dict): Extra context to add to this log entry
        """
        merged_extra = {**self.context}
        if extra:
            merged_extra.update(extra)
        self._logger.warning(msg, extra=merged_extra)
        
    def error(self, msg, extra=None, exc_info=None):
        """
        Logs a message with ERROR level with context
        
        Args:
            msg (str): The message to log
            extra (dict): Extra context to add to this log entry
            exc_info (Exception): Exception information to include
        """
        merged_extra = {**self.context}
        if extra:
            merged_extra.update(extra)
        self._logger.error(msg, extra=merged_extra, exc_info=exc_info)
        
    def critical(self, msg, extra=None, exc_info=None):
        """
        Logs a message with CRITICAL level with context
        
        Args:
            msg (str): The message to log
            extra (dict): Extra context to add to this log entry
            exc_info (Exception): Exception information to include
        """
        merged_extra = {**self.context}
        if extra:
            merged_extra.update(extra)
        self._logger.critical(msg, extra=merged_extra, exc_info=exc_info)
        
    def with_context(self, additional_context):
        """
        Creates a new ContextualLogger with additional context
        
        Args:
            additional_context (dict): Additional context to add
            
        Returns:
            ContextualLogger: New logger instance with merged context
        """
        new_context = {**self.context, **additional_context}
        return ContextualLogger(self._logger, new_context)


def setup_logging(log_level=None, log_file=None):
    """
    Configures the application-wide logging system based on settings
    
    Args:
        log_level (str): Override the log level from settings
        log_file (str): Override the log file path from settings
    """
    global LOGGER_INITIALIZED
    
    if LOGGER_INITIALIZED:
        return
    
    # Determine log level
    log_level = log_level or settings.LOG_LEVEL or "INFO"
    numeric_level = getattr(logging, log_level.upper(), DEFAULT_LOG_LEVEL)
    
    # Determine log file path
    log_file = log_file or settings.LOG_FILE
    
    # Create log directory if it doesn't exist
    if log_file:
        log_dir = os.path.dirname(os.path.abspath(log_file))
        if not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Remove any existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    formatter = logging.Formatter(DEFAULT_LOG_FORMAT, DEFAULT_DATE_FORMAT)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Create file handler if log file is specified
    if log_file:
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=10485760, backupCount=10  # 10MB files, keep 10 backups
        )
        file_handler.setLevel(numeric_level)
        json_formatter = JsonFormatter(None, DEFAULT_DATE_FORMAT)
        file_handler.setFormatter(json_formatter)
        root_logger.addHandler(file_handler)
    
    LOGGER_INITIALIZED = True
    
    # Log initialization message
    logger = logging.getLogger("logging")
    logger.info(
        f"Logging initialized with level {log_level}" +
        (f" to file {log_file}" if log_file else "")
    )


def get_logger(name):
    """
    Returns a configured logger for the specified name
    
    Args:
        name (str): The logger name
        
    Returns:
        logging.Logger: Configured logger instance
    """
    global LOGGER_INITIALIZED
    
    if not LOGGER_INITIALIZED:
        setup_logging()
    
    return logging.getLogger(name)


def get_request_id():
    """
    Generates or retrieves a unique identifier for request correlation
    
    Returns:
        str: Unique request identifier
    """
    return str(uuid.uuid4())


def configure_logger(logger_name, log_level, propagate=True):
    """
    Configures a specific logger with custom settings
    
    Args:
        logger_name (str): The logger name
        log_level (str): The log level
        propagate (bool): Whether to propagate to parent loggers
        
    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger(logger_name)
    logger.setLevel(getattr(logging, log_level.upper()))
    logger.propagate = propagate
    return logger