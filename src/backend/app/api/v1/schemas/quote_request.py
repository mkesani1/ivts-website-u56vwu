from datetime import datetime  # For potential future date/time handling
from enum import Enum
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator  # pydantic v1.10.0


class ServiceInterestEnum(str, Enum):
    """Enum defining valid service interest options for quote requests."""
    DATA_COLLECTION = "data_collection"
    DATA_PREPARATION = "data_preparation"
    AI_MODEL_DEVELOPMENT = "ai_model_development"
    HUMAN_IN_THE_LOOP = "human_in_the_loop"
    SOCIAL_IMPACT = "social_impact"


class BudgetRangeEnum(str, Enum):
    """Enum defining valid budget range options for quote requests."""
    UNDER_10K = "under_10k"
    BETWEEN_10K_50K = "between_10k_50k"
    BETWEEN_50K_100K = "between_50k_100k"
    BETWEEN_100K_500K = "between_100k_500k"
    OVER_500K = "over_500k"
    NOT_SPECIFIED = "not_specified"


class ProjectTimelineEnum(str, Enum):
    """Enum defining valid project timeline options for quote requests."""
    IMMEDIATELY = "immediately"
    WITHIN_1_MONTH = "within_1_month"
    WITHIN_3_MONTHS = "within_3_months"
    WITHIN_6_MONTHS = "within_6_months"
    FUTURE_PLANNING = "future_planning"


class QuoteRequestSchema(BaseModel):
    """
    Pydantic schema for validating quote request form submissions.
    
    This schema ensures all required fields are present and validates 
    data formats before processing the quote request.
    """
    first_name: str = Field(..., min_length=1, max_length=100, description="First name of the requester")
    last_name: str = Field(..., min_length=1, max_length=100, description="Last name of the requester")
    email: str = Field(..., description="Valid email address for contact")
    phone: str = Field(..., min_length=5, max_length=20, description="Phone number including country code")
    company: str = Field(..., min_length=1, max_length=200, description="Company or organization name")
    job_title: Optional[str] = Field(None, max_length=100, description="Job title or role of the requester")
    
    service_interests: List[ServiceInterestEnum] = Field(
        ..., 
        min_items=1, 
        description="List of services the requester is interested in"
    )
    
    project_description: str = Field(
        ..., 
        min_length=10, 
        max_length=2000, 
        description="Detailed description of the project or requirements"
    )
    
    project_timeline: ProjectTimelineEnum = Field(
        ..., 
        description="Expected timeline for project implementation"
    )
    
    budget_range: BudgetRangeEnum = Field(
        ..., 
        description="Expected budget range for the project"
    )
    
    referral_source: Optional[str] = Field(
        None, 
        max_length=200, 
        description="How the requester heard about IndiVillage"
    )
    
    marketing_consent: bool = Field(
        False, 
        description="Whether the user consents to receiving marketing communications"
    )
    
    captcha_token: str = Field(
        ..., 
        description="reCAPTCHA token for form submission validation"
    )
    
    @validator('email')
    def validate_email(cls, v):
        """
        Validate email format using a simple regex.
        For production, consider using a more comprehensive validation approach.
        """
        import re
        pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(pattern, v):
            raise ValueError('Invalid email format')
        return v
    
    @validator('phone')
    def validate_phone(cls, v):
        """
        Validate that phone number contains only digits, spaces, and common phone characters.
        """
        import re
        if not re.match(r'^[0-9\s\+\-\(\)\.]+$', v):
            raise ValueError('Phone number can only contain digits, spaces, and characters: + - ( ) .')
        return v
    
    class Config:
        """Configuration class for the QuoteRequestSchema."""
        schema_extra = {
            "example": {
                "first_name": "Jane",
                "last_name": "Doe",
                "email": "jane.doe@example.com",
                "phone": "+1 (555) 123-4567",
                "company": "Example Corp",
                "job_title": "CTO",
                "service_interests": ["data_preparation", "ai_model_development"],
                "project_description": "We need assistance with data labeling for our machine learning project.",
                "project_timeline": "within_3_months",
                "budget_range": "between_50k_100k",
                "referral_source": "Google Search",
                "marketing_consent": True,
                "captcha_token": "valid-recaptcha-token"
            }
        }


class QuoteRequestResponseSchema(BaseModel):
    """
    Pydantic schema for quote request form submission responses.
    
    Used to provide structured success responses with a submission ID for reference.
    """
    success: bool = Field(True, description="Indicates successful form submission")
    message: str = Field("Quote request submitted successfully", description="Success message")
    submission_id: UUID = Field(..., description="Unique identifier for the submitted request")

    class Config:
        """Configuration class for the QuoteRequestResponseSchema."""
        schema_extra = {
            "example": {
                "success": True,
                "message": "Quote request submitted successfully",
                "submission_id": "123e4567-e89b-12d3-a456-426614174000"
            }
        }


class QuoteRequestErrorSchema(BaseModel):
    """
    Pydantic schema for quote request form submission error responses.
    
    Used to provide structured error responses with detailed validation errors.
    """
    success: bool = Field(False, description="Indicates failed form submission")
    message: str = Field("Error submitting quote request", description="Error message")
    errors: Dict[str, List[str]] = Field({}, description="Detailed validation errors by field")

    class Config:
        """Configuration class for the QuoteRequestErrorSchema."""
        schema_extra = {
            "example": {
                "success": False,
                "message": "Error submitting quote request",
                "errors": {
                    "email": ["Invalid email format"],
                    "service_interests": ["At least one service interest must be selected"]
                }
            }
        }