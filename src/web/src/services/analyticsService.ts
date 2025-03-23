import { 
  initializeAnalytics, 
  trackPageView, 
  trackEvent, 
  trackConversion, 
  trackError, 
  setUserProperties, 
  trackServiceInteraction, 
  trackFileUpload, 
  trackFormSubmission, 
  trackImpactStoryView 
} from '../utils/analytics';
import { Metric } from '../lib/analytics';

// Debug mode flag
const DEBUG_MODE = process.env.NODE_ENV === 'development';

/**
 * Interface for the analytics service
 */
interface AnalyticsService {
  initialize: () => Promise<void>;
  trackPageView: (url: string, pageData?: Record<string, any>) => void;
  trackEvent: (category: string, action: string, eventData?: Record<string, any>) => void;
  trackDemoRequest: (formData: Record<string, any>, success: boolean) => void;
  trackQuoteRequest: (formData: Record<string, any>, success: boolean) => void;
  trackContactFormSubmission: (formData: Record<string, any>, success: boolean) => void;
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
 * Initializes the analytics service
 * @returns Promise that resolves when analytics is initialized
 */
const initialize = async (): Promise<void> => {
  await initializeAnalytics();
  if (DEBUG_MODE) {
    console.log('Analytics service initialized successfully');
  }
};

/**
 * Tracks a page view in the analytics system
 * @param url - URL of the page being viewed
 * @param pageData - Additional data about the page
 */
const trackPageViewWrapper = (url: string, pageData: Record<string, any> = {}): void => {
  trackPageView(url, pageData);
  if (DEBUG_MODE) {
    console.log(`Analytics: Tracked page view for ${url}`, pageData);
  }
};

/**
 * Tracks a custom event in the analytics system
 * @param category - Event category
 * @param action - Event action
 * @param eventData - Additional data about the event
 */
const trackEventWrapper = (
  category: string,
  action: string,
  eventData: Record<string, any> = {}
): void => {
  const eventName = `${category}_${action}`;
  trackEvent(eventName, eventData);
  if (DEBUG_MODE) {
    console.log(`Analytics: Tracked event ${eventName}`, eventData);
  }
};

/**
 * Tracks a demo request form submission
 * @param formData - Data from the form submission
 * @param success - Whether the submission was successful
 */
const trackDemoRequest = (
  formData: Record<string, any>,
  success: boolean
): void => {
  trackFormSubmission('demo_request', formData);
  
  if (success) {
    trackConversion('demo_request', formData);
  }
  
  if (DEBUG_MODE) {
    console.log(`Analytics: Tracked demo request ${success ? '(success)' : '(failed)'}`);
  }
};

/**
 * Tracks a quote request form submission
 * @param formData - Data from the form submission
 * @param success - Whether the submission was successful
 */
const trackQuoteRequest = (
  formData: Record<string, any>,
  success: boolean
): void => {
  trackFormSubmission('quote_request', formData);
  
  if (success) {
    trackConversion('quote_request', formData);
  }
  
  if (DEBUG_MODE) {
    console.log(`Analytics: Tracked quote request ${success ? '(success)' : '(failed)'}`);
  }
};

/**
 * Tracks a contact form submission
 * @param formData - Data from the form submission
 * @param success - Whether the submission was successful
 */
const trackContactFormSubmission = (
  formData: Record<string, any>,
  success: boolean
): void => {
  trackFormSubmission('contact_form', formData);
  
  if (success) {
    trackConversion('contact_form', formData);
  }
  
  if (DEBUG_MODE) {
    console.log(`Analytics: Tracked contact form submission ${success ? '(success)' : '(failed)'}`);
  }
};

/**
 * Tracks a file upload event
 * @param fileType - Type of file being uploaded
 * @param fileSize - Size of the file in bytes
 * @param status - Status of the upload (started, success, failed, etc.)
 * @param metadata - Additional metadata about the file
 */
const trackFileUploadWrapper = (
  fileType: string,
  fileSize: number,
  status: string,
  metadata: Record<string, any> = {}
): void => {
  const fileData = {
    type: fileType,
    size: fileSize,
    status,
    ...metadata
  };
  
  trackFileUpload(fileData);
  
  if (status === 'success') {
    trackConversion('file_upload', fileData);
  }
  
  if (DEBUG_MODE) {
    console.log(`Analytics: Tracked file upload (${fileType}, ${fileSize} bytes, ${status})`);
  }
};

/**
 * Tracks when a user views a service detail page
 * @param serviceId - ID of the service
 * @param serviceName - Name of the service
 * @param additionalData - Additional data about the service view
 */
const trackServiceView = (
  serviceId: string,
  serviceName: string,
  additionalData: Record<string, any> = {}
): void => {
  trackServiceInteraction(serviceId, 'view', {
    service_name: serviceName,
    ...additionalData
  });
  
  if (DEBUG_MODE) {
    console.log(`Analytics: Tracked service view for ${serviceName} (${serviceId})`);
  }
};

/**
 * Tracks interactions with service offerings
 * @param serviceId - ID of the service
 * @param interactionType - Type of interaction (click, view, etc.)
 * @param interactionData - Additional data about the interaction
 */
const trackServiceInteractionWrapper = (
  serviceId: string,
  interactionType: string,
  interactionData: Record<string, any> = {}
): void => {
  trackServiceInteraction(serviceId, interactionType, interactionData);
  
  if (DEBUG_MODE) {
    console.log(`Analytics: Tracked service interaction (${serviceId}, ${interactionType})`);
  }
};

/**
 * Tracks when a user views a case study
 * @param caseStudyId - ID of the case study
 * @param caseStudyTitle - Title of the case study
 * @param relatedServices - IDs of services related to the case study
 */
const trackCaseStudyView = (
  caseStudyId: string,
  caseStudyTitle: string,
  relatedServices: string[]
): void => {
  const eventData = {
    case_study_id: caseStudyId,
    case_study_title: caseStudyTitle,
    related_services: relatedServices
  };
  
  trackEvent('case_study_view', eventData);
  
  if (DEBUG_MODE) {
    console.log(`Analytics: Tracked case study view for ${caseStudyTitle} (${caseStudyId})`);
  }
};

/**
 * Tracks when a user views an impact story
 * @param storyId - ID of the impact story
 * @param storyTitle - Title of the impact story
 * @param timeSpent - Time spent viewing the story in seconds
 */
const trackImpactStoryViewWrapper = (
  storyId: string,
  storyTitle: string,
  timeSpent: number
): void => {
  trackImpactStoryView(storyId, storyTitle, timeSpent);
  
  if (DEBUG_MODE) {
    console.log(`Analytics: Tracked impact story view for ${storyTitle} (${timeSpent}s)`);
  }
};

/**
 * Tracks Core Web Vitals performance metrics
 * @param metric - Web Vitals metric object
 */
const trackWebVitals = (metric: Metric): void => {
  const eventData = {
    metric_name: metric.name,
    metric_value: metric.value,
    metric_id: metric.id
  };
  
  trackEvent('web_vitals', eventData);
  
  if (DEBUG_MODE) {
    console.log(`Analytics: Tracked web vital ${metric.name} = ${metric.value}`);
  }
};

/**
 * Tracks error events for monitoring and debugging
 * @param errorType - Type of error
 * @param errorMessage - Error message
 * @param errorContext - Additional context about the error
 */
const trackErrorWrapper = (
  errorType: string,
  errorMessage: string,
  errorContext: Record<string, any> = {}
): void => {
  const errorData = {
    error_type: errorType,
    error_message: errorMessage,
    ...errorContext
  };
  
  trackError(errorData);
  
  if (DEBUG_MODE) {
    console.log(`Analytics: Tracked error ${errorType} - ${errorMessage}`);
  }
};

/**
 * Sets user properties for more detailed analytics
 * @param properties - User properties to set
 */
const setUserPropertiesWrapper = (properties: Record<string, any>): void => {
  setUserProperties(properties);
  
  if (DEBUG_MODE) {
    console.log('Analytics: Set user properties', properties);
  }
};

// Export the analytics service
const analyticsService = {
  initialize,
  trackPageView: trackPageViewWrapper,
  trackEvent: trackEventWrapper,
  trackDemoRequest,
  trackQuoteRequest,
  trackContactFormSubmission,
  trackFileUpload: trackFileUploadWrapper,
  trackServiceView,
  trackServiceInteraction: trackServiceInteractionWrapper,
  trackCaseStudyView,
  trackImpactStoryView: trackImpactStoryViewWrapper,
  trackWebVitals,
  trackError: trackErrorWrapper,
  setUserProperties: setUserPropertiesWrapper
};

export default analyticsService;