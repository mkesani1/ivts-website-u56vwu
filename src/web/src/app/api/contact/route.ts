import axios from 'axios'; // axios@^1.4.0
import { ContactFormData } from '../../../types/forms';
import { validateForm } from '../../../utils/validation';
import { getContactFormValidationRules } from '../../../services/formSubmissionService';
import { logError, formatValidationErrors } from '../../../utils/errorHandling';

// Environment variables
const RECAPTCHA_SECRET_KEY = process.env.RECAPTCHA_SECRET_KEY;
const BACKEND_API_URL = process.env.BACKEND_API_URL;
const RECAPTCHA_VERIFICATION_URL = 'https://www.google.com/recaptcha/api/siteverify';

/**
 * Verifies a reCAPTCHA token with Google's verification API
 * @param token - The reCAPTCHA token to verify
 * @returns Promise resolving to true if token is valid, false otherwise
 */
async function verifyRecaptchaToken(token: string): Promise<boolean> {
  try {
    // Create URL parameters with secret key and token
    const params = new URLSearchParams();
    params.append('secret', RECAPTCHA_SECRET_KEY || '');
    params.append('response', token);

    // Make POST request to Google reCAPTCHA verification API
    const response = await axios.post(RECAPTCHA_VERIFICATION_URL, params);
    
    // Check if response indicates success and score above threshold
    if (response.data && response.data.success) {
      // For v3 reCAPTCHA, also check the score (typically > 0.5 is considered human)
      if (response.data.score !== undefined) {
        return response.data.score >= 0.5;
      }
      return true;
    }
    
    return false;
  } catch (error) {
    // Catch and log any errors during verification
    logError(error, 'recaptcha-verification');
    // Return false if verification fails due to error
    return false;
  }
}

/**
 * Handles POST requests for contact form submissions
 * @param request - The incoming request object
 * @returns Promise resolving to HTTP response
 */
export async function POST(request: Request): Promise<Response> {
  try {
    // Parse JSON body from request
    const body = await request.json();
    
    // Extract contact form data and reCAPTCHA token
    const { recaptchaToken, ...formData } = body as ContactFormData;
    
    // Get validation rules for contact form
    const validationRules = getContactFormValidationRules();
    
    // Validate form data against rules
    const validationErrors = validateForm(formData, validationRules);
    
    // If validation errors exist, return 400 response with formatted errors
    if (Object.keys(validationErrors).length > 0) {
      // Convert single error messages to arrays for API response format
      const apiErrors: Record<string, string[]> = {};
      Object.entries(validationErrors).forEach(([field, errorMessage]) => {
        apiErrors[field] = [errorMessage];
      });
      
      return new Response(
        JSON.stringify({
          success: false,
          message: 'Validation failed',
          errors: apiErrors
        }),
        {
          status: 400,
          headers: {
            'Content-Type': 'application/json'
          }
        }
      );
    }
    
    // Verify reCAPTCHA token
    const isValidToken = await verifyRecaptchaToken(recaptchaToken);
    
    // If reCAPTCHA verification fails, return 400 response with CAPTCHA error
    if (!isValidToken) {
      return new Response(
        JSON.stringify({
          success: false,
          message: 'CAPTCHA verification failed',
          errors: {
            recaptchaToken: ['Please complete the CAPTCHA verification']
          }
        }),
        {
          status: 400,
          headers: {
            'Content-Type': 'application/json'
          }
        }
      );
    }
    
    // Prepare data for backend API request
    const apiData = {
      ...formData,
      // Additional metadata if needed
      source: 'website',
      submitted_at: new Date().toISOString()
    };
    
    // Make POST request to backend API contact endpoint
    const apiResponse = await axios.post(`${BACKEND_API_URL}/contact`, apiData, {
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    // If backend request succeeds, return 200 response with success data
    return new Response(
      JSON.stringify({
        success: true,
        message: 'Contact form submitted successfully',
        data: apiResponse.data
      }),
      {
        status: 200,
        headers: {
          'Content-Type': 'application/json'
        }
      }
    );
  } catch (error) {
    // Log error and create appropriate error response
    logError(error, 'contact-form-submission');
    
    // Determine error status and message based on error type
    let status = 500;
    let message = 'An unexpected error occurred while processing your request';
    let errors = {};
    
    if (axios.isAxiosError(error)) {
      if (error.response) {
        status = error.response.status;
        message = error.response.data?.message || 'Error submitting contact form';
        errors = error.response.data?.errors || {};
      } else if (error.request) {
        status = 503;
        message = 'Unable to reach the server. Please try again later.';
      }
    }
    
    // Return error response
    return new Response(
      JSON.stringify({
        success: false,
        message,
        errors
      }),
      {
        status,
        headers: {
          'Content-Type': 'application/json'
        }
      }
    );
  }
}