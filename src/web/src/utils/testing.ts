import React from 'react'; // version 18.2.0
import { render, screen, within, fireEvent, waitFor } from '@testing-library/react'; // version 14.0.0
import userEvent from '@testing-library/user-event'; // version 14.4.3
import { act } from 'react-dom/test-utils'; // version 18.2.0

// Import contexts
import { ToastContext } from '../context/ToastContext';
import { AnalyticsContext } from '../context/AnalyticsContext';
import { UploadContext } from '../context/UploadContext';

// Import types
import { FormValidationRules } from '../types/forms';
import { Service, CaseStudy, ImpactStory } from '../types/content';

/**
 * Renders a component wrapped with all necessary context providers for testing
 * @param ui - The component to render
 * @param options - Additional render options and context overrides
 * @returns The rendered component with testing utilities
 */
export const renderWithProviders = (
  ui: React.ReactElement, 
  options: {
    toastContextOverrides?: Partial<React.ContextType<typeof ToastContext>>,
    analyticsContextOverrides?: Partial<React.ContextType<typeof AnalyticsContext>>,
    uploadContextOverrides?: Partial<React.ContextType<typeof UploadContext>>,
    renderOptions?: Parameters<typeof render>[1]
  } = {}
) => {
  // Create mock context values with defaults
  const mockToastContext: React.ContextType<typeof ToastContext> = {
    toasts: [],
    showToast: jest.fn().mockImplementation(() => 'toast-id'),
    removeToast: jest.fn(),
    showSuccess: jest.fn().mockImplementation(() => 'success-toast-id'),
    showError: jest.fn().mockImplementation(() => 'error-toast-id'),
    showWarning: jest.fn().mockImplementation(() => 'warning-toast-id'),
    showInfo: jest.fn().mockImplementation(() => 'info-toast-id'),
    clearAll: jest.fn(),
    ...options.toastContextOverrides
  };

  const mockAnalyticsContext: React.ContextType<typeof AnalyticsContext> = {
    isInitialized: true,
    trackPageView: jest.fn(),
    trackEvent: jest.fn(),
    trackDemoRequest: jest.fn(),
    trackQuoteRequest: jest.fn(),
    trackContactForm: jest.fn(),
    trackFileUpload: jest.fn(),
    trackServiceView: jest.fn(),
    trackServiceInteraction: jest.fn(),
    trackCaseStudyView: jest.fn(),
    trackImpactStoryView: jest.fn(),
    trackWebVitals: jest.fn(),
    trackError: jest.fn(),
    setUserProperties: jest.fn(),
    ...options.analyticsContextOverrides
  };

  const mockUploadContext: React.ContextType<typeof UploadContext> = {
    uploadState: {
      file: null,
      status: 'pending',
      progress: {
        loaded: 0,
        total: 0,
        percentage: 0
      },
      uploadId: null,
      error: 'none',
      errorMessage: null,
      processingStep: null,
      estimatedTimeRemaining: null,
      analysisResult: null
    },
    uploadConfig: {
      maxSizeBytes: 50 * 1024 * 1024, // 50MB
      allowedTypes: ['csv', 'json', 'xml', 'image', 'audio'],
      acceptedMimeTypes: [
        'text/csv',
        'application/json',
        'application/xml',
        'text/xml',
        'image/jpeg',
        'image/png',
        'image/gif',
        'image/webp',
        'image/tiff',
        'audio/mp3',
        'audio/wav',
        'audio/ogg',
        'audio/mpeg'
      ],
      maxFileNameLength: 255
    },
    setUploadConfig: jest.fn(),
    validateFile: jest.fn().mockReturnValue({ valid: true, error: 'none', errorMessage: null }),
    handleFileSelect: jest.fn(),
    startUpload: jest.fn().mockResolvedValue(undefined),
    cancelUpload: jest.fn(),
    resetUpload: jest.fn(),
    ...options.uploadContextOverrides
  };

  // Wrap component with all providers
  const Wrapper = ({ children }: { children: React.ReactNode }) => (
    <ToastContext.Provider value={mockToastContext}>
      <AnalyticsContext.Provider value={mockAnalyticsContext}>
        <UploadContext.Provider value={mockUploadContext}>
          {children}
        </UploadContext.Provider>
      </AnalyticsContext.Provider>
    </ToastContext.Provider>
  );

  // Render with wrapper
  return {
    ...render(ui, { wrapper: Wrapper, ...options.renderOptions }),
    mockToastContext,
    mockAnalyticsContext,
    mockUploadContext
  };
};

/**
 * Creates a mock File object for testing file upload functionality
 * @param options - Options for creating the mock file
 * @returns A mock File object
 */
export const createMockFile = (options: {
  name?: string;
  type?: string;
  size?: number;
  content?: string;
} = {}) => {
  const {
    name = 'test-file.csv',
    type = 'text/csv',
    size = 1024,
    content = 'id,name,value\n1,test,100'
  } = options;

  // Create a Blob with the content
  const blob = new Blob([content], { type });
  
  // Create a File from the Blob
  return new File([blob], name, { type });
};

/**
 * Creates a mock FormData object for testing form submissions
 * @param data - Key-value pairs to add to the FormData
 * @returns A mock FormData object
 */
export const createMockFormData = (data: Record<string, any> = {}) => {
  const formData = new FormData();
  
  Object.entries(data).forEach(([key, value]) => {
    if (value instanceof File) {
      formData.append(key, value);
    } else if (Array.isArray(value)) {
      value.forEach(item => formData.append(key, item));
    } else {
      formData.append(key, String(value));
    }
  });
  
  return formData;
};

/**
 * Mocks the global fetch function for testing API calls
 * @param response - The response object to return
 * @param success - Whether the fetch should succeed or fail
 * @returns A jest mock function for fetch
 */
export const mockFetch = (response: any, success: boolean = true) => {
  const mockFetchImplementation = jest.fn().mockImplementation(() => {
    if (success) {
      return Promise.resolve({
        ok: true,
        status: 200,
        json: () => Promise.resolve(response)
      });
    } else {
      return Promise.resolve({
        ok: false,
        status: response.status || 400,
        json: () => Promise.resolve(response)
      });
    }
  });
  
  global.fetch = mockFetchImplementation;
  return mockFetchImplementation;
};

/**
 * Utility function to wait for an element to be removed from the DOM
 * @param element - The element or a function that returns the element
 * @param options - Additional options for waitFor
 * @returns Promise that resolves when element is removed
 */
export const waitForElementToBeRemoved = (
  element: HTMLElement | (() => HTMLElement),
  options?: Parameters<typeof waitFor>[1]
) => {
  return waitFor(
    () => {
      const el = typeof element === 'function' ? element() : element;
      expect(el).not.toBeInTheDocument();
    },
    options
  );
};

/**
 * Creates mock service data for testing service-related components
 * @param overrides - Properties to override in the default mock
 * @returns A mock Service object
 */
export const createMockService = (overrides: Partial<Service> = {}): Service => {
  return {
    id: 'service-1',
    title: 'Data Collection',
    slug: 'data-collection',
    description: 'Comprehensive data gathering solutions',
    category: 'dataCollection',
    features: [
      {
        id: 'feature-1',
        title: 'Automated Collection',
        description: 'Efficiently gather data from various sources',
        icon: {
          id: 'icon-1',
          title: 'Automation Icon',
          description: 'Icon representing automation',
          url: 'https://example.com/automation-icon.svg',
          width: 24,
          height: 24,
          contentType: 'image/svg+xml'
        }
      }
    ],
    icon: {
      id: 'service-icon-1',
      title: 'Data Collection Icon',
      description: 'Icon representing data collection',
      url: 'https://example.com/data-collection-icon.svg',
      width: 48,
      height: 48,
      contentType: 'image/svg+xml'
    },
    heroImage: {
      id: 'hero-1',
      title: 'Data Collection Hero',
      description: 'Hero image for data collection service',
      url: 'https://example.com/data-collection-hero.jpg',
      width: 1200,
      height: 600,
      contentType: 'image/jpeg'
    },
    howItWorks: '<p>Our data collection service works by...</p>',
    order: 1,
    createdAt: '2023-01-01T00:00:00Z',
    updatedAt: '2023-01-15T00:00:00Z',
    ...overrides
  };
};

/**
 * Creates mock case study data for testing case study components
 * @param overrides - Properties to override in the default mock
 * @returns A mock CaseStudy object
 */
export const createMockCaseStudy = (overrides: Partial<CaseStudy> = {}): CaseStudy => {
  return {
    id: 'case-study-1',
    title: 'E-commerce Product Categorization',
    slug: 'ecommerce-product-categorization',
    client: 'Major Retailer Inc.',
    industry: {
      id: 'industry-1',
      name: 'Retail',
      slug: 'retail'
    },
    challenge: 'The client needed to improve product search accuracy',
    solution: 'We implemented a custom AI model for categorization',
    results: [
      {
        id: 'result-1',
        metric: 'Search Accuracy',
        value: '40%',
        description: 'Improvement in search accuracy'
      }
    ],
    image: {
      id: 'case-study-image-1',
      title: 'E-commerce Case Study',
      description: 'Image for e-commerce case study',
      url: 'https://example.com/case-study.jpg',
      width: 800,
      height: 600,
      contentType: 'image/jpeg'
    },
    services: [createMockService()],
    createdAt: '2023-02-01T00:00:00Z',
    updatedAt: '2023-02-15T00:00:00Z',
    ...overrides
  };
};

/**
 * Creates mock impact story data for testing impact story components
 * @param overrides - Properties to override in the default mock
 * @returns A mock ImpactStory object
 */
export const createMockImpactStory = (overrides: Partial<ImpactStory> = {}): ImpactStory => {
  return {
    id: 'impact-story-1',
    title: 'Empowering Rural Communities',
    slug: 'empowering-rural-communities',
    story: '<p>Our center in Ramanagara created 200+ tech jobs in a previously agricultural community.</p>',
    excerpt: 'Creating tech jobs in rural areas',
    beneficiaries: 'Rural residents of Ramanagara',
    location: {
      id: 'location-1',
      name: 'Ramanagara',
      region: 'Karnataka',
      country: 'India'
    },
    media: [
      {
        id: 'media-1',
        title: 'Ramanagara Center',
        description: 'Image of our center in Ramanagara',
        url: 'https://example.com/ramanagara.jpg',
        width: 800,
        height: 600,
        contentType: 'image/jpeg'
      }
    ],
    metrics: [
      {
        id: 'metric-1',
        metric: 'Jobs Created',
        value: '200',
        unit: 'jobs',
        description: 'Tech jobs created in the community'
      }
    ],
    sdgs: [
      {
        id: 'sdg-1',
        number: 8,
        name: 'Decent Work and Economic Growth',
        description: 'Promote sustained, inclusive and sustainable economic growth, full and productive employment and decent work for all',
        icon: {
          id: 'sdg-icon-1',
          title: 'SDG 8 Icon',
          description: 'Icon for SDG 8',
          url: 'https://example.com/sdg-8.svg',
          width: 100,
          height: 100,
          contentType: 'image/svg+xml'
        }
      }
    ],
    createdAt: '2023-03-01T00:00:00Z',
    updatedAt: '2023-03-15T00:00:00Z',
    ...overrides
  };
};

/**
 * Creates mock form validation rules for testing form validation
 * @param overrides - Properties to override in the default mock
 * @returns Mock validation rules
 */
export const createMockValidationRules = (
  overrides: Partial<FormValidationRules> = {}
): FormValidationRules => {
  return {
    required: true,
    minLength: 2,
    maxLength: 100,
    pattern: /^[a-zA-Z0-9\s]+$/,
    ...overrides
  };
};

/**
 * Simulates a file upload event for testing file upload components
 * @param inputElement - File input element
 * @param files - File or array of files to upload
 */
export const simulateFileUpload = (
  inputElement: HTMLElement,
  files: File | File[]
) => {
  const filesArray = Array.isArray(files) ? files : [files];
  
  // Create a mock change event
  const mockEvent = {
    target: {
      files: Object.assign(filesArray, {
        item: (idx: number) => filesArray[idx]
      })
    }
  };
  
  // Set files directly on the DOM element
  // @ts-ignore - This is needed for testing file inputs
  Object.defineProperty(inputElement, 'files', {
    value: mockEvent.target.files
  });
  
  // Fire the change event
  fireEvent.change(inputElement, mockEvent);
};