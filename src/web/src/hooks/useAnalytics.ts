import { useCallback } from 'react'; // react@^18.2.0
import { useAnalyticsContext } from '../context/AnalyticsContext';

/**
 * Interface for the object returned by the useAnalytics hook
 */
interface UseAnalyticsReturn {
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
  trackError: (errorType: string, errorMessage: string, errorContext?: Record<string, any>) => void;
  setUserProperties: (properties: Record<string, any>) => void;
  isInitialized: boolean;
}

/**
 * Custom hook that provides analytics tracking functionality
 * This hook abstracts the analytics context implementation, making it easier to
 * track user interactions, page views, form submissions, and other business events
 * from any component.
 * 
 * @returns Object containing analytics tracking functions
 */
const useAnalytics = (): UseAnalyticsReturn => {
  // Get the analytics context
  const analytics = useAnalyticsContext();
  
  // Memoize tracking functions
  const trackPageView = useCallback((url: string, pageData?: Record<string, any>) => {
    analytics.trackPageView(url, pageData);
  }, [analytics]);
  
  const trackEvent = useCallback((category: string, action: string, eventData?: Record<string, any>) => {
    analytics.trackEvent(category, action, eventData);
  }, [analytics]);
  
  const trackDemoRequest = useCallback((formData: Record<string, any>, success: boolean) => {
    analytics.trackDemoRequest(formData, success);
  }, [analytics]);
  
  const trackQuoteRequest = useCallback((formData: Record<string, any>, success: boolean) => {
    analytics.trackQuoteRequest(formData, success);
  }, [analytics]);
  
  const trackContactForm = useCallback((formData: Record<string, any>, success: boolean) => {
    analytics.trackContactForm(formData, success);
  }, [analytics]);
  
  const trackFileUpload = useCallback((fileType: string, fileSize: number, status: string, metadata?: Record<string, any>) => {
    analytics.trackFileUpload(fileType, fileSize, status, metadata);
  }, [analytics]);
  
  const trackServiceView = useCallback((serviceId: string, serviceName: string, additionalData?: Record<string, any>) => {
    analytics.trackServiceView(serviceId, serviceName, additionalData);
  }, [analytics]);
  
  const trackServiceInteraction = useCallback((serviceId: string, interactionType: string, interactionData?: Record<string, any>) => {
    analytics.trackServiceInteraction(serviceId, interactionType, interactionData);
  }, [analytics]);
  
  const trackCaseStudyView = useCallback((caseStudyId: string, caseStudyTitle: string, relatedServices: string[]) => {
    analytics.trackCaseStudyView(caseStudyId, caseStudyTitle, relatedServices);
  }, [analytics]);
  
  const trackImpactStoryView = useCallback((storyId: string, storyTitle: string, timeSpent: number) => {
    analytics.trackImpactStoryView(storyId, storyTitle, timeSpent);
  }, [analytics]);
  
  const trackError = useCallback((errorType: string, errorMessage: string, errorContext?: Record<string, any>) => {
    analytics.trackError(errorType, errorMessage, errorContext);
  }, [analytics]);
  
  const setUserProperties = useCallback((properties: Record<string, any>) => {
    analytics.setUserProperties(properties);
  }, [analytics]);
  
  // Return object with all tracking functions
  return {
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
    trackError,
    setUserProperties,
    isInitialized: analytics.isInitialized
  };
};

export default useAnalytics;