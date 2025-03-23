# IndiVillage.com Website

A modern, responsive website showcasing IndiVillage's AI-as-a-service capabilities and social impact initiatives. The website features comprehensive service portfolio presentation, interactive data upload functionality, automated quote/demo request system, and compelling presentation of the "AI for Good" social impact story.

## Overview

The IndiVillage.com website is designed to effectively showcase the company's AI-as-a-service and scalable back-office capabilities while highlighting its social impact mission. The website employs a modern JAMstack architecture with a Next.js frontend, RESTful APIs for system integration, and secure cloud infrastructure for data handling and storage.

## Key Features

- Modern, visually appealing design with intuitive navigation
- Comprehensive service portfolio presentation (data collection, preparation, AI model development, Human-in-the-loop solutions)
- Interactive elements allowing potential clients to upload sample datasets
- Automated quote/demo request functionality
- Compelling presentation of the "AI for Good" social impact story
- Seamless integration with backend systems for lead management

## Technology Stack

### Frontend
- Next.js 13.4+
- React 18.2+
- TailwindCSS 3.3+
- TypeScript 4.9+

### Backend
- Python 3.10+
- Flask 2.3+
- PostgreSQL (Database)
- Redis (Caching)

### Infrastructure
- AWS (EC2, S3, RDS, CloudFront, etc.)
- Docker
- Terraform (Infrastructure as Code)
- GitHub Actions (CI/CD)

## Project Structure

```
├── docs/                  # Project documentation
├── infrastructure/        # Infrastructure as Code (Terraform)
├── src/                   # Source code
│   ├── backend/           # Python Flask backend
│   └── web/               # Next.js frontend
├── .github/               # GitHub workflows and templates
├── .gitignore
├── LICENSE
└── README.md              # This file
```

## Getting Started

### Prerequisites

- Node.js 18.x or higher
- Python 3.10 or higher
- Docker and Docker Compose
- AWS CLI (for deployment)

### Local Development Setup

1. Clone the repository
   ```bash
   git clone https://github.com/your-organization/indivillage-website.git
   cd indivillage-website
   ```

2. Set up the backend
   ```bash
   cd src/backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   cp .env.example .env  # Update with your configuration
   flask run
   ```

3. Set up the frontend
   ```bash
   cd src/web
   npm install
   cp .env.example .env.local  # Update with your configuration
   npm run dev
   ```

4. Using Docker Compose (alternative)
   ```bash
   docker-compose up -d
   ```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000

## Development Workflow

1. Create a feature branch from `develop`
   ```bash
   git checkout develop
   git pull
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and commit them
   ```bash
   git add .
   git commit -m "Description of your changes"
   ```

3. Push your branch and create a pull request
   ```bash
   git push -u origin feature/your-feature-name
   ```

4. After review and approval, your changes will be merged into `develop`

5. Releases to staging and production are managed through the CI/CD pipeline

## Testing

### Backend Tests
```bash
# Run all tests
cd src/backend
pytest

# Run with coverage report
pytest --cov=app
```

### Frontend Tests
```bash
cd src/web
npm test

# Run with coverage report
npm test -- --coverage
```

## Deployment

The application is deployed using GitHub Actions CI/CD pipelines:

- Merges to `develop` branch deploy to the development environment
- Merges to `staging` branch deploy to the staging environment
- Merges to `main` branch deploy to the production environment

Refer to the deployment documentation in `docs/deployment/` for detailed information.

## Documentation

Comprehensive documentation is available in the `docs/` directory:

- Architecture overview: `docs/architecture.md`
- Backend documentation: `docs/backend/`
- Frontend documentation: `docs/web/`
- Deployment guides: `docs/deployment/`
- Infrastructure details: `docs/infrastructure/`
- Operations procedures: `docs/operations/`
- Development guidelines: `docs/development/`
- Integration documentation: `docs/integrations/`

## Contributing

1. Follow the development workflow described above
2. Adhere to the coding standards defined in `docs/development/standards.md`
3. Ensure all tests pass before submitting a pull request
4. Include appropriate documentation for new features
5. Update the changelog with your changes

## License

This project is proprietary and confidential. Unauthorized copying, distribution, or use is strictly prohibited.

## Contact

For questions or support, please contact the development team at dev-team@indivillage.com.