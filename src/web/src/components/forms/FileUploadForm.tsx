import React, { useCallback, useEffect, useState } from 'react'; // version ^18.2.0
import classNames from 'classnames'; // version ^2.3.2

import FormField from './FormField';
import Input from '../ui/Input';
import Select from '../ui/Select';
import Textarea from '../ui/Textarea';
import Button from '../ui/Button';
import FileDropzone from './FileDropzone';
import ProgressBar from './ProgressBar';
import FormSuccess from './FormSuccess';
import FormError from './FormError';
import Captcha from './Captcha';
import { useForm } from '../../hooks/useForm';
import { useFileUpload } from '../../hooks/useFileUpload';
import { UploadFormData } from '../../types/forms';
import { FileValidationError, UploadStatus, DEFAULT_UPLOAD_CONFIG } from '../../types/upload';
import { SERVICE_INTEREST_OPTIONS } from '../../constants/services';

/**
 * Interface defining the props for the FileUploadForm component
 */
export interface FileUploadFormProps {
  /**
   * Callback function called when file upload is successful
   * @param uploadId The ID of the successful upload
   */
  onSuccess: (uploadId: string) => void;
  /**
   * Additional CSS class names
   */
  className?: string;
}

/**
 * Returns a user-friendly error message based on the file validation error type
 * @param error - The FileValidationError enum value
 * @returns User-friendly error message
 */
const getErrorMessageForFileValidation = (error: FileValidationError): string => {
  switch (error) {
    case FileValidationError.FILE_TOO_LARGE:
      return 'The selected file is too large. Please upload a smaller file.';
    case FileValidationError.INVALID_TYPE:
      return 'The selected file type is not supported. Please upload a file in one of the supported formats.';
    case FileValidationError.EMPTY_FILE:
      return 'The selected file is empty. Please select a valid file.';
    case FileValidationError.UPLOAD_ERROR:
      return 'An error occurred during upload. Please try again.';
    case FileValidationError.NONE:
    default:
      return '';
  }
};

/**
 * A comprehensive form component for uploading sample data files with user information
 * @param props - Component props
 * @returns Rendered file upload form component
 */
const FileUploadForm: React.FC<FileUploadFormProps> = ({
  onSuccess,
  className,
  ...rest
}) => {
  // Destructure props including onSuccess, className, and other HTML attributes
  // Initialize useFileUpload hook with DEFAULT_UPLOAD_CONFIG
  const {
    uploadState,
    validateFile,
    handleFileSelect,
    startUpload,
    cancelUpload,
    resetUpload
  } = useFileUpload(DEFAULT_UPLOAD_CONFIG);

  // Initialize useForm hook with initial values and validation rules
  const {
    formState,
    handleChange,
    handleBlur,
    handleSubmit,
    validateForm: validateFormFields,
    resetForm: resetFormFields,
    setStatus: setFormStatus,
    setError: setFormError
  } = useForm({
    initialValues: {
      name: '',
      email: '',
      company: '',
      phone: '',
      serviceInterest: '',
      description: ''
    },
    validationRules: {
      name: { required: true, minLength: 2, maxLength: 100 },
      email: { required: true, email: true },
      company: { required: true, minLength: 2, maxLength: 100 },
      phone: { required: true, phone: true },
      serviceInterest: { required: true },
      description: { maxLength: 500 }
    }
  });

  // Create state for CAPTCHA token
  const [captchaToken, setCaptchaToken] = useState<string | null>(null);

  // Create state for form-level error message
  const [formErrorMessage, setFormErrorMessage] = useState<string | null>(null);

  // Create function to handle file selection
  const handleFileSelection = (file: File) => {
    handleFileSelect(file);
  };

  // Create function to handle CAPTCHA verification
  const handleCaptchaVerify = (token: string) => {
    setCaptchaToken(token);
  };

  // Create function to handle form submission
  const handleFormSubmit = handleSubmit(async () => {
    if (!captchaToken) {
      setFormErrorMessage('Please complete the CAPTCHA verification.');
      return;
    }

    const formData: UploadFormData = {
      ...formState.values,
      recaptchaToken: captchaToken
    };

    await startUpload(formData);
  });

  // Create function to handle upload cancellation
  const handleUploadCancel = () => {
    cancelUpload();
  };

  // Create function to handle form reset
  const handleFormReset = () => {
    resetFormFields();
    resetUpload();
    setFormErrorMessage(null);
  };

  // Use useEffect to reset form when upload is successful
  useEffect(() => {
    if (uploadState.status === UploadStatus.COMPLETED && uploadState.uploadId) {
      onSuccess(uploadState.uploadId);
    }
  }, [uploadState.status, uploadState.uploadId, onSuccess]);

  // Use useEffect to set form error when upload fails
  useEffect(() => {
    if (uploadState.status === UploadStatus.FAILED && uploadState.errorMessage) {
      setFormErrorMessage(uploadState.errorMessage);
    } else {
      setFormErrorMessage(null);
    }
  }, [uploadState.status, uploadState.errorMessage]);

  // Determine current form step based on upload state
  let currentStep: React.ReactNode = null;

  if (uploadState.status === UploadStatus.COMPLETED) {
    // Show success message when upload is complete
    currentStep = (
      <FormSuccess
        message="Your data has been uploaded successfully! We will analyze it and get back to you soon."
        actions={[
          { label: 'Upload Another Sample', onClick: handleFormReset, variant: 'secondary' }
        ]}
      />
    );
  } else if (uploadState.status === UploadStatus.UPLOADING || uploadState.status === UploadStatus.SCANNING || uploadState.status === UploadStatus.PROCESSING) {
    // Show progress bar when uploading
    currentStep = (
      <ProgressBar
        progress={uploadState.progress}
        label="Uploading your data..."
        processingStep={uploadState.processingStep}
        estimatedTimeRemaining={uploadState.estimatedTimeRemaining}
      />
    );
  } else {
    // Render form with appropriate step content
    currentStep = (
      <>
        <FormField
          name="name"
          label="Name"
          required
          error={formState.fields.name?.error}
        >
          <Input
            type="text"
            name="name"
            value={formState.values.name}
            onChange={handleChange}
            onBlur={handleBlur}
            placeholder="Your Name"
          />
        </FormField>

        <FormField
          name="email"
          label="Email"
          required
          error={formState.fields.email?.error}
        >
          <Input
            type="email"
            name="email"
            value={formState.values.email}
            onChange={handleChange}
            onBlur={handleBlur}
            placeholder="Your Email"
          />
        </FormField>

        <FormField
          name="company"
          label="Company"
          required
          error={formState.fields.company?.error}
        >
          <Input
            type="text"
            name="company"
            value={formState.values.company}
            onChange={handleChange}
            onBlur={handleBlur}
            placeholder="Your Company"
          />
        </FormField>

        <FormField
          name="phone"
          label="Phone"
          required
          error={formState.fields.phone?.error}
        >
          <Input
            type="tel"
            name="phone"
            value={formState.values.phone}
            onChange={handleChange}
            onBlur={handleBlur}
            placeholder="Your Phone"
          />
        </FormField>

        <FormField
          name="serviceInterest"
          label="Service Interest"
          required
          error={formState.fields.serviceInterest?.error}
        >
          <Select
            name="serviceInterest"
            value={formState.values.serviceInterest}
            options={SERVICE_INTEREST_OPTIONS}
            onChange={handleChange}
            onBlur={handleBlur}
            placeholder="Select Service Interest"
          />
        </FormField>

        <FormField
          name="description"
          label="Project Description (Optional)"
        >
          <Textarea
            name="description"
            value={formState.values.description}
            onChange={handleChange}
            onBlur={handleBlur}
            placeholder="Tell us about your project"
            rows={4}
          />
        </FormField>

        <FileDropzone
          onFileSelect={handleFileSelection}
          config={DEFAULT_UPLOAD_CONFIG}
          error={uploadState.error}
          errorMessage={getErrorMessageForFileValidation(uploadState.error)}
          selectedFile={uploadState.file}
        />

        <Captcha onVerify={handleCaptchaVerify} />

        <div className="flex justify-end space-x-4 mt-6">
          <Button
            type="button"
            variant="secondary"
            onClick={handleFormReset}
            disabled={formState.status === UploadStatus.UPLOADING}
          >
            Reset
          </Button>
          <Button
            type="submit"
            onClick={handleFormSubmit}
            disabled={formState.status === UploadStatus.UPLOADING || !uploadState.file || !formState.isValid}
            loading={formState.status === UploadStatus.UPLOADING}
          >
            Submit Sample
          </Button>
        </div>
      </>
    );
  }

  // Return the complete form component with all elements and proper styling
  return (
    <div className={classNames('file-upload-form', className)} {...rest}>
      {currentStep}
      {formErrorMessage && <FormError error={formErrorMessage} />}
    </div>
  );
};

export default FileUploadForm;