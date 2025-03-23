"""
Alembic migration environment for IndiVillage.com backend application.

This module configures the Alembic migration environment, which is used to
generate and apply database migrations based on SQLAlchemy model changes.
It connects the application's models with Alembic and provides both online
and offline migration capabilities.
"""

import logging
import os
import sys

from alembic import context
from sqlalchemy import engine_from_config, pool

# Add the parent directory to the path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import application components
from app.db.base import Base  # noqa
from app.core.config import settings
from app.core.logging import get_logger

# Initialize logger
logger = get_logger(__name__)

# This is the Alembic Config object, which provides access to the values within the .ini file
config = context.config

# Set target metadata for migrations
target_metadata = Base.metadata


def get_database_url():
    """
    Retrieve the database URL from Alembic config or application settings.
    
    Returns:
        str: Database connection URL
    """
    # Check if database URL is set in Alembic config (sqlalchemy.url in alembic.ini)
    alembic_url = config.get_main_option("sqlalchemy.url")
    if alembic_url:
        return alembic_url
    
    # If not set in config, use the URL from application settings
    return settings.get_database_url()


def run_migrations_offline():
    """
    Run migrations in 'offline' mode.
    
    This configures the context with a URL and executes the migration
    script, without actually connecting to the database. It generates
    SQL script that would be run to apply the migrations.
    
    Returns:
        None
    """
    try:
        url = get_database_url()
        logger.info("Running offline migrations")
        
        context.configure(
            url=url,
            target_metadata=target_metadata,
            literal_binds=True,
            dialect_opts={"paramstyle": "named"},
        )

        with context.begin_transaction():
            context.run_migrations()
        
        logger.info("Offline migrations completed successfully")
    except Exception as e:
        logger.error(f"Error during offline migrations: {str(e)}", exc_info=True)
        raise


def run_migrations_online():
    """
    Run migrations in 'online' mode.
    
    This configures the context with an engine connected to the database
    and executes the migrations directly against the connected database.
    
    Returns:
        None
    """
    try:
        # Get database URL from settings
        url = get_database_url()
        logger.info("Running online migrations")
        
        # Configure SQLAlchemy engine from alembic.ini settings
        # but override the URL with our application settings
        configuration = config.get_section(config.config_ini_section)
        if configuration is None:
            configuration = {}
        configuration["sqlalchemy.url"] = url
        
        connectable = engine_from_config(
            configuration,
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
        )

        with connectable.connect() as connection:
            context.configure(
                connection=connection, 
                target_metadata=target_metadata
            )

            with context.begin_transaction():
                context.run_migrations()
            
            logger.info("Online migrations completed successfully")
    except Exception as e:
        logger.error(f"Error during online migrations: {str(e)}", exc_info=True)
        raise


# Check if the script is being run in offline mode
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()