/**
 * Common TypeScript types, interfaces, and enums used throughout the IndiVillage website application.
 * This file provides type definitions to ensure type safety and consistency across the codebase.
 * 
 * @module common
 */

import React from 'react';

/**
 * Enum for responsive design breakpoints based on screen width
 * Matches breakpoints defined in Technical Specifications/7.12 RESPONSIVE BREAKPOINTS
 */
export enum Breakpoint {
  MOBILE_SMALL = 'mobileSmall',  // < 375px
  MOBILE = 'mobile',             // 376px - 767px
  TABLET = 'tablet',             // 768px - 1023px
  DESKTOP = 'desktop',           // 1024px - 1439px
  LARGE_DESKTOP = 'largeDesktop' // ≥ 1440px
}

/**
 * Type representing possible breakpoint values
 */
export type BreakpointValue = 'mobileSmall' | 'mobile' | 'tablet' | 'desktop' | 'largeDesktop';

/**
 * Enum for component size options
 */
export enum Size {
  SMALL = 'small',
  MEDIUM = 'medium',
  LARGE = 'large'
}

/**
 * Type representing possible size values
 */
export type SizeValue = 'small' | 'medium' | 'large';

/**
 * Enum for component style variants
 * Matches variant definitions from Technical Specifications/7.14 DESIGN SYSTEM ELEMENTS
 */
export enum Variant {
  PRIMARY = 'primary',     // Filled blue background, white text
  SECONDARY = 'secondary', // White with blue border
  TERTIARY = 'tertiary'    // Text only with underline on hover
}

/**
 * Type representing possible variant values
 */
export type VariantValue = 'primary' | 'secondary' | 'tertiary';

/**
 * Enum for text and content alignment options
 */
export enum Alignment {
  LEFT = 'left',
  CENTER = 'center',
  RIGHT = 'right'
}

/**
 * Type representing possible alignment values
 */
export type AlignmentValue = 'left' | 'center' | 'right';

/**
 * Enum for layout direction options
 */
export enum Direction {
  HORIZONTAL = 'horizontal',
  VERTICAL = 'vertical'
}

/**
 * Type representing possible direction values
 */
export type DirectionValue = 'horizontal' | 'vertical';

/**
 * Interface for pagination parameters in API requests
 */
export interface PaginationParams {
  page: number;
  limit: number;
}

/**
 * Enum for sort direction options
 */
export enum SortDirection {
  ASC = 'asc',
  DESC = 'desc'
}

/**
 * Interface for sorting parameters in API requests
 */
export interface SortParams {
  field: string;
  direction: SortDirection;
}

/**
 * Enum for filter operators in API requests
 */
export enum FilterOperator {
  EQUALS = 'eq',
  NOT_EQUALS = 'neq',
  CONTAINS = 'contains',
  GREATER_THAN = 'gt',
  LESS_THAN = 'lt',
  IN = 'in'
}

/**
 * Interface for filtering parameters in API requests
 */
export interface FilterParams {
  field: string;
  operator: FilterOperator;
  value: string | string[] | number | boolean;
}

/**
 * Interface for page metadata for SEO
 */
export interface MetaData {
  title: string;
  description: string;
  keywords: string[];
  ogImage?: string;
  canonicalUrl?: string;
}

/**
 * Interface for validation error information
 */
export interface ValidationError {
  field: string;
  message: string;
}

/**
 * Enum for form submission states
 */
export enum FormState {
  IDLE = 'idle',
  SUBMITTING = 'submitting',
  SUCCESS = 'success',
  ERROR = 'error'
}

/**
 * Enum for notification toast types
 */
export enum ToastType {
  SUCCESS = 'success',
  ERROR = 'error',
  INFO = 'info',
  WARNING = 'warning'
}

/**
 * Interface for notification toast configuration
 */
export interface Toast {
  id: string;
  type: ToastType;
  message: string;
  duration?: number;
  autoClose?: boolean;
}

/**
 * Type representing available icon names
 * This is a union of string literals for all the icons used in the application
 */
export type IconName = 
  | 'arrowRight'
  | 'arrowLeft'
  | 'check'
  | 'close'
  | 'dataCollection'
  | 'dataPreparation'
  | 'aiModel'
  | 'humanInTheLoop'
  | 'upload'
  | 'download'
  | 'info'
  | 'warning'
  | 'error'
  | 'success'
  | 'user'
  | 'email'
  | 'phone'
  | 'location'
  | 'calendar'
  | 'search'
  | 'linkedin'
  | 'twitter'
  | 'facebook'
  | 'instagram'
  | 'menu';

/**
 * Interface for Icon component props
 */
export interface IconProps {
  name: IconName;
  size?: number | SizeValue;
  color?: string;
  className?: string;
}

/**
 * Interface for Button component props
 */
export interface ButtonProps {
  variant?: VariantValue;
  size?: SizeValue;
  fullWidth?: boolean;
  disabled?: boolean;
  loading?: boolean;
  icon?: IconName;
  iconPosition?: 'left' | 'right';
  children?: React.ReactNode;
  className?: string;
  onClick?: (event: React.MouseEvent<HTMLButtonElement>) => void;
  type?: 'button' | 'submit' | 'reset';
}

/**
 * Interface for Input component props
 */
export interface InputProps {
  name: string;
  type?: string;
  value?: string;
  placeholder?: string;
  disabled?: boolean;
  required?: boolean;
  error?: string;
  icon?: IconName;
  iconPosition?: 'left' | 'right';
  className?: string;
  onChange?: (event: React.ChangeEvent<HTMLInputElement>) => void;
  onBlur?: (event: React.FocusEvent<HTMLInputElement>) => void;
  onFocus?: (event: React.FocusEvent<HTMLInputElement>) => void;
}

/**
 * Interface for select dropdown options
 */
export interface SelectOption {
  value: string;
  label: string;
  disabled?: boolean;
}

/**
 * Interface for Select component props
 */
export interface SelectProps {
  name: string;
  value?: string;
  options: SelectOption[];
  placeholder?: string;
  disabled?: boolean;
  required?: boolean;
  error?: string;
  className?: string;
  onChange?: (event: React.ChangeEvent<HTMLSelectElement>) => void;
  onBlur?: (event: React.FocusEvent<HTMLSelectElement>) => void;
}