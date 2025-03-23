import { ApiResponse, FormErrorResponse } from '../types/api';
import { trackError } from './analytics';
import axios, { AxiosError } from 'axios'; // axios@^1.4.0

// Debug mode flag
const DEBUG_MODE = process.env.NODE_ENV === 'development';

/**
 * Parses API error responses into a standardized format
 * @param error Any error object to be parsed
 * @returns Standardized error object with message, errors, and status properties
 */
export const parseApiError = (error: any): { 
  message: string; 
  errors?: Record<string, string[]>; 
  status?: number;
} => {
  // Check if it's an Axios error
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<ApiResponse>;
    const status = axiosError.response?.status;
    const data = axiosError.response?.data as ApiResponse | undefined;

    // Return standardized error object
    return {
      message: data?.message || axiosError.message || 'An unexpected error occurred',
      errors: data?.errors,
      status
    };
  }

  // If it's not an Axios error, just return a generic error object
  return {
    message: error?.message || 'An unexpected error occurred'
  };
};

/**
 * Processes form submission errors into user-friendly format
 * @param error Any error object to be processed
 * @returns Object mapping field names to error messages
 */
export const handleFormSubmissionError = (error: any): Record<string, string> => {
  const parsedError = parseApiError(error);
  const formErrors: Record<string, string> = {};

  // If we have field-specific errors, process them
  if (parsedError.errors) {
    Object.entries(parsedError.errors).forEach(([field, errorMessages]) => {
      // Take the first error message for each field
      if (errorMessages && errorMessages.length > 0) {
        formErrors[field] = errorMessages[0];
      }
    });
  } 
  
  // If no field-specific errors but we have a general message, add it as a general error
  if (Object.keys(formErrors).length === 0 && parsedError.message) {
    formErrors.general = parsedError.message;
  }

  return formErrors;
};

/**
 * Processes file upload errors into user-friendly format
 * @param error Any error object to be processed
 * @returns Object with error message and error code
 */
export const handleFileUploadError = (error: any): { 
  message: string; 
  code?: string;
} => {
  const parsedError = parseApiError(error);
  
  // Check for specific file upload error types
  if (parsedError.status === 413) {
    return { 
      message: 'The file is too large. Please upload a file smaller than 50MB.',
      code: 'file_too_large'
    };
  }
  
  if (parsedError.errors?.file?.includes('invalid_format')) {
    return { 
      message: 'The file format is not supported. Please upload a file in one of the supported formats.',
      code: 'invalid_format'
    };
  }
  
  if (parsedError.errors?.file?.includes('virus_detected')) {
    return { 
      message: 'The file could not be uploaded because it appears to contain malware.',
      code: 'security_threat'
    };
  }
  
  if (parsedError.errors?.file?.includes('corrupt_file')) {
    return {
      message: 'The file appears to be corrupted. Please try uploading a different file.',
      code: 'corrupt_file'
    };
  }
  
  // Default file upload error message
  return { 
    message: parsedError.message || 'There was a problem uploading your file. Please try again.',
    code: parsedError.status ? `error_${parsedError.status}` : 'upload_error'
  };
};

/**
 * Logs errors for monitoring and debugging
 * @param error Any error object to be logged
 * @param context Additional context for the error
 */
export const logError = (error: any, context: string = 'general'): void => {
  // Format error for logging
  const timestamp = new Date().toISOString();
  const errorDetails = {
    timestamp,
    context,
    message: error?.message || 'Unknown error',
    stack: error?.stack,
    ...(axios.isAxiosError(error) ? {
      status: error.response?.status,
      url: error.config?.url,
      method: error.config?.method,
      data: error.response?.data
    } : {})
  };
  
  // Log to console in development mode
  if (DEBUG_MODE) {
    console.error(
      `%c Error [${context}] %c ${errorDetails.message}`,
      'background: #FF0000; color: white; padding: 2px 4px; border-radius: 3px 0 0 3px;',
      'background: #FF671F; color: white; padding: 2px 4px; border-radius: 0 3px 3px 0;',
      errorDetails
    );
  }
  
  // Track error in analytics
  trackError({
    error_type: context,
    error_message: errorDetails.message,
    error_status: errorDetails.status,
    error_url: errorDetails.url,
    error_method: errorDetails.method
  });
};

/**
 * Formats validation errors for display in forms
 * @param errors Record of field names to arrays of error messages
 * @returns Object mapping field names to error messages
 */
export const formatValidationErrors = (errors: Record<string, string[]>): Record<string, string> => {
  const formattedErrors: Record<string, string> = {};
  
  Object.entries(errors).forEach(([field, errorMessages]) => {
    // Take the first error message for each field
    if (errorMessages && errorMessages.length > 0) {
      formattedErrors[field] = errorMessages[0];
    }
  });
  
  return formattedErrors;
};

/**
 * Gets a user-friendly error message from various error types
 * @param error Any error object
 * @returns User-friendly error message
 */
export const getErrorMessage = (error: any): string => {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<ApiResponse>;
    
    // Check for specific error types
    if (isNetworkError(error)) {
      return 'Unable to connect to the server. Please check your internet connection and try again.';
    }
    
    if (isTimeoutError(error)) {
      return 'The request timed out. Please try again later.';
    }
    
    if (isServerError(error)) {
      return 'We\'re experiencing technical difficulties. Please try again later or contact support if the problem persists.';
    }
    
    // Try to get a message from the response
    const data = axiosError.response?.data as ApiResponse | undefined;
    if (data?.message) {
      return data.message;
    }
  }
  
  // Default error message
  return error?.message || 'An unexpected error occurred. Please try again.';
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

/**
 * Determines if an error is a server-side error (5xx)
 * @param error Any error object
 * @returns True if error is a server error
 */
export const isServerError = (error: any): boolean => {
  if (!axios.isAxiosError(error)) {
    return false;
  }
  
  const status = error.response?.status;
  return status !== undefined && status >= 500 && status < 600;
};