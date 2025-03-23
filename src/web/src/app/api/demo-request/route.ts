import { NextRequest, NextResponse } from 'next/server';
import { submitDemoRequest } from '../../../services/api';
import { DemoRequestFormData } from '../../../types/forms';
import { getDemoRequestValidationRules } from '../../../services/formSubmissionService';
import { validateForm } from '../../../utils/validation';
import { logError } from '../../../utils/errorHandling';

// Get reCAPTCHA secret key from environment variables
const RECAPTCHA_SECRET_KEY = process.env.RECAPTCHA_SECRET_KEY;

/**
 * Verifies a reCAPTCHA token with Google's verification API
 * @param token The reCAPTCHA token to verify
 * @returns Promise resolving to true if verification succeeds, false otherwise
 */
async function verifyRecaptcha(token: string): Promise<boolean> {
  if (!token) {
    return false;
  }

  try {
    // Construct request body with secret key, token, and remote IP
    const body = new URLSearchParams({
      secret: RECAPTCHA_SECRET_KEY || '',
      response: token
    });

    // Send POST request to Google reCAPTCHA verification API
    const response = await fetch('https://www.google.com/recaptcha/api/siteverify', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      body: body.toString()
    });

    // Parse response and check success status
    const data = await response.json();
    return data.success === true;
  } catch (error) {
    // Log any errors that occur during verification
    logError(error, 'reCAPTCHA verification');
    return false;
  }
}

/**
 * Handles POST requests for demo request form submissions
 * @param request The incoming Next.js request
 * @returns Promise resolving to a Next.js response
 */
export async function POST(request: NextRequest): Promise<NextResponse> {
  try {
    // Parse the request body as JSON
    const body = await request.json();
    const { recaptchaToken, ...formData } = body as DemoRequestFormData & { recaptchaToken: string };

    // Get validation rules for demo request form
    const validationRules = getDemoRequestValidationRules();

    // Validate form data against rules
    const validationErrors = validateForm(formData, validationRules);
    if (Object.keys(validationErrors).length > 0) {
      // If validation errors exist, return 400 response with errors
      return NextResponse.json(
        {
          success: false,
          message: 'Validation failed',
          errors: validationErrors
        },
        { status: 400 }
      );
    }

    // Verify reCAPTCHA token using verifyRecaptcha function
    const isRecaptchaValid = await verifyRecaptcha(recaptchaToken);
    if (!isRecaptchaValid) {
      // If reCAPTCHA verification fails, return 400 response with error
      return NextResponse.json(
        {
          success: false,
          message: 'reCAPTCHA verification failed',
          errors: { recaptcha: 'Please complete the reCAPTCHA verification.' }
        },
        { status: 400 }
      );
    }

    // Submit form data to backend API using submitDemoRequest function
    const response = await submitDemoRequest({
      ...formData,
      recaptchaToken
    });

    // Return success response with data from API
    return NextResponse.json({
      success: true,
      message: 'Demo request submitted successfully',
      data: response
    });
  } catch (error) {
    // Log errors with appropriate context
    logError(error, 'demo-request API route');

    // Determine appropriate status code and error message
    let statusCode = 500;
    let errorMessage = 'An unexpected error occurred while processing your demo request.';

    if (error instanceof Error) {
      if (error.message.includes('validation')) {
        statusCode = 400;
      } else if (error.message.includes('timeout') || error.message.includes('network')) {
        statusCode = 503;
      }
    }

    // Return error response with appropriate status code and message
    return NextResponse.json(
      {
        success: false,
        message: errorMessage,
        error: process.env.NODE_ENV === 'development' ? String(error) : undefined
      },
      { status: statusCode }
    );
  }
}