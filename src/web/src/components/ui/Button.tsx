import React from 'react'; // version 18.2.0
import classNames from 'classnames'; // version 2.3.2

import { ButtonProps, Variant, Size } from '../../types/common';
import Icon from './Icon';
import Loader from './Loader';
import { setAriaAttributes } from '../../utils/accessibility';

/**
 * Generates CSS class names for the button based on its props
 */
const getButtonClasses = (
  variant: string,
  size: string,
  fullWidth: boolean,
  disabled: boolean,
  hasIcon: boolean,
  iconPosition: 'left' | 'right',
  className?: string
): string => {
  return classNames(
    'btn', // Base button class
    `btn--${variant}`, // Variant-specific class (primary, secondary, tertiary)
    `btn--${size}`, // Size-specific class (small, medium, large)
    {
      'btn--full-width': fullWidth, // Full width modifier
      'btn--disabled': disabled, // Disabled state modifier
      'btn--with-icon': hasIcon, // Has icon modifier
      [`btn--icon-${iconPosition}`]: hasIcon, // Icon position modifier
    },
    className // Custom classes passed as props
  );
};

/**
 * A customizable button component that supports different variants, sizes, states, and icons.
 * Implements the button styles specified in the design system.
 * 
 * @example
 * // Primary button (default)
 * <Button onClick={handleClick}>Click Me</Button>
 * 
 * // Secondary button with icon
 * <Button variant="secondary" icon="arrowRight" iconPosition="right">
 *   Next Step
 * </Button>
 * 
 * // Loading state
 * <Button loading>Processing...</Button>
 * 
 * // Disabled state
 * <Button disabled>Unavailable</Button>
 */
const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'medium',
  fullWidth = false,
  disabled = false,
  loading = false,
  icon,
  iconPosition = 'left',
  children,
  className,
  onClick,
  type = 'button',
  ...rest
}) => {
  // Determine if the button has an icon
  const hasIcon = !!icon;

  // Generate button class names
  const buttonClasses = getButtonClasses(
    variant,
    size,
    fullWidth,
    disabled,
    hasIcon,
    iconPosition,
    className
  );

  // Handler for button click that respects disabled state
  const handleClick = (event: React.MouseEvent<HTMLButtonElement>) => {
    if (disabled || loading) return;
    onClick?.(event);
  };

  return (
    <button
      className={buttonClasses}
      disabled={disabled}
      onClick={handleClick}
      type={type}
      aria-busy={loading ? 'true' : 'false'}
      {...rest}
    >
      {loading ? (
        // Show loader when in loading state
        <Loader
          size={size}
          className="btn__loader"
          variant="spinner"
        />
      ) : (
        <>
          {/* Render icon if provided and position is 'left' */}
          {hasIcon && iconPosition === 'left' && (
            <Icon
              name={icon}
              size={size}
              className="btn__icon btn__icon--left"
            />
          )}
          
          {/* Button content */}
          <span className="btn__content">{children}</span>
          
          {/* Render icon if provided and position is 'right' */}
          {hasIcon && iconPosition === 'right' && (
            <Icon
              name={icon}
              size={size}
              className="btn__icon btn__icon--right"
            />
          )}
        </>
      )}
    </button>
  );
};

export default Button;