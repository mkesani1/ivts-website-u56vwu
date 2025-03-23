import React, { createContext, useContext, useState, useCallback, useEffect, ReactNode } from 'react'; // version ^18.2.0
import Alert from '../components/ui/Alert';
import { Variant } from '../types/common';

/**
 * Interface for toast notification object
 */
interface Toast {
  id: string;
  variant: Variant;
  title: string;
  message: string | React.ReactNode;
  duration: number;
  icon?: boolean;
}

/**
 * Interface for the toast context value
 */
interface ToastContextType {
  toasts: Toast[];
  showToast: (toast: Omit<Toast, 'id'>) => string;
  removeToast: (id: string) => void;
  showSuccess: (title: string, message: string | React.ReactNode, duration?: number) => string;
  showError: (title: string, message: string | React.ReactNode, duration?: number) => string;
  showWarning: (title: string, message: string | React.ReactNode, duration?: number) => string;
  showInfo: (title: string, message: string | React.ReactNode, duration?: number) => string;
  clearAll: () => void;
}

/**
 * Props for the ToastProvider component
 */
interface ToastProviderProps {
  children: ReactNode;
  defaultDuration?: number;
}

/**
 * Default duration for toast notifications in milliseconds
 */
const DEFAULT_DURATION = 5000;

/**
 * React context for toast notifications
 */
const ToastContext = createContext<ToastContextType | undefined>(undefined);

/**
 * Provider component for toast notifications
 * 
 * Manages the state of all active toast notifications and provides
 * methods for creating, removing, and managing toasts.
 * 
 * @example
 * // Wrap your application with the ToastProvider
 * <ToastProvider>
 *   <App />
 * </ToastProvider>
 */
export const ToastProvider: React.FC<ToastProviderProps> = ({ 
  children, 
  defaultDuration = DEFAULT_DURATION 
}) => {
  // State to store active toast notifications
  const [toasts, setToasts] = useState<Toast[]>([]);

  /**
   * Add a new toast notification
   * @param toast - Toast options without ID
   * @returns The ID of the created toast
   */
  const showToast = useCallback((toast: Omit<Toast, 'id'>) => {
    // Generate a unique ID for the toast
    const id = `toast-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
    const newToast = { ...toast, id };
    
    setToasts(prevToasts => [...prevToasts, newToast]);
    
    return id;
  }, []);

  /**
   * Remove a toast notification by ID
   * @param id - The ID of the toast to remove
   */
  const removeToast = useCallback((id: string) => {
    setToasts(prevToasts => prevToasts.filter(toast => toast.id !== id));
  }, []);

  /**
   * Show a success toast notification
   * @param title - The title of the toast
   * @param message - The message content
   * @param duration - Optional custom duration in milliseconds
   * @returns The ID of the created toast
   */
  const showSuccess = useCallback((title: string, message: string | React.ReactNode, duration?: number) => {
    return showToast({
      variant: Variant.SUCCESS,
      title,
      message,
      duration: duration ?? defaultDuration,
      icon: true
    });
  }, [showToast, defaultDuration]);

  /**
   * Show an error toast notification
   * @param title - The title of the toast
   * @param message - The message content
   * @param duration - Optional custom duration in milliseconds
   * @returns The ID of the created toast
   */
  const showError = useCallback((title: string, message: string | React.ReactNode, duration?: number) => {
    return showToast({
      variant: Variant.ERROR,
      title,
      message,
      duration: duration ?? defaultDuration,
      icon: true
    });
  }, [showToast, defaultDuration]);

  /**
   * Show a warning toast notification
   * @param title - The title of the toast
   * @param message - The message content
   * @param duration - Optional custom duration in milliseconds
   * @returns The ID of the created toast
   */
  const showWarning = useCallback((title: string, message: string | React.ReactNode, duration?: number) => {
    return showToast({
      variant: Variant.WARNING,
      title,
      message,
      duration: duration ?? defaultDuration,
      icon: true
    });
  }, [showToast, defaultDuration]);

  /**
   * Show an info toast notification
   * @param title - The title of the toast
   * @param message - The message content
   * @param duration - Optional custom duration in milliseconds
   * @returns The ID of the created toast
   */
  const showInfo = useCallback((title: string, message: string | React.ReactNode, duration?: number) => {
    return showToast({
      variant: Variant.INFO,
      title,
      message,
      duration: duration ?? defaultDuration,
      icon: true
    });
  }, [showToast, defaultDuration]);

  /**
   * Clear all toast notifications
   */
  const clearAll = useCallback(() => {
    setToasts([]);
  }, []);

  // Set up auto-dismiss timers for toasts
  useEffect(() => {
    const timers: NodeJS.Timeout[] = [];
    
    toasts.forEach(toast => {
      if (toast.duration > 0) {
        const timer = setTimeout(() => {
          removeToast(toast.id);
        }, toast.duration);
        
        timers.push(timer);
      }
    });
    
    // Clear timers on unmount or when toasts change
    return () => {
      timers.forEach(timer => clearTimeout(timer));
    };
  }, [toasts, removeToast]);

  // Create context value object with all toast functions and state
  const contextValue = {
    toasts,
    showToast,
    removeToast,
    showSuccess,
    showError,
    showWarning,
    showInfo,
    clearAll
  };

  return (
    <ToastContext.Provider value={contextValue}>
      {children}
      
      {/* Toast container - positioned in the top-right corner */}
      <div
        className="toast-container fixed top-4 right-4 z-50 flex flex-col items-end space-y-2 max-w-md"
        aria-live="polite"
        aria-atomic="true"
      >
        {toasts.map(toast => (
          <Alert
            key={toast.id}
            variant={toast.variant}
            title={toast.title}
            message={toast.message}
            icon={toast.icon}
            dismissible
            onDismiss={() => removeToast(toast.id)}
            className="shadow-md w-full transition-all duration-300 animate-fadeIn"
          />
        ))}
      </div>
    </ToastContext.Provider>
  );
};

/**
 * Custom hook to access the toast context
 * 
 * @example
 * // Usage in a component
 * const { showSuccess, showError } = useToastContext();
 * 
 * // Show a success toast
 * showSuccess('Success!', 'Operation completed successfully');
 * 
 * // Show an error toast
 * showError('Error', 'Something went wrong, please try again');
 * 
 * @returns The toast context object with notification functions
 * @throws Error if used outside of a ToastProvider
 */
export const useToastContext = (): ToastContextType => {
  const context = useContext(ToastContext);
  
  if (context === undefined) {
    throw new Error('useToastContext must be used within a ToastProvider');
  }
  
  return context;
};