import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone'; // version ^14.2.0
import classNames from 'classnames'; // version ^2.3.2

import {
  FileInfo,
  UploadConfig,
  FileValidationError,
  formatFileSize,
  FILE_TYPE_INFO
} from '../../types/upload';
import Icon from '../ui/Icon';
import Button from '../ui/Button';
import Alert from '../ui/Alert';
import { ToastType } from '../../types/common';

/**
 * Props for the FileDropzone component
 */
export interface FileDropzoneProps {
  /**
   * Callback triggered when a user selects a file
   * @param file The selected file information or null if selection is cleared
   */
  onFileSelect: (file: FileInfo | null) => void;
  
  /**
   * Configuration for file uploads including size limits and allowed types
   */
  config: UploadConfig;
  
  /**
   * Current error state for file validation
   */
  error?: FileValidationError;
  
  /**
   * Custom error message to display
   */
  errorMessage?: string;
  
  /**
   * Currently selected file information
   */
  selectedFile?: FileInfo | null;
  
  /**
   * Additional CSS class names
   */
  className?: string;
  
  /**
   * Whether the dropzone is disabled
   */
  disabled?: boolean;
}

/**
 * A reusable component that provides a drag-and-drop interface for file uploads.
 * Users can either drag files into the dropzone or click to browse their file system.
 * Includes file validation, error handling, and visual feedback.
 */
const FileDropzone: React.FC<FileDropzoneProps> = ({
  onFileSelect,
  config,
  error,
  errorMessage,
  selectedFile,
  className,
  disabled = false
}) => {
  // State to track drag-over state for visual feedback
  const [isDragOver, setIsDragOver] = useState(false);

  // Function to handle file drop
  const handleDrop = useCallback(
    (acceptedFiles: File[]) => {
      // Take only the first file (since we're configuring for single file upload)
      const file = acceptedFiles[0];
      
      if (!file) {
        onFileSelect(null);
        return;
      }

      // Extract file extension
      const nameParts = file.name.split('.');
      const extension = nameParts.length > 1 ? nameParts.pop()?.toLowerCase() ?? '' : '';

      // Determine file type based on MIME type or extension
      const mimeType = file.type;
      let fileType = null;

      // Find matching file type from supported types
      Object.entries(FILE_TYPE_INFO).forEach(([key, info]) => {
        if (info.mimeTypes.includes(mimeType) || info.extensions.includes(extension)) {
          fileType = key;
        }
      });

      // Create FileInfo object
      const fileInfo: FileInfo = {
        name: file.name,
        size: file.size,
        type: file.type,
        extension,
        fileType,
        lastModified: file.lastModified
      };

      onFileSelect(fileInfo);
    },
    [onFileSelect]
  );

  // Build accept object for react-dropzone v14+
  const buildAcceptObject = () => {
    const accept: Record<string, string[]> = {};
    config.acceptedMimeTypes.forEach(mimeType => {
      accept[mimeType] = [];
    });
    return accept;
  };

  // Configure dropzone
  const {
    getRootProps,
    getInputProps,
    isDragActive
  } = useDropzone({
    onDrop: handleDrop,
    accept: buildAcceptObject(),
    maxSize: config.maxSizeBytes,
    multiple: false, // Allow only single file
    disabled,
    onDragEnter: () => setIsDragOver(true),
    onDragLeave: () => setIsDragOver(false)
  });

  // Generate CSS classes
  const dropzoneClasses = classNames(
    'file-dropzone',
    {
      'file-dropzone--active': isDragOver || isDragActive,
      'file-dropzone--error': !!error,
      'file-dropzone--disabled': disabled,
      'file-dropzone--has-file': !!selectedFile
    },
    className
  );

  // Format a list of accepted file types for display
  const getAcceptedFileTypesText = () => {
    const allowedTypes = config.allowedTypes.map(type => FILE_TYPE_INFO[type].label);
    return allowedTypes.join(', ');
  };

  return (
    <div className="file-upload-container">
      <div
        {...getRootProps({
          className: dropzoneClasses
        })}
      >
        <input {...getInputProps()} />
        
        <div className="file-dropzone__content">
          {!selectedFile ? (
            // Display upload prompt when no file is selected
            <>
              <Icon name="upload" size="large" className="file-dropzone__icon" />
              <p className="file-dropzone__text">
                Drag and drop your file here
                <br />
                or
              </p>
              <Button 
                variant="secondary" 
                size="medium"
                disabled={disabled}
              >
                Browse Files
              </Button>
            </>
          ) : (
            // Display file information when a file is selected
            <div className="file-dropzone__selected-file">
              <Icon 
                name={selectedFile.fileType ? FILE_TYPE_INFO[selectedFile.fileType].icon : 'upload'} 
                size="large" 
                className="file-dropzone__file-icon" 
              />
              <div className="file-dropzone__file-info">
                <p className="file-dropzone__file-name">{selectedFile.name}</p>
                <p className="file-dropzone__file-details">
                  {formatFileSize(selectedFile.size)} • {selectedFile.type}
                </p>
              </div>
            </div>
          )}
        </div>

        <p className="file-dropzone__formats">
          Supported formats: {getAcceptedFileTypesText()}
          <br />
          Maximum file size: {formatFileSize(config.maxSizeBytes)}
        </p>
      </div>

      {error && (
        <Alert 
          variant={ToastType.ERROR}
          message={errorMessage || `File upload error: ${error}`}
          className="mt-2"
        />
      )}
    </div>
  );
};

export default FileDropzone;