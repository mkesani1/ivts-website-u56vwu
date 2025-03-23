import React, { createContext, useContext, useState, useCallback, useMemo, ReactNode } from 'react'; // react@^18.2.0
import { useFileUpload, UseFileUploadReturn } from '../hooks/useFileUpload';
import { UploadState, UploadConfig, FileValidationError, DEFAULT_UPLOAD_CONFIG } from '../types/upload';
import { UploadFormData } from '../types/forms';

/**
 * Interface defining the shape of the upload context value
 */
interface UploadContextType {
  uploadState: UploadState;
  uploadConfig: UploadConfig;
  setUploadConfig: (config: UploadConfig | ((prevConfig: UploadConfig) => UploadConfig)) => void;
  validateFile: (file: File) => { valid: boolean; error: FileValidationError; errorMessage: string | null };
  handleFileSelect: (file: File) => void;
  startUpload: (formData: UploadFormData) => Promise<void>;
  cancelUpload: () => void;
  resetUpload: () => void;
}

/**
 * Interface defining the props for the UploadProvider component
 */
interface UploadProviderProps {
  children: ReactNode;
  initialConfig?: UploadConfig;
}

// Create the context with null as initial value
export const UploadContext = createContext<UploadContextType | null>(null);

/**
 * Custom hook that provides access to the UploadContext
 * @returns The upload context value
 * @throws Error if used outside an UploadProvider
 */
export const useUploadContext = (): UploadContextType => {
  const context = useContext(UploadContext);
  if (!context) {
    throw new Error('useUploadContext must be used within an UploadProvider');
  }
  return context;
};

/**
 * Provider component that makes upload functionality available to child components
 * throughout the IndiVillage website.
 * 
 * This provider centralizes state management for file uploads, providing a consistent interface
 * for file selection, validation, upload processing, and status tracking.
 */
export const UploadProvider: React.FC<UploadProviderProps> = ({ 
  children,
  initialConfig
}) => {
  // Set upload configuration with default fallback
  const [uploadConfig, setUploadConfig] = useState<UploadConfig>(
    initialConfig || DEFAULT_UPLOAD_CONFIG
  );
  
  // Use the custom hook for file upload functionality
  const {
    uploadState,
    validateFile,
    handleFileSelect,
    startUpload: startFileUpload,
    cancelUpload,
    resetUpload
  } = useFileUpload(uploadConfig);
  
  // Wrapper function that combines form data with the upload
  const startUpload = useCallback(async (formData: UploadFormData): Promise<void> => {
    return startFileUpload(formData);
  }, [startFileUpload]);
  
  // Create memoized context value to prevent unnecessary re-renders
  const contextValue = useMemo(() => ({
    uploadState,
    uploadConfig,
    setUploadConfig,
    validateFile,
    handleFileSelect,
    startUpload,
    cancelUpload,
    resetUpload
  }), [
    uploadState,
    uploadConfig,
    setUploadConfig,
    validateFile,
    handleFileSelect,
    startUpload,
    cancelUpload,
    resetUpload
  ]);
  
  return (
    <UploadContext.Provider value={contextValue}>
      {children}
    </UploadContext.Provider>
  );
};