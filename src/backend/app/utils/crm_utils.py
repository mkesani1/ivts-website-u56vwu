"""
Utility module providing functions for CRM data mapping, validation, and transformation.

This module handles the conversion of form submission data to HubSpot CRM-compatible formats,
extracts contact identifiers, and prepares data for synchronization with the CRM system.
"""

import re
import datetime
from typing import Dict, List, Optional, Any, Tuple

# Third-party imports
import phonenumbers  # phonenumbers v8.13.0

# Internal imports
from ..core.config import settings
from ..utils.logging_utils import get_component_logger
from ..utils.validation_utils import sanitize_input
from ..api.v1.models.form_submission import FormType

# Initialize logger
logger = get_component_logger('crm_utils')

# Mapping of form field names to HubSpot CRM field names
CRM_FIELD_MAPPING = {
    'first_name': 'firstname',
    'last_name': 'lastname',
    'name': 'name',
    'email': 'email',
    'phone': 'phone',
    'company': 'company',
    'job_title': 'jobtitle',
    'project_details': 'project_description',
    'message': 'message',
    'preferred_date': 'preferred_demo_date',
    'preferred_time': 'preferred_demo_time',
    'time_zone': 'timezone',
    'budget_range': 'budget_range',
    'timeline': 'project_timeline',
    'referral_source': 'lead_source',
    'service_interests': 'service_interest'
}

# Mapping of form types to CRM types
FORM_TYPE_TO_CRM_TYPE = {
    'CONTACT': 'website_contact',
    'DEMO_REQUEST': 'demo_request',
    'QUOTE_REQUEST': 'quote_request'
}


def map_form_data_to_crm(form_data: Dict[str, Any], form_type: FormType) -> Dict[str, Any]:
    """
    Maps form submission data to HubSpot CRM field format.
    
    Args:
        form_data: Dictionary containing form submission data
        form_type: The type of form submitted (contact, demo request, etc.)
        
    Returns:
        Dictionary with data mapped to CRM field names
    """
    result = {}
    
    logger.info(f"Mapping form data to CRM fields for form type: {form_type.name}")
    
    # Process each field in the form data
    for field_name, field_value in form_data.items():
        if field_value is None or field_value == "":
            continue
            
        # Get the corresponding CRM field name
        crm_field = get_crm_field_name(field_name)
        
        # Apply field-specific transformations
        if field_name == 'phone':
            field_value = format_phone_for_crm(field_value, "US")
        elif field_name in ['first_name', 'last_name']:
            # Capitalize names
            if isinstance(field_value, str):
                field_value = field_value.capitalize()
        elif field_name == 'email':
            # Convert email to lowercase
            if isinstance(field_value, str):
                field_value = field_value.lower()
        elif field_name == 'service_interests':
            # Handle list of service interests
            if isinstance(field_value, list):
                field_value = ';'.join(field_value)
            
        # Sanitize and add to result
        if isinstance(field_value, str):
            result[crm_field] = sanitize_input(field_value)
        else:
            result[crm_field] = field_value
    
    # Add form type as a source field
    if form_type.name in FORM_TYPE_TO_CRM_TYPE:
        result['form_type'] = FORM_TYPE_TO_CRM_TYPE[form_type.name]
    
    # Add creation timestamp
    result['create_date'] = datetime.datetime.utcnow().isoformat()
    
    logger.info(f"Completed mapping form data to CRM fields, mapped {len(result)} fields")
    
    return result


def extract_contact_identifier(form_data: Dict[str, Any]) -> Optional[str]:
    """
    Extracts the primary identifier (email) for CRM contact lookup.
    
    Args:
        form_data: Dictionary containing form submission data
        
    Returns:
        Email address for contact identification or None if not found
    """
    # Email is the primary identifier
    if 'email' in form_data and form_data['email']:
        return form_data['email'].lower()
    
    # Log warning if email is missing but other identifiers exist
    if 'name' in form_data and 'company' in form_data:
        logger.warning(
            "Email missing in form data, using name and company for identification may be less reliable",
            extra={"name": form_data.get('name'), "company": form_data.get('company')}
        )
    
    # No suitable identifier found
    logger.error("No suitable contact identifier found in form data")
    return None


def prepare_contact_properties(contact_data: Dict[str, Any]) -> Dict[str, List[Dict[str, str]]]:
    """
    Prepares contact properties in the format required by HubSpot API.
    
    Args:
        contact_data: Dictionary containing contact data
        
    Returns:
        Dictionary with properties formatted for HubSpot API
    """
    properties = []
    
    for field_name, field_value in contact_data.items():
        # Skip None or empty values
        if field_value is None or field_value == "":
            continue
            
        # Handle special case for service interests (convert list to string)
        if field_name == 'service_interest' and isinstance(field_value, list):
            field_value = ';'.join(field_value)
            
        # Convert value to string (HubSpot requires string values)
        if not isinstance(field_value, str):
            field_value = str(field_value)
            
        # Add property to the list
        properties.append({
            "property": field_name,
            "value": field_value
        })
    
    return {"properties": properties}


def format_phone_for_crm(phone_number: str, region: str = "US") -> str:
    """
    Formats a phone number to E.164 format for CRM standardization.
    
    Args:
        phone_number: The phone number to format
        region: The region code for the phone number (default: US)
        
    Returns:
        Formatted phone number or original if formatting fails
    """
    if not phone_number:
        return ""
        
    try:
        parsed_number = phonenumbers.parse(phone_number, region)
        if phonenumbers.is_valid_number(parsed_number):
            formatted_number = phonenumbers.format_number(
                parsed_number, phonenumbers.PhoneNumberFormat.E164
            )
            return formatted_number
    except Exception as e:
        logger.warning(
            f"Failed to format phone number: {phone_number}",
            extra={"error": str(e), "region": region}
        )
    
    # Return original if formatting fails
    return phone_number


def validate_crm_data(data: Dict[str, Any]) -> Tuple[bool, Dict[str, str]]:
    """
    Validates data before submission to CRM system.
    
    Args:
        data: Dictionary containing data to validate
        
    Returns:
        Tuple of (success, errors) where success is a boolean and
        errors is a dictionary of field-specific error messages
    """
    errors = {}
    
    # Check required fields based on context
    if 'email' not in data or not data['email']:
        errors['email'] = "Email is required for CRM contact creation"
    
    # Validate email format if present
    if 'email' in data and data['email']:
        email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        if not email_pattern.match(data['email']):
            errors['email'] = "Invalid email format"
    
    # Validate field lengths against CRM constraints
    for field, value in data.items():
        if isinstance(value, str):
            if field in ['firstname', 'lastname'] and len(value) > 50:
                errors[field] = f"{field} must be 50 characters or less"
            elif field == 'company' and len(value) > 100:
                errors[field] = "Company name must be 100 characters or less"
            elif field == 'project_description' and len(value) > 5000:
                errors[field] = "Project description must be 5000 characters or less"
    
    # If no errors, return success
    if not errors:
        return True, {}
    
    # Log validation failures
    logger.warning(
        "CRM data validation failed",
        extra={"errors": errors}
    )
    
    return False, errors


def get_crm_field_name(form_field_name: str) -> str:
    """
    Gets the CRM field name for a given form field name.
    
    Args:
        form_field_name: The field name from the form
        
    Returns:
        CRM field name or original if not mapped
    """
    if form_field_name in CRM_FIELD_MAPPING:
        return CRM_FIELD_MAPPING[form_field_name]
    
    # Log warning if field is not mapped
    logger.warning(
        f"No CRM field mapping found for form field: {form_field_name}",
        extra={"field": form_field_name}
    )
    
    # Return original if no mapping exists
    return form_field_name


def prepare_deal_properties(deal_data: Dict[str, Any], form_type: FormType) -> Dict[str, List[Dict[str, str]]]:
    """
    Prepares deal properties in the format required by HubSpot API.
    
    Args:
        deal_data: Dictionary containing deal data
        form_type: The type of form submitted
        
    Returns:
        Dictionary with properties formatted for HubSpot API
    """
    properties = []
    
    # Set deal name based on company name and form type
    company_name = deal_data.get('company', 'Unknown Company')
    deal_name = f"{company_name} - {form_type.name.replace('_', ' ').title()}"
    properties.append({
        "property": "dealname",
        "value": deal_name
    })
    
    # Set deal stage based on form type
    if form_type == FormType.DEMO_REQUEST:
        properties.append({
            "property": "dealstage",
            "value": "presentationscheduled"  # HubSpot demo scheduled stage
        })
    elif form_type == FormType.QUOTE_REQUEST:
        properties.append({
            "property": "dealstage",
            "value": "qualifiedtobuy"  # HubSpot qualified stage
        })
    else:
        properties.append({
            "property": "dealstage",
            "value": "appointmentscheduled"  # HubSpot initial stage
        })
    
    # Set deal amount if budget range is provided
    if 'budget_range' in deal_data:
        # Extract numeric value from budget range (e.g., "$5,000-$10,000" -> 7500)
        budget_range = deal_data['budget_range']
        if isinstance(budget_range, str) and '-' in budget_range:
            try:
                # Extract numbers from string and get average
                numbers = re.findall(r'\d+', budget_range)
                if len(numbers) >= 2:
                    amount = (int(numbers[0]) + int(numbers[1])) / 2
                    properties.append({
                        "property": "amount",
                        "value": str(amount)
                    })
            except Exception as e:
                logger.warning(
                    f"Failed to parse budget range: {budget_range}",
                    extra={"error": str(e)}
                )
    
    # Set pipeline and deal type
    properties.append({
        "property": "pipeline",
        "value": "default"
    })
    
    properties.append({
        "property": "deal_type",
        "value": form_type.name.lower()
    })
    
    return {"properties": properties}


def prepare_activity_properties(activity_type: str, activity_data: Dict[str, Any]) -> Dict[str, List[Dict[str, str]]]:
    """
    Prepares activity properties in the format required by HubSpot API.
    
    Args:
        activity_type: The type of activity (e.g., "note", "email", "task")
        activity_data: Dictionary containing activity data
        
    Returns:
        Dictionary with properties formatted for HubSpot API
    """
    properties = []
    
    # Set activity title based on activity type
    if activity_type == "note":
        title = "Website Form Submission Note"
    elif activity_type == "email":
        title = "Website Form Submission Email"
    elif activity_type == "task":
        title = "Website Form Submission Follow-up"
    else:
        title = f"Website Form Submission {activity_type.title()}"
    
    properties.append({
        "property": "hs_note_title",
        "value": title
    })
    
    properties.append({
        "property": "hs_note_body",
        "value": f"Form submission from website: {activity_data.get('message', '')}"
    })
    
    properties.append({
        "property": "hs_timestamp",
        "value": str(int(datetime.datetime.utcnow().timestamp() * 1000))  # HubSpot uses milliseconds
    })
    
    return {"properties": properties}