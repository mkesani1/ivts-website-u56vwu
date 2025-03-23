import React from 'react'; // version 18.2.0
import classNames from 'classnames'; // version 2.3.2
import Alert from '../ui/Alert';
import { ToastType } from '../../types/common';

/**
 * Interface for FormError component props
 */
export interface FormErrorProps extends React.HTMLAttributes<HTMLDivElement> {
  /** Error message to display */
  error?: string;
  /** ID for the error message, used for associating with form field */
  id?: string;
  /** Additional CSS classes */
  className?: string;
}

/**
 * A reusable component for displaying form field validation errors
 * with consistent styling and accessibility features. Used across all form components
 * to provide clear feedback on validation failures.
 *
 * This component implements the error state styling specified in the design system
 * and includes appropriate ARIA attributes for accessibility.
 * 
 * @example
 * // Basic usage with error message
 * <FormError error="This field is required" id="email-error" />
 * 
 * // Associated with a form field
 * <div>
 *   <label htmlFor="email">Email</label>
 *   <input 
 *     id="email" 
 *     name="email" 
 *     aria-describedby="email-error" 
 *     aria-invalid={!!error}
 *   />
 *   <FormError error={error} id="email-error" />
 * </div>
 */
const FormError: React.FC<FormErrorProps> = ({
  error,
  id,
  className,
  ...rest
}) => {
  // Return null if no error message is provided
  if (!error) return null;
  
  // Generate CSS class names
  const errorClasses = classNames(
    'form-error',
    'text-sm',
    'py-1',
    'px-2',
    'mt-1',
    className
  );
  
  return (
    <Alert
      variant={ToastType.ERROR}
      message={error}
      className={errorClasses}
      id={id}
      showIcon={true}
      {...rest}
    />
  );
};

export default FormError;