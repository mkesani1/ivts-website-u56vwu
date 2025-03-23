# Database Migrations

Documentation for the database migration system used in the IndiVillage.com backend application. This project uses Alembic for managing database schema changes in a version-controlled manner.

## Migration Architecture

The migration system is built on Alembic, a database migration tool for SQLAlchemy. It provides a way to incrementally update the database schema through version-controlled migration scripts. The system is configured to work with the SQLAlchemy models defined in the application.

Alembic uses a sequential version numbering approach for database schema changes, where each migration is assigned a unique revision identifier. These revisions form a directed acyclic graph (DAG) that represents the history of schema changes, allowing for both linear and branched migration paths.

Key components of the migration architecture:
- **Migration Repository**: A collection of migration scripts managed by Alembic
- **Revision Identifiers**: Unique identifiers for each migration (automatically generated)
- **Branch Labels**: Optional labels for managing parallel development branches
- **Dependencies**: Relationships between migrations to ensure proper execution order

## Directory Structure

- `env.py`: Configuration script for the Alembic environment
- `script.py.mako`: Template for generating new migration scripts
- `versions/`: Directory containing individual migration script files
- `alembic.ini`: Alembic configuration file (located in the project root)

Each migration script in the `versions/` directory follows a naming convention:
```
{revision_id}_{description}.py
```

For example: `e1a47c12a8e9_create_users_table.py`

## Creating Migrations

To create a new migration script, use the following command:

```bash
alembic revision --autogenerate -m "Description of the changes"
```

This will generate a new migration script in the `versions/` directory based on the differences between the current database schema and the SQLAlchemy models defined in the application.

For more complex migrations that cannot be automatically generated, you can create a blank migration script:

```bash
alembic revision -m "Description of the changes"
```

Each migration script contains two main functions:
- `upgrade()`: Contains the changes to apply to the database
- `downgrade()`: Contains the changes to revert the migration

For example:
```python
def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )

def downgrade():
    op.drop_table('users')
```

## Running Migrations

To apply migrations to the database, use the following command:

```bash
alembic upgrade head
```

This will apply all pending migrations to bring the database schema up to the latest version.

To upgrade to a specific version:

```bash
alembic upgrade <revision>
```

To downgrade to a previous version:

```bash
alembic downgrade <revision>
```

To get the current database version:

```bash
alembic current
```

To list all available migrations:

```bash
alembic history
```

For deploying migrations in production environments, it's recommended to use the following approach:

```bash
# Check current version
alembic current

# Run migrations with SQL preview
alembic upgrade head --sql > migration.sql

# Review the SQL file
# Then apply migrations
alembic upgrade head
```

## Best Practices

1. **Atomic Changes**: Each migration should represent a single, atomic change to the database schema.
   - Keep migrations focused on a specific change (e.g., adding a table, modifying a column)
   - Avoid combining unrelated changes in a single migration

2. **Idempotent Operations**: Migrations should be idempotent, meaning they can be run multiple times without causing errors.
   - Use `op.create_table_if_not_exists()` and similar operations when appropriate
   - Add conditional checks for operations that might fail if run multiple times

3. **Backward Compatibility**: Always implement the `downgrade()` function to allow rolling back changes if needed.
   - Test both the upgrade and downgrade paths
   - Ensure data integrity is maintained during rollbacks

4. **Testing**: Test migrations in a development environment before applying them to production.
   - Create a separate test database for validating migrations
   - Include migration testing in the CI/CD pipeline

5. **Data Migrations**: When changing data structures, include data migration steps to preserve existing data.
   - Separate schema changes from data migrations when possible
   - Use SQLAlchemy Core for complex data transformations

6. **Documentation**: Include clear comments in migration scripts explaining the purpose and impact of the changes.
   - Document any manual steps required before or after migration
   - Note any dependencies on other migrations

7. **Version Control**: Commit migration scripts along with the code changes that require them.
   - Never modify an existing migration that has been applied to any environment
   - Create a new migration instead if additional changes are needed

## Integration with Application

The migration system is integrated with the application through the following components:

- `app.db.base`: Defines the SQLAlchemy declarative base and imports all models
- `app.db.session`: Configures the database connection and session management
- `app.db.init_db`: Handles initial database setup and seeding

The application's models are automatically detected by Alembic for generating migration scripts.

To ensure proper detection of models, follow these guidelines:
1. Import all models in `app.db.base`
2. Use SQLAlchemy's declarative base for all models
3. Define foreign key relationships explicitly
4. Use SQLAlchemy's metadata for table definitions

## Environment-Specific Configurations

Different database configurations can be used for different environments (development, staging, production). The database URL is configured in `app.core.config` and is used by both the application and the migration system.

For environment-specific configurations:
1. Set the `SQLALCHEMY_DATABASE_URI` environment variable to the appropriate connection string
2. Override the default configuration in `alembic.ini` for specific environments
3. Use environment variables in `env.py` to customize migration behavior

Example of environment-specific settings in `env.py`:
```python
# Get configuration from environment variables
config_section = os.environ.get("ALEMBIC_CONFIG", "development")
config.set_section_option(config_section, "sqlalchemy.url", get_database_url())
```

## Troubleshooting

Common issues and their solutions:

1. **Migration conflicts**: If multiple developers create migrations simultaneously, conflicts may occur. Resolve by carefully merging the migration scripts or creating a new migration that combines the changes.
   - Coordinate migration creation in the team
   - Consider using branch labels for parallel development

2. **Failed migrations**: If a migration fails, the database may be left in an inconsistent state. Use `alembic downgrade` to revert to the previous version before fixing and retrying.
   - Always have backup procedures in place
   - Test migrations thoroughly before applying to production

3. **Missing dependencies**: Ensure all required models are imported in `app.db.base` to be detected by Alembic.
   - Check the import statements in `app.db.base`
   - Run `alembic check` to verify the environment

4. **Connection issues**: Verify the database connection settings in `app.core.config` and `alembic.ini`.
   - Check database credentials and network connectivity
   - Ensure the database user has sufficient privileges

5. **Autogenerate limitations**: Be aware that Alembic's autogenerate feature has limitations and may not detect all changes.
   - Review autogenerated migrations carefully
   - Add manual operations for complex changes

6. **Performance considerations**: For large databases, some migrations may impact performance.
   - Consider adding indexes before adding foreign keys
   - Use batching for large data migrations
   - Schedule complex migrations during off-peak hours