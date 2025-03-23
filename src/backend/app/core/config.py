import os
from typing import List, Optional

from pydantic import BaseSettings, Field, validator  # pydantic v1.10.7
from dotenv import load_dotenv  # python-dotenv v1.0.0

# Define project root path for reference
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))

def get_env_file_path() -> str:
    """
    Determines the appropriate .env file path based on the environment.
    
    Returns:
        str: Path to the environment-specific .env file
    """
    env = os.getenv("ENVIRONMENT", "development")
    env_file = os.path.join(PROJECT_ROOT, f".env.{env}")
    
    # Check if environment-specific .env file exists, otherwise use default .env
    if not os.path.exists(env_file):
        env_file = os.path.join(PROJECT_ROOT, ".env")
    
    return env_file

class Settings(BaseSettings):
    """
    Application settings class that loads and validates configuration from environment variables.
    
    This class provides a centralized configuration interface for all components of the
    IndiVillage backend application. It handles loading environment-specific variables,
    validating critical settings, and providing access to configuration values.
    """
    # Basic application settings
    PROJECT_NAME: str = Field(
        default="IndiVillage AI Services",
        description="The name of the application, used in API docs and emails"
    )
    API_V1_PREFIX: str = Field(
        default="/api/v1",
        description="The prefix for API v1 endpoints"
    )
    ENVIRONMENT: str = Field(
        default="development",
        description="Current environment (development, staging, production)"
    )
    DEBUG: bool = Field(
        default=False,
        description="Enable debug mode with enhanced logging and error details"
    )
    
    # Logging settings
    LOG_LEVEL: str = Field(
        default="INFO",
        description="Minimum log level to record (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    )
    LOG_FILE: str = Field(
        default="app.log",
        description="Log file path relative to the application root"
    )
    
    # Security settings
    SECRET_KEY: str = Field(
        description="Secret key for JWT token generation and encryption"
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=60 * 24,  # 24 hours
        description="JWT token expiration time in minutes"
    )
    ALGORITHM: str = Field(
        default="HS256",
        description="Algorithm used for JWT token signing"
    )
    
    # Database settings
    DATABASE_URL: Optional[str] = Field(
        default=None,
        description="Full database connection URL (if provided, other DB settings are ignored)"
    )
    DB_USER: Optional[str] = Field(
        default=None,
        description="Database username"
    )
    DB_PASSWORD: Optional[str] = Field(
        default=None,
        description="Database password"
    )
    DB_HOST: Optional[str] = Field(
        default=None,
        description="Database host address"
    )
    DB_PORT: Optional[str] = Field(
        default=None,
        description="Database port"
    )
    DB_NAME: Optional[str] = Field(
        default=None,
        description="Database name"
    )
    
    # Redis settings
    REDIS_URL: Optional[str] = Field(
        default=None,
        description="Redis connection URL for caching and queue services"
    )
    
    # AWS settings
    AWS_REGION: str = Field(
        default="us-east-1",
        description="AWS region for all AWS services"
    )
    AWS_ACCESS_KEY_ID: Optional[str] = Field(
        default=None,
        description="AWS access key ID for API access"
    )
    AWS_SECRET_ACCESS_KEY: Optional[str] = Field(
        default=None,
        description="AWS secret access key for API access"
    )
    AWS_S3_BUCKET_NAME: Optional[str] = Field(
        default=None,
        description="Main S3 bucket name for general storage"
    )
    AWS_S3_UPLOAD_BUCKET_NAME: Optional[str] = Field(
        default=None,
        description="S3 bucket for temporary file uploads"
    )
    AWS_S3_PROCESSED_BUCKET_NAME: Optional[str] = Field(
        default=None,
        description="S3 bucket for processed file storage"
    )
    AWS_S3_QUARANTINE_BUCKET_NAME: Optional[str] = Field(
        default=None,
        description="S3 bucket for quarantined files that failed security checks"
    )
    
    # File upload settings
    UPLOAD_FOLDER: str = Field(
        default="/tmp/uploads",
        description="Local folder for temporary file storage during processing"
    )
    MAX_UPLOAD_SIZE_MB: int = Field(
        default=50,
        description="Maximum allowed file upload size in megabytes"
    )
    ALLOWED_UPLOAD_EXTENSIONS: str = Field(
        default="csv,json,xml,jpg,jpeg,png,tiff,mp3,wav",
        description="Comma-separated list of allowed file extensions for uploads"
    )
    
    # External API credentials
    HUBSPOT_API_KEY: Optional[str] = Field(
        default=None,
        description="HubSpot API key for CRM integration"
    )
    SENDGRID_API_KEY: Optional[str] = Field(
        default=None,
        description="SendGrid API key for email sending"
    )
    EMAIL_FROM: str = Field(
        default="noreply@indivillage.com",
        description="Default 'from' email address for system emails"
    )
    EMAIL_FROM_NAME: str = Field(
        default="IndiVillage AI Services",
        description="Default 'from' name for system emails"
    )
    ADMIN_EMAIL: str = Field(
        default="admin@indivillage.com",
        description="Email address for system alerts and notifications"
    )
    
    # reCAPTCHA settings
    RECAPTCHA_SECRET_KEY: Optional[str] = Field(
        default=None,
        description="Google reCAPTCHA secret key for bot prevention"
    )
    RECAPTCHA_SITE_KEY: Optional[str] = Field(
        default=None,
        description="Google reCAPTCHA site key for frontend integration"
    )
    
    # Contentful settings
    CONTENTFUL_SPACE_ID: Optional[str] = Field(
        default=None,
        description="Contentful space ID for CMS integration"
    )
    CONTENTFUL_ACCESS_TOKEN: Optional[str] = Field(
        default=None,
        description="Contentful access token for content delivery API"
    )
    CONTENTFUL_MANAGEMENT_TOKEN: Optional[str] = Field(
        default=None,
        description="Contentful management token for content management API"
    )
    
    # CORS settings
    CORS_ORIGINS: str = Field(
        default="http://localhost:3000,http://localhost:8000",
        description="Comma-separated list of allowed CORS origins"
    )
    
    class Config:
        env_file = get_env_file_path()
        env_file_encoding = "utf-8"
        case_sensitive = True
    
    def __init__(self, **kwargs):
        """
        Initializes the Settings class with default values and environment variables.
        
        Loads configuration from the appropriate environment-specific .env file
        based on the current ENVIRONMENT setting.
        """
        # Load environment variables from the appropriate .env file
        env_file = get_env_file_path()
        if os.path.exists(env_file):
            load_dotenv(env_file)
            
        super().__init__(**kwargs)
    
    def get_allowed_origins(self) -> List[str]:
        """
        Parses the CORS_ORIGINS string into a list of allowed origins.
        
        Returns:
            List[str]: List of allowed origin URLs
        """
        if self.CORS_ORIGINS:
            return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
        else:
            return ["http://localhost:3000"]
    
    def get_database_url(self) -> str:
        """
        Constructs a database URL from individual components if DATABASE_URL is not provided.
        
        Returns:
            str: Complete database connection URL
        """
        if self.DATABASE_URL:
            return self.DATABASE_URL
        
        if all([self.DB_USER, self.DB_PASSWORD, self.DB_HOST, self.DB_PORT, self.DB_NAME]):
            return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        
        # Default development database
        return "postgresql://postgres:postgres@localhost:5432/indivillage"
    
    @validator("SECRET_KEY", pre=True)
    def validate_secret_key(cls, v):
        """
        Validates that the SECRET_KEY is set and meets minimum security requirements.
        
        Args:
            cls: The class
            v (str): The secret key value
            
        Returns:
            str: Validated secret key
            
        Raises:
            ValueError: If secret key doesn't meet requirements
        """
        if not v or len(v) < 32:
            if os.getenv("ENVIRONMENT") in ["production", "staging"]:
                raise ValueError("SECRET_KEY must be at least 32 characters long in production/staging environments")
            # For development only: provide a default key
            return "devkeydevkeydevkeydevkeydevkeydevkeydevkey"
        return v
    
    @validator("MAX_UPLOAD_SIZE_MB", pre=True)
    def validate_upload_size(cls, v):
        """
        Validates that the MAX_UPLOAD_SIZE_MB is within acceptable limits.
        
        Args:
            cls: The class
            v (int): The maximum upload size in MB
            
        Returns:
            int: Validated maximum upload size
            
        Raises:
            ValueError: If upload size is outside acceptable range
        """
        if v is None:
            return 50
        
        try:
            v_int = int(v)
        except (ValueError, TypeError):
            raise ValueError("MAX_UPLOAD_SIZE_MB must be an integer")
        
        if v_int < 1 or v_int > 100:
            raise ValueError("MAX_UPLOAD_SIZE_MB must be between 1 and 100")
        
        return v_int
    
    @validator("ALLOWED_UPLOAD_EXTENSIONS", pre=True)
    def validate_allowed_extensions(cls, v):
        """
        Validates and normalizes the ALLOWED_UPLOAD_EXTENSIONS setting.
        
        Args:
            cls: The class
            v (str): Comma-separated list of file extensions
            
        Returns:
            str: Validated and normalized extensions string
        """
        if not v:
            return "csv,json,xml,jpg,jpeg,png,tiff,mp3,wav"
        
        extensions = v.split(",")
        normalized = [ext.strip().lower() for ext in extensions]
        
        return ",".join(normalized)


# Initialize settings instance
settings = Settings()