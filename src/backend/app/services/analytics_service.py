"""
Service module that provides analytics tracking functionality for the IndiVillage application.
This service acts as a bridge between application events and analytics platforms, tracking
user interactions, form submissions, file uploads, and business metrics to provide insights
into user behavior and application performance.
"""

import typing
import uuid
import datetime
import json

from ..core.config import settings, ENVIRONMENT
from ..core.logging import get_logger
from ..integrations.google_analytics import (
    is_analytics_enabled, track_event, track_form_submission,
    track_file_upload, track_demo_request, track_quote_request,
    track_service_interest, track_impact_story_view, track_case_study_view
)
from ..monitoring.metrics import (
    record_business_metric, record_form_submission_metrics,
    record_file_upload_metrics, record_file_processing_metrics
)

# Configure logger for this module
logger = get_logger(__name__)


def is_tracking_enabled() -> bool:
    """
    Checks if analytics tracking is enabled based on configuration
    
    Returns:
        bool: True if analytics tracking is enabled, False otherwise
    """
    # Check both application settings and Google Analytics configuration
    return getattr(settings, 'ANALYTICS_ENABLED', False) and is_analytics_enabled()


def sanitize_tracking_data(data: dict) -> dict:
    """
    Removes sensitive information from data before sending to analytics
    
    Args:
        data: Data dictionary to sanitize
        
    Returns:
        dict: Sanitized data dictionary
    """
    if not data:
        return {}
    
    # Create a copy of the input data
    sanitized = data.copy()
    
    # Define sensitive fields to remove
    sensitive_fields = [
        'email', 'phone', 'name', 'first_name', 'last_name', 
        'password', 'credit_card', 'card_number', 'ssn', 'address',
        'token', 'secret', 'api_key'
    ]
    
    # Remove or mask sensitive fields
    for field in sensitive_fields:
        if field in sanitized:
            sanitized[field] = "***REDACTED***"
    
    return sanitized


def track_custom_event(
    category: str, 
    action: str, 
    label: str = None, 
    value: int = None, 
    additional_data: dict = None,
    client_id: str = None, 
    trace_id: str = None
) -> bool:
    """
    Tracks a custom event in analytics platforms
    
    Args:
        category: Event category
        action: Event action
        label: Optional event label
        value: Optional event value
        additional_data: Additional event data
        client_id: Client identifier for tracking
        trace_id: Trace identifier for correlation
        
    Returns:
        bool: True if event was tracked successfully, False otherwise
    """
    # Check if tracking is enabled
    if not is_tracking_enabled():
        logger.debug("Analytics tracking is disabled, skipping custom event tracking")
        return False
    
    # Sanitize additional data
    if additional_data:
        additional_data = sanitize_tracking_data(additional_data)
    
    # Track in Google Analytics
    success = track_event(category, action, label, value, client_id, additional_data)
    
    # Record business metric for internal monitoring
    if success:
        metric_name = f"{category}_{action}"
        record_business_metric(metric_name, 1, {
            "category": category,
            "action": action,
            "label": label or "none"
        }, trace_id)
    
    logger.debug(
        f"Tracked custom event: {category} - {action} - {label or 'none'} - {value or 'none'}"
    )
    
    return success


def track_form_submission_event(
    form_type: str, 
    success: bool, 
    form_data: dict = None,
    client_id: str = None, 
    trace_id: str = None
) -> bool:
    """
    Tracks a form submission event in analytics platforms
    
    Args:
        form_type: Type of form submitted
        success: Whether the submission was successful
        form_data: Form submission data
        client_id: Client identifier for tracking
        trace_id: Trace identifier for correlation
        
    Returns:
        bool: True if event was tracked successfully, False otherwise
    """
    # Check if tracking is enabled
    if not is_tracking_enabled():
        logger.debug("Analytics tracking is disabled, skipping form submission tracking")
        return False
    
    # Sanitize form data
    if form_data:
        form_data = sanitize_tracking_data(form_data)
    
    # Track in Google Analytics
    ga_success = track_form_submission(form_type, success, form_data, client_id)
    
    # Record metrics for internal monitoring
    record_form_submission_metrics(form_type, success, trace_id=trace_id)
    
    logger.debug(
        f"Tracked form submission: {form_type} - {'Success' if success else 'Failed'}"
    )
    
    return ga_success


def track_file_upload_event(
    file_type: str, 
    file_size: int, 
    success: bool,
    metadata: dict = None, 
    client_id: str = None,
    trace_id: str = None
) -> bool:
    """
    Tracks a file upload event in analytics platforms
    
    Args:
        file_type: Type of file uploaded
        file_size: Size of the file in bytes
        success: Whether the upload was successful
        metadata: Additional metadata about the upload
        client_id: Client identifier for tracking
        trace_id: Trace identifier for correlation
        
    Returns:
        bool: True if event was tracked successfully, False otherwise
    """
    # Check if tracking is enabled
    if not is_tracking_enabled():
        logger.debug("Analytics tracking is disabled, skipping file upload tracking")
        return False
    
    # Sanitize metadata
    if metadata:
        metadata = sanitize_tracking_data(metadata)
    
    # Track in Google Analytics
    ga_success = track_file_upload(file_type, file_size, success, metadata, client_id)
    
    # Record metrics for internal monitoring
    record_file_upload_metrics(file_type, file_size, 0, success, trace_id=trace_id)
    
    logger.debug(
        f"Tracked file upload: {file_type} - {file_size} bytes - {'Success' if success else 'Failed'}"
    )
    
    return ga_success


def track_file_processing_event(
    file_type: str, 
    file_size: int, 
    processing_duration_ms: float, 
    success: bool,
    results: dict = None, 
    client_id: str = None,
    trace_id: str = None
) -> bool:
    """
    Tracks a file processing event in analytics platforms
    
    Args:
        file_type: Type of file processed
        file_size: Size of file in bytes
        processing_duration_ms: Processing duration in milliseconds
        success: Whether the processing was successful
        results: Processing results
        client_id: Client identifier for tracking
        trace_id: Trace identifier for correlation
        
    Returns:
        bool: True if event was tracked successfully, False otherwise
    """
    # Check if tracking is enabled
    if not is_tracking_enabled():
        logger.debug("Analytics tracking is disabled, skipping file processing tracking")
        return False
    
    # Sanitize results
    if results:
        results = sanitize_tracking_data(results)
    
    # Track in Google Analytics
    ga_success = track_event(
        "file_processing", 
        file_type, 
        f"{'Success' if success else 'Failed'}", 
        int(processing_duration_ms),
        client_id,
        results
    )
    
    # Record metrics for internal monitoring
    record_file_processing_metrics(
        file_type, file_size, processing_duration_ms, success, trace_id=trace_id
    )
    
    logger.debug(
        f"Tracked file processing: {file_type} - {file_size} bytes - "
        f"{processing_duration_ms}ms - {'Success' if success else 'Failed'}"
    )
    
    return ga_success


def track_demo_request_event(
    service_interest: str, 
    success: bool, 
    request_data: dict = None, 
    client_id: str = None,
    trace_id: str = None
) -> bool:
    """
    Tracks a demo request event in analytics platforms
    
    Args:
        service_interest: Service the demo is for
        success: Whether the request was successful
        request_data: Additional request data
        client_id: Client identifier for tracking
        trace_id: Trace identifier for correlation
        
    Returns:
        bool: True if event was tracked successfully, False otherwise
    """
    # Check if tracking is enabled
    if not is_tracking_enabled():
        logger.debug("Analytics tracking is disabled, skipping demo request tracking")
        return False
    
    # Sanitize request data
    if request_data:
        request_data = sanitize_tracking_data(request_data)
    
    # Track in Google Analytics
    ga_success = track_demo_request(service_interest, success, request_data, client_id)
    
    # Record business metric for internal monitoring
    record_business_metric("demo_requests", 1, {
        "service_interest": service_interest,
        "success": success
    }, trace_id)
    
    logger.debug(
        f"Tracked demo request: {service_interest} - {'Success' if success else 'Failed'}"
    )
    
    return ga_success


def track_quote_request_event(
    service_interest: str, 
    success: bool, 
    request_data: dict = None, 
    client_id: str = None,
    trace_id: str = None
) -> bool:
    """
    Tracks a quote request event in analytics platforms
    
    Args:
        service_interest: Service the quote is for
        success: Whether the request was successful
        request_data: Additional request data
        client_id: Client identifier for tracking
        trace_id: Trace identifier for correlation
        
    Returns:
        bool: True if event was tracked successfully, False otherwise
    """
    # Check if tracking is enabled
    if not is_tracking_enabled():
        logger.debug("Analytics tracking is disabled, skipping quote request tracking")
        return False
    
    # Sanitize request data
    if request_data:
        request_data = sanitize_tracking_data(request_data)
    
    # Track in Google Analytics
    ga_success = track_quote_request(service_interest, success, request_data, client_id)
    
    # Record business metric for internal monitoring
    record_business_metric("quote_requests", 1, {
        "service_interest": service_interest,
        "success": success
    }, trace_id)
    
    logger.debug(
        f"Tracked quote request: {service_interest} - {'Success' if success else 'Failed'}"
    )
    
    return ga_success


def track_service_interest_event(
    service_slug: str, 
    interaction_type: str,
    additional_data: dict = None, 
    client_id: str = None,
    trace_id: str = None
) -> bool:
    """
    Tracks a service interest event in analytics platforms
    
    Args:
        service_slug: Slug/identifier of the service
        interaction_type: Type of interaction with the service
        additional_data: Additional interaction data
        client_id: Client identifier for tracking
        trace_id: Trace identifier for correlation
        
    Returns:
        bool: True if event was tracked successfully, False otherwise
    """
    # Check if tracking is enabled
    if not is_tracking_enabled():
        logger.debug("Analytics tracking is disabled, skipping service interest tracking")
        return False
    
    # Sanitize additional data
    if additional_data:
        additional_data = sanitize_tracking_data(additional_data)
    
    # Track in Google Analytics
    ga_success = track_service_interest(service_slug, interaction_type, additional_data, client_id)
    
    # Record business metric for internal monitoring
    record_business_metric("service_interest", 1, {
        "service_slug": service_slug,
        "interaction_type": interaction_type
    }, trace_id)
    
    logger.debug(
        f"Tracked service interest: {service_slug} - {interaction_type}"
    )
    
    return ga_success


def track_impact_story_view_event(
    story_slug: str, 
    story_title: str,
    additional_data: dict = None, 
    client_id: str = None,
    trace_id: str = None
) -> bool:
    """
    Tracks an impact story view event in analytics platforms
    
    Args:
        story_slug: Slug/identifier of the impact story
        story_title: Title of the impact story
        additional_data: Additional view data
        client_id: Client identifier for tracking
        trace_id: Trace identifier for correlation
        
    Returns:
        bool: True if event was tracked successfully, False otherwise
    """
    # Check if tracking is enabled
    if not is_tracking_enabled():
        logger.debug("Analytics tracking is disabled, skipping impact story view tracking")
        return False
    
    # Sanitize additional data
    if additional_data:
        additional_data = sanitize_tracking_data(additional_data)
    
    # Track in Google Analytics
    ga_success = track_impact_story_view(story_slug, story_title, additional_data, client_id)
    
    # Record business metric for internal monitoring
    record_business_metric("impact_story_views", 1, {
        "story_slug": story_slug,
        "story_title": story_title
    }, trace_id)
    
    logger.debug(
        f"Tracked impact story view: {story_slug} - {story_title}"
    )
    
    return ga_success


def track_case_study_view_event(
    case_study_slug: str, 
    case_study_title: str,
    additional_data: dict = None, 
    client_id: str = None,
    trace_id: str = None
) -> bool:
    """
    Tracks a case study view event in analytics platforms
    
    Args:
        case_study_slug: Slug/identifier of the case study
        case_study_title: Title of the case study
        additional_data: Additional view data
        client_id: Client identifier for tracking
        trace_id: Trace identifier for correlation
        
    Returns:
        bool: True if event was tracked successfully, False otherwise
    """
    # Check if tracking is enabled
    if not is_tracking_enabled():
        logger.debug("Analytics tracking is disabled, skipping case study view tracking")
        return False
    
    # Sanitize additional data
    if additional_data:
        additional_data = sanitize_tracking_data(additional_data)
    
    # Track in Google Analytics
    ga_success = track_case_study_view(case_study_slug, case_study_title, additional_data, client_id)
    
    # Record business metric for internal monitoring
    record_business_metric("case_study_views", 1, {
        "case_study_slug": case_study_slug,
        "case_study_title": case_study_title
    }, trace_id)
    
    logger.debug(
        f"Tracked case study view: {case_study_slug} - {case_study_title}"
    )
    
    return ga_success


def generate_client_id(existing_client_id: str = None) -> str:
    """
    Generates a unique client ID for anonymous tracking if not provided
    
    Args:
        existing_client_id: Existing client ID to use if provided
        
    Returns:
        str: Client ID for analytics tracking
    """
    if existing_client_id:
        return existing_client_id
    
    # Generate a new UUID
    return str(uuid.uuid4())


class AnalyticsService:
    """
    Service class for tracking analytics events in the application
    """
    
    def __init__(self):
        """
        Initializes the AnalyticsService
        """
        self._tracking_enabled = is_tracking_enabled()
        logger.info(f"Analytics service initialized. Tracking enabled: {self._tracking_enabled}")
    
    def is_enabled(self) -> bool:
        """
        Checks if analytics tracking is enabled
        
        Returns:
            bool: True if tracking is enabled, False otherwise
        """
        return self._tracking_enabled
    
    def track_custom_event(self, category: str, action: str, label: str = None, 
                          value: int = None, additional_data: dict = None,
                          client_id: str = None, trace_id: str = None) -> bool:
        """
        Tracks a custom event in analytics platforms
        
        Args:
            category: Event category
            action: Event action
            label: Optional event label
            value: Optional event value
            additional_data: Additional event data
            client_id: Client identifier for tracking
            trace_id: Trace identifier for correlation
            
        Returns:
            bool: True if event was tracked successfully, False otherwise
        """
        return track_custom_event(
            category, action, label, value, additional_data, client_id, trace_id
        )
    
    def track_form_submission(self, form_type: str, success: bool, form_data: dict = None,
                             client_id: str = None, trace_id: str = None) -> bool:
        """
        Tracks a form submission event in analytics platforms
        
        Args:
            form_type: Type of form submitted
            success: Whether the submission was successful
            form_data: Form submission data
            client_id: Client identifier for tracking
            trace_id: Trace identifier for correlation
            
        Returns:
            bool: True if event was tracked successfully, False otherwise
        """
        return track_form_submission_event(
            form_type, success, form_data, client_id, trace_id
        )
    
    def track_file_upload(self, file_type: str, file_size: int, success: bool,
                         metadata: dict = None, client_id: str = None,
                         trace_id: str = None) -> bool:
        """
        Tracks a file upload event in analytics platforms
        
        Args:
            file_type: Type of file uploaded
            file_size: Size of file in bytes
            success: Whether the upload was successful
            metadata: Additional metadata about the upload
            client_id: Client identifier for tracking
            trace_id: Trace identifier for correlation
            
        Returns:
            bool: True if event was tracked successfully, False otherwise
        """
        return track_file_upload_event(
            file_type, file_size, success, metadata, client_id, trace_id
        )
    
    def track_file_processing(self, file_type: str, file_size: int, 
                             processing_duration_ms: float, success: bool,
                             results: dict = None, client_id: str = None,
                             trace_id: str = None) -> bool:
        """
        Tracks a file processing event in analytics platforms
        
        Args:
            file_type: Type of file processed
            file_size: Size of file in bytes
            processing_duration_ms: Processing duration in milliseconds
            success: Whether the processing was successful
            results: Processing results
            client_id: Client identifier for tracking
            trace_id: Trace identifier for correlation
            
        Returns:
            bool: True if event was tracked successfully, False otherwise
        """
        return track_file_processing_event(
            file_type, file_size, processing_duration_ms, success, 
            results, client_id, trace_id
        )
    
    def track_demo_request(self, service_interest: str, success: bool, 
                          request_data: dict = None, client_id: str = None,
                          trace_id: str = None) -> bool:
        """
        Tracks a demo request event in analytics platforms
        
        Args:
            service_interest: Service the demo is for
            success: Whether the request was successful
            request_data: Additional request data
            client_id: Client identifier for tracking
            trace_id: Trace identifier for correlation
            
        Returns:
            bool: True if event was tracked successfully, False otherwise
        """
        return track_demo_request_event(
            service_interest, success, request_data, client_id, trace_id
        )
    
    def track_quote_request(self, service_interest: str, success: bool, 
                           request_data: dict = None, client_id: str = None,
                           trace_id: str = None) -> bool:
        """
        Tracks a quote request event in analytics platforms
        
        Args:
            service_interest: Service the quote is for
            success: Whether the request was successful
            request_data: Additional request data
            client_id: Client identifier for tracking
            trace_id: Trace identifier for correlation
            
        Returns:
            bool: True if event was tracked successfully, False otherwise
        """
        return track_quote_request_event(
            service_interest, success, request_data, client_id, trace_id
        )
    
    def track_service_interest(self, service_slug: str, interaction_type: str,
                              additional_data: dict = None, client_id: str = None,
                              trace_id: str = None) -> bool:
        """
        Tracks a service interest event in analytics platforms
        
        Args:
            service_slug: Slug/identifier of the service
            interaction_type: Type of interaction with the service
            additional_data: Additional interaction data
            client_id: Client identifier for tracking
            trace_id: Trace identifier for correlation
            
        Returns:
            bool: True if event was tracked successfully, False otherwise
        """
        return track_service_interest_event(
            service_slug, interaction_type, additional_data, client_id, trace_id
        )
    
    def track_impact_story_view(self, story_slug: str, story_title: str,
                               additional_data: dict = None, client_id: str = None,
                               trace_id: str = None) -> bool:
        """
        Tracks an impact story view event in analytics platforms
        
        Args:
            story_slug: Slug/identifier of the impact story
            story_title: Title of the impact story
            additional_data: Additional view data
            client_id: Client identifier for tracking
            trace_id: Trace identifier for correlation
            
        Returns:
            bool: True if event was tracked successfully, False otherwise
        """
        return track_impact_story_view_event(
            story_slug, story_title, additional_data, client_id, trace_id
        )
    
    def track_case_study_view(self, case_study_slug: str, case_study_title: str,
                             additional_data: dict = None, client_id: str = None,
                             trace_id: str = None) -> bool:
        """
        Tracks a case study view event in analytics platforms
        
        Args:
            case_study_slug: Slug/identifier of the case study
            case_study_title: Title of the case study
            additional_data: Additional view data
            client_id: Client identifier for tracking
            trace_id: Trace identifier for correlation
            
        Returns:
            bool: True if event was tracked successfully, False otherwise
        """
        return track_case_study_view_event(
            case_study_slug, case_study_title, additional_data, client_id, trace_id
        )
    
    def generate_client_id(self, existing_client_id: str = None) -> str:
        """
        Generates a unique client ID for anonymous tracking if not provided
        
        Args:
            existing_client_id: Existing client ID to use if provided
            
        Returns:
            str: Client ID for analytics tracking
        """
        return generate_client_id(existing_client_id)


# Create a singleton instance for application-wide use
analytics_service = AnalyticsService()

# Export the service, singleton instance, and utility functions
__all__ = [
    'AnalyticsService',
    'analytics_service',
    'is_tracking_enabled',
    'track_custom_event',
    'track_form_submission_event',
    'track_file_upload_event',
    'track_file_processing_event',
    'track_demo_request_event',
    'track_quote_request_event',
    'track_service_interest_event',
    'track_impact_story_view_event',
    'track_case_study_view_event',
    'generate_client_id'
]