import { NextResponse } from 'next/server'; // next/server@^13.4.0
import { API_ENDPOINTS } from '../../../../../constants/apiEndpoints';
import { parseApiError, logError } from '../../../../../utils/errorHandling';
import { UploadStatusResponse } from '../../../../../types/api';

// Backend API URL from environment variable or default
const BACKEND_API_URL = process.env.BACKEND_API_URL || 'http://localhost:8000/api/v1';

/**
 * Handles GET requests to check the status of a file upload
 * 
 * @param request - The incoming request object
 * @param params - Route parameters containing the upload ID
 * @returns JSON response with upload status or error
 */
export async function GET(
  request: Request,
  { params }: { params: { id: string } }
) {
  try {
    // Extract upload ID from route parameters
    const uploadId = params.id;

    // Validate that we have a valid upload ID
    if (!uploadId || typeof uploadId !== 'string') {
      return NextResponse.json(
        { success: false, message: 'Missing or invalid upload ID' },
        { status: 400 }
      );
    }

    // Fetch the status from the backend API
    const uploadStatus = await getUploadStatus(uploadId);

    // Return the status information
    return NextResponse.json({
      success: true,
      data: uploadStatus
    });
  } catch (error) {
    // Handle any errors that occur
    const parsedError = parseApiError(error);
    logError(error, 'api-upload-status');

    // Return appropriate error response based on the status code
    return NextResponse.json(
      { 
        success: false, 
        message: parsedError.message,
        errors: parsedError.errors
      },
      { status: parsedError.status || 500 }
    );
  }
}

/**
 * Fetches the upload status from the backend API
 * 
 * @param uploadId - The ID of the upload to check
 * @returns Promise resolving to upload status data
 */
async function getUploadStatus(uploadId: string): Promise<UploadStatusResponse> {
  // Construct the URL by replacing the placeholder in the endpoint template
  const url = `${BACKEND_API_URL}${API_ENDPOINTS.UPLOADS.STATUS.replace('{uploadId}', uploadId)}`;
  
  // Set up the request options
  const options = {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  };

  // Make the request to the backend API
  const response = await fetch(url, options);
  
  // Check if the response is successful
  if (!response.ok) {
    // Parse the error response
    const errorData = await response.json().catch(() => ({}));
    
    // Throw an error with the status and data for higher-level handling
    throw {
      response: {
        status: response.status,
        data: errorData
      }
    };
  }

  // Parse and return the successful response
  const data = await response.json();
  return data;
}