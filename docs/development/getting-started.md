# Getting Started with IndiVillage.com Development

This guide will help you set up your development environment and get started with contributing to the IndiVillage.com website project. The project uses a modern tech stack with Next.js for the frontend and FastAPI for the backend, all containerized with Docker for consistent development and deployment.

## Prerequisites

Before you begin, ensure you have the following tools installed on your development machine:

### Required Software
- **Git**: Version control system (v2.30.0+)
- **Docker**: Containerization platform (v20.10.0+)
- **Docker Compose**: Multi-container Docker applications (v2.0.0+)
- **Node.js**: JavaScript runtime (v18.x) - for local frontend development
- **Python**: Programming language (v3.10+) - for local backend development
- **Visual Studio Code** (recommended) or your preferred IDE

Optional but recommended:
- **yarn**: Package manager for Node.js (v1.22.0+)
- **make**: Build automation tool
- **AWS CLI**: For interacting with AWS services during development

### Access Requirements

You'll need access to the following resources:

- **GitHub Repository**: Request access to the IndiVillage.com repository
- **AWS Account**: For accessing development resources (if needed)
- **Contentful CMS**: For content management (request access from the team lead)
- **HubSpot CRM**: For testing CRM integration (development credentials will be provided)

Contact your team lead or the project administrator to request the necessary access.

## Project Structure

The IndiVillage.com project follows a monorepo structure with clear separation between frontend and backend components:

### Repository Overview
```
/
├── .github/            # GitHub Actions workflows and templates
├── docs/               # Project documentation
│   ├── architecture.md
│   ├── backend/        # Backend-specific documentation
│   ├── deployment/     # Deployment documentation
│   ├── development/    # Development guidelines
│   ├── infrastructure/ # Infrastructure documentation
│   ├── integrations/   # External integrations documentation
│   ├── operations/     # Operations documentation
│   └── web/            # Frontend-specific documentation
├── infrastructure/     # Infrastructure as Code (Terraform)
│   ├── terraform/      # Terraform configurations
│   ├── scripts/        # Infrastructure scripts
│   └── monitoring/     # Monitoring configurations
├── src/                # Source code
│   ├── backend/        # Backend application (FastAPI)
│   └── web/            # Frontend application (Next.js)
├── .gitignore
├── LICENSE
└── README.md
```

### Frontend Structure
The frontend application is built with Next.js and follows a modern React architecture:

```
src/web/
├── public/            # Static assets
├── src/
│   ├── app/           # Next.js App Router pages and layouts
│   ├── components/    # React components
│   │   ├── ui/        # Reusable UI components
│   │   ├── shared/    # Shared components
│   │   ├── forms/     # Form components
│   │   ├── layout/    # Layout components
│   │   ├── home/      # Home page components
│   │   ├── services/  # Service page components
│   │   ├── impact/    # Impact page components
│   │   └── case-studies/ # Case study components
│   ├── context/       # React context providers
│   ├── hooks/         # Custom React hooks
│   ├── lib/           # Third-party library integrations
│   ├── services/      # API service integrations
│   ├── styles/        # Global styles and CSS
│   ├── types/         # TypeScript type definitions
│   ├── utils/         # Utility functions
│   └── constants/     # Constants and configuration
├── tests/             # Frontend tests
├── .env.development   # Development environment variables
├── .env.production    # Production environment variables
├── .env.test          # Test environment variables
├── next.config.js     # Next.js configuration
├── package.json       # Dependencies and scripts
├── tsconfig.json      # TypeScript configuration
└── tailwind.config.ts # Tailwind CSS configuration
```

### Backend Structure
The backend application is built with FastAPI and follows a modular architecture:

```
src/backend/
├── app/               # Application code
│   ├── api/           # API endpoints
│   │   ├── v1/        # API version 1
│   │   │   ├── endpoints/ # API route handlers
│   │   │   ├── models/    # Database models
│   │   │   └── schemas/   # Pydantic schemas
│   ├── core/          # Core application components
│   ├── db/            # Database configuration and migrations
│   ├── services/      # Business logic services
│   ├── utils/         # Utility functions
│   ├── security/      # Security-related functionality
│   ├── templates/     # Email templates
│   ├── cache/         # Caching functionality
│   ├── queue/         # Background task queue
│   ├── integrations/  # External service integrations
│   ├── monitoring/    # Monitoring and observability
│   └── middlewares/   # Request/response middlewares
├── migrations/        # Alembic database migrations
├── scripts/           # Utility scripts
├── tests/             # Backend tests
├── .env.example       # Example environment variables
├── requirements.txt   # Python dependencies
├── requirements-dev.txt # Development dependencies
└── alembic.ini        # Alembic configuration
```

## Setting Up Your Development Environment

Follow these steps to set up your local development environment:

### Clone the Repository
```bash
# Clone the repository
git clone https://github.com/your-organization/indivillage-website.git
cd indivillage-website
```

### Docker-based Setup (Recommended)
The recommended way to set up the development environment is using Docker, which ensures consistency across all development machines.

```bash
# Start the backend services
cd src/backend
cp .env.example .env  # Copy and modify with your local settings
docker-compose up -d

# Start the frontend services
cd ../web
cp .env.example .env.development  # Copy and modify with your local settings
docker-compose up -d
```

This will start the following services:

**Backend:**
- FastAPI application on http://localhost:8000
- PostgreSQL database on port 5432
- Redis cache on port 6379
- Celery worker for background tasks
- ClamAV for virus scanning

**Frontend:**
- Next.js application on http://localhost:3000

You can access the API documentation at http://localhost:8000/docs and the website at http://localhost:3000.

### Local Setup (Alternative)
If you prefer to run the services directly on your machine without Docker:

**Backend Setup:**
```bash
cd src/backend

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements-dev.txt

# Set up environment variables
cp .env.example .env  # Modify with your local settings

# Run database migrations
alembic upgrade head

# Start the development server
uvicorn app.main:app --reload --port 8000
```

**Frontend Setup:**
```bash
cd src/web

# Install dependencies
yarn install

# Set up environment variables
cp .env.example .env.development  # Modify with your local settings

# Start the development server
yarn dev
```

Note: For local setup, you'll need to have PostgreSQL and Redis installed and running on your machine.

### Environment Variables
Both the frontend and backend applications use environment variables for configuration. Sample environment files are provided (`.env.example`), but you'll need to set up your own environment variables for local development.

**Key Backend Environment Variables:**
```
ENVIRONMENT=development
DEBUG=true
DATABASE_URL=postgresql://postgres:postgres@db:5432/indivillage
REDIS_URL=redis://redis:6379/0
SECRET_KEY=your_secret_key_here
AWS_REGION=us-east-1
AWS_S3_BUCKET_NAME=indivillage-dev
AWS_S3_UPLOAD_BUCKET_NAME=indivillage-uploads-dev
AWS_S3_PROCESSED_BUCKET_NAME=indivillage-processed-dev
MAX_UPLOAD_SIZE_MB=50
ALLOWED_UPLOAD_EXTENSIONS=.csv,.json,.xml,.jpg,.png,.tiff,.mp3,.wav
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
```

**Key Frontend Environment Variables:**
```
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api
NEXT_PUBLIC_SITE_URL=http://localhost:3000
NEXT_PUBLIC_CONTENTFUL_SPACE_ID=your_contentful_space_id
NEXT_PUBLIC_CONTENTFUL_ACCESS_TOKEN=your_contentful_access_token
NEXT_PUBLIC_RECAPTCHA_SITE_KEY=your_recaptcha_site_key
NEXT_PUBLIC_GOOGLE_ANALYTICS_ID=your_ga_id
NEXT_PUBLIC_ENABLE_ANALYTICS=false
NEXT_PUBLIC_DEBUG_MODE=true
```

Contact your team lead to obtain the necessary credentials for external services like Contentful, AWS, and reCAPTCHA.

### IDE Setup
**Visual Studio Code (Recommended)**

We recommend using Visual Studio Code with the following extensions:

- ESLint: JavaScript/TypeScript linting
- Prettier: Code formatting
- Python: Python language support
- Tailwind CSS IntelliSense: Tailwind CSS class completion
- Docker: Docker integration
- GitLens: Git integration
- Jest: Testing support

A workspace configuration file is provided in the repository (`.vscode/settings.json`) with recommended settings.

**Other IDEs**

If you're using another IDE, ensure you configure it to:

- Use ESLint for JavaScript/TypeScript linting
- Use Prettier for code formatting
- Use Black and isort for Python formatting
- Respect the project's `.editorconfig` file

## Development Workflow

This section provides an overview of the development workflow. For more detailed information, refer to [workflows.md](workflows.md).

### Branching Strategy
We follow a modified GitFlow branching strategy:

- `main`: Production-ready code, deployed to the production environment
- `staging`: Pre-production code, deployed to the staging environment
- `develop`: Development code, deployed to the development environment
- `feature/*`: Feature branches for new development
- `bugfix/*`: Bug fix branches for non-critical fixes
- `hotfix/*`: Hotfix branches for critical production issues

**Working with Branches:**

```bash
# Ensure you have the latest develop branch
git checkout develop
git pull

# Create a new feature branch
git checkout -b feature/your-feature-name

# Make your changes, commit, and push
git add .
git commit -m "Add feature: your feature description"
git push -u origin feature/your-feature-name
```

Once your feature is complete, create a pull request to merge it into the `develop` branch.

### Code Standards
We follow strict coding standards to ensure code quality and consistency. For detailed information, refer to [standards.md](standards.md).

**Key Standards:**

- **Frontend**: TypeScript, React best practices, TailwindCSS for styling
- **Backend**: PEP 8, type hints, comprehensive docstrings
- **General**: Clear commit messages, comprehensive documentation

**Linting and Formatting:**

```bash
# Frontend
cd src/web
yarn lint        # Run ESLint
yarn format      # Run Prettier

# Backend
cd src/backend
flake8 app tests  # Run flake8
black app tests   # Run Black formatter
isort app tests   # Sort imports
```

### Testing
All code changes should be accompanied by appropriate tests. For detailed testing guidelines, refer to [testing.md](testing.md).

**Running Frontend Tests:**

```bash
cd src/web
yarn test              # Run all tests
yarn test --watch      # Run tests in watch mode
yarn test --coverage   # Run tests with coverage
```

**Running Backend Tests:**

```bash
cd src/backend
pytest                 # Run all tests
pytest tests/unit      # Run unit tests
pytest tests/api       # Run API tests
pytest --cov=app       # Run tests with coverage
```

**Running E2E Tests:**

```bash
cd src/web
yarn cypress:open      # Open Cypress test runner
yarn cypress:run       # Run Cypress tests headlessly
```

### Pull Requests
All code changes must be submitted through pull requests:

1. Create a feature branch from `develop`
2. Make your changes and commit them
3. Push your branch to GitHub
4. Create a pull request to merge your branch into `develop`
5. Ensure all CI checks pass
6. Request reviews from team members
7. Address any feedback from reviewers
8. Once approved, your PR will be merged

Pull requests should include:
- A clear description of the changes
- Reference to related issues
- Screenshots for UI changes
- Notes on any breaking changes
- Test coverage for new functionality

### CI/CD Pipeline
The project uses GitHub Actions for CI/CD. For detailed information, refer to [ci-cd.md](../deployment/ci-cd.md).

**CI Pipeline:**

When you push changes or create a pull request, the CI pipeline will automatically:

1. Run linting and static analysis
2. Run unit and integration tests
3. Build the application
4. Run security scans

**CD Pipeline:**

When changes are merged to specific branches, the CD pipeline will automatically:

- `develop` branch: Deploy to the development environment
- `staging` branch: Deploy to the staging environment
- `main` branch: Deploy to the production environment (after approval)

You can monitor the status of CI/CD runs in the GitHub Actions tab of the repository.

## Common Development Tasks

This section covers common tasks you'll encounter during development.

### Working with the Frontend
**Creating a New Component:**

1. Create a new file in the appropriate components directory
2. Implement the component using TypeScript and React
3. Create a test file for the component
4. Import and use the component where needed

**Example Component:**

```tsx
// src/web/src/components/ui/Button.tsx
import React from 'react';

interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'tertiary';
  size?: 'small' | 'medium' | 'large';
  children: React.ReactNode;
  onClick?: () => void;
  disabled?: boolean;
  className?: string;
}

const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'medium',
  children,
  onClick,
  disabled = false,
  className = '',
}) => {
  const baseClasses = 'rounded font-medium focus:outline-none focus:ring-2';
  
  const variantClasses = {
    primary: 'bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500',
    secondary: 'bg-white text-blue-600 border border-blue-600 hover:bg-blue-50 focus:ring-blue-500',
    tertiary: 'text-blue-600 hover:underline focus:ring-blue-500',
  };
  
  const sizeClasses = {
    small: 'py-1 px-3 text-sm',
    medium: 'py-2 px-4 text-base',
    large: 'py-3 px-6 text-lg',
  };
  
  return (
    <button
      className={`${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]} ${className}`}
      onClick={onClick}
      disabled={disabled}
    >
      {children}
    </button>
  );
};

export default Button;
```

**Adding a New Page:**

1. Create a new directory or file in the `src/web/src/app` directory
2. Implement the page component
3. The file path will determine the route (e.g., `src/web/src/app/about/page.tsx` will be accessible at `/about`)

**Example Page:**

```tsx
// src/web/src/app/about/page.tsx
import React from 'react';
import { Metadata } from 'next';
import PageHeader from '@/components/shared/PageHeader';

export const metadata: Metadata = {
  title: 'About Us | IndiVillage',
  description: 'Learn about IndiVillage, our mission, and our team.',
};

export default function AboutPage() {
  return (
    <main className="container mx-auto px-4 py-8">
      <PageHeader title="About Us" />
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mt-8">
        <div>
          <h2 className="text-2xl font-semibold mb-4">Our Story</h2>
          <p className="text-gray-700">
            IndiVillage was founded with a mission to provide high-quality AI services
            while creating positive social impact in rural communities.
          </p>
        </div>
        <div>
          <img
            src="/images/about-us.jpg"
            alt="IndiVillage team"
            className="rounded-lg shadow-md"
          />
        </div>
      </div>
    </main>
  );
}
```

**Working with API Services:**

Use the service layer to interact with the backend API:

```tsx
// src/web/src/services/api.ts
import { fetcher } from '@/utils/fetcher';
import { apiEndpoints } from '@/constants/apiEndpoints';

export const submitContactForm = async (formData: ContactFormData) => {
  return fetcher(apiEndpoints.contact, {
    method: 'POST',
    body: JSON.stringify(formData),
  });
};
```

Then use the service in your component:

```tsx
import { submitContactForm } from '@/services/api';

const handleSubmit = async (formData: ContactFormData) => {
  try {
    const response = await submitContactForm(formData);
    // Handle success
  } catch (error) {
    // Handle error
  }
};
```

### Working with the Backend
**Creating a New API Endpoint:**

1. Create a new file in the `src/backend/app/api/v1/endpoints` directory
2. Define the endpoint using FastAPI
3. Implement the business logic in the appropriate service
4. Register the endpoint in the API router

**Example Endpoint:**

```python
# src/backend/app/api/v1/endpoints/contact.py
from fastapi import APIRouter, Depends, HTTPException, status
from app.api.v1.schemas.contact import ContactRequest, ContactResponse
from app.services.form_processing_service import FormProcessingService
from app.security.captcha import verify_captcha

router = APIRouter()

@router.post("/contact", response_model=ContactResponse, status_code=status.HTTP_200_OK)
async def submit_contact_form(
    request: ContactRequest,
    form_service: FormProcessingService = Depends(),
):
    """Submit a contact form.
    
    Args:
        request: The contact form data
        form_service: Form processing service dependency
        
    Returns:
        ContactResponse: Success response
        
    Raises:
        HTTPException: If captcha verification fails or form processing fails
    """
    # Verify captcha
    if not await verify_captcha(request.captcha_token):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Captcha verification failed",
        )
    
    # Process form submission
    try:
        await form_service.process_contact_form(
            name=request.name,
            email=request.email,
            message=request.message,
            company=request.company,
        )
        return ContactResponse(success=True)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
```

**Register the endpoint in the router:**

```python
# src/backend/app/api/v1/__init__.py
from fastapi import APIRouter
from app.api.v1.endpoints import contact, services, case_studies, impact_stories, uploads

api_router = APIRouter()

api_router.include_router(contact.router, tags=["contact"])
api_router.include_router(services.router, prefix="/services", tags=["services"])
api_router.include_router(case_studies.router, prefix="/case-studies", tags=["case-studies"])
api_router.include_router(impact_stories.router, prefix="/impact-stories", tags=["impact-stories"])
api_router.include_router(uploads.router, prefix="/upload", tags=["uploads"])
```

**Creating a New Service:**

1. Create a new file in the `src/backend/app/services` directory
2. Implement the service class with the required business logic
3. Use dependency injection to make the service available to endpoints

**Example Service:**

```python
# src/backend/app/services/form_processing_service.py
from typing import Optional
from fastapi import Depends
from app.db.session import get_db
from app.api.v1.models.form_submission import FormSubmission, FormType
from app.services.email_service import EmailService
from app.services.crm_service import CRMService

class FormProcessingService:
    """Service for processing form submissions."""
    
    def __init__(
        self,
        db=Depends(get_db),
        email_service: EmailService = Depends(),
        crm_service: CRMService = Depends(),
    ):
        """Initialize the form processing service.
        
        Args:
            db: Database session
            email_service: Email service for sending notifications
            crm_service: CRM service for creating leads
        """
        self.db = db
        self.email_service = email_service
        self.crm_service = crm_service
    
    async def process_contact_form(
        self,
        name: str,
        email: str,
        message: str,
        company: Optional[str] = None,
    ) -> FormSubmission:
        """Process a contact form submission.
        
        Args:
            name: The user's name
            email: The user's email
            message: The message content
            company: The user's company (optional)
            
        Returns:
            The created form submission record
        """
        # Create form submission record
        form_submission = FormSubmission(
            form_type=FormType.CONTACT,
            name=name,
            email=email,
            company=company,
            data={"message": message},
        )
        self.db.add(form_submission)
        self.db.commit()
        self.db.refresh(form_submission)
        
        # Send confirmation email
        await self.email_service.send_contact_confirmation(name=name, email=email)
        
        # Create CRM lead
        await self.crm_service.create_contact_lead(
            name=name,
            email=email,
            company=company,
            message=message,
        )
        
        return form_submission
```

**Working with Database Models:**

1. Define models in the `src/backend/app/api/v1/models` directory
2. Use SQLAlchemy for ORM functionality

**Example Model:**

```python
# src/backend/app/api/v1/models/form_submission.py
import enum
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Enum, JSON
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base

class FormType(str, enum.Enum):
    """Enum for form submission types."""
    CONTACT = "contact"
    DEMO_REQUEST = "demo_request"
    QUOTE_REQUEST = "quote_request"

class FormSubmission(Base):
    """Model for form submissions."""
    __tablename__ = "form_submissions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    form_type = Column(Enum(FormType), nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    company = Column(String, nullable=True)
    data = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
```

**Working with the Database:**

1. Create database migrations using Alembic
2. Apply migrations to update the database schema

**Creating Database Migrations:**

When you make changes to database models, you need to create a migration:

```bash
cd src/backend

# Create a new migration
alembic revision --autogenerate -m "Add form submissions table"

# Apply migrations
alembic upgrade head

# Rollback a migration
alembic downgrade -1
```

**Working with the Database in Code:**

```python
# Query example
from app.api.v1.models.form_submission import FormSubmission

def get_recent_submissions(db, limit: int = 10):
    return db.query(FormSubmission).order_by(FormSubmission.created_at.desc()).limit(limit).all()

# Create example
from app.api.v1.models.form_submission import FormSubmission, FormType

def create_submission(db, name: str, email: str, message: str):
    submission = FormSubmission(
        form_type=FormType.CONTACT,
        name=name,
        email=email,
        data={"message": message},
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)
    return submission
```

**Working with External Services:**

**Contentful CMS Integration:**

The frontend application integrates with Contentful CMS for content management:

```typescript
// src/web/src/lib/contentful.ts
import { createClient } from 'contentful';

const client = createClient({
  space: process.env.NEXT_PUBLIC_CONTENTFUL_SPACE_ID || '',
  accessToken: process.env.NEXT_PUBLIC_CONTENTFUL_ACCESS_TOKEN || '',
});

export const getServices = async () => {
  const entries = await client.getEntries({
    content_type: 'service',
    order: 'fields.order',
  });
  
  return entries.items.map(item => ({
    id: item.sys.id,
    title: item.fields.title,
    slug: item.fields.slug,
    description: item.fields.description,
    icon: item.fields.icon?.fields.file.url,
    // ... other fields
  }));
};
```

**HubSpot CRM Integration:**

The backend integrates with HubSpot CRM for lead management:

```python
# src/backend/app/integrations/hubspot.py
import httpx
from app.core.config import settings

class HubSpotClient:
    """Client for interacting with HubSpot CRM API."""
    
    def __init__(self):
        """Initialize the HubSpot client."""
        self.api_key = settings.HUBSPOT_API_KEY
        self.base_url = "https://api.hubapi.com"
        
    async def create_contact(self, email: str, firstname: str, lastname: str, company: str = None):
        """Create a contact in HubSpot.
        
        Args:
            email: Contact email
            firstname: Contact first name
            lastname: Contact last name
            company: Contact company name
            
        Returns:
            The created contact data
        """
        url = f"{self.base_url}/crm/v3/objects/contacts"
        
        # Split name into first and last name if lastname is not provided
        if not lastname and " " in firstname:
            name_parts = firstname.split(" ", 1)
            firstname = name_parts[0]
            lastname = name_parts[1]
        
        properties = {
            "email": email,
            "firstname": firstname,
            "lastname": lastname,
        }
        
        if company:
            properties["company"] = company
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json={"properties": properties},
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
            )
            
            response.raise_for_status()
            return response.json()
```

**AWS S3 Integration:**

The backend integrates with AWS S3 for file storage:

```python
# src/backend/app/integrations/aws_s3.py
import boto3
from botocore.exceptions import ClientError
from app.core.config import settings

class S3Client:
    """Client for interacting with AWS S3."""
    
    def __init__(self):
        """Initialize the S3 client."""
        self.s3_client = boto3.client(
            's3',
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )
        
    def generate_presigned_url(self, bucket_name: str, object_key: str, expiration: int = 3600):
        """Generate a presigned URL for uploading a file to S3.
        
        Args:
            bucket_name: S3 bucket name
            object_key: S3 object key
            expiration: URL expiration time in seconds
            
        Returns:
            Presigned URL for uploading the file
        """
        try:
            response = self.s3_client.generate_presigned_url(
                'put_object',
                Params={
                    'Bucket': bucket_name,
                    'Key': object_key,
                },
                ExpiresIn=expiration,
            )
            return response
        except ClientError as e:
            print(f"Error generating presigned URL: {e}")
            return None
```

## Troubleshooting

This section covers common issues you might encounter during development and how to resolve them.

### Docker Issues
**Container not starting:**

```bash
# Check container logs
docker-compose logs api

# Rebuild container
docker-compose build api
docker-compose up -d api

# Check container status
docker-compose ps
```

**Port conflicts:**

If you see an error like "port is already allocated", you have another service using the same port:

```bash
# Find process using the port (Linux/Mac)
sudo lsof -i :8000

# Find process using the port (Windows)
netstat -ano | findstr :8000

# Stop the process or change the port in docker-compose.yml
```

**Volume permission issues:**

If you encounter permission issues with Docker volumes:

```bash
# Remove volumes and recreate
docker-compose down -v
docker-compose up -d
```

### Frontend Issues
**Next.js build errors:**

```bash
# Clear Next.js cache
cd src/web
rm -rf .next
yarn dev
```

**Module not found errors:**

```bash
# Reinstall dependencies
cd src/web
rm -rf node_modules
yarn install
```

**TypeScript errors:**

If you encounter TypeScript errors:

1. Check the error message for details
2. Ensure you've defined proper types for your components and functions
3. Run `yarn type-check` to verify all TypeScript files

**API connection issues:**

If the frontend can't connect to the backend API:

1. Ensure the backend is running
2. Check that CORS is properly configured
3. Verify the API URL in your environment variables

### Backend Issues
**Database migration errors:**

```bash
# Reset migrations (development only)
cd src/backend
alembic downgrade base
alembic upgrade head
```

**Module import errors:**

```bash
# Verify Python path
cd src/backend
python -c "import sys; print(sys.path)"

# Reinstall dependencies
pip install -r requirements-dev.txt
```

**API errors:**

If you encounter API errors:

1. Check the API logs for detailed error messages
2. Verify request parameters and formats
3. Use the interactive API documentation at http://localhost:8000/docs to test endpoints

**Environment variable issues:**

If environment variables aren't being loaded:

1. Check that your `.env` file exists and has the correct values
2. Verify that the environment variables are being loaded in your code
3. Try setting the variables directly in your terminal before running the application

### Getting Help
If you encounter issues that you can't resolve:

1. Check the project documentation in the `docs` directory
2. Search for similar issues in the GitHub repository
3. Ask for help in the team Slack channel
4. Create a GitHub issue with detailed information about the problem

When asking for help, always include:

- A clear description of the problem
- Steps to reproduce the issue
- Error messages and logs
- Your environment details (OS, Docker version, etc.)

## Additional Resources
**Project Documentation:**

- [Architecture Overview](../architecture.md)
- [Development Workflows](workflows.md)
- [Coding Standards](standards.md)
- [Testing Guidelines](testing.md)
- [CI/CD Pipeline](../deployment/ci-cd.md)

**External Documentation:**

- [Next.js Documentation](https://nextjs.org/docs)
- [React Documentation](https://reactjs.org/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Docker Documentation](https://docs.docker.com/)

**Learning Resources:**

- [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/intro.html)
- [React Hooks Guide](https://reactjs.org/docs/hooks-intro.html)
- [TailwindCSS Documentation](https://tailwindcss.com/docs)
- [Python Type Hints Guide](https://mypy.readthedocs.io/en/stable/cheat_sheet_py3.html)