/**
 * API Endpoints Configuration
 * 
 * This file provides a centralized configuration for all API endpoints used
 * throughout the IndiVillage website. It ensures consistency and makes it
 * easier to update endpoint paths when needed.
 * 
 * @version 1.0.0
 */

/**
 * Base URL for all API endpoints. Uses the NEXT_PUBLIC_API_URL environment
 * variable if available, otherwise defaults to '/api/v1'.
 */
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '/api/v1';

/**
 * Interface for service-related endpoints
 */
export interface ServiceEndpoints {
  LIST: string;
  DETAIL: string;
  BY_SLUG: string;
}

/**
 * Interface for case study-related endpoints
 */
export interface CaseStudyEndpoints {
  LIST: string;
  DETAIL: string;
  BY_SLUG: string;
  BY_INDUSTRY: string;
}

/**
 * Interface for impact story-related endpoints
 */
export interface ImpactStoryEndpoints {
  LIST: string;
  DETAIL: string;
  BY_SLUG: string;
}

/**
 * Interface for form submission endpoints
 */
export interface FormEndpoints {
  CONTACT: string;
  DEMO_REQUEST: string;
  QUOTE_REQUEST: string;
}

/**
 * Interface for file upload endpoints
 */
export interface UploadEndpoints {
  REQUEST: string;
  COMPLETE: string;
  STATUS: string;
  DELETE: string;
  PROCESS: string;
  RESULTS: string;
  SUPPORTED_TYPES: string;
}

/**
 * Interface for all API endpoints
 */
export interface ApiEndpoints {
  SERVICES: ServiceEndpoints;
  CASE_STUDIES: CaseStudyEndpoints;
  IMPACT_STORIES: ImpactStoryEndpoints;
  FORMS: FormEndpoints;
  UPLOADS: UploadEndpoints;
}

/**
 * Object containing all API endpoint definitions organized by category.
 */
export const API_ENDPOINTS: ApiEndpoints = {
  /**
   * Service-related endpoints for retrieving information about
   * IndiVillage's AI-as-a-service offerings.
   */
  SERVICES: {
    /**
     * Get a list of all services
     */
    LIST: `${API_BASE_URL}/services`,
    
    /**
     * Get details for a specific service by ID
     */
    DETAIL: `${API_BASE_URL}/services/{id}`,
    
    /**
     * Get a specific service by its slug
     */
    BY_SLUG: `${API_BASE_URL}/services/slug/{slug}`,
  },
  
  /**
   * Case study-related endpoints for showcasing successful
   * client implementations.
   */
  CASE_STUDIES: {
    /**
     * Get a list of all case studies
     */
    LIST: `${API_BASE_URL}/case-studies`,
    
    /**
     * Get details for a specific case study by ID
     */
    DETAIL: `${API_BASE_URL}/case-studies/{id}`,
    
    /**
     * Get a specific case study by its slug
     */
    BY_SLUG: `${API_BASE_URL}/case-studies/slug/{slug}`,
    
    /**
     * Get case studies filtered by industry
     */
    BY_INDUSTRY: `${API_BASE_URL}/case-studies/industry/{industryId}`,
  },
  
  /**
   * Impact story-related endpoints for retrieving social impact
   * stories and metrics.
   */
  IMPACT_STORIES: {
    /**
     * Get a list of all impact stories
     */
    LIST: `${API_BASE_URL}/impact-stories`,
    
    /**
     * Get details for a specific impact story by ID
     */
    DETAIL: `${API_BASE_URL}/impact-stories/{id}`,
    
    /**
     * Get a specific impact story by its slug
     */
    BY_SLUG: `${API_BASE_URL}/impact-stories/slug/{slug}`,
  },
  
  /**
   * Form submission endpoints for contact, demo requests, and quote requests.
   */
  FORMS: {
    /**
     * Submit contact form
     */
    CONTACT: `${API_BASE_URL}/contact`,
    
    /**
     * Submit demo request form
     */
    DEMO_REQUEST: `${API_BASE_URL}/demo-request`,
    
    /**
     * Submit quote request form
     */
    QUOTE_REQUEST: `${API_BASE_URL}/quote-request`,
  },
  
  /**
   * File upload endpoints for sample data upload functionality.
   */
  UPLOADS: {
    /**
     * Request permission to upload a file (gets presigned URL)
     */
    REQUEST: `${API_BASE_URL}/uploads/request`,
    
    /**
     * Confirm upload completion after direct upload to storage
     */
    COMPLETE: `${API_BASE_URL}/uploads/complete`,
    
    /**
     * Check upload status and processing progress
     */
    STATUS: `${API_BASE_URL}/uploads/status/{uploadId}`,
    
    /**
     * Delete an uploaded file
     */
    DELETE: `${API_BASE_URL}/uploads/{uploadId}`,
    
    /**
     * Trigger processing for an uploaded file
     */
    PROCESS: `${API_BASE_URL}/uploads/process`,
    
    /**
     * Get processing results for an uploaded file
     */
    RESULTS: `${API_BASE_URL}/uploads/results/{uploadId}`,
    
    /**
     * Get list of supported file types for uploading
     */
    SUPPORTED_TYPES: `${API_BASE_URL}/uploads/allowed-types`,
  },
};

export default API_ENDPOINTS;