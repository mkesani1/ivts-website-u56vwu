import { setupServer } from 'msw/node'; // version ^1.2.1
import '@testing-library/jest-dom'; // version ^5.16.5
import { afterAll, afterEach, beforeAll } from '@jest/globals'; // version ^29.5.0
import { handlers } from './mocks/handlers';

/**
 * Sets up the MSW server with the provided request handlers
 * This allows us to intercept and mock API requests during tests
 */
export const server = setupServer(...handlers);

// Start the MSW server before all tests
beforeAll(() => {
  server.listen({ onUnhandledRequest: 'warn' });
  console.log('MSW server started');
});

// Reset any request handlers that were added during the tests
// so they don't affect other tests
afterEach(() => {
  server.resetHandlers();
});

// Clean up after all tests are done
afterAll(() => {
  server.close();
  console.log('MSW server closed');
});

// Mock window.matchMedia for testing responsive components
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

// Mock window.scrollTo for testing scroll behavior
window.scrollTo = jest.fn();

// Mock IntersectionObserver for testing components that use it
Object.defineProperty(window, 'IntersectionObserver', {
  writable: true,
  value: jest.fn().mockImplementation(() => ({
    observe: jest.fn(),
    unobserve: jest.fn(),
    disconnect: jest.fn(),
    root: null,
    rootMargin: '',
    thresholds: [],
  })),
});

// Mock environment variables needed for tests
process.env.NEXT_PUBLIC_API_URL = 'http://localhost:3000/api/v1';
process.env.NEXT_PUBLIC_RECAPTCHA_SITE_KEY = 'test-recaptcha-site-key';