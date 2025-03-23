import json
import uuid
import datetime
from typing import Dict, List, Optional, Any, Union

import boto3  # boto3 v1.26.0
from botocore.exceptions import ClientError  # boto3 v1.26.0

from ..core.config import settings
from ..utils.logging_utils import get_component_logger

# Initialize module logger
logger = get_component_logger('queue')

# Default SQS configuration
DEFAULT_VISIBILITY_TIMEOUT = 30  # seconds
DEFAULT_WAIT_TIME = 20  # seconds for long polling
DEFAULT_MAX_MESSAGES = 10  # maximum number of messages to receive at once

# Queue names
TASK_QUEUE = 'tasks'
FILE_PROCESSING_QUEUE = 'file_processing'
NOTIFICATION_QUEUE = 'notifications'
CRM_SYNC_QUEUE = 'crm_sync'

# Cached SQS client and queue URLs
_sqs_client = None
_queue_urls = {}


def get_sqs_client():
    """
    Returns or initializes the SQS client
    
    Returns:
        boto3.client: Initialized SQS client
    """
    global _sqs_client
    
    if _sqs_client is None:
        logger.debug("Initializing SQS client")
        _sqs_client = boto3.client(
            'sqs',
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
    
    return _sqs_client


def get_queue_url(queue_name: str) -> str:
    """
    Gets the URL for a queue by name, caching results for performance
    
    Args:
        queue_name (str): Name of the queue
        
    Returns:
        str: Queue URL for the specified queue
    """
    global _queue_urls
    
    if queue_name in _queue_urls:
        return _queue_urls[queue_name]
    
    try:
        client = get_sqs_client()
        response = client.get_queue_url(QueueName=queue_name)
        queue_url = response['QueueUrl']
        _queue_urls[queue_name] = queue_url
        logger.debug(f"Retrieved queue URL for {queue_name}")
        return queue_url
    except ClientError as e:
        logger.error(f"Error getting queue URL for {queue_name}: {str(e)}")
        raise


def send_message(message_body: dict, queue_name: str, delay_seconds: int = 0) -> dict:
    """
    Sends a message to the specified queue
    
    Args:
        message_body (dict): Message body as a dictionary
        queue_name (str): Name of the queue to send to
        delay_seconds (int): Delay in seconds before the message is visible
        
    Returns:
        dict: Response containing MessageId and other metadata
    """
    try:
        client = get_sqs_client()
        queue_url = get_queue_url(queue_name)
        
        # Add timestamp and message ID to the message
        message_body['timestamp'] = datetime.datetime.utcnow().isoformat()
        message_body['message_id'] = str(uuid.uuid4())
        
        # Convert message body to JSON string
        message_json = json.dumps(message_body)
        
        response = client.send_message(
            QueueUrl=queue_url,
            MessageBody=message_json,
            DelaySeconds=delay_seconds
        )
        
        logger.debug(f"Sent message to queue {queue_name}, message ID: {response.get('MessageId')}")
        return response
    except Exception as e:
        logger.error(f"Error sending message to queue {queue_name}: {str(e)}")
        raise


def receive_messages(
    queue_name: str,
    max_messages: int = DEFAULT_MAX_MESSAGES,
    wait_time_seconds: int = DEFAULT_WAIT_TIME,
    visibility_timeout: int = DEFAULT_VISIBILITY_TIMEOUT
) -> List[dict]:
    """
    Receives messages from the specified queue
    
    Args:
        queue_name (str): Name of the queue to receive from
        max_messages (int): Maximum number of messages to receive
        wait_time_seconds (int): Time to wait for messages in long polling
        visibility_timeout (int): Time in seconds that messages are hidden after receipt
        
    Returns:
        list: List of received messages
    """
    try:
        client = get_sqs_client()
        queue_url = get_queue_url(queue_name)
        
        response = client.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=max_messages,
            WaitTimeSeconds=wait_time_seconds,
            VisibilityTimeout=visibility_timeout,
            AttributeNames=['All'],
            MessageAttributeNames=['All']
        )
        
        messages = response.get('Messages', [])
        logger.debug(f"Received {len(messages)} messages from queue {queue_name}")
        
        return messages
    except Exception as e:
        logger.error(f"Error receiving messages from queue {queue_name}: {str(e)}")
        raise


def delete_message(message: dict, queue_name: str) -> bool:
    """
    Deletes a message from the specified queue
    
    Args:
        message (dict): The message to delete (must contain ReceiptHandle)
        queue_name (str): Name of the queue
        
    Returns:
        bool: True if deletion successful, False otherwise
    """
    try:
        client = get_sqs_client()
        queue_url = get_queue_url(queue_name)
        
        receipt_handle = message.get('ReceiptHandle')
        if not receipt_handle:
            logger.error("Cannot delete message: missing receipt handle")
            return False
        
        client.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=receipt_handle
        )
        
        logger.debug(f"Deleted message from queue {queue_name}")
        return True
    except Exception as e:
        logger.error(f"Error deleting message from queue {queue_name}: {str(e)}")
        return False


def purge_queue(queue_name: str) -> bool:
    """
    Purges all messages from the specified queue
    
    Args:
        queue_name (str): Name of the queue to purge
        
    Returns:
        bool: True if purge successful, False otherwise
    """
    try:
        client = get_sqs_client()
        queue_url = get_queue_url(queue_name)
        
        client.purge_queue(QueueUrl=queue_url)
        
        logger.info(f"Purged all messages from queue {queue_name}")
        return True
    except Exception as e:
        logger.error(f"Error purging queue {queue_name}: {str(e)}")
        return False


def get_queue_attributes(queue_name: str, attribute_names: List[str] = None) -> dict:
    """
    Gets attributes for the specified queue
    
    Args:
        queue_name (str): Name of the queue
        attribute_names (list): List of attribute names to retrieve
        
    Returns:
        dict: Queue attributes
    """
    try:
        client = get_sqs_client()
        queue_url = get_queue_url(queue_name)
        
        if attribute_names is None:
            attribute_names = ['All']
        
        response = client.get_queue_attributes(
            QueueUrl=queue_url,
            AttributeNames=attribute_names
        )
        
        return response.get('Attributes', {})
    except Exception as e:
        logger.error(f"Error getting attributes for queue {queue_name}: {str(e)}")
        return {}


def get_queue_depth(queue_name: str) -> int:
    """
    Gets the approximate number of messages in a queue
    
    Args:
        queue_name (str): Name of the queue
        
    Returns:
        int: Approximate number of messages in the queue
    """
    try:
        attributes = get_queue_attributes(
            queue_name, 
            ['ApproximateNumberOfMessages']
        )
        
        return int(attributes.get('ApproximateNumberOfMessages', 0))
    except Exception as e:
        logger.error(f"Error getting queue depth for {queue_name}: {str(e)}")
        return 0