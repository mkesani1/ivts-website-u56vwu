"""
Models for case studies, case study results, and industries in the IndiVillage.com application.

This module defines the SQLAlchemy ORM models for case studies, case study results, and industries,
implementing the database schema for storing client success stories that showcase how IndiVillage's
AI services have been successfully implemented across different industries.
"""

# Standard library imports
import uuid

# SQLAlchemy imports - sqlalchemy v1.4.0
from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

# Internal imports
from app.db.base import Base, BaseModel
from app.api.v1.models.service import ServiceCaseStudy


class Industry(Base, BaseModel):
    """
    SQLAlchemy ORM model representing an industry category for case studies.
    Used to categorize case studies by the industry sector of the client.
    """
    __tablename__ = 'industries'
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Industry details
    name = Column(String(255), nullable=False)
    slug = Column(String(255), nullable=False, unique=True)
    
    # Relationships
    case_studies = relationship("CaseStudy", back_populates="industry")
    
    def to_dict(self):
        """
        Converts the industry model to a dictionary representation.
        
        Returns:
            dict: Dictionary containing industry information
        """
        result = super().to_dict()
        return result


class CaseStudy(Base, BaseModel):
    """
    SQLAlchemy ORM model representing a client case study in the IndiVillage.com application.
    
    Stores information about successful implementations of IndiVillage's AI services for clients.
    """
    __tablename__ = 'case_studies'
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Case study details
    title = Column(String(255), nullable=False)
    slug = Column(String(255), nullable=False, unique=True)
    client = Column(String(255), nullable=False)
    challenge = Column(Text, nullable=False)
    solution = Column(Text, nullable=False)
    
    # Foreign key to Industry
    industry_id = Column(UUID(as_uuid=True), ForeignKey('industries.id'), nullable=False)
    
    # Relationships
    industry = relationship("Industry", back_populates="case_studies")
    results = relationship("CaseStudyResult", back_populates="case_study", cascade="all, delete-orphan")
    services = relationship("Service", secondary=ServiceCaseStudy, back_populates="case_studies")
    
    def to_dict(self):
        """
        Converts the case study model to a dictionary representation.
        
        Returns:
            dict: Dictionary containing case study information
        """
        result = super().to_dict()
        # Note: We don't include results or services by default to avoid circular references
        # These can be added explicitly when needed
        return result
    
    def get_results(self):
        """
        Returns a list of results associated with this case study.
        
        Returns:
            list: List of CaseStudyResult objects associated with this case study
        """
        return self.results
    
    def get_services(self):
        """
        Returns a list of services associated with this case study.
        
        Returns:
            list: List of Service objects associated with this case study
        """
        return self.services


class CaseStudyResult(Base, BaseModel):
    """
    SQLAlchemy ORM model representing a measurable result for a case study.
    
    Each case study can have multiple results that demonstrate the impact of IndiVillage's services.
    """
    __tablename__ = 'case_study_results'
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign key to CaseStudy
    case_study_id = Column(UUID(as_uuid=True), ForeignKey('case_studies.id'), nullable=False)
    
    # Result details
    metric = Column(String(255), nullable=False)
    value = Column(String(255), nullable=False)
    description = Column(String(255), nullable=True)
    
    # Relationships
    case_study = relationship("CaseStudy", back_populates="results")
    
    def to_dict(self):
        """
        Converts the case study result model to a dictionary representation.
        
        Returns:
            dict: Dictionary containing case study result information
        """
        result = super().to_dict()
        # Note: We exclude the full case_study relationship to avoid circular references
        return result