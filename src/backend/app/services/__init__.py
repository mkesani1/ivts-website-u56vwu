"""Initialization module for the services package that exports all service classes and functions for use throughout the application. 
This module provides a centralized access point for all service components that handle business logic for the IndiVillage website.
"""

from .content_service import ContentService  # Import the content service for accessing and managing content from Contentful CMS
from .file_upload_service import FileUploadService  # Import the file upload service for handling file uploads and processing
from .file_processing_service import FileProcessingService  # Import the file processing service for analyzing and processing uploaded files
from .form_processing_service import FormProcessingService  # Import the form processing service for handling form submissions
from .email_service import EmailService, EmailType, EmailStatus, EmailResult  # Import the email service for sending various types of emails
from .crm_service import CRMService  # Import the CRM service for integrating with HubSpot CRM
from .analytics_service import AnalyticsService  # Import the analytics service for tracking user behavior and events
from .security_service import SecurityService  # Import the security service for handling security-related operations

__all__ = [
    "ContentService",  # Provide access to the content service for retrieving content from Contentful CMS
    "FileUploadService",  # Provide access to the file upload service for handling file uploads
    "FileProcessingService",  # Provide access to the file processing service for analyzing uploaded files
    "FormProcessingService",  # Provide access to the form processing service for handling form submissions
    "EmailService",  # Provide access to the email service for sending various types of emails
    "CRMService",  # Provide access to the CRM service for integrating with HubSpot CRM
    "AnalyticsService",  # Provide access to the analytics service for tracking user behavior and events
    "SecurityService",  # Provide access to the security service for handling security-related operations
    "EmailType",  # Provide access to email type enumeration for email categorization
    "EmailStatus",  # Provide access to email status enumeration for tracking email sending results
    "EmailResult",  # Provide access to email result class for structured email sending results
]