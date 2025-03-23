import type { Config } from '@jest/types'; // v29.5.0

// Configuration object for Jest testing framework
const config: Config.InitialOptions = {
  // Test environment - using jsdom to simulate a browser environment for React component testing
  testEnvironment: 'jsdom',
  
  // Setup files to run after Jest is initialized
  setupFilesAfterEnv: ['<rootDir>/tests/setup.ts'],
  
  // File patterns to match for test files
  testMatch: ['**/?(*.)+(spec|test).(ts|tsx)'],
  
  // Directories to ignore when looking for test files
  testPathIgnorePatterns: [
    '/node_modules/',
    '/.next/',
    '/out/',
    '/dist/',
    '/coverage/'
  ],
  
  // File transformations
  transform: {
    '^.+\\.(ts|tsx)$': ['babel-jest', { presets: ['next/babel'] }]
  },
  
  // Module name mappings for easier imports in test files
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1',
    '^@components/(.*)$': '<rootDir>/src/components/$1',
    '^@utils/(.*)$': '<rootDir>/src/utils/$1',
    '^@hooks/(.*)$': '<rootDir>/src/hooks/$1',
    '^@services/(.*)$': '<rootDir>/src/services/$1',
    '^@types/(.*)$': '<rootDir>/src/types/$1',
    '^@constants/(.*)$': '<rootDir>/src/constants/$1',
    '^@context/(.*)$': '<rootDir>/src/context/$1',
    '^@styles/(.*)$': '<rootDir>/src/styles/$1',
    '^@lib/(.*)$': '<rootDir>/src/lib/$1',
    '^@mocks/(.*)$': '<rootDir>/tests/mocks/$1',
    '\\.(css|less|scss|sass)$': 'identity-obj-proxy'
  },
  
  // Files to collect coverage from
  collectCoverageFrom: [
    'src/**/*.{ts,tsx}',
    '!src/**/*.d.ts',
    '!src/**/_*.{ts,tsx}',
    '!src/**/index.{ts,tsx}',
    '!src/pages/_*.{ts,tsx}',
    '!src/types/**/*'
  ],
  
  // Coverage thresholds
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80
    }
  },
  
  // Watch plugins for better developer experience
  watchPlugins: [
    'jest-watch-typeahead/filename',
    'jest-watch-typeahead/testname'
  ],
  
  // Reset mocks between tests
  resetMocks: true,
  
  // Clear mocks between tests
  clearMocks: true,
  
  // Test timeout in milliseconds
  testTimeout: 10000,
  
  // Verbose output
  verbose: true
};

export default config;