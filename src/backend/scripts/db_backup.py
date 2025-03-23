#!/usr/bin/env python3
"""
Database Backup Script for IndiVillage Application

This script creates PostgreSQL database backups, compresses them, and uploads them to AWS S3.
It can be run manually or as a scheduled cron job for automated backups.

Usage:
    python db_backup.py [options]

Options:
    --no-upload          Don't upload to S3
    --no-cleanup-local   Don't clean up old local backups
    --no-cleanup-cloud   Don't clean up old S3 backups
    --format {custom,plain}  Backup format (default: custom)
    --retention-days N   Number of days to retain backups (default: 30)
"""

import os
import sys
import subprocess
import datetime
import argparse
import tempfile
import shutil
import gzip

import boto3  # v1.26.0
from botocore.exceptions import ClientError  # v1.29.0

# Import internal modules
from ..app.core.config import settings
from ..app.core.logging import get_logger
from ..app.utils.aws_utils import get_s3_client, handle_aws_exception, generate_s3_key

# Initialize logger
logger = get_logger(__name__)

# Global constants
BACKUP_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../backups')
S3_BACKUP_PREFIX = 'database/backups/'
BACKUP_RETENTION_DAYS = 30


def create_backup_directory(backup_dir: str = None) -> str:
    """
    Creates the backup directory if it doesn't exist
    
    Args:
        backup_dir: Path to the backup directory
        
    Returns:
        Path to the backup directory
    """
    if not backup_dir:
        backup_dir = BACKUP_DIR
        
    os.makedirs(backup_dir, exist_ok=True)
    logger.info(f"Backup directory created/confirmed: {backup_dir}")
    
    return backup_dir


def get_db_connection_params() -> dict:
    """
    Extracts database connection parameters from settings
    
    Returns:
        Dictionary containing database connection parameters
    """
    db_params = {}
    
    # Check if DATABASE_URL is provided
    if settings.DATABASE_URL:
        # Parse DATABASE_URL to extract components
        # Format: postgresql://user:password@host:port/dbname
        url = settings.DATABASE_URL
        
        # Parse URL components
        if url.startswith('postgresql://'):
            url = url[len('postgresql://'):]
            
            # Extract username and password
            auth, rest = url.split('@', 1) if '@' in url else ('', url)
            if ':' in auth:
                db_params['db_user'], db_params['db_password'] = auth.split(':', 1)
            
            # Extract host, port, and database name
            host_port, db_name = rest.split('/', 1) if '/' in rest else (rest, '')
            if ':' in host_port:
                db_params['db_host'], db_params['db_port'] = host_port.split(':', 1)
            else:
                db_params['db_host'] = host_port
                db_params['db_port'] = '5432'  # Default PostgreSQL port
                
            db_params['db_name'] = db_name
    else:
        # Use individual settings
        db_params = {
            'db_name': settings.DB_NAME,
            'db_user': settings.DB_USER,
            'db_password': settings.DB_PASSWORD,
            'db_host': settings.DB_HOST,
            'db_port': settings.DB_PORT or '5432'
        }
    
    logger.debug("Database connection parameters retrieved", 
                extra={"params": {k: v for k, v in db_params.items() if k != 'db_password'}})
    return db_params


def create_database_backup(db_params: dict, output_file: str, format: str = 'custom') -> bool:
    """
    Creates a database backup using pg_dump
    
    Args:
        db_params: Database connection parameters
        output_file: Path to the output backup file
        format: Backup format ('custom' or 'plain')
        
    Returns:
        True if backup was successful, False otherwise
    """
    # Build pg_dump command
    pg_dump_cmd = [
        'pg_dump',
        '--host', db_params['db_host'],
        '--port', str(db_params['db_port']),
        '--username', db_params['db_user'],
        '--dbname', db_params['db_name']
    ]
    
    # Add format flag
    if format == 'custom':
        pg_dump_cmd.extend(['-F', 'c'])  # Custom format
    else:
        pg_dump_cmd.extend(['-F', 'p'])  # Plain format
    
    # Add output file
    pg_dump_cmd.extend(['-f', output_file])
    
    # Set PGPASSWORD environment variable for authentication
    env = os.environ.copy()
    env['PGPASSWORD'] = db_params['db_password']
    
    try:
        logger.info(f"Starting database backup to {output_file}")
        result = subprocess.run(
            pg_dump_cmd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            logger.info(f"Database backup completed successfully: {output_file}")
            return True
        else:
            logger.error(f"Database backup failed with exit code {result.returncode}", 
                         extra={"error": result.stderr})
            return False
            
    except Exception as e:
        logger.error(f"Error during database backup: {str(e)}", exc_info=True)
        return False


def compress_backup(input_file: str, output_file: str = None) -> str:
    """
    Compresses a backup file using gzip
    
    Args:
        input_file: Path to the input file
        output_file: Path to the output compressed file (defaults to input_file + '.gz')
        
    Returns:
        Path to the compressed file
    """
    if not output_file:
        output_file = input_file + '.gz'
        
    try:
        logger.info(f"Compressing backup file: {input_file} -> {output_file}")
        
        with open(input_file, 'rb') as f_in:
            with gzip.open(output_file, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
                
        logger.info(f"Compression completed: {output_file}")
        return output_file
    except Exception as e:
        logger.error(f"Error compressing backup file: {str(e)}", exc_info=True)
        return None


def upload_to_s3(file_path: str, bucket_name: str = None, prefix: str = None) -> bool:
    """
    Uploads a backup file to AWS S3
    
    Args:
        file_path: Path to the file to upload
        bucket_name: S3 bucket name (defaults to settings.AWS_S3_BUCKET_NAME)
        prefix: S3 object key prefix (defaults to S3_BACKUP_PREFIX)
        
    Returns:
        True if upload was successful, False otherwise
    """
    if not bucket_name:
        bucket_name = settings.AWS_S3_BUCKET_NAME
        
    if not prefix:
        prefix = S3_BACKUP_PREFIX
        
    try:
        s3_client = get_s3_client()
        
        # Create S3 object key
        filename = os.path.basename(file_path)
        s3_key = generate_s3_key(filename, prefix)
        
        logger.info(f"Uploading backup to S3: {file_path} -> s3://{bucket_name}/{s3_key}")
        
        # Upload file
        s3_client.upload_file(file_path, bucket_name, s3_key)
        
        logger.info(f"Upload to S3 completed: s3://{bucket_name}/{s3_key}")
        return True
    except Exception as e:
        error_details = handle_aws_exception(e, "upload backup to S3", file_path)
        logger.error(f"Failed to upload backup to S3: {str(e)}", extra={"details": error_details})
        return False


def cleanup_old_backups(backup_dir: str = None, retention_days: int = None) -> int:
    """
    Removes backup files older than retention period
    
    Args:
        backup_dir: Directory containing backup files
        retention_days: Number of days to retain backups
        
    Returns:
        Number of files deleted
    """
    if not backup_dir:
        backup_dir = BACKUP_DIR
        
    if not retention_days:
        retention_days = BACKUP_RETENTION_DAYS
        
    try:
        logger.info(f"Cleaning up local backups older than {retention_days} days in {backup_dir}")
        
        # Calculate cutoff date
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=retention_days)
        deleted_count = 0
        
        # List all files in backup directory
        for filename in os.listdir(backup_dir):
            file_path = os.path.join(backup_dir, filename)
            
            # Skip if not a file
            if not os.path.isfile(file_path):
                continue
                
            # Check if file is a backup file (simple check)
            if not (filename.endswith('.dump') or filename.endswith('.sql') or 
                    filename.endswith('.gz') or filename.endswith('.bz2')):
                continue
                
            # Check file modification time
            file_mod_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
            if file_mod_time < cutoff_date:
                logger.debug(f"Deleting old backup file: {file_path} (modified: {file_mod_time})")
                os.remove(file_path)
                deleted_count += 1
                
        logger.info(f"Cleanup completed: {deleted_count} old backup files deleted")
        return deleted_count
    except Exception as e:
        logger.error(f"Error cleaning up old backups: {str(e)}", exc_info=True)
        return 0


def cleanup_s3_backups(bucket_name: str = None, prefix: str = None, retention_days: int = None) -> int:
    """
    Removes S3 backup objects older than retention period
    
    Args:
        bucket_name: S3 bucket name
        prefix: S3 object key prefix
        retention_days: Number of days to retain backups
        
    Returns:
        Number of objects deleted
    """
    if not bucket_name:
        bucket_name = settings.AWS_S3_BUCKET_NAME
        
    if not prefix:
        prefix = S3_BACKUP_PREFIX
        
    if not retention_days:
        retention_days = BACKUP_RETENTION_DAYS
        
    try:
        logger.info(f"Cleaning up S3 backups older than {retention_days} days in s3://{bucket_name}/{prefix}")
        
        s3_client = get_s3_client()
        
        # Calculate cutoff date
        cutoff_date = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=retention_days)
        
        # List objects in bucket with prefix
        paginator = s3_client.get_paginator('list_objects_v2')
        old_objects = []
        
        for page in paginator.paginate(Bucket=bucket_name, Prefix=prefix):
            if 'Contents' not in page:
                continue
                
            for obj in page['Contents']:
                # Check if object is older than cutoff date
                if obj['LastModified'] < cutoff_date:
                    old_objects.append({'Key': obj['Key']})
        
        # Delete old objects if any
        if old_objects:
            delete_response = s3_client.delete_objects(
                Bucket=bucket_name,
                Delete={'Objects': old_objects, 'Quiet': True}
            )
            
            deleted_count = len(old_objects)
            errors = delete_response.get('Errors', [])
            
            if errors:
                logger.warning(f"Some errors occurred during S3 cleanup", extra={"errors": errors})
                deleted_count -= len(errors)
                
            logger.info(f"S3 cleanup completed: {deleted_count} old backup objects deleted")
            return deleted_count
        else:
            logger.info("No old S3 backup objects to delete")
            return 0
            
    except Exception as e:
        error_details = handle_aws_exception(e, "cleanup S3 backups", f"s3://{bucket_name}/{prefix}")
        logger.error(f"Failed to clean up S3 backups: {str(e)}", extra={"details": error_details})
        return 0


def run_backup(upload_to_cloud: bool = True, cleanup_local: bool = True, 
              cleanup_cloud: bool = True, backup_format: str = 'custom') -> dict:
    """
    Main function to execute the backup process
    
    Args:
        upload_to_cloud: Whether to upload the backup to S3
        cleanup_local: Whether to clean up old local backups
        cleanup_cloud: Whether to clean up old S3 backups
        backup_format: Backup format ('custom' or 'plain')
        
    Returns:
        Dictionary with backup result information
    """
    logger.info("Starting database backup process")
    
    result = {
        'success': False,
        'file_path': None,
        's3_path': None,
        'timestamp': datetime.datetime.now().isoformat(),
        'environment': settings.ENVIRONMENT
    }
    
    try:
        # Create backup directory
        backup_dir = create_backup_directory()
        
        # Get database connection parameters
        db_params = get_db_connection_params()
        
        # Generate backup filename with timestamp
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"{settings.DB_NAME or 'indivillage'}_{timestamp}.{'dump' if backup_format == 'custom' else 'sql'}"
        backup_file_path = os.path.join(backup_dir, backup_filename)
        
        # Create database backup
        if create_database_backup(db_params, backup_file_path, backup_format):
            # Compress backup file
            compressed_file_path = compress_backup(backup_file_path)
            
            if compressed_file_path:
                result['file_path'] = compressed_file_path
                
                # Upload to S3 if requested
                if upload_to_cloud:
                    s3_uploaded = upload_to_s3(compressed_file_path)
                    if s3_uploaded:
                        # Generate S3 path information for result
                        filename = os.path.basename(compressed_file_path)
                        s3_key = generate_s3_key(filename, S3_BACKUP_PREFIX)
                        result['s3_path'] = f"s3://{settings.AWS_S3_BUCKET_NAME}/{s3_key}"
                
                # Clean up old local backups if requested
                if cleanup_local:
                    deleted_local = cleanup_old_backups()
                    result['deleted_local'] = deleted_local
                
                # Clean up old S3 backups if requested
                if cleanup_cloud and upload_to_cloud:
                    deleted_cloud = cleanup_s3_backups()
                    result['deleted_cloud'] = deleted_cloud
                
                result['success'] = True
                logger.info("Database backup process completed successfully")
            else:
                logger.error("Backup compression failed")
        else:
            logger.error("Database backup failed")
            
    except Exception as e:
        logger.error(f"Unexpected error during backup process: {str(e)}", exc_info=True)
        result['error'] = str(e)
        
    return result


def parse_arguments():
    """
    Parses command line arguments for the script
    
    Returns:
        argparse.Namespace: Parsed command line arguments
    """
    parser = argparse.ArgumentParser(description='Database backup script for IndiVillage application')
    
    parser.add_argument('--no-upload', action='store_true', 
                        help='Do not upload backup to S3')
    
    parser.add_argument('--no-cleanup-local', action='store_true',
                        help='Do not clean up old local backups')
    
    parser.add_argument('--no-cleanup-cloud', action='store_true',
                        help='Do not clean up old S3 backups')
    
    parser.add_argument('--format', choices=['custom', 'plain'], default='custom',
                        help='Backup format (custom or plain)')
    
    parser.add_argument('--retention-days', type=int,
                        help=f'Number of days to retain backups (default: {BACKUP_RETENTION_DAYS})')
    
    return parser.parse_args()


def main():
    """
    Main entry point for the script
    
    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    args = parse_arguments()
    
    # Process arguments
    upload_to_cloud = not args.no_upload
    cleanup_local = not args.no_cleanup_local
    cleanup_cloud = not args.no_cleanup_cloud
    backup_format = args.format
    
    # Update global retention days if specified
    global BACKUP_RETENTION_DAYS
    if args.retention_days:
        BACKUP_RETENTION_DAYS = args.retention_days
    
    # Run backup
    result = run_backup(
        upload_to_cloud=upload_to_cloud,
        cleanup_local=cleanup_local,
        cleanup_cloud=cleanup_cloud,
        backup_format=backup_format
    )
    
    # Return success/failure exit code
    if result['success']:
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())