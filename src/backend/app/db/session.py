"""
Database session management module that configures SQLAlchemy engine, session factory, and provides dependency injection for 
database access in FastAPI endpoints. This module is responsible for establishing database connections, managing connection pooling,
and ensuring proper session lifecycle management.
"""

import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base  # SQLAlchemy 1.4.0
from typing import Generator  # standard library

from ..core.config import settings
from ..core.logging import get_logger
from ..core.exceptions import DatabaseException

# Initialize logger
logger = get_logger(__name__)

# Create database engine with connection pooling configuration
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before using them
    pool_size=10,        # Number of connections to keep open in the pool
    max_overflow=20,     # Maximum number of connections to create beyond pool_size
    pool_recycle=3600,   # Recycle connections after 1 hour to prevent them from becoming stale
    echo=settings.ENVIRONMENT == 'development'  # Log SQL queries in development environment
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator[Session, None, None]:
    """
    Dependency function that provides a database session for FastAPI endpoints.
    
    Yields:
        Generator[Session, None, None]: Yields a database session that is automatically closed after use
    """
    db = SessionLocal()
    try:
        logger.debug("Creating new database session")
        yield db
    except sqlalchemy.exc.SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}", exc_info=e)
        raise DatabaseException(message=f"Database error: {str(e)}", details={"original_error": str(e)})
    finally:
        logger.debug("Closing database session")
        db.close()

def close_engine() -> None:
    """
    Closes the database engine and connection pool.
    
    This function should be called during application shutdown to properly
    release all database connections.
    """
    logger.info("Closing database engine and connection pool")
    try:
        engine.dispose()
        logger.info("Database engine closed successfully")
    except Exception as e:
        logger.error(f"Error closing database engine: {str(e)}", exc_info=e)

def get_engine():
    """
    Returns the SQLAlchemy engine instance.
    
    Returns:
        sqlalchemy.engine.Engine: The configured SQLAlchemy engine
    """
    return engine