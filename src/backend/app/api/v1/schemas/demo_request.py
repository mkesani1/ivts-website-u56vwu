"""
Schema definitions for demo request form submissions.
This module provides Pydantic models for validating and structuring
the demo request form data in the IndiVillage.com application.
"""
from enum import Enum
from typing import List, Dict, Optional
import uuid
from datetime import datetime

from pydantic import BaseModel, Field, validator  # pydantic v1.10.0

class ServiceInterestEnum(str, Enum):
    """Enum defining valid service interest options for demo requests"""
    DATA_COLLECTION = "data_collection"
    DATA_PREPARATION = "data_preparation"
    AI_MODEL_DEVELOPMENT = "ai_model_development"
    HUMAN_IN_THE_LOOP = "human_in_the_loop"
    SOCIAL_IMPACT = "social_impact"

class TimeZoneEnum(str, Enum):
    """Enum defining valid time zone options for demo scheduling"""
    UTC_MINUS_12 = "UTC-12:00"
    UTC_MINUS_11 = "UTC-11:00"
    UTC_MINUS_10 = "UTC-10:00"
    UTC_MINUS_9 = "UTC-09:00"
    UTC_MINUS_8 = "UTC-08:00"
    UTC_MINUS_7 = "UTC-07:00"
    UTC_MINUS_6 = "UTC-06:00"
    UTC_MINUS_5 = "UTC-05:00"
    UTC_MINUS_4 = "UTC-04:00"
    UTC_MINUS_3 = "UTC-03:00"
    UTC_MINUS_2 = "UTC-02:00"
    UTC_MINUS_1 = "UTC-01:00"
    UTC = "UTC+00:00"
    UTC_PLUS_1 = "UTC+01:00"
    UTC_PLUS_2 = "UTC+02:00"
    UTC_PLUS_3 = "UTC+03:00"
    UTC_PLUS_4 = "UTC+04:00"
    UTC_PLUS_5 = "UTC+05:00"
    UTC_PLUS_6 = "UTC+06:00"
    UTC_PLUS_7 = "UTC+07:00"
    UTC_PLUS_8 = "UTC+08:00"
    UTC_PLUS_9 = "UTC+09:00"
    UTC_PLUS_10 = "UTC+10:00"
    UTC_PLUS_11 = "UTC+11:00"
    UTC_PLUS_12 = "UTC+12:00"

class DemoRequestSchema(BaseModel):
    """Pydantic schema for validating demo request form submissions"""
    # Contact Information
    first_name: str = Field(..., min_length=1, max_length=50, description="First name of the requestor")
    last_name: str = Field(..., min_length=1, max_length=50, description="Last name of the requestor")
    email: str = Field(..., description="Email address of the requestor")
    phone: str = Field(..., min_length=7, max_length=20, description="Phone number of the requestor")
    company: str = Field(..., min_length=1, max_length=100, description="Company name of the requestor")
    job_title: str = Field(..., min_length=1, max_length=100, description="Job title of the requestor")
    
    # Demo Preferences
    service_interests: List[ServiceInterestEnum] = Field(
        ..., 
        min_items=1, 
        description="List of services the requestor is interested in"
    )
    preferred_date: str = Field(..., description="Preferred date for the demo in YYYY-MM-DD format")
    preferred_time: str = Field(..., description="Preferred time for the demo in HH:MM format")
    time_zone: TimeZoneEnum = Field(..., description="Time zone for the demo")
    
    # Additional Information
    project_details: str = Field(
        "", 
        max_length=2000,
        description="Details about the requestor's project or requirements"
    )
    referral_source: str = Field(
        "", 
        max_length=100,
        description="How the requestor heard about IndiVillage"
    )
    
    # Consent and Security
    marketing_consent: bool = Field(
        False,
        description="Whether the requestor consents to receiving marketing communications"
    )
    captcha_token: str = Field(..., description="CAPTCHA verification token")
    
    class Config:
        """Configuration class for the DemoRequestSchema"""
        schema_extra = {
            "example": {
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@example.com",
                "phone": "+1 (555) 123-4567",
                "company": "Example Corp",
                "job_title": "CTO",
                "service_interests": ["data_preparation", "ai_model_development"],
                "preferred_date": "2023-12-15",
                "preferred_time": "14:00",
                "time_zone": "UTC+00:00",
                "project_details": "We're looking to implement AI-driven data analysis for our customer feedback.",
                "referral_source": "LinkedIn",
                "marketing_consent": True,
                "captcha_token": "abc123xyz456"
            }
        }
    
    @validator('email')
    def validate_email(cls, v):
        """Validate email format"""
        # Simple email validation - a more comprehensive regex could be used
        if '@' not in v or '.' not in v.split('@')[-1]:
            raise ValueError("Invalid email format")
        return v
    
    @validator('preferred_date')
    def validate_preferred_date(cls, v):
        """Validate that the preferred date is in a valid format and not in the past"""
        try:
            date_obj = datetime.strptime(v, "%Y-%m-%d").date()
            if date_obj < datetime.now().date():
                raise ValueError("Preferred date cannot be in the past")
        except ValueError as e:
            if "does not match format" in str(e):
                raise ValueError("Invalid date format. Use YYYY-MM-DD")
            raise e
        return v
    
    @validator('preferred_time')
    def validate_preferred_time(cls, v):
        """Validate that the preferred time is in a valid format"""
        try:
            datetime.strptime(v, "%H:%M")
        except ValueError:
            raise ValueError("Invalid time format. Use HH:MM (24-hour format)")
        return v

class DemoRequestResponseSchema(BaseModel):
    """Pydantic schema for demo request form submission responses"""
    success: bool = Field(True, description="Whether the demo request was successful")
    message: str = Field(..., description="Success message")
    submission_id: uuid.UUID = Field(..., description="Unique identifier for the demo request submission")
    
    class Config:
        """Configuration class for the DemoRequestResponseSchema"""
        schema_extra = {
            "example": {
                "success": True,
                "message": "Your demo request has been successfully submitted. Our team will contact you shortly.",
                "submission_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
            }
        }

class DemoRequestErrorSchema(BaseModel):
    """Pydantic schema for demo request form submission error responses"""
    success: bool = Field(False, description="Whether the demo request was successful")
    message: str = Field(..., description="Error message")
    errors: Dict[str, List[str]] = Field({}, description="Detailed error information by field")
    
    class Config:
        """Configuration class for the DemoRequestErrorSchema"""
        schema_extra = {
            "example": {
                "success": False,
                "message": "There was an error processing your demo request.",
                "errors": {
                    "email": ["Invalid email format"],
                    "preferred_date": ["Preferred date cannot be in the past"]
                }
            }
        }