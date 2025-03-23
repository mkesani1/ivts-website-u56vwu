import axios, { AxiosError, AxiosRequestConfig } from 'axios'; // axios@^1.4.0
import { parseApiError, logError } from './errorHandling';
import { ApiResponse } from '../types/api';

// Base URL for API requests
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '/api/v1';

// Default timeout for requests (30 seconds)
const DEFAULT_TIMEOUT = 30000;

/**
 * Interface for request configuration options
 */
export interface RequestOptions {
  headers?: Record<string, string>;
  timeout?: number;
  withCredentials?: boolean;
}

/**
 * Creates a standardized request configuration object for API requests
 * @param options Custom request options
 * @returns Configured request options for axios
 */
const createRequestConfig = (options: RequestOptions = {}): AxiosRequestConfig => {
  // Default headers for all requests
  const defaultHeaders: Record<string, string> = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  };

  // Merge headers with priority to provided options
  const headers = {
    ...defaultHeaders,
    ...options.headers,
  };

  // Add CSRF token if available in browser environment
  const csrfToken = typeof document !== 'undefined' 
    ? document.querySelector('meta[name="csrf-token"]')?.getAttribute('content')
    : null;
  
  if (csrfToken) {
    headers['X-CSRF-Token'] = csrfToken;
  }

  // Create the configuration object
  return {
    headers,
    timeout: options.timeout || DEFAULT_TIMEOUT,
    withCredentials: options.withCredentials !== undefined ? options.withCredentials : true,
  };
};

/**
 * Makes a GET request to the specified endpoint
 * @param endpoint The API endpoint to request
 * @param params Optional query parameters
 * @param options Request configuration options
 * @returns Promise resolving to the API response with data of type T
 */
export const get = async <T = any>(
  endpoint: string,
  params: Record<string, any> = {},
  options: RequestOptions = {}
): Promise<ApiResponse<T>> => {
  try {
    const config = createRequestConfig(options);
    config.params = params;
    
    const response = await axios.get<ApiResponse<T>>(`${API_BASE_URL}${endpoint}`, config);
    return response.data;
  } catch (error) {
    logError(error, `GET ${endpoint}`);
    throw parseApiError(error);
  }
};

/**
 * Makes a POST request to the specified endpoint
 * @param endpoint The API endpoint to request
 * @param data Request payload
 * @param options Request configuration options
 * @returns Promise resolving to the API response with data of type T
 */
export const post = async <T = any>(
  endpoint: string,
  data: any = {},
  options: RequestOptions = {}
): Promise<ApiResponse<T>> => {
  try {
    const config = createRequestConfig(options);
    const response = await axios.post<ApiResponse<T>>(`${API_BASE_URL}${endpoint}`, data, config);
    return response.data;
  } catch (error) {
    logError(error, `POST ${endpoint}`);
    throw parseApiError(error);
  }
};

/**
 * Makes a PUT request to the specified endpoint
 * @param endpoint The API endpoint to request
 * @param data Request payload
 * @param options Request configuration options
 * @returns Promise resolving to the API response with data of type T
 */
export const put = async <T = any>(
  endpoint: string,
  data: any = {},
  options: RequestOptions = {}
): Promise<ApiResponse<T>> => {
  try {
    const config = createRequestConfig(options);
    const response = await axios.put<ApiResponse<T>>(`${API_BASE_URL}${endpoint}`, data, config);
    return response.data;
  } catch (error) {
    logError(error, `PUT ${endpoint}`);
    throw parseApiError(error);
  }
};

/**
 * Makes a PATCH request to the specified endpoint
 * @param endpoint The API endpoint to request
 * @param data Request payload
 * @param options Request configuration options
 * @returns Promise resolving to the API response with data of type T
 */
export const patch = async <T = any>(
  endpoint: string,
  data: any = {},
  options: RequestOptions = {}
): Promise<ApiResponse<T>> => {
  try {
    const config = createRequestConfig(options);
    const response = await axios.patch<ApiResponse<T>>(`${API_BASE_URL}${endpoint}`, data, config);
    return response.data;
  } catch (error) {
    logError(error, `PATCH ${endpoint}`);
    throw parseApiError(error);
  }
};

/**
 * Makes a DELETE request to the specified endpoint
 * @param endpoint The API endpoint to request
 * @param options Request configuration options
 * @returns Promise resolving to the API response with data of type T
 */
export const del = async <T = any>(
  endpoint: string,
  options: RequestOptions = {}
): Promise<ApiResponse<T>> => {
  try {
    const config = createRequestConfig(options);
    const response = await axios.delete<ApiResponse<T>>(`${API_BASE_URL}${endpoint}`, config);
    return response.data;
  } catch (error) {
    logError(error, `DELETE ${endpoint}`);
    throw parseApiError(error);
  }
};

/**
 * Uploads a file directly to a presigned URL
 * @param presignedUrl The presigned URL for upload
 * @param file The file to upload
 * @param fields Additional fields required by the presigned URL
 * @returns Promise resolving to upload result with success status and optional ETag
 */
export const uploadToPresignedUrl = async (
  presignedUrl: string,
  file: File,
  fields: Record<string, string> = {}
): Promise<{success: boolean, etag?: string}> => {
  try {
    // Create a FormData object to hold the file and additional fields
    const formData = new FormData();
    
    // Add all fields from the presigned URL to the FormData
    // These fields must be added before the file for S3 uploads to work correctly
    Object.entries(fields).forEach(([key, value]) => {
      formData.append(key, value);
    });
    
    // Add the file as the last field (required for S3)
    formData.append('file', file);
    
    // Upload directly to the presigned URL
    const response = await axios.post(presignedUrl, formData, {
      headers: {
        // Let the browser set the content type for FormData
        'Content-Type': 'multipart/form-data',
      },
    });
    
    // Extract the ETag from the response headers (AWS returns this for successful uploads)
    const etag = response.headers.etag || response.headers.ETag;
    
    return {
      success: true,
      etag: etag ? etag.replace(/"/g, '') : undefined // Remove quotes from ETag if present
    };
  } catch (error) {
    logError(error, 'File Upload');
    throw parseApiError(error);
  }
};

/**
 * Determines if an error is a network connectivity error
 * @param error Any error object
 * @returns True if error is a network error
 */
export const isNetworkError = (error: any): boolean => {
  if (!axios.isAxiosError(error)) {
    return false;
  }
  
  return !error.response && Boolean(error.request) || 
         error.code === 'ECONNABORTED' ||
         error.code === 'ECONNRESET' ||
         error.code === 'ECONNREFUSED';
};

/**
 * Determines if an error is a request timeout error
 * @param error Any error object
 * @returns True if error is a timeout error
 */
export const isTimeoutError = (error: any): boolean => {
  if (!axios.isAxiosError(error)) {
    return false;
  }
  
  return error.code === 'ECONNABORTED' && error.message.includes('timeout');
};