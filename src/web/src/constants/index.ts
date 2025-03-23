/**
 * Central export file for all constants used throughout the IndiVillage website.
 * 
 * This file aggregates and re-exports constants from various domain-specific 
 * constant files to provide a single import point, ensuring consistency across 
 * the application and simplifying imports.
 * 
 * @version 1.0.0
 */

// API Endpoints
export { API_ENDPOINTS } from './apiEndpoints';

// Impact-related constants
export { 
  IMPACT_METRICS,
  IMPACT_CATEGORIES,
  SUSTAINABLE_DEVELOPMENT_GOALS,
  IMPACT_STORY_TYPES
} from './impact';

// Route path constants
export { ROUTES } from './routes';

// Service-related constants
export {
  SERVICE_CATEGORIES,
  SERVICE_FEATURES,
  SERVICE_ICONS,
  SERVICE_DESCRIPTIONS,
  HOW_IT_WORKS_STEPS,
  SUPPORTED_FILE_TYPES,
  getServiceByCategory
} from './services';

// Validation message constants
export { VALIDATION_MESSAGES } from './validationMessages';