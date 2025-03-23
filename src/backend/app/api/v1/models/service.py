"""
Models for AI services and their features in the IndiVillage.com application.

This module defines the SQLAlchemy ORM models for services and service features,
implementing the database schema for storing AI service offerings including data
collection, data preparation, AI model development, and Human-in-the-loop solutions,
along with their features and relationships to case studies.
"""

# Standard library imports
import uuid

# SQLAlchemy imports - sqlalchemy v1.4.0
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

# Internal imports
from app.db.base import Base, BaseModel

# Association table for the many-to-many relationship between services and case studies
ServiceCaseStudy = Table(
    'service_case_study',
    Base.metadata,
    Column('service_id', UUID(as_uuid=True), ForeignKey('services.id'), primary_key=True),
    Column('case_study_id', UUID(as_uuid=True), ForeignKey('case_studies.id'), primary_key=True)
)


class Service(Base, BaseModel):
    """
    SQLAlchemy ORM model representing an AI service offering in the IndiVillage.com application.
    
    Stores information about services such as data collection, data preparation, 
    AI model development, and human-in-the-loop solutions.
    """
    __tablename__ = 'services'
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Service details
    name = Column(String(255), nullable=False)
    slug = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=False)
    icon = Column(String(255), nullable=True)
    order = Column(Integer, nullable=False, default=0)
    
    # Relationships
    features = relationship("ServiceFeature", back_populates="service", cascade="all, delete-orphan")
    case_studies = relationship("CaseStudy", secondary=ServiceCaseStudy, back_populates="services")
    
    def to_dict(self):
        """
        Converts the service model to a dictionary representation.
        
        Returns:
            dict: Dictionary containing service information
        """
        result = super().to_dict()
        # Note: We don't include features or case studies by default to avoid circular references
        # These can be added explicitly when needed
        return result
    
    def get_features(self):
        """
        Returns a list of features associated with this service.
        
        Returns:
            list: List of ServiceFeature objects associated with this service
        """
        return self.features
    
    def get_case_studies(self):
        """
        Returns a list of case studies associated with this service.
        
        Returns:
            list: List of CaseStudy objects associated with this service
        """
        return self.case_studies


class ServiceFeature(Base, BaseModel):
    """
    SQLAlchemy ORM model representing a feature of an AI service.
    
    Each service can have multiple features that describe its capabilities and benefits.
    """
    __tablename__ = 'service_features'
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign key to Service
    service_id = Column(UUID(as_uuid=True), ForeignKey('services.id'), nullable=False)
    
    # Feature details
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    order = Column(Integer, nullable=False, default=0)
    
    # Relationships
    service = relationship("Service", back_populates="features")
    
    def to_dict(self):
        """
        Converts the service feature model to a dictionary representation.
        
        Returns:
            dict: Dictionary containing service feature information
        """
        result = super().to_dict()
        # Note: We exclude the full service relationship to avoid circular references
        return result