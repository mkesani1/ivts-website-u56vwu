import { rest } from 'msw'; // version ^1.0.0
import * as apiService from '../../src/services/api';
import { server } from '../setup';
import { 
  mockServices, 
  mockCaseStudies, 
  mockImpactStories, 
  mockContactFormData, 
  mockDemoRequestFormData, 
  mockQuoteRequestFormData, 
  mockUploadFormData, 
  mockApiResponses, 
  mockUploadResponses 
} from '../mocks/data';
import { API_ENDPOINTS } from '../../src/constants/apiEndpoints';

/**
 * Unit tests for the API service
 * 
 * These tests verify that the API service properly communicates with backend services
 * and correctly handles both successful responses and errors.
 */

describe('Service API functions', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('getServices should return a paginated list of services', async () => {
    const result = await apiService.getServices();
    expect(result).toBeDefined();
    expect(result.items).toHaveLength(mockServices.length);
    expect(result.total).toBe(mockServices.length);
    expect(result.page).toBe(1);
  });

  it('getServices should accept query parameters', async () => {
    const category = 'data-collection';
    const result = await apiService.getServices({ category });
    expect(result).toBeDefined();
    expect(result.items.some(service => service.slug.includes(category))).toBeTruthy();
  });

  it('getServiceById should return a service by ID', async () => {
    const serviceId = 'srv-001';
    const result = await apiService.getServiceById(serviceId);
    expect(result).toBeDefined();
    expect(result.id).toBe(serviceId);
  });

  it('getServiceById should throw an error for invalid ID', async () => {
    const serviceId = 'error';
    await expect(apiService.getServiceById(serviceId)).rejects.toThrow();
  });

  it('getServiceBySlug should return a service by slug', async () => {
    const serviceSlug = 'data-collection';
    const result = await apiService.getServiceBySlug(serviceSlug);
    expect(result).toBeDefined();
    expect(result.slug).toBe(serviceSlug);
  });

  it('getServiceBySlug should throw an error for invalid slug', async () => {
    const serviceSlug = 'invalid-slug';
    await expect(apiService.getServiceBySlug(serviceSlug)).rejects.toThrow();
  });

  it('should handle network errors', async () => {
    // Mock a network error
    server.use(
      rest.get(API_ENDPOINTS.SERVICES.LIST, (req, res, ctx) => {
        return res.networkError('Network error');
      })
    );

    await expect(apiService.getServices()).rejects.toThrow();
  });
});

describe('Case Study API functions', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('getCaseStudies should return a paginated list of case studies', async () => {
    const result = await apiService.getCaseStudies();
    expect(result).toBeDefined();
    expect(result.items).toHaveLength(mockCaseStudies.length);
    expect(result.total).toBe(mockCaseStudies.length);
    expect(result.page).toBe(1);
  });

  it('getCaseStudies should accept query parameters', async () => {
    const industry = 'ind-001'; // Healthcare
    const result = await apiService.getCaseStudies({ industry });
    expect(result).toBeDefined();
    expect(result.items.some(caseStudy => caseStudy.industry_id === industry)).toBeTruthy();
  });

  it('getCaseStudyById should return a case study by ID', async () => {
    const caseStudyId = 'cs-001';
    const result = await apiService.getCaseStudyById(caseStudyId);
    expect(result).toBeDefined();
    expect(result.id).toBe(caseStudyId);
  });

  it('getCaseStudyById should throw an error for invalid ID', async () => {
    const caseStudyId = 'error';
    await expect(apiService.getCaseStudyById(caseStudyId)).rejects.toThrow();
  });

  it('getCaseStudyBySlug should return a case study by slug', async () => {
    const caseStudySlug = 'ecommerce-product-categorization';
    const result = await apiService.getCaseStudyBySlug(caseStudySlug);
    expect(result).toBeDefined();
    expect(result.slug).toBe(caseStudySlug);
  });

  it('getCaseStudyBySlug should throw an error for invalid slug', async () => {
    const caseStudySlug = 'invalid-slug';
    await expect(apiService.getCaseStudyBySlug(caseStudySlug)).rejects.toThrow();
  });

  it('should handle server errors', async () => {
    // Mock a server error
    server.use(
      rest.get(API_ENDPOINTS.CASE_STUDIES.LIST, (req, res, ctx) => {
        return res(ctx.status(500), ctx.json(mockApiResponses.errors.serverError));
      })
    );

    await expect(apiService.getCaseStudies()).rejects.toThrow();
  });
});

describe('Impact Story API functions', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('getImpactStories should return a paginated list of impact stories', async () => {
    const result = await apiService.getImpactStories();
    expect(result).toBeDefined();
    expect(result.items).toHaveLength(mockImpactStories.length);
    expect(result.total).toBe(mockImpactStories.length);
    expect(result.page).toBe(1);
  });

  it('getImpactStories should accept query parameters', async () => {
    const category = 'education';
    const result = await apiService.getImpactStories({ category });
    expect(result).toBeDefined();
    // In our mock implementation, filtering is based on the slug containing the category
    const hasMatchingStories = result.items.some(story => story.slug.includes(category));
    expect(hasMatchingStories).toBeTruthy();
  });

  it('getImpactStoryById should return an impact story by ID', async () => {
    const storyId = 'is-001';
    const result = await apiService.getImpactStoryById(storyId);
    expect(result).toBeDefined();
    expect(result.id).toBe(storyId);
  });

  it('getImpactStoryById should throw an error for invalid ID', async () => {
    const storyId = 'error';
    await expect(apiService.getImpactStoryById(storyId)).rejects.toThrow();
  });

  it('getImpactStoryBySlug should return an impact story by slug', async () => {
    const storySlug = 'empowering-rural-communities';
    const result = await apiService.getImpactStoryBySlug(storySlug);
    expect(result).toBeDefined();
    expect(result.slug).toBe(storySlug);
  });

  it('getImpactStoryBySlug should throw an error for invalid slug', async () => {
    const storySlug = 'invalid-slug';
    await expect(apiService.getImpactStoryBySlug(storySlug)).rejects.toThrow();
  });

  it('should handle timeout errors', async () => {
    // Mock a timeout error
    server.use(
      rest.get(API_ENDPOINTS.IMPACT_STORIES.LIST, (req, res, ctx) => {
        return res.networkError('ETIMEDOUT');
      })
    );

    await expect(apiService.getImpactStories()).rejects.toThrow();
  });
});

describe('Form Submission API functions', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('submitContactForm should submit contact form data', async () => {
    const result = await apiService.submitContactForm(mockContactFormData);
    expect(result).toBeDefined();
    expect(result.success).toBe(true);
    expect(result.submission_id).toBeDefined();
  });

  it('submitContactForm should handle validation errors', async () => {
    const invalidData = { 
      ...mockContactFormData, 
      email: 'error@example.com' 
    };
    await expect(apiService.submitContactForm(invalidData)).rejects.toThrow();
  });

  it('submitDemoRequest should submit demo request form data', async () => {
    const result = await apiService.submitDemoRequest(mockDemoRequestFormData);
    expect(result).toBeDefined();
    expect(result.success).toBe(true);
    expect(result.submission_id).toBeDefined();
  });

  it('submitDemoRequest should handle validation errors', async () => {
    const invalidData = { 
      ...mockDemoRequestFormData, 
      email: 'error@example.com' 
    };
    await expect(apiService.submitDemoRequest(invalidData)).rejects.toThrow();
  });

  it('submitQuoteRequest should submit quote request form data', async () => {
    const result = await apiService.submitQuoteRequest(mockQuoteRequestFormData);
    expect(result).toBeDefined();
    expect(result.success).toBe(true);
    expect(result.submission_id).toBeDefined();
  });

  it('submitQuoteRequest should handle validation errors', async () => {
    const invalidData = { 
      ...mockQuoteRequestFormData, 
      email: 'error@example.com' 
    };
    await expect(apiService.submitQuoteRequest(invalidData)).rejects.toThrow();
  });

  it('should handle authentication errors', async () => {
    // Mock an authentication error
    server.use(
      rest.post(API_ENDPOINTS.FORMS.CONTACT, (req, res, ctx) => {
        return res(ctx.status(401), ctx.json(mockApiResponses.errors.unauthorized));
      })
    );

    await expect(apiService.submitContactForm(mockContactFormData)).rejects.toThrow();
  });
});

describe('File Upload API functions', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('requestFileUpload should request a presigned URL', async () => {
    const uploadParams = {
      filename: 'test.csv',
      size: 1024,
      mime_type: 'text/csv',
      form_data: mockUploadFormData
    };
    
    const result = await apiService.requestFileUpload(uploadParams);
    expect(result).toBeDefined();
    expect(result.upload_id).toBeDefined();
    expect(result.presigned_url).toBeDefined();
    expect(result.presigned_fields).toBeDefined();
  });

  it('requestFileUpload should handle errors', async () => {
    const uploadParams = {
      filename: 'error.csv', // Triggering error in mock handler
      size: 1024,
      mime_type: 'text/csv',
      form_data: mockUploadFormData
    };
    
    await expect(apiService.requestFileUpload(uploadParams)).rejects.toThrow();
  });

  it('uploadFileToPresignedUrl should upload a file to a presigned URL', async () => {
    // Create a mock File object
    const file = new File(['test file content'], 'test.csv', { type: 'text/csv' });
    
    // Mock global fetch to handle the direct upload to presigned URL
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      headers: new Headers({ etag: '"mock-etag"' }),
      json: () => Promise.resolve({ success: true })
    });
    
    const result = await apiService.uploadFileToPresignedUrl(file, mockUploadResponses.uploadRequest.success);
    expect(result).toBeDefined();
    expect(result.success).toBe(true);
  });

  it('getUploadStatus should return the status of an upload', async () => {
    const uploadId = 'upload-123456';
    const result = await apiService.getUploadStatus(uploadId);
    expect(result).toBeDefined();
    expect(result.upload_id).toBe(uploadId);
    expect(result.status).toBeDefined();
  });

  it('getUploadStatus should handle invalid upload IDs', async () => {
    // Mock a response for an error case
    server.use(
      rest.get(API_ENDPOINTS.UPLOADS.STATUS.replace('{uploadId}', 'error'), (req, res, ctx) => {
        return res(ctx.status(404), ctx.json({ 
          success: false, 
          message: 'Upload not found' 
        }));
      })
    );
    
    await expect(apiService.getUploadStatus('error')).rejects.toThrow();
  });

  it('deleteUpload should delete an upload', async () => {
    const uploadId = 'upload-123456';
    const result = await apiService.deleteUpload(uploadId);
    expect(result).toBeDefined();
    expect(result.success).toBe(true);
  });

  it('deleteUpload should handle invalid upload IDs', async () => {
    const uploadId = 'error';
    await expect(apiService.deleteUpload(uploadId)).rejects.toThrow();
  });

  it('getSupportedFileTypes should return supported file types', async () => {
    const result = await apiService.getSupportedFileTypes();
    expect(result).toBeDefined();
    expect(Array.isArray(result)).toBe(true);
    expect(result.length).toBeGreaterThan(0);
    expect(result[0].extension).toBeDefined();
    expect(result[0].mime_type).toBeDefined();
    expect(result[0].description).toBeDefined();
    expect(result[0].max_size_mb).toBeDefined();
  });

  it('should handle authorization errors', async () => {
    // Mock an authorization error
    server.use(
      rest.get(API_ENDPOINTS.UPLOADS.STATUS.replace('{uploadId}', 'upload-123'), (req, res, ctx) => {
        return res(ctx.status(403), ctx.json(mockApiResponses.errors.unauthorized));
      })
    );

    await expect(apiService.getUploadStatus('upload-123')).rejects.toThrow();
  });
});

// Additional general error handling tests
describe('Error handling', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should handle network errors', async () => {
    // Mock a network error
    server.use(
      rest.get(API_ENDPOINTS.SERVICES.LIST, (req, res) => {
        return res.networkError('Network error');
      })
    );

    await expect(apiService.getServices()).rejects.toThrow();
  });

  it('should handle timeout errors', async () => {
    // Mock a timeout error
    server.use(
      rest.get(API_ENDPOINTS.SERVICES.LIST, (req, res) => {
        return res.networkError('ETIMEDOUT');
      })
    );

    await expect(apiService.getServices()).rejects.toThrow();
  });

  it('should handle server errors', async () => {
    // Mock a server error
    server.use(
      rest.get(API_ENDPOINTS.SERVICES.LIST, (req, res, ctx) => {
        return res(ctx.status(500), ctx.json({
          success: false,
          message: 'Internal server error',
          errors: {
            server: ['An unexpected error occurred. Please try again later.']
          }
        }));
      })
    );

    await expect(apiService.getServices()).rejects.toThrow();
  });

  it('should handle authentication errors', async () => {
    // Mock an authentication error
    server.use(
      rest.get(API_ENDPOINTS.SERVICES.LIST, (req, res, ctx) => {
        return res(ctx.status(401), ctx.json({
          success: false,
          message: 'Unauthorized',
          errors: {
            auth: ['You must be authenticated to access this resource']
          }
        }));
      })
    );

    await expect(apiService.getServices()).rejects.toThrow();
  });

  it('should handle authorization errors', async () => {
    // Mock an authorization error
    server.use(
      rest.get(API_ENDPOINTS.SERVICES.LIST, (req, res, ctx) => {
        return res(ctx.status(403), ctx.json({
          success: false,
          message: 'Forbidden',
          errors: {
            auth: ['You do not have permission to access this resource']
          }
        }));
      })
    );

    await expect(apiService.getServices()).rejects.toThrow();
  });
});