/**
 * @file recaptcha.ts
 * @description Utility library for Google reCAPTCHA integration
 * 
 * This library provides functions for loading, executing, and managing reCAPTCHA v3 (invisible)
 * and v2 (checkbox) verification on the IndiVillage website. It abstracts the complexity of
 * reCAPTCHA implementation and provides a consistent interface for form security across the application.
 */

// reCAPTCHA site keys from environment variables
const RECAPTCHA_SITE_KEY = process.env.NEXT_PUBLIC_RECAPTCHA_SITE_KEY;
const RECAPTCHA_V3_SITE_KEY = process.env.NEXT_PUBLIC_RECAPTCHA_V3_SITE_KEY || RECAPTCHA_SITE_KEY;
const RECAPTCHA_V2_SITE_KEY = process.env.NEXT_PUBLIC_RECAPTCHA_V2_SITE_KEY || RECAPTCHA_SITE_KEY;

// Type definition for global grecaptcha to help with TypeScript checking
declare global {
  interface Window {
    grecaptcha: {
      ready: (callback: () => void) => void;
      execute: (siteKey: string, options: { action: string }) => Promise<string>;
      render: (container: string | HTMLElement, options: any) => number;
      getResponse: (widgetId: number) => string;
      reset: (widgetId?: number) => void;
    };
  }
}

/**
 * Loads the Google reCAPTCHA script dynamically if not already loaded
 * 
 * @param version - The reCAPTCHA version to load ('v2' or 'v3')
 * @returns Promise resolving to true if script loaded successfully, false otherwise
 */
const loadRecaptchaScript = (version: string): Promise<boolean> => {
  return new Promise((resolve, reject) => {
    // Check if reCAPTCHA script is already loaded
    if (typeof window !== 'undefined' && window.grecaptcha) {
      resolve(true);
      return;
    }

    try {
      // Create script element
      const script = document.createElement('script');
      const recaptchaUrl = `https://www.google.com/recaptcha/api.js`;
      
      // Set the appropriate src URL based on version
      script.src = version === 'v3' 
        ? `${recaptchaUrl}?render=${RECAPTCHA_V3_SITE_KEY}` 
        : recaptchaUrl;
      
      script.async = true;
      script.defer = true;

      // Handle script load success
      script.onload = () => {
        // For v3, we need to ensure grecaptcha is ready
        if (version === 'v3' && window.grecaptcha) {
          window.grecaptcha.ready(() => {
            resolve(true);
          });
        } else {
          resolve(true);
        }
      };

      // Handle script load failure
      script.onerror = () => {
        console.error('Failed to load reCAPTCHA script');
        reject(new Error('Failed to load reCAPTCHA script'));
      };

      // Add script to document
      document.head.appendChild(script);
    } catch (error) {
      console.error('Error loading reCAPTCHA script:', error);
      reject(error);
    }
  });
};

/**
 * Executes reCAPTCHA v3 verification and returns the token
 * 
 * @param action - The action name to associate with this verification (for analytics)
 * @returns Promise resolving to the reCAPTCHA token
 */
export const executeRecaptchaV3 = async (action: string): Promise<string> => {
  if (!RECAPTCHA_V3_SITE_KEY) {
    throw new Error('reCAPTCHA site key is not configured');
  }

  try {
    // Load the reCAPTCHA script if not already loaded
    await loadRecaptchaScript('v3');

    // Execute reCAPTCHA and get token
    return await window.grecaptcha.execute(RECAPTCHA_V3_SITE_KEY, { action });
  } catch (error) {
    console.error('Error executing reCAPTCHA v3:', error);
    throw new Error('Failed to execute reCAPTCHA verification. Please try again.');
  }
};

/**
 * Renders a reCAPTCHA v2 widget in the specified container
 * 
 * @param containerId - The ID of the HTML element where the widget should be rendered
 * @returns Promise resolving to the widget ID
 */
export const renderRecaptchaV2 = async (containerId: string): Promise<number> => {
  if (!RECAPTCHA_V2_SITE_KEY) {
    throw new Error('reCAPTCHA site key is not configured');
  }

  try {
    // Load the reCAPTCHA script if not already loaded
    await loadRecaptchaScript('v2');

    // Find the container element
    const container = document.getElementById(containerId);
    if (!container) {
      throw new Error(`Container element with ID "${containerId}" not found`);
    }

    // Render the reCAPTCHA widget
    return window.grecaptcha.render(container, {
      sitekey: RECAPTCHA_V2_SITE_KEY,
      theme: 'light',
      size: 'normal'
    });
  } catch (error) {
    console.error('Error rendering reCAPTCHA v2:', error);
    throw new Error('Failed to render reCAPTCHA widget. Please refresh the page and try again.');
  }
};

/**
 * Gets the response token from a rendered reCAPTCHA v2 widget
 * 
 * @param widgetId - The ID of the rendered reCAPTCHA widget
 * @returns The reCAPTCHA token
 */
export const getRecaptchaToken = (widgetId: number): string => {
  if (typeof window === 'undefined' || !window.grecaptcha) {
    throw new Error('reCAPTCHA is not loaded');
  }

  try {
    return window.grecaptcha.getResponse(widgetId);
  } catch (error) {
    console.error('Error getting reCAPTCHA token:', error);
    throw new Error('Failed to get reCAPTCHA verification. Please try again.');
  }
};

/**
 * Resets a reCAPTCHA v2 widget
 * 
 * @param widgetId - The ID of the rendered reCAPTCHA widget
 */
export const resetRecaptcha = (widgetId: number): void => {
  if (typeof window === 'undefined' || !window.grecaptcha) {
    return; // Silently return if grecaptcha is not available
  }

  try {
    window.grecaptcha.reset(widgetId);
  } catch (error) {
    console.error('Error resetting reCAPTCHA:', error);
    // We don't throw here to avoid breaking form resets
  }
};

/**
 * Checks if the reCAPTCHA script has been loaded
 * 
 * @returns True if reCAPTCHA is loaded, false otherwise
 */
export const isRecaptchaLoaded = (): boolean => {
  return typeof window !== 'undefined' && 
         !!window.grecaptcha && 
         typeof window.grecaptcha.ready === 'function';
};