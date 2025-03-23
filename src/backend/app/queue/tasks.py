# typing
from typing import Dict, List, Optional, Any, Union

# json
import json  # standard library
# uuid
import uuid  # standard library
# datetime
import datetime  # standard library
# traceback
import traceback  # standard library

# sqlalchemy.orm
from sqlalchemy.orm import Session  # sqlalchemy ^1.4.0

# Import application configuration settings
from ..core.config import settings
# Import logger for security-related logging
from ..utils.logging_utils import get_component_logger
# Import function to send messages to queues
from . import send_message
# Import queue names
from . import TASK_QUEUE, FILE_PROCESSING_QUEUE, NOTIFICATION_QUEUE, CRM_SYNC_QUEUE
# Import the FileProcessingService class
from ..services.file_processing_service import FileProcessingService
# Import the FormProcessingService class
from ..services.form_processing_service import FormProcessingService
# Import the EmailService class
from ..services.email_service import EmailService
# Import the function to sync form submissions to CRM
from ..services.crm_service import sync_form_submission_to_crm
# Import the function to process pending CRM submissions
from ..services.crm_service import process_pending_submissions
# Import the function to retry failed CRM synchronizations
from ..services.crm_service import retry_failed_crm_sync
# Import the database session factory
from ..db.session import SessionLocal
# Import the FormSubmission model
from ..api.v1.models.form_submission import FormSubmission
# Import the FileUpload model
from ..api.v1.models.file_upload import FileUpload

# Initialize logger for tasks
logger = get_component_logger('tasks')

# Initialize services
file_processing_service = FileProcessingService()
form_processing_service = FormProcessingService()
email_service = EmailService()

# Define maximum retry attempts
MAX_RETRIES = 3

# Define retry delays in seconds
RETRY_DELAYS = {1: 60, 2: 300, 3: 1800}


def queue_task(task_name: str, task_data: dict, queue_name: str, delay_seconds: int = 0) -> dict:
    """
    Queues a task for asynchronous processing

    Args:
        task_name (str): Name of the task
        task_data (dict): Data for the task
        queue_name (str): Name of the queue
        delay_seconds (int): Delay in seconds before the message is visible

    Returns:
        dict: Response containing MessageId and other metadata
    """
    # Create message body with task_name and task_data
    message_body = {
        'task_name': task_name,
        'task_data': task_data
    }
    # Log queueing of task with task name and queue name
    logger.info(f"Queueing task '{task_name}' on queue '{queue_name}'")
    # Call send_message with message body, queue name, and delay
    response = send_message(message_body, queue_name, delay_seconds)
    # Return the response from send_message
    return response


def queue_retry(task_name: str, task_data: dict, queue_name: str, retry_count: int) -> dict:
    """
    Queues a failed task for retry with exponential backoff

    Args:
        task_name (str): Name of the task
        task_data (dict): Data for the task
        queue_name (str): Name of the queue
        retry_count (int): Number of times the task has been retried

    Returns:
        dict: Response containing MessageId and other metadata or None if max retries exceeded
    """
    # Check if retry_count exceeds MAX_RETRIES
    if retry_count > MAX_RETRIES:
        logger.error(f"Max retries exceeded for task '{task_name}'")
        return None
    # Increment retry_count in task_data
    task_data['retry_count'] = retry_count + 1
    # Calculate delay based on retry count using RETRY_DELAYS
    delay_seconds = RETRY_DELAYS.get(retry_count + 1, 3600)  # Default to 1 hour
    # Log retry attempt with task name, retry count, and delay
    logger.info(f"Retrying task '{task_name}' (attempt {retry_count + 1}) with delay {delay_seconds}s")
    # Call queue_task with updated task_data and calculated delay
    response = queue_task(task_name, task_data, queue_name, delay_seconds)
    # Return the response from queue_task
    return response


def process_file_upload(task_data: dict) -> dict:
    """
    Processes a file upload task

    Args:
        task_data (dict): Data for the task

    Returns:
        dict: Processing result
    """
    # Extract upload_id from task_data
    upload_id = task_data.get('upload_id')
    # Log start of file upload processing
    logger.info(f"Processing file upload with ID: {upload_id}")
    # Create database session
    db = SessionLocal()
    try:
        # Call file_processing_service.process_file with upload_id and session
        processing_results = file_processing_service.process_file(upload_id, db)
        # If processing successful, queue analyze_file_upload task
        if processing_results.get('success'):
            analyze_task_data = {'upload_id': upload_id}
            queue_task('analyze_file_upload', analyze_task_data, FILE_PROCESSING_QUEUE)
            # Return success result with processing details
            return {
                'success': True,
                'upload_id': upload_id,
                'details': processing_results
            }
        else:
            # Log processing failure
            logger.error(f"File processing failed for upload ID: {upload_id}")
            return {
                'success': False,
                'upload_id': upload_id,
                'error': processing_results.get('error', 'Unknown processing error')
            }
    except Exception as e:
        # Log error
        logger.error(f"Error processing file upload: {str(e)}")
        # Return error result
        return {
            'success': False,
            'upload_id': upload_id,
            'error': str(e)
        }
    finally:
        # Ensure database session is closed
        db.close()


def analyze_file_upload(task_data: dict) -> dict:
    """
    Analyzes a processed file upload

    Args:
        task_data (dict): Data for the task

    Returns:
        dict: Analysis result
    """
    # Extract upload_id from task_data
    upload_id = task_data.get('upload_id')
    # Log start of file analysis
    logger.info(f"Analyzing file upload with ID: {upload_id}")
    # Create database session
    db = SessionLocal()
    try:
        # Call file_processing_service.get_processing_results with upload_id and session
        analysis_results = file_processing_service.get_processing_results(upload_id, db)
        # If analysis successful, queue send_upload_notification task
        if analysis_results.get('success'):
            notification_task_data = {
                'upload_id': upload_id,
                'processing_status': 'completed'
            }
            queue_task('send_upload_notification', notification_task_data, NOTIFICATION_QUEUE)
            # Return success result with analysis details
            return {
                'success': True,
                'upload_id': upload_id,
                'details': analysis_results
            }
        else:
            # Log analysis failure
            logger.error(f"File analysis failed for upload ID: {upload_id}")
            return {
                'success': False,
                'upload_id': upload_id,
                'error': analysis_results.get('error', 'Unknown analysis error')
            }
    except Exception as e:
        # Log error
        logger.error(f"Error analyzing file upload: {str(e)}")
        # Return error result
        return {
            'success': False,
            'upload_id': upload_id,
            'error': str(e)
        }
    finally:
        # Ensure database session is closed
        db.close()


def send_upload_notification(task_data: dict) -> dict:
    """
    Sends notification for a completed file upload

    Args:
        task_data (dict): Data for the task

    Returns:
        dict: Notification result
    """
    # Extract upload_id and processing_status from task_data
    upload_id = task_data.get('upload_id')
    processing_status = task_data.get('processing_status')
    # Log start of upload notification
    logger.info(f"Sending upload notification for upload ID: {upload_id}, status: {processing_status}")
    # Create database session
    db = SessionLocal()
    try:
        # Query database for FileUpload record
        file_upload = db.query(FileUpload).filter(FileUpload.id == upload_id).first()
        if not file_upload:
            logger.error(f"FileUpload record not found for ID: {upload_id}")
            return {
                'success': False,
                'upload_id': upload_id,
                'error': 'FileUpload record not found'
            }
        # Query database for user information
        user = file_upload.user
        if not user:
            logger.error(f"User record not found for upload ID: {upload_id}")
            return {
                'success': False,
                'upload_id': upload_id,
                'error': 'User record not found'
            }
        # Send success notification
        if processing_status == 'completed':
            email_service.send_upload_complete_notification(
                to_email=user.email,
                name=user.name,
                upload_data=file_upload.to_dict(),
                processing_results=file_upload.analysis_result.to_dict() if file_upload.analysis_result else {}
            )
        # Send failure notification
        elif processing_status == 'failed':
            email_service.send_upload_failed_notification(
                to_email=user.email,
                name=user.name,
                upload_data=file_upload.to_dict(),
                error_message='File processing failed'
            )
        # Return notification result
        return {
            'success': True,
            'upload_id': upload_id,
            'status': processing_status
        }
    except Exception as e:
        # Log error
        logger.error(f"Error sending upload notification: {str(e)}")
        # Return error result
        return {
            'success': False,
            'upload_id': upload_id,
            'error': str(e)
        }
    finally:
        # Ensure database session is closed
        db.close()


def process_form_submission(task_data: dict) -> dict:
    """
    Processes a form submission task

    Args:
        task_data (dict): Data for the task

    Returns:
        dict: Processing result
    """
    # Extract submission_id and form_type from task_data
    submission_id = task_data.get('submission_id')
    form_type = task_data.get('form_type')
    # Log start of form submission processing
    logger.info(f"Processing form submission with ID: {submission_id}, type: {form_type}")
    # Create database session
    db = SessionLocal()
    try:
        # Query database for FormSubmission record
        form_submission = db.query(FormSubmission).filter(FormSubmission.id == submission_id).first()
        if not form_submission:
            logger.error(f"FormSubmission record not found for ID: {submission_id}")
            return {
                'success': False,
                'submission_id': submission_id,
                'error': 'FormSubmission record not found'
            }
        # Call appropriate form processing method based on form_type
        if form_type == 'contact':
            form_processing_service.process_contact_form(form_submission)
        elif form_type == 'demo_request':
            form_processing_service.process_demo_request(form_submission)
        elif form_type == 'quote_request':
            form_processing_service.process_quote_request(form_submission)
        else:
            logger.error(f"Invalid form type: {form_type}")
            return {
                'success': False,
                'submission_id': submission_id,
                'error': f'Invalid form type: {form_type}'
            }
        # Queue sync_with_crm task
        crm_task_data = {'submission_id': submission_id}
        queue_task('sync_with_crm', crm_task_data, CRM_SYNC_QUEUE)
        # Return success result
        return {
            'success': True,
            'submission_id': submission_id
        }
    except Exception as e:
        # Log error
        logger.error(f"Error processing form submission: {str(e)}")
        # Return error result
        return {
            'success': False,
            'submission_id': submission_id,
            'error': str(e)
        }
    finally:
        # Ensure database session is closed
        db.close()


def sync_with_crm(task_data: dict) -> dict:
    """
    Synchronizes a form submission with CRM

    Args:
        task_data (dict): Data for the task

    Returns:
        dict: Synchronization result
    """
    # Extract submission_id from task_data
    submission_id = task_data.get('submission_id')
    # Log start of CRM synchronization
    logger.info(f"Synchronizing form submission with CRM, ID: {submission_id}")
    # Create database session
    db = SessionLocal()
    try:
        # Query database for FormSubmission record
        form_submission = db.query(FormSubmission).filter(FormSubmission.id == submission_id).first()
        if not form_submission:
            logger.error(f"FormSubmission record not found for ID: {submission_id}")
            return {
                'success': False,
                'submission_id': submission_id,
                'error': 'FormSubmission record not found'
            }
        # Call sync_form_submission_to_crm with form submission
        crm_details = sync_form_submission_to_crm(form_submission)
        # Return success result with CRM details
        return {
            'success': True,
            'submission_id': submission_id,
            'crm_details': crm_details
        }
    except Exception as e:
        # Log error
        logger.error(f"Error synchronizing with CRM: {str(e)}")
        # Return error result
        return {
            'success': False,
            'submission_id': submission_id,
            'error': str(e)
        }
    finally:
        # Ensure database session is closed
        db.close()


def retry_failed_task(task_data: dict) -> dict:
    """
    Retries a previously failed task

    Args:
        task_data (dict): Data for the task

    Returns:
        dict: Retry result
    """
    # Extract original_task_name, original_task_data, and original_queue from task_data
    original_task_name = task_data.get('original_task_name')
    original_task_data = task_data.get('original_task_data')
    original_queue = task_data.get('original_queue')
    retry_count = task_data.get('retry_count', 0)
    # Log retry attempt for failed task
    logger.info(f"Retrying failed task: {original_task_name}")
    # Call queue_task with original task information
    response = queue_retry(original_task_name, original_task_data, original_queue, retry_count)
    # Return success result with retry details
    return {
        'success': True,
        'task_name': original_task_name,
        'queue': original_queue,
        'response': response
    }


def process_pending_crm_submissions(task_data: dict) -> dict:
    """
    Processes pending CRM submissions in batch

    Args:
        task_data (dict): Data for the task

    Returns:
        dict: Batch processing result
    """
    # Extract batch_size from task_data or use default
    batch_size = task_data.get('batch_size', 10)
    # Log start of batch processing
    logger.info(f"Processing pending CRM submissions in batch, size: {batch_size}")
    try:
        # Call process_pending_submissions with batch size
        summary = process_pending_submissions(batch_size)
        # Return success result with processing summary
        return {
            'success': True,
            'summary': summary
        }
    except Exception as e:
        # Log error
        logger.error(f"Error processing pending CRM submissions: {str(e)}")
        # Return error result
        return {
            'success': False,
            'error': str(e)
        }


def retry_failed_crm_task(task_data: dict) -> dict:
    """
    Retries a failed CRM synchronization task

    Args:
        task_data (dict): Data for the task

    Returns:
        dict: Retry result
    """
    # Extract submission_id from task_data
    submission_id = task_data.get('submission_id')
    # Log retry attempt for failed CRM sync
    logger.info(f"Retrying failed CRM sync for submission ID: {submission_id}")
    try:
        # Call retry_failed_crm_sync with submission ID
        retry_failed_crm_sync(submission_id)
        # Return success result with retry details
        return {
            'success': True,
            'submission_id': submission_id
        }
    except Exception as e:
        # Log error
        logger.error(f"Error retrying failed CRM sync: {str(e)}")
        # Return error result
        return {
            'success': False,
            'submission_id': submission_id,
            'error': str(e)
        }


def schedule_recurring_tasks() -> dict:
    """
    Schedules recurring tasks for system maintenance

    Returns:
        dict: Scheduling result
    """
    # Log scheduling of recurring tasks
    logger.info("Scheduling recurring tasks")
    try:
        # Schedule process_pending_crm_submissions task
        task_data = {'batch_size': 50}
        queue_task('process_pending_crm_submissions', task_data, TASK_QUEUE, delay_seconds=86400)  # Every 24 hours
        # Return success result with scheduled task details
        return {
            'success': True,
            'scheduled_tasks': ['process_pending_crm_submissions']
        }
    except Exception as e:
        # Log error
        logger.error(f"Error scheduling recurring tasks: {str(e)}")
        # Return error result
        return {
            'success': False,
            'error': str(e)
        }


__all__ = [
    'queue_task',
    'queue_retry',
    'process_file_upload',
    'analyze_file_upload',
    'send_upload_notification',
    'process_form_submission',
    'sync_with_crm',
    'retry_failed_task',
    'process_pending_crm_submissions',
    'retry_failed_crm_task',
    'schedule_recurring_tasks'
]