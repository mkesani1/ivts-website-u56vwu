import { NextResponse } from 'next/server'; // next/server@14.0.0
import { API_ENDPOINTS } from '../../../constants/apiEndpoints';
import { parseApiError, logError } from '../../../utils/errorHandling';
import { UploadCompleteParams } from '../../../types/api';

/**
 * Validates the upload completion parameters
 * @param body - The request body to validate
 * @returns Object indicating if the params are valid, the validated params, and any error message
 */
function validateUploadCompleteParams(body: any): {
  valid: boolean;
  params?: UploadCompleteParams;
  error?: string;
} {
  // Check if body is an object
  if (!body || typeof body !== 'object') {
    return { valid: false, error: 'Invalid request body' };
  }

  // Check required fields
  if (!body.upload_id || typeof body.upload_id !== 'string') {
    return { valid: false, error: 'upload_id is required and must be a string' };
  }

  if (typeof body.success !== 'boolean') {
    return { valid: false, error: 'success is required and must be a boolean' };
  }

  if (!body.etag || typeof body.etag !== 'string') {
    return { valid: false, error: 'etag is required and must be a string' };
  }

  // Return validated params
  const params: UploadCompleteParams = {
    upload_id: body.upload_id,
    success: body.success,
    etag: body.etag
  };

  return { valid: true, params };
}

/**
 * Handles POST requests to the upload completion endpoint.
 * This endpoint is called after a file has been successfully uploaded to the presigned URL
 * to notify the backend that the upload is complete and processing can begin.
 * 
 * @param request - The incoming HTTP request
 * @returns NextResponse with success or error details
 */
export async function POST(request: Request): Promise<NextResponse> {
  try {
    // Extract request body
    const body = await request.json();
    
    // Validate request parameters
    const validation = validateUploadCompleteParams(body);
    if (!validation.valid) {
      return NextResponse.json(
        { success: false, message: validation.error },
        { status: 400 }
      );
    }

    const params = validation.params!;
    
    // If the client reports upload was unsuccessful, still record it but don't process
    if (!params.success) {
      return NextResponse.json({
        success: false,
        message: 'File upload was reported as unsuccessful by the client',
        upload_id: params.upload_id
      }, { status: 200 });
    }

    // Make API request to backend
    const response = await fetch(API_ENDPOINTS.UPLOADS.COMPLETE, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(params),
    });

    // Parse response
    const data = await response.json();

    // Check if request was successful
    if (!response.ok) {
      // Log error details for monitoring
      logError(
        { status: response.status, data, upload_id: params.upload_id },
        'upload-complete-api-backend-error'
      );
      
      return NextResponse.json(
        { 
          success: false, 
          message: data.message || 'Failed to complete upload process',
          errors: data.errors,
          upload_id: params.upload_id
        },
        { status: response.status }
      );
    }

    // Return success response
    return NextResponse.json(data);
  } catch (error) {
    // Log error for monitoring
    logError(error, 'upload-complete-api');
    
    // Parse error for client response
    const parsedError = parseApiError(error);
    
    // Return error response
    return NextResponse.json(
      { 
        success: false, 
        message: parsedError.message || 'An error occurred while completing the upload'
      },
      { status: parsedError.status || 500 }
    );
  }
}