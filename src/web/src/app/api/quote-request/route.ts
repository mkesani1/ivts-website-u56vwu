import { NextRequest, NextResponse } from 'next/server'; // ^13.4.0
import { submitQuoteRequest } from '../../../services/api';
import { QuoteRequestFormData } from '../../../types/forms';
import { getQuoteRequestValidationRules } from '../../../services/formSubmissionService';
import { validateForm } from '../../../utils/validation';
import { logError } from '../../../utils/errorHandling';

// Get reCAPTCHA secret key from environment variables
const RECAPTCHA_SECRET_KEY = process.env.RECAPTCHA_SECRET_KEY;

/**
 * Verifies a reCAPTCHA token with Google's verification API
 * @param token reCAPTCHA token to verify
 * @returns Promise resolving to true if verification succeeds, false otherwise
 */
async function verifyRecaptcha(token: string): Promise<boolean> {
  if (!token) {
    return false;
  }

  try {
    const response = await fetch('https://www.google.com/recaptcha/api/siteverify', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: new URLSearchParams({
        secret: RECAPTCHA_SECRET_KEY ?? '',
        response: token,
      }),
    });

    const data = await response.json();
    
    if (!data.success) {
      logError({ 
        message: "reCAPTCHA verification failed", 
        errorCodes: data['error-codes'] 
      }, 'reCAPTCHA verification');
    }
    
    return data.success === true;
  } catch (error) {
    logError(error, 'reCAPTCHA verification');
    return false;
  }
}

/**
 * Handles POST requests for quote request form submissions
 * @param request Next.js request object
 * @returns Next.js response object
 */
export async function POST(request: NextRequest): Promise<NextResponse> {
  try {
    // Parse request body
    const body = await request.json();
    const formData: QuoteRequestFormData = body;
    const recaptchaToken = formData.recaptchaToken;

    // Validate form data
    const validationRules = getQuoteRequestValidationRules();
    const validationErrors = validateForm(formData, validationRules);

    if (Object.keys(validationErrors).length > 0) {
      return NextResponse.json({
        success: false,
        message: 'Validation failed',
        errors: validationErrors,
      }, { status: 400 });
    }

    // Verify reCAPTCHA token
    const isRecaptchaValid = await verifyRecaptcha(recaptchaToken);
    if (!isRecaptchaValid) {
      return NextResponse.json({
        success: false,
        message: 'reCAPTCHA verification failed',
        errors: {
          recaptcha: 'Failed to verify reCAPTCHA. Please try again.'
        }
      }, { status: 400 });
    }

    // Submit form data to backend API
    const response = await submitQuoteRequest(formData);

    // Return success response
    return NextResponse.json({
      success: true,
      message: 'Quote request submitted successfully',
      data: response
    });
  } catch (error: any) {
    // Log the error with context
    logError(error, 'quote-request API route');

    // Determine the appropriate status code
    const status = error.status || 500;
    
    // Return error response with appropriate message
    return NextResponse.json({
      success: false,
      message: error.message || 'Failed to process quote request',
      errors: error.errors || { 
        general: 'An unexpected error occurred. Please try again later.' 
      }
    }, { status });
  }
}