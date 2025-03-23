import { useState, useEffect, useCallback, useRef } from 'react'; // react@^18.2.0
import {
  FileInfo,
  UploadState,
  UploadConfig,
  FileValidationError,
  DEFAULT_UPLOAD_CONFIG,
  INITIAL_UPLOAD_STATE
} from '../types/upload';
import { UploadFormData } from '../types/forms';
import { UploadStatus } from '../types/api';
import {
  validateFile,
  createFileInfo,
  startUpload,
  cancelUpload
} from '../services/uploadService';
import { logError } from '../utils/errorHandling';
import { useUploadStatus } from './useUploadStatus';

/**
 * Return type for the useFileUpload hook
 */
export interface UseFileUploadReturn {
  uploadState: UploadState;
  validateFile: (file: File) => { valid: boolean; error: FileValidationError; errorMessage: string | null };
  handleFileSelect: (file: File) => void;
  startUpload: (formData: UploadFormData) => Promise<void>;
  cancelUpload: () => void;
  resetUpload: () => void;
}

/**
 * Custom React hook that provides comprehensive file upload functionality.
 * Manages the entire file upload process including file selection, validation,
 * upload state tracking, progress monitoring, and error handling.
 * 
 * @param config - Optional configuration for file uploads
 * @returns Object containing upload state and functions for managing file uploads
 */
export const useFileUpload = (config?: UploadConfig): UseFileUploadReturn => {
  // Initialize upload state using useState with INITIAL_UPLOAD_STATE
  const [uploadState, setUploadState] = useState<UploadState>(INITIAL_UPLOAD_STATE);
  
  // Create a ref to store the abort controller for cancellation
  const abortControllerRef = useRef<{ abort: () => void } | null>(null);
  
  // Create a ref to track if the component is mounted
  const isMountedRef = useRef<boolean>(true);
  
  // Ref to store the selected File object
  const selectedFileRef = useRef<File | null>(null);
  
  // Use useUploadStatus hook to track upload status if uploadId exists
  const { uploadState: statusState } = useUploadStatus(
    uploadState.uploadId,
    uploadState
  );
  
  /**
   * Validates a file against the provided upload configuration
   * 
   * @param file - The file to validate
   * @returns Validation result with error information if invalid
   */
  const validateSelectedFile = useCallback((file: File): { 
    valid: boolean; 
    error: FileValidationError; 
    errorMessage: string | null 
  } => {
    return validateFile(file, config || DEFAULT_UPLOAD_CONFIG);
  }, [config]);
  
  /**
   * Handles file selection and performs initial validation
   * 
   * @param file - The selected file
   */
  const handleFileSelect = useCallback((file: File): void => {
    // Store the original File object for later upload
    selectedFileRef.current = file;
    
    // Create file info object with metadata
    const fileInfo = createFileInfo(file);
    
    // Validate file against configuration
    const validation = validateSelectedFile(file);
    
    // Update state based on validation result
    if (validation.valid) {
      setUploadState(prevState => ({
        ...prevState,
        file: fileInfo,
        status: UploadStatus.PENDING,
        error: FileValidationError.NONE,
        errorMessage: null,
      }));
    } else {
      setUploadState(prevState => ({
        ...prevState,
        file: fileInfo,
        status: UploadStatus.FAILED,
        error: validation.error,
        errorMessage: validation.errorMessage,
      }));
    }
  }, [validateSelectedFile]);
  
  /**
   * Handles upload progress updates
   * 
   * @param progress - Upload progress information
   */
  const handleUploadProgress = useCallback((progress: {
    loaded: number;
    total: number;
    percentage: number;
  }): void => {
    if (isMountedRef.current) {
      setUploadState(prevState => ({
        ...prevState,
        progress,
      }));
    }
  }, []);
  
  /**
   * Initiates the file upload process
   * 
   * @param formData - Form data associated with the upload
   * @returns Promise that resolves when upload is initiated
   */
  const startFileUpload = useCallback(async (formData: UploadFormData): Promise<void> => {
    // Make sure we have a file to upload
    if (!selectedFileRef.current || !uploadState.file) {
      return;
    }
    
    try {
      // Set status to uploading
      setUploadState(prevState => ({
        ...prevState,
        status: UploadStatus.UPLOADING,
        error: FileValidationError.NONE,
        errorMessage: null,
      }));
      
      // Start the upload using the service function
      const { uploadState: newUploadState, abort } = await startUpload(
        selectedFileRef.current,
        formData,
        config || DEFAULT_UPLOAD_CONFIG,
        handleUploadProgress
      );
      
      // Store the abort function for potential cancellation
      abortControllerRef.current = { abort };
      
      // Update state with the new upload state
      if (isMountedRef.current) {
        setUploadState(newUploadState);
      }
    } catch (error) {
      // Handle upload errors
      logError(error, 'useFileUpload.startFileUpload');
      
      if (isMountedRef.current) {
        setUploadState(prevState => ({
          ...prevState,
          status: UploadStatus.FAILED,
          error: FileValidationError.UPLOAD_ERROR,
          errorMessage: 'Failed to upload file. Please try again.',
        }));
      }
    }
  }, [uploadState.file, config, handleUploadProgress]);
  
  /**
   * Cancels an ongoing upload
   */
  const cancelFileUpload = useCallback((): void => {
    // Cancel the upload via abort function if available
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    
    // If we have an upload ID, try to cancel it on the server
    if (uploadState.uploadId) {
      cancelUpload(uploadState.uploadId).catch(error => {
        logError(error, 'useFileUpload.cancelFileUpload');
      });
    }
    
    // Update state to reflect cancellation
    setUploadState(prevState => ({
      ...prevState,
      status: UploadStatus.FAILED,
      error: FileValidationError.UPLOAD_ERROR,
      errorMessage: 'Upload canceled.',
    }));
  }, [uploadState.uploadId]);
  
  /**
   * Resets the upload state to initial values
   */
  const resetUpload = useCallback((): void => {
    // Cancel any ongoing upload
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    
    // Clear selected file
    selectedFileRef.current = null;
    
    // Reset state to initial values
    setUploadState(INITIAL_UPLOAD_STATE);
  }, []);
  
  // Update upload state when status changes from the status hook
  useEffect(() => {
    if (
      statusState && 
      statusState.status !== uploadState.status &&
      statusState.uploadId === uploadState.uploadId
    ) {
      setUploadState(prevState => ({
        ...prevState,
        status: statusState.status,
        processingStep: statusState.processingStep || prevState.processingStep,
        estimatedTimeRemaining: statusState.estimatedTimeRemaining || prevState.estimatedTimeRemaining,
        analysisResult: statusState.analysisResult || prevState.analysisResult,
      }));
    }
  }, [statusState, uploadState.status, uploadState.uploadId]);
  
  // Mark component as mounted/unmounted
  useEffect(() => {
    isMountedRef.current = true;
    return () => {
      isMountedRef.current = false;
    };
  }, []);
  
  // Clean up by cancelling upload on unmount
  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
        abortControllerRef.current = null;
      }
    };
  }, []);
  
  // Return object with upload state and control functions
  return {
    uploadState,
    validateFile: validateSelectedFile,
    handleFileSelect,
    startUpload: startFileUpload,
    cancelUpload: cancelFileUpload,
    resetUpload,
  };
};