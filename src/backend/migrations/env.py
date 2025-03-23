import logging
import os
import sys
from logging.config import fileConfig

# Add the parent directory to the Python path so we can import application modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from alembic import context
from sqlalchemy import engine_from_config, pool
import sqlalchemy

# Import application settings and models
from app.core.config import settings
from app.db.base import Base

# This is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)
logger = logging.getLogger('alembic.env')

# Add your model's MetaData object here for 'autogenerate' support
target_metadata = Base.metadata


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.
    """
    # Get database URL from alembic config or application settings
    url = config.get_main_option("sqlalchemy.url") or settings.get_database_url()
    
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()
    
    logger.info("Offline migrations completed successfully.")


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    # Get database URL from application settings
    db_url = settings.get_database_url()
    
    # Override alembic config with the application database URL
    config_section = config.get_section(config.config_ini_section)
    config_section['sqlalchemy.url'] = db_url

    # Create engine with appropriate configuration for migrations
    # Using NullPool to ensure connections are closed after migration operations
    connectable = engine_from_config(
        config_section,
        prefix='sqlalchemy.',
        poolclass=pool.NullPool,
    )

    try:
        with connectable.connect() as connection:
            context.configure(
                connection=connection,
                target_metadata=target_metadata,
                compare_type=True,  # Check column type changes
                compare_server_default=True,  # Check for server default changes
            )

            with context.begin_transaction():
                context.run_migrations()
            
        logger.info("Online migrations completed successfully.")
    except Exception as e:
        logger.error(f"Error during migration: {str(e)}")
        raise


# Determine which mode to run based on Alembic's context
if context.is_offline_mode():
    logger.info("Running migrations offline")
    run_migrations_offline()
else:
    logger.info("Running migrations online")
    run_migrations_online()