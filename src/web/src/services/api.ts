/**
 * IndiVillage API Service
 * 
 * This module provides a centralized interface for all API interactions in the IndiVillage website.
 * It handles communication with backend services, including content retrieval, form submissions,
 * and file uploads, with standardized error handling and request formatting.
 * 
 * All API requests are routed through this service to ensure consistent error handling,
 * logging, and data formatting across the application.
 *
 * @module services/api
 * @version 1.0.0
 */

import { API_ENDPOINTS } from '../constants/apiEndpoints';
import { get, post, put, del, uploadToPresignedUrl } from '../utils/fetcher';
import { parseApiError, logError } from '../utils/errorHandling';
import {
  Service,
  CaseStudy,
  ImpactStory,
  ContactResponse,
  DemoRequestResponse,
  QuoteRequestResponse,
  UploadRequestParams,
  UploadResponse,
  UploadStatusResponse,
  UploadCompleteParams,
  UploadCompleteResponse,
  PaginatedResponse
} from '../types/api';
import {
  ContactFormData,
  DemoRequestFormData,
  QuoteRequestFormData
} from '../types/forms';

/**
 * Fetches all services with optional filtering
 * @param params Query parameters for filtering services
 * @returns Promise resolving to paginated service data
 */
export const getServices = async (params: Record<string, any> = {}): Promise<PaginatedResponse<Service>> => {
  try {
    const endpoint = API_ENDPOINTS.SERVICES.LIST;
    const response = await get<PaginatedResponse<Service>>(endpoint, params);
    return response.data;
  } catch (error) {
    logError(error, 'getServices');
    throw error;
  }
};

/**
 * Fetches a service by its ID
 * @param id Service ID
 * @returns Promise resolving to service data
 */
export const getServiceById = async (id: string): Promise<Service> => {
  try {
    const endpoint = API_ENDPOINTS.SERVICES.DETAIL.replace('{id}', id);
    const response = await get<Service>(endpoint);
    return response.data;
  } catch (error) {
    logError(error, 'getServiceById');
    throw error;
  }
};

/**
 * Fetches a service by its slug
 * @param slug Service slug
 * @returns Promise resolving to service data
 */
export const getServiceBySlug = async (slug: string): Promise<Service> => {
  try {
    const endpoint = API_ENDPOINTS.SERVICES.BY_SLUG.replace('{slug}', slug);
    const response = await get<Service>(endpoint);
    return response.data;
  } catch (error) {
    logError(error, 'getServiceBySlug');
    throw error;
  }
};

/**
 * Fetches all case studies with optional filtering
 * @param params Query parameters for filtering case studies
 * @returns Promise resolving to paginated case study data
 */
export const getCaseStudies = async (params: Record<string, any> = {}): Promise<PaginatedResponse<CaseStudy>> => {
  try {
    const endpoint = API_ENDPOINTS.CASE_STUDIES.LIST;
    const response = await get<PaginatedResponse<CaseStudy>>(endpoint, params);
    return response.data;
  } catch (error) {
    logError(error, 'getCaseStudies');
    throw error;
  }
};

/**
 * Fetches a case study by its ID
 * @param id Case study ID
 * @returns Promise resolving to case study data
 */
export const getCaseStudyById = async (id: string): Promise<CaseStudy> => {
  try {
    const endpoint = API_ENDPOINTS.CASE_STUDIES.DETAIL.replace('{id}', id);
    const response = await get<CaseStudy>(endpoint);
    return response.data;
  } catch (error) {
    logError(error, 'getCaseStudyById');
    throw error;
  }
};

/**
 * Fetches a case study by its slug
 * @param slug Case study slug
 * @returns Promise resolving to case study data
 */
export const getCaseStudyBySlug = async (slug: string): Promise<CaseStudy> => {
  try {
    const endpoint = API_ENDPOINTS.CASE_STUDIES.BY_SLUG.replace('{slug}', slug);
    const response = await get<CaseStudy>(endpoint);
    return response.data;
  } catch (error) {
    logError(error, 'getCaseStudyBySlug');
    throw error;
  }
};

/**
 * Fetches all impact stories with optional filtering
 * @param params Query parameters for filtering impact stories
 * @returns Promise resolving to paginated impact story data
 */
export const getImpactStories = async (params: Record<string, any> = {}): Promise<PaginatedResponse<ImpactStory>> => {
  try {
    const endpoint = API_ENDPOINTS.IMPACT_STORIES.LIST;
    const response = await get<PaginatedResponse<ImpactStory>>(endpoint, params);
    return response.data;
  } catch (error) {
    logError(error, 'getImpactStories');
    throw error;
  }
};

/**
 * Fetches an impact story by its ID
 * @param id Impact story ID
 * @returns Promise resolving to impact story data
 */
export const getImpactStoryById = async (id: string): Promise<ImpactStory> => {
  try {
    const endpoint = API_ENDPOINTS.IMPACT_STORIES.DETAIL.replace('{id}', id);
    const response = await get<ImpactStory>(endpoint);
    return response.data;
  } catch (error) {
    logError(error, 'getImpactStoryById');
    throw error;
  }
};

/**
 * Fetches an impact story by its slug
 * @param slug Impact story slug
 * @returns Promise resolving to impact story data
 */
export const getImpactStoryBySlug = async (slug: string): Promise<ImpactStory> => {
  try {
    const endpoint = API_ENDPOINTS.IMPACT_STORIES.BY_SLUG.replace('{slug}', slug);
    const response = await get<ImpactStory>(endpoint);
    return response.data;
  } catch (error) {
    logError(error, 'getImpactStoryBySlug');
    throw error;
  }
};

/**
 * Submits a contact form
 * @param formData Contact form data
 * @returns Promise resolving to contact form submission response
 */
export const submitContactForm = async (formData: ContactFormData): Promise<ContactResponse> => {
  try {
    const endpoint = API_ENDPOINTS.FORMS.CONTACT;
    const response = await post<ContactResponse>(endpoint, formData);
    return response.data;
  } catch (error) {
    logError(error, 'submitContactForm');
    throw error;
  }
};

/**
 * Submits a demo request form
 * @param formData Demo request form data
 * @returns Promise resolving to demo request submission response
 */
export const submitDemoRequest = async (formData: DemoRequestFormData): Promise<DemoRequestResponse> => {
  try {
    const endpoint = API_ENDPOINTS.FORMS.DEMO_REQUEST;
    const response = await post<DemoRequestResponse>(endpoint, formData);
    return response.data;
  } catch (error) {
    logError(error, 'submitDemoRequest');
    throw error;
  }
};

/**
 * Submits a quote request form
 * @param formData Quote request form data
 * @returns Promise resolving to quote request submission response
 */
export const submitQuoteRequest = async (formData: QuoteRequestFormData): Promise<QuoteRequestResponse> => {
  try {
    const endpoint = API_ENDPOINTS.FORMS.QUOTE_REQUEST;
    const response = await post<QuoteRequestResponse>(endpoint, formData);
    return response.data;
  } catch (error) {
    logError(error, 'submitQuoteRequest');
    throw error;
  }
};

/**
 * Requests a presigned URL for file upload
 * @param params Upload request parameters
 * @returns Promise resolving to upload request response with presigned URL
 */
export const requestFileUpload = async (params: UploadRequestParams): Promise<UploadResponse> => {
  try {
    const endpoint = API_ENDPOINTS.UPLOADS.REQUEST;
    const response = await post<UploadResponse>(endpoint, params);
    return response.data;
  } catch (error) {
    logError(error, 'requestFileUpload');
    throw error;
  }
};

/**
 * Uploads a file to a presigned URL and notifies completion
 * @param file File to upload
 * @param uploadResponse Upload response containing presigned URL
 * @returns Promise resolving to upload completion response
 */
export const uploadFileToPresignedUrl = async (
  file: File,
  uploadResponse: UploadResponse
): Promise<UploadCompleteResponse> => {
  try {
    // Extract the presigned URL and fields from the upload response
    const { presigned_url, presigned_fields, upload_id } = uploadResponse;
    
    // Upload the file directly to the storage provider using the presigned URL
    const uploadResult = await uploadToPresignedUrl(presigned_url, file, presigned_fields);
    
    if (uploadResult.success) {
      // Notify the backend that the upload is complete
      const completeParams: UploadCompleteParams = {
        upload_id,
        success: true,
        etag: uploadResult.etag || ''
      };
      
      const endpoint = API_ENDPOINTS.UPLOADS.COMPLETE;
      const response = await post<UploadCompleteResponse>(endpoint, completeParams);
      return response.data;
    } else {
      throw new Error('File upload failed');
    }
  } catch (error) {
    logError(error, 'uploadFileToPresignedUrl');
    throw error;
  }
};

/**
 * Checks the status of a file upload
 * @param uploadId Upload ID to check
 * @returns Promise resolving to upload status response
 */
export const getUploadStatus = async (uploadId: string): Promise<UploadStatusResponse> => {
  try {
    const endpoint = API_ENDPOINTS.UPLOADS.STATUS.replace('{uploadId}', uploadId);
    const response = await get<UploadStatusResponse>(endpoint);
    return response.data;
  } catch (error) {
    logError(error, 'getUploadStatus');
    throw error;
  }
};

/**
 * Deletes a file upload
 * @param uploadId Upload ID to delete
 * @returns Promise resolving to deletion success status
 */
export const deleteUpload = async (uploadId: string): Promise<{ success: boolean }> => {
  try {
    const endpoint = API_ENDPOINTS.UPLOADS.DELETE.replace('{uploadId}', uploadId);
    const response = await del<{ success: boolean }>(endpoint);
    return response.data;
  } catch (error) {
    logError(error, 'deleteUpload');
    throw error;
  }
};

/**
 * Fetches the list of supported file types for upload
 * @returns Promise resolving to array of supported file types
 */
export const getSupportedFileTypes = async (): Promise<Array<{
  extension: string;
  mime_type: string;
  description: string;
  max_size_mb: number;
}>> => {
  try {
    const endpoint = API_ENDPOINTS.UPLOADS.SUPPORTED_TYPES;
    const response = await get<Array<{
      extension: string;
      mime_type: string;
      description: string;
      max_size_mb: number;
    }>>(endpoint);
    return response.data;
  } catch (error) {
    logError(error, 'getSupportedFileTypes');
    throw error;
  }
};