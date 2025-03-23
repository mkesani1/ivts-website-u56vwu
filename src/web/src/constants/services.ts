import { ServiceCategory, ServiceCategoryValue } from '../types/content';

/**
 * Detailed information about each service category including title, description, and display order
 * Used for rendering service cards and detail pages throughout the website
 */
export const SERVICE_CATEGORIES = {
  [ServiceCategory.DATA_COLLECTION]: {
    title: 'Data Collection',
    description: 'Comprehensive data gathering solutions',
    order: 1,
  },
  [ServiceCategory.DATA_PREPARATION]: {
    title: 'Data Preparation',
    description: 'Annotation, labeling, and processing',
    order: 2,
  },
  [ServiceCategory.AI_MODEL_DEVELOPMENT]: {
    title: 'AI Model Development',
    description: 'Custom AI model creation and optimization',
    order: 3,
  },
  [ServiceCategory.HUMAN_IN_THE_LOOP]: {
    title: 'Human-in-the-Loop',
    description: 'Human oversight for AI accuracy and quality',
    order: 4,
  },
};

/**
 * Paths to icon images for each service category
 * Used for visual representation in service cards and navigation
 */
export const SERVICE_ICONS = {
  [ServiceCategory.DATA_COLLECTION]: '/images/icons/data-collection.svg',
  [ServiceCategory.DATA_PREPARATION]: '/images/icons/data-preparation.svg',
  [ServiceCategory.AI_MODEL_DEVELOPMENT]: '/images/icons/ai-model.svg',
  [ServiceCategory.HUMAN_IN_THE_LOOP]: '/images/icons/human-in-loop.svg',
};

/**
 * Detailed descriptions for each service category
 * Used on service detail pages and for SEO content
 */
export const SERVICE_DESCRIPTIONS = {
  [ServiceCategory.DATA_COLLECTION]: 'Comprehensive data gathering solutions to collect high-quality data from various sources for AI training and analysis.',
  [ServiceCategory.DATA_PREPARATION]: 'Transform raw data into AI-ready datasets with our comprehensive data preparation services including cleaning, annotation, and validation.',
  [ServiceCategory.AI_MODEL_DEVELOPMENT]: 'Custom AI model development and optimization tailored to your business needs, from concept to deployment.',
  [ServiceCategory.HUMAN_IN_THE_LOOP]: 'Enhance AI accuracy and quality with human oversight and intervention, ensuring optimal results for complex scenarios.',
};

/**
 * Key features for each service category
 * Displayed on service detail pages to highlight capabilities
 */
export const SERVICE_FEATURES = {
  [ServiceCategory.DATA_COLLECTION]: [
    {
      title: 'Web Data Collection',
      description: 'Automated web scraping and data extraction from websites, social media, and online platforms.'
    },
    {
      title: 'Surveys & Feedback',
      description: 'Design and implementation of digital surveys for market research and customer feedback.'
    },
    {
      title: 'Sensor Data Collection',
      description: 'Collection and processing of data from IoT devices and sensors across various environments.'
    },
    {
      title: 'Document Digitization',
      description: 'Conversion of physical documents to digital format with OCR and data extraction.'
    }
  ],
  [ServiceCategory.DATA_PREPARATION]: [
    {
      title: 'Data Annotation',
      description: 'Precise tagging of data elements for AI training.'
    },
    {
      title: 'Data Labeling',
      description: 'Accurate categorization for machine learning models.'
    },
    {
      title: 'Data Cleansing',
      description: 'Removing errors and duplicates from datasets.'
    },
    {
      title: 'Data Validation',
      description: 'Ensuring data quality and consistency.'
    }
  ],
  [ServiceCategory.AI_MODEL_DEVELOPMENT]: [
    {
      title: 'Custom Model Development',
      description: 'Building tailored AI models for specific business problems.'
    },
    {
      title: 'Model Training',
      description: 'Training AI algorithms with your data for optimal performance.'
    },
    {
      title: 'Model Optimization',
      description: 'Fine-tuning models for improved accuracy and efficiency.'
    },
    {
      title: 'Model Deployment',
      description: 'Integrating AI models into your existing systems and workflows.'
    }
  ],
  [ServiceCategory.HUMAN_IN_THE_LOOP]: [
    {
      title: 'Quality Assurance',
      description: 'Human verification and correction of AI outputs for maximum accuracy.'
    },
    {
      title: 'Edge Case Handling',
      description: 'Human intervention for complex scenarios beyond AI capabilities.'
    },
    {
      title: 'Feedback Integration',
      description: 'Incorporating human feedback to continuously improve AI performance.'
    },
    {
      title: 'Continuous Learning',
      description: 'Ongoing model improvement through human oversight and validation.'
    }
  ]
};

/**
 * Process steps for "How It Works" section on service detail pages
 * Visualizes the workflow and methodology for each service
 */
export const HOW_IT_WORKS_STEPS = {
  [ServiceCategory.DATA_COLLECTION]: [
    {
      step: 1,
      title: 'Requirement Analysis',
      description: 'We analyze your data needs and define collection parameters.'
    },
    {
      step: 2,
      title: 'Collection Strategy',
      description: 'We develop a tailored data collection strategy and methodology.'
    },
    {
      step: 3,
      title: 'Data Gathering',
      description: 'Our team executes the collection process with quality controls.'
    },
    {
      step: 4,
      title: 'Delivery & Validation',
      description: 'We deliver the collected data with comprehensive validation reports.'
    }
  ],
  [ServiceCategory.DATA_PREPARATION]: [
    {
      step: 1,
      title: 'Data Receipt',
      description: 'We receive and securely store your raw data.'
    },
    {
      step: 2,
      title: 'Expert Processing',
      description: 'Our specialists clean, annotate, and transform your data.'
    },
    {
      step: 3,
      title: 'Quality Check',
      description: 'Rigorous quality control ensures data accuracy and consistency.'
    },
    {
      step: 4,
      title: 'Delivery & Report',
      description: 'We deliver the prepared data with detailed documentation.'
    }
  ],
  [ServiceCategory.AI_MODEL_DEVELOPMENT]: [
    {
      step: 1,
      title: 'Problem Definition',
      description: 'We define the business problem and AI solution requirements.'
    },
    {
      step: 2,
      title: 'Data Assessment',
      description: 'We evaluate available data and identify additional needs.'
    },
    {
      step: 3,
      title: 'Model Development',
      description: 'Our AI experts develop and train custom models for your needs.'
    },
    {
      step: 4,
      title: 'Testing & Deployment',
      description: 'We rigorously test the model and support its deployment.'
    }
  ],
  [ServiceCategory.HUMAN_IN_THE_LOOP]: [
    {
      step: 1,
      title: 'System Integration',
      description: 'We integrate human review capabilities into your AI workflow.'
    },
    {
      step: 2,
      title: 'Review Protocol',
      description: 'We establish protocols for when and how human intervention occurs.'
    },
    {
      step: 3,
      title: 'Human Verification',
      description: 'Our experts review AI outputs according to established protocols.'
    },
    {
      step: 4,
      title: 'Continuous Improvement',
      description: 'Human feedback is used to continuously improve the AI system.'
    }
  ]
};

/**
 * Supported file types for sample data upload for each service category
 * Used to validate and filter files in the upload component
 */
export const SUPPORTED_FILE_TYPES = {
  [ServiceCategory.DATA_COLLECTION]: [
    'CSV', 'JSON', 'XML', 'TXT', 'XLSX', 'PDF'
  ],
  [ServiceCategory.DATA_PREPARATION]: [
    'CSV', 'JSON', 'XML', 'Images (JPG, PNG, TIFF)', 'Audio (MP3, WAV)', 'Text (TXT, PDF)'
  ],
  [ServiceCategory.AI_MODEL_DEVELOPMENT]: [
    'CSV', 'JSON', 'TXT', 'Images (JPG, PNG)', 'Audio (MP3, WAV)', 'Structured Data Files'
  ],
  [ServiceCategory.HUMAN_IN_THE_LOOP]: [
    'CSV', 'JSON', 'Images (JPG, PNG)', 'Text Documents', 'Audio Samples', 'Video Clips'
  ]
};

/**
 * Helper function to get service information by category
 * Consolidates all information about a service category into a single object
 * 
 * @param category - The service category to retrieve information for
 * @returns Service information including title, description, icon, and features
 */
export const getServiceByCategory = (category: ServiceCategoryValue) => {
  if (!category || !SERVICE_CATEGORIES[category]) {
    return null;
  }
  
  return {
    ...SERVICE_CATEGORIES[category],
    icon: SERVICE_ICONS[category],
    description: SERVICE_DESCRIPTIONS[category],
    features: SERVICE_FEATURES[category],
    howItWorksSteps: HOW_IT_WORKS_STEPS[category],
    supportedFileTypes: SUPPORTED_FILE_TYPES[category]
  };
};