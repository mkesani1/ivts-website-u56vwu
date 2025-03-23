"""
Pydantic schemas for impact story-related data validation.

This module defines Pydantic models used for validating request/response data
for impact story endpoints, ensuring data integrity and proper API documentation.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, validator, UUID4, constr  # pydantic v1.9.0

from app.api.v1.models.impact_story import ImpactStory, ImpactMetric, Location


class LocationSchema(BaseModel):
    """Pydantic model for location response data."""
    id: UUID4
    name: str
    region: str
    country: str
    
    class Config:
        orm_mode = True
    
    @classmethod
    def from_orm(cls, obj: Location):
        """Creates a LocationSchema instance from a Location ORM model."""
        return super().from_orm(obj)


class LocationCreate(BaseModel):
    """Pydantic model for validating location creation requests."""
    name: str
    region: str
    country: str


class LocationUpdate(BaseModel):
    """Pydantic model for validating location update requests."""
    name: Optional[str] = None
    region: Optional[str] = None
    country: Optional[str] = None


class ImpactMetricBase(BaseModel):
    """Base Pydantic model for impact metric data validation with common fields."""
    metric_name: str
    value: str
    unit: str
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None


class ImpactMetricCreate(ImpactMetricBase):
    """Pydantic model for validating impact metric creation requests."""
    story_id: UUID4


class ImpactMetricUpdate(BaseModel):
    """Pydantic model for validating impact metric update requests."""
    metric_name: Optional[str] = None
    value: Optional[str] = None
    unit: Optional[str] = None
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None


class ImpactMetricSchema(ImpactMetricBase):
    """Pydantic model for impact metric response data."""
    id: UUID4
    story_id: UUID4
    
    class Config:
        orm_mode = True
        
    @classmethod
    def from_orm(cls, obj: ImpactMetric):
        """Creates an ImpactMetricSchema instance from an ImpactMetric ORM model."""
        return super().from_orm(obj)


class ImpactStoryBase(BaseModel):
    """Base Pydantic model for impact story data validation with common fields."""
    title: str
    slug: constr(regex='^[a-z0-9]+(?:-[a-z0-9]+)*$')
    story: str
    beneficiaries: str
    media: Optional[str] = None
    
    @validator('slug')
    def validate_slug(cls, value):
        """Validates that the slug is in the correct format."""
        if not value:
            raise ValueError('Slug cannot be empty')
        
        if value.startswith('-') or value.endswith('-'):
            raise ValueError('Slug cannot start or end with a hyphen')
            
        if '--' in value:
            raise ValueError('Slug cannot contain consecutive hyphens')
            
        return value


class ImpactStoryCreate(ImpactStoryBase):
    """Pydantic model for validating impact story creation requests."""
    location_id: UUID4
    metrics: Optional[List[ImpactMetricCreate]] = None


class ImpactStoryUpdate(BaseModel):
    """Pydantic model for validating impact story update requests."""
    title: Optional[str] = None
    slug: Optional[constr(regex='^[a-z0-9]+(?:-[a-z0-9]+)*$')] = None
    story: Optional[str] = None
    beneficiaries: Optional[str] = None
    location_id: Optional[UUID4] = None
    media: Optional[str] = None
    
    @validator('slug')
    def validate_slug(cls, value):
        """Validates that the slug is in the correct format."""
        if not value:
            return value
            
        if value.startswith('-') or value.endswith('-'):
            raise ValueError('Slug cannot start or end with a hyphen')
            
        if '--' in value:
            raise ValueError('Slug cannot contain consecutive hyphens')
            
        return value


class ImpactStorySchema(ImpactStoryBase):
    """Pydantic model for impact story response data."""
    id: UUID4
    location_id: UUID4
    created_at: datetime
    updated_at: datetime
    location: Optional[LocationSchema] = None
    metrics: Optional[List[ImpactMetricSchema]] = None
    
    class Config:
        orm_mode = True
        
    @classmethod
    def from_orm(cls, obj: ImpactStory):
        """Creates an ImpactStorySchema instance from an ImpactStory ORM model."""
        schema = super().from_orm(obj)
        
        # Convert location to LocationSchema if present
        if obj.location:
            schema.location = LocationSchema.from_orm(obj.location)
            
        # Convert metrics to ImpactMetricSchema instances if present
        if obj.metrics:
            schema.metrics = [ImpactMetricSchema.from_orm(metric) for metric in obj.metrics]
            
        return schema