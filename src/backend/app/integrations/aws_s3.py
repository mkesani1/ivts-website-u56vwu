import os
import uuid
import datetime
from typing import Dict, List, Optional, Any, Union, Tuple

import boto3  # version: ^1.26.0
from botocore.exceptions import ClientError  # version: ^1.26.0

from ..core.config import settings
from ..core.logging import get_logger

# Initialize logger
logger = get_logger(__name__)

# Constants
DEFAULT_EXPIRATION = 3600  # 1 hour expiration for presigned URLs
UPLOAD_BUCKET = settings.AWS_S3_UPLOAD_BUCKET_NAME
PROCESSED_BUCKET = settings.AWS_S3_PROCESSED_BUCKET_NAME
QUARANTINE_BUCKET = settings.AWS_S3_QUARANTINE_BUCKET_NAME


def generate_presigned_post(
    object_key: str,
    content_type: str,
    expiration: int = DEFAULT_EXPIRATION,
    bucket_name: str = None
) -> Dict[str, Any]:
    """
    Generates a presigned POST URL for direct file upload to S3.
    
    Args:
        object_key: The key (path) where the object will be stored in S3
        content_type: MIME type of the file being uploaded
        expiration: URL expiration time in seconds (default: 1 hour)
        bucket_name: S3 bucket name (defaults to UPLOAD_BUCKET)
        
    Returns:
        Dictionary containing presigned URL and fields for POST request
    """
    s3_client = boto3.client(
        's3',
        region_name=settings.AWS_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
    )
    
    bucket = bucket_name or UPLOAD_BUCKET
    
    try:
        response = s3_client.generate_presigned_post(
            Bucket=bucket,
            Key=object_key,
            Fields={
                'Content-Type': content_type,
            },
            Conditions=[
                {'Content-Type': content_type},
                ['content-length-range', 1, settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024]
            ],
            ExpiresIn=expiration
        )
        
        # Add server-side encryption requirement
        response['fields']['x-amz-server-side-encryption'] = 'AES256'
        
        logger.info(f"Generated presigned POST URL for {object_key} in bucket {bucket}, expires in {expiration}s")
        return response
    except ClientError as e:
        logger.error(f"Error generating presigned POST URL: {str(e)}", exc_info=True)
        raise


def generate_presigned_url(
    object_key: str,
    bucket_name: str = None,
    expiration: int = DEFAULT_EXPIRATION
) -> str:
    """
    Generates a presigned URL for downloading a file from S3.
    
    Args:
        object_key: The key (path) of the object in S3
        bucket_name: S3 bucket name (defaults to PROCESSED_BUCKET)
        expiration: URL expiration time in seconds (default: 1 hour)
        
    Returns:
        Presigned URL for downloading the object
    """
    s3_client = boto3.client(
        's3',
        region_name=settings.AWS_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
    )
    
    bucket = bucket_name or PROCESSED_BUCKET
    
    try:
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': bucket,
                'Key': object_key
            },
            ExpiresIn=expiration
        )
        
        logger.info(f"Generated presigned download URL for {object_key} in bucket {bucket}, expires in {expiration}s")
        return url
    except ClientError as e:
        logger.error(f"Error generating presigned download URL: {str(e)}", exc_info=True)
        raise


def upload_file(
    file_path: str,
    object_key: str,
    bucket_name: str = None,
    metadata: Dict[str, str] = None
) -> bool:
    """
    Uploads a file to S3 bucket with server-side encryption.
    
    Args:
        file_path: Local path to the file
        object_key: The key (path) where the object will be stored in S3
        bucket_name: S3 bucket name (defaults to UPLOAD_BUCKET)
        metadata: Optional metadata to attach to the S3 object
        
    Returns:
        True if upload successful, False otherwise
    """
    s3_client = boto3.client(
        's3',
        region_name=settings.AWS_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
    )
    
    bucket = bucket_name or UPLOAD_BUCKET
    meta = metadata or {}
    
    try:
        extra_args = {
            'ServerSideEncryption': 'AES256',
            'Metadata': meta
        }
        
        if os.path.getsize(file_path) > 0:
            s3_client.upload_file(
                file_path,
                bucket,
                object_key,
                ExtraArgs=extra_args
            )
            
            logger.info(f"Successfully uploaded {file_path} to {bucket}/{object_key}")
            return True
        else:
            logger.error(f"Cannot upload empty file {file_path}")
            return False
    except ClientError as e:
        logger.error(f"Error uploading file to S3: {str(e)}", exc_info=True)
        return False
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}", exc_info=True)
        return False


def download_file(
    object_key: str,
    download_path: str,
    bucket_name: str = None
) -> bool:
    """
    Downloads a file from S3 bucket to local filesystem.
    
    Args:
        object_key: The key (path) of the object in S3
        download_path: Local path where the file should be saved
        bucket_name: S3 bucket name (defaults to PROCESSED_BUCKET)
        
    Returns:
        True if download successful, False otherwise
    """
    s3_client = boto3.client(
        's3',
        region_name=settings.AWS_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
    )
    
    bucket = bucket_name or PROCESSED_BUCKET
    
    try:
        # Ensure the target directory exists
        os.makedirs(os.path.dirname(os.path.abspath(download_path)), exist_ok=True)
        
        s3_client.download_file(
            bucket,
            object_key,
            download_path
        )
        
        logger.info(f"Successfully downloaded {bucket}/{object_key} to {download_path}")
        return True
    except ClientError as e:
        logger.error(f"Error downloading file from S3: {str(e)}", exc_info=True)
        return False
    except Exception as e:
        logger.error(f"Unexpected error downloading file: {str(e)}", exc_info=True)
        return False


def delete_file(
    object_key: str,
    bucket_name: str = None
) -> bool:
    """
    Deletes a file from S3 bucket.
    
    Args:
        object_key: The key (path) of the object in S3
        bucket_name: S3 bucket name (defaults to UPLOAD_BUCKET)
        
    Returns:
        True if deletion successful, False otherwise
    """
    s3_client = boto3.client(
        's3',
        region_name=settings.AWS_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
    )
    
    bucket = bucket_name or UPLOAD_BUCKET
    
    try:
        s3_client.delete_object(
            Bucket=bucket,
            Key=object_key
        )
        
        logger.info(f"Successfully deleted {bucket}/{object_key}")
        return True
    except ClientError as e:
        logger.error(f"Error deleting file from S3: {str(e)}", exc_info=True)
        return False


def copy_file(
    source_key: str,
    destination_key: str,
    source_bucket: str = None,
    destination_bucket: str = None
) -> bool:
    """
    Copies a file from one S3 location to another.
    
    Args:
        source_key: The key (path) of the source object
        destination_key: The key (path) for the destination object
        source_bucket: Source S3 bucket name (defaults to UPLOAD_BUCKET)
        destination_bucket: Destination S3 bucket name (defaults to PROCESSED_BUCKET)
        
    Returns:
        True if copy successful, False otherwise
    """
    s3_client = boto3.client(
        's3',
        region_name=settings.AWS_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
    )
    
    src_bucket = source_bucket or UPLOAD_BUCKET
    dst_bucket = destination_bucket or PROCESSED_BUCKET
    
    try:
        copy_source = {
            'Bucket': src_bucket,
            'Key': source_key
        }
        
        s3_client.copy_object(
            CopySource=copy_source,
            Bucket=dst_bucket,
            Key=destination_key,
            ServerSideEncryption='AES256'
        )
        
        logger.info(f"Successfully copied {src_bucket}/{source_key} to {dst_bucket}/{destination_key}")
        return True
    except ClientError as e:
        logger.error(f"Error copying file in S3: {str(e)}", exc_info=True)
        return False


def move_to_quarantine(
    source_key: str,
    source_bucket: str = None
) -> bool:
    """
    Moves a file to the quarantine bucket for security isolation.
    
    Args:
        source_key: The key (path) of the source object
        source_bucket: Source S3 bucket name (defaults to UPLOAD_BUCKET)
        
    Returns:
        True if move successful, False otherwise
    """
    src_bucket = source_bucket or UPLOAD_BUCKET
    # Prefix with 'quarantine/' to indicate the security status
    quarantine_key = f"quarantine/{os.path.basename(source_key)}"
    
    # First, copy the file to quarantine bucket
    copy_success = copy_file(
        source_key=source_key,
        destination_key=quarantine_key,
        source_bucket=src_bucket,
        destination_bucket=QUARANTINE_BUCKET
    )
    
    if copy_success:
        # If copy succeeded, delete the original file
        delete_success = delete_file(source_key, src_bucket)
        if delete_success:
            logger.info(f"Successfully moved {src_bucket}/{source_key} to quarantine bucket")
            return True
        else:
            logger.warning(
                f"File copied to quarantine bucket, but failed to delete original at {src_bucket}/{source_key}"
            )
            return True  # Still consider it a success since the file is in quarantine
    else:
        logger.error(f"Failed to move {src_bucket}/{source_key} to quarantine bucket")
        return False


def check_file_exists(
    object_key: str,
    bucket_name: str = None
) -> bool:
    """
    Checks if a file exists in S3 bucket.
    
    Args:
        object_key: The key (path) of the object in S3
        bucket_name: S3 bucket name (defaults to UPLOAD_BUCKET)
        
    Returns:
        True if file exists, False otherwise
    """
    s3_client = boto3.client(
        's3',
        region_name=settings.AWS_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
    )
    
    bucket = bucket_name or UPLOAD_BUCKET
    
    try:
        s3_client.head_object(
            Bucket=bucket,
            Key=object_key
        )
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            return False
        else:
            logger.error(f"Error checking if file exists: {str(e)}", exc_info=True)
            # Re-raise for other types of errors
            raise


def get_file_size(
    object_key: str,
    bucket_name: str = None
) -> int:
    """
    Gets the size of a file in S3 bucket.
    
    Args:
        object_key: The key (path) of the object in S3
        bucket_name: S3 bucket name (defaults to UPLOAD_BUCKET)
        
    Returns:
        Size of the file in bytes, or -1 if file not found
    """
    s3_client = boto3.client(
        's3',
        region_name=settings.AWS_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
    )
    
    bucket = bucket_name or UPLOAD_BUCKET
    
    try:
        response = s3_client.head_object(
            Bucket=bucket,
            Key=object_key
        )
        return response['ContentLength']
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            logger.warning(f"File not found when getting size: {bucket}/{object_key}")
            return -1
        else:
            logger.error(f"Error getting file size: {str(e)}", exc_info=True)
            return -1


def get_file_metadata(
    object_key: str,
    bucket_name: str = None
) -> Dict[str, str]:
    """
    Gets the metadata of a file in S3 bucket.
    
    Args:
        object_key: The key (path) of the object in S3
        bucket_name: S3 bucket name (defaults to UPLOAD_BUCKET)
        
    Returns:
        File metadata, or empty dict if file not found
    """
    s3_client = boto3.client(
        's3',
        region_name=settings.AWS_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
    )
    
    bucket = bucket_name or UPLOAD_BUCKET
    
    try:
        response = s3_client.head_object(
            Bucket=bucket,
            Key=object_key
        )
        return response.get('Metadata', {})
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            logger.warning(f"File not found when getting metadata: {bucket}/{object_key}")
            return {}
        else:
            logger.error(f"Error getting file metadata: {str(e)}", exc_info=True)
            return {}


def generate_object_key(
    original_filename: str,
    prefix: str = ''
) -> str:
    """
    Generates a unique object key for S3 storage.
    
    Args:
        original_filename: Original filename to include in the key
        prefix: Optional prefix for organizational purposes
        
    Returns:
        Unique object key for S3 storage
    """
    # Generate a unique identifier
    unique_id = str(uuid.uuid4())
    
    # Sanitize the filename to ensure it's S3 compatible
    sanitized_filename = os.path.basename(original_filename)
    sanitized_filename = sanitized_filename.replace(' ', '_')
    
    # Construct the key with prefix (if any), unique ID, and sanitized filename
    if prefix:
        # Ensure prefix ends with a slash
        if not prefix.endswith('/'):
            prefix += '/'
        return f"{prefix}{unique_id}_{sanitized_filename}"
    else:
        return f"{unique_id}_{sanitized_filename}"


class S3Client:
    """
    Client class for interacting with AWS S3 service.
    
    Provides an object-oriented interface to S3 operations with consistent
    configuration and error handling.
    """
    
    def __init__(
        self,
        region: str = None,
        access_key: str = None,
        secret_key: str = None
    ):
        """
        Initializes the S3Client with AWS credentials and configuration.
        
        Args:
            region: AWS region (defaults to settings.AWS_REGION)
            access_key: AWS access key ID (defaults to settings.AWS_ACCESS_KEY_ID)
            secret_key: AWS secret access key (defaults to settings.AWS_SECRET_ACCESS_KEY)
        """
        self._region = region or settings.AWS_REGION
        access_key = access_key or settings.AWS_ACCESS_KEY_ID
        secret_key = secret_key or settings.AWS_SECRET_ACCESS_KEY
        
        self._client = boto3.client(
            's3',
            region_name=self._region,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key
        )
        
        self._upload_bucket = UPLOAD_BUCKET
        self._processed_bucket = PROCESSED_BUCKET
        self._quarantine_bucket = QUARANTINE_BUCKET
        
        logger.info(f"Initialized S3Client in region {self._region}")
    
    def generate_presigned_post(
        self,
        object_key: str,
        content_type: str,
        expiration: int = DEFAULT_EXPIRATION,
        bucket_name: str = None
    ) -> Dict[str, Any]:
        """
        Generates a presigned POST URL for direct file upload.
        
        Args:
            object_key: The key (path) where the object will be stored in S3
            content_type: MIME type of the file being uploaded
            expiration: URL expiration time in seconds (default: 1 hour)
            bucket_name: S3 bucket name (defaults to self._upload_bucket)
            
        Returns:
            Dictionary containing presigned URL and fields
        """
        bucket = bucket_name or self._upload_bucket
        
        try:
            response = self._client.generate_presigned_post(
                Bucket=bucket,
                Key=object_key,
                Fields={
                    'Content-Type': content_type,
                },
                Conditions=[
                    {'Content-Type': content_type},
                    ['content-length-range', 1, settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024]
                ],
                ExpiresIn=expiration
            )
            
            # Add server-side encryption requirement
            response['fields']['x-amz-server-side-encryption'] = 'AES256'
            
            logger.info(f"Generated presigned POST URL for {object_key} in bucket {bucket}, expires in {expiration}s")
            return response
        except ClientError as e:
            logger.error(f"Error generating presigned POST URL: {str(e)}", exc_info=True)
            raise
    
    def generate_presigned_url(
        self,
        object_key: str,
        bucket_name: str = None,
        expiration: int = DEFAULT_EXPIRATION
    ) -> str:
        """
        Generates a presigned URL for downloading a file.
        
        Args:
            object_key: The key (path) of the object in S3
            bucket_name: S3 bucket name (defaults to self._processed_bucket)
            expiration: URL expiration time in seconds (default: 1 hour)
            
        Returns:
            Presigned URL for downloading the object
        """
        bucket = bucket_name or self._processed_bucket
        
        try:
            url = self._client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': bucket,
                    'Key': object_key
                },
                ExpiresIn=expiration
            )
            
            logger.info(f"Generated presigned download URL for {object_key} in bucket {bucket}, expires in {expiration}s")
            return url
        except ClientError as e:
            logger.error(f"Error generating presigned download URL: {str(e)}", exc_info=True)
            raise
    
    def upload_file(
        self,
        file_path: str,
        object_key: str,
        bucket_name: str = None,
        metadata: Dict[str, str] = None
    ) -> bool:
        """
        Uploads a file to S3 bucket with server-side encryption.
        
        Args:
            file_path: Local path to the file
            object_key: The key (path) where the object will be stored in S3
            bucket_name: S3 bucket name (defaults to self._upload_bucket)
            metadata: Optional metadata to attach to the S3 object
            
        Returns:
            True if upload successful, False otherwise
        """
        bucket = bucket_name or self._upload_bucket
        meta = metadata or {}
        
        try:
            extra_args = {
                'ServerSideEncryption': 'AES256',
                'Metadata': meta
            }
            
            if os.path.getsize(file_path) > 0:
                self._client.upload_file(
                    file_path,
                    bucket,
                    object_key,
                    ExtraArgs=extra_args
                )
                
                logger.info(f"Successfully uploaded {file_path} to {bucket}/{object_key}")
                return True
            else:
                logger.error(f"Cannot upload empty file {file_path}")
                return False
        except ClientError as e:
            logger.error(f"Error uploading file to S3: {str(e)}", exc_info=True)
            return False
        except FileNotFoundError:
            logger.error(f"File not found: {file_path}", exc_info=True)
            return False
    
    def download_file(
        self,
        object_key: str,
        download_path: str,
        bucket_name: str = None
    ) -> bool:
        """
        Downloads a file from S3 bucket to local filesystem.
        
        Args:
            object_key: The key (path) of the object in S3
            download_path: Local path where the file should be saved
            bucket_name: S3 bucket name (defaults to self._processed_bucket)
            
        Returns:
            True if download successful, False otherwise
        """
        bucket = bucket_name or self._processed_bucket
        
        try:
            # Ensure the target directory exists
            os.makedirs(os.path.dirname(os.path.abspath(download_path)), exist_ok=True)
            
            self._client.download_file(
                bucket,
                object_key,
                download_path
            )
            
            logger.info(f"Successfully downloaded {bucket}/{object_key} to {download_path}")
            return True
        except ClientError as e:
            logger.error(f"Error downloading file from S3: {str(e)}", exc_info=True)
            return False
        except Exception as e:
            logger.error(f"Unexpected error downloading file: {str(e)}", exc_info=True)
            return False
    
    def delete_file(
        self,
        object_key: str,
        bucket_name: str = None
    ) -> bool:
        """
        Deletes a file from S3 bucket.
        
        Args:
            object_key: The key (path) of the object in S3
            bucket_name: S3 bucket name (defaults to self._upload_bucket)
            
        Returns:
            True if deletion successful, False otherwise
        """
        bucket = bucket_name or self._upload_bucket
        
        try:
            self._client.delete_object(
                Bucket=bucket,
                Key=object_key
            )
            
            logger.info(f"Successfully deleted {bucket}/{object_key}")
            return True
        except ClientError as e:
            logger.error(f"Error deleting file from S3: {str(e)}", exc_info=True)
            return False
    
    def copy_file(
        self,
        source_key: str,
        destination_key: str,
        source_bucket: str = None,
        destination_bucket: str = None
    ) -> bool:
        """
        Copies a file from one S3 location to another.
        
        Args:
            source_key: The key (path) of the source object
            destination_key: The key (path) for the destination object
            source_bucket: Source S3 bucket name (defaults to self._upload_bucket)
            destination_bucket: Destination S3 bucket name (defaults to self._processed_bucket)
            
        Returns:
            True if copy successful, False otherwise
        """
        src_bucket = source_bucket or self._upload_bucket
        dst_bucket = destination_bucket or self._processed_bucket
        
        try:
            copy_source = {
                'Bucket': src_bucket,
                'Key': source_key
            }
            
            self._client.copy_object(
                CopySource=copy_source,
                Bucket=dst_bucket,
                Key=destination_key,
                ServerSideEncryption='AES256'
            )
            
            logger.info(f"Successfully copied {src_bucket}/{source_key} to {dst_bucket}/{destination_key}")
            return True
        except ClientError as e:
            logger.error(f"Error copying file in S3: {str(e)}", exc_info=True)
            return False
    
    def move_to_quarantine(
        self,
        source_key: str,
        source_bucket: str = None
    ) -> bool:
        """
        Moves a file to the quarantine bucket for security isolation.
        
        Args:
            source_key: The key (path) of the source object
            source_bucket: Source S3 bucket name (defaults to self._upload_bucket)
            
        Returns:
            True if move successful, False otherwise
        """
        src_bucket = source_bucket or self._upload_bucket
        # Prefix with 'quarantine/' to indicate the security status
        quarantine_key = f"quarantine/{os.path.basename(source_key)}"
        
        # First, copy the file to quarantine bucket
        copy_success = self.copy_file(
            source_key=source_key,
            destination_key=quarantine_key,
            source_bucket=src_bucket,
            destination_bucket=self._quarantine_bucket
        )
        
        if copy_success:
            # If copy succeeded, delete the original file
            delete_success = self.delete_file(source_key, src_bucket)
            if delete_success:
                logger.info(f"Successfully moved {src_bucket}/{source_key} to quarantine bucket")
                return True
            else:
                logger.warning(
                    f"File copied to quarantine bucket, but failed to delete original at {src_bucket}/{source_key}"
                )
                return True  # Still consider it a success since the file is in quarantine
        else:
            logger.error(f"Failed to move {src_bucket}/{source_key} to quarantine bucket")
            return False
    
    def check_file_exists(
        self,
        object_key: str,
        bucket_name: str = None
    ) -> bool:
        """
        Checks if a file exists in S3 bucket.
        
        Args:
            object_key: The key (path) of the object in S3
            bucket_name: S3 bucket name (defaults to self._upload_bucket)
            
        Returns:
            True if file exists, False otherwise
        """
        bucket = bucket_name or self._upload_bucket
        
        try:
            self._client.head_object(
                Bucket=bucket,
                Key=object_key
            )
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            else:
                logger.error(f"Error checking if file exists: {str(e)}", exc_info=True)
                # Re-raise for other types of errors
                raise
    
    def get_file_size(
        self,
        object_key: str,
        bucket_name: str = None
    ) -> int:
        """
        Gets the size of a file in S3 bucket.
        
        Args:
            object_key: The key (path) of the object in S3
            bucket_name: S3 bucket name (defaults to self._upload_bucket)
            
        Returns:
            Size of the file in bytes, or -1 if file not found
        """
        bucket = bucket_name or self._upload_bucket
        
        try:
            response = self._client.head_object(
                Bucket=bucket,
                Key=object_key
            )
            return response['ContentLength']
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                logger.warning(f"File not found when getting size: {bucket}/{object_key}")
                return -1
            else:
                logger.error(f"Error getting file size: {str(e)}", exc_info=True)
                return -1
    
    def get_file_metadata(
        self,
        object_key: str,
        bucket_name: str = None
    ) -> Dict[str, str]:
        """
        Gets the metadata of a file in S3 bucket.
        
        Args:
            object_key: The key (path) of the object in S3
            bucket_name: S3 bucket name (defaults to self._upload_bucket)
            
        Returns:
            File metadata, or empty dict if file not found
        """
        bucket = bucket_name or self._upload_bucket
        
        try:
            response = self._client.head_object(
                Bucket=bucket,
                Key=object_key
            )
            return response.get('Metadata', {})
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                logger.warning(f"File not found when getting metadata: {bucket}/{object_key}")
                return {}
            else:
                logger.error(f"Error getting file metadata: {str(e)}", exc_info=True)
                return {}
    
    def list_files(
        self,
        prefix: str = '',
        bucket_name: str = None,
        max_keys: int = 1000
    ) -> List[str]:
        """
        Lists files in an S3 bucket with optional prefix.
        
        Args:
            prefix: Object key prefix to filter results
            bucket_name: S3 bucket name (defaults to self._upload_bucket)
            max_keys: Maximum number of keys to return
            
        Returns:
            List of object keys matching the prefix
        """
        bucket = bucket_name or self._upload_bucket
        
        try:
            result = []
            response = self._client.list_objects_v2(
                Bucket=bucket,
                Prefix=prefix,
                MaxKeys=max_keys
            )
            
            if 'Contents' in response:
                for obj in response['Contents']:
                    result.append(obj['Key'])
                    
            # Handle pagination if there are more objects
            while response.get('IsTruncated', False) and len(result) < max_keys:
                response = self._client.list_objects_v2(
                    Bucket=bucket,
                    Prefix=prefix,
                    MaxKeys=max_keys - len(result),
                    ContinuationToken=response['NextContinuationToken']
                )
                
                if 'Contents' in response:
                    for obj in response['Contents']:
                        result.append(obj['Key'])
            
            return result
        except ClientError as e:
            logger.error(f"Error listing files in S3: {str(e)}", exc_info=True)
            return []
    
    def get_object(
        self,
        object_key: str,
        bucket_name: str = None
    ) -> Optional[Dict[str, Any]]:
        """
        Gets an object from S3 bucket.
        
        Args:
            object_key: The key (path) of the object in S3
            bucket_name: S3 bucket name (defaults to self._processed_bucket)
            
        Returns:
            Object data and metadata, or None if not found
        """
        bucket = bucket_name or self._processed_bucket
        
        try:
            response = self._client.get_object(
                Bucket=bucket,
                Key=object_key
            )
            
            result = {
                'Body': response['Body'],
                'ContentType': response.get('ContentType'),
                'ContentLength': response.get('ContentLength'),
                'Metadata': response.get('Metadata', {}),
                'LastModified': response.get('LastModified')
            }
            
            return result
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                logger.warning(f"Object not found: {bucket}/{object_key}")
                return None
            else:
                logger.error(f"Error getting object from S3: {str(e)}", exc_info=True)
                return None