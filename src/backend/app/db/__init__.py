"""
Database module initialization file that exports essential database components for use throughout 
the IndiVillage.com backend application. This file serves as the entry point for database-related 
functionality, providing access to the SQLAlchemy base class, session management, 
and database initialization functions.
"""

# Import database components
from .base import Base
from .session import engine, SessionLocal, get_db
from .init_db import init_db

# Define which components are exported from the module
__all__ = [
    'Base',
    'engine',
    'SessionLocal',
    'get_db',
    'init_db',
]