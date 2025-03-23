"""
Main configuration file for the IndiVillage backend application.

This file serves as a centralized entry point for all configuration settings, 
importing and re-exporting the core configuration module. It provides 
environment-specific configuration loading and makes settings accessible 
throughout the application.
"""

import os
import sys
import logging
from dotenv import load_dotenv  # python-dotenv v1.0.0

# Define base directory (exported)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_FILE = os.path.join(BASE_DIR, '.env')

# Configure logger
logger = logging.getLogger(__name__)

def load_env_file() -> bool:
    """
    Loads environment variables from the appropriate .env file based on the environment.
    
    Returns:
        bool: True if environment variables were loaded successfully, False otherwise
    """
    if os.path.exists(ENV_FILE):
        try:
            load_dotenv(ENV_FILE)
            logger.info(f"Loaded environment variables from {ENV_FILE}")
            return True
        except Exception as e:
            logger.error(f"Error loading environment variables: {e}")
            return False
    else:
        logger.warning(f"Environment file {ENV_FILE} not found")
        return False

def get_environment() -> str:
    """
    Retrieves the current environment (development, staging, production).
    
    Returns:
        str: Current environment name
    """
    env = os.environ.get("ENVIRONMENT", "development")
    allowed_environments = ["development", "staging", "production"]
    
    if env not in allowed_environments:
        logger.warning(f"Invalid environment '{env}', falling back to 'development'")
        return "development"
    
    return env

def configure_logging():
    """
    Configures basic logging for the configuration module.
    """
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
    )
    
    # Set appropriate log level based on environment
    if get_environment() == "development":
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        logging.getLogger().setLevel(logging.INFO)

# Configure logging
configure_logging()

# Load environment variables
load_env_file()

# Import settings from core module (re-exported)
from app.core.config import settings  # Import after environment setup

# Log the application environment
logger.info(f"Application running in {settings.ENVIRONMENT} environment")

# Explicitly define exports
__all__ = ['settings', 'BASE_DIR', 'get_environment']