import React from 'react'; // version 18.2.0
import classNames from 'classnames'; // version 2.3.2
import { InputProps } from '../../types/common';
import Icon from './Icon';
import { setAriaAttributes } from '../../utils/accessibility';

/**
 * Generates CSS class names for the input based on its props
 *
 * @param hasIcon - Whether the input has an icon
 * @param iconPosition - Position of the icon (left or right)
 * @param disabled - Whether the input is disabled
 * @param hasError - Whether the input has an error
 * @param className - Additional custom class names
 * @returns Combined CSS class names string
 */
const getInputClasses = (
  hasIcon: boolean,
  iconPosition: string,
  disabled: boolean,
  hasError: boolean,
  className?: string
): string => {
  return classNames(
    'input', // Base class
    {
      'input--with-icon': hasIcon,
      [`input--icon-${iconPosition}`]: hasIcon && iconPosition,
      'input--disabled': disabled,
      'input--error': hasError,
    },
    className // Additional custom classes
  );
};

/**
 * A reusable Input component that provides consistent styling, behavior, and 
 * accessibility features for text input fields throughout the IndiVillage website.
 * Supports various input types, states (error, disabled), and optional icon integration.
 * 
 * @example
 * // Basic text input
 * <Input name="username" placeholder="Enter your username" />
 * 
 * // Email input with icon
 * <Input 
 *   name="email" 
 *   type="email" 
 *   icon="email" 
 *   placeholder="Enter your email" 
 *   required 
 * />
 * 
 * // Input with error state
 * <Input 
 *   name="password" 
 *   type="password" 
 *   error="Password must be at least 8 characters" 
 * />
 */
const Input: React.FC<InputProps> = ({
  name,
  type = 'text',
  value,
  placeholder,
  disabled = false,
  required = false,
  error,
  icon,
  iconPosition = 'left',
  className,
  onChange,
  onBlur,
  onFocus,
  ...rest
}) => {
  // Generate unique ID for the input field
  const inputId = `input-${name}`;
  
  // Determine if input has icon or error
  const hasIcon = !!icon;
  const hasError = !!error;

  // Generate CSS classes for the input container
  const inputClasses = getInputClasses(hasIcon, iconPosition, disabled, hasError, className);

  return (
    <div className={inputClasses}>
      {/* Render icon if provided */}
      {hasIcon && (
        <div className={`input__icon input__icon--${iconPosition}`}>
          <Icon name={icon} size="small" />
        </div>
      )}
      
      {/* Input element */}
      <input
        id={inputId}
        type={type}
        name={name}
        value={value}
        placeholder={placeholder}
        disabled={disabled}
        required={required}
        className="input__field"
        onChange={onChange}
        onBlur={onBlur}
        onFocus={onFocus}
        ref={(node) => {
          if (node) {
            // Set ARIA attributes for accessibility
            const ariaAttributes: Record<string, string> = {};
            
            if (required) {
              ariaAttributes.required = 'true';
            }
            
            if (hasError) {
              ariaAttributes.invalid = 'true';
              ariaAttributes.describedby = `${inputId}-error`;
            }
            
            setAriaAttributes(node, ariaAttributes);
          }
        }}
        {...rest} // Spread any additional props
      />
      
      {/* Error message */}
      {hasError && (
        <div id={`${inputId}-error`} className="input__error" aria-live="polite">
          {error}
        </div>
      )}
    </div>
  );
};

export default Input;