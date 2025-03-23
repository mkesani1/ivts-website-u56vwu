import { rest, PathParams } from 'msw'; // version ^1.2.1
import {
  mockServices,
  mockCaseStudies,
  mockImpactStories,
  mockApiResponses,
  mockUploadResponses
} from './data';
import { API_ENDPOINTS } from '../../src/constants/apiEndpoints';

/**
 * Creates a paginated response object for list endpoints
 *
 * @param items - Array of items to paginate
 * @param page - Current page number (1-based)
 * @param limit - Number of items per page
 * @returns Paginated response object with items and pagination metadata
 */
const createPaginatedResponse = (items: any[], page: number, limit: number) => {
  const totalPages = Math.ceil(items.length / limit);
  const startIndex = (page - 1) * limit;
  const endIndex = startIndex + limit;
  const paginatedItems = items.slice(startIndex, endIndex);

  return {
    items: paginatedItems,
    total: items.length,
    page,
    limit,
    totalPages
  };
};

/**
 * MSW request handlers for API mocking during tests
 */
export const handlers = [
  // ==================== Services API ====================
  rest.get(API_ENDPOINTS.SERVICES.LIST, (req, res, ctx) => {
    const page = parseInt(req.url.searchParams.get('page') || '1', 10);
    const limit = parseInt(req.url.searchParams.get('limit') || '10', 10);
    const category = req.url.searchParams.get('category');
    
    let filteredServices = [...mockServices];
    if (category) {
      filteredServices = filteredServices.filter(service => 
        service.slug.includes(category)
      );
    }
    
    const paginatedResponse = createPaginatedResponse(filteredServices, page, limit);
    
    return res(
      ctx.status(200),
      ctx.json({
        success: true,
        data: paginatedResponse,
        message: 'Services retrieved successfully'
      })
    );
  }),
  
  rest.get(API_ENDPOINTS.SERVICES.DETAIL, (req, res, ctx) => {
    const { id } = req.params as PathParams;
    
    // Special case for testing error scenarios
    if (id === 'error') {
      return res(
        ctx.status(404),
        ctx.json(mockApiResponses.services.error)
      );
    }
    
    const service = mockServices.find(s => s.id === id);
    
    if (service) {
      return res(
        ctx.status(200),
        ctx.json({
          success: true,
          data: service,
          message: 'Service retrieved successfully'
        })
      );
    }
    
    return res(
      ctx.status(404),
      ctx.json(mockApiResponses.services.error)
    );
  }),
  
  rest.get(API_ENDPOINTS.SERVICES.BY_SLUG, (req, res, ctx) => {
    const { slug } = req.params as PathParams;
    
    const service = mockServices.find(s => s.slug === slug);
    
    if (service) {
      return res(
        ctx.status(200),
        ctx.json({
          success: true,
          data: service,
          message: 'Service retrieved successfully'
        })
      );
    }
    
    return res(
      ctx.status(404),
      ctx.json(mockApiResponses.services.error)
    );
  }),
  
  // ==================== Case Studies API ====================
  rest.get(API_ENDPOINTS.CASE_STUDIES.LIST, (req, res, ctx) => {
    const page = parseInt(req.url.searchParams.get('page') || '1', 10);
    const limit = parseInt(req.url.searchParams.get('limit') || '10', 10);
    const industry = req.url.searchParams.get('industry');
    const service = req.url.searchParams.get('service');
    
    let filteredCaseStudies = [...mockCaseStudies];
    
    if (industry) {
      filteredCaseStudies = filteredCaseStudies.filter(cs => 
        cs.industry_id === industry
      );
    }
    
    if (service) {
      filteredCaseStudies = filteredCaseStudies.filter(cs => 
        cs.services.some(s => s.id === service || s.slug === service)
      );
    }
    
    const paginatedResponse = createPaginatedResponse(filteredCaseStudies, page, limit);
    
    return res(
      ctx.status(200),
      ctx.json({
        success: true,
        data: paginatedResponse,
        message: 'Case studies retrieved successfully'
      })
    );
  }),
  
  rest.get(API_ENDPOINTS.CASE_STUDIES.DETAIL, (req, res, ctx) => {
    const { id } = req.params as PathParams;
    
    // Special case for testing error scenarios
    if (id === 'error') {
      return res(
        ctx.status(404),
        ctx.json(mockApiResponses.caseStudies.error)
      );
    }
    
    const caseStudy = mockCaseStudies.find(cs => cs.id === id);
    
    if (caseStudy) {
      return res(
        ctx.status(200),
        ctx.json({
          success: true,
          data: caseStudy,
          message: 'Case study retrieved successfully'
        })
      );
    }
    
    return res(
      ctx.status(404),
      ctx.json(mockApiResponses.caseStudies.error)
    );
  }),
  
  rest.get(API_ENDPOINTS.CASE_STUDIES.BY_SLUG, (req, res, ctx) => {
    const { slug } = req.params as PathParams;
    
    const caseStudy = mockCaseStudies.find(cs => cs.slug === slug);
    
    if (caseStudy) {
      return res(
        ctx.status(200),
        ctx.json({
          success: true,
          data: caseStudy,
          message: 'Case study retrieved successfully'
        })
      );
    }
    
    return res(
      ctx.status(404),
      ctx.json(mockApiResponses.caseStudies.error)
    );
  }),
  
  rest.get(API_ENDPOINTS.CASE_STUDIES.BY_INDUSTRY, (req, res, ctx) => {
    const { industryId } = req.params as PathParams;
    
    const filteredCaseStudies = mockCaseStudies.filter(cs => cs.industry_id === industryId);
    
    return res(
      ctx.status(200),
      ctx.json({
        success: true,
        data: filteredCaseStudies,
        message: 'Case studies retrieved successfully'
      })
    );
  }),
  
  // ==================== Impact Stories API ====================
  rest.get(API_ENDPOINTS.IMPACT_STORIES.LIST, (req, res, ctx) => {
    const page = parseInt(req.url.searchParams.get('page') || '1', 10);
    const limit = parseInt(req.url.searchParams.get('limit') || '10', 10);
    const category = req.url.searchParams.get('category');
    
    let filteredStories = [...mockImpactStories];
    
    if (category) {
      filteredStories = filteredStories.filter(story => 
        story.slug.includes(category)
      );
    }
    
    const paginatedResponse = createPaginatedResponse(filteredStories, page, limit);
    
    return res(
      ctx.status(200),
      ctx.json({
        success: true,
        data: paginatedResponse,
        message: 'Impact stories retrieved successfully'
      })
    );
  }),
  
  rest.get(API_ENDPOINTS.IMPACT_STORIES.DETAIL, (req, res, ctx) => {
    const { id } = req.params as PathParams;
    
    // Special case for testing error scenarios
    if (id === 'error') {
      return res(
        ctx.status(404),
        ctx.json(mockApiResponses.impactStories.error)
      );
    }
    
    const story = mockImpactStories.find(s => s.id === id);
    
    if (story) {
      return res(
        ctx.status(200),
        ctx.json({
          success: true,
          data: story,
          message: 'Impact story retrieved successfully'
        })
      );
    }
    
    return res(
      ctx.status(404),
      ctx.json(mockApiResponses.impactStories.error)
    );
  }),
  
  rest.get(API_ENDPOINTS.IMPACT_STORIES.BY_SLUG, (req, res, ctx) => {
    const { slug } = req.params as PathParams;
    
    const story = mockImpactStories.find(s => s.slug === slug);
    
    if (story) {
      return res(
        ctx.status(200),
        ctx.json({
          success: true,
          data: story,
          message: 'Impact story retrieved successfully'
        })
      );
    }
    
    return res(
      ctx.status(404),
      ctx.json(mockApiResponses.impactStories.error)
    );
  }),
  
  // ==================== Forms API ====================
  rest.post(API_ENDPOINTS.FORMS.CONTACT, async (req, res, ctx) => {
    const body = await req.json();
    
    // For testing error scenarios
    if (body.email === 'error@example.com') {
      return res(
        ctx.status(400),
        ctx.json(mockApiResponses.contactForm.error)
      );
    }
    
    return res(
      ctx.status(200),
      ctx.json(mockApiResponses.contactForm.success)
    );
  }),
  
  rest.post(API_ENDPOINTS.FORMS.DEMO_REQUEST, async (req, res, ctx) => {
    const body = await req.json();
    
    // For testing error scenarios
    if (body.email === 'error@example.com') {
      return res(
        ctx.status(400),
        ctx.json(mockApiResponses.demoRequest.error)
      );
    }
    
    return res(
      ctx.status(200),
      ctx.json(mockApiResponses.demoRequest.success)
    );
  }),
  
  rest.post(API_ENDPOINTS.FORMS.QUOTE_REQUEST, async (req, res, ctx) => {
    const body = await req.json();
    
    // For testing error scenarios
    if (body.email === 'error@example.com') {
      return res(
        ctx.status(400),
        ctx.json(mockApiResponses.quoteRequest.error)
      );
    }
    
    return res(
      ctx.status(200),
      ctx.json(mockApiResponses.quoteRequest.success)
    );
  }),
  
  // ==================== Upload API ====================
  rest.post(API_ENDPOINTS.UPLOADS.REQUEST, async (req, res, ctx) => {
    const body = await req.json();
    
    // For testing error scenarios
    if (body.filename && body.filename.includes('error')) {
      return res(
        ctx.status(500),
        ctx.json({
          success: false,
          message: 'Server error processing upload request',
          errors: {
            server: ['Internal server error occurred. Please try again later.']
          }
        })
      );
    }
    
    return res(
      ctx.status(200),
      ctx.json(mockUploadResponses.uploadRequest.success)
    );
  }),
  
  rest.post(API_ENDPOINTS.UPLOADS.COMPLETE, async (req, res, ctx) => {
    const body = await req.json();
    
    // For testing error scenarios
    if (body.upload_id && body.upload_id.includes('error')) {
      return res(
        ctx.status(400),
        ctx.json(mockUploadResponses.uploadComplete.error)
      );
    }
    
    return res(
      ctx.status(200),
      ctx.json(mockUploadResponses.uploadComplete.success)
    );
  }),
  
  rest.get(API_ENDPOINTS.UPLOADS.STATUS, (req, res, ctx) => {
    const { uploadId } = req.params as PathParams;
    
    // Return different statuses based on the uploadId to facilitate testing various states
    if (uploadId.includes('pending')) {
      return res(
        ctx.status(200),
        ctx.json(mockUploadResponses.uploadStatus.pending)
      );
    } else if (uploadId.includes('uploading')) {
      return res(
        ctx.status(200),
        ctx.json(mockUploadResponses.uploadStatus.uploading)
      );
    } else if (uploadId.includes('uploaded')) {
      return res(
        ctx.status(200),
        ctx.json(mockUploadResponses.uploadStatus.uploaded)
      );
    } else if (uploadId.includes('scanning')) {
      return res(
        ctx.status(200),
        ctx.json(mockUploadResponses.uploadStatus.scanning)
      );
    } else if (uploadId.includes('processing')) {
      return res(
        ctx.status(200),
        ctx.json(mockUploadResponses.uploadStatus.processing)
      );
    } else if (uploadId.includes('failed')) {
      return res(
        ctx.status(200),
        ctx.json(mockUploadResponses.uploadStatus.failed)
      );
    } else if (uploadId.includes('quarantined')) {
      return res(
        ctx.status(200),
        ctx.json(mockUploadResponses.uploadStatus.quarantined)
      );
    } else {
      // Default to completed status
      return res(
        ctx.status(200),
        ctx.json(mockUploadResponses.uploadStatus.completed)
      );
    }
  }),
  
  rest.delete(API_ENDPOINTS.UPLOADS.DELETE, (req, res, ctx) => {
    const { uploadId } = req.params as PathParams;
    
    // For testing error scenarios
    if (uploadId.includes('error')) {
      return res(
        ctx.status(404),
        ctx.json({
          success: false,
          message: 'Upload not found',
          errors: {
            upload_id: ['Invalid upload ID']
          }
        })
      );
    }
    
    return res(
      ctx.status(200),
      ctx.json({
        success: true,
        message: 'Upload deleted successfully'
      })
    );
  }),
  
  rest.get(API_ENDPOINTS.UPLOADS.SUPPORTED_TYPES, (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        success: true,
        data: [
          {
            extension: 'csv',
            mime_type: 'text/csv',
            description: 'Comma-separated values file',
            max_size_mb: 50
          },
          {
            extension: 'json',
            mime_type: 'application/json',
            description: 'JavaScript Object Notation file',
            max_size_mb: 50
          },
          {
            extension: 'xml',
            mime_type: 'application/xml',
            description: 'Extensible Markup Language file',
            max_size_mb: 50
          },
          {
            extension: 'jpg',
            mime_type: 'image/jpeg',
            description: 'JPEG image',
            max_size_mb: 50
          },
          {
            extension: 'png',
            mime_type: 'image/png',
            description: 'PNG image',
            max_size_mb: 50
          },
          {
            extension: 'mp3',
            mime_type: 'audio/mpeg',
            description: 'MP3 audio file',
            max_size_mb: 50
          },
          {
            extension: 'wav',
            mime_type: 'audio/wav',
            description: 'WAV audio file',
            max_size_mb: 50
          }
        ],
        message: 'Supported file types retrieved successfully'
      })
    );
  })
];