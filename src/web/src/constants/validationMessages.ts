/**
 * validationMessages.ts
 * 
 * Defines standardized validation error messages used throughout the IndiVillage website
 * for form validation and error handling. This ensures consistent user feedback across
 * all forms including contact forms, demo requests, quote requests, and file uploads.
 */

/**
 * Returns a formatted error message for minimum length validation failures
 * @param length - The minimum required length
 * @returns Formatted error message with the minimum length requirement
 */
export const MIN_LENGTH = (length: number): string => {
  return `This field must be at least ${length} characters long.`;
};

/**
 * Returns a formatted error message for maximum length validation failures
 * @param length - The maximum allowed length
 * @returns Formatted error message with the maximum length requirement
 */
export const MAX_LENGTH = (length: number): string => {
  return `This field cannot exceed ${length} characters.`;
};

/**
 * Returns a formatted error message for file size validation failures
 * @param maxSizeInMB - The maximum allowed file size in megabytes
 * @returns Formatted error message with the maximum file size
 */
export const FILE_SIZE_FORMATTED = (maxSizeInMB: number): string => {
  return `File size should not exceed ${maxSizeInMB} MB.`;
};

/**
 * Standardized validation messages used throughout the application
 */
export const VALIDATION_MESSAGES = {
  /** Required field error message */
  REQUIRED: "This field is required.",
  
  /** Invalid email format error message */
  EMAIL_INVALID: "Please enter a valid email address.",
  
  /** Invalid phone number format error message */
  PHONE_INVALID: "Please enter a valid phone number.",
  
  /** Minimum length error message function */
  MIN_LENGTH,
  
  /** Maximum length error message function */
  MAX_LENGTH,
  
  /** File size exceeded error message */
  FILE_SIZE_EXCEEDED: "The selected file exceeds the maximum allowed size.",
  
  /** Invalid file type error message */
  FILE_TYPE_INVALID: "The selected file type is not supported.",
  
  /** File size formatted error message function */
  FILE_SIZE_FORMATTED,
  
  /** CAPTCHA validation error message */
  CAPTCHA_REQUIRED: "Please complete the CAPTCHA verification.",
  
  /** General validation error message */
  GENERAL_ERROR: "There was a problem with your submission. Please check the form and try again.",
  
  /** File upload failure error message */
  UPLOAD_FAILED: "We couldn't upload your file. Please try again.",
  
  /** Network connection error message */
  NETWORK_ERROR: "Network error. Please check your connection and try again.",
  
  /** Server error message */
  SERVER_ERROR: "We're experiencing technical difficulties. Please try again later.",
  
  /** Form submission error message */
  FORM_SUBMISSION_ERROR: "We couldn't submit your form. Please try again."
};