"""
Entry point for the IndiVillage backend monitoring module that provides a comprehensive
observability framework including logging, metrics collection, distributed tracing,
and alerting capabilities. This module centralizes monitoring functionality to track
system health, performance, and business metrics while enabling proper incident
detection and response.
"""

import typing

from ..core.logging import get_logger  # Import function to get a configured logger
from ..core.config import settings  # Import application settings for monitoring configuration
from .logging import setup_monitoring_logging, get_monitoring_logger, log_system_health, log_performance_metric, log_threshold_exceeded, log_service_status, log_security_event, log_api_metrics, log_database_metrics, log_integration_event, MonitoringLogFilter, MonitoringJsonFormatter, PerformanceMonitor  # Import function to initialize monitoring logging system
from .metrics import MetricsCollector, MetricsRegistry, TimingMetric, record_metric, record_api_metrics, record_database_metrics, record_file_upload_metrics, record_form_submission_metrics, record_system_metrics, record_integration_metrics, record_business_metric, metrics  # Import metrics collector class for metrics collection
from .tracing import setup_tracing, start_span, end_span, add_span_event, get_current_span, get_current_trace_id, trace, trace_async, Span, SpanEvent, TraceMiddleware, TracingContextManager  # Import function to initialize tracing system
from .alerting import setup_alerting, trigger_alert, resolve_alert, acknowledge_alert, get_active_alerts, get_alert_by_id, register_alert_rule, evaluate_alert_rules, AlertSeverity, AlertStatus, Alert, AlertRule  # Import function to initialize alerting system

# Initialize logger
logger = get_logger(__name__)

# Define module version
VERSION = "1.0.0"


def setup_monitoring(app_config: typing.Dict) -> None:
    """
    Initializes all monitoring subsystems (logging, metrics, tracing, alerting)

    Args:
        app_config: Application configuration dictionary

    Returns:
        None: Function performs side effects only
    """
    # Log initialization of monitoring system
    logger.info("Initializing monitoring system...")

    # Initialize monitoring logging by calling setup_monitoring_logging()
    setup_monitoring_logging()

    # Initialize metrics collection
    # The metrics collector is initialized when the metrics module is imported.
    # No explicit initialization is needed here.

    # Initialize distributed tracing by calling setup_tracing(app_config)
    setup_tracing(app_config)

    # Initialize alerting system by calling setup_alerting(app_config)
    setup_alerting(app_config)

    # Log successful initialization of all monitoring subsystems
    logger.info("Monitoring system initialized successfully.")


__all__ = [
    "setup_monitoring",
    "setup_monitoring_logging",
    "get_monitoring_logger",
    "log_system_health",
    "log_performance_metric",
    "log_threshold_exceeded",
    "log_service_status",
    "log_security_event",
    "log_api_metrics",
    "log_database_metrics",
    "log_integration_event",
    "PerformanceMonitor",
    "record_metric",
    "record_api_metrics",
    "record_database_metrics",
    "record_file_upload_metrics",
    "record_form_submission_metrics",
    "record_system_metrics",
    "record_integration_metrics",
    "record_business_metric",
    "metrics",
    "TimingMetric",
    "setup_tracing",
    "start_span",
    "end_span",
    "add_span_event",
    "get_current_span",
    "trace",
    "trace_async",
    "setup_alerting",
    "trigger_alert",
    "resolve_alert",
    "acknowledge_alert",
    "get_active_alerts",
    "AlertSeverity",
    "AlertStatus",
    "Span",
    "SpanEvent",
    "TraceMiddleware",
    "TracingContextManager",
    "get_alert_by_id",
    "register_alert_rule",
    "evaluate_alert_rules",
    "MonitoringLogFilter",
    "MonitoringJsonFormatter"
]