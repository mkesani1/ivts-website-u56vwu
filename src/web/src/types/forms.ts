/**
 * Form-related TypeScript interfaces, types, and enums for the IndiVillage website
 * These types support form state management, validation, and various form submissions
 * including contact forms, demo requests, quote requests, and file uploads.
 */

/**
 * Enum representing the possible states of a form during the submission process
 */
export enum FormStatus {
  IDLE = 'idle',
  SUBMITTING = 'submitting',
  SUCCESS = 'success',
  ERROR = 'error'
}

/**
 * Interface representing a form field with its value, validation state, and error message
 */
export interface FormField {
  value: string | string[] | boolean;
  touched: boolean;
  error: string;
}

/**
 * Interface representing the complete state of a form including values, validation state, and submission status
 */
export interface FormState {
  values: Record<string, any>;
  fields: Record<string, FormField>;
  status: FormStatus;
  error: string;
  isValid: boolean;
  isDirty: boolean;
}

/**
 * Interface defining validation rules that can be applied to form fields
 */
export interface FormValidationRules {
  required?: boolean;
  minLength?: number;
  maxLength?: number;
  pattern?: RegExp;
  email?: boolean;
  phone?: boolean;
  custom?: (value: any, formValues: Record<string, any>) => string | undefined;
}

/**
 * Interface defining the data structure for contact form submissions
 */
export interface ContactFormData {
  name: string;
  email: string;
  phone: string;
  company: string;
  message: string;
  recaptchaToken: string;
}

/**
 * Interface defining the data structure for demo request form submissions
 */
export interface DemoRequestFormData {
  firstName: string;
  lastName: string;
  email: string;
  phone: string;
  company: string;
  jobTitle: string;
  serviceInterests: string[];
  preferredDate: string;
  preferredTime: string;
  timeZone: string;
  projectDetails: string;
  referralSource: string;
  recaptchaToken: string;
}

/**
 * Interface defining the data structure for quote request form submissions
 */
export interface QuoteRequestFormData {
  firstName: string;
  lastName: string;
  email: string;
  phone: string;
  company: string;
  jobTitle: string;
  serviceInterests: string[];
  projectDetails: string;
  budgetRange: string;
  timeline: string;
  referralSource: string;
  recaptchaToken: string;
}

/**
 * Interface defining the data structure for file upload form submissions
 */
export interface UploadFormData {
  name: string;
  email: string;
  company: string;
  phone: string;
  serviceInterest: string;
  description: string;
  recaptchaToken: string;
}

/**
 * Interface defining the response structure for form submissions
 */
export interface FormResponse {
  success: boolean;
  message: string;
  errors?: Record<string, string>;
  data?: any;
}

/**
 * Interface defining service interest options for form select fields
 */
export interface ServiceInterestOption {
  value: string;
  label: string;
}

/**
 * Interface defining time zone options for form select fields
 */
export interface TimeZoneOption {
  value: string;
  label: string;
  offset: string;
}

/**
 * Interface defining budget range options for quote request forms
 */
export interface BudgetRangeOption {
  value: string;
  label: string;
}

/**
 * Interface defining timeline options for quote request forms
 */
export interface TimelineOption {
  value: string;
  label: string;
}

/**
 * Interface defining referral source options for form select fields
 */
export interface ReferralSourceOption {
  value: string;
  label: string;
}