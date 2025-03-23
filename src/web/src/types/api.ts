/**
 * API TypeScript interfaces and types for IndiVillage website
 * This file defines all types used for API interactions, including request and response types
 * for services, case studies, impact stories, form submissions, and file uploads.
 */

import {
  ContactFormData,
  DemoRequestFormData,
  QuoteRequestFormData,
  UploadFormData
} from './forms';

/**
 * Generic API response interface with a type parameter for the response data
 */
export interface ApiResponse<T = any> {
  success: boolean;
  data: T;
  message: string;
  errors?: Record<string, string[]>;
}

/**
 * Interface for paginated API responses
 */
export interface PaginatedResponse<T = any> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  totalPages: number;
}

/**
 * Enum for possible file upload status values
 */
export enum UploadStatus {
  PENDING = 'pending',
  UPLOADING = 'uploading',
  UPLOADED = 'uploaded',
  SCANNING = 'scanning',
  PROCESSING = 'processing',
  COMPLETED = 'completed',
  FAILED = 'failed',
  QUARANTINED = 'quarantined'
}

/**
 * Interface for service feature data
 */
export interface ServiceFeature {
  id: string;
  service_id: string;
  title: string;
  description: string;
  order: number;
}

/**
 * Interface for service data
 */
export interface Service {
  id: string;
  name: string;
  slug: string;
  description: string;
  icon: string;
  order: number;
  features: ServiceFeature[];
  case_studies: CaseStudy[];
  created_at: string;
  updated_at: string;
}

/**
 * Interface for industry data
 */
export interface Industry {
  id: string;
  name: string;
  slug: string;
}

/**
 * Interface for case study result data
 */
export interface CaseStudyResult {
  id: string;
  case_study_id: string;
  metric: string;
  value: string;
  description: string;
}

/**
 * Interface for case study data
 */
export interface CaseStudy {
  id: string;
  title: string;
  slug: string;
  client: string;
  challenge: string;
  solution: string;
  industry_id: string;
  industry: Industry;
  results: CaseStudyResult[];
  services: Service[];
  created_at: string;
  updated_at: string;
}

/**
 * Interface for location data
 */
export interface Location {
  id: string;
  name: string;
  region: string;
  country: string;
}

/**
 * Interface for impact metric data
 */
export interface ImpactMetric {
  id: string;
  story_id: string;
  metric_name: string;
  value: string;
  unit: string;
  period_start: string;
  period_end: string;
}

/**
 * Interface for impact story data
 */
export interface ImpactStory {
  id: string;
  title: string;
  slug: string;
  story: string;
  beneficiaries: string;
  location_id: string;
  location: Location;
  media: string;
  metrics: ImpactMetric[];
  created_at: string;
  updated_at: string;
}

/**
 * Interface for contact form submission response
 */
export interface ContactResponse {
  success: boolean;
  message: string;
  submission_id: string;
}

/**
 * Interface for demo request form submission response
 */
export interface DemoRequestResponse {
  success: boolean;
  message: string;
  submission_id: string;
}

/**
 * Interface for quote request form submission response
 */
export interface QuoteRequestResponse {
  success: boolean;
  message: string;
  submission_id: string;
}

/**
 * Interface for form submission error response
 */
export interface FormErrorResponse {
  success: boolean;
  message: string;
  errors: Record<string, string[]>;
}

/**
 * Enum for service interest options in form submissions
 */
export enum ServiceInterestEnum {
  DATA_COLLECTION = 'data_collection',
  DATA_PREPARATION = 'data_preparation',
  AI_MODEL_DEVELOPMENT = 'ai_model_development',
  HUMAN_IN_THE_LOOP = 'human_in_the_loop',
  SOCIAL_IMPACT = 'social_impact'
}

/**
 * Enum for time zone options in demo request form submissions
 */
export enum TimeZoneEnum {
  UTC_MINUS_12 = 'UTC-12:00',
  UTC_MINUS_11 = 'UTC-11:00',
  UTC_MINUS_10 = 'UTC-10:00',
  UTC_MINUS_9 = 'UTC-09:00',
  UTC_MINUS_8 = 'UTC-08:00',
  UTC_MINUS_7 = 'UTC-07:00',
  UTC_MINUS_6 = 'UTC-06:00',
  UTC_MINUS_5 = 'UTC-05:00',
  UTC_MINUS_4 = 'UTC-04:00',
  UTC_MINUS_3 = 'UTC-03:00',
  UTC_MINUS_2 = 'UTC-02:00',
  UTC_MINUS_1 = 'UTC-01:00',
  UTC = 'UTC+00:00',
  UTC_PLUS_1 = 'UTC+01:00',
  UTC_PLUS_2 = 'UTC+02:00',
  UTC_PLUS_3 = 'UTC+03:00',
  UTC_PLUS_4 = 'UTC+04:00',
  UTC_PLUS_5 = 'UTC+05:00',
  UTC_PLUS_6 = 'UTC+06:00',
  UTC_PLUS_7 = 'UTC+07:00',
  UTC_PLUS_8 = 'UTC+08:00',
  UTC_PLUS_9 = 'UTC+09:00',
  UTC_PLUS_10 = 'UTC+10:00',
  UTC_PLUS_11 = 'UTC+11:00',
  UTC_PLUS_12 = 'UTC+12:00'
}

/**
 * Enum for budget range options in quote request form submissions
 */
export enum BudgetRangeEnum {
  UNDER_10K = 'under_10k',
  BETWEEN_10K_50K = 'between_10k_50k',
  BETWEEN_50K_100K = 'between_50k_100k',
  BETWEEN_100K_500K = 'between_100k_500k',
  OVER_500K = 'over_500k',
  NOT_SPECIFIED = 'not_specified'
}

/**
 * Enum for project timeline options in quote request form submissions
 */
export enum ProjectTimelineEnum {
  IMMEDIATELY = 'immediately',
  WITHIN_1_MONTH = 'within_1_month',
  WITHIN_3_MONTHS = 'within_3_months',
  WITHIN_6_MONTHS = 'within_6_months',
  FUTURE_PLANNING = 'future_planning'
}

/**
 * Interface for file upload request response
 */
export interface UploadResponse {
  upload_id: string;
  presigned_url: string;
  presigned_fields: Record<string, string>;
  expires_at: string;
  status: string;
}

/**
 * Interface for file upload status response
 */
export interface UploadStatusResponse {
  upload_id: string;
  filename: string;
  status: UploadStatus;
  created_at: string;
  processed_at: string;
  analysis_result: Record<string, any>;
}

/**
 * Interface for file upload completion response
 */
export interface UploadCompleteResponse {
  success: boolean;
  message: string;
  upload_id: string;
}

/**
 * Interface for file processing results
 */
export interface ProcessingResult {
  upload_id: string;
  status: string;
  summary: Record<string, any>;
  details: Record<string, any>;
  completed_at: string;
}

/**
 * Interface for supported file type information
 */
export interface SupportedFileType {
  extension: string;
  mime_type: string;
  description: string;
  max_size_mb: number;
}

/**
 * Interface for upload request parameters
 */
export interface UploadRequestParams {
  filename: string;
  size: number;
  mime_type: string;
  form_data: UploadFormData;
}

/**
 * Interface for upload completion parameters
 */
export interface UploadCompleteParams {
  upload_id: string;
  success: boolean;
  etag: string;
}