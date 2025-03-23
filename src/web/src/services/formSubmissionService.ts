/**
 * Form Submission Service
 * 
 * This service handles form submissions for the IndiVillage website, including contact forms,
 * demo requests, and quote requests. It provides a higher-level abstraction over the API service,
 * adding validation, error handling, analytics tracking, and reCAPTCHA verification.
 * 
 * @module services/formSubmissionService
 * @version 1.0.0
 */

import { submitContactForm, submitDemoRequest, submitQuoteRequest } from './api';
import { 
  ContactFormData, 
  DemoRequestFormData, 
  QuoteRequestFormData, 
  FormResponse 
} from '../types/forms';
import {
  ContactResponse,
  DemoRequestResponse,
  QuoteRequestResponse,
  FormErrorResponse
} from '../types/api';
import { executeRecaptchaV3 } from '../lib/recaptcha';
import { validateForm } from '../utils/validation';
import { handleFormSubmissionError, logError } from '../utils/errorHandling';
import { trackFormSubmission, trackConversion } from '../utils/analytics';

/**
 * Returns validation rules for contact form fields
 * @returns Validation rules for contact form fields
 */
export const getContactFormValidationRules = (): Record<string, any> => {
  return {
    name: {
      required: true,
      maxLength: 100
    },
    email: {
      required: true,
      email: true
    },
    phone: {
      phone: true // Optional
    },
    company: {
      required: true
    },
    message: {
      required: true,
      minLength: 10,
      maxLength: 1000
    }
  };
};

/**
 * Returns validation rules for demo request form fields
 * @returns Validation rules for demo request form fields
 */
export const getDemoRequestValidationRules = (): Record<string, any> => {
  return {
    firstName: {
      required: true,
      maxLength: 50
    },
    lastName: {
      required: true,
      maxLength: 50
    },
    email: {
      required: true,
      email: true
    },
    phone: {
      phone: true // Optional
    },
    company: {
      required: true
    },
    jobTitle: {
      required: true
    },
    serviceInterests: {
      required: true
    },
    preferredDate: {
      required: true
    },
    preferredTime: {
      required: true
    },
    timeZone: {
      required: true
    },
    projectDetails: {
      maxLength: 2000 // Optional
    },
    referralSource: {} // Optional
  };
};

/**
 * Returns validation rules for quote request form fields
 * @returns Validation rules for quote request form fields
 */
export const getQuoteRequestValidationRules = (): Record<string, any> => {
  return {
    firstName: {
      required: true,
      maxLength: 50
    },
    lastName: {
      required: true,
      maxLength: 50
    },
    email: {
      required: true,
      email: true
    },
    phone: {
      phone: true // Optional
    },
    company: {
      required: true
    },
    jobTitle: {
      required: true
    },
    serviceInterests: {
      required: true
    },
    projectDetails: {
      required: true,
      minLength: 50,
      maxLength: 2000
    },
    budgetRange: {
      required: true
    },
    timeline: {
      required: true
    },
    referralSource: {} // Optional
  };
};

/**
 * Submits a contact form with validation and reCAPTCHA verification
 * @param formData Contact form data
 * @returns Promise resolving to form submission response
 */
export const submitContactFormWithValidation = async (
  formData: ContactFormData
): Promise<FormResponse> => {
  try {
    // Validate form data
    const validationRules = getContactFormValidationRules();
    const validationErrors = validateForm(formData, validationRules);
    
    if (Object.keys(validationErrors).length > 0) {
      return {
        success: false,
        message: 'Validation failed',
        errors: validationErrors
      };
    }
    
    // Execute reCAPTCHA verification
    const recaptchaToken = await executeRecaptchaV3('contact_form');
    const formDataWithToken = {
      ...formData,
      recaptchaToken
    };
    
    // Submit form data to API
    const response = await submitContactForm(formDataWithToken);
    
    // Track form submission in analytics
    trackFormSubmission('contact_form', {
      form_type: 'contact',
      company_provided: !!formData.company
    });
    
    // Track conversion event
    trackConversion('contact_form', {
      conversion_type: 'contact',
      value: 10 // Lower value for contact form
    });
    
    // Return success response
    return formatFormResponse(response);
  } catch (error) {
    // Log error and return error response
    logError(error, 'submitContactForm');
    return formatFormErrorResponse(error);
  }
};

/**
 * Submits a demo request form with validation and reCAPTCHA verification
 * @param formData Demo request form data
 * @returns Promise resolving to form submission response
 */
export const submitDemoRequestWithValidation = async (
  formData: DemoRequestFormData
): Promise<FormResponse> => {
  try {
    // Validate form data
    const validationRules = getDemoRequestValidationRules();
    const validationErrors = validateForm(formData, validationRules);
    
    if (Object.keys(validationErrors).length > 0) {
      return {
        success: false,
        message: 'Validation failed',
        errors: validationErrors
      };
    }
    
    // Execute reCAPTCHA verification
    const recaptchaToken = await executeRecaptchaV3('demo_request');
    const formDataWithToken = {
      ...formData,
      recaptchaToken
    };
    
    // Submit form data to API
    const response = await submitDemoRequest(formDataWithToken);
    
    // Track form submission in analytics
    trackFormSubmission('demo_request', {
      form_type: 'demo_request',
      services_selected: formData.serviceInterests?.length || 0
    });
    
    // Track conversion event with higher value
    trackConversion('demo_request', {
      conversion_type: 'demo_request',
      value: 50, // Higher value for demo request
      services: formData.serviceInterests
    });
    
    // Return success response
    return formatFormResponse(response);
  } catch (error) {
    // Log error and return error response
    logError(error, 'submitDemoRequest');
    return formatFormErrorResponse(error);
  }
};

/**
 * Submits a quote request form with validation and reCAPTCHA verification
 * @param formData Quote request form data
 * @returns Promise resolving to form submission response
 */
export const submitQuoteRequestWithValidation = async (
  formData: QuoteRequestFormData
): Promise<FormResponse> => {
  try {
    // Validate form data
    const validationRules = getQuoteRequestValidationRules();
    const validationErrors = validateForm(formData, validationRules);
    
    if (Object.keys(validationErrors).length > 0) {
      return {
        success: false,
        message: 'Validation failed',
        errors: validationErrors
      };
    }
    
    // Execute reCAPTCHA verification
    const recaptchaToken = await executeRecaptchaV3('quote_request');
    const formDataWithToken = {
      ...formData,
      recaptchaToken
    };
    
    // Submit form data to API
    const response = await submitQuoteRequest(formDataWithToken);
    
    // Track form submission in analytics
    trackFormSubmission('quote_request', {
      form_type: 'quote_request',
      services_selected: formData.serviceInterests?.length || 0,
      budget_range: formData.budgetRange,
      timeline: formData.timeline
    });
    
    // Track conversion event with highest value
    trackConversion('quote_request', {
      conversion_type: 'quote_request',
      value: 100, // Highest value for quote request
      services: formData.serviceInterests,
      budget: formData.budgetRange,
      timeline: formData.timeline
    });
    
    // Return success response
    return formatFormResponse(response);
  } catch (error) {
    // Log error and return error response
    logError(error, 'submitQuoteRequest');
    return formatFormErrorResponse(error);
  }
};

/**
 * Formats API response into a standardized form response
 * @param response API response
 * @returns Standardized form response
 */
const formatFormResponse = (response: any): FormResponse => {
  return {
    success: response.success,
    message: response.message,
    data: response
  };
};

/**
 * Formats error into a standardized form error response
 * @param error Error object
 * @returns Standardized form error response
 */
const formatFormErrorResponse = (error: any): FormResponse => {
  const processedError = handleFormSubmissionError(error);
  
  return {
    success: false,
    message: processedError.general || 'An error occurred while submitting the form. Please try again.',
    errors: processedError
  };
};