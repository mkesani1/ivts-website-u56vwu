import boto3  # boto3 v1.26.0
import botocore.exceptions  # botocore v1.29.0
import os  # standard library
import uuid  # standard library
import datetime  # standard library
from typing import Dict, Optional, Any, Union  # standard library

from ..core.config import settings
from ..core.logging import get_logger

# Initialize logger
logger = get_logger(__name__)

# Constants
MAX_UPLOAD_SIZE_MB = settings.MAX_UPLOAD_SIZE_MB
MAX_UPLOAD_SIZE_BYTES = MAX_UPLOAD_SIZE_MB * 1024 * 1024
DEFAULT_REGION = settings.AWS_REGION


def validate_file_size(file_size: int, max_size_mb: int = None) -> bool:
    """
    Validates if a file's size is within allowed limits.
    
    Args:
        file_size: Size of the file in bytes
        max_size_mb: Maximum allowed size in megabytes (defaults to MAX_UPLOAD_SIZE_MB)
        
    Returns:
        bool: True if file size is within limits, False otherwise
    """
    max_size_bytes = (max_size_mb * 1024 * 1024) if max_size_mb else MAX_UPLOAD_SIZE_BYTES
    
    is_valid = file_size <= max_size_bytes
    
    if not is_valid:
        logger.warning(
            f"File size validation failed: {file_size} bytes exceeds limit of {max_size_bytes} bytes",
            extra={"file_size": file_size, "max_size": max_size_bytes}
        )
    else:
        logger.debug(
            f"File size validation passed: {file_size} bytes is within limit of {max_size_bytes} bytes",
            extra={"file_size": file_size, "max_size": max_size_bytes}
        )
        
    return is_valid


def get_aws_credentials() -> Dict[str, str]:
    """
    Retrieves AWS credentials from application settings.
    
    Returns:
        Dict: Dictionary containing AWS credentials
    """
    credentials = {
        'aws_access_key_id': settings.AWS_ACCESS_KEY_ID,
        'aws_secret_access_key': settings.AWS_SECRET_ACCESS_KEY,
        'region_name': settings.AWS_REGION or DEFAULT_REGION
    }
    
    # Mask sensitive info for logging
    log_credentials = {
        'aws_access_key_id': f"{credentials['aws_access_key_id'][:4]}****" if credentials['aws_access_key_id'] else None,
        'region_name': credentials['region_name']
    }
    
    logger.debug(f"Retrieved AWS credentials", extra={"credentials": log_credentials})
    
    return credentials


def create_boto3_session(credentials: Dict[str, str] = None) -> boto3.session.Session:
    """
    Creates a boto3 session with proper credentials.
    
    Args:
        credentials: Dictionary containing AWS credentials
        
    Returns:
        boto3.session.Session: Configured boto3 session
    """
    if credentials is None:
        credentials = get_aws_credentials()
        
    session = boto3.session.Session(
        aws_access_key_id=credentials.get('aws_access_key_id'),
        aws_secret_access_key=credentials.get('aws_secret_access_key'),
        region_name=credentials.get('region_name', DEFAULT_REGION)
    )
    
    logger.debug(f"Created boto3 session for region {credentials.get('region_name', DEFAULT_REGION)}")
    
    return session


def get_s3_client(credentials: Dict[str, str] = None) -> boto3.client:
    """
    Creates and returns a configured boto3 S3 client.
    
    Args:
        credentials: Dictionary containing AWS credentials
        
    Returns:
        boto3.client: Configured S3 client instance
    """
    session = create_boto3_session(credentials)
    s3_client = session.client('s3')
    
    logger.debug("Created S3 client")
    
    return s3_client


def get_s3_resource(credentials: Dict[str, str] = None) -> boto3.resource:
    """
    Creates and returns a configured boto3 S3 resource.
    
    Args:
        credentials: Dictionary containing AWS credentials
        
    Returns:
        boto3.resource: Configured S3 resource instance
    """
    session = create_boto3_session(credentials)
    s3_resource = session.resource('s3')
    
    logger.debug("Created S3 resource")
    
    return s3_resource


def generate_s3_key(filename: str, prefix: str = "") -> str:
    """
    Generates a unique S3 object key with optional prefix.
    
    Args:
        filename: Original filename
        prefix: Optional prefix for organizing objects in S3
        
    Returns:
        str: Unique S3 object key
    """
    # Clean filename to remove problematic characters
    clean_filename = "".join(c for c in filename if c.isalnum() or c in "._-")
    
    # Generate unique identifier
    unique_id = str(uuid.uuid4())
    
    # Construct the key
    if prefix:
        # Ensure prefix ends with a slash
        if not prefix.endswith('/'):
            prefix = f"{prefix}/"
        key = f"{prefix}{unique_id}-{clean_filename}"
    else:
        key = f"{unique_id}-{clean_filename}"
    
    logger.debug(f"Generated S3 key: {key}", extra={"original_filename": filename, "s3_key": key})
    
    return key


def check_bucket_exists(bucket_name: str, s3_client: boto3.client = None) -> bool:
    """
    Checks if an S3 bucket exists and is accessible.
    
    Args:
        bucket_name: Name of the S3 bucket
        s3_client: Optional S3 client instance
        
    Returns:
        bool: True if bucket exists and is accessible, False otherwise
    """
    if s3_client is None:
        s3_client = get_s3_client()
    
    try:
        s3_client.head_bucket(Bucket=bucket_name)
        logger.debug(f"Bucket {bucket_name} exists and is accessible")
        return True
    except botocore.exceptions.ClientError as e:
        error_code = e.response.get('Error', {}).get('Code')
        if error_code == '404':
            logger.warning(f"Bucket {bucket_name} does not exist", extra={"error": str(e)})
        else:
            logger.error(f"Error checking bucket {bucket_name}", extra={"error": str(e)})
        return False
    except Exception as e:
        logger.error(f"Unexpected error checking bucket {bucket_name}", extra={"error": str(e)})
        return False


def calculate_s3_etag(file_path: str, chunk_size: int = 8 * 1024 * 1024) -> str:
    """
    Calculates the ETag for a file using S3's algorithm.
    
    Args:
        file_path: Path to the file
        chunk_size: Size of chunks for multipart calculation (default: 8MB)
        
    Returns:
        str: Calculated ETag value
    """
    import hashlib
    
    md5s = []
    
    with open(file_path, 'rb') as f:
        # Check if file is smaller than chunk size
        file_size = os.path.getsize(file_path)
        
        if file_size <= chunk_size:
            # For small files, just calculate the MD5
            md5 = hashlib.md5()
            md5.update(f.read())
            etag = f'"{md5.hexdigest()}"'
            logger.debug(f"Calculated ETag for small file: {etag}", extra={"file": file_path})
            return etag
        
        # For larger files, calculate MD5 of each chunk
        chunk = f.read(chunk_size)
        while chunk:
            md5 = hashlib.md5()
            md5.update(chunk)
            md5s.append(md5.digest())
            chunk = f.read(chunk_size)
        
        # Combine chunk MD5s and calculate final MD5
        combined_md5 = hashlib.md5()
        for md5_digest in md5s:
            combined_md5.update(md5_digest)
        
        # Format as S3 ETag
        etag = f'"{combined_md5.hexdigest()}-{len(md5s)}"'
        logger.debug(f"Calculated ETag for multipart file: {etag}", extra={"file": file_path, "parts": len(md5s)})
        
        return etag


def format_s3_url(bucket_name: str, object_key: str, region: str = None) -> str:
    """
    Formats a complete S3 URL for an object.
    
    Args:
        bucket_name: S3 bucket name
        object_key: S3 object key
        region: AWS region (defaults to DEFAULT_REGION)
        
    Returns:
        str: Formatted S3 URL
    """
    region = region or DEFAULT_REGION
    url = f"https://{bucket_name}.s3.{region}.amazonaws.com/{object_key}"
    
    logger.debug(f"Formatted S3 URL: {url}", extra={"bucket": bucket_name, "key": object_key})
    
    return url


def handle_aws_exception(exception: Exception, operation: str, resource_id: str = None) -> Dict[str, Any]:
    """
    Handles and logs AWS exceptions with appropriate context.
    
    Args:
        exception: The exception that was raised
        operation: Description of the operation being performed
        resource_id: Identifier for the resource being operated on
        
    Returns:
        Dict: Error details dictionary
    """
    error_context = {
        "operation": operation,
        "resource_id": resource_id,
        "exception_type": type(exception).__name__,
        "exception_message": str(exception)
    }
    
    if isinstance(exception, botocore.exceptions.ClientError):
        error_code = exception.response.get('Error', {}).get('Code', 'Unknown')
        error_message = exception.response.get('Error', {}).get('Message', str(exception))
        error_context.update({
            "error_code": error_code,
            "error_message": error_message
        })
        
        logger.error(
            f"AWS error during {operation}: {error_code} - {error_message}",
            extra=error_context,
            exc_info=True
        )
        
        return {
            "error_type": "AWS Client Error",
            "error_code": error_code,
            "error_message": error_message,
            "details": error_context
        }
    
    logger.error(
        f"Unexpected error during {operation}: {str(exception)}",
        extra=error_context,
        exc_info=True
    )
    
    return {
        "error_type": "Unexpected Error",
        "error_message": str(exception),
        "details": error_context
    }


class AWSCredentials:
    """
    Class for managing AWS credentials with secure handling.
    
    This class provides a secure way to store and manage AWS credentials,
    including validation and structured access.
    """
    
    def __init__(
        self,
        access_key: str = None,
        secret_key: str = None,
        region: str = None,
        session_token: str = None
    ):
        """
        Initializes AWS credentials from settings or parameters.
        
        Args:
            access_key: AWS access key ID
            secret_key: AWS secret access key
            region: AWS region
            session_token: AWS session token for temporary credentials
        """
        self.access_key = access_key or settings.AWS_ACCESS_KEY_ID
        self.secret_key = secret_key or settings.AWS_SECRET_ACCESS_KEY
        self.region = region or settings.AWS_REGION or DEFAULT_REGION
        self.session_token = session_token
        
        # Validate that we have the minimum required credentials
        if not self.is_valid():
            logger.warning(
                "Incomplete AWS credentials provided",
                extra={
                    "has_access_key": bool(self.access_key),
                    "has_secret_key": bool(self.secret_key),
                    "region": self.region
                }
            )
        else:
            # Log initialization with masked credentials
            logger.debug(
                "AWS credentials initialized",
                extra={
                    "access_key_prefix": self.access_key[:4] + '****' if self.access_key else None,
                    "region": self.region,
                    "has_session_token": bool(self.session_token)
                }
            )
    
    def to_dict(self) -> Dict[str, str]:
        """
        Converts credentials to a dictionary for boto3.
        
        Returns:
            Dict: Credentials dictionary
        """
        credentials = {
            'aws_access_key_id': self.access_key,
            'aws_secret_access_key': self.secret_key,
            'region_name': self.region
        }
        
        if self.session_token:
            credentials['aws_session_token'] = self.session_token
            
        return credentials
    
    def is_valid(self) -> bool:
        """
        Checks if the credentials are valid and complete.
        
        Returns:
            bool: True if credentials are valid, False otherwise
        """
        return (
            self.access_key is not None and len(self.access_key) > 0 and
            self.secret_key is not None and len(self.secret_key) > 0 and
            self.region is not None and len(self.region) > 0
        )
    
    def validate(self) -> bool:
        """
        Validates credentials by making a test AWS API call.
        
        Returns:
            bool: True if credentials are valid, False otherwise
        """
        if not self.is_valid():
            logger.warning("Cannot validate incomplete credentials")
            return False
        
        try:
            # Create a session and list S3 buckets as a simple validation
            session = boto3.session.Session(
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                aws_session_token=self.session_token,
                region_name=self.region
            )
            
            s3 = session.client('s3')
            s3.list_buckets()
            
            logger.info("AWS credentials validated successfully")
            return True
        except Exception as e:
            logger.error(
                f"AWS credentials validation failed: {str(e)}",
                extra={"error": str(e), "error_type": type(e).__name__}
            )
            return False


class S3Util:
    """
    Utility class for common S3 operations.
    
    This class provides a convenient interface for interacting with S3,
    handling common operations like checking if objects exist, getting
    object sizes, and generating presigned URLs.
    """
    
    def __init__(self, credentials: AWSCredentials = None):
        """
        Initializes S3Util with credentials.
        
        Args:
            credentials: AWSCredentials instance
        """
        self._credentials = credentials or AWSCredentials()
        self._s3_client = None
        self._s3_resource = None
        
        logger.debug("S3Util initialized")
    
    def get_client(self) -> boto3.client:
        """
        Gets or creates an S3 client.
        
        Returns:
            boto3.client: S3 client instance
        """
        if self._s3_client is None:
            self._s3_client = get_s3_client(self._credentials.to_dict())
            
        return self._s3_client
    
    def get_resource(self) -> boto3.resource:
        """
        Gets or creates an S3 resource.
        
        Returns:
            boto3.resource: S3 resource instance
        """
        if self._s3_resource is None:
            self._s3_resource = get_s3_resource(self._credentials.to_dict())
            
        return self._s3_resource
    
    def check_object_exists(self, bucket_name: str, object_key: str) -> bool:
        """
        Checks if an object exists in S3.
        
        Args:
            bucket_name: S3 bucket name
            object_key: S3 object key
            
        Returns:
            bool: True if object exists, False otherwise
        """
        s3_client = self.get_client()
        
        try:
            s3_client.head_object(Bucket=bucket_name, Key=object_key)
            logger.debug(f"Object exists: {bucket_name}/{object_key}")
            return True
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == '404':
                logger.debug(f"Object does not exist: {bucket_name}/{object_key}")
                return False
            else:
                logger.error(
                    f"Error checking object existence: {bucket_name}/{object_key}",
                    extra={"error": str(e), "bucket": bucket_name, "key": object_key}
                )
                return False
        except Exception as e:
            logger.error(
                f"Unexpected error checking object existence: {bucket_name}/{object_key}",
                extra={"error": str(e), "bucket": bucket_name, "key": object_key}
            )
            return False
    
    def get_object_size(self, bucket_name: str, object_key: str) -> int:
        """
        Gets the size of an S3 object in bytes.
        
        Args:
            bucket_name: S3 bucket name
            object_key: S3 object key
            
        Returns:
            int: Size of the object in bytes
        """
        s3_client = self.get_client()
        
        try:
            response = s3_client.head_object(Bucket=bucket_name, Key=object_key)
            size = response.get('ContentLength', 0)
            
            logger.debug(
                f"Object size: {size} bytes",
                extra={"bucket": bucket_name, "key": object_key, "size": size}
            )
            
            return size
        except Exception as e:
            logger.error(
                f"Error getting object size: {bucket_name}/{object_key}",
                extra={"error": str(e), "bucket": bucket_name, "key": object_key}
            )
            return 0
    
    def generate_presigned_url(
        self,
        bucket_name: str,
        object_key: str,
        operation: str = 'get_object',
        expiration: int = 3600,
        params: Dict[str, Any] = None
    ) -> str:
        """
        Generates a presigned URL for an S3 operation.
        
        Args:
            bucket_name: S3 bucket name
            object_key: S3 object key
            operation: S3 operation (default: 'get_object')
            expiration: URL expiration in seconds (default: 3600)
            params: Additional parameters for the operation
            
        Returns:
            str: Presigned URL
        """
        s3_client = self.get_client()
        params = params or {}
        
        try:
            url = s3_client.generate_presigned_url(
                ClientMethod=operation,
                Params={'Bucket': bucket_name, 'Key': object_key, **params},
                ExpiresIn=expiration
            )
            
            logger.debug(
                f"Generated presigned URL for {operation}",
                extra={
                    "bucket": bucket_name,
                    "key": object_key,
                    "operation": operation,
                    "expiration": expiration
                }
            )
            
            return url
        except Exception as e:
            logger.error(
                f"Error generating presigned URL: {bucket_name}/{object_key}",
                extra={
                    "error": str(e),
                    "bucket": bucket_name,
                    "key": object_key,
                    "operation": operation
                }
            )
            raise