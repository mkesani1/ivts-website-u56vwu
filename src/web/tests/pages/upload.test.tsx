import React from 'react'; // version ^18.2.0
import { render, screen, waitFor, within, fireEvent } from '@testing-library/react'; // version ^14.0.0
import userEvent from '@testing-library/user-event'; // version ^14.4.3
import { describe, it, expect, beforeEach, jest } from '@jest/globals'; // version ^29.5.0

import UploadSamplePage from '../../src/app/upload-sample/page';
import UploadProcessingPage from '../../src/app/upload-sample/processing/page';
import UploadSuccessPage from '../../src/app/upload-sample/success/page';
import { renderWithProviders, createMockFile, simulateFileUpload } from '../../src/utils/testing';
import { mockUploadFormData, mockUploadResponses } from '../mocks/data';
import { ROUTES } from '../../src/constants/routes';
import { UploadStatus } from '../../src/types/api';
import { FileValidationError } from '../../src/types/upload';

// Mock Next.js navigation hooks and components
jest.mock('next/navigation', () => ({
  useRouter: jest.fn().mockReturnValue({
    push: jest.fn(),
    replace: jest.fn(),
    prefetch: jest.fn(),
  }),
  useSearchParams: jest.fn().mockReturnValue({
    get: jest.fn(),
  }),
}));

describe('UploadSamplePage', () => {
  beforeEach(() => {
    // Reset mocks before each test
    jest.clearAllMocks();
  });

  it('should render the upload form with all required fields', async () => {
    // Render the UploadSamplePage component with test providers
    renderWithProviders(<UploadSamplePage />);

    // Verify the page title and description are present
    expect(screen.getByText('Upload Sample Data')).toBeInTheDocument();
    expect(screen.getByText('Let us analyze your data and provide a customized solution proposal for your specific needs.')).toBeInTheDocument();

    // Verify the form contains name, email, company, and phone fields
    expect(screen.getByLabelText('Name')).toBeInTheDocument();
    expect(screen.getByLabelText('Email')).toBeInTheDocument();
    expect(screen.getByLabelText('Company')).toBeInTheDocument();
    expect(screen.getByLabelText('Phone')).toBeInTheDocument();

    // Verify the service interest selection is present
    expect(screen.getByLabelText('Service Interest')).toBeInTheDocument();

    // Verify the file upload dropzone is present
    expect(screen.getByText('Drag and drop your file here')).toBeInTheDocument();

    // Verify the optional description field is present
    expect(screen.getByLabelText('Project Description (Optional)')).toBeInTheDocument();

    // Verify the submit and cancel buttons are present
    expect(screen.getByRole('button', { name: 'Submit Sample' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Reset' })).toBeInTheDocument();
  });

  it('should validate form fields and show error messages', async () => {
    // Render the UploadSamplePage component with test providers
    renderWithProviders(<UploadSamplePage />);

    // Click the submit button without filling required fields
    const submitButton = screen.getByRole('button', { name: 'Submit Sample' });
    await userEvent.click(submitButton);

    // Verify error messages are displayed for required fields
    expect(screen.getByText('This field is required.')).toBeInTheDocument();

    // Enter invalid email format
    const emailInput = screen.getByLabelText('Email');
    await userEvent.type(emailInput, 'invalid-email');
    await userEvent.click(submitButton);

    // Verify email format error message is displayed
    expect(screen.getByText('Please enter a valid email address.')).toBeInTheDocument();

    // Enter valid data in all required fields
    await userEvent.type(screen.getByLabelText('Name'), 'John Doe');
    await userEvent.type(emailInput, 'john.doe@example.com');
    await userEvent.type(screen.getByLabelText('Company'), 'Test Company');
    await userEvent.type(screen.getByLabelText('Phone'), '+1 (555) 123-4567');
    await userEvent.selectOptions(screen.getByLabelText('Service Interest'), 'data_preparation');

    // Verify error messages are no longer displayed
    expect(screen.queryByText('This field is required.')).not.toBeInTheDocument();
    expect(screen.queryByText('Please enter a valid email address.')).not.toBeInTheDocument();
  });

  it('should handle file selection and validate file types', async () => {
    // Render the UploadSamplePage component with test providers
    renderWithProviders(<UploadSamplePage />);

    // Create a mock valid file using createMockFile
    const validFile = createMockFile({ name: 'test-file.csv', type: 'text/csv' });

    // Simulate file upload with the mock file
    const fileInput = screen.getByLabelText('Drag and drop your file here') as HTMLElement;
    simulateFileUpload(fileInput, validFile);

    // Verify the file name is displayed in the UI
    expect(screen.getByText('test-file.csv')).toBeInTheDocument();

    // Create a mock invalid file type
    const invalidFile = createMockFile({ name: 'test-file.exe', type: 'application/exe' });

    // Simulate file upload with the invalid file
    simulateFileUpload(fileInput, invalidFile);

    // Verify error message for invalid file type is displayed
    expect(screen.getByText('The selected file type is not supported.')).toBeInTheDocument();

    // Create a mock file that exceeds size limit
    const oversizedFile = createMockFile({ name: 'oversized-file.csv', type: 'text/csv', size: 60 * 1024 * 1024 });

    // Simulate file upload with the oversized file
    simulateFileUpload(fileInput, oversizedFile);

    // Verify error message for file size limit is displayed
    expect(screen.getByText('The selected file is too large.')).toBeInTheDocument();
  });

  it('should submit the form and redirect to processing page on success', async () => {
    // Mock the useRouter hook
    const pushMock = jest.fn();
    (require('next/navigation').useRouter as jest.Mock).mockReturnValue({
      push: pushMock,
      replace: jest.fn(),
      prefetch: jest.fn(),
    });

    // Render the UploadSamplePage component with test providers
    renderWithProviders(<UploadSamplePage />);

    // Fill in all required form fields with valid data
    await userEvent.type(screen.getByLabelText('Name'), mockUploadFormData.name);
    await userEvent.type(screen.getByLabelText('Email'), mockUploadFormData.email);
    await userEvent.type(screen.getByLabelText('Company'), mockUploadFormData.company);
    await userEvent.type(screen.getByLabelText('Phone'), mockUploadFormData.phone);
    await userEvent.selectOptions(screen.getByLabelText('Service Interest'), mockUploadFormData.serviceInterest);

    // Create a mock valid file and simulate upload
    const validFile = createMockFile({ name: 'test-file.csv', type: 'text/csv' });
    const fileInput = screen.getByLabelText('Drag and drop your file here') as HTMLElement;
    simulateFileUpload(fileInput, validFile);

    // Click the submit button
    const submitButton = screen.getByRole('button', { name: 'Submit Sample' });
    await userEvent.click(submitButton);

    // Verify form submission is processed
    // Verify redirection to processing page with correct uploadId parameter
    await waitFor(() => {
      expect(pushMock).toHaveBeenCalledTimes(1);
      expect(pushMock).toHaveBeenCalledWith(expect.stringContaining(ROUTES.UPLOAD_SAMPLE.PROCESSING));
    });
  });
});

describe('UploadProcessingPage', () => {
  beforeEach(() => {
    // Reset mocks before each test
    jest.clearAllMocks();
  });

  it('should render the processing page with progress indicator', async () => {
    // Mock searchParams to include uploadId
    (require('next/navigation').useSearchParams as jest.Mock).mockReturnValue({
      get: jest.fn().mockReturnValue('upload-123'),
    });

    // Mock useUploadStatus to return PROCESSING status with 50% progress
    const mockUploadStatus = {
      uploadState: {
        file: { name: 'test-file.csv', size: 1024, type: 'text/csv', extension: 'csv', fileType: 'csv', lastModified: Date.now() },
        status: UploadStatus.PROCESSING,
        progress: { loaded: 512, total: 1024, percentage: 50 },
        uploadId: 'upload-123',
        error: FileValidationError.NONE,
        errorMessage: null,
        processingStep: 'Analyzing data structure',
        estimatedTimeRemaining: 60,
        analysisResult: null
      },
      isPolling: true
    };
    jest.mock('../../src/hooks/useUploadStatus', () => ({
      useUploadStatus: jest.fn().mockReturnValue(mockUploadStatus),
    }));

    // Render the UploadProcessingPage component with test providers
    renderWithProviders(<UploadProcessingPage />);

    // Verify the processing title and description are present
    expect(screen.getByText('Processing Data Upload')).toBeInTheDocument();
    expect(screen.getByText('Your file "test-file.csv" is being processed.')).toBeInTheDocument();

    // Verify the progress bar is displayed with 50% completion
    const progressBar = screen.getByRole('progressbar');
    expect(progressBar).toBeInTheDocument();
    expect(progressBar).toHaveAttribute('aria-valuenow', '50');

    // Verify the current processing step is displayed
    expect(screen.getByText('Analyzing data structure')).toBeInTheDocument();

    // Verify the estimated time remaining is displayed
    expect(screen.getByText('Estimated time remaining: 1 minute')).toBeInTheDocument();

    // Verify the 'What Happens Next' section is present
    expect(screen.getByText('What Happens Next?')).toBeInTheDocument();
  });

  it('should redirect to success page when processing is complete', async () => {
    // Mock the useRouter hook
    const pushMock = jest.fn();
    (require('next/navigation').useRouter as jest.Mock).mockReturnValue({
      push: pushMock,
      replace: jest.fn(),
      prefetch: jest.fn(),
    });

    // Mock searchParams to include uploadId
    (require('next/navigation').useSearchParams as jest.Mock).mockReturnValue({
      get: jest.fn().mockReturnValue('upload-123'),
    });

    // Mock useUploadStatus to return COMPLETED status
    const mockUploadStatus = {
      uploadState: {
        file: { name: 'test-file.csv', size: 1024, type: 'text/csv', extension: 'csv', fileType: 'csv', lastModified: Date.now() },
        status: UploadStatus.COMPLETED,
        progress: { loaded: 1024, total: 1024, percentage: 100 },
        uploadId: 'upload-123',
        error: FileValidationError.NONE,
        errorMessage: null,
        processingStep: null,
        estimatedTimeRemaining: null,
        analysisResult: null
      },
      isPolling: false
    };
    jest.mock('../../src/hooks/useUploadStatus', () => ({
      useUploadStatus: jest.fn().mockReturnValue(mockUploadStatus),
    }));

    // Render the UploadProcessingPage component with test providers
    renderWithProviders(<UploadProcessingPage />);

    // Verify redirection to success page with correct fileId parameter
    await waitFor(() => {
      expect(pushMock).toHaveBeenCalledTimes(1);
      expect(pushMock).toHaveBeenCalledWith(expect.stringContaining(`${ROUTES.UPLOAD_SAMPLE.SUCCESS}?uploadId=upload-123`));
    });
  });

  it('should handle error state and show error message', async () => {
    // Mock the useRouter hook
    const pushMock = jest.fn();
    (require('next/navigation').useRouter as jest.Mock).mockReturnValue({
      push: pushMock,
      replace: jest.fn(),
      prefetch: jest.fn(),
    });

    // Mock searchParams to include uploadId
    (require('next/navigation').useSearchParams as jest.Mock).mockReturnValue({
      get: jest.fn().mockReturnValue('upload-123'),
    });

    // Mock useUploadStatus to return FAILED status
    const mockUploadStatus = {
      uploadState: {
        file: { name: 'test-file.csv', size: 1024, type: 'text/csv', extension: 'csv', fileType: 'csv', lastModified: Date.now() },
        status: UploadStatus.FAILED,
        progress: { loaded: 0, total: 0, percentage: 0 },
        uploadId: 'upload-123',
        error: FileValidationError.UPLOAD_ERROR,
        errorMessage: 'An unexpected error occurred.',
        processingStep: null,
        estimatedTimeRemaining: null,
        analysisResult: null
      },
      isPolling: false
    };
    jest.mock('../../src/hooks/useUploadStatus', () => ({
      useUploadStatus: jest.fn().mockReturnValue(mockUploadStatus),
    }));

    // Render the UploadProcessingPage component with test providers
    renderWithProviders(<UploadProcessingPage />);

    // Verify error message is displayed
    expect(screen.getByText('Upload Failed')).toBeInTheDocument();
    expect(screen.getByText('An unexpected error occurred.')).toBeInTheDocument();

    // Verify retry button is present
    const retryButton = screen.getByRole('button', { name: 'Retry Upload' });
    expect(retryButton).toBeInTheDocument();

    // Click retry button
    await userEvent.click(retryButton);

    // Verify navigation back to upload page
    expect(pushMock).toHaveBeenCalledTimes(1);
    expect(pushMock).toHaveBeenCalledWith(ROUTES.UPLOAD_SAMPLE.INDEX);
  });

  it('should redirect to upload page if uploadId is missing', async () => {
    // Mock the useRouter hook
    const pushMock = jest.fn();
    (require('next/navigation').useRouter as jest.Mock).mockReturnValue({
      push: pushMock,
      replace: jest.fn(),
      prefetch: jest.fn(),
    });

    // Mock searchParams to return empty (no uploadId)
    (require('next/navigation').useSearchParams as jest.Mock).mockReturnValue({
      get: jest.fn().mockReturnValue(null),
    });

    // Render the UploadProcessingPage component with test providers
    renderWithProviders(<UploadProcessingPage />);

    // Verify redirection to upload page
    expect(pushMock).toHaveBeenCalledTimes(1);
    expect(pushMock).toHaveBeenCalledWith(ROUTES.UPLOAD_SAMPLE.INDEX);
  });
});

describe('UploadSuccessPage', () => {
  beforeEach(() => {
    // Reset mocks before each test
    jest.clearAllMocks();
  });

  it('should render the success page with confirmation message', async () => {
    // Mock searchParams to include fileId
    (require('next/navigation').useSearchParams as jest.Mock).mockReturnValue({
      get: jest.fn().mockReturnValue('file-123'),
    });

    // Render the UploadSuccessPage component with test providers
    renderWithProviders(<UploadSuccessPage />);

    // Verify the success title and confirmation message are present
    expect(screen.getByText('Upload Successful')).toBeInTheDocument();
    expect(screen.getByText('Your data has been successfully uploaded!')).toBeInTheDocument();

    // Verify the checkmark icon is displayed
    expect(screen.getByRole('img')).toHaveAttribute('aria-label', 'success');

    // Verify the 'What Happens Next' section is present
    expect(screen.getByText('What Happens Next?')).toBeInTheDocument();

    // Verify the email notification message is present
    expect(screen.getByText('You\'ll receive an email confirmation when processing is complete')).toBeInTheDocument();

    // Verify the CTA buttons for demo request and exploring services are present
    expect(screen.getByRole('button', { name: 'Request a Demo' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Explore Our Services' })).toBeInTheDocument();
  });

  it('should navigate to correct pages when CTA buttons are clicked', async () => {
    // Mock the useRouter hook
    const pushMock = jest.fn();
    (require('next/navigation').useRouter as jest.Mock).mockReturnValue({
      push: pushMock,
      replace: jest.fn(),
      prefetch: jest.fn(),
    });

    // Mock searchParams to include fileId
    (require('next/navigation').useSearchParams as jest.Mock).mockReturnValue({
      get: jest.fn().mockReturnValue('file-123'),
    });

    // Render the UploadSuccessPage component with test providers
    renderWithProviders(<UploadSuccessPage />);

    // Click the 'Request Demo' button
    const requestDemoButton = screen.getByRole('button', { name: 'Request a Demo' });
    await userEvent.click(requestDemoButton);

    // Verify navigation to demo request page
    expect(pushMock).toHaveBeenCalledWith(ROUTES.REQUEST_DEMO);

    // Click the 'Explore Our Services' button
    const exploreServicesButton = screen.getByRole('button', { name: 'Explore Our Services' });
    await userEvent.click(exploreServicesButton);

    // Verify navigation to services page
    expect(pushMock).toHaveBeenCalledWith(ROUTES.SERVICES.INDEX);
  });

  it('should handle missing fileId and show appropriate message', async () => {
    // Mock the useRouter hook
    const pushMock = jest.fn();
    (require('next/navigation').useRouter as jest.Mock).mockReturnValue({
      push: pushMock,
      replace: jest.fn(),
      prefetch: jest.fn(),
    });

    // Mock searchParams to return empty (no fileId)
    (require('next/navigation').useSearchParams as jest.Mock).mockReturnValue({
      get: jest.fn().mockReturnValue(null),
    });

    // Render the UploadSuccessPage component with test providers
    renderWithProviders(<UploadSuccessPage />);

    // Verify error message about missing file information is displayed
    expect(screen.getByText('There was an error processing your file.')).toBeInTheDocument();

    // Verify 'Try Again' button is present
    const tryAgainButton = screen.getByRole('button', { name: 'Try Again' });
    expect(tryAgainButton).toBeInTheDocument();

    // Click 'Try Again' button
    await userEvent.click(tryAgainButton);

    // Verify navigation back to upload page
    expect(pushMock).toHaveBeenCalledWith(ROUTES.UPLOAD_SAMPLE.INDEX);
  });
});