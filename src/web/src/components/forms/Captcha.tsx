import React, { useState, useEffect, useRef, useCallback } from 'react'; // version 18.2.0
import classNames from 'classnames'; // version 2.3.2
import { 
  executeRecaptchaV3, 
  renderRecaptchaV2, 
  getRecaptchaToken, 
  resetRecaptcha 
} from '../../lib/recaptcha';
import Loader from '../ui/Loader';
import FormError from './FormError';
import { Size } from '../../types/common';
import { setAriaAttributes } from '../../utils/accessibility';

/**
 * Interface defining the props for the Captcha component
 */
export interface CaptchaProps {
  /** Callback function called when CAPTCHA verification is successful */
  onVerify: (token: string) => void;
  /** Callback function called when CAPTCHA verification fails */
  onError?: (error: Error) => void;
  /** Action name for reCAPTCHA analytics */
  action?: string;
  /** Additional CSS class names */
  className?: string;
  /** Force the use of reCAPTCHA v2 instead of v3 */
  useV2?: boolean;
}

/**
 * Generates a unique ID for the CAPTCHA container element
 * @returns A unique ID string
 */
const generateCaptchaContainerId = (): string => {
  return `recaptcha-container-${Math.random().toString(36).substring(2, 11)}-${Date.now()}`;
};

/**
 * A reusable component that implements Google reCAPTCHA for form security
 * Supports both invisible reCAPTCHA v3 and fallback to checkbox reCAPTCHA v2 when needed,
 * providing protection against spam and automated submissions.
 * 
 * @param props - Component props
 * @returns Rendered Captcha component
 */
const Captcha: React.FC<CaptchaProps> = ({
  onVerify,
  onError,
  action = 'form_submit',
  className,
  useV2 = false,
}) => {
  // State variables
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [widgetId, setWidgetId] = useState<number | null>(null);
  
  // Reference for the CAPTCHA container
  const captchaRef = useRef<HTMLDivElement>(null);
  
  // Generate a unique ID for the CAPTCHA container
  const containerId = generateCaptchaContainerId();
  
  // Initialize CAPTCHA
  useEffect(() => {
    let isMounted = true;
    setLoading(true);
    setError(null);
    
    const initCaptcha = async () => {
      try {
        if (useV2) {
          // Initialize v2 CAPTCHA (checkbox)
          if (captchaRef.current) {
            const id = await renderRecaptchaV2(containerId);
            if (isMounted) {
              setWidgetId(id);
            }
          }
        } else {
          // Initialize v3 CAPTCHA (invisible)
          const token = await executeRecaptchaV3(action);
          if (isMounted) {
            onVerify(token);
          }
        }
        if (isMounted) {
          setLoading(false);
        }
      } catch (err) {
        if (isMounted) {
          setLoading(false);
          const errorMessage = err instanceof Error ? err.message : 'Failed to initialize CAPTCHA';
          setError(errorMessage);
          if (onError && err instanceof Error) {
            onError(err);
          }
        }
      }
    };
    
    initCaptcha();
    
    // Cleanup function
    return () => {
      isMounted = false;
      if (widgetId !== null) {
        resetRecaptcha(widgetId);
      }
    };
  }, [useV2, action, onVerify, onError, containerId]);
  
  // Function to verify the CAPTCHA (for v2)
  const verify = useCallback(() => {
    if (widgetId === null) {
      setError('CAPTCHA not initialized');
      return;
    }
    
    try {
      const token = getRecaptchaToken(widgetId);
      if (!token) {
        setError('Please complete the CAPTCHA verification');
        return;
      }
      setError(null);
      onVerify(token);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'CAPTCHA verification failed';
      setError(errorMessage);
      if (onError && err instanceof Error) {
        onError(err);
      }
    }
  }, [widgetId, onVerify, onError]);
  
  // Function to reset the CAPTCHA (for v2)
  const reset = useCallback(() => {
    if (widgetId !== null) {
      resetRecaptcha(widgetId);
      setError(null);
    }
  }, [widgetId]);
  
  // Set ARIA attributes for accessibility
  useEffect(() => {
    if (captchaRef.current) {
      setAriaAttributes(captchaRef.current, {
        'role': 'region',
        'live': 'polite',
        'label': 'CAPTCHA verification',
        'describedby': error ? `${containerId}-error` : undefined
      });
    }
  }, [containerId, error]);
  
  // Combine CSS classes
  const captchaClasses = classNames(
    'captcha-container',
    {
      'captcha-loading': loading,
      'captcha-error': !!error,
    },
    className
  );
  
  return (
    <div className={captchaClasses}>
      {loading && (
        <div className="captcha-loader flex items-center mb-2">
          <Loader size={Size.SMALL} />
          <span className="ml-2">Verifying you're human...</span>
        </div>
      )}
      
      {error && (
        <FormError 
          error={error} 
          id={`${containerId}-error`} 
          className="captcha-error-message mb-2" 
        />
      )}
      
      <div 
        id={containerId}
        ref={captchaRef}
        className="g-recaptcha"
        aria-label="CAPTCHA verification challenge"
      />
      
      {useV2 && !loading && (
        <div className="captcha-controls mt-2">
          <button 
            type="button" 
            className="captcha-verify-button text-sm mr-2 px-3 py-1 bg-primary text-white rounded" 
            onClick={verify}
            aria-label="Verify CAPTCHA"
          >
            Verify
          </button>
          <button 
            type="button" 
            className="captcha-reset-button text-sm px-3 py-1 border border-gray-300 rounded" 
            onClick={reset}
            aria-label="Reset CAPTCHA"
          >
            Reset
          </button>
        </div>
      )}
    </div>
  );
};

export default Captcha;