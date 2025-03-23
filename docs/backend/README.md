# IndiVillage.com Backend Documentation

## Table of Contents
- [Introduction](#introduction)
- [Architecture Overview](#architecture-overview)
- [Project Structure](#project-structure)
- [Key Features](#key-features)
- [API Documentation](#api-documentation)
- [Database Models](#database-models)
- [Service Components](#service-components)
- [Integration Components](#integration-components)
- [Security Features](#security-features)
- [Development Guidelines](#development-guidelines)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)
- [Additional Resources](#additional-resources)

## Introduction

This documentation provides a comprehensive guide to the IndiVillage.com backend system, which powers the AI-as-a-service website. The backend is built with Python using FastAPI framework and provides APIs for content delivery, form submissions, file uploads, and integrations with external systems.

## Architecture Overview

The backend follows a modular service-oriented architecture with clear separation of concerns. It is designed to be scalable, secure, and maintainable.

### Key Components

- **API Layer**: FastAPI-based REST API endpoints
- **Service Layer**: Business logic implementation
- **Data Access Layer**: Database models and queries
- **Integration Layer**: External system connections (CRM, Email, Storage)
- **Security Layer**: Input validation, authentication, and authorization
- **Monitoring Layer**: Logging, metrics, and observability

```
┌───────────────────┐      ┌───────────────────┐      ┌───────────────────┐
│                   │      │                   │      │                   │
│   Clients         │      │   API Layer       │      │   Service Layer   │
│   - Web Frontend  ├─────►│   - Endpoints     ├─────►│   - Business Logic│
│   - Mobile App    │      │   - Validation    │      │   - Processing    │
│                   │      │   - Routing       │      │                   │
└───────────────────┘      └─────────┬─────────┘      └─────────┬─────────┘
                                     │                          │
                           ┌─────────▼─────────┐      ┌─────────▼─────────┐
                           │                   │      │                   │
                           │   Security Layer  │      │   Data Access     │
                           │   - Authentication│      │   - Models        │
                           │   - Authorization │      │   - Repositories  │
                           │                   │      │                   │
                           └─────────┬─────────┘      └─────────┬─────────┘
                                     │                          │
                           ┌─────────▼─────────┐      ┌─────────▼─────────┐
                           │                   │      │                   │
                           │   Integration     │      │   Database        │
                           │   - External APIs │      │   - PostgreSQL    │
                           │   - Third-parties │      │   - Redis Cache   │
                           │                   │      │                   │
                           └───────────────────┘      └───────────────────┘
```

## Project Structure

The backend code is organized in a modular structure following domain-driven design principles:

```
app/                        # Main application package
├── api/                    # API endpoints and route definitions
│   └── v1/                 # API version 1 implementation
│       ├── endpoints/      # API endpoint handlers
│       ├── models/         # Database models
│       └── schemas/        # Pydantic schemas for validation
├── core/                   # Core application components
├── db/                     # Database configuration and migrations
├── services/               # Business logic services
├── integrations/           # External system integrations
├── security/               # Security-related components
├── utils/                  # Utility functions
├── templates/              # Email templates
├── cache/                  # Caching mechanisms
├── monitoring/             # Monitoring and observability
├── queue/                  # Asynchronous task processing
├── middlewares/            # HTTP middleware components
└── main.py                 # Application entry point
tests/                      # Test suite
```

## Key Features

### Form Submission Processing

Handles contact forms, demo requests, and quote requests with validation, storage, email notifications, and CRM integration.

**Key Components:**
- `app/api/v1/endpoints/contact.py`
- `app/api/v1/endpoints/demo_request.py`
- `app/api/v1/endpoints/quote_request.py`
- `app/services/form_processing_service.py`
- `app/integrations/hubspot.py`

### File Upload and Processing

Secure file upload system with validation, virus scanning, and data analysis for sample datasets.

**Key Components:**
- `app/api/v1/endpoints/uploads.py`
- `app/services/file_upload_service.py`
- `app/services/file_processing_service.py`
- `app/security/file_scanner.py`
- `app/integrations/aws_s3.py`

### Content Delivery

API endpoints for delivering website content including services, case studies, and impact stories.

**Key Components:**
- `app/api/v1/endpoints/services.py`
- `app/api/v1/endpoints/case_studies.py`
- `app/api/v1/endpoints/impact_stories.py`
- `app/services/content_service.py`
- `app/integrations/contentful.py`

### Security Features

Comprehensive security measures including input validation, CAPTCHA verification, rate limiting, and secure file handling.

**Key Components:**
- `app/security/input_validation.py`
- `app/security/captcha.py`
- `app/security/rate_limiting.py`
- `app/security/file_scanner.py`
- `app/middlewares/security_middleware.py`

### External Integrations

Integrations with external systems including HubSpot CRM, Contentful CMS, AWS S3, and SendGrid.

**Key Components:**
- `app/integrations/hubspot.py`
- `app/integrations/contentful.py`
- `app/integrations/aws_s3.py`
- `app/integrations/sendgrid.py`
- `app/integrations/google_analytics.py`

## API Documentation

The backend exposes a RESTful API for frontend and third-party integration. All endpoints are versioned and follow consistent patterns.

**Base URL:** `/api/v1`

### Authentication

API endpoints use different authentication methods based on their sensitivity. Public endpoints may use CAPTCHA verification, while admin endpoints require JWT authentication.

### Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/services` | GET | Retrieve service listings with optional filtering |
| `/services/{id}` | GET | Retrieve specific service details |
| `/case-studies` | GET | Retrieve case studies with optional filtering |
| `/impact-stories` | GET | Retrieve social impact stories |
| `/contact` | POST | Submit contact form |
| `/demo-request` | POST | Request service demonstration |
| `/quote-request` | POST | Request service quote |
| `/uploads/request` | POST | Request file upload URL |
| `/uploads/complete` | POST | Confirm upload completion |
| `/uploads/status/{id}` | GET | Check upload status |

Detailed API documentation is available through Swagger UI at `/docs` and ReDoc at `/redoc` when running the application.

## Database Models

The application uses SQLAlchemy ORM with PostgreSQL. Key models include:

### User

Represents website users who submit forms or upload files

**Key Fields:**
- `id`: UUID primary key
- `email`: String, unique
- `name`: String
- `company`: String
- `created_at`: DateTime

### FormSubmission

Stores form submissions including contact forms, demo requests, and quote requests

**Key Fields:**
- `id`: UUID primary key
- `user_id`: UUID, foreign key to User
- `form_type`: String enumeration
- `data`: JSONB
- `status`: String enumeration
- `created_at`: DateTime

### FileUpload

Tracks uploaded files through the processing pipeline

**Key Fields:**
- `id`: UUID primary key
- `user_id`: UUID, foreign key to User
- `filename`: String
- `size`: Integer
- `mime_type`: String
- `storage_path`: String
- `status`: String enumeration
- `created_at`: DateTime

### FileAnalysis

Stores analysis results for processed files

**Key Fields:**
- `id`: UUID primary key
- `upload_id`: UUID, foreign key to FileUpload
- `summary`: Text
- `details_path`: String
- `created_at`: DateTime

### Service

Represents AI service offerings

**Key Fields:**
- `id`: UUID primary key
- `name`: String
- `slug`: String, unique
- `description`: Text
- `icon`: String

### CaseStudy

Represents client success stories

**Key Fields:**
- `id`: UUID primary key
- `title`: String
- `slug`: String, unique
- `client`: String
- `challenge`: Text
- `solution`: Text
- `industry_id`: UUID, foreign key to Industry

### ImpactStory

Represents social impact narratives

**Key Fields:**
- `id`: UUID primary key
- `title`: String
- `slug`: String, unique
- `story`: Text
- `beneficiaries`: String
- `location_id`: UUID, foreign key to Location

## Service Components

The business logic is implemented in service classes that encapsulate related functionality:

### FormProcessingService

Handles form submission processing including validation, storage, email notifications, and CRM integration

**Key Methods:**
- `process_contact_form`
- `process_demo_request`
- `process_quote_request`

### FileUploadService

Manages file uploads including presigned URL generation, validation, and status tracking

**Key Methods:**
- `create_upload`
- `complete_upload`
- `get_upload_status`
- `scan_uploaded_file`

### FileProcessingService

Processes uploaded files including data analysis and result generation

**Key Methods:**
- `process_file`
- `get_processing_results`

### ContentService

Retrieves and manages content for the website

**Key Methods:**
- `get_services`
- `get_case_studies`
- `get_impact_stories`

### EmailService

Sends email notifications using templates

**Key Methods:**
- `send_contact_confirmation`
- `send_demo_request_confirmation`
- `send_upload_confirmation`

### CRMService

Integrates with HubSpot CRM for lead management

**Key Methods:**
- `sync_contact`
- `sync_form_submission`
- `create_deal`

### SecurityService

Provides security-related functionality

**Key Methods:**
- `validate_captcha`
- `scan_file`
- `validate_input`

### AnalyticsService

Tracks analytics events

**Key Methods:**
- `track_form_submission`
- `track_file_upload`
- `track_page_view`

## Integration Components

The backend integrates with several external systems:

### HubSpot CRM

Integration with HubSpot for lead management

**Implementation:** `app/integrations/hubspot.py`

**Features:**
- Contact creation/update
- Deal creation
- Activity logging

### Contentful CMS

Integration with Contentful for content management

**Implementation:** `app/integrations/contentful.py`

**Features:**
- Content retrieval
- Content synchronization

### AWS S3

Integration with AWS S3 for file storage

**Implementation:** `app/integrations/aws_s3.py`

**Features:**
- Presigned URL generation
- File upload/download
- Lifecycle management

### SendGrid

Integration with SendGrid for email delivery

**Implementation:** `app/integrations/sendgrid.py`

**Features:**
- Transactional emails
- Template rendering
- Delivery tracking

### Google Analytics

Integration with Google Analytics for user tracking

**Implementation:** `app/integrations/google_analytics.py`

**Features:**
- Event tracking
- Conversion tracking

## Security Features

The backend implements comprehensive security measures:

### Input Validation

Strict validation of all user inputs using Pydantic schemas

**Implementation:** `app/api/v1/schemas/` and `app/security/input_validation.py`

### CAPTCHA Verification

reCAPTCHA integration for form submissions to prevent spam

**Implementation:** `app/security/captcha.py`

### Rate Limiting

API rate limiting to prevent abuse

**Implementation:** `app/security/rate_limiting.py` and `app/middlewares/rate_limiter.py`

### File Scanning

Malware scanning for uploaded files

**Implementation:** `app/security/file_scanner.py`

### Secure File Handling

Secure file upload and storage with validation and access control

**Implementation:** `app/services/file_upload_service.py`

### Authentication

JWT-based authentication for protected endpoints

**Implementation:** `app/security/jwt.py`

### Security Headers

HTTP security headers for protection against common web vulnerabilities

**Implementation:** `app/middlewares/security_middleware.py`

## Development Guidelines

### Setup

Instructions for setting up the development environment:

1. Clone the repository
2. Install dependencies with `pip install -r requirements-dev.txt`
3. Set up environment variables using `.env.example` as a template
4. Initialize the database with `alembic upgrade head`
5. Run the development server with `uvicorn app.main:app --reload`

### Coding Standards

Coding standards for backend development:

- Follow PEP 8 style guide
- Use type hints for all function parameters and return values
- Write docstrings for all modules, classes, and functions
- Keep functions small and focused on a single responsibility
- Use meaningful variable and function names
- Follow the existing project structure and patterns

### Testing

Testing guidelines for backend development:

- Write unit tests for all new functionality
- Ensure test coverage of at least 80% for new code
- Use pytest fixtures for test setup
- Mock external dependencies in unit tests
- Write integration tests for API endpoints
- Run tests with `pytest` before submitting pull requests

### Pull Requests

Guidelines for submitting pull requests:

- Create a feature branch from develop
- Keep changes focused on a single feature or bug fix
- Ensure all tests pass before submitting
- Include appropriate documentation updates
- Follow the pull request template
- Request review from at least one team member

## Deployment

The backend is deployed using Docker containers in AWS ECS. Deployment is automated through CI/CD pipelines.

### Environments

#### Development
- For active development and testing
- Automatic deployment on merge to develop branch

#### Staging
- For pre-production testing and validation
- Manual promotion from development

#### Production
- Live environment for end users
- Manual promotion from staging with approval

### Monitoring

The application is monitored using AWS CloudWatch for logs and metrics, with alerts configured for critical issues.

## Troubleshooting

Common issues and troubleshooting steps:

### API returns 500 Internal Server Error

**Possible causes:**
- Database connection issue
- External service integration failure
- Unhandled exception

**Troubleshooting:**
- Check application logs
- Verify database connection
- Check external service status

### File upload fails

**Possible causes:**
- File size too large
- Unsupported file type
- S3 integration issue

**Troubleshooting:**
- Check file size and type
- Verify S3 credentials and permissions
- Check upload service logs

### Form submission not appearing in CRM

**Possible causes:**
- CRM integration issue
- Rate limiting
- Data mapping error

**Troubleshooting:**
- Check CRM integration logs
- Verify HubSpot API status
- Check form data format

### Email notifications not being sent

**Possible causes:**
- SendGrid integration issue
- Template rendering error
- Email configuration issue

**Troubleshooting:**
- Check email service logs
- Verify SendGrid API status
- Check email templates

## Additional Resources

### Internal Documentation

- [API Documentation](docs/backend/api.md) - Detailed API documentation
- [Database Schema](docs/backend/database.md) - Database schema documentation
- [Services Documentation](docs/backend/services.md) - Service layer documentation
- [File Processing](docs/backend/file-processing.md) - File upload and processing documentation
- [Security Documentation](docs/backend/security.md) - Security features documentation

### External Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/) - Official FastAPI documentation
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/) - Official SQLAlchemy documentation