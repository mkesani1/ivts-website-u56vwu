"""
Alerting module for the IndiVillage backend application.

This module provides a comprehensive alerting system for monitoring system health,
performance issues, and security events. It handles alert definition, triggering,
routing, and notification across various channels.
"""

import typing
import enum
import datetime
import json
import uuid
import threading
import requests  # version: ^2.28.2
import pdpyras  # version: ^4.5.1

from ..core.config import settings
from ..core.logging import get_logger
from .logging import get_alert_logger, log_alert
from .metrics import record_counter, AlertSeverity
from .tracing import get_current_trace_id
from ..integrations.sendgrid import SendGridClient
from ..integrations.aws_s3 import S3Client

# Initialize loggers
logger = get_logger(__name__)
alert_logger = get_alert_logger()

# Configuration from settings
ALERTING_ENABLED = getattr(settings, 'ALERTING_ENABLED', True)
ALERT_DEDUPLICATION_WINDOW = getattr(settings, 'ALERT_DEDUPLICATION_WINDOW', 300)  # 5 minutes
PAGERDUTY_ENABLED = hasattr(settings, 'PAGERDUTY_API_KEY') and settings.PAGERDUTY_API_KEY
SLACK_ENABLED = hasattr(settings, 'SLACK_WEBHOOK_URL') and settings.SLACK_WEBHOOK_URL
EMAIL_ENABLED = hasattr(settings, 'ADMIN_EMAIL') and settings.ADMIN_EMAIL

# Alert registry for deduplication and tracking
_alert_registry = {}
_registry_lock = threading.Lock()


class AlertType(enum.Enum):
    """Enum defining types of alerts for categorization"""
    SYSTEM = "system"
    SECURITY = "security"
    PERFORMANCE = "performance"
    API = "api"
    DATABASE = "database"
    FILE_PROCESSING = "file_processing"
    INTEGRATION = "integration"
    BUSINESS = "business"


class AlertChannel(enum.Enum):
    """Enum defining notification channels for alerts"""
    PAGERDUTY = "pagerduty"
    SLACK = "slack"
    EMAIL = "email"
    CONSOLE = "console"
    WEBHOOK = "webhook"


class Alert:
    """Class representing an alert with all relevant information"""
    
    def __init__(self, name, message, severity, details=None, alert_type=None, trace_id=None):
        """Initializes a new alert
        
        Args:
            name (str): The name/identifier of the alert
            message (str): Alert message describing the issue
            severity (AlertSeverity): Severity level of the alert
            details (dict): Additional details about the alert
            alert_type (AlertType): Type of alert for categorization
            trace_id (str): Optional trace ID for correlation with distributed tracing
        """
        self.id = str(uuid.uuid4())
        self.name = name
        self.message = message
        self.severity = severity
        self.alert_type = alert_type or AlertType.SYSTEM
        self.details = details or {}
        self.created_at = datetime.datetime.utcnow()
        self.updated_at = self.created_at
        self.is_resolved = False
        self.resolution_message = None
        self.resolved_at = None
        self.trace_id = trace_id
        self.notification_status = {}  # Tracks status of notifications for each channel
        self.artifacts = []  # Links to additional data related to the alert
    
    def resolve(self, resolution_message):
        """Marks the alert as resolved
        
        Args:
            resolution_message (str): Message explaining the resolution
        """
        self.is_resolved = True
        self.resolution_message = resolution_message
        self.resolved_at = datetime.datetime.utcnow()
        self.updated_at = self.resolved_at
    
    def update_notification_status(self, channel, status):
        """Updates the notification status for a channel
        
        Args:
            channel (AlertChannel): The notification channel
            status (dict): Status information for the notification
        """
        self.notification_status[channel] = status
        self.updated_at = datetime.datetime.utcnow()
    
    def add_artifact(self, name, url, content_type):
        """Adds an artifact reference to the alert
        
        Args:
            name (str): Name/identifier for the artifact
            url (str): URL where the artifact can be accessed
            content_type (str): Content type of the artifact
        """
        self.artifacts.append({
            'name': name,
            'url': url,
            'content_type': content_type,
            'timestamp': datetime.datetime.utcnow().isoformat()
        })
        self.updated_at = datetime.datetime.utcnow()
    
    def to_dict(self):
        """Converts the alert to a dictionary representation
        
        Returns:
            dict: Dictionary representation of the alert
        """
        return {
            'id': self.id,
            'name': self.name,
            'message': self.message,
            'severity': self.severity.value if isinstance(self.severity, enum.Enum) else self.severity,
            'alert_type': self.alert_type.value if isinstance(self.alert_type, enum.Enum) else self.alert_type,
            'details': self.details,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'is_resolved': self.is_resolved,
            'resolution_message': self.resolution_message,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'trace_id': self.trace_id,
            'notification_status': self.notification_status,
            'artifacts': self.artifacts
        }
    
    def to_json(self):
        """Converts the alert to a JSON string
        
        Returns:
            str: JSON string representation of the alert
        """
        return json.dumps(self.to_dict())


class AlertRegistry:
    """Singleton class that maintains a registry of alerts"""
    
    _instance = None
    
    def __init__(self):
        """Initializes the AlertRegistry singleton"""
        self._alerts = {}  # Dictionary of alerts by ID
        self._deduplication_keys = {}  # Dictionary of deduplication keys with timestamps
        self._lock = threading.Lock()
    
    @classmethod
    def get_instance(cls):
        """Returns the singleton instance of AlertRegistry
        
        Returns:
            AlertRegistry: Singleton instance
        """
        if cls._instance is None:
            cls._instance = AlertRegistry()
        return cls._instance
    
    def register_alert(self, alert):
        """Registers an alert in the registry
        
        Args:
            alert (Alert): The alert to register
            
        Returns:
            str: Alert ID
        """
        with self._lock:
            # Add alert to the registry
            self._alerts[alert.id] = alert
            
            # Generate deduplication key if needed
            dedup_key = f"{alert.name}|{json.dumps(alert.details, sort_keys=True)}"
            self._deduplication_keys[dedup_key] = datetime.datetime.utcnow()
            
            return alert.id
    
    def get_alert(self, alert_id):
        """Retrieves an alert by ID
        
        Args:
            alert_id (str): The alert ID
            
        Returns:
            Alert: Alert object or None if not found
        """
        with self._lock:
            return self._alerts.get(alert_id)
    
    def get_alerts(self, active_only=False, severity=None, alert_type=None, since=None, until=None):
        """Retrieves alerts, optionally filtered
        
        Args:
            active_only (bool): If True, return only unresolved alerts
            severity (AlertSeverity): Filter by severity
            alert_type (AlertType): Filter by alert type
            since (datetime): Filter by alerts created after this time
            until (datetime): Filter by alerts created before this time
            
        Returns:
            list: List of Alert objects matching filters
        """
        with self._lock:
            filtered_alerts = list(self._alerts.values())
            
            # Apply active_only filter
            if active_only:
                filtered_alerts = [a for a in filtered_alerts if not a.is_resolved]
            
            # Apply severity filter
            if severity:
                filtered_alerts = [a for a in filtered_alerts if a.severity == severity]
            
            # Apply alert_type filter
            if alert_type:
                filtered_alerts = [a for a in filtered_alerts if a.alert_type == alert_type]
            
            # Apply time range filters
            if since:
                filtered_alerts = [a for a in filtered_alerts if a.created_at >= since]
            
            if until:
                filtered_alerts = [a for a in filtered_alerts if a.created_at <= until]
            
            return filtered_alerts
    
    def is_duplicate(self, dedup_key):
        """Checks if an alert is a duplicate within the deduplication window
        
        Args:
            dedup_key (str): Deduplication key to check
            
        Returns:
            bool: True if duplicate, False otherwise
        """
        with self._lock:
            if dedup_key in self._deduplication_keys:
                # Check if within deduplication window
                last_time = self._deduplication_keys[dedup_key]
                now = datetime.datetime.utcnow()
                time_diff = (now - last_time).total_seconds()
                
                if time_diff < ALERT_DEDUPLICATION_WINDOW:
                    return True
            
            return False
    
    def cleanup_old_alerts(self, older_than):
        """Removes old resolved alerts from the registry
        
        Args:
            older_than (datetime): Time threshold for clearing
            
        Returns:
            int: Number of alerts cleared
        """
        with self._lock:
            to_remove = []
            
            for alert_id, alert in self._alerts.items():
                if alert.is_resolved and alert.resolved_at < older_than:
                    to_remove.append(alert_id)
            
            for alert_id in to_remove:
                del self._alerts[alert_id]
            
            return len(to_remove)
    
    def cleanup_deduplication_keys(self):
        """Removes expired deduplication keys
        
        Returns:
            int: Number of keys cleared
        """
        with self._lock:
            now = datetime.datetime.utcnow()
            expired_time = now - datetime.timedelta(seconds=ALERT_DEDUPLICATION_WINDOW)
            to_remove = []
            
            for key, timestamp in self._deduplication_keys.items():
                if timestamp < expired_time:
                    to_remove.append(key)
            
            for key in to_remove:
                del self._deduplication_keys[key]
            
            return len(to_remove)


class PagerDutyClient:
    """Client for sending alerts to PagerDuty"""
    
    def __init__(self, api_key, service_id):
        """Initializes the PagerDuty client
        
        Args:
            api_key (str): PagerDuty API key
            service_id (str): PagerDuty service ID
        """
        self._api_key = api_key
        self._service_id = service_id
        self._session = pdpyras.EventsAPISession(api_key)
        
        logger.info(f"Initialized PagerDuty client for service {service_id}")
    
    def trigger_incident(self, alert):
        """Creates a new incident in PagerDuty
        
        Args:
            alert (Alert): The alert to create an incident for
            
        Returns:
            dict: Response with incident details
        """
        try:
            # Build the event payload
            payload = {
                'routing_key': self._api_key,
                'event_action': 'trigger',
                'dedup_key': alert.id,
                'payload': {
                    'summary': f"{alert.name}: {alert.message}",
                    'source': settings.PROJECT_NAME,
                    'severity': self._severity_to_pd_severity(alert.severity),
                    'component': alert.alert_type.value if isinstance(alert.alert_type, enum.Enum) else alert.alert_type,
                    'group': settings.ENVIRONMENT,
                    'class': alert.name,
                    'custom_details': alert.details
                }
            }
            
            # Add trace ID if available
            if alert.trace_id:
                payload['payload']['custom_details']['trace_id'] = alert.trace_id
            
            # Create the incident
            response = self._session.send_event(payload)
            
            logger.info(f"Created PagerDuty incident for alert {alert.id}: {response['dedup_key']}")
            
            return {
                'status': 'success',
                'incident_id': response.get('dedup_key'),
                'message': 'Incident created successfully'
            }
            
        except Exception as e:
            logger.error(f"Error creating PagerDuty incident for alert {alert.id}: {str(e)}", exc_info=True)
            
            return {
                'status': 'error',
                'message': f"Failed to create incident: {str(e)}"
            }
    
    def resolve_incident(self, incident_id, resolution_message):
        """Resolves an existing incident in PagerDuty
        
        Args:
            incident_id (str): The incident ID to resolve
            resolution_message (str): Resolution message
            
        Returns:
            dict: Response with resolution status
        """
        try:
            # Build the resolution payload
            payload = {
                'routing_key': self._api_key,
                'event_action': 'resolve',
                'dedup_key': incident_id,
                'payload': {
                    'summary': resolution_message,
                    'source': settings.PROJECT_NAME,
                }
            }
            
            # Resolve the incident
            response = self._session.send_event(payload)
            
            logger.info(f"Resolved PagerDuty incident {incident_id}")
            
            return {
                'status': 'success',
                'message': 'Incident resolved successfully'
            }
            
        except Exception as e:
            logger.error(f"Error resolving PagerDuty incident {incident_id}: {str(e)}", exc_info=True)
            
            return {
                'status': 'error',
                'message': f"Failed to resolve incident: {str(e)}"
            }
    
    def _severity_to_pd_severity(self, severity):
        """Maps AlertSeverity to PagerDuty severity levels
        
        Args:
            severity (AlertSeverity): The alert severity
            
        Returns:
            str: PagerDuty severity level
        """
        if severity == AlertSeverity.CRITICAL:
            return 'critical'
        elif severity == AlertSeverity.HIGH:
            return 'error'
        elif severity == AlertSeverity.MEDIUM:
            return 'warning'
        else:
            return 'info'


class SlackClient:
    """Client for sending alerts to Slack"""
    
    def __init__(self, webhook_url, channel=None, username=None):
        """Initializes the Slack client
        
        Args:
            webhook_url (str): Slack webhook URL
            channel (str): Slack channel to send messages to
            username (str): Username to use for messages
        """
        self._webhook_url = webhook_url
        self._channel = channel
        self._username = username or "AlertBot"
        
        logger.info(f"Initialized Slack client")
    
    def send_alert(self, alert):
        """Sends an alert to Slack
        
        Args:
            alert (Alert): The alert to send
            
        Returns:
            dict: Response with sending status
        """
        try:
            # Determine color based on severity
            color = self._severity_to_color(alert.severity)
            
            # Create message payload
            payload = {
                'text': f"*{alert.severity.value.upper() if isinstance(alert.severity, enum.Enum) else alert.severity.upper()}*: {alert.name}",
                'username': self._username,
                'attachments': [
                    {
                        'color': color,
                        'title': alert.message,
                        'text': self._format_details(alert.details),
                        'fields': [
                            {
                                'title': 'Alert Type',
                                'value': alert.alert_type.value if isinstance(alert.alert_type, enum.Enum) else alert.alert_type,
                                'short': True
                            },
                            {
                                'title': 'Time',
                                'value': alert.created_at.strftime('%Y-%m-%d %H:%M:%S UTC'),
                                'short': True
                            }
                        ],
                        'footer': f"{settings.PROJECT_NAME} - {settings.ENVIRONMENT}"
                    }
                ]
            }
            
            # Add channel if specified
            if self._channel:
                payload['channel'] = self._channel
            
            # Add trace ID if available
            if alert.trace_id:
                payload['attachments'][0]['fields'].append({
                    'title': 'Trace ID',
                    'value': alert.trace_id,
                    'short': True
                })
            
            # Send to Slack
            response = requests.post(
                self._webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'}
            )
            
            response.raise_for_status()
            
            logger.info(f"Sent alert {alert.id} to Slack, status: {response.status_code}")
            
            return {
                'status': 'success',
                'message': 'Alert sent to Slack successfully'
            }
            
        except Exception as e:
            logger.error(f"Error sending alert {alert.id} to Slack: {str(e)}", exc_info=True)
            
            return {
                'status': 'error',
                'message': f"Failed to send to Slack: {str(e)}"
            }
    
    def _severity_to_color(self, severity):
        """Maps AlertSeverity to Slack colors
        
        Args:
            severity (AlertSeverity): The alert severity
            
        Returns:
            str: Slack color code
        """
        if severity == AlertSeverity.CRITICAL:
            return '#ff0000'  # Red
        elif severity == AlertSeverity.HIGH:
            return '#ffa500'  # Orange
        elif severity == AlertSeverity.MEDIUM:
            return '#ffff00'  # Yellow
        elif severity == AlertSeverity.LOW:
            return '#00ff00'  # Green
        else:
            return '#808080'  # Gray for info/unknown
    
    def _format_details(self, details):
        """Formats alert details for Slack message
        
        Args:
            details (dict): Alert details
            
        Returns:
            str: Formatted details string
        """
        if not details:
            return "No additional details"
        
        try:
            return "```" + json.dumps(details, indent=2, sort_keys=True) + "```"
        except Exception:
            return str(details)


def setup_alerting(app_config=None):
    """Initializes the alerting system with appropriate configuration
    
    Args:
        app_config (dict): Configuration dictionary
    """
    global ALERTING_ENABLED, ALERT_DEDUPLICATION_WINDOW, PAGERDUTY_ENABLED, SLACK_ENABLED, EMAIL_ENABLED
    
    if app_config is None:
        app_config = {}
    
    # Check if alerting is enabled in the config
    if 'ALERTING_ENABLED' in app_config:
        ALERTING_ENABLED = app_config['ALERTING_ENABLED']
    
    # Configure deduplication window
    if 'ALERT_DEDUPLICATION_WINDOW' in app_config:
        ALERT_DEDUPLICATION_WINDOW = app_config['ALERT_DEDUPLICATION_WINDOW']
    
    # Initialize alert registry
    registry = AlertRegistry.get_instance()
    
    # Configure notification integrations
    if 'PAGERDUTY_API_KEY' in app_config:
        PAGERDUTY_ENABLED = bool(app_config['PAGERDUTY_API_KEY'])
    
    if 'SLACK_WEBHOOK_URL' in app_config:
        SLACK_ENABLED = bool(app_config['SLACK_WEBHOOK_URL'])
    
    if 'ADMIN_EMAIL' in app_config:
        EMAIL_ENABLED = bool(app_config['ADMIN_EMAIL'])
    
    logger.info(
        f"Alerting system initialized. Enabled: {ALERTING_ENABLED}, "
        f"Channels: PagerDuty={PAGERDUTY_ENABLED}, Slack={SLACK_ENABLED}, Email={EMAIL_ENABLED}"
    )


def trigger_alert(alert_name, message, severity, details=None, channels=None, deduplicate=True):
    """Triggers an alert with the specified parameters
    
    Args:
        alert_name (str): Name/identifier for the alert
        message (str): Alert message describing the issue
        severity (AlertSeverity): Severity level
        details (dict): Additional details about the alert
        channels (list): List of AlertChannel to use, or None for default routing
        deduplicate (bool): Whether to check for and suppress duplicate alerts
        
    Returns:
        dict: Alert result with alert ID and status
    """
    if not ALERTING_ENABLED:
        logger.info(f"Alert '{alert_name}' not triggered because alerting is disabled")
        return {'status': 'disabled', 'message': 'Alerting is disabled'}
    
    # Create alert object
    alert_type = details.get('alert_type', AlertType.SYSTEM) if details else AlertType.SYSTEM
    if isinstance(alert_type, str):
        try:
            alert_type = AlertType[alert_type]
        except (KeyError, ValueError):
            alert_type = AlertType.SYSTEM
    
    # Get trace ID for correlation
    trace_id = details.get('trace_id') if details else None
    if not trace_id:
        trace_id = get_current_trace_id()
    
    # Create the alert
    alert = Alert(
        name=alert_name,
        message=message,
        severity=severity,
        details=details,
        alert_type=alert_type,
        trace_id=trace_id
    )
    
    # Check for duplicate alerts
    if deduplicate and is_duplicate_alert(alert):
        logger.info(f"Suppressing duplicate alert: {alert_name}")
        return {
            'status': 'deduplicated',
            'message': 'Duplicate alert suppressed',
            'alert_id': None
        }
    
    # Register the alert
    register_alert(alert)
    
    # Log the alert
    log_alert(
        alert_name=alert_name,
        severity=severity,
        message=message,
        details=details,
        context={'alert_id': alert.id, 'trace_id': trace_id}
    )
    
    # Record alert metric
    record_counter(
        name="alerts.triggered",
        dimensions={
            "severity": severity.value if isinstance(severity, enum.Enum) else severity,
            "alert_type": alert_type.value if isinstance(alert_type, enum.Enum) else alert_type,
            "alert_name": alert_name
        },
        trace_id=trace_id
    )
    
    # Route the alert to appropriate channels
    notification_results = route_alert(alert, channels)
    
    return {
        'status': 'triggered',
        'message': 'Alert triggered successfully',
        'alert_id': alert.id,
        'notification_results': notification_results
    }


def is_duplicate_alert(alert):
    """Checks if an alert is a duplicate within the deduplication window
    
    Args:
        alert (Alert): The alert to check
        
    Returns:
        bool: True if alert is a duplicate, False otherwise
    """
    dedup_key = f"{alert.name}|{json.dumps(alert.details, sort_keys=True)}"
    
    with _registry_lock:
        if dedup_key in _alert_registry:
            # Check if within deduplication window
            last_time = _alert_registry[dedup_key]
            now = datetime.datetime.utcnow()
            time_diff = (now - last_time).total_seconds()
            
            if time_diff < ALERT_DEDUPLICATION_WINDOW:
                return True
        
        return False


def register_alert(alert):
    """Registers an alert in the alert registry for deduplication
    
    Args:
        alert (Alert): The alert to register
    """
    dedup_key = f"{alert.name}|{json.dumps(alert.details, sort_keys=True)}"
    
    with _registry_lock:
        # Store in registry with current timestamp
        _alert_registry[dedup_key] = datetime.datetime.utcnow()
    
    # Also register in the AlertRegistry singleton
    registry = AlertRegistry.get_instance()
    registry.register_alert(alert)


def route_alert(alert, channels=None):
    """Routes an alert to appropriate notification channels
    
    Args:
        alert (Alert): The alert to route
        channels (list): List of AlertChannel to use, or None for default routing
        
    Returns:
        dict: Notification results for each channel
    """
    results = {}
    
    # Determine which channels to use
    if not channels:
        # Default routing based on severity
        if alert.severity in [AlertSeverity.CRITICAL, AlertSeverity.HIGH]:
            channels = [AlertChannel.PAGERDUTY, AlertChannel.SLACK, AlertChannel.EMAIL]
        elif alert.severity == AlertSeverity.MEDIUM:
            channels = [AlertChannel.SLACK, AlertChannel.EMAIL]
        else:  # LOW or INFO
            channels = [AlertChannel.SLACK]
    
    # Convert string channel names to AlertChannel enum if needed
    parsed_channels = []
    for channel in channels:
        if isinstance(channel, str):
            try:
                channel = AlertChannel[channel.upper()]
            except (KeyError, ValueError):
                logger.warning(f"Unknown alert channel: {channel}")
                continue
        parsed_channels.append(channel)
    
    # Send to each channel
    for channel in parsed_channels:
        if channel == AlertChannel.PAGERDUTY and PAGERDUTY_ENABLED:
            results[channel.value] = send_pagerduty_alert(alert)
        elif channel == AlertChannel.SLACK and SLACK_ENABLED:
            results[channel.value] = send_slack_alert(alert)
        elif channel == AlertChannel.EMAIL and EMAIL_ENABLED:
            results[channel.value] = send_email_alert(alert)
        elif channel == AlertChannel.CONSOLE:
            # Just log to console
            logger.info(f"ALERT: [{alert.severity.value if isinstance(alert.severity, enum.Enum) else alert.severity}] {alert.name} - {alert.message}")
            results[channel.value] = {'status': 'success', 'message': 'Logged to console'}
    
    # Update notification status in the alert
    for channel, result in results.items():
        try:
            channel_enum = AlertChannel(channel)
            alert.update_notification_status(channel_enum, result)
        except ValueError:
            alert.update_notification_status(channel, result)
    
    return results


def send_pagerduty_alert(alert):
    """Sends an alert to PagerDuty
    
    Args:
        alert (Alert): The alert to send
        
    Returns:
        dict: PagerDuty notification result
    """
    if not PAGERDUTY_ENABLED:
        return {'status': 'disabled', 'message': 'PagerDuty integration is disabled'}
    
    try:
        # Create PagerDuty client
        client = PagerDutyClient(
            settings.PAGERDUTY_API_KEY,
            getattr(settings, 'PAGERDUTY_SERVICE_ID', 'default')
        )
        
        # Trigger incident
        result = client.trigger_incident(alert)
        
        # If successful, store the incident ID in the alert
        if result['status'] == 'success' and 'incident_id' in result:
            alert.details['pagerduty_incident_id'] = result['incident_id']
        
        return result
    except Exception as e:
        error_message = f"Error sending alert to PagerDuty: {str(e)}"
        logger.error(error_message, exc_info=True)
        return {'status': 'error', 'message': error_message}


def send_slack_alert(alert):
    """Sends an alert to Slack
    
    Args:
        alert (Alert): The alert to send
        
    Returns:
        dict: Slack notification result
    """
    if not SLACK_ENABLED:
        return {'status': 'disabled', 'message': 'Slack integration is disabled'}
    
    try:
        # Create Slack client
        client = SlackClient(
            settings.SLACK_WEBHOOK_URL,
            getattr(settings, 'SLACK_CHANNEL', None),
            getattr(settings, 'SLACK_USERNAME', 'AlertBot')
        )
        
        # Send alert
        return client.send_alert(alert)
    except Exception as e:
        error_message = f"Error sending alert to Slack: {str(e)}"
        logger.error(error_message, exc_info=True)
        return {'status': 'error', 'message': error_message}


def send_email_alert(alert):
    """Sends an alert via email
    
    Args:
        alert (Alert): The alert to send
        
    Returns:
        dict: Email notification result
    """
    if not EMAIL_ENABLED:
        return {'status': 'disabled', 'message': 'Email notifications are disabled'}
    
    try:
        # Create SendGrid client
        client = SendGridClient()
        
        # Format subject with severity and alert name
        severity_str = alert.severity.value.upper() if isinstance(alert.severity, enum.Enum) else alert.severity.upper()
        subject = f"{severity_str} ALERT: {alert.name} - {settings.PROJECT_NAME} ({settings.ENVIRONMENT})"
        
        # Create email content
        content = f"""
        <h2>{alert.name}</h2>
        <p><strong>Severity:</strong> {severity_str}</p>
        <p><strong>Time:</strong> {alert.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
        <p><strong>Message:</strong> {alert.message}</p>
        <p><strong>Type:</strong> {alert.alert_type.value if isinstance(alert.alert_type, enum.Enum) else alert.alert_type}</p>
        
        <h3>Details:</h3>
        <pre>{json.dumps(alert.details, indent=2, sort_keys=True)}</pre>
        
        <p>
        This is an automated alert from the {settings.PROJECT_NAME} system.
        </p>
        """
        
        # Add trace ID if available
        if alert.trace_id:
            content += f"<p><strong>Trace ID:</strong> {alert.trace_id}</p>"
        
        # Send email
        result = client.send_email(
            to_email=settings.ADMIN_EMAIL,
            subject=subject,
            html_content=content,
            categories=['alert', alert.severity.value if isinstance(alert.severity, enum.Enum) else alert.severity]
        )
        
        return result
    except Exception as e:
        error_message = f"Error sending alert email: {str(e)}"
        logger.error(error_message, exc_info=True)
        return {'status': 'error', 'message': error_message}


def clear_alert(alert_id, resolution_message):
    """Clears an active alert
    
    Args:
        alert_id (str): ID of the alert to clear
        resolution_message (str): Message explaining the resolution
        
    Returns:
        dict: Clear result with status
    """
    if not ALERTING_ENABLED:
        return {'status': 'disabled', 'message': 'Alerting is disabled'}
    
    # Get the alert from registry
    registry = AlertRegistry.get_instance()
    alert = registry.get_alert(alert_id)
    
    if not alert:
        return {'status': 'error', 'message': f'Alert with ID {alert_id} not found'}
    
    # Resolve the alert
    alert.resolve(resolution_message)
    
    # If there's a PagerDuty incident ID, resolve it
    if PAGERDUTY_ENABLED and alert.details.get('pagerduty_incident_id'):
        try:
            client = PagerDutyClient(
                settings.PAGERDUTY_API_KEY,
                getattr(settings, 'PAGERDUTY_SERVICE_ID', 'default')
            )
            
            client.resolve_incident(
                alert.details['pagerduty_incident_id'],
                resolution_message
            )
        except Exception as e:
            logger.error(f"Error resolving PagerDuty incident: {str(e)}", exc_info=True)
    
    # Log the resolution
    logger.info(f"Alert {alert_id} ({alert.name}) resolved: {resolution_message}")
    
    return {
        'status': 'resolved',
        'message': 'Alert resolved successfully',
        'alert_id': alert_id
    }


def get_active_alerts(severity=None, alert_type=None, since=None):
    """Retrieves active alerts, optionally filtered
    
    Args:
        severity (AlertSeverity): Filter by severity
        alert_type (str): Filter by alert type
        since (datetime): Filter by alerts created after this time
        
    Returns:
        list: List of active alerts matching filters
    """
    registry = AlertRegistry.get_instance()
    
    # Convert string alert_type to enum if needed
    if isinstance(alert_type, str):
        try:
            alert_type = AlertType[alert_type]
        except (KeyError, ValueError):
            pass
    
    return registry.get_alerts(
        active_only=True,
        severity=severity,
        alert_type=alert_type,
        since=since
    )


def get_alert_by_id(alert_id):
    """Retrieves an alert by its ID
    
    Args:
        alert_id (str): The alert ID
        
    Returns:
        Alert: Alert object if found, None otherwise
    """
    registry = AlertRegistry.get_instance()
    return registry.get_alert(alert_id)


def cleanup_old_alerts(older_than):
    """Removes old resolved alerts from the registry
    
    Args:
        older_than (datetime): Time threshold for clearing
        
    Returns:
        int: Number of alerts cleared
    """
    registry = AlertRegistry.get_instance()
    return registry.cleanup_old_alerts(older_than)


def store_alert_artifact(alert_id, artifact_name, data, content_type):
    """Stores additional data related to an alert in S3
    
    Args:
        alert_id (str): ID of the alert
        artifact_name (str): Name for the artifact
        data (bytes): Binary data to store
        content_type (str): MIME type of the data
        
    Returns:
        dict: Storage result with artifact URL
    """
    # Get the alert
    alert = get_alert_by_id(alert_id)
    if not alert:
        return {'status': 'error', 'message': f'Alert with ID {alert_id} not found'}
    
    try:
        # Create S3 client
        s3_client = S3Client()
        
        # Generate object key
        object_key = f"alerts/{alert_id}/{artifact_name}"
        
        # Create metadata for the object
        metadata = {
            'alert_id': alert_id,
            'alert_name': alert.name,
            'artifact_name': artifact_name,
            'content_type': content_type,
            'created_at': datetime.datetime.utcnow().isoformat()
        }
        
        # We need to write the data to a temporary file since upload_file uses file path
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(data)
            temp_path = temp_file.name
        
        try:
            # Upload to S3
            bucket_name = getattr(settings, 'AWS_S3_BUCKET_NAME', None)
            
            s3_client.upload_file(
                file_path=temp_path,
                object_key=object_key,
                bucket_name=bucket_name,
                metadata=metadata
            )
            
            # Generate a URL for the artifact
            url = s3_client.generate_presigned_url(
                object_key=object_key,
                bucket_name=bucket_name,
                expiration=3600 * 24  # 24 hours
            )
            
            # Add artifact to the alert
            alert.add_artifact(artifact_name, url, content_type)
            
            return {
                'status': 'success',
                'message': 'Artifact stored successfully',
                'artifact_url': url
            }
        finally:
            # Clean up the temporary file
            os.unlink(temp_path)
            
    except Exception as e:
        error_message = f"Error storing alert artifact: {str(e)}"
        logger.error(error_message, exc_info=True)
        return {'status': 'error', 'message': error_message}