import { VALIDATION_MESSAGES } from '../constants/validationMessages';
import { FormValidationRules, FormField } from '../types/forms';
import { logError } from './errorHandling';

// Regular expressions for common validation patterns
const EMAIL_REGEX = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
const PHONE_REGEX = /^\+?[0-9\s\(\)\-\.]{8,20}$/;

// Constants for file validation
const ALLOWED_FILE_TYPES = [
  'image/jpeg',
  'image/png',
  'image/gif',
  'text/csv',
  'application/json',
  'application/xml',
  'text/plain',
  'application/vnd.ms-excel',
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
  'audio/mpeg',
  'audio/wav'
];
const MAX_FILE_SIZE_MB = 50;

/**
 * Validates that a field has a non-empty value
 * @param value - The value to validate
 * @returns Error message if validation fails, empty string if passes
 */
export const validateRequired = (value: any): string => {
  if (value === undefined || value === null || value === '') {
    return VALIDATION_MESSAGES.REQUIRED;
  }
  return '';
};

/**
 * Validates that a string is a properly formatted email address
 * @param value - The email string to validate
 * @returns Error message if validation fails, empty string if passes
 */
export const validateEmail = (value: string): string => {
  if (!value) {
    return ''; // Optional validation
  }
  
  if (!EMAIL_REGEX.test(value)) {
    return VALIDATION_MESSAGES.EMAIL_INVALID;
  }
  
  return '';
};

/**
 * Validates that a string is a properly formatted phone number
 * @param value - The phone string to validate
 * @returns Error message if validation fails, empty string if passes
 */
export const validatePhone = (value: string): string => {
  if (!value) {
    return ''; // Optional validation
  }
  
  if (!PHONE_REGEX.test(value)) {
    return VALIDATION_MESSAGES.PHONE_INVALID;
  }
  
  return '';
};

/**
 * Validates that a string meets minimum length requirements
 * @param value - The string to validate
 * @param minLength - The minimum required length
 * @returns Error message if validation fails, empty string if passes
 */
export const validateMinLength = (value: string, minLength: number): string => {
  if (!value) {
    return ''; // Optional validation
  }
  
  if (value.length < minLength) {
    return VALIDATION_MESSAGES.MIN_LENGTH(minLength);
  }
  
  return '';
};

/**
 * Validates that a string does not exceed maximum length
 * @param value - The string to validate
 * @param maxLength - The maximum allowed length
 * @returns Error message if validation fails, empty string if passes
 */
export const validateMaxLength = (value: string, maxLength: number): string => {
  if (!value) {
    return ''; // Optional validation
  }
  
  if (value.length > maxLength) {
    return VALIDATION_MESSAGES.MAX_LENGTH(maxLength);
  }
  
  return '';
};

/**
 * Validates that a string matches a specified regular expression pattern
 * @param value - The string to validate
 * @param pattern - The regular expression pattern to match against
 * @param errorMessage - Custom error message to return if validation fails
 * @returns Error message if validation fails, empty string if passes
 */
export const validatePattern = (value: string, pattern: RegExp, errorMessage: string): string => {
  if (!value) {
    return ''; // Optional validation
  }
  
  if (!pattern.test(value)) {
    return errorMessage;
  }
  
  return '';
};

/**
 * Validates that a file is of an allowed type
 * @param file - The file to validate
 * @param allowedTypes - Array of allowed MIME types (optional, uses default if not provided)
 * @returns Error message if validation fails, empty string if passes
 */
export const validateFileType = (file: File, allowedTypes?: string[]): string => {
  if (!file) {
    return '';
  }
  
  const types = allowedTypes || ALLOWED_FILE_TYPES;
  
  if (!types.includes(file.type)) {
    return VALIDATION_MESSAGES.FILE_TYPE_INVALID;
  }
  
  return '';
};

/**
 * Validates that a file does not exceed maximum size
 * @param file - The file to validate
 * @param maxSizeMB - Maximum file size in MB (optional, uses default if not provided)
 * @returns Error message if validation fails, empty string if passes
 */
export const validateFileSize = (file: File, maxSizeMB?: number): string => {
  if (!file) {
    return '';
  }
  
  const maxSize = maxSizeMB || MAX_FILE_SIZE_MB;
  const fileSizeMB = file.size / (1024 * 1024);
  
  if (fileSizeMB > maxSize) {
    return VALIDATION_MESSAGES.FILE_SIZE_EXCEEDED;
  }
  
  return '';
};

/**
 * Validates a single form field against specified validation rules
 * @param name - Field name
 * @param value - Field value
 * @param rules - Validation rules to apply
 * @returns Error message if validation fails, empty string if passes
 */
export const validateField = (name: string, value: any, rules: FormValidationRules): string => {
  if (!rules) {
    return '';
  }
  
  // Required validation - check first
  if (rules.required) {
    const error = validateRequired(value);
    if (error) {
      logError({ message: `Field "${name}" failed required validation`, field: name, value }, 'validation');
      return error;
    }
  }
  
  // Skip other validations if value is empty and not required
  if (value === undefined || value === null || value === '') {
    return '';
  }
  
  // Email validation
  if (rules.email) {
    const error = validateEmail(value as string);
    if (error) {
      logError({ message: `Field "${name}" failed email validation`, field: name, value }, 'validation');
      return error;
    }
  }
  
  // Phone validation
  if (rules.phone) {
    const error = validatePhone(value as string);
    if (error) {
      logError({ message: `Field "${name}" failed phone validation`, field: name, value }, 'validation');
      return error;
    }
  }
  
  // MinLength validation
  if (rules.minLength !== undefined) {
    const error = validateMinLength(value as string, rules.minLength);
    if (error) {
      logError(
        { message: `Field "${name}" failed minLength validation`, field: name, value, minLength: rules.minLength },
        'validation'
      );
      return error;
    }
  }
  
  // MaxLength validation
  if (rules.maxLength !== undefined) {
    const error = validateMaxLength(value as string, rules.maxLength);
    if (error) {
      logError(
        { message: `Field "${name}" failed maxLength validation`, field: name, value, maxLength: rules.maxLength },
        'validation'
      );
      return error;
    }
  }
  
  // Pattern validation
  if (rules.pattern) {
    const error = validatePattern(
      value as string,
      rules.pattern,
      'Invalid format' // Default error message
    );
    if (error) {
      logError({ message: `Field "${name}" failed pattern validation`, field: name, value }, 'validation');
      return error;
    }
  }
  
  // Custom validation - run this last
  if (rules.custom) {
    const customError = rules.custom(value, {});
    if (customError) {
      logError({ message: `Field "${name}" failed custom validation`, field: name, value }, 'validation');
      return customError;
    }
  }
  
  return '';
};

/**
 * Validates an entire form against validation rules
 * @param values - Form values object
 * @param validationRules - Object mapping field names to validation rules
 * @returns Object mapping field names to error messages
 */
export const validateForm = (
  values: Record<string, any>,
  validationRules: Record<string, FormValidationRules>
): Record<string, string> => {
  const errors: Record<string, string> = {};
  
  for (const field in validationRules) {
    const error = validateField(field, values[field], validationRules[field]);
    if (error) {
      errors[field] = error;
    }
  }
  
  return errors;
};

/**
 * Validates a file against type and size constraints
 * @param file - The file to validate
 * @param options - Options including allowedTypes and maxSizeMB
 * @returns Object with isValid flag and error message if invalid
 */
export const validateFile = (
  file: File,
  options: {
    allowedTypes?: string[];
    maxSizeMB?: number;
  } = {}
): { isValid: boolean; errorMessage: string } => {
  if (!file) {
    return { isValid: false, errorMessage: 'No file provided' };
  }
  
  const { allowedTypes, maxSizeMB } = options;
  
  // Validate file type
  const typeError = validateFileType(file, allowedTypes);
  if (typeError) {
    return { isValid: false, errorMessage: typeError };
  }
  
  // Validate file size
  const sizeError = validateFileSize(file, maxSizeMB);
  if (sizeError) {
    return { isValid: false, errorMessage: sizeError };
  }
  
  return { isValid: true, errorMessage: '' };
};

export {
  ALLOWED_FILE_TYPES,
  MAX_FILE_SIZE_MB
};