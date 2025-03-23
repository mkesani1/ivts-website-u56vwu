/**
 * TypeScript types, interfaces, enums, and constants related to file upload functionality
 * for the IndiVillage website. This includes file validation, upload state management,
 * file type definitions, and configuration options for the file upload process.
 */

import { UploadStatus } from './api';
import { UploadFormData } from './forms';

/**
 * Enum defining supported file types for upload
 */
export enum FileType {
  CSV = 'csv',
  JSON = 'json',
  XML = 'xml',
  IMAGE = 'image',
  AUDIO = 'audio'
}

/**
 * Enum defining possible file validation error types
 */
export enum FileValidationError {
  NONE = 'none',
  FILE_TOO_LARGE = 'file_too_large',
  INVALID_TYPE = 'invalid_type',
  EMPTY_FILE = 'empty_file',
  UPLOAD_ERROR = 'upload_error'
}

/**
 * Interface defining structured file information
 */
export interface FileInfo {
  name: string;
  size: number;
  type: string; // MIME type
  extension: string;
  fileType: FileType | null;
  lastModified: number;
}

/**
 * Interface for tracking upload progress
 */
export interface UploadProgress {
  loaded: number;
  total: number;
  percentage: number;
}

/**
 * Interface for tracking the complete state of a file upload
 */
export interface UploadState {
  file: FileInfo | null;
  status: UploadStatus;
  progress: UploadProgress;
  uploadId: string | null;
  error: FileValidationError;
  errorMessage: string | null;
  processingStep: string | null;
  estimatedTimeRemaining: number | null; // in seconds
  analysisResult: Record<string, any> | null;
}

/**
 * Interface for upload configuration options
 */
export interface UploadConfig {
  maxSizeBytes: number;
  allowedTypes: FileType[];
  acceptedMimeTypes: string[];
  maxFileNameLength: number;
}

/**
 * Interface for upload request parameters sent to the API
 */
export interface UploadRequestParams {
  filename: string;
  size: number;
  mime_type: string;
  form_data: UploadFormData;
}

/**
 * Interface for file type information including human-readable labels and icons
 */
export interface FileTypeInfo {
  label: string;
  extensions: string[];
  mimeTypes: string[];
  icon: string;
}

/**
 * Default configuration for file uploads with size limits and allowed types
 */
export const DEFAULT_UPLOAD_CONFIG: UploadConfig = {
  maxSizeBytes: 50 * 1024 * 1024, // 50MB
  allowedTypes: [
    FileType.CSV,
    FileType.JSON,
    FileType.XML,
    FileType.IMAGE,
    FileType.AUDIO
  ],
  acceptedMimeTypes: [
    'text/csv',
    'application/json',
    'application/xml',
    'text/xml',
    'image/jpeg',
    'image/png',
    'image/gif',
    'image/webp',
    'image/tiff',
    'audio/mp3',
    'audio/wav',
    'audio/ogg',
    'audio/mpeg'
  ],
  maxFileNameLength: 255
};

/**
 * Initial state for the file upload process
 */
export const INITIAL_UPLOAD_STATE: UploadState = {
  file: null,
  status: UploadStatus.PENDING,
  progress: {
    loaded: 0,
    total: 0,
    percentage: 0
  },
  uploadId: null,
  error: FileValidationError.NONE,
  errorMessage: null,
  processingStep: null,
  estimatedTimeRemaining: null,
  analysisResult: null
};

/**
 * Information about supported file types including labels, extensions, and MIME types
 */
export const FILE_TYPE_INFO: Record<FileType, FileTypeInfo> = {
  [FileType.CSV]: {
    label: 'CSV',
    extensions: ['csv'],
    mimeTypes: ['text/csv'],
    icon: 'file-csv'
  },
  [FileType.JSON]: {
    label: 'JSON',
    extensions: ['json'],
    mimeTypes: ['application/json'],
    icon: 'file-code'
  },
  [FileType.XML]: {
    label: 'XML',
    extensions: ['xml'],
    mimeTypes: ['application/xml', 'text/xml'],
    icon: 'file-code'
  },
  [FileType.IMAGE]: {
    label: 'Image',
    extensions: ['jpg', 'jpeg', 'png', 'gif', 'webp', 'tiff'],
    mimeTypes: ['image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/tiff'],
    icon: 'file-image'
  },
  [FileType.AUDIO]: {
    label: 'Audio',
    extensions: ['mp3', 'wav', 'ogg', 'm4a'],
    mimeTypes: ['audio/mp3', 'audio/wav', 'audio/ogg', 'audio/mpeg'],
    icon: 'file-audio'
  }
};

/**
 * Determines the file type based on the MIME type
 * 
 * @param mimeType - The MIME type of the file
 * @returns The determined file type or null if not recognized
 */
export function getFileTypeFromMimeType(mimeType: string): FileType | null {
  if (mimeType.startsWith('image/')) {
    return FileType.IMAGE;
  }

  if (mimeType === 'application/json') {
    return FileType.JSON;
  }

  if (mimeType === 'text/csv') {
    return FileType.CSV;
  }

  if (mimeType === 'application/xml' || mimeType === 'text/xml') {
    return FileType.XML;
  }

  if (mimeType.startsWith('audio/')) {
    return FileType.AUDIO;
  }

  return null;
}

/**
 * Determines the file type based on the file extension
 * 
 * @param extension - The file extension (with or without leading dot)
 * @returns The determined file type or null if not recognized
 */
export function getFileTypeFromExtension(extension: string): FileType | null {
  // Normalize extension by removing leading dot if present and converting to lowercase
  const normalizedExtension = extension.toLowerCase().replace(/^\./, '');

  if (['jpg', 'jpeg', 'png', 'gif', 'webp', 'tiff'].includes(normalizedExtension)) {
    return FileType.IMAGE;
  }

  if (normalizedExtension === 'json') {
    return FileType.JSON;
  }

  if (normalizedExtension === 'csv') {
    return FileType.CSV;
  }

  if (normalizedExtension === 'xml') {
    return FileType.XML;
  }

  if (['mp3', 'wav', 'ogg', 'm4a'].includes(normalizedExtension)) {
    return FileType.AUDIO;
  }

  return null;
}

/**
 * Formats a file size in bytes to a human-readable string
 * 
 * @param bytes - The file size in bytes
 * @returns Human-readable file size (e.g., '2.5 MB')
 */
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes';

  const units = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  const size = parseFloat((bytes / Math.pow(1024, i)).toFixed(1));

  return `${size} ${units[i]}`;
}