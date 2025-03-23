/**
 * Central configuration file that defines all route paths used throughout the IndiVillage website.
 * This provides a single source of truth for navigation URLs, ensuring consistency across the
 * application and making it easier to update route paths when needed.
 */

/**
 * Object containing all route path definitions organized by section
 */
export const ROUTES = {
  /**
   * Home page
   */
  HOME: '/',
  
  /**
   * Services section paths
   */
  SERVICES: {
    /**
     * Services overview page
     */
    INDEX: '/services',
    
    /**
     * Dynamic service detail page with slug parameter
     */
    DETAIL: '/services/[slug]',
    
    /**
     * Specific service pages
     */
    DATA_COLLECTION: '/services/data-collection',
    DATA_PREPARATION: '/services/data-preparation',
    AI_MODEL_DEVELOPMENT: '/services/ai-model-development',
    HUMAN_IN_THE_LOOP: '/services/human-in-the-loop',
  },
  
  /**
   * About section paths
   */
  ABOUT: {
    /**
     * About overview page
     */
    INDEX: '/about',
    
    /**
     * Leadership team page
     */
    LEADERSHIP: '/about/leadership',
    
    /**
     * Careers page
     */
    CAREERS: '/about/careers',
    
    /**
     * Press and media page
     */
    PRESS: '/about/press',
  },
  
  /**
   * Social Impact section paths
   */
  IMPACT: {
    /**
     * Impact overview page
     */
    INDEX: '/impact',
    
    /**
     * Dynamic impact story detail page with slug parameter
     */
    DETAIL: '/impact/[slug]',
    
    /**
     * Foundation page
     */
    FOUNDATION: '/impact/foundation',
    
    /**
     * Sustainability page
     */
    SUSTAINABILITY: '/impact/sustainability',
  },
  
  /**
   * Case Studies section paths
   */
  CASE_STUDIES: {
    /**
     * Case studies overview page
     */
    INDEX: '/case-studies',
    
    /**
     * Dynamic case study detail page with slug parameter
     */
    DETAIL: '/case-studies/[slug]',
  },
  
  /**
   * Blog section paths
   */
  BLOG: {
    /**
     * Blog overview page
     */
    INDEX: '/blog',
    
    /**
     * Dynamic blog post detail page with slug parameter
     */
    DETAIL: '/blog/[slug]',
  },
  
  /**
   * Contact page
   */
  CONTACT: '/contact',
  
  /**
   * Demo request page
   */
  REQUEST_DEMO: '/request-demo',
  
  /**
   * Sample Data Upload section paths
   */
  UPLOAD_SAMPLE: {
    /**
     * Initial upload page
     */
    INDEX: '/upload-sample',
    
    /**
     * Processing status page
     */
    PROCESSING: '/upload-sample/processing',
    
    /**
     * Success confirmation page
     */
    SUCCESS: '/upload-sample/success',
  },
  
  /**
   * Legal section paths
   */
  LEGAL: {
    /**
     * Privacy policy page
     */
    PRIVACY_POLICY: '/legal/privacy-policy',
    
    /**
     * Terms of service page
     */
    TERMS_OF_SERVICE: '/legal/terms-of-service',
    
    /**
     * Cookie policy page
     */
    COOKIE_POLICY: '/legal/cookie-policy',
    
    /**
     * Accessibility statement page
     */
    ACCESSIBILITY: '/legal/accessibility',
  },
} as const;