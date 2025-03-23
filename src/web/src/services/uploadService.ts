/**
 * Upload Service
 * 
 * Provides comprehensive file upload functionality for the IndiVillage website.
 * Handles file validation, upload processing, status tracking, and integration
 * with backend API endpoints for the sample data upload feature.
 * 
 * @module services/uploadService
 * @version 1.0.0
 */

import {
  requestFileUpload,
  uploadFileToPresignedUrl,
  getUploadStatus,
  deleteUpload
} from './api';

import {
  FileType,
  FileValidationError,
  FileInfo,
  UploadState,
  UploadConfig,
  UploadProgress,
  getFileTypeFromMimeType,
  getFileTypeFromExtension,
  DEFAULT_UPLOAD_CONFIG,
  UploadRequestParams
} from '../types/upload';

import { UploadStatus } from '../types/api';
import { logError, handleFileUploadError } from '../utils/errorHandling';

/**
 * Validates a file against the provided upload configuration
 * 
 * @param file - The file to validate
 * @param config - Upload configuration options
 * @returns Validation result with error information if invalid
 */
export const validateFile = (
  file: File,
  config: UploadConfig = DEFAULT_UPLOAD_CONFIG
): { valid: boolean; error: FileValidationError; errorMessage: string | null } => {
  // Check if file exists
  if (!file || file.size === 0) {
    return {
      valid: false,
      error: FileValidationError.EMPTY_FILE,
      errorMessage: 'Please select a valid file.'
    };
  }

  // Check file size
  if (file.size > config.maxSizeBytes) {
    const maxSizeMB = config.maxSizeBytes / (1024 * 1024);
    return {
      valid: false,
      error: FileValidationError.FILE_TOO_LARGE,
      errorMessage: `File is too large. Maximum allowed size is ${maxSizeMB}MB.`
    };
  }

  // Get file extension from file name
  const extension = file.name.split('.').pop() || '';
  
  // Determine file type from MIME type and extension
  const fileTypeFromMime = getFileTypeFromMimeType(file.type);
  const fileTypeFromExt = getFileTypeFromExtension(extension);
  const fileType = fileTypeFromMime || fileTypeFromExt;

  // Check if file type is allowed
  if (!fileType || !config.allowedTypes.includes(fileType)) {
    return {
      valid: false,
      error: FileValidationError.INVALID_TYPE,
      errorMessage: 'File type is not supported. Please upload a file in one of the supported formats.'
    };
  }

  // File is valid
  return {
    valid: true,
    error: FileValidationError.NONE,
    errorMessage: null
  };
};

/**
 * Creates a structured FileInfo object from a File object
 * 
 * @param file - The file to extract information from
 * @returns Structured file information
 */
export const createFileInfo = (file: File): FileInfo => {
  // Extract file extension from file name
  const nameParts = file.name.split('.');
  const extension = nameParts.length > 1 ? nameParts.pop()?.toLowerCase() || '' : '';
  
  // Determine file type from MIME type and extension
  const fileType = getFileTypeFromMimeType(file.type) || getFileTypeFromExtension(extension);
  
  return {
    name: file.name,
    size: file.size,
    type: file.type,
    extension,
    fileType,
    lastModified: file.lastModified
  };
};

/**
 * Calculates upload progress percentage
 * 
 * @param loaded - Number of bytes loaded
 * @param total - Total number of bytes to load
 * @returns Upload progress information
 */
export const getUploadProgress = (loaded: number, total: number): UploadProgress => {
  const percentage = total > 0 ? Math.min(Math.round((loaded / total) * 100), 100) : 0;
  
  return {
    loaded,
    total,
    percentage
  };
};

/**
 * Initiates the file upload process
 * 
 * @param file - The file to upload
 * @param formData - Form data associated with the upload
 * @param config - Upload configuration options
 * @param onProgress - Callback function for tracking upload progress
 * @returns Promise resolving to upload state and abort function
 */
export const startUpload = async (
  file: File,
  formData: UploadFormData,
  config: UploadConfig = DEFAULT_UPLOAD_CONFIG,
  onProgress: (progress: UploadProgress) => void
): Promise<{ uploadState: UploadState; abort: () => void }> => {
  try {
    // Validate the file
    const validation = validateFile(file, config);
    if (!validation.valid) {
      return {
        uploadState: {
          file: createFileInfo(file),
          status: UploadStatus.FAILED,
          progress: { loaded: 0, total: file.size, percentage: 0 },
          uploadId: null,
          error: validation.error,
          errorMessage: validation.errorMessage,
          processingStep: null,
          estimatedTimeRemaining: null,
          analysisResult: null
        },
        abort: () => {}
      };
    }

    // Create file info
    const fileInfo = createFileInfo(file);

    // Prepare upload parameters
    const uploadParams: UploadRequestParams = {
      filename: file.name,
      size: file.size,
      mime_type: file.type,
      form_data: formData
    };

    // Request presigned URL from backend
    const uploadResponse = await requestFileUpload(uploadParams);
    const uploadId = uploadResponse.upload_id;

    // Create abort controller for cancellation capability
    const abortController = new AbortController();
    const abort = () => {
      abortController.abort();
      // Attempt to cancel the upload on the server side as well
      if (uploadId) {
        deleteUpload(uploadId).catch(error => {
          logError(error, 'cancelUpload');
        });
      }
    };

    // Create initial upload state
    let uploadState: UploadState = {
      file: fileInfo,
      status: UploadStatus.UPLOADING,
      progress: { loaded: 0, total: file.size, percentage: 0 },
      uploadId,
      error: FileValidationError.NONE,
      errorMessage: null,
      processingStep: null,
      estimatedTimeRemaining: null,
      analysisResult: null
    };

    // Set up progress tracking
    const progressListener = (progressEvent: ProgressEvent) => {
      const progress = getUploadProgress(progressEvent.loaded, progressEvent.total);
      onProgress(progress);
      uploadState.progress = progress;
    };

    try {
      // Upload file to presigned URL
      const uploadResult = await uploadFileToPresignedUrl(file, uploadResponse);
      
      // Update upload state based on result
      if (uploadResult.upload_id === uploadId) {
        uploadState.status = UploadStatus.UPLOADED;
        uploadState.progress.percentage = 100;
      }
    } catch (error) {
      // Handle upload failure
      const uploadError = handleFileUploadError(error);
      uploadState.status = UploadStatus.FAILED;
      uploadState.error = FileValidationError.UPLOAD_ERROR;
      uploadState.errorMessage = uploadError.message;
      logError(error, 'startUpload');
    }

    return { uploadState, abort };
  } catch (error) {
    // Handle any unexpected errors
    logError(error, 'startUpload');
    
    return {
      uploadState: {
        file: createFileInfo(file),
        status: UploadStatus.FAILED,
        progress: { loaded: 0, total: file.size, percentage: 0 },
        uploadId: null,
        error: FileValidationError.UPLOAD_ERROR,
        errorMessage: 'An unexpected error occurred during upload. Please try again.',
        processingStep: null,
        estimatedTimeRemaining: null,
        analysisResult: null
      },
      abort: () => {}
    };
  }
};

/**
 * Cancels an ongoing upload
 * 
 * @param uploadId - ID of the upload to cancel
 * @returns Promise resolving to cancellation success status
 */
export const cancelUpload = async (uploadId: string): Promise<boolean> => {
  try {
    const result = await deleteUpload(uploadId);
    return result.success;
  } catch (error) {
    logError(error, 'cancelUpload');
    return false;
  }
};

/**
 * Checks the status of an ongoing upload
 * 
 * @param uploadId - ID of the upload to check
 * @returns Promise resolving to current upload status information
 */
export const checkUploadStatus = async (uploadId: string): Promise<{
  status: UploadStatus;
  processingStep?: string;
  estimatedTimeRemaining?: number;
  analysisResult?: Record<string, any>;
}> => {
  try {
    const statusResponse = await getUploadStatus(uploadId);
    
    return {
      status: statusResponse.status,
      processingStep: statusResponse.status === UploadStatus.PROCESSING ? 
        'Analyzing data structure' : undefined,
      estimatedTimeRemaining: statusResponse.status === UploadStatus.PROCESSING ? 
        120 : undefined, // Default estimate of 2 minutes
      analysisResult: statusResponse.analysis_result
    };
  } catch (error) {
    logError(error, 'checkUploadStatus');
    throw error;
  }
};

/**
 * Calculates estimated time remaining for processing based on elapsed time and progress
 * 
 * @param startTime - Start time in milliseconds
 * @param progress - Current progress percentage (0-100)
 * @returns Estimated time remaining in seconds
 */
export const getEstimatedTimeRemaining = (startTime: number, progress: number): number => {
  const now = Date.now();
  const elapsedTime = (now - startTime) / 1000; // Convert to seconds
  
  // If no progress yet, return a default estimate
  if (progress <= 0) {
    return 120; // Default estimate of 2 minutes
  }
  
  // Calculate estimated total time based on elapsed time and progress
  const estimatedTotalTime = elapsedTime * (100 / progress);
  
  // Calculate remaining time
  const remainingTime = Math.max(0, estimatedTotalTime - elapsedTime);
  
  return Math.round(remainingTime);
};