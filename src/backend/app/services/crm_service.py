"""
Service module that provides a high-level interface for CRM integration in the IndiVillage application.

This module handles synchronization of form submissions and file uploads with HubSpot CRM,
including contact management, deal creation, and activity logging. It implements robust
error handling and retry mechanisms to ensure reliable CRM operations.
"""

import uuid
import datetime
import json
from typing import Dict, List, Optional, Any, Union

# External imports
import tenacity  # tenacity v8.2.0
from sqlalchemy.orm import Session

# Internal imports
from ..core.config import settings
from ..utils.logging_utils import get_component_logger, log_exception, mask_sensitive_data
from ..utils.crm_utils import map_form_data_to_crm, extract_contact_identifier, validate_crm_data
from ..integrations.hubspot import HubSpotClient, process_form_submission
from ..core.exceptions import IntegrationException
from ..api.v1.models.form_submission import FormSubmission, FormType, FormStatus
from ..api.v1.models.file_upload import FileUpload, UploadStatus
from ..db.session import SessionLocal

# Initialize logger
logger = get_component_logger('crm_service')


@tenacity.retry(
    stop=tenacity.stop_after_attempt(3),
    wait=tenacity.wait_exponential(multiplier=1, min=2, max=10),
    retry=tenacity.retry_if_exception_type(IntegrationException),
    reraise=True
)
def sync_form_submission_to_crm(submission_id: uuid.UUID) -> Dict[str, Any]:
    """
    Synchronizes a form submission with the CRM system.
    
    Args:
        submission_id: UUID of the form submission to synchronize
        
    Returns:
        Dict with the result of the synchronization operation
        
    Raises:
        IntegrationException: If CRM synchronization fails
    """
    # Create database session
    db = SessionLocal()
    
    try:
        # Retrieve form submission from database
        submission = db.query(FormSubmission).filter(FormSubmission.id == submission_id).first()
        
        if not submission:
            logger.error(f"Form submission not found: {submission_id}")
            return {
                "success": False,
                "error": "Form submission not found",
                "submission_id": str(submission_id)
            }
        
        # Extract form data and form type
        form_data = submission.get_data()
        form_type = submission.form_type
        
        # Log the start of CRM synchronization with masked data
        logger.info(
            f"Synchronizing form submission with CRM: {submission_id}",
            extra={
                "submission_id": str(submission_id),
                "form_type": form_type.name,
                "form_data": mask_sensitive_data(form_data)
            }
        )
        
        # Update form status to PROCESSING
        submission.update_status(FormStatus.PROCESSING)
        db.commit()
        
        # Process form submission in HubSpot
        result = process_form_submission(form_data, form_type)
        
        if result.get("success", False):
            # Update form status to COMPLETED
            submission.update_status(FormStatus.COMPLETED)
            
            # Update CRM IDs in the database
            submission.update_crm_id(result.get("contact_id"))
            
            # If there's a deal ID, store it in the data field
            if "deal_id" in result:
                form_data["deal_id"] = result["deal_id"]
                submission.set_data(form_data)
            
            db.commit()
            
            logger.info(
                f"Form submission successfully synchronized with CRM: {submission_id}",
                extra={
                    "submission_id": str(submission_id),
                    "contact_id": result.get("contact_id"),
                    "deal_id": result.get("deal_id")
                }
            )
            
            return {
                "success": True,
                "submission_id": str(submission_id),
                "contact_id": result.get("contact_id"),
                "deal_id": result.get("deal_id")
            }
        else:
            # Update form status to FAILED
            submission.update_status(FormStatus.FAILED)
            db.commit()
            
            logger.error(
                f"Failed to synchronize form submission with CRM: {submission_id}",
                extra={
                    "submission_id": str(submission_id),
                    "error": result.get("error", "Unknown error")
                }
            )
            
            return {
                "success": False,
                "error": result.get("error", "Failed to synchronize with CRM"),
                "submission_id": str(submission_id)
            }
    
    except IntegrationException as e:
        # Update form status to FAILED
        if submission:
            submission.update_status(FormStatus.FAILED)
            db.commit()
        
        # Log exception with details
        log_exception(
            logger,
            e,
            "Failed to synchronize form submission with CRM due to integration error",
            extra={
                "submission_id": str(submission_id),
                "error": str(e)
            }
        )
        
        # Re-raise the exception to trigger retry
        raise
    
    except Exception as e:
        # Update form status to FAILED
        if submission:
            submission.update_status(FormStatus.FAILED)
            db.commit()
        
        # Log exception with details
        log_exception(
            logger,
            e,
            "Failed to synchronize form submission with CRM due to unexpected error",
            extra={
                "submission_id": str(submission_id),
                "error": str(e)
            }
        )
        
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "submission_id": str(submission_id)
        }
    
    finally:
        # Close database session
        db.close()


@tenacity.retry(
    stop=tenacity.stop_after_attempt(3),
    wait=tenacity.wait_exponential(multiplier=1, min=2, max=10),
    retry=tenacity.retry_if_exception_type(IntegrationException),
    reraise=True
)
def update_contact_with_file_upload(upload_id: uuid.UUID, processing_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Updates a CRM contact record with file upload information.
    
    Args:
        upload_id: UUID of the file upload
        processing_results: Results of file processing
        
    Returns:
        Dict with the result of the CRM update operation
        
    Raises:
        IntegrationException: If CRM update fails
    """
    # Create database session
    db = SessionLocal()
    
    try:
        # Retrieve file upload from database
        upload = db.query(FileUpload).filter(FileUpload.id == upload_id).first()
        
        if not upload:
            logger.error(f"File upload not found: {upload_id}")
            return {
                "success": False,
                "error": "File upload not found",
                "upload_id": str(upload_id)
            }
        
        # Extract user information
        user = upload.user
        
        if not user or not user.email:
            logger.error(f"User information not available for upload: {upload_id}")
            return {
                "success": False,
                "error": "User information not available",
                "upload_id": str(upload_id)
            }
        
        # Prepare data for CRM update
        crm_data = prepare_file_upload_data(upload, processing_results)
        
        # Initialize HubSpot client
        hubspot_client = HubSpotClient()
        
        # Check if contact exists
        existing_contact = hubspot_client.find_contact_by_email(user.email)
        
        contact_id = None
        
        if existing_contact:
            # Update existing contact
            contact_id = existing_contact['id']
            logger.info(
                f"Updating existing contact with file upload information: {contact_id}",
                extra={
                    "contact_id": contact_id,
                    "upload_id": str(upload_id)
                }
            )
            
            hubspot_client.update_contact(contact_id, crm_data)
        else:
            # Create new contact
            logger.info(
                f"Creating new contact for file upload: {upload_id}",
                extra={"upload_id": str(upload_id)}
            )
            
            contact_data = {
                "email": user.email,
                "firstname": user.name.split()[0] if user.name and ' ' in user.name else user.name,
                "lastname": user.name.split()[-1] if user.name and ' ' in user.name else "",
                "company": user.company
            }
            
            # Add file upload data
            contact_data.update(crm_data)
            
            # Create contact
            contact = hubspot_client.create_contact(contact_data)
            contact_id = contact['id']
        
        # Log file upload activity
        if contact_id:
            activity_data = {
                "message": f"File upload: {upload.filename}",
                "file_details": {
                    "filename": upload.filename,
                    "size": upload.size,
                    "mime_type": upload.mime_type,
                    "upload_date": upload.created_at.isoformat() if upload.created_at else None
                },
                "processing_summary": processing_results.get("summary", "")
            }
            
            hubspot_client.log_activity(contact_id, "note", activity_data)
            
            # Store CRM reference in a way that's compatible with the data model
            # We'll just log this information instead of trying to update a field that might not exist
            logger.info(
                f"Associated file upload with CRM contact: {contact_id}",
                extra={
                    "upload_id": str(upload_id),
                    "contact_id": contact_id
                }
            )
            
            # Commit any changes to the database
            db.commit()
            
            logger.info(
                f"Successfully updated CRM with file upload information: {upload_id}",
                extra={
                    "contact_id": contact_id,
                    "upload_id": str(upload_id)
                }
            )
            
            return {
                "success": True,
                "upload_id": str(upload_id),
                "contact_id": contact_id
            }
        else:
            logger.error(
                f"Failed to identify or create contact for file upload: {upload_id}",
                extra={"upload_id": str(upload_id)}
            )
            
            return {
                "success": False,
                "error": "Failed to identify or create contact",
                "upload_id": str(upload_id)
            }
    
    except IntegrationException as e:
        # Log exception with details
        log_exception(
            logger,
            e,
            "Failed to update CRM with file upload information due to integration error",
            extra={
                "upload_id": str(upload_id),
                "error": str(e)
            }
        )
        
        # Re-raise the exception to trigger retry
        raise
    
    except Exception as e:
        # Log exception with details
        log_exception(
            logger,
            e,
            "Failed to update CRM with file upload information due to unexpected error",
            extra={
                "upload_id": str(upload_id),
                "error": str(e)
            }
        )
        
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "upload_id": str(upload_id)
        }
    
    finally:
        # Close database session
        db.close()


def get_crm_contact(contact_id: str) -> Dict[str, Any]:
    """
    Retrieves a contact from the CRM system by ID.
    
    Args:
        contact_id: The HubSpot contact ID
        
    Returns:
        Contact details from CRM or empty dict if not found
    """
    try:
        # Initialize HubSpot client
        hubspot_client = HubSpotClient()
        
        # Get contact details
        contact = hubspot_client.get_contact(contact_id)
        
        logger.info(f"Retrieved contact from CRM: {contact_id}")
        
        return contact
    
    except Exception as e:
        logger.error(
            f"Failed to retrieve contact from CRM: {contact_id}",
            extra={"error": str(e), "contact_id": contact_id}
        )
        
        return {}


def get_crm_deal(deal_id: str) -> Dict[str, Any]:
    """
    Retrieves a deal from the CRM system by ID.
    
    Args:
        deal_id: The HubSpot deal ID
        
    Returns:
        Deal details from CRM or empty dict if not found
    """
    try:
        # Initialize HubSpot client
        hubspot_client = HubSpotClient()
        
        # Get deal details
        deal = hubspot_client.get_deal(deal_id)
        
        logger.info(f"Retrieved deal from CRM: {deal_id}")
        
        return deal
    
    except Exception as e:
        logger.error(
            f"Failed to retrieve deal from CRM: {deal_id}",
            extra={"error": str(e), "deal_id": deal_id}
        )
        
        return {}


def log_crm_activity(contact_id: str, activity_type: str, activity_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Logs an activity on a contact in the CRM system.
    
    Args:
        contact_id: The HubSpot contact ID
        activity_type: Type of activity (note, task, etc.)
        activity_data: Activity details
        
    Returns:
        Result of the activity logging operation
    """
    try:
        # Initialize HubSpot client
        hubspot_client = HubSpotClient()
        
        # Log activity
        result = hubspot_client.log_activity(contact_id, activity_type, activity_data)
        
        logger.info(
            f"Logged {activity_type} activity for contact in CRM: {contact_id}",
            extra={"contact_id": contact_id, "activity_type": activity_type}
        )
        
        return result
    
    except Exception as e:
        logger.error(
            f"Failed to log activity in CRM: {contact_id}",
            extra={
                "error": str(e),
                "contact_id": contact_id,
                "activity_type": activity_type
            }
        )
        
        return {
            "success": False,
            "error": f"Failed to log activity: {str(e)}"
        }


def prepare_file_upload_data(upload: FileUpload, processing_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Prepares file upload data for CRM integration.
    
    Args:
        upload: The file upload record
        processing_results: Results of file processing
        
    Returns:
        Prepared data for CRM update
    """
    # Extract user information
    user = upload.user
    user_info = {
        "email": user.email if user else None,
        "name": user.name if user else None,
        "company": user.company if user else None
    }
    
    # Extract file details
    file_info = {
        "filename": upload.filename,
        "file_type": upload.mime_type,
        "file_size": upload.size,
        "upload_date": upload.created_at.isoformat() if upload.created_at else None
    }
    
    # Extract processing results summary
    processing_summary = processing_results.get("summary", "")
    
    # Prepare CRM data
    crm_data = {
        "sample_file_name": upload.filename,
        "sample_file_size": f"{upload.size / 1024:.2f} KB",
        "sample_file_type": upload.mime_type,
        "sample_analysis_summary": processing_summary,
        "sample_upload_date": upload.created_at.isoformat() if upload.created_at else None,
        "sample_processed_date": upload.processed_at.isoformat() if upload.processed_at else None,
        "service_interest": upload.service_interest,
        "lead_source": "Website File Upload",
        "last_activity_date": datetime.datetime.utcnow().isoformat()
    }
    
    return crm_data


class CRMService:
    """
    Service class for CRM integration in the application.
    
    Provides methods for synchronizing form submissions, updating contacts with file upload
    information, and other CRM-related operations.
    """
    
    def __init__(self):
        """
        Initializes the CRM service with necessary dependencies.
        """
        self._logger = get_component_logger('crm_service')
        self._hubspot_client = None
        self._logger.info("CRM service initialized")
    
    def sync_form_submission(self, submission_id: uuid.UUID) -> Dict[str, Any]:
        """
        Synchronizes a form submission with the CRM system.
        
        Args:
            submission_id: UUID of the form submission to synchronize
            
        Returns:
            Dict with the result of the synchronization operation
        """
        return sync_form_submission_to_crm(submission_id)
    
    def update_contact_with_file_upload(self, upload_id: uuid.UUID, processing_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Updates a CRM contact record with file upload information.
        
        Args:
            upload_id: UUID of the file upload
            processing_results: Results of file processing
            
        Returns:
            Dict with the result of the CRM update operation
        """
        return update_contact_with_file_upload(upload_id, processing_results)
    
    def get_contact(self, contact_id: str) -> Dict[str, Any]:
        """
        Retrieves a contact from the CRM system by ID.
        
        Args:
            contact_id: The HubSpot contact ID
            
        Returns:
            Contact details from CRM
        """
        return get_crm_contact(contact_id)
    
    def get_deal(self, deal_id: str) -> Dict[str, Any]:
        """
        Retrieves a deal from the CRM system by ID.
        
        Args:
            deal_id: The HubSpot deal ID
            
        Returns:
            Deal details from CRM
        """
        return get_crm_deal(deal_id)
    
    def log_activity(self, contact_id: str, activity_type: str, activity_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Logs an activity on a contact in the CRM system.
        
        Args:
            contact_id: The HubSpot contact ID
            activity_type: Type of activity (note, task, etc.)
            activity_data: Activity details
            
        Returns:
            Result of the activity logging operation
        """
        return log_crm_activity(contact_id, activity_type, activity_data)
    
    def find_contact_by_email(self, email: str) -> Dict[str, Any]:
        """
        Finds a contact in the CRM system by email address.
        
        Args:
            email: The email address to search for
            
        Returns:
            Contact details if found, empty dict if not found
        """
        try:
            # Initialize HubSpot client if not already initialized
            if not self._hubspot_client:
                self._hubspot_client = HubSpotClient()
            
            # Search for contact by email
            contact = self._hubspot_client.find_contact_by_email(email)
            
            if contact:
                self._logger.info(
                    f"Found contact in CRM for email",
                    extra={"contact_id": contact.get('id')}
                )
            else:
                self._logger.info(f"No contact found in CRM for email")
            
            return contact or {}
        
        except Exception as e:
            self._logger.error(
                f"Failed to find contact by email in CRM",
                extra={"error": str(e)}
            )
            
            return {}
    
    def create_contact(self, contact_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Creates a new contact in the CRM system.
        
        Args:
            contact_data: Contact data to create
            
        Returns:
            Created contact details including ID
        """
        try:
            # Validate contact data
            is_valid, errors = validate_crm_data(contact_data)
            
            if not is_valid:
                self._logger.error(
                    f"Invalid contact data for CRM",
                    extra={"errors": errors}
                )
                
                return {
                    "success": False,
                    "error": "Invalid contact data",
                    "details": errors
                }
            
            # Initialize HubSpot client if not already initialized
            if not self._hubspot_client:
                self._hubspot_client = HubSpotClient()
            
            # Create contact
            contact = self._hubspot_client.create_contact(contact_data)
            
            self._logger.info(
                f"Created new contact in CRM",
                extra={"contact_id": contact.get('id')}
            )
            
            return contact
        
        except IntegrationException as e:
            self._logger.error(
                f"Failed to create contact in CRM due to integration error",
                extra={"error": str(e)}
            )
            
            return {
                "success": False,
                "error": str(e)
            }
        
        except Exception as e:
            self._logger.error(
                f"Failed to create contact in CRM due to unexpected error",
                extra={"error": str(e)}
            )
            
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }
    
    def update_contact(self, contact_id: str, contact_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Updates an existing contact in the CRM system.
        
        Args:
            contact_id: The HubSpot contact ID
            contact_data: Contact data to update
            
        Returns:
            Updated contact details
        """
        try:
            # Validate contact data
            is_valid, errors = validate_crm_data(contact_data)
            
            if not is_valid:
                self._logger.error(
                    f"Invalid contact data for CRM update",
                    extra={"errors": errors, "contact_id": contact_id}
                )
                
                return {
                    "success": False,
                    "error": "Invalid contact data",
                    "details": errors
                }
            
            # Initialize HubSpot client if not already initialized
            if not self._hubspot_client:
                self._hubspot_client = HubSpotClient()
            
            # Update contact
            contact = self._hubspot_client.update_contact(contact_id, contact_data)
            
            self._logger.info(
                f"Updated contact in CRM",
                extra={"contact_id": contact_id}
            )
            
            return contact
        
        except IntegrationException as e:
            self._logger.error(
                f"Failed to update contact in CRM due to integration error",
                extra={"error": str(e), "contact_id": contact_id}
            )
            
            return {
                "success": False,
                "error": str(e)
            }
        
        except Exception as e:
            self._logger.error(
                f"Failed to update contact in CRM due to unexpected error",
                extra={"error": str(e), "contact_id": contact_id}
            )
            
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }
    
    def create_deal(self, contact_id: str, deal_data: Dict[str, Any], form_type: FormType) -> Dict[str, Any]:
        """
        Creates a new deal in the CRM system associated with a contact.
        
        Args:
            contact_id: The HubSpot contact ID
            deal_data: Deal data to create
            form_type: The type of form submission
            
        Returns:
            Created deal details including ID
        """
        try:
            # Initialize HubSpot client if not already initialized
            if not self._hubspot_client:
                self._hubspot_client = HubSpotClient()
            
            # Create deal
            deal = self._hubspot_client.create_deal(contact_id, deal_data, form_type)
            
            self._logger.info(
                f"Created new deal in CRM",
                extra={"deal_id": deal.get('id'), "contact_id": contact_id}
            )
            
            return deal
        
        except IntegrationException as e:
            self._logger.error(
                f"Failed to create deal in CRM due to integration error",
                extra={"error": str(e), "contact_id": contact_id}
            )
            
            return {
                "success": False,
                "error": str(e)
            }
        
        except Exception as e:
            self._logger.error(
                f"Failed to create deal in CRM due to unexpected error",
                extra={"error": str(e), "contact_id": contact_id}
            )
            
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }