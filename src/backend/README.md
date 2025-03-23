# IndiVillage.com Backend

Backend services for the IndiVillage.com website, providing API endpoints for content delivery, form processing, file uploads, and integrations with external services.

## Architecture Overview

The backend is built using Flask with a modular architecture, organized around core services for content management, form processing, file uploads, and data analysis. It integrates with AWS S3 for file storage, HubSpot for CRM, Contentful for content management, and SendGrid for email notifications.

The architecture follows a layered approach:
- RESTful API layer for client communication
- Service layer for business logic
- Integration layer for external service communication
- Data access layer for database operations

Key components include:
- Flask API framework (v2.3+)
- PostgreSQL for operational data storage
- Redis for caching and message queuing
- AWS S3 for file storage
- Security middleware for authentication and authorization

## Getting Started

### Prerequisites

- Python 3.10+
- PostgreSQL 13+
- Redis 7.0+
- Docker (optional but recommended)
- AWS account with S3 access
- API keys for external services (HubSpot, Contentful, SendGrid)

### Installation

#### Local Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/indivillage/indivillage-website-backend.git
   cd indivillage-website-backend
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # For development tools
   ```

4. Create a local PostgreSQL database:
   ```bash
   createdb indivillage_dev
   ```

5. Run database migrations:
   ```bash
   flask db upgrade
   ```

6. Start the development server:
   ```bash
   flask run --debug
   ```

#### Docker Setup

1. Build the Docker image:
   ```bash
   docker-compose build
   ```

2. Start the services:
   ```bash
   docker-compose up
   ```

3. Run migrations inside the container:
   ```bash
   docker-compose exec web flask db upgrade
   ```

### Environment Configuration

Create a `.env` file in the project root with the following variables:

```
# Application configuration
FLASK_APP=app
FLASK_ENV=development
SECRET_KEY=your-secret-key

# Database configuration
DATABASE_URL=postgresql://username:password@localhost:5432/indivillage_dev
REDIS_URL=redis://localhost:6379/0

# AWS configuration
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_DEFAULT_REGION=us-east-1
S3_BUCKET_UPLOADS=indivillage-uploads-dev
S3_BUCKET_PROCESSED=indivillage-processed-dev

# External services
HUBSPOT_API_KEY=your-hubspot-api-key
CONTENTFUL_SPACE_ID=your-contentful-space-id
CONTENTFUL_ACCESS_TOKEN=your-contentful-access-token
SENDGRID_API_KEY=your-sendgrid-api-key
RECAPTCHA_SECRET_KEY=your-recaptcha-secret-key

# Security configuration
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ACCESS_TOKEN_EXPIRES=3600
JWT_REFRESH_TOKEN_EXPIRES=86400
```

## Project Structure

The backend follows a modular structure organized around features and concerns:

```
indivillage-backend/
├── app/                    # Main application package
│   ├── __init__.py         # Application factory
│   ├── api/                # API endpoints and route definitions
│   │   ├── __init__.py
│   │   ├── services.py     # Service catalog endpoints
│   │   ├── case_studies.py # Case study endpoints
│   │   ├── impact.py       # Social impact story endpoints
│   │   ├── forms.py        # Form submission endpoints
│   │   └── uploads.py      # File upload endpoints
│   ├── core/               # Core application configuration
│   │   ├── __init__.py
│   │   ├── config.py       # Configuration management
│   │   ├── exceptions.py   # Custom exceptions
│   │   └── logging.py      # Logging configuration
│   ├── db/                 # Database models and migrations
│   │   ├── __init__.py
│   │   ├── models/         # SQLAlchemy models
│   │   └── migrations/     # Alembic migrations
│   ├── services/           # Business logic implementations
│   │   ├── __init__.py
│   │   ├── content.py      # Content service
│   │   ├── forms.py        # Form processing service
│   │   ├── uploads.py      # File upload service
│   │   └── analysis.py     # Data analysis service
│   ├── integrations/       # External service integrations
│   │   ├── __init__.py
│   │   ├── contentful.py   # Contentful CMS integration
│   │   ├── hubspot.py      # HubSpot CRM integration
│   │   ├── sendgrid.py     # SendGrid email integration
│   │   └── s3.py           # AWS S3 integration
│   ├── security/           # Security-related functionality
│   │   ├── __init__.py
│   │   ├── auth.py         # Authentication
│   │   ├── rate_limit.py   # Rate limiting
│   │   └── file_scan.py    # File security scanning
│   └── utils/              # Utility functions and helpers
│       ├── __init__.py
│       ├── validators.py   # Input validators
│       ├── formatters.py   # Data formatters
│       └── helpers.py      # General helpers
├── tests/                  # Test suite
│   ├── conftest.py         # Test fixtures
│   ├── unit/               # Unit tests
│   ├── integration/        # Integration tests
│   └── e2e/                # End-to-end tests
├── scripts/                # Utility scripts
├── migrations/             # Database migrations
├── requirements.txt        # Production dependencies
├── requirements-dev.txt    # Development dependencies
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker Compose configuration
└── README.md               # This file
```

## API Documentation

The IndiVillage.com backend exposes the following API endpoints:

### Content Endpoints

* `GET /api/services` - List all service offerings
* `GET /api/services/:id` - Get details for a specific service
* `GET /api/case-studies` - List case studies (with optional filtering)
* `GET /api/case-studies/:id` - Get details for a specific case study
* `GET /api/impact-stories` - List social impact stories
* `GET /api/impact-stories/:id` - Get details for a specific impact story
* `GET /api/impact-metrics` - Get social impact metrics

### Form Submission Endpoints

* `POST /api/contact` - Submit a contact form
* `POST /api/demo-request` - Request a service demonstration
* `POST /api/quote-request` - Request a service quote

### File Upload Endpoints

* `POST /api/upload/request` - Request a file upload (returns presigned URL)
* `POST /api/upload/complete` - Confirm upload completion
* `GET /api/upload/status/:id` - Check status of a file upload
* `GET /api/upload/result/:id` - Get results of file analysis

Detailed API documentation is available through the Swagger UI at `/docs` when running the application in development mode, or in the [API Reference](docs/api-reference.md) document.

## Database

The backend uses PostgreSQL for operational data storage, with SQLAlchemy as the ORM.

### Key Data Models

* `User`: Stores information about website visitors who submit forms or upload files
* `FormSubmission`: Records form submissions with type and data
* `FileUpload`: Tracks uploaded files with metadata and processing status
* `FileAnalysis`: Stores the results of file analysis

### Migrations

Database migrations are managed with Alembic through Flask-Migrate.

To create a new migration:
```bash
flask db migrate -m "Description of changes"
```

To apply migrations:
```bash
flask db upgrade
```

To revert the last migration:
```bash
flask db downgrade
```

### Seeding Test Data

To seed the database with test data:
```bash
flask seed-db
```

## File Upload Processing

The file upload and processing pipeline handles user-uploaded datasets for analysis.

### Upload Flow

1. Client requests an upload URL via `POST /api/upload/request`
2. Backend generates a presigned S3 URL with temporary credentials
3. Client uploads the file directly to S3 using the presigned URL
4. Client notifies backend of upload completion via `POST /api/upload/complete`
5. Backend initiates the processing pipeline

### Processing Pipeline

1. **Security Scanning**: Files are scanned for malware and validated for allowed types
2. **File Analysis**: Based on file type, appropriate analysis is performed:
   * CSV/JSON/XML: Structure analysis, data type detection, statistical analysis
   * Images: Image classification, metadata extraction
   * Audio: Audio quality analysis, transcription (if applicable)
3. **Result Generation**: Analysis results are compiled and stored
4. **Notification**: User is notified via email when processing completes
5. **CRM Update**: The user's CRM record is updated with upload and analysis information

### Security Measures

* File type validation before and after upload
* Size limits and rate limiting to prevent abuse
* Malware scanning using ClamAV
* Automatic file purging after 30 days
* Access control through temporary signed URLs

## External Integrations

The backend integrates with several external services:

### AWS S3

Used for secure file storage, with separate buckets for:
* `indivillage-uploads`: Temporary storage for uploaded files
* `indivillage-processed`: Storage for processed results
* `indivillage-assets`: Public website assets

Integration is handled via the AWS SDK for Python (Boto3).

### HubSpot CRM

Integration with HubSpot for lead management:
* Creating/updating contacts from form submissions
* Tracking file uploads and analysis as activities
* Managing demo requests and quotes

The integration uses the HubSpot API v3 through the official Python SDK.

### Contentful CMS

Content management integration for:
* Service descriptions
* Case studies
* Impact stories
* Team information

The integration uses the Contentful Content Delivery API through the official Python SDK.

### SendGrid

Email service for sending:
* Form submission confirmations
* Upload processing notifications
* Demo scheduling confirmations

The integration uses the SendGrid API v3 through the official Python SDK.

## Testing

The backend uses pytest for testing, with a combination of unit, integration, and end-to-end tests.

### Running Tests

Run all tests:
```bash
pytest
```

Run specific test categories:
```bash
pytest tests/unit/  # Unit tests only
pytest tests/integration/  # Integration tests only
pytest tests/e2e/  # End-to-end tests only
```

Run with coverage reporting:
```bash
pytest --cov=app --cov-report=term-missing
```

### Testing Strategy

* **Unit Tests**: Test individual functions and methods in isolation
* **Integration Tests**: Test interactions between components, with external services mocked
* **End-to-End Tests**: Test complete workflows with a test database

### CI Integration

Tests are automatically run in the CI pipeline on pull requests and before deployment.

## Deployment

The backend can be deployed to different environments using Docker and AWS services.

### Deployment Environments

* **Development**: For local development and testing
* **Staging**: For QA and pre-production testing
* **Production**: Live environment for real users

### Deployment Process

1. Build the Docker image:
   ```bash
   docker build -t indivillage-backend .
   ```

2. Tag the image for the target environment:
   ```bash
   docker tag indivillage-backend:latest indivillage-backend:production
   ```

3. Push to the container registry:
   ```bash
   docker push indivillage-backend:production
   ```

4. Deploy to AWS ECS:
   ```bash
   aws ecs update-service --cluster indivillage-cluster --service backend-service --force-new-deployment
   ```

For detailed deployment instructions, see the [Deployment Guide](docs/deployment.md).

## Monitoring and Logging

The backend uses a comprehensive monitoring and logging setup:

### Logging

* Structured JSON logs for easy parsing
* Log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
* Request logging middleware for API requests
* Error tracking with stack traces
* Log rotation and archiving

Logs are forwarded to CloudWatch Logs in AWS environments.

### Metrics

* API request counts and response times
* Error rates and types
* File upload counts and processing times
* External service integration metrics
* Database performance metrics

Metrics are collected using CloudWatch Metrics in AWS environments.

### Alerting

Alerts are configured for:
* High error rates
* Slow API responses
* Failed file processing
* External service integration failures
* Database performance issues

Alerts are sent via CloudWatch Alarms to SNS topics for email/Slack notifications.

## Security Considerations

The backend implements several security measures:

### Authentication and Authorization

* JWT-based authentication for protected endpoints
* Role-based access control for administrative functions
* Secure token handling with proper expiration

### Input Validation

* Comprehensive validation of all user inputs
* Schema validation for API requests
* File type validation for uploads

### Rate Limiting

* IP-based rate limiting for public endpoints
* User-based rate limiting for authenticated endpoints
* Graduated response for repeated violations

### Data Protection

* Encryption in transit (TLS/SSL)
* Encryption at rest (database, file storage)
* Data minimization practices
* Automatic data purging based on retention policy

### Security Headers

* Content-Security-Policy (CSP)
* X-Content-Type-Options
* X-Frame-Options
* X-XSS-Protection
* Strict-Transport-Security (HSTS)

## Contributing

We welcome contributions to the IndiVillage.com backend!

### Development Workflow

1. Create a feature branch from `develop`
2. Make your changes
3. Write tests for your changes
4. Ensure all tests pass
5. Submit a pull request to `develop`

### Code Style

The project uses Black for code formatting and Flake8 for linting.

Format your code:
```bash
black app tests
```

Check for linting issues:
```bash
flake8 app tests
```

### Commit Guidelines

We follow the Conventional Commits specification:
* `feat`: New feature
* `fix`: Bug fix
* `docs`: Documentation changes
* `style`: Changes that do not affect code functionality
* `refactor`: Code changes that neither fix bugs nor add features
* `perf`: Performance improvements
* `test`: Adding or modifying tests
* `chore`: Changes to build process, dependencies, etc.

Example: `feat: Add support for CSV file analysis`

## License

Copyright © 2023 IndiVillage

All rights reserved. This software is proprietary and confidential.
Unauthorized copying, distribution, or use is strictly prohibited.