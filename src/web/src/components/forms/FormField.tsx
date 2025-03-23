import React from 'react'; // version 18.2.0
import classNames from 'classnames'; // version 2.3.2
import FormError from './FormError';
import { setAriaAttributes } from '../../utils/accessibility';

/**
 * Interface defining the props for the FormField component
 */
export interface FormFieldProps {
  /** ID attribute for the form field */
  id?: string;
  /** Name attribute for the form field */
  name: string;
  /** Label text for the form field */
  label: string;
  /** Form control element(s) */
  children: React.ReactNode;
  /** Whether the field is required */
  required?: boolean;
  /** Validation error message */
  error?: string;
  /** Whether to visually hide the label (still accessible to screen readers) */
  hideLabel?: boolean;
  /** Additional CSS classes for the field container */
  className?: string;
  /** Optional help text to display below the field */
  helpText?: string;
}

/**
 * Generates CSS class names for the form field container based on its props
 * @param required - Whether the field is required
 * @param hasError - Whether the field has an error
 * @param className - Additional custom classes
 * @returns Combined CSS class names string
 */
const getFieldClasses = (required: boolean, hasError: boolean, className?: string): string => {
  return classNames(
    'form-field', 
    'mb-4',
    {
      'form-field-required': required,
      'form-field-error': hasError
    },
    className
  );
};

/**
 * Generates CSS class names for the form field label based on its props
 * @param required - Whether the field is required
 * @param hasError - Whether the field has an error
 * @param hideLabel - Whether to visually hide the label
 * @returns Combined CSS class names string
 */
const getLabelClasses = (required: boolean, hasError: boolean, hideLabel?: boolean): string => {
  return classNames(
    'form-label', 
    'block', 
    'mb-2', 
    'font-medium',
    {
      'text-gray-700': !hasError,
      'text-red-600': hasError,
      'sr-only': hideLabel // Screen reader only
    }
  );
};

/**
 * A reusable form field wrapper component that provides consistent layout, labeling, and error handling
 * for various form input types throughout the IndiVillage website. This component enhances accessibility
 * and user experience by standardizing form field presentation and validation feedback.
 * 
 * @example
 * // Basic usage with an input
 * <FormField name="email" label="Email Address" required>
 *   <Input type="email" placeholder="Enter your email" />
 * </FormField>
 * 
 * // With error message
 * <FormField name="password" label="Password" error="Password must be at least 8 characters">
 *   <Input type="password" />
 * </FormField>
 * 
 * // With help text
 * <FormField name="username" label="Username" helpText="Choose a unique username">
 *   <Input />
 * </FormField>
 */
const FormField: React.FC<FormFieldProps> = ({
  id,
  name,
  label,
  children,
  required = false,
  error,
  hideLabel = false,
  className,
  helpText
}) => {
  // Generate a unique ID if not provided
  const fieldId = id || `field-${name}`;
  
  // Check if the field has an error
  const hasError = !!error;
  
  // Generate error ID for aria-describedby
  const errorId = hasError ? `${fieldId}-error` : undefined;
  
  // Generate help text ID
  const helpTextId = helpText ? `${fieldId}-help` : undefined;
  
  // Determine what will describe the input for screen readers
  const describedBy = [helpTextId, errorId].filter(Boolean).join(' ') || undefined;
  
  // Get CSS classes
  const fieldClasses = getFieldClasses(required, hasError, className);
  const labelClasses = getLabelClasses(required, hasError, hideLabel);
  
  // Clone the child element(s) to add necessary props
  const childrenWithProps = React.Children.map(children, child => {
    if (React.isValidElement(child)) {
      return React.cloneElement(child, {
        id: fieldId,
        name: child.props.name || name,
        'aria-invalid': hasError ? 'true' : undefined,
        'aria-describedby': describedBy,
        required: required,
        error: error,
        ...child.props
      });
    }
    return child;
  });
  
  return (
    <div 
      className={fieldClasses}
      ref={(node) => {
        if (node) {
          // Set field group role for accessibility
          setAriaAttributes(node, {
            'role': 'group',
            'labelledby': hideLabel ? fieldId + '-label' : undefined
          });
        }
      }}
    >
      <label
        id={hideLabel ? `${fieldId}-label` : undefined}
        htmlFor={fieldId}
        className={labelClasses}
      >
        {label}
        {required && <span className="ml-1 text-red-500" aria-hidden="true">*</span>}
      </label>
      
      {childrenWithProps}
      
      {helpText && (
        <div id={helpTextId} className="help-text text-sm mt-1 text-gray-600">
          {helpText}
        </div>
      )}
      
      {error && (
        <FormError error={error} id={errorId} />
      )}
    </div>
  );
};

export default FormField;