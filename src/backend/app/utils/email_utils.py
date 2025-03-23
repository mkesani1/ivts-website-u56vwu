import re
import os
from typing import Dict, Optional, Any
from datetime import datetime
from enum import Enum

import jinja2  # v3.1.2
from email_validator import validate_email as validate_email_lib, EmailNotValidError  # v2.0.0

from ..core.config import settings
from ..utils.logging_utils import get_component_logger

# Initialize logger
logger = get_component_logger('email_utils')

# Regular expression for basic email validation
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

# Path to email templates directory
TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates', 'email')

# Initialize Jinja2 environment
jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(TEMPLATE_DIR),
    autoescape=True,
    trim_blocks=True,
    lstrip_blocks=True
)


class EmailTemplate(Enum):
    """Enum class defining available email templates"""
    CONTACT_CONFIRMATION = "contact_confirmation"
    DEMO_REQUEST = "demo_request"
    QUOTE_REQUEST = "quote_request"
    UPLOAD_CONFIRMATION = "upload_confirmation"
    UPLOAD_COMPLETE = "upload_complete"
    UPLOAD_FAILED = "upload_failed"
    INTERNAL_NOTIFICATION = "internal_notification"
    
    def get_filename(self) -> str:
        """Returns the filename for the template"""
        return f"{self.value.lower().replace('_', '-')}.html"


def validate_email(email: str) -> bool:
    """
    Validates an email address format
    
    Args:
        email: Email address to validate
        
    Returns:
        True if email is valid, False otherwise
    """
    if not email:
        return False
    
    try:
        # Use the email_validator library for robust validation
        validate_email_lib(email)
        return True
    except EmailNotValidError as e:
        logger.debug(f"Invalid email address: {email}, error: {str(e)}")
        return False


def format_email_address(email: str, name: Optional[str] = None) -> Optional[str]:
    """
    Formats an email address with an optional display name
    
    Args:
        email: Email address
        name: Display name (optional)
        
    Returns:
        Formatted email address (e.g., 'Name <email@example.com>')
    """
    if not validate_email(email):
        logger.warning(f"Attempted to format invalid email: {email}")
        return None
    
    if name:
        return f"{name} <{email}>"
    return email


def get_default_sender() -> str:
    """
    Returns the default sender email address with display name
    
    Returns:
        Formatted default sender email address
    """
    return format_email_address(settings.EMAIL_FROM, settings.EMAIL_FROM_NAME)


def render_template(template_name: str, context: Optional[Dict[str, Any]] = None) -> Optional[str]:
    """
    Renders an email template with the provided context
    
    Args:
        template_name: Name of the template file
        context: Context data for template rendering
        
    Returns:
        Rendered HTML content
    """
    # Ensure template name has .html extension
    if not template_name.endswith('.html'):
        template_name = f"{template_name}.html"
    
    # Create a base context with common variables if context is None
    if context is None:
        context = create_email_context({})
    else:
        # Ensure basic context variables are present
        context = create_email_context(context)
    
    try:
        template = jinja_env.get_template(template_name)
        return template.render(**context)
    except Exception as e:
        logger.error(f"Error rendering email template '{template_name}': {str(e)}")
        return None


def create_email_context(context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Creates a base context dictionary for email templates with common variables
    
    Args:
        context: Base context to extend
        
    Returns:
        Context dictionary with common variables
    """
    # Initialize an empty context if None provided
    base_context = {} if context is None else context.copy()
    
    # Add common variables if not already present
    if 'current_year' not in base_context:
        base_context['current_year'] = datetime.now().year
    
    if 'company_name' not in base_context:
        base_context['company_name'] = settings.PROJECT_NAME
    
    if 'website_url' not in base_context:
        base_context['website_url'] = "https://indivillage.com"
    
    if 'company_address' not in base_context:
        base_context['company_address'] = "IndiVillage, India"
    
    if 'unsubscribe_url' not in base_context:
        base_context['unsubscribe_url'] = "https://indivillage.com/unsubscribe"
    
    return base_context


def get_plain_text_from_html(html_content: str) -> str:
    """
    Converts HTML content to plain text for multipart emails
    
    Args:
        html_content: HTML content to convert
        
    Returns:
        Plain text version of the HTML content
    """
    if not html_content:
        return ""
    
    # Simple HTML tag replacements for basic plain text conversion
    text = html_content
    
    # Replace paragraph and div tags with newlines
    text = re.sub(r'<p[^>]*>|<div[^>]*>', '\n', text)
    
    # Replace break tags with newlines
    text = re.sub(r'<br[^>]*>', '\n', text)
    
    # Replace list items with asterisks
    text = re.sub(r'<li[^>]*>', '* ', text)
    
    # Replace horizontal rules with dashes
    text = re.sub(r'<hr[^>]*>', '\n----------\n', text)
    
    # Remove all remaining HTML tags
    text = re.sub(r'<[^>]*>', '', text)
    
    # Replace multiple newlines with double newlines
    text = re.sub(r'\n\s*\n', '\n\n', text)
    
    return text.strip()


def generate_email_subject(subject_key: str, context: Optional[Dict[str, Any]] = None) -> str:
    """
    Generates a standardized email subject line
    
    Args:
        subject_key: Key identifying the type of email
        context: Context for subject line formatting
        
    Returns:
        Formatted email subject line
    """
    # Default context
    ctx = context or {}
    
    # Subject templates for different email types
    subject_templates = {
        'contact_confirmation': "We've received your message",
        'demo_request': "Your demo request has been received",
        'quote_request': "Your quote request has been received",
        'upload_confirmation': "Your file upload has been received",
        'upload_complete': "Your file upload has been processed",
        'upload_failed': "Issue with your file upload",
        'internal_notification': "New website submission",
    }
    
    # Get the subject template or use a default
    subject_template = subject_templates.get(
        subject_key, 
        "Information from {company_name}"
    )
    
    # Format the subject template with the context variables
    subject = subject_template.format(
        company_name=settings.PROJECT_NAME,
        **ctx
    )
    
    # Prepend company name if not already included
    if settings.PROJECT_NAME not in subject:
        subject = f"{settings.PROJECT_NAME}: {subject}"
    
    return subject