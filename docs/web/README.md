# IndiVillage Website Frontend Documentation

This documentation provides comprehensive information about the IndiVillage website frontend implementation. The website is built using Next.js, React, TypeScript, and TailwindCSS, following modern web development practices to create a responsive, accessible, and performant user experience.

## Technology Stack

The IndiVillage website frontend is built with the following technologies:

| Technology | Version | Purpose |
|------------|---------|----------|
| Next.js | 13.4+ | React framework with server-side rendering and static site generation |
| React | 18.2+ | UI library for component-based development |
| TypeScript | 4.9+ | Type-safe JavaScript for improved developer experience |
| TailwindCSS | 3.3+ | Utility-first CSS framework for styling |
| Framer Motion | 10.12+ | Animation library for enhanced user experience |
| React Hook Form | 7.45+ | Form handling with validation |
| React Query | 4.29+ | Data fetching and state management |
| React Dropzone | 14.2+ | File upload functionality |
| Jest | 29.5+ | Testing framework |
| React Testing Library | 14.0+ | Component testing utilities |
| ESLint | 8.40+ | Code linting |
| Prettier | 2.8+ | Code formatting |

### Key Dependencies

- **@hookform/resolvers**: Form validation schema integration
- **axios**: HTTP client for API requests
- **next-seo**: SEO optimization for Next.js
- **react-intersection-observer**: Intersection observer for lazy loading
- **react-toastify**: Toast notifications
- **zod**: Schema validation library
- **tailwind-merge**: Utility for merging Tailwind classes
- **clsx**: Utility for conditional class names

### Development Dependencies

- **@testing-library/jest-dom**: Custom Jest matchers for DOM testing
- **@testing-library/react**: React component testing utilities
- **@types/node**, **@types/react**: TypeScript type definitions
- **autoprefixer**, **postcss**: CSS processing
- **msw**: Mock Service Worker for API mocking in tests
- **cypress**: End-to-end testing framework
- **axe-core**: Accessibility testing library

## Project Structure

The frontend codebase follows a well-organized structure to promote maintainability and scalability:

```
src/
├── app/                    # Next.js App Router pages and layouts
│   ├── layout.tsx          # Root layout component
│   ├── page.tsx            # Homepage
│   ├── about/              # About section pages
│   ├── services/           # Service pages
│   ├── case-studies/       # Case study pages
│   ├── impact/             # Social impact pages
│   ├── request-demo/       # Demo request page
│   ├── upload-sample/      # File upload pages
│   └── api/                # API routes
├── components/             # React components
│   ├── ui/                 # Base UI components
│   ├── shared/             # Shared components
│   ├── layout/             # Layout components
│   ├── forms/              # Form components
│   ├── home/               # Homepage-specific components
│   ├── services/           # Service-specific components
│   ├── case-studies/       # Case study components
│   └── impact/             # Impact-specific components
├── context/                # React context providers
├── hooks/                  # Custom React hooks
├── lib/                    # Third-party library integrations
├── services/               # API service modules
├── styles/                 # Global styles and CSS variables
├── types/                  # TypeScript type definitions
├── utils/                  # Utility functions
└── constants/              # Constants and configuration
```

### Key Directories

- **app/**: Next.js App Router pages and API routes
- **components/**: Reusable React components organized by type and feature
- **context/**: React Context providers for global state management
- **hooks/**: Custom React hooks for shared logic
- **services/**: API service modules for data fetching
- **styles/**: Global styles and CSS variables
- **utils/**: Utility functions for common operations

### Naming Conventions

- **Files**: PascalCase for components (e.g., `Button.tsx`), camelCase for utilities (e.g., `fetcher.ts`)
- **Components**: PascalCase (e.g., `ServiceCard`)
- **Functions**: camelCase (e.g., `formatDate`)
- **Constants**: UPPER_SNAKE_CASE for global constants, PascalCase for exported objects
- **Types/Interfaces**: PascalCase with descriptive names (e.g., `ServiceData`)
- **CSS Classes**: Tailwind utility classes, with custom classes in kebab-case when needed

## Core Features

The IndiVillage website frontend implements several key features to showcase the company's AI services and social impact mission:

### Modern Responsive Design

The website features a modern, responsive design that adapts to different screen sizes and devices. Key aspects include:

- Mobile-first approach with responsive breakpoints
- Fluid typography and spacing
- Optimized images for different screen sizes
- Touch-friendly interface elements
- Consistent branding and visual language

See [components.md](./components.md) for detailed information about UI components and design implementation.

### AI Service Portfolio Showcase

The service portfolio showcase presents IndiVillage's AI-as-a-service offerings in an engaging and informative way:

- Service overview with categorized listings
- Detailed service pages with features and benefits
- Interactive service process visualization
- Related case studies for each service
- Call-to-action elements for service inquiries

The services are implemented using a modular approach with components like ServiceCard, ServiceDetail, and ServiceFeature to ensure consistency and maintainability. Each service page implements static generation for optimal performance with dynamic elements for interactive features.

### Sample Data Upload Functionality

The file upload functionality allows potential clients to upload sample datasets for analysis:

- Drag-and-drop file upload interface
- File type and size validation
- Upload progress tracking
- Secure direct-to-S3 uploads
- Processing status updates
- Results presentation

See [components.md](./components.md) for details on the upload components and [state-management.md](./state-management.md) for information about upload state management.

### Demo/Quote Request System

The form submission system handles demo requests, quote requests, and general inquiries:

- Form validation with real-time feedback
- Multi-step forms for complex requests
- CAPTCHA protection against spam
- Submission to CRM via API
- Confirmation messages and emails

The form system is built using React Hook Form with Zod validation schemas. Form submissions are processed through API routes that integrate with the backend services for CRM integration and email notifications.

### Social Impact Storytelling

The social impact section showcases IndiVillage's mission and community impact:

- Impact metrics visualization
- Community stories with rich media
- Interactive elements for engagement
- SDG alignment presentation
- Foundation information integration

The impact pages use a combination of static content and interactive elements to create an engaging narrative about IndiVillage's social mission. Key components include ImpactMetrics for data visualization, ImpactStory for narrative presentation, and SDGSection for displaying sustainable development goal alignment.

## Development Guidelines

This section provides guidelines for frontend development on the IndiVillage website project.

### Getting Started

To set up the development environment:

1. Clone the repository
2. Install dependencies with `yarn install`
3. Copy `.env.example` to `.env.local` and configure environment variables
4. Start the development server with `yarn dev`
5. Access the site at `http://localhost:3000`

For more detailed setup instructions, see the project README.md file.

### Development Workflow

The development workflow follows these steps:

1. Create a feature branch from `develop`
2. Implement the feature or fix
3. Write tests for the changes
4. Ensure all tests pass with `yarn test`
5. Ensure code quality with `yarn lint`
6. Submit a pull request to `develop`
7. Address review feedback
8. Merge to `develop` after approval

The CI/CD pipeline will automatically build, test, and deploy changes to the appropriate environment.

### Coding Standards

Follow these coding standards for consistency:

- Use TypeScript for all new code
- Follow the ESLint and Prettier configurations
- Write meaningful comments for complex logic
- Use descriptive variable and function names
- Keep components focused and composable
- Follow the React hooks rules
- Implement proper error handling
- Write unit tests for components and utilities

### Performance Considerations

Keep these performance considerations in mind:

- Use appropriate rendering strategies (SSG, SSR, CSR)
- Implement code splitting for large components
- Optimize images with Next.js Image component
- Minimize JavaScript bundle size
- Use memoization for expensive calculations
- Implement efficient state management
- Follow loading best practices
- Monitor and optimize Core Web Vitals

### Accessibility Requirements

The website must meet WCAG 2.1 AA compliance standards:

- Use semantic HTML elements
- Ensure keyboard navigation
- Provide text alternatives for non-text content
- Maintain sufficient color contrast
- Implement ARIA attributes appropriately
- Ensure form accessibility
- Test with screen readers

See [accessibility.md](./accessibility.md) for detailed accessibility implementation guidelines.

## Architecture Overview

The frontend architecture follows modern best practices for React and Next.js applications.

### Next.js App Router

The website uses Next.js App Router for routing and rendering:

- File-based routing with nested layouts
- Server Components for improved performance
- Static Site Generation for content-heavy pages
- Server-Side Rendering for dynamic content
- API Routes for backend functionality

The routing structure follows the project organization with dedicated routes for services, case studies, impact stories, and interactive features like demo requests and file uploads. Each route implements the appropriate rendering strategy based on its content and interaction requirements.

### Component Architecture

The component architecture follows a hierarchical approach:

- Atomic design principles (atoms, molecules, organisms)
- Composition over inheritance
- Container/presentation component pattern
- Reusable UI components
- Feature-specific components

See [components.md](./components.md) for detailed component documentation.

### State Management

State management uses a hybrid approach:

- React Context for global state
- React Query for server state
- React Hook Form for form state
- Custom hooks for complex state logic
- Local component state where appropriate

See [state-management.md](./state-management.md) for detailed state management documentation.

### Data Fetching

Data fetching follows these patterns:

- Server Components for direct data fetching
- React Query for client-side data fetching
- API service modules for consistent API access
- Error handling and loading states
- Caching and revalidation strategies

The application implements a consistent approach to data fetching with dedicated service modules that abstract API calls. Server components fetch data directly during rendering while client components use React Query for data fetching with built-in caching, refetching, and synchronization.

### Styling Approach

The styling approach uses TailwindCSS with some enhancements:

- Utility-first CSS with TailwindCSS
- Custom theme configuration
- Component-specific styles when needed
- CSS variables for theming
- Responsive design utilities

See [components.md](./components.md) for information about the design system implementation.

## Testing Strategy

The frontend implements a comprehensive testing strategy to ensure quality and reliability.

### Unit Testing

Unit tests focus on individual components and utilities:

- Jest as the test runner
- React Testing Library for component testing
- Mock Service Worker for API mocking
- Test coverage requirements
- Snapshot testing where appropriate

Run unit tests with `yarn test` or `yarn test:watch` for development.

### Integration Testing

Integration tests verify that components work together correctly:

- Testing component compositions
- Testing page rendering
- Testing user flows
- Testing form submissions
- Testing error states

### End-to-End Testing

End-to-end tests verify complete user journeys:

- Cypress for browser-based testing
- Critical user flow testing
- Cross-browser compatibility
- Mobile responsiveness
- Performance testing

Run E2E tests with `yarn test:e2e`.

### Accessibility Testing

Accessibility testing ensures WCAG 2.1 AA compliance:

- Automated testing with axe-core
- Manual testing with screen readers
- Keyboard navigation testing
- Color contrast verification
- Focus management testing

See [accessibility.md](./accessibility.md) for detailed accessibility testing information.

### Visual Regression Testing

Visual regression testing catches unintended visual changes:

- Screenshot comparison across builds
- Component visual testing
- Responsive layout testing
- Theme and styling verification

Run visual tests with `yarn test:visual`.

## Deployment

The frontend is deployed using a robust CI/CD pipeline.

### Build Process

The build process includes:

- TypeScript compilation
- Next.js build optimization
- Asset optimization
- Environment-specific configuration
- Bundle analysis

The production build is created with `yarn build`.

### Deployment Environments

The application is deployed to three environments:

- **Development**: For ongoing development and testing
- **Staging**: For pre-production validation
- **Production**: Live environment for end users

Each environment has its own configuration and deployment pipeline.

### CI/CD Pipeline

The CI/CD pipeline automates building, testing, and deployment:

- GitHub Actions for CI/CD automation
- Automated testing on pull requests
- Deployment to development on merge to develop
- Deployment to staging after approval
- Deployment to production after approval
- Automated rollback for failed deployments

### Monitoring and Analytics

The deployed application includes monitoring and analytics:

- Google Analytics for user behavior tracking
- Error tracking with Sentry
- Performance monitoring with Lighthouse CI
- Real User Monitoring (RUM)
- Custom event tracking for business metrics

## Additional Resources

For more detailed information, refer to these resources:

### Documentation

- [Components Documentation](./components.md): Detailed information about UI components
- [State Management Documentation](./state-management.md): Details on state management approach
- [Accessibility Documentation](./accessibility.md): Accessibility implementation guidelines
- System Architecture: Overall system architecture with details on frontend and backend integration

### External Resources

- [Next.js Documentation](https://nextjs.org/docs): Official Next.js documentation
- [React Documentation](https://reactjs.org/docs): Official React documentation
- [TailwindCSS Documentation](https://tailwindcss.com/docs): Official TailwindCSS documentation
- [TypeScript Documentation](https://www.typescriptlang.org/docs): Official TypeScript documentation

### Contributing

For information on contributing to the project, see the [Contributing Guide](../../CONTRIBUTING.md) in the repository root.