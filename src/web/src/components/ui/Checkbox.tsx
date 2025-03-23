import React from 'react'; // version 18.2.0
import classNames from 'classnames'; // version 2.3.2
import { setAriaAttributes } from '../../utils/accessibility';
import Icon from './Icon';

/**
 * Props for the Checkbox component
 */
export interface CheckboxProps {
  /** Unique identifier for the checkbox */
  name: string;
  /** Whether the checkbox is checked */
  checked?: boolean;
  /** Whether the checkbox is disabled */
  disabled?: boolean;
  /** Whether the checkbox is required */
  required?: boolean;
  /** Error message to display */
  error?: string;
  /** Additional CSS classes */
  className?: string;
  /** Change event handler */
  onChange?: (event: React.ChangeEvent<HTMLInputElement>) => void;
  /** Blur event handler */
  onBlur?: (event: React.FocusEvent<HTMLInputElement>) => void;
  /** Focus event handler */
  onFocus?: (event: React.FocusEvent<HTMLInputElement>) => void;
}

/**
 * Generates CSS class names for the checkbox element based on its state and props
 */
const getCheckboxClasses = ({ 
  error, 
  disabled, 
  className 
}: Pick<CheckboxProps, 'error' | 'disabled' | 'className'>) => {
  return classNames(
    'checkbox',
    {
      'checkbox--error': error,
      'checkbox--disabled': disabled
    },
    className
  );
};

/**
 * A customizable checkbox component that supports different states and integrates with form validation
 */
const Checkbox: React.FC<CheckboxProps & React.InputHTMLAttributes<HTMLInputElement>> = ({
  name,
  checked = false,
  disabled = false,
  required = false,
  error,
  className,
  onChange,
  onBlur,
  onFocus,
  children,
  ...inputProps
}) => {
  const inputRef = React.useRef<HTMLInputElement>(null);
  const checkboxClasses = getCheckboxClasses({ error, disabled, className });

  return (
    <div className={checkboxClasses}>
      {/* Hidden native checkbox for accessibility and form handling */}
      <input
        ref={inputRef}
        type="checkbox"
        id={name}
        name={name}
        checked={checked}
        disabled={disabled}
        required={required}
        onChange={onChange}
        onBlur={onBlur}
        onFocus={onFocus}
        className="checkbox__input"
        aria-invalid={!!error}
        aria-describedby={error ? `${name}-error` : undefined}
        {...inputProps}
      />
      
      {/* Custom visual checkbox */}
      <label htmlFor={name} className="checkbox__label">
        <span 
          className="checkbox__custom"
          ref={(node) => {
            if (node) {
              // Set ARIA attributes for accessibility
              setAriaAttributes(node, {
                'hidden': 'true'
              });
            }
          }}
        >
          {checked && <Icon name="check" size={16} />}
        </span>
        
        {/* Checkbox label text */}
        {children && <span className="checkbox__text">{children}</span>}
      </label>
      
      {/* Error message if applicable */}
      {error && (
        <div id={`${name}-error`} className="checkbox__error">
          {error}
        </div>
      )}
    </div>
  );
};

export default Checkbox;