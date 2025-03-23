import os
from ..utils.logging_utils import get_component_logger

# Set up logger for the templates package
logger = get_component_logger('templates')

# Define template directory paths
TEMPLATE_DIR = os.path.dirname(__file__)
EMAIL_TEMPLATE_DIR = os.path.join(TEMPLATE_DIR, 'email')

def get_template_path(template_name, subdir=None):
    """
    Returns the absolute path to a template file
    
    Args:
        template_name (str): The name of the template file
        subdir (str): Optional subdirectory within the templates directory
        
    Returns:
        str: Absolute path to the template file
    """
    # Ensure template_name ends with .html if not already
    if not template_name.endswith('.html'):
        template_name = f"{template_name}.html"
    
    # Construct the template path based on whether a subdirectory is provided
    if subdir:
        template_path = os.path.join(TEMPLATE_DIR, subdir, template_name)
    else:
        template_path = os.path.join(TEMPLATE_DIR, template_name)
    
    logger.debug(f"Template path resolved to: {template_path}")
    
    return template_path

def get_email_template_path(template_name):
    """
    Returns the absolute path to an email template file
    
    Args:
        template_name (str): The name of the email template file
        
    Returns:
        str: Absolute path to the email template file
    """
    email_template_path = get_template_path(template_name, 'email')
    
    logger.debug(f"Email template path resolved to: {email_template_path}")
    
    return email_template_path

def list_email_templates():
    """
    Lists all available email templates in the email template directory
    
    Returns:
        list: List of available email template names without extension
    """
    if not os.path.exists(EMAIL_TEMPLATE_DIR):
        logger.warning(f"Email template directory not found: {EMAIL_TEMPLATE_DIR}")
        return []
    
    # Get all files in the email template directory
    template_files = os.listdir(EMAIL_TEMPLATE_DIR)
    
    # Filter for .html files and remove the extension
    templates = [os.path.splitext(f)[0] for f in template_files if f.endswith('.html')]
    
    logger.debug(f"Available email templates: {templates}")
    
    return templates