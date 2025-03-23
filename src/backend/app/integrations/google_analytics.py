"""
Google Analytics integration module for IndiVillage backend.

This module provides functionality to track user interactions, page views, and business
events in Google Analytics. It implements server-side tracking using the Measurement
Protocol API, allowing comprehensive tracking of user behavior and business metrics.
"""

import json
import typing
import time
import uuid
import datetime
import requests  # version ^2.28.0

from ..core.config import settings, GOOGLE_ANALYTICS_ID, ENVIRONMENT
from ..core.logging import get_logger
from ..monitoring.metrics import record_integration_metrics

# Configure logger for this module
logger = get_logger(__name__)

# Google Analytics Measurement Protocol API endpoints
GA_MEASUREMENT_PROTOCOL_URL = "https://www.google-analytics.com/mp/collect"
GA_MEASUREMENT_DEBUG_URL = "https://www.google-analytics.com/debug/mp/collect"

# Get Google Analytics configuration from settings
GA_API_SECRET = getattr(settings, 'GOOGLE_ANALYTICS_API_SECRET', '')
GA_MEASUREMENT_ID = getattr(settings, 'GOOGLE_ANALYTICS_ID', '')

# Check if analytics is enabled based on configuration
ANALYTICS_ENABLED = (
    GA_MEASUREMENT_ID and 
    GA_API_SECRET and 
    getattr(settings, 'ANALYTICS_ENABLED', True)
)


def is_analytics_enabled() -> bool:
    """
    Check if Google Analytics tracking is enabled based on configuration.
    
    Returns:
        True if Google Analytics is enabled, False otherwise
    """
    return ANALYTICS_ENABLED


def send_ga_event(client_id: str, event_name: str, event_params: dict) -> bool:
    """
    Send an event to Google Analytics using the Measurement Protocol.
    
    Args:
        client_id: Client identifier for the user
        event_name: Name of the event to track
        event_params: Parameters for the event
        
    Returns:
        True if the event was sent successfully, False otherwise
    """
    # Check if analytics is enabled
    if not is_analytics_enabled():
        logger.debug("Google Analytics is disabled, skipping event tracking")
        return False
    
    # Construct the URL with measurement ID and API secret
    base_url = GA_MEASUREMENT_DEBUG_URL if settings.ENVIRONMENT == "development" else GA_MEASUREMENT_PROTOCOL_URL
    url = f"{base_url}?measurement_id={GA_MEASUREMENT_ID}&api_secret={GA_API_SECRET}"
    
    # Prepare the event payload
    payload = {
        "client_id": client_id,
        "events": [{
            "name": event_name,
            "params": event_params
        }]
    }
    
    # Add timestamp to the event
    event_params["timestamp"] = int(datetime.datetime.now().timestamp() * 1000)
    
    start_time = time.time()
    success = False
    
    try:
        # Send the event using requests
        response = requests.post(
            url,
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"},
            timeout=5  # 5 second timeout
        )
        
        success = 200 <= response.status_code < 300
        
        if success:
            logger.debug(f"Successfully sent event '{event_name}' to Google Analytics")
        else:
            logger.warning(
                f"Failed to send event to Google Analytics: {response.status_code} - {response.text}"
            )
            
        return success
        
    except Exception as e:
        logger.error(f"Error sending event to Google Analytics: {str(e)}", exc_info=True)
        return False
    finally:
        # Record metrics for the Google Analytics call
        duration_ms = (time.time() - start_time) * 1000
        record_integration_metrics(
            "google_analytics", 
            "send_event", 
            duration_ms, 
            success=success
        )


def generate_client_id() -> str:
    """
    Generate a unique client ID for anonymous tracking.
    
    Returns:
        A unique client ID
    """
    return str(uuid.uuid4())


def track_pageview(page_path: str, page_title: str, client_id: str = None,
                  additional_params: dict = None) -> bool:
    """
    Track a page view event in Google Analytics.
    
    Args:
        page_path: Path of the page viewed
        page_title: Title of the page viewed
        client_id: Client identifier (generated if not provided)
        additional_params: Additional parameters to include
        
    Returns:
        True if the event was sent successfully, False otherwise
    """
    # Generate client ID if not provided
    client_id = client_id or generate_client_id()
    
    # Create event parameters
    event_params = {
        "page_path": page_path,
        "page_title": page_title,
    }
    
    # Add additional parameters if provided
    if additional_params:
        event_params.update(additional_params)
    
    # Send the pageview event
    return send_ga_event(client_id, "page_view", event_params)


def track_event(category: str, action: str, label: str = None, value: int = None,
               client_id: str = None, additional_params: dict = None) -> bool:
    """
    Track a custom event in Google Analytics.
    
    Args:
        category: Event category
        action: Event action
        label: Event label (optional)
        value: Event value (optional)
        client_id: Client identifier (generated if not provided)
        additional_params: Additional parameters to include
        
    Returns:
        True if the event was sent successfully, False otherwise
    """
    # Generate client ID if not provided
    client_id = client_id or generate_client_id()
    
    # Create event parameters
    event_params = {
        "event_category": category,
        "event_action": action,
    }
    
    # Add optional parameters if provided
    if label:
        event_params["event_label"] = label
    
    if value is not None:
        event_params["event_value"] = value
    
    # Add additional parameters if provided
    if additional_params:
        event_params.update(additional_params)
    
    # Send the custom event
    return send_ga_event(client_id, f"{category}_{action}", event_params)


def track_form_submission(form_type: str, success: bool, form_data: dict = None, 
                         client_id: str = None) -> bool:
    """
    Track a form submission event in Google Analytics.
    
    Args:
        form_type: Type of form submitted
        success: Whether the submission was successful
        form_data: Form submission data (sensitive data will be removed)
        client_id: Client identifier (generated if not provided)
        
    Returns:
        True if the event was sent successfully, False otherwise
    """
    # Generate client ID if not provided
    client_id = client_id or generate_client_id()
    
    # Create event parameters
    event_params = {
        "form_type": form_type,
        "form_success": success,
    }
    
    # Add sanitized form data if provided
    if form_data:
        sanitized_data = sanitize_event_data(form_data)
        event_params.update(sanitized_data)
    
    # Send the form submission event
    return send_ga_event(client_id, "form_submission", event_params)


def track_file_upload(file_type: str, file_size: int, success: bool, metadata: dict = None, 
                     client_id: str = None) -> bool:
    """
    Track a file upload event in Google Analytics.
    
    Args:
        file_type: Type of file uploaded
        file_size: Size of the file in bytes
        success: Whether the upload was successful
        metadata: Additional metadata about the upload
        client_id: Client identifier (generated if not provided)
        
    Returns:
        True if the event was sent successfully, False otherwise
    """
    # Generate client ID if not provided
    client_id = client_id or generate_client_id()
    
    # Create event parameters
    event_params = {
        "file_type": file_type,
        "file_size": file_size,
        "upload_success": success,
    }
    
    # Add metadata if provided
    if metadata:
        event_params.update(metadata)
    
    # Send the file upload event
    return send_ga_event(client_id, "file_upload", event_params)


def track_demo_request(service_interest: str, success: bool, request_data: dict = None, 
                      client_id: str = None) -> bool:
    """
    Track a demo request event in Google Analytics.
    
    Args:
        service_interest: Service the demo is for
        success: Whether the request was successful
        request_data: Additional request data (sensitive data will be removed)
        client_id: Client identifier (generated if not provided)
        
    Returns:
        True if the event was sent successfully, False otherwise
    """
    # Generate client ID if not provided
    client_id = client_id or generate_client_id()
    
    # Create event parameters
    event_params = {
        "service_interest": service_interest,
        "request_success": success,
    }
    
    # Add sanitized request data if provided
    if request_data:
        sanitized_data = sanitize_event_data(request_data)
        event_params.update(sanitized_data)
    
    # Send the demo request event
    return send_ga_event(client_id, "demo_request", event_params)


def track_quote_request(service_interest: str, success: bool, request_data: dict = None, 
                       client_id: str = None) -> bool:
    """
    Track a quote request event in Google Analytics.
    
    Args:
        service_interest: Service the quote is for
        success: Whether the request was successful
        request_data: Additional request data (sensitive data will be removed)
        client_id: Client identifier (generated if not provided)
        
    Returns:
        True if the event was sent successfully, False otherwise
    """
    # Generate client ID if not provided
    client_id = client_id or generate_client_id()
    
    # Create event parameters
    event_params = {
        "service_interest": service_interest,
        "request_success": success,
    }
    
    # Add sanitized request data if provided
    if request_data:
        sanitized_data = sanitize_event_data(request_data)
        event_params.update(sanitized_data)
    
    # Send the quote request event
    return send_ga_event(client_id, "quote_request", event_params)


def sanitize_event_data(data: dict) -> dict:
    """
    Remove sensitive information from event data before sending to Google Analytics.
    
    Args:
        data: Data dictionary to sanitize
        
    Returns:
        Sanitized data dictionary
    """
    # Create a copy of the input data
    sanitized = data.copy() if data else {}
    
    # Define sensitive fields to remove
    sensitive_fields = [
        'email', 'phone', 'name', 'first_name', 'last_name', 'address',
        'password', 'credit_card', 'card_number', 'ssn', 'social_security',
        'secret', 'token'
    ]
    
    # Remove or mask sensitive fields
    for field in sensitive_fields:
        if field in sanitized:
            sanitized[field] = "***REDACTED***"
    
    return sanitized


def track_service_interest(service_slug: str, interaction_type: str, additional_data: dict = None, 
                          client_id: str = None) -> bool:
    """
    Track user interest in a specific service.
    
    Args:
        service_slug: Slug/identifier of the service
        interaction_type: Type of interaction with the service
        additional_data: Additional interaction data
        client_id: Client identifier (generated if not provided)
        
    Returns:
        True if the event was sent successfully, False otherwise
    """
    # Generate client ID if not provided
    client_id = client_id or generate_client_id()
    
    # Create event parameters
    event_params = {
        "service_slug": service_slug,
        "interaction_type": interaction_type,
    }
    
    # Add additional data if provided
    if additional_data:
        event_params.update(additional_data)
    
    # Send the service interaction event
    return send_ga_event(client_id, "service_interaction", event_params)


def track_impact_story_view(story_slug: str, story_title: str, additional_data: dict = None, 
                           client_id: str = None) -> bool:
    """
    Track views of impact stories.
    
    Args:
        story_slug: Slug/identifier of the impact story
        story_title: Title of the impact story
        additional_data: Additional view data
        client_id: Client identifier (generated if not provided)
        
    Returns:
        True if the event was sent successfully, False otherwise
    """
    # Generate client ID if not provided
    client_id = client_id or generate_client_id()
    
    # Create event parameters
    event_params = {
        "story_slug": story_slug,
        "story_title": story_title,
    }
    
    # Add additional data if provided
    if additional_data:
        event_params.update(additional_data)
    
    # Send the impact story view event
    return send_ga_event(client_id, "impact_story_view", event_params)


def track_case_study_view(case_study_slug: str, case_study_title: str, additional_data: dict = None, 
                         client_id: str = None) -> bool:
    """
    Track views of case studies.
    
    Args:
        case_study_slug: Slug/identifier of the case study
        case_study_title: Title of the case study
        additional_data: Additional view data
        client_id: Client identifier (generated if not provided)
        
    Returns:
        True if the event was sent successfully, False otherwise
    """
    # Generate client ID if not provided
    client_id = client_id or generate_client_id()
    
    # Create event parameters
    event_params = {
        "case_study_slug": case_study_slug,
        "case_study_title": case_study_title,
    }
    
    # Add additional data if provided
    if additional_data:
        event_params.update(additional_data)
    
    # Send the case study view event
    return send_ga_event(client_id, "case_study_view", event_params)


class GoogleAnalyticsClient:
    """Client class for interacting with Google Analytics Measurement Protocol"""
    
    def __init__(self, measurement_id: str = None, api_secret: str = None, debug_mode: bool = None):
        """
        Initialize the Google Analytics client.
        
        Args:
            measurement_id: Google Analytics measurement ID (default: from settings)
            api_secret: Google Analytics API secret (default: from settings)
            debug_mode: Whether to use debug mode (default: based on environment)
        """
        self.measurement_id = measurement_id or GA_MEASUREMENT_ID
        self.api_secret = api_secret or GA_API_SECRET
        # Set debug mode based on parameter or environment setting
        self.debug_mode = debug_mode if debug_mode is not None else settings.ENVIRONMENT == "development"
        # Use debug URL if in debug mode
        self.base_url = GA_MEASUREMENT_DEBUG_URL if self.debug_mode else GA_MEASUREMENT_PROTOCOL_URL
        
        logger.info(f"Google Analytics client initialized with measurement ID: {self.measurement_id[:5] if self.measurement_id else 'None'} "
                    f"in {'debug' if self.debug_mode else 'production'} mode")
    
    def is_enabled(self) -> bool:
        """
        Check if the Google Analytics client is properly configured.
        
        Returns:
            True if the client is properly configured, False otherwise
        """
        return bool(self.measurement_id and self.api_secret)
    
    def send_event(self, client_id: str, event_name: str, event_params: dict) -> bool:
        """
        Send an event to Google Analytics.
        
        Args:
            client_id: Client identifier for the user
            event_name: Name of the event to track
            event_params: Parameters for the event
            
        Returns:
            True if the event was sent successfully, False otherwise
        """
        if not self.is_enabled():
            logger.debug("Google Analytics is not properly configured, skipping event tracking")
            return False
        
        start_time = time.time()
        success = False
        
        try:
            # Construct the full URL with API parameters
            url = f"{self.base_url}?measurement_id={self.measurement_id}&api_secret={self.api_secret}"
            
            # Prepare the event payload
            payload = {
                "client_id": client_id,
                "events": [{
                    "name": event_name,
                    "params": event_params
                }]
            }
            
            # Add timestamp to the event
            event_params["timestamp"] = int(datetime.datetime.now().timestamp() * 1000)
            
            # Send the event using requests
            response = requests.post(
                url,
                data=json.dumps(payload),
                headers={"Content-Type": "application/json"},
                timeout=5  # 5 second timeout
            )
            
            success = 200 <= response.status_code < 300
            
            if success:
                logger.debug(f"Successfully sent event '{event_name}' to Google Analytics")
            else:
                logger.warning(
                    f"Failed to send event to Google Analytics: {response.status_code} - {response.text}"
                )
                
            return success
            
        except Exception as e:
            logger.error(f"Error sending event to Google Analytics: {str(e)}", exc_info=True)
            return False
        finally:
            # Record metrics for the Google Analytics call
            duration_ms = (time.time() - start_time) * 1000
            record_integration_metrics(
                "google_analytics", 
                "send_event", 
                duration_ms, 
                success=success
            )
    
    def track_pageview(self, page_path: str, page_title: str, client_id: str = None,
                      additional_params: dict = None) -> bool:
        """
        Track a page view event.
        
        Args:
            page_path: Path of the page viewed
            page_title: Title of the page viewed
            client_id: Client identifier (generated if not provided)
            additional_params: Additional parameters to include
            
        Returns:
            True if the event was sent successfully, False otherwise
        """
        # Create event parameters
        event_params = {
            "page_path": page_path,
            "page_title": page_title,
        }
        
        # Add additional parameters if provided
        if additional_params:
            event_params.update(additional_params)
        
        # Use the provided client_id or generate a new one
        client_id = client_id or generate_client_id()
        
        # Send the pageview event
        return self.send_event(client_id, "page_view", event_params)
    
    def track_event(self, category: str, action: str, label: str = None, value: int = None,
                   client_id: str = None, additional_params: dict = None) -> bool:
        """
        Track a custom event.
        
        Args:
            category: Event category
            action: Event action
            label: Event label (optional)
            value: Event value (optional)
            client_id: Client identifier (generated if not provided)
            additional_params: Additional parameters to include
            
        Returns:
            True if the event was sent successfully, False otherwise
        """
        # Create event parameters
        event_params = {
            "event_category": category,
            "event_action": action,
        }
        
        # Add optional parameters if provided
        if label:
            event_params["event_label"] = label
        
        if value is not None:
            event_params["event_value"] = value
        
        # Add additional parameters if provided
        if additional_params:
            event_params.update(additional_params)
        
        # Use the provided client_id or generate a new one
        client_id = client_id or generate_client_id()
        
        # Send the custom event
        return self.send_event(client_id, f"{category}_{action}", event_params)


# Create a singleton instance of GoogleAnalyticsClient for application-wide use
analytics_client = GoogleAnalyticsClient()