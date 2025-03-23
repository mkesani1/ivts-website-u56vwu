"""
Initialization file for the scripts package in the IndiVillage backend application.
This file makes utility scripts accessible as a Python package and provides convenient imports for commonly used script functionality.
"""

__version__ = "0.1.0"

# Import the main database seeding function for direct access
from scripts.seed_data import seed_database

# Import the OpenAPI specification generator function
from scripts.generate_api_docs import generate_openapi_spec

# Import the database backup creation function
from scripts.db_backup import create_backup

# Import the S3 backup upload function
from scripts.db_backup import upload_backup_to_s3

# Import the performance testing class for programmatic use
from scripts.performance_test import PerformanceTester

# Expose the database seeding function for importing from the scripts package
__all__ = ["seed_database", "generate_openapi_spec", "create_backup", "upload_backup_to_s3", "PerformanceTester"]