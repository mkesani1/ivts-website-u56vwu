"""
Core database module that defines the SQLAlchemy declarative base and base model classes.

This module serves as a central point for database model configuration and 
should be imported by all model definitions to ensure they are registered 
with SQLAlchemy.
"""

from sqlalchemy.ext.declarative import declarative_base  # SQLAlchemy 1.4.0
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey  # SQLAlchemy 1.4.0
from sqlalchemy.orm import relationship  # SQLAlchemy 1.4.0
from datetime import datetime
import json
from typing import Dict, Any

# Create the declarative base class that will be used for all models
Base = declarative_base()


def get_base():
    """
    Returns the SQLAlchemy declarative base class for use in model definitions.

    Returns:
        DeclarativeMeta: The SQLAlchemy declarative base class
    """
    return Base


class BaseModel:
    """
    Abstract base model class that provides common fields and functionality for all database models.
    
    This class should be inherited by all database model classes to ensure
    consistent behavior and fields across the application.
    """
    
    # Common timestamp fields for all models
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Converts the model instance to a dictionary representation.
        
        Returns:
            dict: Dictionary containing model data
        """
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            
            # Handle datetime objects for JSON serialization
            if isinstance(value, datetime):
                value = value.isoformat()
                
            result[column.name] = value
            
        return result