"""
Form submission models for the IndiVillage.com backend application.

This module defines the database models related to form submissions, including
the FormSubmission model, FormType and FormStatus enums, and the association table
for linking form submissions to services.
"""

import enum
import uuid
import json
from datetime import datetime

from sqlalchemy import Column, String, Text, ForeignKey, Enum, DateTime, Table  # SQLAlchemy 1.4.0
from sqlalchemy.dialects.postgresql import UUID  # SQLAlchemy 1.4.0
from sqlalchemy.orm import relationship  # SQLAlchemy 1.4.0

from app.db.base import Base


class FormType(enum.Enum):
    """
    Enumeration of form submission types supported by the application.
    """
    CONTACT = "contact"
    DEMO_REQUEST = "demo_request"
    QUOTE_REQUEST = "quote_request"


class FormStatus(enum.Enum):
    """
    Enumeration of processing statuses for form submissions.
    """
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


# Association table for the many-to-many relationship between form submissions and services
FormServiceInterest = Table(
    "form_service_interest",
    Base.metadata,
    Column("form_id", UUID(as_uuid=True), ForeignKey("form_submissions.id"), primary_key=True),
    Column("service_id", UUID(as_uuid=True), ForeignKey("services.id"), primary_key=True),
)


class FormSubmission(Base):
    """
    SQLAlchemy ORM model representing a form submission in the IndiVillage.com application.
    
    This model stores form data, submission status, and maintains relationships with users
    and services. It supports various form types including contact forms, demo requests,
    and quote requests as defined in the FormType enum.
    """
    __tablename__ = "form_submissions"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign key to user
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Form data
    form_type = Column(Enum(FormType), nullable=False)
    data = Column(Text, nullable=False)  # JSON data
    status = Column(Enum(FormStatus), default=FormStatus.PENDING, nullable=False)
    ip_address = Column(String(45), nullable=True)  # Accommodates IPv6 addresses
    crm_id = Column(String(255), nullable=True)  # ID from HubSpot after sync
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="form_submissions")
    services = relationship(
        "Service",
        secondary=FormServiceInterest,
        back_populates="form_submissions"
    )
    
    def to_dict(self):
        """
        Converts the form submission model to a dictionary representation.
        
        Returns:
            dict: Dictionary containing form submission information
        """
        result = {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "form_type": self.form_type.value,
            "status": self.status.value,
            "ip_address": self.ip_address,
            "crm_id": self.crm_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        
        # Parse and include the JSON data
        data = self.get_data()
        if data:
            result["data"] = data
        
        # Include user information if available
        if self.user:
            result["user"] = {
                "id": str(self.user.id),
                "email": self.user.email,
                "name": self.user.name
            }
        
        # Include services information if available
        if self.services:
            result["services"] = [
                {"id": str(service.id), "name": service.name}
                for service in self.services
            ]
        
        return result
    
    def get_data(self):
        """
        Retrieves the form data as a Python dictionary.
        
        Returns:
            dict: Form data as a dictionary
        """
        if not self.data:
            return {}
        
        try:
            return json.loads(self.data)
        except json.JSONDecodeError:
            return {}
    
    def set_data(self, data_dict):
        """
        Sets the form data from a Python dictionary.
        
        Args:
            data_dict (dict): The form data to store
        """
        if data_dict is None:
            self.data = "{}"
        else:
            self.data = json.dumps(data_dict)
    
    def update_status(self, status):
        """
        Updates the form submission status.
        
        Args:
            status (FormStatus): The new status
        """
        self.status = status
        self.updated_at = datetime.utcnow()
    
    def update_crm_id(self, crm_id):
        """
        Updates the CRM ID after successful synchronization with HubSpot.
        
        Args:
            crm_id (str): The HubSpot CRM record ID
        """
        self.crm_id = crm_id
        self.updated_at = datetime.utcnow()