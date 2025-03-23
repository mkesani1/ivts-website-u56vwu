import { Metric } from 'web-vitals'; // web-vitals ^3.0.0

// Configuration
const GA_MEASUREMENT_ID = process.env.NEXT_PUBLIC_GA_MEASUREMENT_ID;
const DEBUG_MODE = process.env.NODE_ENV === 'development';
let isAnalyticsInitialized = false;

// Type definitions
interface AnalyticsEventData {
  event_category?: string;
  event_label?: string;
  value?: number;
  non_interaction?: boolean;
  [key: string]: any;
}

interface AnalyticsPageViewData {
  page_title?: string;
  page_location?: string;
  page_path?: string;
  [key: string]: any;
}

interface WebVitalsMetric {
  name: string;
  value: number;
  id: string;
  delta: number;
}

// Declare gtag function for TypeScript
declare global {
  interface Window {
    gtag: (
      command: 'config' | 'event' | 'set' | 'consent' | 'js',
      targetId: string | Date,
      config?: Record<string, any>
    ) => void;
  }
}

/**
 * Dynamically loads the Google Analytics script
 * @returns Promise that resolves when the script is loaded
 */
export function loadGoogleAnalytics(): Promise<void> {
  return new Promise((resolve, reject) => {
    if (typeof window === 'undefined') {
      // Don't load during SSR
      resolve();
      return;
    }

    // Check if script already exists
    if (document.querySelector(`script[src*="googletagmanager.com/gtag/js"]`)) {
      resolve();
      return;
    }

    try {
      // Create script element
      const script = document.createElement('script');
      script.async = true;
      script.src = `https://www.googletagmanager.com/gtag/js?id=${GA_MEASUREMENT_ID}`;
      
      // Set up load and error handlers
      script.onload = () => {
        // Initialize the global gtag function
        window.dataLayer = window.dataLayer || [];
        function gtag(...args: any[]) {
          window.dataLayer.push(arguments);
        }
        window.gtag = window.gtag || gtag;
        
        // Initialize gtag
        window.gtag('js', new Date());
        
        resolve();
      };
      script.onerror = () => {
        reject(new Error('Failed to load Google Analytics script'));
      };
      
      // Add script to document
      document.head.appendChild(script);
    } catch (error) {
      reject(error);
    }
  });
}

/**
 * Initializes Google Analytics with configuration parameters
 * @returns Promise that resolves when analytics is initialized
 */
export async function initializeAnalytics(): Promise<void> {
  if (isAnalyticsInitialized) {
    return;
  }

  if (!GA_MEASUREMENT_ID) {
    if (DEBUG_MODE) {
      console.warn('Google Analytics Measurement ID is not defined. Analytics will not be initialized.');
    }
    return;
  }

  try {
    // Load the Google Analytics script
    await loadGoogleAnalytics();

    // Configure GA with the measurement ID
    if (typeof window !== 'undefined' && window.gtag) {
      window.gtag('config', GA_MEASUREMENT_ID, {
        send_page_view: false, // We'll handle page views manually for more control
        anonymize_ip: true,
        cookie_flags: 'SameSite=None;Secure',
        cookie_domain: window.location.hostname,
        custom_map: {
          dimension1: 'service_interest',
          dimension2: 'user_role',
          dimension3: 'device_type',
        }
      });

      isAnalyticsInitialized = true;
      logAnalyticsAction('Analytics Initialized', { measurementId: GA_MEASUREMENT_ID });
    }
  } catch (error) {
    console.error('Failed to initialize analytics:', error);
  }
}

/**
 * Tracks a page view in Google Analytics
 * @param url The URL of the page
 * @param pageData Additional data to send with the page view
 */
export function trackPageView(url: string, pageData: Record<string, any> = {}): void {
  if (!isAnalyticsAvailable()) {
    return;
  }

  try {
    const sanitizedData = sanitizeAnalyticsData(pageData);
    const data: AnalyticsPageViewData = {
      page_path: url,
      page_location: typeof window !== 'undefined' ? window.location.href : url,
      page_title: typeof document !== 'undefined' ? document.title : '',
      ...sanitizedData
    };

    window.gtag('event', 'page_view', data);
    logAnalyticsAction('Page View', data);
  } catch (error) {
    console.error('Error tracking page view:', error);
  }
}

/**
 * Tracks a custom event in Google Analytics
 * @param eventName The name of the event
 * @param eventData Additional data to send with the event
 */
export function trackEvent(eventName: string, eventData: Record<string, any> = {}): void {
  if (!isAnalyticsAvailable()) {
    return;
  }

  try {
    const sanitizedData = sanitizeAnalyticsData(eventData);
    window.gtag('event', eventName, sanitizedData);
    logAnalyticsAction('Event', { name: eventName, ...sanitizedData });
  } catch (error) {
    console.error('Error tracking event:', error);
  }
}

/**
 * Tracks Core Web Vitals metrics in Google Analytics
 * @param metric The web vitals metric to track
 */
export function trackWebVitals(metric: Metric): void {
  if (!isAnalyticsAvailable()) {
    return;
  }

  try {
    // Format the metric data for GA
    const data = {
      name: metric.name,
      value: metric.value,
      id: metric.id,
      delta: metric.delta
    };
    
    // Send as a web_vitals event
    window.gtag('event', 'web_vitals', {
      event_category: 'Web Vitals',
      event_label: metric.name,
      value: Math.round(metric.value * 1000) / 1000, // Send value with 3 decimal points
      metric_id: metric.id,
      metric_value: metric.value,
      metric_delta: metric.delta,
      non_interaction: true, // Doesn't affect bounce rate
    });
    
    logAnalyticsAction('Web Vitals', data);
  } catch (error) {
    console.error('Error tracking web vitals:', error);
  }
}

/**
 * Sets user properties for more detailed analytics
 * @param properties The user properties to set
 */
export function setUserProperties(properties: Record<string, any>): void {
  if (!isAnalyticsAvailable()) {
    return;
  }

  try {
    const sanitizedProps = sanitizeAnalyticsData(properties);
    window.gtag('set', 'user_properties', sanitizedProps);
    logAnalyticsAction('User Properties', sanitizedProps);
  } catch (error) {
    console.error('Error setting user properties:', error);
  }
}

/**
 * Checks if Google Analytics is available and initialized
 * @returns True if analytics is available, false otherwise
 */
export function isAnalyticsAvailable(): boolean {
  return (
    typeof window !== 'undefined' && 
    typeof window.gtag === 'function' && 
    isAnalyticsInitialized
  );
}

/**
 * Removes sensitive information from data before sending to analytics
 * @param data The data object to sanitize
 * @returns Sanitized data object
 */
function sanitizeAnalyticsData(data: Record<string, any>): Record<string, any> {
  if (!data) return {};
  
  // Create a deep copy of the data
  const sanitized = JSON.parse(JSON.stringify(data));
  
  const sensitivePatterns = [
    // Email pattern
    /^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$/,
    // Phone pattern
    /(\+\d{1,3}[- ]?)?\(?\d{3}\)?[- ]?\d{3}[- ]?\d{4}/,
    // Credit card pattern
    /\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}/,
    // Social security number pattern
    /\d{3}[- ]?\d{2}[- ]?\d{4}/
  ];

  // Function to recursively sanitize objects
  function sanitizeObject(obj: Record<string, any>): Record<string, any> {
    for (const key in obj) {
      if (typeof obj[key] === 'object' && obj[key] !== null) {
        sanitizeObject(obj[key]);
      } else if (typeof obj[key] === 'string') {
        // Check against sensitive patterns
        for (const pattern of sensitivePatterns) {
          if (pattern.test(obj[key])) {
            obj[key] = '[REDACTED]';
            break;
          }
        }
        
        // Check explicitly for known sensitive field names
        const sensitiveFields = ['password', 'token', 'secret', 'api_key', 'apikey', 'api-key', 'auth'];
        if (sensitiveFields.includes(key.toLowerCase())) {
          obj[key] = '[REDACTED]';
        }
      }
    }
    
    return obj;
  }
  
  return sanitizeObject(sanitized);
}

/**
 * Logs analytics actions in development mode for debugging
 * @param action The analytics action type
 * @param data The data associated with the action
 */
function logAnalyticsAction(action: string, data: Record<string, any>): void {
  if (!DEBUG_MODE) {
    return;
  }
  
  const styles = 'color: #0055A4; font-weight: bold;';
  console.groupCollapsed(`%c Analytics: ${action}`, styles);
  console.log('Data:', data);
  console.log('Timestamp:', new Date().toISOString());
  console.groupEnd();
}

// Initialize analytics on module load if not in SSR context
if (typeof window !== 'undefined') {
  // Defer initialization to not block page load
  setTimeout(() => {
    initializeAnalytics().catch(err => {
      console.error('Failed to initialize analytics:', err);
    });
  }, 0);
}