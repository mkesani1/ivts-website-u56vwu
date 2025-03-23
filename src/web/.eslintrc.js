module.exports = {
  root: true,
  parser: '@typescript-eslint/parser',
  parserOptions: {
    ecmaVersion: 2020,
    sourceType: 'module',
    ecmaFeatures: {
      jsx: true,
    },
    project: './tsconfig.json',
  },
  extends: [
    'eslint:recommended', // v8.22.0
    'plugin:@typescript-eslint/recommended', // v5.30.7
    'plugin:react/recommended', // v7.30.1
    'plugin:react-hooks/recommended', // v4.6.0
    'plugin:jsx-a11y/recommended', // v6.6.1
    'plugin:jest/recommended', // v26.8.7
    'next/core-web-vitals', // v12.2.5
    'prettier', // v8.5.0
  ],
  plugins: [
    '@typescript-eslint', // v5.30.7
    'react', // v7.30.1
    'react-hooks', // v4.6.0
    'jsx-a11y', // v6.6.1
    'jest', // v26.8.7
  ],
  settings: {
    react: {
      version: 'detect',
    },
    'import/resolver': {
      typescript: {
        alwaysTryTypes: true,
      },
      node: {
        extensions: ['.js', '.jsx', '.ts', '.tsx'],
      },
    },
  },
  env: {
    browser: true,
    node: true,
    es6: true,
    jest: true,
  },
  rules: {
    // React specific rules
    'react/react-in-jsx-scope': 'off', // Not needed in Next.js
    'react/prop-types': 'off', // We're using TypeScript instead
    'react-hooks/rules-of-hooks': 'error', // Enforce Rules of Hooks
    'react-hooks/exhaustive-deps': 'warn', // Warn about missing dependencies
    
    // TypeScript specific rules
    '@typescript-eslint/explicit-module-boundary-types': 'off', // Often too verbose for React components
    '@typescript-eslint/no-unused-vars': ['error', { 
      argsIgnorePattern: '^_', 
      varsIgnorePattern: '^_' 
    }], // Allow unused variables that start with underscore
    '@typescript-eslint/no-explicit-any': 'warn', // Discourage 'any' type but don't error
    
    // Accessibility rules
    'jsx-a11y/anchor-is-valid': ['error', {
      components: ['Link'],
      specialLink: ['hrefLeft', 'hrefRight'],
      aspects: ['invalidHref', 'preferButton'],
    }], // Special case for Next.js Link component
    
    // Security and best practices
    'no-console': ['warn', { allow: ['warn', 'error'] }], // Discourage console.log in production
    
    // Testing rules
    'jest/no-disabled-tests': 'warn', // Warn about disabled tests
    'jest/no-focused-tests': 'error', // Error on focused tests which can disrupt test suites
    'jest/valid-expect': 'error', // Ensure expect statements are valid
  },
  overrides: [
    // Test files can have different rules
    {
      files: ['**/*.test.ts', '**/*.test.tsx', '**/tests/**/*'],
      env: {
        jest: true,
      },
      rules: {
        '@typescript-eslint/no-explicit-any': 'off', // Allow 'any' in tests for flexibility
      },
    },
    // API routes are Node.js environment
    {
      files: ['src/pages/api/**/*'],
      env: {
        node: true,
      },
    },
  ],
  ignorePatterns: [
    'node_modules/',
    '.next/',
    'out/',
    'public/',
    'coverage/',
    '**/*.js', // Ignore all JavaScript files by default
    '!.eslintrc.js', // But not this config file
  ],
};