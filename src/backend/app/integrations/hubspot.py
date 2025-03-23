"""
Integration module for HubSpot CRM.

This module provides a client for interacting with the HubSpot API, handling
contact management, deal creation, activity logging, and form submission processing.
It implements error handling, rate limiting, and retry mechanisms to ensure
reliable integration with the HubSpot CRM system.
"""

import requests  # requests v2.31.0
import json
import time
import typing
from typing import Dict, List, Optional, Any, Union
import urllib.parse
import tenacity  # tenacity v8.2.0
import circuitbreaker  # circuitbreaker v1.4.0

from ..core.config import settings
from ..core.exceptions import IntegrationException
from ..utils.logging_utils import get_component_logger, log_exception, mask_sensitive_data
from ..utils.crm_utils import (
    map_form_data_to_crm,
    prepare_contact_properties,
    prepare_deal_properties,
    prepare_activity_properties
)
from ..api.v1.models.form_submission import FormType

# Initialize logger
logger = get_component_logger('hubspot')

# Constants
HUBSPOT_API_BASE_URL = 'https://api.hubapi.com'
HUBSPOT_RATE_LIMIT_PAUSE = 10  # seconds
HUBSPOT_MAX_RETRIES = 3


class HubSpotClient:
    """
    Client for interacting with the HubSpot API with error handling, rate limiting,
    and circuit breaker patterns.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initializes the HubSpot client with API key from settings.
        
        Args:
            api_key: HubSpot API key (optional, will use settings if not provided)
        
        Raises:
            IntegrationException: If API key is not provided and not in settings
        """
        self.api_key = api_key or settings.HUBSPOT_API_KEY
        self.base_url = HUBSPOT_API_BASE_URL
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        self._logger = logger
        
        # Validate API key
        if not self.api_key:
            raise IntegrationException(
                "HubSpot API key not configured. Please set HUBSPOT_API_KEY in settings.",
                status_code=500
            )
    
    @circuitbreaker.circuit(
        failure_threshold=5,
        recovery_timeout=60,
        expected_exception=IntegrationException
    )
    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        params: Optional[Dict[str, Any]] = None, 
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Makes an HTTP request to the HubSpot API with error handling.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint to call
            params: URL parameters for the request
            data: JSON body data for the request
            
        Returns:
            JSON response from the API
            
        Raises:
            IntegrationException: If the API call fails
        """
        url = f"{self.base_url}{endpoint}"
        
        # Log request (mask sensitive data)
        masked_data = mask_sensitive_data(data) if data else None
        masked_params = mask_sensitive_data(params) if params else None
        self._logger.info(
            f"Making HubSpot API request: {method} {endpoint}",
            extra={
                "params": masked_params,
                "data": masked_data
            }
        )
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                params=params,
                json=data
            )
            
            # Handle rate limiting
            if response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', HUBSPOT_RATE_LIMIT_PAUSE))
                self.handle_rate_limit(retry_after)
                # Retry the request
                return self._make_request(method, endpoint, params, data)
            
            # Log response status
            self._logger.info(
                f"HubSpot API response: {response.status_code}",
                extra={"status_code": response.status_code}
            )
            
            # Check for successful response
            if 200 <= response.status_code < 300:
                # Parse and return JSON response
                if response.content:
                    return response.json()
                return {}
            
            # Handle error responses
            error_data = {}
            try:
                error_data = response.json()
            except json.JSONDecodeError:
                error_data = {"message": response.text}
            
            # Log error
            self._logger.error(
                f"HubSpot API error: {response.status_code}",
                extra={
                    "status_code": response.status_code,
                    "error_data": error_data
                }
            )
            
            # Handle different error types
            if response.status_code == 401:
                raise IntegrationException(
                    "Authentication error with HubSpot API. Please check API key.",
                    status_code=401,
                    details=error_data
                )
            elif response.status_code == 400:
                raise IntegrationException(
                    "Invalid request to HubSpot API.",
                    status_code=400,
                    details=error_data
                )
            elif response.status_code >= 500:
                raise IntegrationException(
                    "HubSpot API server error.",
                    status_code=502,
                    details=error_data
                )
            else:
                raise IntegrationException(
                    f"HubSpot API error: {response.status_code}",
                    status_code=response.status_code,
                    details=error_data
                )
        
        except requests.RequestException as e:
            # Handle request exceptions (connection errors, timeouts, etc.)
            self._logger.error(
                f"HubSpot API request failed: {str(e)}",
                extra={"error": str(e), "error_type": type(e).__name__}
            )
            raise IntegrationException(
                f"Failed to connect to HubSpot API: {str(e)}",
                status_code=503
            )
    
    def find_contact_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Searches for a contact in HubSpot by email address.
        
        Args:
            email: Email address to search for
            
        Returns:
            Contact details if found, None if not found
            
        Raises:
            IntegrationException: If the search operation fails
        """
        self._logger.info(f"Searching for contact by email", extra={"email": mask_sensitive_data(email)})
        
        try:
            # Use the contacts/search endpoint to find contacts by email
            params = {
                "filterGroups": [{
                    "filters": [{
                        "propertyName": "email",
                        "operator": "EQ",
                        "value": email
                    }]
                }]
            }
            
            response = self._make_request(
                method="POST",
                endpoint="/crm/v3/objects/contacts/search",
                data=params
            )
            
            # Check if any contacts were found
            if response and response.get('results') and len(response['results']) > 0:
                self._logger.info(f"Contact found for email", extra={"contact_id": response['results'][0]['id']})
                return response['results'][0]
            
            self._logger.info(f"No contact found for email")
            return None
        
        except IntegrationException:
            # Re-raise IntegrationException
            raise
        except Exception as e:
            # Log and wrap other exceptions
            self._logger.error(
                f"Error searching for contact by email: {str(e)}",
                extra={"error": str(e), "error_type": type(e).__name__}
            )
            raise IntegrationException(
                f"Failed to search for contact in HubSpot: {str(e)}",
                status_code=500
            )
    
    def create_contact(self, contact_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Creates a new contact in HubSpot.
        
        Args:
            contact_data: Contact data to create
            
        Returns:
            Created contact details including ID
            
        Raises:
            IntegrationException: If contact creation fails
        """
        self._logger.info(
            f"Creating new contact in HubSpot",
            extra={"contact_data": mask_sensitive_data(contact_data)}
        )
        
        try:
            # Prepare contact properties
            properties = prepare_contact_properties(contact_data)
            
            # Create contact
            response = self._make_request(
                method="POST",
                endpoint="/crm/v3/objects/contacts",
                data=properties
            )
            
            self._logger.info(
                f"Contact created successfully in HubSpot",
                extra={"contact_id": response.get('id')}
            )
            
            return response
        
        except IntegrationException:
            # Re-raise IntegrationException
            raise
        except Exception as e:
            # Log and wrap other exceptions
            self._logger.error(
                f"Error creating contact in HubSpot: {str(e)}",
                extra={"error": str(e), "error_type": type(e).__name__}
            )
            raise IntegrationException(
                f"Failed to create contact in HubSpot: {str(e)}",
                status_code=500
            )
    
    def update_contact(self, contact_id: str, contact_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Updates an existing contact in HubSpot.
        
        Args:
            contact_id: HubSpot contact ID to update
            contact_data: Contact data to update
            
        Returns:
            Updated contact details
            
        Raises:
            IntegrationException: If contact update fails
        """
        self._logger.info(
            f"Updating contact in HubSpot",
            extra={
                "contact_id": contact_id,
                "contact_data": mask_sensitive_data(contact_data)
            }
        )
        
        try:
            # Prepare contact properties
            properties = prepare_contact_properties(contact_data)
            
            # Update contact
            response = self._make_request(
                method="PATCH",
                endpoint=f"/crm/v3/objects/contacts/{contact_id}",
                data=properties
            )
            
            self._logger.info(
                f"Contact updated successfully in HubSpot",
                extra={"contact_id": contact_id}
            )
            
            return response
        
        except IntegrationException:
            # Re-raise IntegrationException
            raise
        except Exception as e:
            # Log and wrap other exceptions
            self._logger.error(
                f"Error updating contact in HubSpot: {str(e)}",
                extra={"error": str(e), "error_type": type(e).__name__}
            )
            raise IntegrationException(
                f"Failed to update contact in HubSpot: {str(e)}",
                status_code=500
            )
    
    def create_deal(self, contact_id: str, deal_data: Dict[str, Any], form_type: FormType) -> Dict[str, Any]:
        """
        Creates a new deal in HubSpot associated with a contact.
        
        Args:
            contact_id: HubSpot contact ID to associate with the deal
            deal_data: Deal data to create
            form_type: Type of form submission that triggered deal creation
            
        Returns:
            Created deal details including ID
            
        Raises:
            IntegrationException: If deal creation fails
        """
        self._logger.info(
            f"Creating new deal in HubSpot",
            extra={
                "contact_id": contact_id,
                "deal_data": mask_sensitive_data(deal_data),
                "form_type": form_type.name
            }
        )
        
        try:
            # Prepare deal properties
            properties = prepare_deal_properties(deal_data, form_type)
            
            # Create deal
            response = self._make_request(
                method="POST",
                endpoint="/crm/v3/objects/deals",
                data=properties
            )
            
            deal_id = response.get('id')
            
            # Associate deal with contact
            self.associate_deal_with_contact(deal_id, contact_id)
            
            self._logger.info(
                f"Deal created successfully in HubSpot",
                extra={"deal_id": deal_id, "contact_id": contact_id}
            )
            
            return response
        
        except IntegrationException:
            # Re-raise IntegrationException
            raise
        except Exception as e:
            # Log and wrap other exceptions
            self._logger.error(
                f"Error creating deal in HubSpot: {str(e)}",
                extra={"error": str(e), "error_type": type(e).__name__}
            )
            raise IntegrationException(
                f"Failed to create deal in HubSpot: {str(e)}",
                status_code=500
            )
    
    def associate_deal_with_contact(self, deal_id: str, contact_id: str) -> bool:
        """
        Associates a deal with a contact in HubSpot.
        
        Args:
            deal_id: HubSpot deal ID
            contact_id: HubSpot contact ID
            
        Returns:
            True if association successful, False otherwise
        """
        self._logger.info(
            f"Associating deal with contact in HubSpot",
            extra={"deal_id": deal_id, "contact_id": contact_id}
        )
        
        try:
            # Create association
            self._make_request(
                method="PUT",
                endpoint=f"/crm/v3/objects/deals/{deal_id}/associations/contacts/{contact_id}/deal_to_contact"
            )
            
            self._logger.info(
                f"Deal associated with contact successfully in HubSpot",
                extra={"deal_id": deal_id, "contact_id": contact_id}
            )
            
            return True
        
        except Exception as e:
            # Log error but don't fail the entire operation
            self._logger.error(
                f"Error associating deal with contact in HubSpot: {str(e)}",
                extra={
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "deal_id": deal_id,
                    "contact_id": contact_id
                }
            )
            return False
    
    def log_activity(self, contact_id: str, activity_type: str, activity_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Logs an activity on a contact in HubSpot.
        
        Args:
            contact_id: HubSpot contact ID
            activity_type: Type of activity to log (note, task, etc.)
            activity_data: Activity data to log
            
        Returns:
            Created activity details
            
        Raises:
            IntegrationException: If activity logging fails
        """
        self._logger.info(
            f"Logging activity in HubSpot",
            extra={
                "contact_id": contact_id,
                "activity_type": activity_type,
                "activity_data": mask_sensitive_data(activity_data)
            }
        )
        
        try:
            # Prepare activity properties
            properties = prepare_activity_properties(activity_type, activity_data)
            
            # Add engagement with contact
            engagement_data = {
                "engagement": {
                    "type": activity_type
                },
                "associations": {
                    "contactIds": [contact_id]
                },
                "metadata": properties
            }
            
            # Create engagement
            response = self._make_request(
                method="POST",
                endpoint="/engagements/v1/engagements",
                data=engagement_data
            )
            
            self._logger.info(
                f"Activity logged successfully in HubSpot",
                extra={"contact_id": contact_id, "activity_id": response.get('id')}
            )
            
            return response
        
        except IntegrationException:
            # Re-raise IntegrationException
            raise
        except Exception as e:
            # Log and wrap other exceptions
            self._logger.error(
                f"Error logging activity in HubSpot: {str(e)}",
                extra={"error": str(e), "error_type": type(e).__name__}
            )
            raise IntegrationException(
                f"Failed to log activity in HubSpot: {str(e)}",
                status_code=500
            )
    
    def get_contact(self, contact_id: str) -> Dict[str, Any]:
        """
        Retrieves a contact by ID from HubSpot.
        
        Args:
            contact_id: HubSpot contact ID
            
        Returns:
            Contact details
            
        Raises:
            IntegrationException: If contact retrieval fails
        """
        self._logger.info(f"Retrieving contact from HubSpot", extra={"contact_id": contact_id})
        
        try:
            response = self._make_request(
                method="GET",
                endpoint=f"/crm/v3/objects/contacts/{contact_id}"
            )
            
            self._logger.info(f"Contact retrieved successfully from HubSpot", extra={"contact_id": contact_id})
            
            return response
        
        except IntegrationException:
            # Re-raise IntegrationException
            raise
        except Exception as e:
            # Log and wrap other exceptions
            self._logger.error(
                f"Error retrieving contact from HubSpot: {str(e)}",
                extra={"error": str(e), "error_type": type(e).__name__}
            )
            raise IntegrationException(
                f"Failed to retrieve contact from HubSpot: {str(e)}",
                status_code=500
            )
    
    def get_deal(self, deal_id: str) -> Dict[str, Any]:
        """
        Retrieves a deal by ID from HubSpot.
        
        Args:
            deal_id: HubSpot deal ID
            
        Returns:
            Deal details
            
        Raises:
            IntegrationException: If deal retrieval fails
        """
        self._logger.info(f"Retrieving deal from HubSpot", extra={"deal_id": deal_id})
        
        try:
            response = self._make_request(
                method="GET",
                endpoint=f"/crm/v3/objects/deals/{deal_id}"
            )
            
            self._logger.info(f"Deal retrieved successfully from HubSpot", extra={"deal_id": deal_id})
            
            return response
        
        except IntegrationException:
            # Re-raise IntegrationException
            raise
        except Exception as e:
            # Log and wrap other exceptions
            self._logger.error(
                f"Error retrieving deal from HubSpot: {str(e)}",
                extra={"error": str(e), "error_type": type(e).__name__}
            )
            raise IntegrationException(
                f"Failed to retrieve deal from HubSpot: {str(e)}",
                status_code=500
            )
    
    def handle_rate_limit(self, retry_after: int = None) -> None:
        """
        Handles rate limiting by pausing execution.
        
        Args:
            retry_after: Number of seconds to wait before retrying
        """
        pause_time = retry_after or HUBSPOT_RATE_LIMIT_PAUSE
        
        self._logger.warning(
            f"HubSpot API rate limit encountered. Pausing for {pause_time} seconds",
            extra={"retry_after": pause_time}
        )
        
        time.sleep(pause_time)
        
        self._logger.info("Resuming HubSpot API operations after rate limit pause")


@tenacity.retry(
    stop=tenacity.stop_after_attempt(3),
    wait=tenacity.wait_exponential(multiplier=1, min=2, max=10),
    retry=tenacity.retry_if_exception_type(IntegrationException),
    reraise=True
)
def process_form_submission(form_data: Dict[str, Any], form_type: FormType) -> Dict[str, Any]:
    """
    Processes a form submission by creating or updating a contact and associated records in HubSpot.
    
    Args:
        form_data: The submitted form data
        form_type: The type of form submission
        
    Returns:
        Result of the form processing operation including CRM IDs
        
    Raises:
        IntegrationException: If the form processing fails
    """
    # Log the form processing start (mask sensitive data)
    logger.info(
        f"Processing form submission for HubSpot CRM",
        extra={
            "form_type": form_type.name,
            "form_data": mask_sensitive_data(form_data)
        }
    )
    
    try:
        # Create HubSpot client
        hubspot_client = HubSpotClient()
        
        # Map form data to CRM format
        crm_data = map_form_data_to_crm(form_data, form_type)
        
        # Extract email for contact lookup
        email = form_data.get('email')
        if not email:
            raise IntegrationException(
                "Email is required for CRM integration",
                status_code=400
            )
        
        # Check if contact exists
        existing_contact = hubspot_client.find_contact_by_email(email)
        
        # Create or update contact
        if existing_contact:
            contact_id = existing_contact['id']
            logger.info(f"Updating existing contact in HubSpot", extra={"contact_id": contact_id})
            contact = hubspot_client.update_contact(contact_id, crm_data)
        else:
            logger.info(f"Creating new contact in HubSpot")
            contact = hubspot_client.create_contact(crm_data)
            contact_id = contact['id']
        
        # Create deal associated with contact
        deal = hubspot_client.create_deal(contact_id, crm_data, form_type)
        deal_id = deal['id']
        
        # Log activity for form submission
        activity_data = {
            "message": f"Form submission of type {form_type.name}",
            "form_data": form_data
        }
        hubspot_client.log_activity(contact_id, "note", activity_data)
        
        # Return success result
        result = {
            "success": True,
            "contact_id": contact_id,
            "deal_id": deal_id,
            "form_type": form_type.name
        }
        
        logger.info(
            f"Successfully processed form submission in HubSpot",
            extra=result
        )
        
        return result
    
    except IntegrationException as e:
        # Log and re-raise the exception
        logger.error(
            f"Error processing form submission in HubSpot: {str(e)}",
            extra={
                "error": str(e),
                "error_type": "IntegrationException",
                "form_type": form_type.name,
                "details": getattr(e, 'details', {})
            }
        )
        raise
    
    except Exception as e:
        # Log and wrap other exceptions
        logger.error(
            f"Unexpected error processing form submission in HubSpot: {str(e)}",
            extra={
                "error": str(e),
                "error_type": type(e).__name__,
                "form_type": form_type.name
            }
        )
        raise IntegrationException(
            f"Failed to process form submission in HubSpot: {str(e)}",
            status_code=500
        )