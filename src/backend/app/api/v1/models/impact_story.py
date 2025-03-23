"""
Impact story models module for the IndiVillage.com application.

This module defines SQLAlchemy ORM models for representing social impact stories, 
metrics, and locations that showcase IndiVillage's 'AI for Good' mission and 
the positive social change created through their technology services.
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime  # sqlalchemy 1.4.0
from sqlalchemy.orm import relationship  # sqlalchemy 1.4.0
from sqlalchemy.dialects.postgresql import UUID  # sqlalchemy 1.4.0
import uuid  # standard library

from app.db.base import Base, BaseModel


class ImpactStory(Base, BaseModel):
    """
    SQLAlchemy ORM model representing a social impact story in the IndiVillage.com application.
    
    Stores information about how IndiVillage's AI services create positive social change,
    including narrative content, beneficiaries, geographic location, and quantifiable metrics.
    """
    __tablename__ = "impact_stories"
    
    # Primary key
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    
    # Core fields
    title = Column(String(255), nullable=False)
    slug = Column(String(255), nullable=False, unique=True)
    story = Column(Text, nullable=False)
    beneficiaries = Column(String(255), nullable=True)
    location_id = Column(UUID, ForeignKey("locations.id"), nullable=True)
    media = Column(String(255), nullable=True)  # Path or URL to media assets
    
    # Relationships
    location = relationship("Location", back_populates="impact_stories")
    metrics = relationship("ImpactMetric", back_populates="story", cascade="all, delete-orphan")
    
    def to_dict(self):
        """
        Converts the impact story model to a dictionary representation.
        
        Returns:
            dict: Dictionary containing impact story information
        """
        result = {
            "id": str(self.id),
            "title": self.title,
            "slug": self.slug,
            "story": self.story,
            "beneficiaries": self.beneficiaries,
            "location_id": str(self.location_id) if self.location_id else None,
            "media": self.media,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
        return result
    
    def get_metrics(self):
        """
        Returns a list of metrics associated with this impact story.
        
        Returns:
            list: List of ImpactMetric objects associated with this impact story
        """
        return self.metrics


class ImpactMetric(Base, BaseModel):
    """
    SQLAlchemy ORM model representing a measurable metric for an impact story.
    
    Each impact story can have multiple metrics that demonstrate the quantifiable 
    impact of IndiVillage's social mission, such as jobs created, community impact,
    or other measurable outcomes.
    """
    __tablename__ = "impact_metrics"
    
    # Primary key
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    
    # Foreign key
    story_id = Column(UUID, ForeignKey("impact_stories.id"), nullable=False)
    
    # Core fields
    metric_name = Column(String(255), nullable=False)
    value = Column(String(100), nullable=False)  # Using string to support various formats (numbers, percentages, etc.)
    unit = Column(String(50), nullable=True)
    period_start = Column(DateTime, nullable=True)  # Optional time period for the metric
    period_end = Column(DateTime, nullable=True)
    
    # Relationships
    story = relationship("ImpactStory", back_populates="metrics")
    
    def to_dict(self):
        """
        Converts the impact metric model to a dictionary representation.
        
        Returns:
            dict: Dictionary containing impact metric information
        """
        result = {
            "id": str(self.id),
            "story_id": str(self.story_id),
            "metric_name": self.metric_name,
            "value": self.value,
            "unit": self.unit,
            "period_start": self.period_start.isoformat() if self.period_start else None,
            "period_end": self.period_end.isoformat() if self.period_end else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
        return result


class Location(Base, BaseModel):
    """
    SQLAlchemy ORM model representing a geographic location for impact stories.
    
    Used to specify where the social impact initiatives take place, supporting the
    storytelling of how IndiVillage's work creates positive change in specific communities.
    """
    __tablename__ = "locations"
    
    # Primary key
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    
    # Core fields
    name = Column(String(255), nullable=False)
    region = Column(String(255), nullable=True)
    country = Column(String(255), nullable=False)
    
    # Relationships
    impact_stories = relationship("ImpactStory", back_populates="location")
    
    def to_dict(self):
        """
        Converts the location model to a dictionary representation.
        
        Returns:
            dict: Dictionary containing location information
        """
        result = {
            "id": str(self.id),
            "name": self.name,
            "region": self.region,
            "country": self.country,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
        return result