import React from 'react'; // version 18.2.0
import classNames from 'classnames'; // version 2.3.2
import { ToastType } from '../../types/common';
import Icon from './Icon';
import { setAriaAttributes } from '../../utils/accessibility';

/**
 * Interface for Alert component props
 */
export interface AlertProps extends React.HTMLAttributes<HTMLDivElement> {
  /** The alert variant that determines its styling */
  variant?: ToastType;
  /** The message to display */
  message?: string;
  /** Optional custom icon name to override the default icon */
  icon?: string;
  /** Whether to show the icon */
  showIcon?: boolean;
  /** Additional CSS classes */
  className?: string;
  /** React children for custom content */
  children?: React.ReactNode;
}

/**
 * Returns the appropriate icon name based on the alert variant
 * @param variant - The alert variant
 * @returns The icon name to use
 */
const getAlertIcon = (variant: ToastType): string => {
  switch (variant) {
    case ToastType.SUCCESS:
      return 'success';
    case ToastType.ERROR:
      return 'error';
    case ToastType.WARNING:
      return 'warning';
    case ToastType.INFO:
    default:
      return 'info';
  }
};

/**
 * Generates CSS class names for the alert based on variant and custom className
 * @param variant - The alert variant
 * @param className - Additional CSS classes
 * @returns A string of combined CSS class names
 */
const getAlertClasses = (variant: ToastType, className?: string): string => {
  return classNames(
    'alert',
    'flex items-center p-4 mb-4 border rounded-lg',
    {
      'bg-green-50 text-green-800 border-green-300': variant === ToastType.SUCCESS,
      'bg-red-50 text-red-800 border-red-300': variant === ToastType.ERROR,
      'bg-yellow-50 text-yellow-800 border-yellow-300': variant === ToastType.WARNING,
      'bg-blue-50 text-blue-800 border-blue-300': variant === ToastType.INFO || !variant,
    },
    className
  );
};

/**
 * A customizable alert component that displays notifications with different severity levels
 * 
 * @example
 * // Basic usage with message
 * <Alert variant={ToastType.SUCCESS} message="Operation completed successfully" />
 * 
 * // With custom content
 * <Alert variant={ToastType.WARNING}>
 *   <h4>Warning</h4>
 *   <p>This action cannot be undone.</p>
 * </Alert>
 * 
 * // Without icon
 * <Alert variant={ToastType.INFO} message="For your information" showIcon={false} />
 */
const Alert: React.FC<AlertProps> = ({
  variant = ToastType.INFO,
  message,
  icon,
  showIcon = true,
  className,
  children,
  ...rest
}) => {
  // Generate CSS classes
  const alertClasses = getAlertClasses(variant, className);
  
  // Determine which icon to display
  const iconName = icon || getAlertIcon(variant);
  
  return (
    <div 
      className={alertClasses}
      ref={(node) => {
        if (node) {
          // Set ARIA role and attributes for accessibility
          setAriaAttributes(node, {
            'role': 'alert',
            'atomic': 'true',
          });
        }
      }}
      {...rest}
    >
      {showIcon && (
        <Icon 
          name={iconName} 
          className="mr-3 flex-shrink-0" 
          size="medium"
        />
      )}
      <div className="alert-content ml-2">
        {message || children}
      </div>
    </div>
  );
};

export default Alert;