"""
Pydantic schemas for case study-related data validation in the IndiVillage.com backend API.

This module defines the schemas used for validating request and response data for case study
endpoints, ensuring data integrity and proper API documentation.
"""

# Standard library imports
from typing import List, Optional
from datetime import datetime
import re

# External imports - pydantic v1.9.0
from pydantic import BaseModel, Field, validator, UUID4, constr

# Internal imports
from app.api.v1.models.case_study import CaseStudy, CaseStudyResult, Industry


class ServiceSchemaBase(BaseModel):
    """Simplified schema for service data used in case study relationships."""
    id: UUID4
    name: str
    slug: str
    
    class Config:
        orm_mode = True


class CaseStudyResultBase(BaseModel):
    """Base Pydantic model for case study result data validation with common fields"""
    metric: str
    value: str
    description: str
    
    class Config:
        orm_mode = True


class CaseStudyResultCreate(CaseStudyResultBase):
    """Pydantic model for validating case study result creation requests"""
    case_study_id: UUID4


class CaseStudyResultUpdate(BaseModel):
    """Pydantic model for validating case study result update requests"""
    metric: Optional[str] = None
    value: Optional[str] = None
    description: Optional[str] = None
    
    class Config:
        orm_mode = True


class CaseStudyResultSchema(CaseStudyResultBase):
    """Pydantic model for case study result response data"""
    id: UUID4
    case_study_id: UUID4
    
    class Config:
        orm_mode = True
    
    @classmethod
    def from_orm(cls, obj: CaseStudyResult):
        """Creates a CaseStudyResultSchema instance from a CaseStudyResult ORM model"""
        return super().from_orm(obj)


class IndustrySchema(BaseModel):
    """Pydantic model for industry response data"""
    id: UUID4
    name: str
    slug: str
    
    class Config:
        orm_mode = True
    
    @classmethod
    def from_orm(cls, obj: Industry):
        """Creates an IndustrySchema instance from an Industry ORM model"""
        return super().from_orm(obj)


class IndustryCreate(BaseModel):
    """Pydantic model for validating industry creation requests"""
    name: str
    slug: str
    
    @validator('slug')
    def validate_slug(cls, value):
        """Validates that the slug is in the correct format"""
        if not re.match(r'^[a-z0-9]+(?:-[a-z0-9]+)*$', value):
            raise ValueError("Slug must contain only lowercase letters, numbers, and hyphens, and cannot start or end with a hyphen")
        return value
    
    class Config:
        orm_mode = True


class IndustryUpdate(BaseModel):
    """Pydantic model for validating industry update requests"""
    name: Optional[str] = None
    slug: Optional[str] = None
    
    @validator('slug')
    def validate_slug(cls, value):
        """Validates that the slug is in the correct format"""
        if value is not None and not re.match(r'^[a-z0-9]+(?:-[a-z0-9]+)*$', value):
            raise ValueError("Slug must contain only lowercase letters, numbers, and hyphens, and cannot start or end with a hyphen")
        return value
    
    class Config:
        orm_mode = True


class CaseStudyBase(BaseModel):
    """Base Pydantic model for case study data validation with common fields"""
    title: str
    slug: str
    client: str
    challenge: str
    solution: str
    
    @validator('slug')
    def validate_slug(cls, value):
        """Validates that the slug is in the correct format"""
        if not re.match(r'^[a-z0-9]+(?:-[a-z0-9]+)*$', value):
            raise ValueError("Slug must contain only lowercase letters, numbers, and hyphens, and cannot start or end with a hyphen")
        return value
    
    class Config:
        orm_mode = True


class CaseStudyCreate(CaseStudyBase):
    """Pydantic model for validating case study creation requests"""
    industry_id: UUID4
    service_ids: Optional[List[UUID4]] = None
    results: Optional[List[CaseStudyResultCreate]] = None
    
    class Config:
        orm_mode = True


class CaseStudyUpdate(BaseModel):
    """Pydantic model for validating case study update requests"""
    title: Optional[str] = None
    slug: Optional[str] = None
    client: Optional[str] = None
    challenge: Optional[str] = None
    solution: Optional[str] = None
    industry_id: Optional[UUID4] = None
    service_ids: Optional[List[UUID4]] = None
    
    @validator('slug')
    def validate_slug(cls, value):
        """Validates that the slug is in the correct format"""
        if value is not None and not re.match(r'^[a-z0-9]+(?:-[a-z0-9]+)*$', value):
            raise ValueError("Slug must contain only lowercase letters, numbers, and hyphens, and cannot start or end with a hyphen")
        return value
    
    class Config:
        orm_mode = True


class CaseStudySchema(CaseStudyBase):
    """Pydantic model for case study response data"""
    id: UUID4
    industry_id: UUID4
    created_at: datetime
    updated_at: datetime
    industry: Optional[IndustrySchema] = None
    results: Optional[List[CaseStudyResultSchema]] = None
    services: Optional[List[ServiceSchemaBase]] = None
    
    class Config:
        orm_mode = True
    
    @classmethod
    def from_orm(cls, obj: CaseStudy):
        """Creates a CaseStudySchema instance from a CaseStudy ORM model"""
        return super().from_orm(obj)