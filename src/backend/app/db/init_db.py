"""
Database initialization module that creates database tables and sets up initial data
for the IndiVillage.com application. This module is responsible for ensuring the database 
schema is properly created and populated with necessary seed data during application 
startup or when explicitly invoked.
"""

import logging
import uuid
from sqlalchemy import exc

from .base import Base
from .session import engine, SessionLocal
from app.api.v1.models.user import User, UserRole
from app.api.v1.models.service import Service
from app.core.config import settings
from app.core.logging import get_logger
from scripts.seed_data import seed_database

# Initialize logger
logger = get_logger(__name__)

def create_tables():
    """
    Creates all database tables defined in SQLAlchemy models.
    """
    logger.info("Creating database tables")
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except exc.SQLAlchemyError as e:
        logger.error(f"Error creating database tables: {str(e)}", exc_info=e)
        raise

def create_admin_user(db):
    """
    Creates an admin user if one doesn't already exist.
    
    Args:
        db: Database session
    
    Returns:
        User: The admin user object (existing or newly created)
    """
    # Check if admin user already exists
    admin_user = db.query(User).filter(User.role == UserRole.ADMINISTRATOR).first()
    
    if admin_user:
        logger.info(f"Admin user already exists: {admin_user.email}")
        return admin_user
    
    # Create admin user
    logger.info(f"Creating admin user with email: {settings.ADMIN_EMAIL}")
    admin_user = User(
        id=uuid.uuid4(),
        email=settings.ADMIN_EMAIL,
        name="Admin User",
        company="IndiVillage",
        phone=None,  # Optional field
        country="India",
        role=UserRole.ADMINISTRATOR,
        is_active=True
    )
    
    # Set a secure password for the admin user - should be changed after first login
    admin_user.set_password("ChangeMe123!")
    
    db.add(admin_user)
    db.commit()
    logger.info(f"Admin user created successfully: {admin_user.email}")
    
    return admin_user

def create_initial_services(db):
    """
    Creates initial service categories if they don't already exist.
    
    Args:
        db: Database session
    
    Returns:
        list: List of service objects (existing or newly created)
    """
    # Check if services already exist
    existing_services = db.query(Service).all()
    if existing_services:
        logger.info(f"Initial services already exist: {len(existing_services)} services found")
        return existing_services
    
    # Create initial services
    logger.info("Creating initial service categories")
    services = [
        Service(
            id=uuid.uuid4(),
            name="Data Collection",
            slug="data-collection",
            description="Comprehensive data gathering solutions to power your AI models with high-quality training data.",
            icon="data-collection-icon.svg",
            order=1
        ),
        Service(
            id=uuid.uuid4(),
            name="Data Preparation",
            slug="data-preparation",
            description="Transform raw data into AI-ready datasets with our comprehensive data preparation services.",
            icon="data-preparation-icon.svg",
            order=2
        ),
        Service(
            id=uuid.uuid4(),
            name="AI Model Development",
            slug="ai-model-development",
            description="Custom AI model creation and optimization to meet your specific business needs.",
            icon="ai-model-development-icon.svg",
            order=3
        ),
        Service(
            id=uuid.uuid4(),
            name="Human-in-the-Loop",
            slug="human-in-the-loop",
            description="Enhance AI accuracy with human oversight for critical decision points and edge cases.",
            icon="human-in-the-loop-icon.svg",
            order=4
        )
    ]
    
    db.add_all(services)
    db.commit()
    logger.info(f"Created {len(services)} initial service categories")
    
    return services

def init_development_data():
    """
    Initializes development environment with sample data.
    
    This function checks if the current environment is development, and if so,
    calls the seed_database function to populate sample data for development
    and testing purposes.
    """
    if settings.ENVIRONMENT.lower() == "development":
        logger.info("Initializing development environment with sample data")
        try:
            seed_database()
            logger.info("Development data initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing development data: {str(e)}", exc_info=e)
    else:
        logger.info(f"Skipping development data initialization for environment: {settings.ENVIRONMENT}")

def init_db():
    """
    Main function to initialize the database with tables and initial data.
    
    This function is called during application startup to ensure the database
    schema is created and required initial data is present.
    """
    logger.info("Starting database initialization")
    try:
        # Create tables
        create_tables()
        
        # Create a database session
        db = SessionLocal()
        
        try:
            # Create admin user
            create_admin_user(db)
            
            # Create initial services
            create_initial_services(db)
        finally:
            # Close the session
            db.close()
        
        # Initialize development data if in development environment
        init_development_data()
        
        logger.info("Database initialization completed successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}", exc_info=e)
        raise