import React from 'react'; // version 18.2.0
import classNames from 'classnames'; // version 2.3.2
import Alert from '../ui/Alert';
import Button from '../ui/Button';
import { ToastType } from '../../types/common';
import { useFadeIn } from '../../utils/animations';

/**
 * Interface defining the props for the FormSuccess component
 */
export interface FormSuccessProps extends React.HTMLAttributes<HTMLDivElement> {
  /**
   * The success message to display
   */
  message?: string;
  
  /**
   * Optional array of action buttons to display beneath the success message
   */
  actions?: Array<{
    label: string;
    onClick: () => void;
    variant?: 'PRIMARY' | 'SECONDARY' | 'TERTIARY';
  }>;
  
  /**
   * Additional CSS class names
   */
  className?: string;
}

/**
 * A component that displays form submission success messages with optional action buttons
 * 
 * @example
 * // Basic usage
 * <FormSuccess message="Your form has been submitted successfully!" />
 * 
 * // With action buttons
 * <FormSuccess 
 *   message="Your data has been uploaded successfully!"
 *   actions={[
 *     { label: "View Results", onClick: () => navigate("/results") },
 *     { label: "Upload Another", onClick: handleReset, variant: "SECONDARY" }
 *   ]}
 * />
 */
const FormSuccess: React.FC<FormSuccessProps> = ({
  message,
  actions,
  className,
  ...rest
}) => {
  // Return null if no message is provided
  if (!message) return null;
  
  // Use fade-in animation for a smooth entrance
  const fadeIn = useFadeIn({
    duration: 300,
    delay: 100
  });
  
  // Generate CSS class names
  const containerClasses = classNames(
    'form-success',
    className
  );
  
  return (
    <div 
      className={containerClasses}
      ref={fadeIn.ref as React.RefObject<HTMLDivElement>}
      style={fadeIn.style}
      {...rest}
    >
      <Alert 
        variant={ToastType.SUCCESS}
        message={message}
        showIcon={true}
        className="form-success__alert"
      />
      
      {actions && actions.length > 0 && (
        <div className="form-success__actions mt-4 flex space-x-3">
          {actions.map((action, index) => (
            <Button
              key={index}
              onClick={action.onClick}
              variant={(action.variant?.toLowerCase() as 'primary' | 'secondary' | 'tertiary') || 'primary'}
              size="medium"
            >
              {action.label}
            </Button>
          ))}
        </div>
      )}
    </div>
  );
};

export default FormSuccess;