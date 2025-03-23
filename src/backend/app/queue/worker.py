import json
import time
import signal
import sys
import traceback
from typing import Dict, List, Optional, Any, Union

# Standard library imports
import argparse

# Internal imports
from ..core.config import settings  # Import application configuration settings
from ..utils.logging_utils import get_component_logger  # Get configured logger for worker operations
from . import receive_messages, delete_message  # Receive messages from queues, Delete processed messages from queues
from . import TASK_QUEUE, FILE_PROCESSING_QUEUE, NOTIFICATION_QUEUE, CRM_SYNC_QUEUE  # Queue name for general tasks, Queue name for file processing tasks, Queue name for notification tasks, Queue name for CRM synchronization tasks
from .tasks import process_file_upload, analyze_file_upload, send_upload_notification, process_form_submission, sync_with_crm, retry_failed_task, process_pending_crm_submissions, retry_failed_crm_task, schedule_recurring_tasks  # Task handler for processing file uploads, Task handler for analyzing processed files, Task handler for sending upload notifications, Task handler for processing form submissions, Task handler for CRM synchronization, Task handler for retrying failed tasks
from .tasks import queue_retry  # Function to queue a task for retry with backoff
from ..monitoring.metrics import record_queue_metrics  # Record metrics about queue processing
from ..monitoring.tracing import start_span, end_span  # Start a tracing span for task processing, End a tracing span for task processing

# Initialize logger
logger = get_component_logger('worker')

# Global flag to control worker loop
running = True

# Task handlers mapping
TASK_HANDLERS = {
    "process_file_upload": process_file_upload,
    "analyze_file_upload": analyze_file_upload,
    "send_upload_notification": send_upload_notification,
    "process_form_submission": process_form_submission,
    "sync_with_crm": sync_with_crm,
    "retry_failed_task": retry_failed_task,
    "process_pending_crm_submissions": process_pending_crm_submissions,
    "retry_failed_crm_task": retry_failed_crm_task,
    "schedule_recurring_tasks": schedule_recurring_tasks
}

# Queue configurations
QUEUE_CONFIGS = {
    TASK_QUEUE: {"visibility_timeout": 300, "wait_time": 20, "max_messages": 10},
    FILE_PROCESSING_QUEUE: {"visibility_timeout": 600, "wait_time": 20, "max_messages": 5},
    NOTIFICATION_QUEUE: {"visibility_timeout": 120, "wait_time": 20, "max_messages": 10},
    CRM_SYNC_QUEUE: {"visibility_timeout": 300, "wait_time": 20, "max_messages": 5}
}

# Maximum consecutive errors before backing off
MAX_CONSECUTIVE_ERRORS = 5


def process_message(message: Dict, queue_name: str) -> bool:
    """Processes a single message from a queue

    Args:
        message (dict): Message from the queue
        queue_name (str): Name of the queue

    Returns:
        bool: True if message was processed successfully, False otherwise
    """
    try:
        # Extract message body and parse JSON
        message_body_str = message['Body']
        message_body = json.loads(message_body_str)

        # Extract task_name and task_data from message body
        task_name = message_body['task_name']
        task_data = message_body['task_data']

        # Start a tracing span for the task
        span = start_span(name=f"task:{task_name}", attributes={"queue": queue_name})

        # Log task processing start
        logger.info(f"Processing task '{task_name}' from queue '{queue_name}'")

        # Look up task handler function from TASK_HANDLERS
        handler = TASK_HANDLERS.get(task_name)
        if handler:
            # Execute handler with task_data
            handler(task_data)

            # If successful, delete message from queue and return True
            delete_message(message, queue_name)
            logger.info(f"Successfully processed task '{task_name}' from queue '{queue_name}'")
            end_span(span, attributes={"success": True})
            return True
        else:
            logger.error(f"No handler found for task '{task_name}'")
            end_span(span, attributes={"success": False, "error": "No handler found"})
            return False

    except Exception as e:
        # Log error and handle retry logic
        logger.error(f"Error processing message: {str(e)}", exc_info=True)
        end_span(span, attributes={"success": False, "error": str(e)})
        handle_retry(message_body, queue_name, e)
        return False


def poll_queue(queue_name: str) -> int:
    """Polls a queue for messages and processes them

    Args:
        queue_name (str): Name of the queue

    Returns:
        int: Number of messages processed
    """
    processed_count = 0
    try:
        # Get queue configuration for the specified queue
        queue_config = QUEUE_CONFIGS.get(queue_name)
        if not queue_config:
            logger.error(f"No configuration found for queue '{queue_name}'")
            return 0

        # Receive messages from the queue using configuration parameters
        messages = receive_messages(
            queue_name,
            max_messages=queue_config['max_messages'],
            wait_time_seconds=queue_config['wait_time'],
            visibility_timeout=queue_config['visibility_timeout']
        )

        # Log number of messages received
        logger.debug(f"Received {len(messages)} messages from queue '{queue_name}'")

        # Process each message
        for message in messages:
            if process_message(message, queue_name):
                processed_count += 1

        # Record queue metrics for monitoring
        record_queue_metrics(queue_name, processed_count)

    except Exception as e:
        logger.error(f"Error polling queue '{queue_name}': {str(e)}", exc_info=True)

    # Return the total number of messages processed
    return processed_count


def handle_retry(message_body: Dict, queue_name: str, exception: Exception) -> bool:
    """Handles retry logic for failed message processing

    Args:
        message_body (dict): Message body
        queue_name (str): Name of the queue
        exception (Exception): Exception that occurred

    Returns:
        bool: True if message was queued for retry, False if max retries exceeded
    """
    try:
        # Extract retry_count from message_body or initialize to 0
        retry_count = message_body.get('retry_count', 0)

        # Log retry attempt with task name and exception details
        task_name = message_body.get('task_name', 'unknown_task')
        logger.warning(f"Task '{task_name}' failed, attempting retry {retry_count + 1}", exc_info=True)

        # Call queue_retry with task information and incremented retry count
        response = queue_retry(task_name, message_body, queue_name, retry_count)

        if response:
            logger.info(f"Task '{task_name}' queued for retry")
            return True
        else:
            logger.error(f"Max retries exceeded for task '{task_name}'")
            return False

    except Exception as e:
        logger.error(f"Error handling retry: {str(e)}", exc_info=True)
        return False


def run_worker(queue_names: List[str], polling_interval: int):
    """Main worker function that polls all queues in a loop

    Args:
        queue_names (List[str]): List of queue names to poll
        polling_interval (int): Interval in seconds between polling cycles
    """
    logger.info(f"Worker started, polling queues: {queue_names}")

    # Initialize error counters for each queue
    error_counters = {queue_name: 0 for queue_name in queue_names}

    # Enter main processing loop
    while running:
        try:
            # For each queue, poll for messages and process them
            for queue_name in queue_names:
                try:
                    processed_count = poll_queue(queue_name)
                    error_counters[queue_name] = 0  # Reset error counter on success
                except Exception as e:
                    error_counters[queue_name] += 1
                    logger.error(f"Error polling queue '{queue_name}': {str(e)}", exc_info=True)

                    # If consecutive errors exceed threshold, log warning and increase backoff
                    if error_counters[queue_name] > MAX_CONSECUTIVE_ERRORS:
                        logger.warning(
                            f"Consecutive errors exceeded for queue '{queue_name}', backing off",
                            extra={"consecutive_errors": error_counters[queue_name]}
                        )
                        time.sleep(polling_interval * 2)  # Double the polling interval
                else:
                    # If no errors, reset error counter and backoff for the queue
                    error_counters[queue_name] = 0

            # Sleep for polling_interval seconds between polling cycles
            time.sleep(polling_interval)

        except KeyboardInterrupt:
            # Handle keyboard interrupts for graceful shutdown
            logger.info("Received shutdown signal, exiting...")
            break

    # Log worker shutdown when loop exits
    logger.info("Worker stopped")


def handle_shutdown(signum, frame):
    """Signal handler for graceful shutdown

    Args:
        signum (int): Signal number
        frame (frame): Frame object
    """
    global running
    running = False
    logger.info("Initiating graceful shutdown...")


def parse_args():
    """Parses command line arguments for the worker

    Returns:
        argparse.Namespace: Parsed command line arguments
    """
    parser = argparse.ArgumentParser(description="IndiVillage Worker Process")
    parser.add_argument(
        "--queues",
        nargs="+",
        default=[TASK_QUEUE, FILE_PROCESSING_QUEUE, NOTIFICATION_QUEUE, CRM_SYNC_QUEUE],
        help="List of queue names to poll (default: all queues)"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=10,
        help="Polling interval in seconds (default: 10)"
    )
    return parser.parse_args()


def main():
    """Main entry point for the worker process

    Returns:
        int: Exit code (0 for success, 1 for error)
    """
    try:
        # Parse command line arguments
        args = parse_args()

        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, handle_shutdown)
        signal.signal(signal.SIGTERM, handle_shutdown)

        # Determine queues to poll based on arguments or use all queues
        queues_to_poll = args.queues

        # Log worker initialization
        logger.info(f"Worker initializing with queues: {queues_to_poll}, interval: {args.interval}")

        # Call run_worker with specified queues and polling interval
        run_worker(queues_to_poll, args.interval)

        # Return 0 for successful execution
        return 0

    except Exception as e:
        logger.critical(f"Worker failed to start: {str(e)}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())