# IndiVillage Website Frontend

Modern, responsive website for IndiVillage's AI-as-a-service offerings with social impact focus. Built with Next.js, React, TypeScript, and TailwindCSS.

## Project Overview

This repository contains the frontend application for IndiVillage.com, showcasing the company's AI services and social impact mission. The website features a modern design, interactive elements for customer engagement, and integration with backend services for form submissions and file uploads.

## Key Features

- Responsive design that works across all devices
- Interactive service portfolio showcase
- Sample data upload functionality for potential clients
- Demo and quote request forms with CRM integration
- Social impact storytelling section
- Case studies and success stories
- Accessibility compliance (WCAG 2.1 AA)

## Technology Stack

- **Framework**: Next.js 13.4+ with App Router
- **Language**: TypeScript 5.0+
- **Styling**: TailwindCSS 3.3+ with custom design system
- **State Management**: React Context API, React Query
- **Form Handling**: React Hook Form with Zod validation
- **File Upload**: React Dropzone with AWS S3 integration
- **Animation**: Framer Motion
- **Testing**: Jest, React Testing Library, Cypress
- **Deployment**: Docker, AWS

## Getting Started

### Prerequisites

- Node.js 18.x or higher
- Yarn 1.22.x or higher
- Docker and Docker Compose (optional, for containerized development)

### Installation

1. Clone the repository
2. Navigate to the web directory: `cd src/web`
3. Install dependencies: `yarn install`
4. Copy `.env.example` to `.env.local` and update environment variables
5. Start the development server: `yarn dev`
6. Open [http://localhost:3000](http://localhost:3000) in your browser

### Using Docker

1. Navigate to the web directory: `cd src/web`
2. Build and start the container: `docker-compose up -d`
3. Open [http://localhost:3000](http://localhost:3000) in your browser
4. Stop the container when finished: `docker-compose down`

## Environment Variables

### Required Environment Variables

- `NEXT_PUBLIC_API_URL`: Backend API URL
- `NEXT_PUBLIC_SITE_URL`: Public URL of the website
- `NEXT_PUBLIC_RECAPTCHA_SITE_KEY`: Google reCAPTCHA site key
- `NEXT_PUBLIC_GA_MEASUREMENT_ID`: Google Analytics measurement ID
- `NEXT_PUBLIC_MAX_UPLOAD_SIZE`: Maximum file upload size in MB (default: 50)

### Optional Environment Variables

- `NEXT_PUBLIC_CONTENTFUL_SPACE_ID`: Contentful space ID (if using Contentful)
- `NEXT_PUBLIC_CONTENTFUL_ACCESS_TOKEN`: Contentful access token (if using Contentful)
- `NEXT_PUBLIC_SUPPORTED_FILE_TYPES`: Comma-separated list of supported file extensions
- `NEXT_PUBLIC_UPLOAD_RETENTION_DAYS`: Number of days uploaded files are retained
- `NEXT_PUBLIC_DEBUG_MODE`: Enable debug mode (true/false)

## Project Structure

### Directory Structure

```
src/web/
├── public/               # Static assets
├── src/
│   ├── app/              # Next.js App Router pages
│   ├── components/       # React components
│   │   ├── ui/           # Base UI components
│   │   ├── shared/       # Shared components
│   │   ├── forms/        # Form components
│   │   ├── layout/       # Layout components
│   │   ├── home/         # Homepage components
│   │   ├── services/     # Service-related components
│   │   ├── case-studies/ # Case study components
│   │   └── impact/       # Social impact components
│   ├── context/          # React context providers
│   ├── hooks/            # Custom React hooks
│   ├── lib/              # Third-party library integrations
│   ├── services/         # API and business logic services
│   ├── styles/           # Global styles and CSS variables
│   ├── types/            # TypeScript type definitions
│   ├── utils/            # Utility functions
│   └── constants/        # Application constants
├── tests/                # Test files
├── .env.example          # Example environment variables
├── .eslintrc.js          # ESLint configuration
├── .prettierrc           # Prettier configuration
├── docker-compose.yml    # Docker Compose configuration
├── Dockerfile            # Docker configuration
├── jest.config.ts        # Jest configuration
├── next.config.js        # Next.js configuration
├── package.json          # Project dependencies and scripts
├── postcss.config.js     # PostCSS configuration
├── tailwind.config.ts    # TailwindCSS configuration
└── tsconfig.json         # TypeScript configuration
```

## Key Components

### UI Components

- `Button.tsx`: Reusable button component with various styles and states
- `Input.tsx`: Text input component with validation integration
- `Card.tsx`: Container component for content sections
- `Modal.tsx`: Dialog component for overlays and popups
- `Form components`: Specialized components for form handling and validation

### Feature Components

- `ServiceCard.tsx`: Displays individual AI services with icons and descriptions
- `FileUploadForm.tsx`: Handles file uploads with drag-and-drop functionality
- `DemoRequestForm.tsx`: Form for requesting service demonstrations
- `QuoteRequestForm.tsx`: Form for requesting price quotes
- `ImpactStory.tsx`: Displays social impact stories and metrics

### Custom Hooks

- `useFileUpload.tsx`: Manages file upload state and processing
- `useForm.tsx`: Custom hook for form state management
- `useBreakpoint.tsx`: Provides responsive breakpoint detection
- `useAnalytics.tsx`: Handles analytics tracking

## Available Scripts

### Development Scripts

- `yarn dev`: Starts the development server
- `yarn build`: Builds the application for production
- `yarn start`: Starts the production server
- `yarn lint`: Runs ESLint to check for code issues
- `yarn lint:fix`: Automatically fixes ESLint issues where possible
- `yarn format`: Runs Prettier to format code

### Testing Scripts

- `yarn test`: Runs Jest tests
- `yarn test:watch`: Runs Jest in watch mode
- `yarn test:coverage`: Generates test coverage report
- `yarn analyze`: Analyzes bundle size

### Type Checking

- `yarn type-check`: Runs TypeScript compiler to check types without emitting files

## Development Workflow

### Code Style and Quality

This project uses ESLint and Prettier to enforce code style and quality. Pre-commit hooks are set up with Husky to ensure that all committed code meets the project standards.

- Follow the existing code style and patterns
- Write meaningful commit messages
- Include tests for new features and bug fixes
- Ensure accessibility compliance for UI changes

### Testing Guidelines

- Write tests for all new features and bug fixes
- Focus on testing behavior rather than implementation details
- Aim for high test coverage, especially for critical paths
- Use mock data and services for API-dependent tests

### Pull Request Process

1. Create a feature branch from develop
2. Implement changes with appropriate tests
3. Ensure all tests pass with `yarn test`
4. Submit a pull request to the develop branch
5. Address any review comments
6. Once approved, changes will be merged

## Deployment

### Build for Production

To build the application for production:

```bash
yarn build
```

This will create an optimized production build in the `.next` directory.

### Docker Deployment

To build and deploy using Docker:

```bash
# Build the production image
docker build --target production -t indivillage-web:prod .

# Run the container
docker run -p 3000:3000 indivillage-web:prod
```

### Deployment Environments

- **Development**: Automatic deployment from the develop branch
- **Staging**: Deployment from the staging branch after approval
- **Production**: Deployment from the main branch after approval

## Troubleshooting

### Common Issues

- **Module not found errors**: Run `yarn install` to ensure all dependencies are installed
- **Environment variable issues**: Check that `.env.local` is properly configured
- **Build errors**: Make sure Node.js version is 18.x or higher
- **API connection issues**: Verify that `NEXT_PUBLIC_API_URL` is correctly set

## Performance Optimization

The application implements various performance optimizations:

- Next.js Image component for automatic image optimization
- Code splitting and lazy loading for improved initial load time
- Static generation for content-heavy pages
- Caching strategies for API responses and static assets
- Bundle analysis for identifying and reducing large dependencies

## Accessibility

The application is designed to meet WCAG 2.1 AA standards for accessibility:

- Semantic HTML structure
- ARIA attributes for interactive elements
- Keyboard navigation support
- Color contrast compliance
- Screen reader compatibility

Run accessibility checks during development with the axe DevTools browser extension.

## Resources

### Documentation

- [Next.js Documentation](https://nextjs.org/docs)
- [React Documentation](https://reactjs.org/docs)
- [TypeScript Documentation](https://www.typescriptlang.org/docs)
- [TailwindCSS Documentation](https://tailwindcss.com/docs)
- [Project Architecture](../../docs/web/README.md)
- [Component Documentation](../../docs/web/components.md)
- [Accessibility Guidelines](../../docs/web/accessibility.md)

## License

Copyright © 2023 IndiVillage. All rights reserved.