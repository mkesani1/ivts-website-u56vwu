import { Metric } from 'web-vitals'; // web-vitals@^3.0.0
import { getCLS, getFID, getLCP, getFCP, getTTFB } from 'web-vitals'; // web-vitals@^3.0.0

// Global declarations for Google Analytics
declare global {
  interface Window {
    gtag: (
      command: 'config' | 'set' | 'event',
      targetId: string,
      config?: Record<string, any> | undefined
    ) => void;
    dataLayer: any[];
  }
}

// Constants
const DEBUG_MODE = process.env.NODE_ENV === 'development';
const GA_MEASUREMENT_ID = process.env.NEXT_PUBLIC_GA_MEASUREMENT_ID;

// Interfaces
export interface AnalyticsEventData {
  event_category?: string;
  event_label?: string;
  value?: number;
  non_interaction?: boolean;
  [key: string]: any;
}

export interface AnalyticsPageViewData {
  page_title?: string;
  page_location?: string;
  page_path?: string;
  [key: string]: any;
}

// Tracking state
let isAnalyticsInitialized = false;

/**
 * Initializes analytics tracking by setting up Google Analytics and other tracking services
 * @returns Promise that resolves when analytics is initialized
 */
export const initializeAnalytics = async (): Promise<void> => {
  if (isAnalyticsInitialized) {
    return;
  }

  try {
    if (!DEBUG_MODE && GA_MEASUREMENT_ID) {
      // Load Google Analytics script
      await loadGoogleAnalytics();

      // Initialize Google Analytics
      window.dataLayer = window.dataLayer || [];
      window.gtag = function gtag() {
        window.dataLayer.push(arguments);
      };
      window.gtag('config', GA_MEASUREMENT_ID, {
        send_page_view: false // We'll track page views manually
      });

      // Setup web vitals tracking
      setupWebVitalsTracking();

      // Setup error tracking
      setupErrorTracking();

      isAnalyticsInitialized = true;
      if (DEBUG_MODE) {
        console.log('🔍 Analytics initialized successfully');
      }
    } else if (DEBUG_MODE) {
      // In development mode, we'll just log analytics events
      isAnalyticsInitialized = true;
      console.log('🔍 Analytics initialized in debug mode');
    }
  } catch (error) {
    console.error('Failed to initialize analytics:', error);
    // Still mark as initialized to prevent repeated attempts
    isAnalyticsInitialized = true;
  }
};

/**
 * Loads the Google Analytics script
 * @returns Promise that resolves when script is loaded
 */
const loadGoogleAnalytics = (): Promise<void> => {
  return new Promise((resolve, reject) => {
    if (document.querySelector(`script[src*="googletagmanager.com/gtag/js"]`)) {
      resolve();
      return;
    }

    const script = document.createElement('script');
    script.src = `https://www.googletagmanager.com/gtag/js?id=${GA_MEASUREMENT_ID}`;
    script.async = true;
    script.onload = () => resolve();
    script.onerror = () => reject(new Error('Failed to load Google Analytics'));
    document.head.appendChild(script);
  });
};

/**
 * Sets up tracking for Web Vitals metrics
 */
const setupWebVitalsTracking = (): void => {
  const reportWebVital = ({ name, delta, id }: Metric): void => {
    trackEvent('web_vitals', {
      event_category: 'Web Vitals',
      event_label: name,
      value: Math.round(name === 'CLS' ? delta * 1000 : delta),
      metric_id: id,
      non_interaction: true
    });
  };

  getCLS(reportWebVital);
  getFID(reportWebVital);
  getLCP(reportWebVital);
  getFCP(reportWebVital);
  getTTFB(reportWebVital);
};

/**
 * Sets up global error tracking
 */
const setupErrorTracking = (): void => {
  window.addEventListener('error', (event) => {
    trackError({
      error_type: 'uncaught_error',
      error_message: event.message,
      error_stack: event.error?.stack,
      error_source: event.filename,
      error_line: event.lineno,
      error_column: event.colno
    });
  });

  window.addEventListener('unhandledrejection', (event) => {
    trackError({
      error_type: 'unhandled_promise_rejection',
      error_message: event.reason?.message || String(event.reason),
      error_stack: event.reason?.stack,
      error_source: 'promise_rejection'
    });
  });
};

/**
 * Tracks a page view in the analytics system
 * @param url - The URL of the page being viewed
 * @param pageData - Additional data about the page view
 */
export const trackPageView = (
  url: string,
  pageData: Record<string, any> = {}
): void => {
  if (!isAnalyticsInitialized) {
    if (DEBUG_MODE) {
      console.warn('Analytics not initialized. Call initializeAnalytics first.');
    }
    return;
  }

  const cleanPageData = sanitizeAnalyticsData({
    page_path: url,
    page_location: typeof window !== 'undefined' ? window.location.href : url,
    page_title: typeof document !== 'undefined' ? document.title : '',
    ...pageData
  });

  if (!DEBUG_MODE && GA_MEASUREMENT_ID && typeof window !== 'undefined') {
    window.gtag('event', 'page_view', cleanPageData);
  }

  logAnalyticsEvent('page_view', cleanPageData);
};

/**
 * Tracks a custom event in the analytics system
 * @param eventName - Name of the event to track
 * @param eventData - Additional data about the event
 */
export const trackEvent = (
  eventName: string,
  eventData: Record<string, any> = {}
): void => {
  if (!isAnalyticsInitialized) {
    if (DEBUG_MODE) {
      console.warn('Analytics not initialized. Call initializeAnalytics first.');
    }
    return;
  }

  const cleanEventData = sanitizeAnalyticsData(eventData);

  if (!DEBUG_MODE && GA_MEASUREMENT_ID && typeof window !== 'undefined') {
    window.gtag('event', eventName, cleanEventData);
  }

  logAnalyticsEvent(eventName, cleanEventData);
};

/**
 * Tracks a conversion event (e.g., form submission, signup)
 * @param conversionType - Type of conversion (demo_request, quote_request, etc.)
 * @param conversionData - Additional data about the conversion
 */
export const trackConversion = (
  conversionType: string,
  conversionData: Record<string, any> = {}
): void => {
  if (!isAnalyticsInitialized) {
    if (DEBUG_MODE) {
      console.warn('Analytics not initialized. Call initializeAnalytics first.');
    }
    return;
  }

  // Format conversion event name
  const eventName = `conversion_${conversionType}`;
  
  const cleanConversionData = sanitizeAnalyticsData({
    event_category: 'Conversion',
    event_label: conversionType,
    ...conversionData
  });

  if (!DEBUG_MODE && GA_MEASUREMENT_ID && typeof window !== 'undefined') {
    window.gtag('event', eventName, cleanConversionData);
  }

  logAnalyticsEvent(eventName, cleanConversionData);
};

/**
 * Tracks interactions with service offerings (view, click, etc.)
 * @param serviceId - ID of the service being interacted with
 * @param interactionType - Type of interaction (view, click, etc.)
 * @param interactionData - Additional data about the interaction
 */
export const trackServiceInteraction = (
  serviceId: string,
  interactionType: string,
  interactionData: Record<string, any> = {}
): void => {
  if (!isAnalyticsInitialized) {
    if (DEBUG_MODE) {
      console.warn('Analytics not initialized. Call initializeAnalytics first.');
    }
    return;
  }

  const eventData = {
    event_category: 'Service Interaction',
    event_label: serviceId,
    interaction_type: interactionType,
    service_id: serviceId,
    ...interactionData
  };

  trackEvent('service_interaction', eventData);
};

/**
 * Tracks file upload events with metadata
 * @param fileData - Data about the file being uploaded
 */
export const trackFileUpload = (fileData: Record<string, any>): void => {
  if (!isAnalyticsInitialized) {
    if (DEBUG_MODE) {
      console.warn('Analytics not initialized. Call initializeAnalytics first.');
    }
    return;
  }

  const eventData = {
    event_category: 'File Upload',
    file_type: fileData.type || 'unknown',
    file_size: fileData.size || 0,
    file_name: fileData.name ? fileData.name.split('.').pop() : 'unknown', // Just get extension to avoid PII
    upload_status: fileData.status || 'started',
    ...fileData
  };

  trackEvent('file_upload', eventData);
};

/**
 * Tracks form submission events (contact, demo request, quote)
 * @param formType - Type of form being submitted
 * @param formData - Data from the submitted form (will be sanitized)
 */
export const trackFormSubmission = (
  formType: string,
  formData: Record<string, any> = {}
): void => {
  if (!isAnalyticsInitialized) {
    if (DEBUG_MODE) {
      console.warn('Analytics not initialized. Call initializeAnalytics first.');
    }
    return;
  }

  // For forms, we want to be extra careful about sanitizing the data
  const sanitizedFormData = sanitizeAnalyticsData(formData);
  
  const eventData = {
    event_category: 'Form Submission',
    event_label: formType,
    form_type: formType,
    ...sanitizedFormData
  };

  trackEvent('form_submission', eventData);
  
  // Also track as a conversion event
  trackConversion(formType, sanitizedFormData);
};

/**
 * Tracks when users view impact stories
 * @param storyId - ID of the story being viewed
 * @param storyTitle - Title of the story
 * @param timeSpent - Time spent viewing the story in seconds
 */
export const trackImpactStoryView = (
  storyId: string,
  storyTitle: string,
  timeSpent: number = 0
): void => {
  if (!isAnalyticsInitialized) {
    if (DEBUG_MODE) {
      console.warn('Analytics not initialized. Call initializeAnalytics first.');
    }
    return;
  }

  const eventData = {
    event_category: 'Social Impact',
    event_label: storyTitle,
    story_id: storyId,
    story_title: storyTitle,
    time_spent: timeSpent,
    value: Math.round(timeSpent) // GA uses value as an integer
  };

  trackEvent('impact_story_view', eventData);
};

/**
 * Tracks error events for monitoring and debugging
 * @param errorData - Data about the error
 */
export const trackError = (errorData: Record<string, any>): void => {
  if (!isAnalyticsInitialized) {
    if (DEBUG_MODE) {
      console.warn('Analytics not initialized. Call initializeAnalytics first.');
    }
    // For errors, we should still log them even if analytics isn't initialized
    console.error('Analytics Error:', errorData);
    return;
  }

  // Make sure we don't include any sensitive data in error reports
  const sanitizedErrorData = sanitizeAnalyticsData({
    event_category: 'Error',
    event_label: errorData.error_type || 'general_error',
    non_interaction: true,
    ...errorData
  });

  if (!DEBUG_MODE && GA_MEASUREMENT_ID && typeof window !== 'undefined') {
    window.gtag('event', 'error', sanitizedErrorData);
  }

  logAnalyticsEvent('error', sanitizedErrorData);
};

/**
 * Sets user properties for more detailed analytics
 * @param properties - User properties to set
 */
export const setUserProperties = (properties: Record<string, any>): void => {
  if (!isAnalyticsInitialized) {
    if (DEBUG_MODE) {
      console.warn('Analytics not initialized. Call initializeAnalytics first.');
    }
    return;
  }

  // Sanitize user properties to ensure no PII is included
  const sanitizedProperties = sanitizeAnalyticsData(properties);

  if (!DEBUG_MODE && GA_MEASUREMENT_ID && typeof window !== 'undefined') {
    window.gtag('set', 'user_properties', sanitizedProperties);
  }

  logAnalyticsEvent('set_user_properties', sanitizedProperties);
};

/**
 * Removes sensitive information from data before sending to analytics
 * @param data - Data object to sanitize
 * @returns Sanitized data object
 */
export const sanitizeAnalyticsData = (data: Record<string, any>): Record<string, any> => {
  if (!data || typeof data !== 'object') {
    return data;
  }

  const sanitized = { ...data };
  
  // List of fields that might contain PII
  const sensitiveFields = [
    'email', 'phone', 'address', 'name', 'firstName', 'lastName', 'fullName', 
    'password', 'creditCard', 'ssn', 'socialSecurity', 'dob', 'dateOfBirth',
    'passport', 'license', 'ip', 'ipAddress'
  ];
  
  // Email regex pattern
  const emailPattern = /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/;
  
  // Phone regex pattern (simple version)
  const phonePattern = /(\+\d{1,3})?[\s.-]?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}/;
  
  // Process all properties
  Object.keys(sanitized).forEach(key => {
    // Check if this is a sensitive field
    if (sensitiveFields.some(field => key.toLowerCase().includes(field.toLowerCase()))) {
      sanitized[key] = '[REDACTED]';
    } 
    // Check if the value looks like an email
    else if (typeof sanitized[key] === 'string' && emailPattern.test(sanitized[key])) {
      sanitized[key] = '[REDACTED EMAIL]';
    }
    // Check if the value looks like a phone number
    else if (typeof sanitized[key] === 'string' && phonePattern.test(sanitized[key])) {
      sanitized[key] = '[REDACTED PHONE]';
    }
    // Recursively sanitize nested objects
    else if (typeof sanitized[key] === 'object' && sanitized[key] !== null) {
      sanitized[key] = sanitizeAnalyticsData(sanitized[key]);
    }
  });
  
  return sanitized;
};

/**
 * Logs analytics events in development mode for debugging
 * @param eventType - Type of event being tracked
 * @param eventData - Data about the event
 */
export const logAnalyticsEvent = (
  eventType: string,
  eventData: Record<string, any> = {}
): void => {
  if (DEBUG_MODE) {
    console.log(
      `%c Analytics: ${eventType} %c`,
      'background: #0055A4; color: white; padding: 2px 4px; border-radius: 3px 0 0 3px;',
      'background: #FF671F; color: white; padding: 2px 4px; border-radius: 0 3px 3px 0;',
      eventData
    );
  }
};

export default {
  initializeAnalytics,
  trackPageView,
  trackEvent,
  trackConversion,
  trackServiceInteraction,
  trackFileUpload,
  trackFormSubmission,
  trackImpactStoryView,
  trackError,
  setUserProperties
};