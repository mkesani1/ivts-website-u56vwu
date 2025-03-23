import React, { 
  createContext, 
  useContext, 
  useState, 
  useEffect, 
  useCallback,
  ReactNode 
} from 'react'; // react@^18.2.0

import analyticsService from '../services/analyticsService';
import { Metric } from '../lib/analytics';

/**
 * Interface defining the analytics context value with all tracking functions
 */
interface AnalyticsContextType {
  isInitialized: boolean;
  trackPageView: (url: string, pageData?: Record<string, any>) => void;
  trackEvent: (category: string, action: string, eventData?: Record<string, any>) => void;
  trackDemoRequest: (formData: Record<string, any>, success: boolean) => void;
  trackQuoteRequest: (formData: Record<string, any>, success: boolean) => void;
  trackContactForm: (formData: Record<string, any>, success: boolean) => void;
  trackFileUpload: (fileType: string, fileSize: number, status: string, metadata?: Record<string, any>) => void;
  trackServiceView: (serviceId: string, serviceName: string, additionalData?: Record<string, any>) => void;
  trackServiceInteraction: (serviceId: string, interactionType: string, interactionData?: Record<string, any>) => void;
  trackCaseStudyView: (caseStudyId: string, caseStudyTitle: string, relatedServices: string[]) => void;
  trackImpactStoryView: (storyId: string, storyTitle: string, timeSpent: number) => void;
  trackWebVitals: (metric: Metric) => void;
  trackError: (errorType: string, errorMessage: string, errorContext?: Record<string, any>) => void;
  setUserProperties: (properties: Record<string, any>) => void;
}

/**
 * Props for the AnalyticsProvider component
 */
interface AnalyticsProviderProps {
  children: ReactNode;
}

/**
 * Context for analytics functionality
 * Use the useAnalyticsContext hook to access this context
 */
const AnalyticsContext = createContext<AnalyticsContextType | undefined>(undefined);

/**
 * Provider component for analytics functionality
 * Initializes analytics service and provides tracking methods to all child components
 */
export const AnalyticsProvider: React.FC<AnalyticsProviderProps> = ({ children }) => {
  // Track initialization state
  const [isInitialized, setIsInitialized] = useState(false);

  // Initialize analytics on component mount
  useEffect(() => {
    const initializeAnalytics = async () => {
      try {
        await analyticsService.initialize();
        setIsInitialized(true);
      } catch (error) {
        console.error('Failed to initialize analytics:', error);
      }
    };

    initializeAnalytics();
  }, []);

  /**
   * Track a page view in analytics
   * @param url URL of the page being viewed
   * @param pageData Additional data about the page
   */
  const trackPageView = useCallback((url: string, pageData?: Record<string, any>) => {
    if (isInitialized) {
      analyticsService.trackPageView(url, pageData);
    }
  }, [isInitialized]);

  /**
   * Track a custom event in analytics
   * @param category Event category
   * @param action Event action
   * @param eventData Additional data about the event
   */
  const trackEvent = useCallback((category: string, action: string, eventData?: Record<string, any>) => {
    if (isInitialized) {
      analyticsService.trackEvent(category, action, eventData);
    }
  }, [isInitialized]);

  /**
   * Track a demo request form submission
   * @param formData Data from the form submission
   * @param success Whether the submission was successful
   */
  const trackDemoRequest = useCallback((formData: Record<string, any>, success: boolean) => {
    if (isInitialized) {
      analyticsService.trackDemoRequest(formData, success);
    }
  }, [isInitialized]);

  /**
   * Track a quote request form submission
   * @param formData Data from the form submission
   * @param success Whether the submission was successful
   */
  const trackQuoteRequest = useCallback((formData: Record<string, any>, success: boolean) => {
    if (isInitialized) {
      analyticsService.trackQuoteRequest(formData, success);
    }
  }, [isInitialized]);

  /**
   * Track a contact form submission
   * @param formData Data from the form submission
   * @param success Whether the submission was successful
   */
  const trackContactForm = useCallback((formData: Record<string, any>, success: boolean) => {
    if (isInitialized) {
      analyticsService.trackContactFormSubmission(formData, success);
    }
  }, [isInitialized]);

  /**
   * Track a file upload event
   * @param fileType Type of file being uploaded
   * @param fileSize Size of the file in bytes
   * @param status Status of the upload (started, success, failed, etc.)
   * @param metadata Additional metadata about the file
   */
  const trackFileUpload = useCallback((
    fileType: string, 
    fileSize: number, 
    status: string, 
    metadata?: Record<string, any>
  ) => {
    if (isInitialized) {
      analyticsService.trackFileUpload(fileType, fileSize, status, metadata);
    }
  }, [isInitialized]);

  /**
   * Track when a user views a service detail page
   * @param serviceId ID of the service
   * @param serviceName Name of the service
   * @param additionalData Additional data about the service view
   */
  const trackServiceView = useCallback((
    serviceId: string, 
    serviceName: string, 
    additionalData?: Record<string, any>
  ) => {
    if (isInitialized) {
      analyticsService.trackServiceView(serviceId, serviceName, additionalData);
    }
  }, [isInitialized]);

  /**
   * Track interactions with service offerings
   * @param serviceId ID of the service
   * @param interactionType Type of interaction (click, view, etc.)
   * @param interactionData Additional data about the interaction
   */
  const trackServiceInteraction = useCallback((
    serviceId: string, 
    interactionType: string, 
    interactionData?: Record<string, any>
  ) => {
    if (isInitialized) {
      analyticsService.trackServiceInteraction(serviceId, interactionType, interactionData);
    }
  }, [isInitialized]);

  /**
   * Track when a user views a case study
   * @param caseStudyId ID of the case study
   * @param caseStudyTitle Title of the case study
   * @param relatedServices IDs of services related to the case study
   */
  const trackCaseStudyView = useCallback((
    caseStudyId: string, 
    caseStudyTitle: string, 
    relatedServices: string[]
  ) => {
    if (isInitialized) {
      analyticsService.trackCaseStudyView(caseStudyId, caseStudyTitle, relatedServices);
    }
  }, [isInitialized]);

  /**
   * Track when a user views an impact story
   * @param storyId ID of the impact story
   * @param storyTitle Title of the impact story
   * @param timeSpent Time spent viewing the story in seconds
   */
  const trackImpactStoryView = useCallback((
    storyId: string, 
    storyTitle: string, 
    timeSpent: number
  ) => {
    if (isInitialized) {
      analyticsService.trackImpactStoryView(storyId, storyTitle, timeSpent);
    }
  }, [isInitialized]);

  /**
   * Track Core Web Vitals performance metrics
   * @param metric Web Vitals metric object
   */
  const trackWebVitals = useCallback((metric: Metric) => {
    if (isInitialized) {
      analyticsService.trackWebVitals(metric);
    }
  }, [isInitialized]);

  /**
   * Track error events for monitoring and debugging
   * @param errorType Type of error
   * @param errorMessage Error message
   * @param errorContext Additional context about the error
   */
  const trackError = useCallback((
    errorType: string, 
    errorMessage: string, 
    errorContext?: Record<string, any>
  ) => {
    if (isInitialized) {
      analyticsService.trackError(errorType, errorMessage, errorContext);
    }
  }, [isInitialized]);

  /**
   * Set user properties for more detailed analytics
   * @param properties User properties to set
   */
  const setUserProperties = useCallback((properties: Record<string, any>) => {
    if (isInitialized) {
      analyticsService.setUserProperties(properties);
    }
  }, [isInitialized]);

  // Create the context value object
  const contextValue: AnalyticsContextType = {
    isInitialized,
    trackPageView,
    trackEvent,
    trackDemoRequest,
    trackQuoteRequest,
    trackContactForm,
    trackFileUpload,
    trackServiceView,
    trackServiceInteraction,
    trackCaseStudyView,
    trackImpactStoryView,
    trackWebVitals,
    trackError,
    setUserProperties
  };

  return (
    <AnalyticsContext.Provider value={contextValue}>
      {children}
    </AnalyticsContext.Provider>
  );
};

/**
 * Custom hook to access the analytics context
 * Must be used within an AnalyticsProvider
 * @returns The analytics context with tracking functions
 * @throws Error if used outside of an AnalyticsProvider
 */
export const useAnalyticsContext = (): AnalyticsContextType => {
  const context = useContext(AnalyticsContext);
  if (context === undefined) {
    throw new Error('useAnalyticsContext must be used within an AnalyticsProvider');
  }
  return context;
};

// Export the context for advanced use cases
export default AnalyticsContext;