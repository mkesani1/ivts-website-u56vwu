# Testing Strategy for IndiVillage.com

## Introduction

This document outlines the testing strategy for the IndiVillage.com website project. It provides guidelines for developers on how to write, run, and maintain tests across both frontend and backend components. The testing approach is designed to ensure high quality, reliability, and security of the application while supporting the development workflow.

## Testing Philosophy

The IndiVillage.com project follows a comprehensive testing approach that emphasizes test-driven development, automated testing, and continuous integration. Our testing philosophy is based on the following principles:

- **Test Early, Test Often**: Tests should be written alongside or before the code they verify
- **Automation First**: Prioritize automated tests over manual testing wherever possible
- **Risk-Based Testing**: Focus testing efforts on critical functionality and high-risk areas
- **Shift Left**: Identify issues as early as possible in the development lifecycle
- **Comprehensive Coverage**: Aim for high test coverage across all application layers
- **Maintainable Tests**: Write clear, concise tests that are easy to understand and maintain

## Testing Levels

The testing strategy includes multiple levels of testing to ensure comprehensive coverage of the application:

### Unit Testing

Unit tests verify individual components in isolation, focusing on specific functions, methods, or components.

**Frontend Unit Testing:**
- Uses Jest and React Testing Library
- Tests are co-located with components (`Component.tsx` paired with `Component.test.tsx`)
- Focuses on component rendering, state changes, and user interactions
- Mocks external dependencies and services

**Backend Unit Testing:**
- Uses pytest with unittest for Python code
- Tests are organized in a parallel directory structure (`tests/unit/module_name/`)
- Focuses on business logic, data transformations, and error handling
- Uses pytest fixtures for dependency injection and test setup

**Code Coverage Requirements:**
- Overall coverage target: 80%
- Critical paths: 90% coverage
- Utility functions: 100% coverage

### Integration Testing

Integration tests verify that different components work together correctly.

**Frontend Integration Testing:**
- Tests interactions between multiple components
- Verifies state management across component boundaries
- Tests form submissions and API interactions with mocked responses

**Backend Integration Testing:**
- Tests API endpoints with actual database interactions
- Verifies service interactions and data flow between components
- Uses containerized dependencies (PostgreSQL, Redis) for realistic testing

**API Testing:**
- Verifies API contracts and responses
- Tests authentication, authorization, and error handling
- Validates request validation and response formats

### End-to-End Testing

End-to-end tests verify complete user journeys and business flows.

**Key E2E Test Scenarios:**
1. Complete demo request journey
2. File upload and processing flow
3. Service exploration and information gathering
4. Social impact story navigation
5. Mobile responsive behavior verification

**Tools:**
- Cypress for browser testing
- Playwright for cross-browser testing

**Implementation Approach:**
- Page Object Model for UI interaction
- Database seeding for test data setup
- Isolated test environments to prevent interference

### Performance Testing

Performance tests verify that the application meets performance requirements.

**Types of Performance Tests:**
- Load testing: Simulate 100 concurrent users with normal usage patterns
- Stress testing: Ramp up to 500 concurrent users to identify breaking points
- Endurance testing: Maintain moderate load (50 users) for 24 hours

**Tools:**
- k6 for API load testing
- Lighthouse for frontend performance

**Key Metrics:**
- Page load time: < 2 seconds
- API response time: < 300ms (95th percentile)
- Time to Interactive: < 3.5 seconds
- First Contentful Paint: < 1.5 seconds

### Security Testing

Security tests verify that the application is secure against common vulnerabilities.

**Types of Security Tests:**
- Static Application Security Testing (SAST): SonarQube, ESLint security rules
- Dynamic Application Security Testing (DAST): OWASP ZAP
- Dependency scanning: npm audit, safety
- Penetration testing: Manual testing by security team

**Focus Areas:**
1. Authentication and authorization
2. Input validation and sanitization
3. File upload security
4. API security (rate limiting, input validation)
5. Data protection and privacy
6. Third-party integration security

### Accessibility Testing

Accessibility tests verify that the application meets WCAG 2.1 AA standards.

**Types of Accessibility Tests:**
- Automated scans: axe-core, Lighthouse
- Screen reader testing: NVDA, VoiceOver
- Contrast checking: Contrast Analyzer
- Keyboard navigation: Manual testing

**Key Requirements:**
- All interactive elements must be keyboard accessible
- Proper heading structure and semantic HTML
- Sufficient color contrast (4.5:1 ratio)
- Appropriate alt text for images
- ARIA attributes where necessary

## Testing Tools and Frameworks

The IndiVillage.com project uses the following tools and frameworks for testing:

### Frontend Testing Tools

- **Jest**: Primary test runner and assertion library
- **React Testing Library**: Component testing with user-centric approach
- **Cypress**: End-to-end testing in browser environment
- **Playwright**: Cross-browser testing
- **MSW (Mock Service Worker)**: API mocking for component and integration tests
- **Testing Library User Event**: Simulating user interactions
- **Jest Axe**: Accessibility testing
- **Lighthouse**: Performance and best practices testing

### Backend Testing Tools

- **pytest**: Primary test framework for Python code
- **pytest-cov**: Code coverage reporting
- **pytest-mock**: Mocking functionality
- **pytest-xdist**: Parallel test execution
- **pytest-flask**: Flask-specific testing utilities
- **factory_boy**: Test data generation
- **Faker**: Random test data generation
- **unittest.mock**: Mocking functionality from standard library

### CI/CD Integration

- **GitHub Actions**: Automated test execution in CI pipeline
- **JUnit XML**: Test result reporting
- **Codecov/Coveralls**: Code coverage reporting and tracking
- **SonarQube**: Code quality and security analysis
- **Trivy**: Container and dependency scanning

## Test Organization

Tests are organized according to the following structure:

### Frontend Test Organization

```
src/web/
├── src/
│   ├── components/
│   │   ├── ui/
│   │   │   ├── Button.tsx
│   │   │   └── Button.test.tsx  # Co-located component test
│   ├── hooks/
│   │   ├── useForm.ts
│   │   └── useForm.test.ts      # Co-located hook test
├── tests/
│   ├── setup.ts                 # Test setup configuration
│   ├── mocks/
│   │   ├── data.ts              # Mock data for tests
│   │   └── handlers.ts          # MSW API mock handlers
│   ├── components/
│   │   ├── ui/
│   │   │   └── Button.test.tsx  # Alternative location for component tests
│   ├── hooks/
│   │   └── useForm.test.ts      # Alternative location for hook tests
│   ├── pages/
│   │   ├── home.test.tsx        # Page component tests
│   │   └── upload.test.tsx      # Page component tests
│   ├── utils/
│   │   └── validation.test.ts   # Utility function tests
│   └── e2e/
│       └── upload.spec.ts       # Cypress E2E tests
```

### Backend Test Organization

```
src/backend/
├── app/
│   ├── api/
│   ├── services/
│   └── utils/
├── tests/
│   ├── conftest.py              # Test fixtures and configuration
│   ├── test_config.py           # Configuration tests
│   ├── api/
│   │   ├── test_services.py     # API endpoint tests
│   │   └── test_uploads.py      # API endpoint tests
│   ├── services/
│   │   ├── test_content_service.py  # Service layer tests
│   │   └── test_file_upload_service.py
│   ├── utils/
│   │   └── test_validation_utils.py  # Utility function tests
│   ├── integrations/
│   │   ├── test_contentful.py   # External integration tests
│   │   └── test_hubspot.py
│   └── security/
│       └── test_file_scanner.py  # Security-related tests
```

### Test Naming Conventions

**Frontend Test Naming:**
```typescript
describe('ComponentName', () => {
  it('should render correctly with props', () => {...})
  it('should handle user interaction', () => {...})
})
```

**Backend Test Naming:**
```python
def test_function_name_expected_behavior_when_condition():
    # Test implementation
```

## Writing Effective Tests

Guidelines for writing effective tests:

### Frontend Testing Best Practices

1. **Test behavior, not implementation**: Focus on what the component does, not how it's implemented
2. **Use user-centric queries**: Prefer `getByRole`, `getByLabelText`, and `getByText` over `getByTestId`
3. **Test accessibility**: Include basic accessibility checks in component tests
4. **Keep tests simple**: Each test should verify one specific behavior
5. **Use realistic user interactions**: Use `userEvent` instead of `fireEvent` when possible
6. **Avoid snapshot testing**: Prefer explicit assertions over snapshots
7. **Mock external dependencies**: Use MSW to mock API calls
8. **Test error states**: Verify that components handle errors gracefully
9. **Test loading states**: Verify that components show appropriate loading indicators
10. **Test responsive behavior**: Verify that components adapt to different screen sizes

### Backend Testing Best Practices

1. **Use fixtures for test data**: Create reusable fixtures for common test data
2. **Isolate tests**: Each test should be independent and not rely on state from other tests
3. **Use parameterized tests**: Test multiple input variations with parameterized tests
4. **Mock external services**: Use mocks for external services and APIs
5. **Test edge cases**: Include tests for boundary conditions and error cases
6. **Test security constraints**: Verify that security controls work as expected
7. **Use appropriate assertions**: Choose specific assertions that clearly express the expected outcome
8. **Clean up after tests**: Ensure tests clean up any resources they create
9. **Test database interactions**: Verify that database operations work correctly
10. **Test API contracts**: Ensure API endpoints adhere to their specified contracts

### Test Data Management

**Test Data Sources:**
- Static fixtures for common test cases
- Factory functions for generating test data with variations
- In-memory databases for data-dependent tests
- Environment-specific test data for integration tests

**Test Data Principles:**
- Tests should create the data they need
- Tests should not depend on external data sources
- Test data should be realistic but minimal
- Sensitive data should not be used in tests

### Coding Standards Validation

Tests should help validate that code adheres to project coding standards:

- Verify that components follow accessibility standards
- Ensure backend code follows security best practices
- Validate that API endpoints follow RESTful conventions
- Check that error handling follows project guidelines
- Confirm that performance requirements are met

Tests serve as executable documentation of these standards and help ensure consistent implementation across the codebase.

## Project Setup and Running Tests

Instructions for setting up the project and running tests in different environments:

### Initial Project Setup

**Frontend Setup:**
```bash
# Clone the repository
git clone https://github.com/indivillage/indivillage-website.git
cd indivillage-website

# Install dependencies for web project
cd src/web
yarn install
```

**Backend Setup:**
```bash
# From the project root
cd src/backend

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

**Environment Configuration:**
- Copy `.env.example` to `.env` in both frontend and backend directories
- Configure environment variables as needed for local development

### Running Frontend Tests

**Running All Tests:**
```bash
cd src/web
yarn test
```

**Running Tests in Watch Mode:**
```bash
yarn test:watch
```

**Running Tests with Coverage:**
```bash
yarn test:coverage
```

**Running a Specific Test File:**
```bash
yarn test Button.test.tsx
```

**Running E2E Tests:**
```bash
yarn cypress:open  # Interactive mode
yarn cypress:run   # Headless mode
```

### Running Backend Tests

**Running All Tests:**
```bash
cd src/backend
pytest
```

**Running Tests with Coverage:**
```bash
pytest --cov=app
```

**Running a Specific Test File:**
```bash
pytest tests/api/test_uploads.py
```

**Running Tests by Marker:**
```bash
pytest -m unit          # Run unit tests only
pytest -m integration   # Run integration tests only
pytest -m "not slow"   # Skip slow tests
```

### Running Tests in CI/CD

Tests are automatically run in the CI/CD pipeline on pull requests and pushes to main branches. The CI workflow includes:

1. Linting and static analysis
2. Unit tests for frontend and backend
3. Integration tests
4. Build verification
5. Security scanning
6. End-to-end tests

Test results and coverage reports are available in the GitHub Actions workflow summary.

## Test Environments

The project uses different environments for testing:

### Local Development Environment

- Used for development and unit testing
- Mocked external services
- In-memory or containerized databases
- Fast feedback loop for developers

### CI Environment

- Used for automated testing in the CI pipeline
- Containerized services for integration testing
- Isolated test databases
- Mocked external APIs

### Staging Environment

- Used for end-to-end testing and manual testing
- Production-like configuration
- Sandbox external APIs
- Isolated from production data

## Handling Flaky Tests

Strategies for dealing with flaky tests:

### Identifying Flaky Tests

- Monitor test success rate over time
- Track tests that fail intermittently
- Use test result history to identify patterns

### Fixing Flaky Tests

Common causes of flaky tests and how to fix them:

1. **Timing issues**: Add appropriate waits or use async/await properly
2. **Order dependencies**: Ensure tests are isolated and don't depend on execution order
3. **Shared state**: Reset state between tests
4. **External dependencies**: Mock external services consistently
5. **Race conditions**: Use proper synchronization mechanisms
6. **Resource constraints**: Ensure sufficient resources for test execution

### Quarantine Process

For tests that cannot be immediately fixed:

1. Move flaky tests to a separate suite marked with `@flaky` or `-m flaky`
2. Run flaky tests in a separate job that doesn't block the build
3. Prioritize fixing the most impactful flaky tests
4. Regularly review quarantined tests

## Code Coverage

Code coverage requirements and tracking:

### Coverage Targets

- Overall coverage target: 80%
- Critical paths: 90% coverage
- Utility functions: 100% coverage

### Coverage Reporting

- Frontend: Jest coverage reports
- Backend: pytest-cov reports
- CI/CD: Codecov or Coveralls integration
- Coverage trends tracked over time

### Coverage Enforcement

- Pull requests must maintain or improve coverage
- Critical code paths have stricter coverage requirements
- Coverage reports are generated for each build
- Coverage thresholds are enforced in CI

## Testing Responsibilities

Roles and responsibilities for testing:

### Developer Responsibilities

- Write unit tests for all new code
- Maintain existing tests
- Fix failing tests in their areas of responsibility
- Ensure tests run successfully locally before pushing
- Review test coverage in pull requests

### QA Engineer Responsibilities

- Develop and maintain end-to-end tests
- Create and execute test plans for new features
- Perform exploratory testing
- Identify gaps in test coverage
- Coordinate user acceptance testing

### DevOps Responsibilities

- Maintain test infrastructure
- Ensure CI/CD pipeline includes all test types
- Monitor test performance and stability
- Provide tools for test result analysis
- Support test environment provisioning

## Development Workflow for Testing

The standard workflow for incorporating testing into the development process includes:

1. **Before coding**: Understand requirements and plan test scenarios
2. **During development**: Write unit tests alongside code implementation
3. **Before PR submission**: Ensure all tests pass locally
4. **During PR review**: Review test coverage and test quality
5. **After merge**: Automated tests run in CI/CD pipeline

This approach ensures that testing is integrated throughout the development lifecycle rather than treated as a separate phase. Tests should be considered as important as the code they verify and maintained with the same level of care.

## Continuous Improvement

Processes for improving the testing strategy:

### Test Retrospectives

- Regular review of test effectiveness
- Identification of testing gaps
- Analysis of escaped defects
- Improvement of test processes

### Test Metrics

Key metrics to track:

- Test coverage percentage
- Test execution time
- Number of flaky tests
- Defect detection rate
- Escaped defects
- Test maintenance cost

### Learning Resources

Recommended resources for improving testing skills:

- [React Testing Library documentation](https://testing-library.com/docs/react-testing-library/intro/)
- [Jest documentation](https://jestjs.io/docs/getting-started)
- [pytest documentation](https://docs.pytest.org/)
- [Testing JavaScript](https://testingjavascript.com/) by Kent C. Dodds
- [Python Testing with pytest](https://pragprog.com/titles/bopytest/python-testing-with-pytest/) by Brian Okken