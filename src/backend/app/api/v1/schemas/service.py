"""
Pydantic schemas for service-related data validation in the IndiVillage.com backend API.

This module defines the schemas used for validating request and response data for service
endpoints, ensuring data integrity and proper API documentation.
"""

# Standard library imports
from typing import List, Optional
from datetime import datetime
import re

# External imports - pydantic v1.9.0
from pydantic import BaseModel, Field, validator, UUID4, constr

# Internal imports
from app.api.v1.models.service import Service, ServiceFeature
from app.api.v1.schemas.case_study import CaseStudySchema


class ServiceFeatureBase(BaseModel):
    """Base Pydantic model for service feature data validation with common fields"""
    title: str
    description: str
    order: int


class ServiceFeatureCreate(ServiceFeatureBase):
    """Pydantic model for validating service feature creation requests"""
    service_id: UUID4


class ServiceFeatureUpdate(BaseModel):
    """Pydantic model for validating service feature update requests"""
    title: Optional[str] = None
    description: Optional[str] = None
    order: Optional[int] = None


class ServiceFeatureSchema(ServiceFeatureBase):
    """Pydantic model for service feature response data"""
    id: UUID4
    service_id: UUID4
    
    class Config:
        orm_mode = True
    
    @classmethod
    def from_orm(cls, obj: ServiceFeature):
        """Creates a ServiceFeatureSchema instance from a ServiceFeature ORM model"""
        return super().from_orm(obj)


class ServiceBase(BaseModel):
    """Base Pydantic model for service data validation with common fields"""
    name: str
    slug: str
    description: str
    icon: Optional[str] = None  # Optional to match nullable in ORM model
    order: int
    
    @validator('slug')
    def validate_slug(cls, value):
        """Validates that the slug is in the correct format"""
        if not re.match(r'^[a-z0-9]+(?:-[a-z0-9]+)*$', value):
            raise ValueError("Slug must contain only lowercase letters, numbers, and hyphens, and cannot start or end with a hyphen")
        return value


class ServiceCreate(ServiceBase):
    """Pydantic model for validating service creation requests"""
    features: Optional[List[ServiceFeatureCreate]] = None
    case_study_ids: Optional[List[UUID4]] = None


class ServiceUpdate(BaseModel):
    """Pydantic model for validating service update requests"""
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    order: Optional[int] = None
    case_study_ids: Optional[List[UUID4]] = None
    
    @validator('slug')
    def validate_slug(cls, value):
        """Validates that the slug is in the correct format"""
        if value is not None and not re.match(r'^[a-z0-9]+(?:-[a-z0-9]+)*$', value):
            raise ValueError("Slug must contain only lowercase letters, numbers, and hyphens, and cannot start or end with a hyphen")
        return value


class ServiceSchema(ServiceBase):
    """Pydantic model for service response data"""
    id: UUID4
    created_at: datetime
    updated_at: datetime
    features: Optional[List[ServiceFeatureSchema]] = None
    case_studies: Optional[List[CaseStudySchema]] = None
    
    class Config:
        orm_mode = True
    
    @classmethod
    def from_orm(cls, obj: Service):
        """Creates a ServiceSchema instance from a Service ORM model"""
        return super().from_orm(obj)