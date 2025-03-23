import { NextResponse } from 'next/server'; // next/server@^13.4.0
import fetch from 'node-fetch'; // node-fetch@^3.3.1
import { API_ENDPOINTS } from '../../../constants/apiEndpoints';
import { validateRequired, validateFileSize, ALLOWED_FILE_TYPES, MAX_FILE_SIZE_MB } from '../../../utils/validation';
import { parseApiError, logError } from '../../../utils/errorHandling';
import { UploadRequestParams } from '../../../types/api';
import { UploadFormData } from '../../../types/forms';

// Backend API URL from environment variables
const BACKEND_API_URL = process.env.BACKEND_API_URL || 'http://localhost:8000/api/v1';

/**
 * Handles POST requests to initiate a file upload
 * 
 * This endpoint validates the upload request, checks file metadata,
 * and requests a presigned URL from the backend for secure direct-to-S3 uploads.
 * 
 * @param request - The incoming request object
 * @returns JSON response with presigned URL or error
 */
export async function POST(request: Request): Promise<NextResponse> {
  try {
    // Parse request body as JSON
    const body = await request.json();

    // Validate upload request parameters
    const validation = validateUploadRequest(body);
    if (!validation.valid || !validation.params) {
      return NextResponse.json(
        { success: false, message: validation.error || 'Invalid upload request' },
        { status: 400 }
      );
    }

    const { filename, size, mime_type, form_data } = validation.params;

    // Validate file metadata (size and type)
    const metadataValidation = validateFileMetadata(mime_type, size);
    if (!metadataValidation.valid) {
      return NextResponse.json(
        { success: false, message: metadataValidation.error },
        { status: 400 }
      );
    }

    // Request presigned URL from backend
    const response = await getPresignedUrl(validation.params);

    // Return success response with presigned URL and upload ID
    return NextResponse.json({
      success: true,
      message: 'Upload authorized',
      upload_id: response.upload_id,
      presigned_url: response.presigned_url,
      presigned_fields: response.presigned_fields,
      expires_at: response.expires_at
    });
  } catch (error) {
    // Log error for monitoring
    logError(error, 'upload_request');

    // Parse error and return appropriate response
    const parsedError = parseApiError(error);
    return NextResponse.json(
      { success: false, message: parsedError.message, errors: parsedError.errors },
      { status: parsedError.status || 500 }
    );
  }
}

/**
 * Validates the upload request parameters
 * 
 * @param body - The request body to validate
 * @returns Validation result with params or error
 */
function validateUploadRequest(body: any): { valid: boolean; params?: UploadRequestParams; error?: string } {
  // Check if body is an object
  if (!body || typeof body !== 'object') {
    return { valid: false, error: 'Invalid request body' };
  }

  // Extract parameters
  const { filename, size, mime_type, form_data } = body;

  // Validate required parameters
  if (!filename || typeof filename !== 'string') {
    return { valid: false, error: 'Filename is required and must be a string' };
  }

  if (size === undefined || typeof size !== 'number' || size <= 0) {
    return { valid: false, error: 'Size is required and must be a positive number' };
  }

  if (!mime_type || typeof mime_type !== 'string') {
    return { valid: false, error: 'MIME type is required and must be a string' };
  }

  if (!form_data || typeof form_data !== 'object') {
    return { valid: false, error: 'Form data is required and must be an object' };
  }

  // Validate required form data fields
  const nameError = validateRequired(form_data.name);
  if (nameError) {
    return { valid: false, error: 'Name is required' };
  }

  const emailError = validateRequired(form_data.email);
  if (emailError) {
    return { valid: false, error: 'Email is required' };
  }

  const companyError = validateRequired(form_data.company);
  if (companyError) {
    return { valid: false, error: 'Company is required' };
  }

  // Return validated parameters
  return {
    valid: true,
    params: {
      filename,
      size,
      mime_type,
      form_data: form_data as UploadFormData
    }
  };
}

/**
 * Validates file metadata against size and type restrictions
 * 
 * @param mimeType - The MIME type of the file
 * @param sizeBytes - The size of the file in bytes
 * @returns Validation result with optional error message
 */
function validateFileMetadata(mimeType: string, sizeBytes: number): { valid: boolean; error?: string } {
  // Check file size
  const sizeMB = sizeBytes / (1024 * 1024);
  if (sizeMB > MAX_FILE_SIZE_MB) {
    return {
      valid: false,
      error: `File size (${sizeMB.toFixed(2)} MB) exceeds maximum allowed size (${MAX_FILE_SIZE_MB} MB)`
    };
  }

  // Check file type
  if (!ALLOWED_FILE_TYPES.includes(mimeType)) {
    return {
      valid: false,
      error: `File type (${mimeType}) is not allowed. Supported types: ${ALLOWED_FILE_TYPES.join(', ')}`
    };
  }

  return { valid: true };
}

/**
 * Requests a presigned URL from the backend API
 * 
 * @param params - The upload request parameters
 * @returns Promise resolving to presigned URL response
 */
async function getPresignedUrl(params: UploadRequestParams): Promise<any> {
  // Construct the backend API URL for upload requests
  const url = `${BACKEND_API_URL}/uploads/request`;

  // Prepare request options
  const options = {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(params)
  };

  // Make request to backend API
  const response = await fetch(url, options);

  // Check if response is successful
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw {
      message: errorData.message || `Failed to get presigned URL: ${response.status} ${response.statusText}`,
      status: response.status,
      errors: errorData.errors
    };
  }

  // Parse and return response data
  const data = await response.json();
  return data;
}