import React from 'react'; // version ^18.2.0
import {
  render,
  screen,
  waitFor,
  fireEvent,
} from '@testing-library/react'; // version ^14.0.0
import {
  vi,
  describe,
  it,
  expect,
  beforeEach,
  afterEach,
} from 'vitest'; // version ^0.32.0
import userEvent from '@testing-library/user-event'; // version ^14.4.3

import FileUploadForm from '../../../src/components/forms/FileUploadForm';
import { mockUploadFormData } from '../../mocks/data';
import { FileValidationError, UploadStatus } from '../../../src/types/upload';
import { useFileUpload } from '../../../src/hooks/useFileUpload';

/**
 * Creates a mock File object for testing file uploads
 * @param name - The name of the file
 * @param size - The size of the file in bytes
 * @param type - The MIME type of the file
 * @returns A mock File object with the specified properties
 */
const createMockFile = (name: string, size: number, type: string): File => {
  // LD1: Create a new Blob with empty array and specified MIME type
  const blob = new Blob([''], { type });
  // LD1: Create a new File object with the Blob, name, and additional properties
  const file = new File([blob], name, { type, lastModified: Date.now() });
  // LD1: Return the mock File object
  return file;
};

/**
 * Creates a mock implementation of the useFileUpload hook
 * @param mockState - An object containing the mock state values for the hook
 * @returns Mock implementation of useFileUpload hook return value
 */
const mockUseFileUpload = (mockState: any) => {
  // LD1: Create mock functions for all hook methods
  const mockValidateFile = vi.fn().mockReturnValue({ valid: true, error: FileValidationError.NONE, errorMessage: null });
  const mockHandleFileSelect = vi.fn();
  const mockStartUpload = vi.fn();
  const mockCancelUpload = vi.fn();
  const mockResetUpload = vi.fn();

  // LD1: Return an object with uploadState and mock functions
  return {
    uploadState: {
      file: null,
      status: UploadStatus.PENDING,
      progress: { loaded: 0, total: 0, percentage: 0 },
      uploadId: null,
      error: FileValidationError.NONE,
      errorMessage: null,
      processingStep: null,
      estimatedTimeRemaining: null,
      analysisResult: null,
      ...mockState,
    },
    validateFile: mockValidateFile,
    handleFileSelect: mockHandleFileSelect,
    startUpload: mockStartUpload,
    cancelUpload: mockCancelUpload,
    resetUpload: mockResetUpload,
  };
};

/**
 * Helper function to render the FileUploadForm component with props
 * @param props - The props to pass to the FileUploadForm component
 * @returns Rendered component and utilities
 */
const renderFileUploadForm = (props = {}) => {
  // LD1: Render the FileUploadForm component with provided props
  const renderResult = render(<FileUploadForm onSuccess={vi.fn()} {...props} />);
  // LD1: Return the rendered component and utilities
  return renderResult;
};

// Mock the useFileUpload and useForm hooks
vi.mock('../../../src/hooks/useFileUpload');
vi.mock('../../../src/hooks/useForm');

describe('FileUploadForm', () => {
  beforeEach(() => {
    // LD1: Reset all mock implementations before each test to ensure clean state
    vi.clearAllMocks();

    // LD1: Mock the useFileUpload and useForm hooks to control component behavior
    (useFileUpload as any).mockImplementation(mockUseFileUpload);
  });

  afterEach(() => {
    // LD1: Restore original implementations after each test
    vi.restoreAllMocks();
  });

  it('renders the form correctly', () => {
    // LD1: Render the FileUploadForm component
    renderFileUploadForm();

    // LD1: Check that all form fields are present (name, email, company, phone, service interest)
    expect(screen.getByLabelText(/Name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Company/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Phone/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Service Interest/i)).toBeInTheDocument();

    // LD1: Check that the file upload dropzone is present
    expect(screen.getByText(/Drag and drop your file here/i)).toBeInTheDocument();

    // LD1: Check that the submit button is present and disabled initially
    const submitButton = screen.getByRole('button', { name: /Submit Sample/i });
    expect(submitButton).toBeInTheDocument();
    expect(submitButton).toBeDisabled();
  });

  it('validates required fields', async () => {
    // LD1: Render the FileUploadForm component
    renderFileUploadForm();

    // LD1: Submit the form without filling required fields
    const submitButton = screen.getByRole('button', { name: /Submit Sample/i });
    userEvent.click(submitButton);

    // LD1: Check that validation errors are displayed for required fields
    await waitFor(() => {
      expect(screen.getByText(/This field is required/i)).toBeVisible();
    });
  });

  it('validates email format', async () => {
    // LD1: Render the FileUploadForm component
    renderFileUploadForm();

    // LD1: Enter an invalid email format
    const emailInput = screen.getByLabelText(/Email/i);
    fireEvent.change(emailInput, { target: { value: 'invalid-email' } });

    // LD1: Submit the form
    const submitButton = screen.getByRole('button', { name: /Submit Sample/i });
    userEvent.click(submitButton);

    // LD1: Check that email validation error is displayed
    await waitFor(() => {
      expect(screen.getByText(/Please enter a valid email address/i)).toBeVisible();
    });
  });

  it('handles file selection', () => {
    // LD1: Render the FileUploadForm component
    renderFileUploadForm();

    // LD1: Mock the useFileUpload hook to track file selection
    const mockHandleFileSelect = vi.fn();
    (useFileUpload as any).mockImplementation(() => ({
      ...mockUseFileUpload({}),
      handleFileSelect: mockHandleFileSelect,
    }));

    // LD1: Upload a mock file using the dropzone
    const file = createMockFile('test-file.csv', 1024, 'text/csv');
    const dropzone = screen.getByText(/Drag and drop your file here/i);
    fireEvent.drop(dropzone, { dataTransfer: { files: [file] } });

    // LD1: Verify that handleFileSelect was called with the file
    expect(mockHandleFileSelect).toHaveBeenCalledWith(file);
  });

  it('displays file validation errors', () => {
    // LD1: Render the FileUploadForm component
    renderFileUploadForm();

    // LD1: Mock the useFileUpload hook to return a file validation error
    (useFileUpload as any).mockImplementation(() =>
      mockUseFileUpload({
        error: FileValidationError.FILE_TOO_LARGE,
        errorMessage: 'File size exceeds the limit.',
      })
    );

    // LD1: Check that the appropriate error message is displayed
    expect(screen.getByText(/File size exceeds the limit./i)).toBeVisible();
  });

  it('submits the form with valid data', async () => {
    // LD1: Render the FileUploadForm component
    renderFileUploadForm();

    // LD1: Mock the useFileUpload hook to simulate upload in progress
    const mockStartUpload = vi.fn();
    (useFileUpload as any).mockImplementation(() => ({
      ...mockUseFileUpload({}),
      startUpload: mockStartUpload,
    }));

    // LD1: Fill all required fields with valid data
    fireEvent.change(screen.getByLabelText(/Name/i), { target: { value: mockUploadFormData.name } });
    fireEvent.change(screen.getByLabelText(/Email/i), { target: { value: mockUploadFormData.email } });
    fireEvent.change(screen.getByLabelText(/Company/i), { target: { value: mockUploadFormData.company } });
    fireEvent.change(screen.getByLabelText(/Phone/i), { target: { value: mockUploadFormData.phone } });
    fireEvent.change(screen.getByLabelText(/Service Interest/i), { target: { value: mockUploadFormData.serviceInterest } });

    // LD1: Upload a valid mock file
    const file = createMockFile('test-file.csv', 1024, 'text/csv');
    const dropzone = screen.getByText(/Drag and drop your file here/i);
    fireEvent.drop(dropzone, { dataTransfer: { files: [file] } });

    // LD1: Submit the form
    const submitButton = screen.getByRole('button', { name: /Submit Sample/i });
    userEvent.click(submitButton);

    // LD1: Verify that the form submission handler was called with correct data
    await waitFor(() => {
      expect(mockStartUpload).toHaveBeenCalled();
    });
  });

  it('shows upload progress', () => {
    // LD1: Render the FileUploadForm component
    renderFileUploadForm();

    // LD1: Mock the useFileUpload hook to simulate upload in progress
    (useFileUpload as any).mockImplementation(() =>
      mockUseFileUpload({ status: UploadStatus.UPLOADING, progress: { loaded: 50, total: 100, percentage: 50 } })
    );

    // LD1: Check that the progress bar is displayed with correct percentage
    expect(screen.getByText(/50%/i)).toBeVisible();
  });

  it('shows success message on completion', async () => {
    // LD1: Render the FileUploadForm component
    const onSuccessMock = vi.fn();
    renderFileUploadForm({ onSuccess: onSuccessMock });

    // LD1: Mock the useFileUpload hook to simulate completed upload
    (useFileUpload as any).mockImplementation(() =>
      mockUseFileUpload({ status: UploadStatus.COMPLETED, uploadId: 'test-upload-id' })
    );

    // LD1: Check that success message is displayed
    await waitFor(() => {
      expect(screen.getByText(/Your data has been uploaded successfully!/i)).toBeVisible();
    });

    // LD1: Verify that onSuccess callback was called
    expect(onSuccessMock).toHaveBeenCalledWith('test-upload-id');
  });

  it('handles upload cancellation', () => {
    // LD1: Render the FileUploadForm component
    renderFileUploadForm();

    // LD1: Mock the useFileUpload hook to simulate upload in progress
    const mockCancelUpload = vi.fn();
    (useFileUpload as any).mockImplementation(() => ({
      ...mockUseFileUpload({ status: UploadStatus.UPLOADING }),
      cancelUpload: mockCancelUpload,
    }));

    // LD1: Click the cancel button
    const resetButton = screen.getByRole('button', { name: /Reset/i });
    userEvent.click(resetButton);

    // LD1: Verify that cancelUpload was called
    expect(mockCancelUpload).toHaveBeenCalled();
  });

  it('handles form-level errors', () => {
    // LD1: Render the FileUploadForm component
    renderFileUploadForm();

    // LD1: Mock the useFileUpload hook to simulate an upload error
    (useFileUpload as any).mockImplementation(() =>
      mockUseFileUpload({
        status: UploadStatus.FAILED,
        errorMessage: 'An error occurred during upload.',
      })
    );

    // LD1: Check that the form-level error message is displayed
    expect(screen.getByText(/An error occurred during upload./i)).toBeVisible();
  });
});