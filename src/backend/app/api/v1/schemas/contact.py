from pydantic import BaseModel
from typing import Dict
import uuid

class ContactSchema(BaseModel):
    """
    Pydantic schema for validating contact form submissions.
    
    This schema defines the structure and validation rules for incoming
    contact form data, ensuring all required fields are present and 
    properly formatted before processing.
    """
    name: str
    email: str
    company: str
    phone: str
    message: str
    captcha_token: str
    
    class Config:
        """Configuration class for the ContactSchema."""
        pass


class ContactResponseSchema(BaseModel):
    """
    Pydantic schema for contact form submission responses.
    
    This schema defines the structure of successful response data sent back
    to the client after a contact form has been successfully processed.
    """
    success: bool
    message: str
    submission_id: uuid.UUID
    
    class Config:
        """Configuration class for the ContactResponseSchema."""
        pass


class ContactErrorSchema(BaseModel):
    """
    Pydantic schema for contact form submission error responses.
    
    This schema defines the structure of error response data sent back
    to the client when contact form validation or processing fails.
    """
    success: bool
    message: str
    errors: Dict
    
    class Config:
        """Configuration class for the ContactErrorSchema."""
        pass