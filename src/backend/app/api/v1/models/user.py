"""
User model module for IndiVillage.com application.

This module defines the SQLAlchemy ORM model for users in the system,
including authentication details, profile information, and relationships
with other entities such as form submissions and file uploads.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
import datetime
import enum

from app.db.base import Base
from app.core.security import get_password_hash, verify_password

# Define user roles as an enumeration
UserRole = enum.Enum('UserRole', ['ANONYMOUS', 'REGISTERED', 'CONTENT_EDITOR', 'ADMINISTRATOR'])


class User(Base):
    """
    SQLAlchemy ORM model representing a user in the IndiVillage.com application.
    Stores user authentication information, contact details, and maintains
    relationships with form submissions and file uploads.
    """
    __tablename__ = "users"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # User information and authentication
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    name = Column(String, nullable=False)
    company = Column(String)
    phone = Column(String)
    country = Column(String)
    
    # Role and status
    role = Column(Enum(UserRole), nullable=False, default=UserRole.REGISTERED)
    crm_id = Column(String)  # ID in the HubSpot CRM system
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)
    
    # Relationships
    form_submissions = relationship("FormSubmission", back_populates="user")
    file_uploads = relationship("FileUpload", back_populates="user")
    
    def set_password(self, password: str) -> None:
        """
        Sets the user's password by hashing the provided plain password.
        
        Args:
            password: The plain text password to hash
        """
        self.hashed_password = get_password_hash(password)
    
    def check_password(self, password: str) -> bool:
        """
        Verifies if the provided password matches the user's stored password hash.
        
        Args:
            password: The plain text password to verify
            
        Returns:
            bool: True if password matches, False otherwise
        """
        return verify_password(password, self.hashed_password)
    
    def update_crm_id(self, crm_id: str) -> None:
        """
        Updates the CRM ID after successful synchronization with HubSpot.
        
        Args:
            crm_id: The ID from HubSpot CRM
        """
        self.crm_id = crm_id
        self.updated_at = datetime.datetime.utcnow()
    
    def is_admin(self) -> bool:
        """
        Checks if the user has administrator privileges.
        
        Returns:
            bool: True if user has ADMINISTRATOR role, False otherwise
        """
        return self.role == UserRole.ADMINISTRATOR
    
    def is_content_editor(self) -> bool:
        """
        Checks if the user has content editor privileges.
        
        Returns:
            bool: True if user has CONTENT_EDITOR or ADMINISTRATOR role, False otherwise
        """
        return self.role in [UserRole.CONTENT_EDITOR, UserRole.ADMINISTRATOR]
    
    def to_dict(self) -> dict:
        """
        Converts the user model to a dictionary representation, excluding sensitive information.
        
        Returns:
            dict: Dictionary containing user information
        """
        return {
            "id": str(self.id),
            "email": self.email,
            "name": self.name,
            "company": self.company,
            "phone": self.phone,
            "country": self.country,
            "role": self.role.name,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }