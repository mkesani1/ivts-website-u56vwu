import React, { Component, ErrorInfo, ReactNode } from 'react';
import Alert from '../ui/Alert';
import Button from '../ui/Button';
import { Variant } from '../../types/common';
import { logError, getErrorMessage } from '../../utils/errorHandling';
import { useToastContext } from '../../context/ToastContext';

/**
 * Props for the ErrorBoundary component
 */
export interface ErrorBoundaryProps {
  /**
   * Child components that this error boundary will wrap
   */
  children: ReactNode;
  
  /**
   * Custom fallback UI to display when an error occurs
   * Can be a ReactNode or a function that returns a ReactNode
   */
  fallback?: ReactNode | ((props: { error: Error; resetErrorBoundary: () => void }) => ReactNode);
  
  /**
   * Callback function that is called when an error is caught
   */
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
  
  /**
   * Callback function that is called when the error boundary is reset
   */
  onReset?: () => void;
  
  /**
   * Array of values that when changed should reset the error boundary
   */
  resetKeys?: any[];
  
  /**
   * Whether to show toast notifications for errors
   */
  useToast?: boolean;
}

/**
 * State for the ErrorBoundary component
 */
export interface ErrorBoundaryState {
  /**
   * Whether an error has been caught
   */
  hasError: boolean;
  
  /**
   * The caught error
   */
  error: Error | null;
}

/**
 * A React error boundary component that catches JavaScript errors in its child component tree,
 * logs those errors, and displays a fallback UI instead of crashing the entire application.
 * 
 * This component implements the "Fail Gracefully" pattern, maintaining system stability and
 * providing clear user feedback when errors occur.
 * 
 * @example
 * // Basic usage
 * <ErrorBoundary>
 *   <MyComponent />
 * </ErrorBoundary>
 * 
 * // With custom fallback UI
 * <ErrorBoundary 
 *   fallback={<div>Something went wrong. Please try again later.</div>}
 * >
 *   <MyComponent />
 * </ErrorBoundary>
 * 
 * // With error callback and toast notifications
 * const MyWrapper = ({ children }) => {
 *   const { showError } = useToastContext();
 *   
 *   return (
 *     <ErrorBoundary 
 *       onError={(error) => showError('Error', getErrorMessage(error))}
 *       useToast={true}
 *     >
 *       {children}
 *     </ErrorBoundary>
 *   );
 * };
 */
class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  /**
   * Constructor for the ErrorBoundary component
   */
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      error: null
    };
  }

  /**
   * Static lifecycle method called when an error is thrown in a descendant component.
   * Used to update the component's state to trigger a re-render with the fallback UI.
   * 
   * @param error - The error that was thrown
   * @returns New state with hasError flag and the error object
   */
  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    // Update state to indicate an error has occurred
    return {
      hasError: true,
      error
    };
  }

  /**
   * Lifecycle method called after an error has been thrown by a descendant component.
   * Used for logging the error and informing any error monitoring services.
   * 
   * @param error - The error that was thrown
   * @param errorInfo - Additional information about where the error occurred
   */
  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    // Log the error to our error handling utility
    logError(error, 'ErrorBoundary');
    
    // Call the onError prop if provided
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }
    
    // If toast notifications are enabled, we need to handle this through
    // the onError callback since we can't use hooks directly in class components
    if (this.props.useToast) {
      // This is intentionally left as a comment to document the expected usage pattern
      // The parent component should handle toast notifications through the onError callback:
      // 
      // const { showError } = useToastContext();
      // <ErrorBoundary onError={(error) => showError('Error', getErrorMessage(error))} useToast={true}>
      //   <Component />
      // </ErrorBoundary>
    }
  }

  /**
   * Check if resetKeys prop has changed - if so, reset the error state
   */
  componentDidUpdate(prevProps: ErrorBoundaryProps): void {
    const { resetKeys } = this.props;
    
    // If resetKeys are defined and have changed, reset the error boundary
    if (
      resetKeys && 
      prevProps.resetKeys &&
      resetKeys.length === prevProps.resetKeys.length &&
      resetKeys.some((key, idx) => key !== prevProps.resetKeys?.[idx])
    ) {
      this.resetErrorBoundary();
    }
  }

  /**
   * Reset the error boundary to its initial state
   * This can be called from the fallback UI to allow the user to retry
   */
  resetErrorBoundary = (): void => {
    // Reset error state
    this.setState({
      hasError: false,
      error: null
    });
    
    // Call the onReset prop if provided
    if (this.props.onReset) {
      this.props.onReset();
    }
  };

  /**
   * Render either the fallback UI when an error occurs, or the children normally
   */
  render(): ReactNode {
    const { hasError, error } = this.state;
    const { children, fallback } = this.props;

    // If there's an error, show the fallback UI
    if (hasError && error) {
      // If a custom fallback is provided, use it
      if (fallback) {
        // If fallback is a function, call it with the error and reset function
        if (typeof fallback === 'function') {
          return fallback({ error, resetErrorBoundary: this.resetErrorBoundary });
        }
        // Otherwise, just render the fallback ReactNode
        return fallback;
      }

      // Default fallback UI
      return (
        <div className="error-boundary-fallback" role="alert" aria-live="assertive">
          <Alert
            variant={Variant.ERROR}
            message={
              <div className="error-boundary-content">
                <h3 className="text-lg font-semibold mb-2">Something went wrong</h3>
                <p className="mb-4">{getErrorMessage(error)}</p>
                <Button onClick={this.resetErrorBoundary}>Try again</Button>
              </div>
            }
            className="p-4"
          />
        </div>
      );
    }

    // No error, render children normally
    return children;
  }
}

export default ErrorBoundary;