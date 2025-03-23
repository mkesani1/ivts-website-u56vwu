import React, { useRef, useEffect } from 'react'; // version 18.2.0
import classNames from 'classnames'; // version 2.3.2
import { setAriaAttributes } from '../../utils/accessibility';

/**
 * Props for the RadioButton component
 */
export interface RadioButtonProps {
  /** Name attribute for the radio button */
  name: string;
  /** Value attribute for the radio button */
  value: string;
  /** Whether the radio button is checked */
  checked?: boolean;
  /** Whether the radio button is disabled */
  disabled?: boolean;
  /** Whether the radio button is required */
  required?: boolean;
  /** Error message for validation errors */
  error?: string;
  /** Additional CSS class names */
  className?: string;
  /** Change event handler */
  onChange?: React.ChangeEventHandler<HTMLInputElement>;
  /** Blur event handler */
  onBlur?: React.FocusEventHandler<HTMLInputElement>;
  /** Focus event handler */
  onFocus?: React.FocusEventHandler<HTMLInputElement>;
}

/**
 * Generates CSS class names for the radio button element based on its state and props
 */
const getRadioButtonClasses = (options: {
  error?: string;
  disabled?: boolean;
  className?: string;
}): string => {
  return classNames(
    // Base classes
    'inline-flex items-center',
    // Conditional classes
    {
      'text-error': options.error,
      'opacity-60 cursor-not-allowed': options.disabled,
      'cursor-pointer': !options.disabled,
    },
    // Additional custom classes
    options.className
  );
};

/**
 * A customizable radio button component that supports different states and integrates with form validation
 */
const RadioButton = ({
  name,
  value,
  checked = false,
  disabled = false,
  required = false,
  error,
  className,
  onChange,
  onBlur,
  onFocus,
  ...rest
}: RadioButtonProps & React.InputHTMLAttributes<HTMLInputElement>): JSX.Element => {
  const containerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Set ARIA attributes for accessibility
  useEffect(() => {
    if (containerRef.current) {
      setAriaAttributes(containerRef.current, {
        'describedby': error ? `${name}-${value}-error` : undefined
      });
    }
  }, [name, value, error]);

  // Handle click on the custom radio visual
  const handleCustomRadioClick = () => {
    if (!disabled && inputRef.current) {
      inputRef.current.click();
    }
  };

  return (
    <div
      ref={containerRef}
      className={getRadioButtonClasses({ error, disabled, className })}
    >
      {/* Native radio input (visually hidden) */}
      <input
        ref={inputRef}
        type="radio"
        id={`radio-${name}-${value}`}
        name={name}
        value={value}
        checked={checked}
        disabled={disabled}
        required={required}
        onChange={onChange}
        onBlur={onBlur}
        onFocus={onFocus}
        className="sr-only" // Visually hidden but accessible to screen readers
        aria-invalid={!!error}
        {...rest}
      />
      
      {/* Custom radio button visual */}
      <div 
        onClick={handleCustomRadioClick}
        className={classNames(
          'w-5 h-5 rounded-full border-2 flex items-center justify-center mr-2 transition-colors',
          {
            'border-primary bg-white': !error && !disabled && !checked,
            'border-primary bg-primary': !error && !disabled && checked,
            'border-error': !!error && !disabled,
            'border-gray-300 bg-gray-100': disabled,
          }
        )}
        aria-hidden="true"
      >
        {checked && (
          <div 
            className={classNames(
              'w-2.5 h-2.5 rounded-full',
              {
                'bg-white': !error && !disabled,
                'bg-error': !!error && !disabled,
                'bg-gray-300': disabled,
              }
            )}
          />
        )}
      </div>

      {/* Error message for screen readers */}
      {error && (
        <span id={`${name}-${value}-error`} className="sr-only">
          {error}
        </span>
      )}
    </div>
  );
};

export default RadioButton;