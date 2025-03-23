import React from 'react'; // version 18.2.0
import classNames from 'classnames'; // version 2.3.2
import { setAriaAttributes } from '../../utils/accessibility';

/**
 * Interface defining the props for the Textarea component
 */
export interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  /** Name attribute for the textarea */
  name: string;
  /** Current value of the textarea */
  value: string;
  /** Placeholder text to display when textarea is empty */
  placeholder?: string;
  /** Number of visible text rows */
  rows?: number;
  /** Whether the textarea is disabled */
  disabled?: boolean;
  /** Whether the textarea is required */
  required?: boolean;
  /** Error message to display when validation fails */
  error?: string;
  /** Additional class names to apply to the textarea */
  className?: string;
  /** Handler for value change events */
  onChange?: (e: React.ChangeEvent<HTMLTextAreaElement>) => void;
  /** Handler for blur events */
  onBlur?: (e: React.FocusEvent<HTMLTextAreaElement>) => void;
  /** Handler for focus events */
  onFocus?: (e: React.FocusEvent<HTMLTextAreaElement>) => void;
}

/**
 * Generates CSS class names for the textarea based on its props
 * 
 * @param disabled - Whether the textarea is disabled
 * @param hasError - Whether the textarea has an error
 * @param className - Additional custom class names
 * @returns Combined CSS class names string
 */
const getTextareaClasses = (disabled: boolean, hasError: boolean, className?: string): string => {
  return classNames(
    // Base styles for all textareas
    'w-full px-4 py-3 border rounded-md transition-colors',
    'font-sans text-base leading-relaxed resize-vertical',
    'focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
    {
      // Conditional styles based on component state
      'bg-gray-100 text-gray-500 cursor-not-allowed border-gray-300': disabled,
      'border-red-500 focus:ring-red-500 focus:border-red-500': hasError,
      'border-gray-300 bg-white': !disabled && !hasError,
    },
    // Custom class names passed as props
    className
  );
};

/**
 * A customizable textarea component that supports different states and integrates with forms
 * 
 * @param props - The component props
 * @returns Rendered textarea element
 */
const Textarea: React.FC<TextareaProps> = ({
  name,
  value,
  placeholder,
  rows = 3,
  disabled = false,
  required = false,
  error,
  className,
  onChange,
  onBlur,
  onFocus,
  ...rest
}) => {
  // Generate a unique ID for the textarea based on the name
  const textareaId = `textarea-${name}`;
  // Determine if the textarea has an error
  const hasError = !!error;
  // Generate textarea classes
  const textareaClasses = getTextareaClasses(disabled, hasError, className);

  return (
    <div className="relative w-full mb-4">
      <textarea
        id={textareaId}
        name={name}
        value={value}
        placeholder={placeholder}
        rows={rows}
        disabled={disabled}
        required={required}
        className={textareaClasses}
        onChange={onChange}
        onBlur={onBlur}
        onFocus={onFocus}
        ref={(element) => {
          if (element) {
            // Add appropriate ARIA attributes for accessibility
            setAriaAttributes(element, {
              required: required ? 'true' : 'false',
              invalid: hasError ? 'true' : 'false',
              describedby: hasError ? `${textareaId}-error` : undefined,
            });
          }
        }}
        {...rest}
      />
      
      {/* Error message display */}
      {hasError && (
        <div 
          id={`${textareaId}-error`}
          className="mt-1 text-sm text-red-600"
          role="alert"
        >
          {error}
        </div>
      )}
    </div>
  );
};

export default Textarea;