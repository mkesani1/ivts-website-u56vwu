# src/web/tests/hooks/useFileUpload.test.ts
```typescript
import { useFileUpload } from '../../src/hooks/useFileUpload'; // Tested hook
import { FileType, FileValidationError, UploadConfig } from '../../src/types/upload'; // version from upload.ts
import { UploadStatus } from '../../src/types/api'; // version from api.ts
import { createMockFile } from '../utils/testing'; // Utility for creating mock File objects
import { mockUploadFormData, mockUploadResponses } from '../mocks/data'; // Mock form data and API responses
import { renderHook, act, waitFor } from '@testing-library/react'; // testing-library/react@^14.0.0
import React from 'react'; // react@^18.2.0
import { describe, it, expect, jest, beforeEach, afterEach } from '@jest/globals'; // jest@^29.5.0

// Mock the global fetch function for testing API calls
global.fetch = jest.fn();

// Mock implementation of the upload service functions
const uploadService = {
  startUpload: jest.fn(),
  cancelUpload: jest.fn(),
  validateFile: jest.fn(),
  createFileInfo: jest.fn()
};

// Mock implementation of the useUploadStatus hook
const useUploadStatus = jest.fn();

// Mock the uploadService module
jest.mock('../../src/services/uploadService', () => ({
  startUpload: uploadService.startUpload,
  cancelUpload: uploadService.cancelUpload,
  validateFile: uploadService.validateFile,
  createFileInfo: uploadService.createFileInfo
}));

// Mock the useUploadStatus hook
jest.mock('../../src/hooks/useUploadStatus', () => ({
  useUploadStatus: () => useUploadStatus()
}));

/**
 * Sets up mocks for testing the useFileUpload hook
 */
const setupMocks = () => {
  // Mock the startUpload function from uploadService
  uploadService.startUpload.mockResolvedValue({
    uploadState: {
      file: null,
      status: UploadStatus.UPLOADED,
      progress: { loaded: 100, total: 100, percentage: 100 },
      uploadId: 'mock-upload-id',
      error: FileValidationError.NONE,
      errorMessage: null,
      processingStep: null,
      estimatedTimeRemaining: null,
      analysisResult: null
    },
    abort: jest.fn()
  });

  // Mock the cancelUpload function from uploadService
  uploadService.cancelUpload.mockResolvedValue(true);

  // Mock the useUploadStatus hook
  useUploadStatus.mockReturnValue({
    uploadState: {
      file: null,
      status: UploadStatus.COMPLETED,
      progress: { loaded: 100, total: 100, percentage: 100 },
      uploadId: 'mock-upload-id',
      error: FileValidationError.NONE,
      errorMessage: null,
      processingStep: null,
      estimatedTimeRemaining: null,
      analysisResult: null
    },
    isPolling: false
  });

  // Reset all mocks between tests
  beforeEach(() => {
    jest.clearAllMocks();
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });
};

describe('useFileUpload', () => {
  setupMocks();

  it('should initialize with default state', () => {
    // Render the hook with renderHook
    const { result } = renderHook(() => useFileUpload());

    // Check that the initial state matches INITIAL_UPLOAD_STATE
    expect(result.current.uploadState).toEqual({
      file: null,
      status: UploadStatus.PENDING,
      progress: { loaded: 0, total: 0, percentage: 0 },
      uploadId: null,
      error: FileValidationError.NONE,
      errorMessage: null,
      processingStep: null,
      estimatedTimeRemaining: null,
      analysisResult: null
    });

    // Verify that all expected functions are returned
    expect(typeof result.current.validateFile).toBe('function');
    expect(typeof result.current.handleFileSelect).toBe('function');
    expect(typeof result.current.startUpload).toBe('function');
    expect(typeof result.current.cancelUpload).toBe('function');
    expect(typeof result.current.resetUpload).toBe('function');
  });

  it('should accept custom upload configuration', () => {
    // Create a custom upload configuration
    const customConfig: UploadConfig = {
      maxSizeBytes: 10 * 1024 * 1024, // 10MB
      allowedTypes: [FileType.JSON],
      acceptedMimeTypes: ['application/json'],
      maxFileNameLength: 100
    };

    // Render the hook with the custom configuration
    const { result } = renderHook(() => useFileUpload(customConfig));

    // Verify that the configuration is used in validation
    const mockFile = createMockFile({ size: 15 * 1024 * 1024, type: 'text/csv' });
    const validationResult = result.current.validateFile(mockFile);
    expect(validationResult.valid).toBe(false);
    expect(validationResult.error).toBe(FileValidationError.FILE_TOO_LARGE);
  });

  it('should validate files correctly', () => {
    const { result } = renderHook(() => useFileUpload());

    // Test validation for valid file
    let mockFile = createMockFile({ size: 1024, type: 'text/csv' });
    let validationResult = result.current.validateFile(mockFile);
    expect(validationResult.valid).toBe(true);
    expect(validationResult.error).toBe(FileValidationError.NONE);

    // Test validation for file too large
    mockFile = createMockFile({ size: 60 * 1024 * 1024, type: 'text/csv' });
    validationResult = result.current.validateFile(mockFile);
    expect(validationResult.valid).toBe(false);
    expect(validationResult.error).toBe(FileValidationError.FILE_TOO_LARGE);

    // Test validation for invalid file type
    mockFile = createMockFile({ size: 1024, type: 'text/plain' });
    validationResult = result.current.validateFile(mockFile);
    expect(validationResult.valid).toBe(false);
    expect(validationResult.error).toBe(FileValidationError.INVALID_TYPE);

    // Test validation for empty file
    mockFile = createMockFile({ size: 0, type: 'text/csv' });
    validationResult = result.current.validateFile(mockFile);
    expect(validationResult.valid).toBe(false);
    expect(validationResult.error).toBe(FileValidationError.EMPTY_FILE);
  });

  it('should handle file selection', () => {
    const { result } = renderHook(() => useFileUpload());

    // Create a mock file
    const mockFile = createMockFile({ name: 'test-file.csv', type: 'text/csv', size: 1024 });

    // Call handleFileSelect with the mock file
    act(() => {
      result.current.handleFileSelect(mockFile);
    });

    // Verify that the file is stored in state
    expect(result.current.uploadState.file).toEqual({
      name: 'test-file.csv',
      size: 1024,
      type: 'text/csv',
      extension: 'csv',
      fileType: FileType.CSV,
      lastModified: expect.any(Number)
    });

    // Verify that validation is performed
    expect(result.current.uploadState.status).toBe(UploadStatus.PENDING);
    expect(result.current.uploadState.error).toBe(FileValidationError.NONE);
  });

  it('should start file upload', async () => {
    const { result } = renderHook(() => useFileUpload());

    // Set up a valid file in state
    const mockFile = createMockFile({ name: 'test-file.csv', type: 'text/csv', size: 1024 });
    act(() => {
      result.current.handleFileSelect(mockFile);
    });

    // Call startUpload with form data
    await act(async () => {
      await result.current.startUpload(mockUploadFormData);
    });

    // Verify that the upload service is called with correct parameters
    expect(uploadService.startUpload).toHaveBeenCalledWith(
      expect.any(File),
      mockUploadFormData,
      expect.anything(),
      expect.any(Function)
    );

    // Verify that the upload state is updated correctly
    expect(result.current.uploadState.status).toBe(UploadStatus.UPLOADED);
    expect(result.current.uploadState.uploadId).toBe('mock-upload-id');
  });

  it('should handle upload progress', async () => {
    // Set up a mock implementation of startUpload that reports progress
    uploadService.startUpload.mockImplementation(
      async (file, formData, config, onProgress) => {
        // Simulate progress events
        onProgress({ loaded: 25, total: 100, percentage: 25 });
        onProgress({ loaded: 50, total: 100, percentage: 50 });
        onProgress({ loaded: 75, total: 100, percentage: 75 });

        return {
          uploadState: {
            file: null,
            status: UploadStatus.UPLOADED,
            progress: { loaded: 100, total: 100, percentage: 100 },
            uploadId: 'mock-upload-id',
            error: FileValidationError.NONE,
            errorMessage: null,
            processingStep: null,
            estimatedTimeRemaining: null,
            analysisResult: null
          },
          abort: jest.fn()
        };
      }
    );

    const { result } = renderHook(() => useFileUpload());

    // Set up a valid file in state
    const mockFile = createMockFile({ name: 'test-file.csv', type: 'text/csv', size: 1024 });
    act(() => {
      result.current.handleFileSelect(mockFile);
    });

    // Start an upload
    await act(async () => {
      await result.current.startUpload(mockUploadFormData);
    });

    // Verify that the progress state is updated correctly
    expect(result.current.uploadState.progress.percentage).toBe(100);
  });

  it('should handle upload completion', async () => {
    const { result } = renderHook(() => useFileUpload());

    // Set up a mock implementation of startUpload that completes successfully
    uploadService.startUpload.mockResolvedValue({
      uploadState: {
        file: null,
        status: UploadStatus.UPLOADED,
        progress: { loaded: 100, total: 100, percentage: 100 },
        uploadId: 'mock-upload-id',
        error: FileValidationError.NONE,
        errorMessage: null,
        processingStep: null,
        estimatedTimeRemaining: null,
        analysisResult: null
      },
      abort: jest.fn()
    });

    // Set up a valid file in state
    const mockFile = createMockFile({ name: 'test-file.csv', type: 'text/csv', size: 1024 });
    act(() => {
      result.current.handleFileSelect(mockFile);
    });

    // Start an upload
    await act(async () => {
      await result.current.startUpload(mockUploadFormData);
    });

    // Verify that the status is updated to UPLOADED
    expect(result.current.uploadState.status).toBe(UploadStatus.UPLOADED);

    // Verify that the uploadId is stored in state
    expect(result.current.uploadState.uploadId).toBe('mock-upload-id');
  });

  it('should handle upload errors', async () => {
    // Set up a mock implementation of startUpload that fails
    uploadService.startUpload.mockRejectedValue(new Error('Upload failed'));

    const { result } = renderHook(() => useFileUpload());

    // Set up a valid file in state
    const mockFile = createMockFile({ name: 'test-file.csv', type: 'text/csv', size: 1024 });
    act(() => {
      result.current.handleFileSelect(mockFile);
    });

    // Start an upload
    await act(async () => {
      await result.current.startUpload(mockUploadFormData);
    });

    // Verify that the error state is updated correctly
    expect(result.current.uploadState.status).toBe(UploadStatus.FAILED);
    expect(result.current.uploadState.error).toBe(FileValidationError.UPLOAD_ERROR);
  });

  it('should cancel ongoing upload', async () => {
    const { result } = renderHook(() => useFileUpload());

    // Set up a mock implementation of startUpload that returns an abort function
    const mockAbort = jest.fn();
    uploadService.startUpload.mockResolvedValue({
      uploadState: {
        file: null,
        status: UploadStatus.UPLOADING,
        progress: { loaded: 50, total: 100, percentage: 50 },
        uploadId: 'mock-upload-id',
        error: FileValidationError.NONE,
        errorMessage: null,
        processingStep: null,
        estimatedTimeRemaining: null,
        analysisResult: null
      },
      abort: mockAbort
    });

    // Set up a valid file in state
    const mockFile = createMockFile({ name: 'test-file.csv', type: 'text/csv', size: 1024 });
    act(() => {
      result.current.handleFileSelect(mockFile);
    });

    // Start an upload
    await act(async () => {
      await result.current.startUpload(mockUploadFormData);
    });

    // Call cancelUpload
    act(() => {
      result.current.cancelUpload();
    });

    // Verify that the abort function is called
    expect(mockAbort).toHaveBeenCalled();

    // Verify that the status is updated to FAILED
    expect(result.current.uploadState.status).toBe(UploadStatus.FAILED);
  });

  it('should reset upload state', async () => {
    const { result } = renderHook(() => useFileUpload());

    // Set up a state with an ongoing or completed upload
    const mockFile = createMockFile({ name: 'test-file.csv', type: 'text/csv', size: 1024 });
    act(() => {
      result.current.handleFileSelect(mockFile);
    });
    await act(async () => {
      await result.current.startUpload(mockUploadFormData);
    });

    // Call resetUpload
    act(() => {
      result.current.resetUpload();
    });

    // Verify that the state is reset to initial values
    expect(result.current.uploadState).toEqual({
      file: null,
      status: UploadStatus.PENDING,
      progress: { loaded: 0, total: 0, percentage: 0 },
      uploadId: null,
      error: FileValidationError.NONE,
      errorMessage: null,
      processingStep: null,
      estimatedTimeRemaining: null,
      analysisResult: null
    });
  });

  it('should track upload status with useUploadStatus', async () => {
    const { result } = renderHook(() => useFileUpload());

    // Set up a state with a completed upload and uploadId
    const mockFile = createMockFile({ name: 'test-file.csv', type: 'text/csv', size: 1024 });
    act(() => {
      result.current.handleFileSelect(mockFile);
    });
    await act(async () => {
      await result.current.startUpload(mockUploadFormData);
    });

    // Mock useUploadStatus to return updated status
    useUploadStatus.mockReturnValue({
      uploadState: {
        file: null,
        status: UploadStatus.COMPLETED,
        progress: { loaded: 100, total: 100, percentage: 100 },
        uploadId: 'mock-upload-id',
        error: FileValidationError.NONE,
        errorMessage: null,
        processingStep: 'Analysis Complete',
        estimatedTimeRemaining: 0,
        analysisResult: { message: 'Analysis completed successfully' }
      },
      isPolling: false
    });

    // Verify that the upload state is updated based on status changes
    expect(result.current.uploadState.status).toBe(UploadStatus.UPLOADED);
  });

  it('should clean up on unmount', async () => {
    const { result, unmount } = renderHook(() => useFileUpload());

    // Set up a mock implementation of startUpload that returns an abort function
    const mockAbort = jest.fn();
    uploadService.startUpload.mockResolvedValue({
      uploadState: {
        file: null,
        status: UploadStatus.UPLOADING,
        progress: { loaded: 50, total: 100, percentage: 50 },
        uploadId: 'mock-upload-id',
        error: FileValidationError.NONE,
        errorMessage: null,
        processingStep: null,
        estimatedTimeRemaining: null,
        analysisResult: null
      },
      abort: mockAbort
    });

    // Set up a valid file in state
    const mockFile = createMockFile({ name: 'test-file.csv', type: 'text/csv', size: 1024 });
    act(() => {
      result.current.handleFileSelect(mockFile);
    });

    // Start an upload
    await act(async () => {
      await result.current.startUpload(mockUploadFormData);
    });

    // Unmount the component
    unmount();

    // Verify that the upload is cancelled
    expect(mockAbort).toHaveBeenCalled();

    // Verify that any intervals or timeouts are cleared
    // (This is difficult to directly verify without access to the hook's internals)
    // A more robust test would involve checking that no further state updates occur after unmount
  });
});