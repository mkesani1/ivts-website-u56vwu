import time
import datetime
import uuid
import typing
import functools
import contextlib
import threading
import enum
import boto3
import psutil

from ..core.config import settings
from ..core.logging import get_logger
from .logging import get_metrics_logger

# Logger for this module
logger = get_logger(__name__)

# Configuration flags
METRICS_ENABLED = getattr(settings, 'METRICS_ENABLED', True)
CLOUDWATCH_ENABLED = getattr(settings, 'CLOUDWATCH_ENABLED', False)
METRICS_NAMESPACE = f"{settings.PROJECT_NAME}-{settings.ENVIRONMENT}"
DEFAULT_DIMENSIONS = {"service": settings.PROJECT_NAME, "environment": settings.ENVIRONMENT}


class AlertSeverity(enum.Enum):
    """Enum defining severity levels for metric-based alerts"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class Metric:
    """Class representing a single metric data point"""
    
    def __init__(self, name, value, unit, dimensions=None, metric_type="gauge"):
        """Initializes a new metric
        
        Args:
            name (str): The name of the metric
            value (float): The numeric value of the metric
            unit (str): The unit of measurement
            dimensions (dict): Additional dimensions for the metric
            metric_type (str): Type of metric (gauge, counter, timing)
        """
        self.id = str(uuid.uuid4())
        self.name = name
        self.value = value
        self.unit = unit
        self.dimensions = dimensions or {}
        self.metric_type = metric_type
        self.timestamp = datetime.datetime.utcnow()
        self.trace_id = None
        
    def add_dimension(self, key, value):
        """Adds a dimension to the metric
        
        Args:
            key (str): Dimension key
            value (str): Dimension value
        """
        self.dimensions[key] = value
        
    def set_trace_id(self, trace_id):
        """Sets the trace ID for correlation with distributed tracing
        
        Args:
            trace_id (str): The trace ID to associate with this metric
        """
        self.trace_id = trace_id
        
    def to_dict(self):
        """Converts the metric to a dictionary representation
        
        Returns:
            dict: Dictionary representation of the metric
        """
        return {
            "id": self.id,
            "name": self.name,
            "value": self.value,
            "unit": self.unit,
            "dimensions": self.dimensions,
            "metric_type": self.metric_type,
            "timestamp": self.timestamp.isoformat(),
            "trace_id": self.trace_id
        }


class MetricsRegistry:
    """Singleton class that maintains a registry of metrics"""
    
    _instance = None
    
    def __init__(self):
        """Initializes the MetricsRegistry singleton"""
        self._metrics = []
        self._counters = {}
        self._lock = threading.Lock()
        
    @classmethod
    def get_instance(cls):
        """Returns the singleton instance of MetricsRegistry
        
        Returns:
            MetricsRegistry: Singleton instance
        """
        if cls._instance is None:
            cls._instance = MetricsRegistry()
        return cls._instance
        
    def register_metric(self, metric):
        """Registers a metric in the registry
        
        Args:
            metric (Metric): The metric to register
            
        Returns:
            str: Metric ID
        """
        with self._lock:
            self._metrics.append(metric)
            
            # If this is a counter, update the counter value
            if metric.metric_type == "counter":
                counter_key = f"{metric.name}|{str(sorted([(k, v) for k, v in metric.dimensions.items()]))}"
                current_value = self._counters.get(counter_key, 0)
                self._counters[counter_key] = current_value + metric.value
                
            return metric.id
            
    def get_metrics(self, name=None, metric_type=None, dimensions=None, 
                   start_time=None, end_time=None):
        """Retrieves all metrics, optionally filtered
        
        Args:
            name (str): Filter by metric name
            metric_type (str): Filter by metric type
            dimensions (dict): Filter by dimensions
            start_time (datetime): Filter by start time
            end_time (datetime): Filter by end time
            
        Returns:
            list: List of Metric objects matching filters
        """
        with self._lock:
            # Start with all metrics
            filtered_metrics = self._metrics
            
            # Apply name filter
            if name:
                filtered_metrics = [m for m in filtered_metrics if m.name == name]
                
            # Apply metric type filter
            if metric_type:
                filtered_metrics = [m for m in filtered_metrics if m.metric_type == metric_type]
                
            # Apply dimensions filter
            if dimensions:
                filtered_metrics = [
                    m for m in filtered_metrics if all(
                        k in m.dimensions and m.dimensions[k] == v 
                        for k, v in dimensions.items()
                    )
                ]
                
            # Apply time range filter
            if start_time:
                filtered_metrics = [m for m in filtered_metrics if m.timestamp >= start_time]
                
            if end_time:
                filtered_metrics = [m for m in filtered_metrics if m.timestamp <= end_time]
                
            return filtered_metrics
            
    def get_counter_value(self, name, dimensions=None):
        """Gets the current value of a counter metric
        
        Args:
            name (str): The counter name
            dimensions (dict): The counter dimensions
            
        Returns:
            float: The current counter value or 0 if not found
        """
        with self._lock:
            dimensions = dimensions or {}
            counter_key = f"{name}|{str(sorted([(k, v) for k, v in dimensions.items()]))}"
            return self._counters.get(counter_key, 0)
            
    def clear_metrics(self):
        """Clears all metrics from the registry
        
        Returns:
            int: Number of metrics cleared
        """
        with self._lock:
            count = len(self._metrics)
            self._metrics = []
            self._counters = {}
            return count
            
    def clear_old_metrics(self, older_than):
        """Clears metrics older than a specified time
        
        Args:
            older_than (datetime): Time threshold for clearing
            
        Returns:
            int: Number of metrics cleared
        """
        with self._lock:
            original_count = len(self._metrics)
            self._metrics = [m for m in self._metrics if m.timestamp >= older_than]
            return original_count - len(self._metrics)


class TimingMetric:
    """Context manager for timing operations and recording duration metrics"""
    
    def __init__(self, name, dimensions=None, trace_id=None):
        """Initializes the timing context
        
        Args:
            name (str): The name for the timing metric
            dimensions (dict): Optional dimensions for the metric
            trace_id (str): Optional trace ID for correlation
        """
        self.name = name
        self.dimensions = dimensions or {}
        self.trace_id = trace_id
        self.start_time = None
        self.success = True
        
    def __enter__(self):
        """Enter the context manager and start timing
        
        Returns:
            TimingMetric: Self reference
        """
        self.start_time = time.perf_counter()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context manager, calculate duration, and record metric
        
        Args:
            exc_type: Exception type if an exception occurred
            exc_val: Exception value if an exception occurred
            exc_tb: Exception traceback if an exception occurred
            
        Returns:
            bool: False to allow exception propagation
        """
        # Calculate the elapsed time in milliseconds
        elapsed_ms = (time.perf_counter() - self.start_time) * 1000
        
        # If an exception occurred, mark as unsuccessful
        if exc_type is not None:
            self.success = False
            
        # Record the timing metric
        record_timing(self.name, elapsed_ms, self.dimensions, self.trace_id)
        
        # Don't suppress exceptions
        return False


class timing_metric:
    """Decorator for timing function execution and recording metrics"""
    
    def __init__(self, name=None, dimensions=None, trace_id=None):
        """Initializes the timing decorator
        
        Args:
            name (str): The name for the metric or None to use function name
            dimensions (dict): Optional dimensions for the metric
            trace_id (str): Optional trace ID for correlation
        """
        self.name = name
        self.dimensions = dimensions or {}
        self.trace_id = trace_id
        
    def __call__(self, func):
        """Wraps the function with timing metrics
        
        Args:
            func (callable): The function to wrap
            
        Returns:
            callable: Wrapped function with timing metrics
        """
        # Use the function name if no metric name was provided
        metric_name = self.name or func.__name__
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with TimingMetric(metric_name, self.dimensions, self.trace_id):
                return func(*args, **kwargs)
                
        return wrapper


def setup_metrics(app_config=None):
    """Initializes the metrics collection system with appropriate configuration
    
    Args:
        app_config (dict): Configuration dictionary
    """
    global METRICS_ENABLED, CLOUDWATCH_ENABLED, METRICS_NAMESPACE, DEFAULT_DIMENSIONS
    
    # Check if metrics are enabled in the configuration
    if app_config and 'METRICS_ENABLED' in app_config:
        METRICS_ENABLED = app_config['METRICS_ENABLED']
        
    # Initialize the registry
    metrics_registry = MetricsRegistry.get_instance()
    
    # Configure CloudWatch if enabled
    if app_config and 'CLOUDWATCH_ENABLED' in app_config:
        CLOUDWATCH_ENABLED = app_config['CLOUDWATCH_ENABLED']
        
    # Set up default dimensions for metrics
    if app_config and 'METRICS_DIMENSIONS' in app_config:
        DEFAULT_DIMENSIONS.update(app_config['METRICS_DIMENSIONS'])
        
    # Initialize system metrics collection if enabled
    if METRICS_ENABLED and app_config and app_config.get('COLLECT_SYSTEM_METRICS', False):
        # Set up a background task to collect system metrics periodically
        pass
        
    logger.info(f"Metrics system initialized. Enabled: {METRICS_ENABLED}, CloudWatch: {CLOUDWATCH_ENABLED}")


def record_metric(name, value, unit="Count", dimensions=None, metric_type="gauge", trace_id=None):
    """Records a generic metric with name, value, and optional dimensions
    
    Args:
        name (str): The name of the metric
        value (float): The metric value
        unit (str): The unit of measurement
        dimensions (dict): Additional dimensions
        metric_type (str): Type of metric (gauge, counter, timing)
        trace_id (str): Optional trace ID for correlation
        
    Returns:
        bool: True if the metric was recorded, False otherwise
    """
    # Check if metrics are enabled
    if not METRICS_ENABLED:
        return False
        
    # Get the registry instance
    registry = MetricsRegistry.get_instance()
    
    # Combine default dimensions with provided dimensions
    all_dimensions = DEFAULT_DIMENSIONS.copy()
    if dimensions:
        all_dimensions.update(dimensions)
        
    # Create the metric
    metric = Metric(name, value, unit, all_dimensions, metric_type)
    
    # Set trace ID if provided
    if trace_id:
        metric.set_trace_id(trace_id)
        
    # Register the metric
    registry.register_metric(metric)
    
    # Send to CloudWatch if enabled
    if CLOUDWATCH_ENABLED:
        send_metric_to_cloudwatch(metric)
    
    # Log the metric
    metrics_logger = get_metrics_logger()
    metrics_logger.info(
        f"METRIC: {name}={value} {unit} [{metric_type}]",
        extra={"dimensions": all_dimensions, "trace_id": trace_id}
    )
    
    return True


def record_counter(name, value=1, dimensions=None, trace_id=None):
    """Records a counter metric (incrementing value)
    
    Args:
        name (str): The name of the counter
        value (float): The value to increment by
        dimensions (dict): Additional dimensions
        trace_id (str): Optional trace ID for correlation
        
    Returns:
        bool: True if the metric was recorded, False otherwise
    """
    return record_metric(
        name=name,
        value=value,
        unit="Count",
        dimensions=dimensions,
        metric_type="counter",
        trace_id=trace_id
    )


def record_gauge(name, value, unit="None", dimensions=None, trace_id=None):
    """Records a gauge metric (point-in-time value)
    
    Args:
        name (str): The name of the gauge
        value (float): The current value
        unit (str): The unit of measurement
        dimensions (dict): Additional dimensions
        trace_id (str): Optional trace ID for correlation
        
    Returns:
        bool: True if the metric was recorded, False otherwise
    """
    return record_metric(
        name=name,
        value=value,
        unit=unit,
        dimensions=dimensions,
        metric_type="gauge",
        trace_id=trace_id
    )


def record_timing(name, duration_ms, dimensions=None, trace_id=None):
    """Records a timing metric (duration of an operation)
    
    Args:
        name (str): The name of the timed operation
        duration_ms (float): The duration in milliseconds
        dimensions (dict): Additional dimensions
        trace_id (str): Optional trace ID for correlation
        
    Returns:
        bool: True if the metric was recorded, False otherwise
    """
    return record_metric(
        name=name,
        value=duration_ms,
        unit="Milliseconds",
        dimensions=dimensions,
        metric_type="timing",
        trace_id=trace_id
    )


def trigger_alert(alert_name, message, severity=AlertSeverity.MEDIUM, context=None):
    """Simplified local implementation to trigger alerts when metrics exceed thresholds
    
    Args:
        alert_name (str): The name of the alert
        message (str): Alert message
        severity (AlertSeverity): Severity level
        context (dict): Additional context for the alert
        
    Returns:
        bool: True if alert was triggered, False otherwise
    """
    context = context or {}
    
    # Log the alert with appropriate severity
    metrics_logger = get_metrics_logger()
    if severity == AlertSeverity.CRITICAL:
        metrics_logger.critical(f"ALERT: {alert_name} - {message}", extra={"context": context})
    elif severity == AlertSeverity.HIGH:
        metrics_logger.error(f"ALERT: {alert_name} - {message}", extra={"context": context})
    elif severity == AlertSeverity.MEDIUM:
        metrics_logger.warning(f"ALERT: {alert_name} - {message}", extra={"context": context})
    else:
        metrics_logger.info(f"ALERT: {alert_name} - {message}", extra={"context": context})
    
    # Create alert dimensions
    alert_dimensions = {
        "alert_name": alert_name,
        "severity": severity.value
    }
    
    # Record an alert metric
    record_counter(
        name="alerts",
        value=1,
        dimensions=alert_dimensions
    )
    
    return True


def record_api_metrics(endpoint, method, status_code, duration_ms, success=True, trace_id=None):
    """Records metrics related to API requests
    
    Args:
        endpoint (str): API endpoint path
        method (str): HTTP method
        status_code (int): HTTP status code
        duration_ms (float): Request duration in milliseconds
        success (bool): Whether the request was successful
        trace_id (str): Optional trace ID for correlation
        
    Returns:
        bool: True if all metrics were recorded, False otherwise
    """
    # Create dimensions for API metrics
    dimensions = {
        "endpoint": endpoint,
        "method": method,
        "status_code": str(status_code)
    }
    
    # Record request count
    record_counter(
        name="api.requests",
        dimensions=dimensions,
        trace_id=trace_id
    )
    
    # Record request duration
    record_timing(
        name="api.request_duration",
        duration_ms=duration_ms,
        dimensions=dimensions,
        trace_id=trace_id
    )
    
    # Record error count if not successful
    if not success:
        record_counter(
            name="api.errors",
            dimensions=dimensions,
            trace_id=trace_id
        )
    
    # Check if this is a slow request and trigger alert if needed
    if duration_ms > 1000:  # 1 second threshold for slow API requests
        slow_dimensions = dimensions.copy()
        slow_dimensions["duration_ms"] = str(int(duration_ms))
        
        record_counter(
            name="api.slow_requests",
            dimensions=slow_dimensions,
            trace_id=trace_id
        )
        
        # Trigger an alert if very slow (adjust thresholds as needed)
        if duration_ms > 5000:  # 5 second threshold for alert
            trigger_alert(
                alert_name="api_slow_request",
                message=f"Slow API request: {method} {endpoint} took {duration_ms}ms",
                severity=AlertSeverity.MEDIUM if duration_ms < 10000 else AlertSeverity.HIGH,
                context={"endpoint": endpoint, "method": method, "duration_ms": duration_ms}
            )
    
    return True


def record_database_metrics(operation, table, duration_ms, success=True, rows_affected=None, trace_id=None):
    """Records metrics related to database operations
    
    Args:
        operation (str): Database operation (query, insert, update, delete)
        table (str): Database table name
        duration_ms (float): Operation duration in milliseconds
        success (bool): Whether the operation was successful
        rows_affected (int): Number of rows affected by the operation
        trace_id (str): Optional trace ID for correlation
        
    Returns:
        bool: True if all metrics were recorded, False otherwise
    """
    # Create dimensions for database metrics
    dimensions = {
        "operation": operation,
        "table": table
    }
    
    # Record operation count
    record_counter(
        name="database.operations",
        dimensions=dimensions,
        trace_id=trace_id
    )
    
    # Record operation duration
    record_timing(
        name="database.operation_duration",
        duration_ms=duration_ms,
        dimensions=dimensions,
        trace_id=trace_id
    )
    
    # Record rows affected if provided
    if rows_affected is not None:
        record_gauge(
            name="database.rows_affected",
            value=rows_affected,
            dimensions=dimensions,
            trace_id=trace_id
        )
    
    # Record error count if not successful
    if not success:
        record_counter(
            name="database.errors",
            dimensions=dimensions,
            trace_id=trace_id
        )
    
    # Check if this is a slow query and trigger alert if needed
    if duration_ms > 500:  # 500ms threshold for slow database operations
        slow_dimensions = dimensions.copy()
        slow_dimensions["duration_ms"] = str(int(duration_ms))
        
        record_counter(
            name="database.slow_operations",
            dimensions=slow_dimensions,
            trace_id=trace_id
        )
        
        # Trigger an alert if very slow (adjust thresholds as needed)
        if duration_ms > 2000:  # 2 second threshold for alert
            trigger_alert(
                alert_name="database_slow_operation",
                message=f"Slow database operation: {operation} on {table} took {duration_ms}ms",
                severity=AlertSeverity.MEDIUM if duration_ms < 5000 else AlertSeverity.HIGH,
                context={"operation": operation, "table": table, "duration_ms": duration_ms}
            )
    
    return True


def record_file_upload_metrics(file_type, file_size, upload_duration_ms, success=True, trace_id=None):
    """Records metrics related to file uploads
    
    Args:
        file_type (str): Type of file uploaded
        file_size (int): Size of file in bytes
        upload_duration_ms (float): Upload duration in milliseconds
        success (bool): Whether the upload was successful
        trace_id (str): Optional trace ID for correlation
        
    Returns:
        bool: True if all metrics were recorded, False otherwise
    """
    # Create dimensions for upload metrics
    dimensions = {
        "file_type": file_type
    }
    
    # Record upload count
    record_counter(
        name="file.uploads",
        dimensions=dimensions,
        trace_id=trace_id
    )
    
    # Record upload size
    record_gauge(
        name="file.upload_size",
        value=file_size,
        unit="Bytes",
        dimensions=dimensions,
        trace_id=trace_id
    )
    
    # Record upload duration
    record_timing(
        name="file.upload_duration",
        duration_ms=upload_duration_ms,
        dimensions=dimensions,
        trace_id=trace_id
    )
    
    # Record error count if not successful
    if not success:
        record_counter(
            name="file.upload_errors",
            dimensions=dimensions,
            trace_id=trace_id
        )
    
    # Calculate and record upload speed (KB/s)
    if upload_duration_ms > 0:
        upload_speed = (file_size / 1024) / (upload_duration_ms / 1000)
        record_gauge(
            name="file.upload_speed",
            value=upload_speed,
            unit="KBps",
            dimensions=dimensions,
            trace_id=trace_id
        )
    
    return True


def record_file_processing_metrics(file_type, file_size, processing_duration_ms, success=True, trace_id=None):
    """Records metrics related to file processing
    
    Args:
        file_type (str): Type of file processed
        file_size (int): Size of file in bytes
        processing_duration_ms (float): Processing duration in milliseconds
        success (bool): Whether the processing was successful
        trace_id (str): Optional trace ID for correlation
        
    Returns:
        bool: True if all metrics were recorded, False otherwise
    """
    # Create dimensions for processing metrics
    dimensions = {
        "file_type": file_type
    }
    
    # Record processing count
    record_counter(
        name="file.processing",
        dimensions=dimensions,
        trace_id=trace_id
    )
    
    # Record processing duration
    record_timing(
        name="file.processing_duration",
        duration_ms=processing_duration_ms,
        dimensions=dimensions,
        trace_id=trace_id
    )
    
    # Record error count if not successful
    if not success:
        record_counter(
            name="file.processing_errors",
            dimensions=dimensions,
            trace_id=trace_id
        )
    
    # Check if this is slow processing and trigger alert if needed
    if processing_duration_ms > 10000:  # 10 second threshold for slow processing
        slow_dimensions = dimensions.copy()
        slow_dimensions["duration_ms"] = str(int(processing_duration_ms))
        slow_dimensions["file_size"] = str(file_size)
        
        record_counter(
            name="file.slow_processing",
            dimensions=slow_dimensions,
            trace_id=trace_id
        )
        
        # Trigger an alert if very slow (adjust thresholds as needed)
        if processing_duration_ms > 60000:  # 1 minute threshold for alert
            trigger_alert(
                alert_name="file_slow_processing",
                message=f"Slow file processing: {file_type} ({file_size} bytes) took {processing_duration_ms}ms",
                severity=AlertSeverity.MEDIUM if processing_duration_ms < 300000 else AlertSeverity.HIGH,
                context={"file_type": file_type, "file_size": file_size, "duration_ms": processing_duration_ms}
            )
    
    return True


def record_form_submission_metrics(form_type, submission_duration_ms, success=True, trace_id=None):
    """Records metrics related to form submissions
    
    Args:
        form_type (str): Type of form submitted
        submission_duration_ms (float): Submission processing duration in milliseconds
        success (bool): Whether the submission was successful
        trace_id (str): Optional trace ID for correlation
        
    Returns:
        bool: True if all metrics were recorded, False otherwise
    """
    # Create dimensions for form submission metrics
    dimensions = {
        "form_type": form_type
    }
    
    # Record submission count
    record_counter(
        name="form.submissions",
        dimensions=dimensions,
        trace_id=trace_id
    )
    
    # Record submission duration
    record_timing(
        name="form.submission_duration",
        duration_ms=submission_duration_ms,
        dimensions=dimensions,
        trace_id=trace_id
    )
    
    # Record error count if not successful
    if not success:
        record_counter(
            name="form.submission_errors",
            dimensions=dimensions,
            trace_id=trace_id
        )
    
    return True


def record_system_metrics():
    """Records system-level metrics like CPU, memory, and disk usage
    
    Returns:
        bool: True if metrics were recorded, False otherwise
    """
    if not METRICS_ENABLED:
        return False
    
    try:
        # CPU usage (percent)
        cpu_percent = psutil.cpu_percent(interval=0.1)
        record_gauge(
            name="system.cpu_usage",
            value=cpu_percent,
            unit="Percent"
        )
        
        # Memory usage (percent and absolute)
        memory = psutil.virtual_memory()
        record_gauge(
            name="system.memory_usage",
            value=memory.percent,
            unit="Percent"
        )
        record_gauge(
            name="system.memory_used",
            value=memory.used / (1024 * 1024),  # Convert to MB
            unit="Megabytes"
        )
        
        # Disk usage
        disk = psutil.disk_usage('/')
        record_gauge(
            name="system.disk_usage",
            value=disk.percent,
            unit="Percent"
        )
        record_gauge(
            name="system.disk_free",
            value=disk.free / (1024 * 1024 * 1024),  # Convert to GB
            unit="Gigabytes"
        )
        
        # Network I/O
        net_io = psutil.net_io_counters()
        record_gauge(
            name="system.network_sent",
            value=net_io.bytes_sent / (1024 * 1024),  # Convert to MB
            unit="Megabytes"
        )
        record_gauge(
            name="system.network_recv",
            value=net_io.bytes_recv / (1024 * 1024),  # Convert to MB
            unit="Megabytes"
        )
        
        # Check if any metrics exceed critical thresholds
        if cpu_percent > 90:
            trigger_alert(
                alert_name="high_cpu_usage",
                message=f"High CPU usage: {cpu_percent}%",
                severity=AlertSeverity.HIGH,
                context={"cpu_percent": cpu_percent}
            )
            
        if memory.percent > 90:
            trigger_alert(
                alert_name="high_memory_usage",
                message=f"High memory usage: {memory.percent}%",
                severity=AlertSeverity.HIGH,
                context={"memory_percent": memory.percent}
            )
            
        if disk.percent > 90:
            trigger_alert(
                alert_name="high_disk_usage",
                message=f"High disk usage: {disk.percent}%",
                severity=AlertSeverity.HIGH,
                context={"disk_percent": disk.percent}
            )
        
        return True
        
    except Exception as e:
        logger.error(f"Error recording system metrics: {str(e)}", exc_info=True)
        return False


def record_integration_metrics(service_name, operation, duration_ms, success=True, trace_id=None):
    """Records metrics related to external service integrations
    
    Args:
        service_name (str): External service name
        operation (str): Operation performed
        duration_ms (float): Operation duration in milliseconds
        success (bool): Whether the operation was successful
        trace_id (str): Optional trace ID for correlation
        
    Returns:
        bool: True if all metrics were recorded, False otherwise
    """
    # Create dimensions for integration metrics
    dimensions = {
        "service_name": service_name,
        "operation": operation
    }
    
    # Record integration call count
    record_counter(
        name="integration.calls",
        dimensions=dimensions,
        trace_id=trace_id
    )
    
    # Record integration duration
    record_timing(
        name="integration.duration",
        duration_ms=duration_ms,
        dimensions=dimensions,
        trace_id=trace_id
    )
    
    # Record error count if not successful
    if not success:
        record_counter(
            name="integration.errors",
            dimensions=dimensions,
            trace_id=trace_id
        )
    
    # Check if this is a slow integration and trigger alert if needed
    if duration_ms > 1000:  # 1 second threshold for slow integrations
        slow_dimensions = dimensions.copy()
        slow_dimensions["duration_ms"] = str(int(duration_ms))
        
        record_counter(
            name="integration.slow_calls",
            dimensions=slow_dimensions,
            trace_id=trace_id
        )
        
        # Trigger an alert if very slow (adjust thresholds as needed)
        if duration_ms > 5000:  # 5 second threshold for alert
            trigger_alert(
                alert_name="integration_slow_call",
                message=f"Slow integration call: {service_name}.{operation} took {duration_ms}ms",
                severity=AlertSeverity.MEDIUM if duration_ms < 10000 else AlertSeverity.HIGH,
                context={"service_name": service_name, "operation": operation, "duration_ms": duration_ms}
            )
    
    return True


def record_business_metric(name, value, dimensions=None, trace_id=None):
    """Records business-level metrics like conversions and engagement
    
    Args:
        name (str): Metric name
        value (float): Metric value
        dimensions (dict): Additional dimensions
        trace_id (str): Optional trace ID for correlation
        
    Returns:
        bool: True if metric was recorded, False otherwise
    """
    # Add business metric type to dimensions
    business_dimensions = dimensions.copy() if dimensions else {}
    business_dimensions["metric_type"] = "business"
    
    # Record the business metric
    return record_metric(
        name=name,
        value=value,
        unit="Count",
        dimensions=business_dimensions,
        metric_type="gauge",
        trace_id=trace_id
    )


def get_cloudwatch_client():
    """Creates and returns a boto3 CloudWatch client with proper configuration
    
    Returns:
        boto3.client: Configured CloudWatch client instance or None if CloudWatch is disabled
    """
    if not CLOUDWATCH_ENABLED:
        return None
        
    try:
        # Create CloudWatch client
        client = boto3.client(
            'cloudwatch',
            region_name=getattr(settings, 'AWS_REGION', 'us-east-1'),
            aws_access_key_id=getattr(settings, 'AWS_ACCESS_KEY_ID', None),
            aws_secret_access_key=getattr(settings, 'AWS_SECRET_ACCESS_KEY', None)
        )
        return client
    except Exception as e:
        logger.error(f"Error creating CloudWatch client: {str(e)}", exc_info=True)
        return None


def send_metric_to_cloudwatch(metric):
    """Sends a metric to AWS CloudWatch
    
    Args:
        metric (Metric): The metric to send
        
    Returns:
        bool: True if successful, False otherwise
    """
    if not CLOUDWATCH_ENABLED:
        return False
        
    try:
        client = get_cloudwatch_client()
        if not client:
            return False
            
        # Convert dimensions to CloudWatch format
        cw_dimensions = [
            {'Name': key, 'Value': str(value)}
            for key, value in metric.dimensions.items()
        ]
        
        # Send the metric
        client.put_metric_data(
            Namespace=METRICS_NAMESPACE,
            MetricData=[
                {
                    'MetricName': metric.name,
                    'Dimensions': cw_dimensions,
                    'Timestamp': metric.timestamp,
                    'Value': metric.value,
                    'Unit': metric.unit
                }
            ]
        )
        
        return True
    except Exception as e:
        logger.error(f"Error sending metric to CloudWatch: {str(e)}", exc_info=True)
        return False


# Create a singleton instance of the registry for use throughout the app
metrics = MetricsRegistry.get_instance()