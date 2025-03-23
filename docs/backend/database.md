# IndiVillage.com Database Architecture

## Introduction

This document provides comprehensive documentation for the database architecture of the IndiVillage.com backend application. It covers the database schema design, data models, relationships, migration procedures, and best practices for database operations. The application uses PostgreSQL as the primary database with SQLAlchemy as the ORM layer.

## Database Configuration

The database configuration is managed through environment variables and the SQLAlchemy ORM. The main configuration is defined in the `src/backend/app/db/session.py` file.

### Connection Setup

Database connections are established using SQLAlchemy's `create_engine` function with connection pooling enabled. The connection string is defined in environment variables and accessed through the application settings.

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URI,
    pool_pre_ping=True,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_recycle=settings.DATABASE_POOL_RECYCLE,
    echo=settings.DATABASE_ECHO
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

### Session Management

Database sessions are managed using SQLAlchemy's `sessionmaker` and provided to API endpoints through FastAPI's dependency injection system. The `get_db` function yields a session that is automatically closed after use.

```python
from fastapi import Depends
from sqlalchemy.orm import Session

def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### Environment-specific Configuration

Different database configurations are used for development, testing, and production environments. In development, SQL echo is enabled for debugging. In production, connection pooling is optimized for performance.

```python
# Development settings
DATABASE_URI=postgresql://postgres:postgres@localhost:5432/indivillage_dev
DATABASE_POOL_SIZE=5
DATABASE_MAX_OVERFLOW=10
DATABASE_POOL_RECYCLE=3600
DATABASE_ECHO=True

# Production settings
DATABASE_URI=postgresql://user:password@host:port/indivillage
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30
DATABASE_POOL_RECYCLE=1800
DATABASE_ECHO=False
```

## Data Models

The application uses SQLAlchemy ORM models to define the database schema. All models inherit from a base model class that provides common fields and functionality.

### Base Model

The `BaseModel` class in `src/backend/app/db/base.py` provides common fields like `created_at` and `updated_at` for all models, as well as utility methods like `to_dict()` for serialization.

```python
from datetime import datetime
from sqlalchemy import Column, DateTime
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.sql import func
import uuid

class CustomBase:
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

Base = declarative_base(cls=CustomBase)
```

### User Model

The `User` model represents users of the system, storing authentication information, contact details, and maintaining relationships with form submissions and file uploads. It includes methods for password management and role-based access control.

```python
from sqlalchemy import Column, String, Boolean, Enum
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.core.security import get_password_hash, verify_password

class UserRole(enum.Enum):
    ADMIN = "admin"
    EDITOR = "editor"
    USER = "user"

class User(Base):
    __tablename__ = "users"
    
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    name = Column(String, nullable=False)
    company = Column(String)
    phone = Column(String)
    country = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    
    form_submissions = relationship("FormSubmission", back_populates="user")
    file_uploads = relationship("FileUpload", back_populates="user")
    
    def set_password(self, password):
        self.hashed_password = get_password_hash(password)
    
    def verify_password(self, password):
        return verify_password(password, self.hashed_password)
    
    def is_admin(self):
        return self.role == UserRole.ADMIN
    
    def is_editor(self):
        return self.role in [UserRole.ADMIN, UserRole.EDITOR]
```

### File Upload Models

The `FileUpload` model tracks uploaded files and their processing status. The `FileAnalysis` model stores the results of file processing. These models support the sample data upload functionality.

```python
from sqlalchemy import Column, String, Integer, ForeignKey, Enum, Text, JSON
from sqlalchemy.orm import relationship
import enum

class FileStatus(enum.Enum):
    PENDING = "pending"
    UPLOADING = "uploading"
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    QUARANTINED = "quarantined"

class FileUpload(Base):
    __tablename__ = "file_uploads"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    filename = Column(String, nullable=False)
    size = Column(Integer, nullable=False)
    mime_type = Column(String, nullable=False)
    status = Column(Enum(FileStatus), default=FileStatus.PENDING, nullable=False)
    storage_path = Column(String, nullable=False)
    processed_at = Column(DateTime)
    
    user = relationship("User", back_populates="file_uploads")
    analysis = relationship("FileAnalysis", back_populates="upload", uselist=False)
    
    @property
    def is_processed(self):
        return self.status == FileStatus.COMPLETED
    
    @property
    def is_failed(self):
        return self.status in [FileStatus.FAILED, FileStatus.QUARANTINED]

class FileAnalysis(Base):
    __tablename__ = "file_analyses"
    
    upload_id = Column(UUID(as_uuid=True), ForeignKey("file_uploads.id"), unique=True, nullable=False)
    summary = Column(Text, nullable=False)
    details_path = Column(String, nullable=False)
    
    upload = relationship("FileUpload", back_populates="analysis")
    
    @property
    def details(self):
        # Load details from storage using details_path
        # Implementation depends on storage solution
        pass
```

### Form Submission Models

The `FormSubmission` model stores form submissions including contact forms, demo requests, and quote requests. The `FormType` enum categorizes different types of forms, and the `FormStatus` enum tracks the processing status.

```python
from sqlalchemy import Column, String, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
import enum

class FormType(enum.Enum):
    CONTACT = "contact"
    DEMO_REQUEST = "demo_request"
    QUOTE_REQUEST = "quote_request"

class FormStatus(enum.Enum):
    SUBMITTED = "submitted"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class FormSubmission(Base):
    __tablename__ = "form_submissions"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    form_type_id = Column(Enum(FormType), nullable=False)
    data = Column(JSON, nullable=False)
    status = Column(Enum(FormStatus), default=FormStatus.SUBMITTED, nullable=False)
    
    user = relationship("User", back_populates="form_submissions")
    services = relationship("Service", secondary="form_service_interest", back_populates="form_submissions")
    
    @property
    def email(self):
        return self.data.get("email")
    
    @property
    def name(self):
        return self.data.get("name") or f"{self.data.get('first_name', '')} {self.data.get('last_name', '')}"
    
    @property
    def company(self):
        return self.data.get("company")
    
    @property
    def phone(self):
        return self.data.get("phone")

# Association table for many-to-many relationship between FormSubmission and Service
form_service_interest = Table(
    "form_service_interest",
    Base.metadata,
    Column("form_id", UUID(as_uuid=True), ForeignKey("form_submissions.id"), primary_key=True),
    Column("service_id", UUID(as_uuid=True), ForeignKey("services.id"), primary_key=True)
)
```

### Service Models

The `Service` model represents AI service offerings, and the `ServiceFeature` model stores features of each service. These models support the AI-as-a-Service portfolio showcase.

```python
from sqlalchemy import Column, String, Text, Integer, ForeignKey
from sqlalchemy.orm import relationship

class Service(Base):
    __tablename__ = "services"
    
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text, nullable=False)
    icon = Column(String, nullable=False)
    order = Column(Integer, nullable=False)
    
    features = relationship("ServiceFeature", back_populates="service", cascade="all, delete-orphan")
    case_studies = relationship("CaseStudy", secondary="service_case_study", back_populates="services")
    form_submissions = relationship("FormSubmission", secondary="form_service_interest", back_populates="services")

class ServiceFeature(Base):
    __tablename__ = "service_features"
    
    service_id = Column(UUID(as_uuid=True), ForeignKey("services.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    order = Column(Integer, nullable=False)
    
    service = relationship("Service", back_populates="features")
```

### Case Study Models

The `CaseStudy` model represents client success stories, with related `CaseStudyResult` and `Industry` models. These models support the case studies and success stories feature.

```python
from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.orm import relationship

class Industry(Base):
    __tablename__ = "industries"
    
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)
    
    case_studies = relationship("CaseStudy", back_populates="industry")

class CaseStudy(Base):
    __tablename__ = "case_studies"
    
    title = Column(String, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)
    client = Column(String, nullable=False)
    challenge = Column(Text, nullable=False)
    solution = Column(Text, nullable=False)
    industry_id = Column(UUID(as_uuid=True), ForeignKey("industries.id"), nullable=False)
    
    industry = relationship("Industry", back_populates="case_studies")
    results = relationship("CaseStudyResult", back_populates="case_study", cascade="all, delete-orphan")
    services = relationship("Service", secondary="service_case_study", back_populates="case_studies")

class CaseStudyResult(Base):
    __tablename__ = "case_study_results"
    
    case_study_id = Column(UUID(as_uuid=True), ForeignKey("case_studies.id"), nullable=False)
    metric = Column(String, nullable=False)
    value = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    
    case_study = relationship("CaseStudy", back_populates="results")

# Association table for many-to-many relationship between Service and CaseStudy
service_case_study = Table(
    "service_case_study",
    Base.metadata,
    Column("service_id", UUID(as_uuid=True), ForeignKey("services.id"), primary_key=True),
    Column("case_study_id", UUID(as_uuid=True), ForeignKey("case_studies.id"), primary_key=True)
)
```

### Impact Story Models

The `ImpactStory` model represents social impact narratives, with related `ImpactMetric` and `Location` models. These models support the social impact storytelling feature.

```python
from sqlalchemy import Column, String, Text, ForeignKey, Numeric
from sqlalchemy.orm import relationship

class Location(Base):
    __tablename__ = "locations"
    
    name = Column(String, nullable=False)
    region = Column(String, nullable=False)
    country = Column(String, nullable=False)
    
    impact_stories = relationship("ImpactStory", back_populates="location")

class ImpactStory(Base):
    __tablename__ = "impact_stories"
    
    title = Column(String, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)
    story = Column(Text, nullable=False)
    beneficiaries = Column(String, nullable=False)
    location_id = Column(UUID(as_uuid=True), ForeignKey("locations.id"), nullable=False)
    
    location = relationship("Location", back_populates="impact_stories")
    metrics = relationship("ImpactMetric", back_populates="story", cascade="all, delete-orphan")

class ImpactMetric(Base):
    __tablename__ = "impact_metrics"
    
    story_id = Column(UUID(as_uuid=True), ForeignKey("impact_stories.id"), nullable=False)
    metric_name = Column(String, nullable=False)
    value = Column(Numeric, nullable=False)
    unit = Column(String, nullable=False)
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    
    story = relationship("ImpactStory", back_populates="metrics")
```

## Entity Relationships

The database schema includes several entity relationships that define how data is connected across different models.

### One-to-Many Relationships

- User to FileUpload: One user can have many file uploads
- User to FormSubmission: One user can have many form submissions
- Service to ServiceFeature: One service can have many features
- CaseStudy to CaseStudyResult: One case study can have many results
- Industry to CaseStudy: One industry can have many case studies
- ImpactStory to ImpactMetric: One impact story can have many metrics
- Location to ImpactStory: One location can have many impact stories

These relationships are implemented in SQLAlchemy using the `relationship` function with the `back_populates` parameter, and foreign keys in the child tables.

### Many-to-Many Relationships

- Service to CaseStudy: Services can be featured in multiple case studies, and case studies can involve multiple services
- FormSubmission to Service: Form submissions can indicate interest in multiple services

Many-to-many relationships are implemented using association tables with primary key columns referencing both related tables.

### One-to-One Relationships

- FileUpload to FileAnalysis: Each file upload has one analysis result

One-to-one relationships are implemented using a foreign key with a unique constraint, and a `uselist=False` parameter in the relationship definition.

## Database Migrations

Database migrations are managed using Alembic, which is integrated with SQLAlchemy. Migrations are stored in the `src/backend/migrations` directory.

### Migration Workflow

1. Generate a new migration: `alembic revision --autogenerate -m "description"`
2. Review and edit the generated migration file
3. Apply the migration: `alembic upgrade head`
4. Rollback if needed: `alembic downgrade -1`

When generating migrations, Alembic compares the current database state with the models defined in the code and creates migration scripts that include the necessary changes.

### Migration Best Practices

- Always review autogenerated migrations before applying them
- Include both upgrade and downgrade operations
- Test migrations on a staging environment before production
- Keep migrations small and focused on specific changes
- Include data migrations when schema changes affect existing data

Example migration file:

```python
"""create users table

Revision ID: e1fb32e1c3f8
Revises: 
Create Date: 2023-05-01 12:34:56.789012

"""
from alembic import op
import sqlalchemy as sa
import uuid

# revision identifiers, used by Alembic.
revision = 'e1fb32e1c3f8'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('users',
        sa.Column('id', sa.UUID(), nullable=False, default=uuid.uuid4),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('company', sa.String(), nullable=True),
        sa.Column('phone', sa.String(), nullable=True),
        sa.Column('country', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('role', sa.Enum('admin', 'editor', 'user', name='userrole'), nullable=False, default='user'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), onupdate=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

def downgrade():
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
```

## Database Initialization

The database is initialized during application startup using the `init_db` function in `src/backend/app/db/init_db.py`. This function creates tables and sets up initial data.

### Table Creation

Tables are created based on the SQLAlchemy models using `Base.metadata.create_all(engine)`. In production, this is typically handled by migrations instead.

```python
def create_tables(engine):
    Base.metadata.create_all(bind=engine)
```

### Initial Data Setup

The initialization process creates an admin user and core service categories if they don't already exist. This ensures the application has the minimum required data to function.

```python
def init_db(db: Session) -> None:
    # Create admin user if it doesn't exist
    user = db.query(User).filter(User.email == settings.FIRST_ADMIN_EMAIL).first()
    if not user:
        user = User(
            email=settings.FIRST_ADMIN_EMAIL,
            name="Admin User",
            role=UserRole.ADMIN,
            is_active=True
        )
        user.set_password(settings.FIRST_ADMIN_PASSWORD)
        db.add(user)
        db.commit()
        db.refresh(user)
    
    # Create core service categories if they don't exist
    core_services = [
        {"name": "Data Collection", "slug": "data-collection", "order": 1},
        {"name": "Data Preparation", "slug": "data-preparation", "order": 2},
        {"name": "AI Model Development", "slug": "ai-model-development", "order": 3},
        {"name": "Human-in-the-Loop", "slug": "human-in-the-loop", "order": 4}
    ]
    
    for service_data in core_services:
        service = db.query(Service).filter(Service.slug == service_data["slug"]).first()
        if not service:
            service = Service(
                name=service_data["name"],
                slug=service_data["slug"],
                description=f"{service_data['name']} services",
                icon=service_data["slug"],
                order=service_data["order"]
            )
            db.add(service)
    
    db.commit()
```

### Development Data

In development environments, sample data is populated using the `seed_database` function from `src/backend/scripts/seed_data.py`. This includes sample users, file uploads, form submissions, case studies, and impact stories.

```python
def seed_database(db: Session) -> None:
    # Only run in development environment
    if settings.ENVIRONMENT != "development":
        return
    
    # Create sample users
    for i in range(5):
        user = db.query(User).filter(User.email == f"user{i}@example.com").first()
        if not user:
            user = User(
                email=f"user{i}@example.com",
                name=f"User {i}",
                company="Example Corp",
                role=UserRole.USER,
                is_active=True
            )
            user.set_password("password")
            db.add(user)
    
    # Create sample industries
    industries = ["Technology", "Healthcare", "Retail", "Finance", "Manufacturing"]
    for industry_name in industries:
        industry = db.query(Industry).filter(Industry.name == industry_name).first()
        if not industry:
            industry = Industry(
                name=industry_name,
                slug=industry_name.lower()
            )
            db.add(industry)
    
    # Create sample locations
    locations = [
        {"name": "Ramanagara", "region": "Karnataka", "country": "India"},
        {"name": "Yemmiganur", "region": "Andhra Pradesh", "country": "India"}
    ]
    for location_data in locations:
        location = db.query(Location).filter(Location.name == location_data["name"]).first()
        if not location:
            location = Location(**location_data)
            db.add(location)
    
    db.commit()
    
    # Add more sample data (case studies, impact stories, etc.)
    # ...
```

## Query Patterns

The application uses several common query patterns for efficient data access.

### Repository Pattern

Data access is encapsulated in service modules that follow the repository pattern. These services provide methods for CRUD operations and more complex queries.

```python
class ServiceRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(self, skip: int = 0, limit: int = 100):
        return self.db.query(Service).offset(skip).limit(limit).all()
    
    def get_by_id(self, service_id: UUID):
        return self.db.query(Service).filter(Service.id == service_id).first()
    
    def get_by_slug(self, slug: str):
        return self.db.query(Service).filter(Service.slug == slug).first()
    
    def create(self, service_data: dict):
        service = Service(**service_data)
        self.db.add(service)
        self.db.commit()
        self.db.refresh(service)
        return service
    
    def update(self, service_id: UUID, service_data: dict):
        service = self.get_by_id(service_id)
        if service:
            for key, value in service_data.items():
                setattr(service, key, value)
            self.db.commit()
            self.db.refresh(service)
        return service
    
    def delete(self, service_id: UUID):
        service = self.get_by_id(service_id)
        if service:
            self.db.delete(service)
            self.db.commit()
            return True
        return False
```

### Eager Loading

Relationships are eagerly loaded when needed to avoid the N+1 query problem. This is done using SQLAlchemy's `joinedload` and `selectinload` options.

```python
def get_service_with_features(db: Session, service_id: UUID):
    return db.query(Service)\
        .options(joinedload(Service.features))\
        .filter(Service.id == service_id)\
        .first()

def get_case_study_with_relationships(db: Session, case_study_id: UUID):
    return db.query(CaseStudy)\
        .options(
            joinedload(CaseStudy.industry),
            selectinload(CaseStudy.results),
            selectinload(CaseStudy.services)
        )\
        .filter(CaseStudy.id == case_study_id)\
        .first()
```

### Pagination

List endpoints use pagination to limit the amount of data returned in a single request. This is implemented using SQLAlchemy's `limit` and `offset` methods.

```python
def get_paginated_services(db: Session, skip: int = 0, limit: int = 10):
    total = db.query(Service).count()
    services = db.query(Service).order_by(Service.order).offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "items": services,
        "skip": skip,
        "limit": limit
    }
```

### Filtering and Sorting

List endpoints support filtering and sorting based on query parameters. This is implemented using SQLAlchemy's filter methods and order_by clause.

```python
def get_filtered_case_studies(db: Session, industry_id: Optional[UUID] = None, 
                             service_id: Optional[UUID] = None, 
                             skip: int = 0, limit: int = 10):
    query = db.query(CaseStudy)
    
    if industry_id:
        query = query.filter(CaseStudy.industry_id == industry_id)
    
    if service_id:
        query = query.join(service_case_study).filter(service_case_study.c.service_id == service_id)
    
    total = query.count()
    case_studies = query.order_by(CaseStudy.created_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "items": case_studies,
        "skip": skip,
        "limit": limit
    }
```

## Data Validation

Data validation is performed at multiple levels to ensure data integrity.

### Schema Validation

API request and response schemas are defined using Pydantic models, which provide automatic validation of incoming and outgoing data.

```python
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from uuid import UUID

class ServiceCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    slug: str = Field(..., min_length=1, max_length=100, regex=r'^[a-z0-9-]+$')
    description: str = Field(..., min_length=10)
    icon: str = Field(..., min_length=1, max_length=50)
    order: int = Field(..., ge=0)
    
    @validator('slug')
    def slug_must_be_unique(cls, v, values, **kwargs):
        # This validation is performed at the API level
        # by checking the database for existing slugs
        return v

class ServiceFeatureCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=10)
    order: int = Field(..., ge=0)
```

### Database Constraints

Database constraints such as NOT NULL, UNIQUE, and FOREIGN KEY are used to enforce data integrity at the database level.

```python
class Service(Base):
    __tablename__ = "services"
    
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text, nullable=False)
    icon = Column(String, nullable=False)
    order = Column(Integer, nullable=False)
```

### Application Validation

Additional validation logic is implemented in service methods to enforce business rules that can't be expressed through schema or database constraints.

```python
def create_service(db: Session, service_data: ServiceCreate):
    # Check if slug already exists
    existing_service = db.query(Service).filter(Service.slug == service_data.slug).first()
    if existing_service:
        raise ValueError(f"Service with slug '{service_data.slug}' already exists")
    
    # Check if icon is valid
    valid_icons = ["data-collection", "data-preparation", "ai-model", "hitl"]
    if service_data.icon not in valid_icons:
        raise ValueError(f"Invalid icon name. Must be one of: {', '.join(valid_icons)}")
    
    # Create the service
    service = Service(**service_data.dict())
    db.add(service)
    db.commit()
    db.refresh(service)
    return service
```

## Performance Optimization

Several techniques are used to optimize database performance.

### Indexing Strategy

Indexes are defined on frequently queried columns, including foreign keys, unique constraints, and common filter fields. Composite indexes are used for queries that filter on multiple columns.

```python
# Index on email for User
email = Column(String, unique=True, index=True, nullable=False)

# Index on slug for Service
slug = Column(String, unique=True, index=True, nullable=False)

# Composite index on FormSubmission
__table_args__ = (
    Index('ix_form_submissions_form_type_status', 'form_type_id', 'status'),
)
```

The indexing strategy is based on query patterns identified during development and testing:

- Primary keys are automatically indexed
- Foreign keys are indexed to optimize joins
- Unique constraints create indexes
- Columns used in WHERE clauses are indexed
- Columns used for sorting are indexed
- Composite indexes are created for common query combinations

### Connection Pooling

SQLAlchemy's connection pooling is configured with appropriate pool size, max overflow, and connection recycling to optimize database connection usage.

```python
engine = create_engine(
    settings.DATABASE_URI,
    pool_pre_ping=True,  # Verify connections before use
    pool_size=settings.DATABASE_POOL_SIZE,  # Base pool size
    max_overflow=settings.DATABASE_MAX_OVERFLOW,  # Additional connections when pool is depleted
    pool_recycle=settings.DATABASE_POOL_RECYCLE,  # Recycle connections after this many seconds
    pool_timeout=settings.DATABASE_POOL_TIMEOUT  # Timeout waiting for a connection
)
```

The pool configuration is adjusted based on the environment and expected load:

- Development: Smaller pool (5 connections, 10 overflow)
- Testing: Minimal pool (3 connections, 5 overflow)
- Production: Larger pool (20 connections, 30 overflow)

### Query Optimization

Complex queries are optimized using SQLAlchemy's query options, such as selecting only needed columns, using appropriate join types, and applying filters early in the query.

```python
# Select only needed columns
users = db.query(User.id, User.email, User.name).all()

# Use appropriate join type (LEFT OUTER JOIN)
case_studies = db.query(CaseStudy).outerjoin(CaseStudy.results).all()

# Apply filters early
services = db.query(Service).filter(Service.active == True).options(
    selectinload(Service.features.and_(ServiceFeature.active == True))
).all()
```

Optimization techniques include:

- Filtering early to reduce the result set
- Using appropriate join types (INNER, LEFT, etc.)
- Selecting only needed columns
- Using subqueries for complex queries
- Optimizing aggregations

### Caching

Frequently accessed, relatively static data is cached using Redis to reduce database load. This includes service listings, case studies, and impact stories.

```python
from app.core.cache import cache

@cache.cached(timeout=3600, key_prefix="all_services")
def get_all_services(db: Session):
    return db.query(Service).all()

@cache.cached(timeout=3600, key_prefix="service_by_slug_{0}")
def get_service_by_slug(db: Session, slug: str):
    return db.query(Service).filter(Service.slug == slug).first()
```

Caching is implemented using the following approach:

- Redis is used as the cache backend
- Cache keys are prefixed with the function name and parameters
- Cache timeouts are set based on data volatility
- Cache invalidation occurs when data is updated
- Cache warmup is performed during application startup

## Data Security

The database implements several security measures to protect sensitive data.

### Password Hashing

User passwords are hashed using bcrypt before storage. The hashing is performed in the User model's `set_password` method.

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

class User(Base):
    # ...
    
    def set_password(self, password: str):
        self.hashed_password = get_password_hash(password)
    
    def verify_password(self, password: str) -> bool:
        return verify_password(password, self.hashed_password)
```

### Data Encryption

Sensitive data is encrypted at rest using PostgreSQL's encryption features. Transport encryption is provided by TLS for all database connections.

```python
# Enable TLS for database connection
engine = create_engine(
    settings.DATABASE_URI,
    connect_args={"sslmode": "require"} if settings.DATABASE_SSL else {}
)
```

For field-level encryption, a custom type is defined:

```python
from sqlalchemy.types import TypeDecorator, String
from cryptography.fernet import Fernet

class EncryptedString(TypeDecorator):
    impl = String
    
    def __init__(self, *args, **kwargs):
        super(EncryptedString, self).__init__(*args, **kwargs)
        self.cipher = Fernet(settings.ENCRYPTION_KEY.encode())
    
    def process_bind_param(self, value, dialect):
        if value is not None:
            value = self.cipher.encrypt(value.encode()).decode()
        return value
    
    def process_result_value(self, value, dialect):
        if value is not None:
            value = self.cipher.decrypt(value.encode()).decode()
        return value

# Usage in models
class User(Base):
    # ...
    sensitive_data = Column(EncryptedString)
```

### Access Control

Database access is restricted through role-based permissions. Application services access the database using a service account with limited privileges.

```python
# Example of role-based access in the API layer
def get_current_active_user(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def get_current_admin_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    if not current_user.is_admin():
        raise HTTPException(
            status_code=403,
            detail="The user doesn't have enough privileges"
        )
    return current_user
```

### Audit Logging

Database operations on sensitive data are logged for audit purposes. This includes user creation, role changes, and access to personal information.

```python
class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    action = Column(String, nullable=False)
    entity_type = Column(String, nullable=False)
    entity_id = Column(UUID(as_uuid=True), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    changes = Column(JSON, nullable=True)
    ip_address = Column(String, nullable=True)

def log_audit_event(db: Session, action: str, entity_type: str, entity_id: UUID, 
                   user_id: Optional[UUID], changes: Optional[dict], ip_address: Optional[str]):
    log = AuditLog(
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        user_id=user_id,
        changes=changes,
        ip_address=ip_address
    )
    db.add(log)
    db.commit()
```

## Backup and Recovery

The database has a comprehensive backup and recovery strategy.

### Backup Schedule

- Full backups: Daily
- Incremental backups: Hourly
- Transaction logs: Continuous
- Retention period: 30 days for daily backups, 7 days for hourly backups

Backups are automated using AWS RDS backup features for managed databases, or custom scripts for self-hosted databases.

```python
# Example backup script (conceptual)
import subprocess
from datetime import datetime

def create_database_backup():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"/backups/indivillage_{timestamp}.sql"
    
    # Create backup using pg_dump
    subprocess.run([
        "pg_dump",
        "-h", DB_HOST,
        "-U", DB_USER,
        "-d", DB_NAME,
        "-f", backup_file,
        "--compress=9"
    ], check=True)
    
    # Upload to S3 for long-term storage
    subprocess.run([
        "aws", "s3", "cp",
        backup_file,
        f"s3://indivillage-backups/database/{timestamp}.sql.gz"
    ], check=True)
```

### Recovery Procedures

Recovery procedures are documented for different scenarios:

- Point-in-time recovery for data corruption
- Full database recovery for catastrophic failure
- Single table recovery for targeted issues

```python
# Example recovery script (conceptual)
import subprocess
from datetime import datetime

def restore_database_from_backup(backup_file):
    # Create a temporary database for restoration
    temp_db = f"restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    subprocess.run([
        "createdb",
        "-h", DB_HOST,
        "-U", DB_USER,
        temp_db
    ], check=True)
    
    # Restore the backup to the temporary database
    subprocess.run([
        "pg_restore",
        "-h", DB_HOST,
        "-U", DB_USER,
        "-d", temp_db,
        backup_file
    ], check=True)
    
    # Verify the restoration
    # ... verification process ...
    
    # If verified, rename databases to switch to the restored version
    # ... switching process ...
```

### Backup Verification

Backups are regularly verified by restoring to a test environment and validating data integrity. This is performed weekly for a randomly selected backup.

```python
# Example verification script (conceptual)
import subprocess
import random
import os

def verify_random_backup():
    # List available backups
    result = subprocess.run([
        "aws", "s3", "ls",
        "s3://indivillage-backups/database/"
    ], capture_output=True, text=True, check=True)
    
    # Select a random backup
    backups = [line.split()[-1] for line in result.stdout.splitlines()]
    if not backups:
        return "No backups found"
    
    random_backup = random.choice(backups)
    local_path = f"/tmp/{random_backup}"
    
    # Download the backup
    subprocess.run([
        "aws", "s3", "cp",
        f"s3://indivillage-backups/database/{random_backup}",
        local_path
    ], check=True)
    
    # Restore to verification database
    # ... restoration process ...
    
    # Run integrity checks
    # ... verification process ...
    
    # Clean up
    os.remove(local_path)
```

## Compliance and Data Retention

The database implements compliance requirements for data protection and retention.

### Data Retention Policies

- User data: Retained for 24 months after last activity
- File uploads: Retained for 12 months
- Form submissions: Retained for 24 months
- Audit logs: Retained for 7 years

These policies are implemented through automated data archival and purging processes.

```python
# Example data retention job (conceptual)
from datetime import datetime, timedelta
from sqlalchemy import func

def process_data_retention(db: Session):
    now = datetime.utcnow()
    
    # Archive and anonymize user data older than 24 months
    inactive_threshold = now - timedelta(days=730)
    inactive_users = db.query(User).filter(
        User.updated_at < inactive_threshold,
        User.is_active == True
    ).all()
    
    for user in inactive_users:
        # Archive user data
        archive_user_data(user)
        
        # Anonymize user
        user.email = f"anonymized_{user.id}@example.com"
        user.name = "Anonymized User"
        user.phone = None
        user.is_active = False
    
    db.commit()
    
    # Delete file uploads older than 12 months
    upload_threshold = now - timedelta(days=365)
    old_uploads = db.query(FileUpload).filter(
        FileUpload.created_at < upload_threshold
    ).all()
    
    for upload in old_uploads:
        # Delete file from storage
        delete_file_from_storage(upload.storage_path)
        
        # Delete database record
        db.delete(upload)
    
    db.commit()
```

### Data Anonymization

Personal data is anonymized when retention periods expire, rather than being completely deleted. This preserves analytical data while protecting privacy.

```python
def anonymize_user_data(db: Session, user_id: UUID):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return False
    
    # Generate anonymized values
    anonymized_email = f"anonymized_{user.id}@example.com"
    anonymized_name = "Anonymized User"
    
    # Update user record
    user.email = anonymized_email
    user.name = anonymized_name
    user.phone = None
    user.company = None
    user.country = None
    user.hashed_password = "ANONYMIZED"
    user.is_active = False
    
    # Log the anonymization
    log_audit_event(db, "ANONYMIZE", "user", user.id, None, 
                    {"reason": "Data retention policy"}, None)
    
    db.commit()
    return True
```

### GDPR Compliance

The database supports GDPR requirements including:

- Right to access: API endpoints to retrieve all user data
- Right to be forgotten: Procedures to delete or anonymize user data
- Data portability: Export functionality for user data

```python
def export_user_data(db: Session, user_id: UUID):
    # Get user and related data
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None
    
    # Get all form submissions
    form_submissions = db.query(FormSubmission).filter(
        FormSubmission.user_id == user_id
    ).all()
    
    # Get all file uploads
    file_uploads = db.query(FileUpload).filter(
        FileUpload.user_id == user_id
    ).all()
    
    # Compile the data
    user_data = {
        "user": user.to_dict(),
        "form_submissions": [fs.to_dict() for fs in form_submissions],
        "file_uploads": [fu.to_dict() for fu in file_uploads]
    }
    
    # Log the export
    log_audit_event(db, "EXPORT", "user", user.id, None, 
                    {"reason": "GDPR data request"}, None)
    
    return user_data
```

## Troubleshooting

Common database issues and their solutions.

### Connection Issues

- Check database service status
- Verify connection string and credentials
- Check network connectivity and firewall rules
- Inspect connection pool metrics for exhaustion

```python
def check_database_connection():
    try:
        # Try to create a database connection
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        return {"status": "connected"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
```

### Performance Problems

- Identify slow queries using database logs
- Analyze query execution plans
- Check for missing indexes
- Monitor database resource usage

```python
def analyze_slow_query(query_text):
    db = SessionLocal()
    result = db.execute(f"EXPLAIN ANALYZE {query_text}")
    execution_plan = [row[0] for row in result]
    db.close()
    return execution_plan
```

### Migration Failures

- Review migration logs for errors
- Check for conflicts with existing schema
- Verify database permissions
- Test migrations in development environment

```python
def verify_migration(migration_script):
    # Create a temporary database
    temp_db = f"migration_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    try:
        # Create database
        subprocess.run([
            "createdb",
            "-h", DB_HOST,
            "-U", DB_USER,
            temp_db
        ], check=True)
        
        # Apply migrations up to current state
        subprocess.run([
            "alembic", "upgrade", "head"
        ], env={"DATABASE_URI": f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{temp_db}"}, check=True)
        
        # Apply the migration being tested
        subprocess.run([
            "alembic", "upgrade", migration_script
        ], env={"DATABASE_URI": f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{temp_db}"}, check=True)
        
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        # Drop the temporary database
        subprocess.run([
            "dropdb",
            "-h", DB_HOST,
            "-U", DB_USER,
            temp_db
        ], check=True)
```

## Best Practices

Recommended practices for working with the database.

### Development Practices

- Use migrations for all schema changes
- Write tests for database operations
- Use transactions for multi-step operations
- Keep database logic in service layers, not API endpoints

```python
# Example of transaction usage
def transfer_data(db: Session, source_id: UUID, target_id: UUID):
    try:
        # Start transaction
        source = db.query(Source).filter(Source.id == source_id).with_for_update().first()
        target = db.query(Target).filter(Target.id == target_id).with_for_update().first()
        
        if not source or not target:
            raise ValueError("Source or target not found")
        
        # Perform transfer
        target.value += source.value
        source.value = 0
        
        # Commit transaction
        db.commit()
        return True
    except Exception as e:
        # Rollback on error
        db.rollback()
        raise e
```

### Query Optimization

- Select only needed columns
- Use appropriate join types
- Apply filters early in queries
- Use pagination for large result sets
- Monitor and optimize slow queries

```python
# Bad practice: selecting all columns, no filtering
bad_query = db.query(User).all()

# Good practice: selecting specific columns, applying filters
good_query = db.query(User.id, User.email, User.name)\
    .filter(User.is_active == True)\
    .order_by(User.name)\
    .limit(100)\
    .all()
```

### Schema Evolution

- Make additive changes when possible
- Plan for backward compatibility
- Use database migrations for all schema changes
- Document schema changes in migration descriptions

```python
# Example of backward compatible schema evolution
"""add user preferences column

Revision ID: a1b2c3d4e5f6
Revises: e1fb32e1c3f8
Create Date: 2023-05-15 12:34:56.789012

"""
from alembic import op
import sqlalchemy as sa
import json

# revision identifiers
revision = 'a1b2c3d4e5f6'
down_revision = 'e1fb32e1c3f8'
branch_labels = None
depends_on = None

def upgrade():
    # Add nullable column with default value
    op.add_column('users', sa.Column('preferences', sa.JSON(), nullable=True))
    
    # Set default preferences for existing users
    default_preferences = json.dumps({"notifications": True, "theme": "light"})
    op.execute(f"UPDATE users SET preferences = '{default_preferences}'::jsonb")
    
    # Make column non-nullable after setting defaults
    op.alter_column('users', 'preferences', nullable=False)

def downgrade():
    op.drop_column('users', 'preferences')
```
```

## Advanced Topics

### 1. Database Partitioning

For large tables, partitioning improves query performance and manageability:

```sql
-- Example of table partitioning for audit logs
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY,
    action VARCHAR NOT NULL,
    entity_type VARCHAR NOT NULL,
    entity_id UUID NOT NULL,
    user_id UUID,
    changes JSONB,
    ip_address VARCHAR,
    created_at TIMESTAMP NOT NULL
) PARTITION BY RANGE (created_at);

-- Create partitions by month
CREATE TABLE audit_logs_y2023m01 PARTITION OF audit_logs
    FOR VALUES FROM ('2023-01-01') TO ('2023-02-01');
CREATE TABLE audit_logs_y2023m02 PARTITION OF audit_logs
    FOR VALUES FROM ('2023-02-01') TO ('2023-03-01');
-- Additional partitions...
```

### 2. Connection Pooling Tuning

```python
# Connection pooling configuration with detailed parameters
engine = create_engine(
    settings.DATABASE_URI,
    pool_pre_ping=True,          # Verify connections before use
    pool_size=20,                # Base pool size
    max_overflow=30,             # Additional connections when pool is exhausted
    pool_recycle=1800,           # Recycle connections after 30 minutes
    pool_timeout=30,             # Timeout waiting for a connection (seconds)
    pool_use_lifo=True,          # Last In, First Out - better for burst traffic
    echo_pool=settings.DEBUG     # Log pool events in debug mode
)
```

### 3. Data JSON Querying

```python
# Example of querying JSON data in PostgreSQL
def find_users_with_notification_preference(db: Session, notification_type: str, enabled: bool):
    return db.query(User).filter(
        User.preferences[notification_type].astext.cast(Boolean) == enabled
    ).all()
```

### 4. Database Monitoring

```python
# Example database monitoring query
def get_database_metrics(db: Session):
    # Table sizes
    table_sizes = db.execute("""
        SELECT
            table_name,
            pg_size_pretty(pg_total_relation_size(quote_ident(table_name))) as total_size,
            pg_size_pretty(pg_relation_size(quote_ident(table_name))) as table_size,
            pg_size_pretty(pg_total_relation_size(quote_ident(table_name)) - 
                          pg_relation_size(quote_ident(table_name))) as index_size
        FROM
            information_schema.tables
        WHERE
            table_schema = 'public'
        ORDER BY
            pg_total_relation_size(quote_ident(table_name)) DESC
        LIMIT 10
    """).fetchall()
    
    # Index usage
    index_usage = db.execute("""
        SELECT
            relname as table_name,
            indexrelname as index_name,
            idx_scan as index_scans,
            idx_tup_read as tuples_read,
            idx_tup_fetch as tuples_fetched
        FROM
            pg_stat_all_indexes
        WHERE
            schemaname = 'public'
        ORDER BY
            idx_scan DESC
        LIMIT 10
    """).fetchall()
    
    # Active connections
    connections = db.execute("""
        SELECT
            count(*) as active_connections,
            state,
            waiting
        FROM
            pg_stat_activity
        GROUP BY
            state, waiting
    """).fetchall()
    
    return {
        "table_sizes": table_sizes,
        "index_usage": index_usage,
        "connections": connections
    }
```

### 5. Database Replication

For high availability, the IndiVillage database uses PostgreSQL streaming replication:

```
# postgresql.conf (primary)
wal_level = replica
max_wal_senders = 10
wal_keep_segments = 32

# postgresql.conf (replica)
primary_conninfo = 'host=primary port=5432 user=replicator password=secret'
hot_standby = on
```

This setup ensures continuous data replication with minimal performance impact while providing failover capability.