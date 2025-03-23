import {
  Service,
  ServiceFeature,
  Industry,
  CaseStudy,
  CaseStudyResult,
  Location,
  ImpactStory,
  ImpactMetric,
  UploadStatus
} from '../../src/types/api';
import {
  ContactFormData,
  DemoRequestFormData,
  QuoteRequestFormData,
  UploadFormData
} from '../../src/types/forms';
import { FileType } from '../../src/types/upload';

/**
 * Mock data for AI services including data collection, data preparation,
 * AI model development, and human-in-the-loop services
 */
export const mockServices: Service[] = [
  {
    id: 'srv-001',
    name: 'Data Collection',
    slug: 'data-collection',
    description: 'Comprehensive data gathering solutions for AI and machine learning applications.',
    icon: 'data-collection-icon',
    order: 1,
    features: [], // Will be populated with references to mockServiceFeatures
    case_studies: [], // Will be populated with references to mockCaseStudies
    created_at: '2023-01-15T08:00:00Z',
    updated_at: '2023-04-10T14:30:00Z'
  },
  {
    id: 'srv-002',
    name: 'Data Preparation',
    slug: 'data-preparation',
    description: 'Annotation, labeling, and processing services to prepare your data for AI training.',
    icon: 'data-preparation-icon',
    order: 2,
    features: [],
    case_studies: [],
    created_at: '2023-01-15T08:15:00Z',
    updated_at: '2023-04-10T14:35:00Z'
  },
  {
    id: 'srv-003',
    name: 'AI Model Development',
    slug: 'ai-model-development',
    description: 'Custom AI model creation and optimization to solve your specific business challenges.',
    icon: 'ai-model-development-icon',
    order: 3,
    features: [],
    case_studies: [],
    created_at: '2023-01-15T08:30:00Z',
    updated_at: '2023-04-10T14:40:00Z'
  },
  {
    id: 'srv-004',
    name: 'Human-in-the-Loop',
    slug: 'human-in-the-loop',
    description: 'Combining human intelligence with AI automation for superior accuracy and quality.',
    icon: 'human-in-the-loop-icon',
    order: 4,
    features: [],
    case_studies: [],
    created_at: '2023-01-15T08:45:00Z',
    updated_at: '2023-04-10T14:45:00Z'
  }
];

/**
 * Mock data for service features associated with each service
 */
export const mockServiceFeatures: ServiceFeature[] = [
  // Data Collection features
  {
    id: 'feat-001',
    service_id: 'srv-001',
    title: 'Web Data Collection',
    description: 'Automated collection of publicly available web data for training AI models.',
    order: 1
  },
  {
    id: 'feat-002',
    service_id: 'srv-001',
    title: 'Survey & Form Data',
    description: 'Design and implementation of surveys and forms to collect structured data.',
    order: 2
  },
  {
    id: 'feat-003',
    service_id: 'srv-001',
    title: 'Custom Data Sources',
    description: 'Integration with your existing systems and databases to extract valuable data.',
    order: 3
  },

  // Data Preparation features
  {
    id: 'feat-004',
    service_id: 'srv-002',
    title: 'Data Annotation',
    description: 'Precise tagging of data elements for AI training across various formats.',
    order: 1
  },
  {
    id: 'feat-005',
    service_id: 'srv-002',
    title: 'Data Labeling',
    description: 'Accurate categorization and labeling of data for supervised learning models.',
    order: 2
  },
  {
    id: 'feat-006',
    service_id: 'srv-002',
    title: 'Data Cleansing',
    description: 'Removing errors, duplicates, and inconsistencies from datasets to improve quality.',
    order: 3
  },
  {
    id: 'feat-007',
    service_id: 'srv-002',
    title: 'Data Validation',
    description: 'Ensuring data quality and consistency through comprehensive validation processes.',
    order: 4
  },

  // AI Model Development features
  {
    id: 'feat-008',
    service_id: 'srv-003',
    title: 'Custom Model Creation',
    description: 'Building specialized AI models tailored to your unique business requirements.',
    order: 1
  },
  {
    id: 'feat-009',
    service_id: 'srv-003',
    title: 'Model Training & Optimization',
    description: 'Fine-tuning models for peak performance and efficiency using advanced techniques.',
    order: 2
  },
  {
    id: 'feat-010',
    service_id: 'srv-003',
    title: 'Model Deployment',
    description: 'Seamless integration of AI models into your existing systems and workflows.',
    order: 3
  },
  {
    id: 'feat-011',
    service_id: 'srv-003',
    title: 'Performance Monitoring',
    description: 'Continuous monitoring and improvement of deployed AI models over time.',
    order: 4
  },

  // Human-in-the-Loop features
  {
    id: 'feat-012',
    service_id: 'srv-004',
    title: 'Human Verification',
    description: 'Expert human review of AI-generated results to ensure accuracy and quality.',
    order: 1
  },
  {
    id: 'feat-013',
    service_id: 'srv-004',
    title: 'Edge Case Handling',
    description: 'Specialized human intervention for complex cases that AI cannot resolve.',
    order: 2
  },
  {
    id: 'feat-014',
    service_id: 'srv-004',
    title: 'Continuous Learning',
    description: 'Feedback loop between human experts and AI systems for ongoing improvement.',
    order: 3
  },
  {
    id: 'feat-015',
    service_id: 'srv-004',
    title: 'Quality Assurance',
    description: 'Multi-level quality checks combining automated and human verification processes.',
    order: 4
  }
];

/**
 * Mock data for industries like healthcare, retail, finance, etc.
 */
export const mockIndustries: Industry[] = [
  {
    id: 'ind-001',
    name: 'Healthcare',
    slug: 'healthcare'
  },
  {
    id: 'ind-002',
    name: 'Retail & E-commerce',
    slug: 'retail-ecommerce'
  },
  {
    id: 'ind-003',
    name: 'Financial Services',
    slug: 'financial-services'
  },
  {
    id: 'ind-004',
    name: 'Manufacturing',
    slug: 'manufacturing'
  },
  {
    id: 'ind-005',
    name: 'Transportation & Logistics',
    slug: 'transportation-logistics'
  },
  {
    id: 'ind-006',
    name: 'Technology',
    slug: 'technology'
  }
];

/**
 * Mock data for case studies showcasing successful client implementations
 */
export const mockCaseStudies: CaseStudy[] = [
  {
    id: 'cs-001',
    title: 'E-commerce Product Categorization',
    slug: 'ecommerce-product-categorization',
    client: 'GlobalShop',
    challenge: 'With over 1 million products, GlobalShop struggled to maintain accurate and consistent categorization across their catalog, leading to poor search results and reduced sales.',
    solution: 'We implemented a data preparation and AI model development solution to automatically categorize products based on descriptions, images, and metadata, with human-in-the-loop validation for edge cases.',
    industry_id: 'ind-002',
    industry: mockIndustries[1], // Retail & E-commerce
    results: [], // Will be populated with references to mockCaseStudyResults
    services: [mockServices[1], mockServices[2], mockServices[3]], // Data Preparation, AI Model Development, Human-in-the-Loop
    created_at: '2023-03-10T10:00:00Z',
    updated_at: '2023-05-15T14:20:00Z'
  },
  {
    id: 'cs-002',
    title: 'Healthcare Image Annotation',
    slug: 'healthcare-image-annotation',
    client: 'MediScan Technologies',
    challenge: 'MediScan needed to annotate hundreds of thousands of medical images to train their diagnostic AI system, requiring extremely high accuracy and specialized medical knowledge.',
    solution: 'We assembled a team of medical professionals and data annotation experts to provide precise image annotation services, creating a high-quality dataset for AI training.',
    industry_id: 'ind-001',
    industry: mockIndustries[0], // Healthcare
    results: [], // Will be populated with references to mockCaseStudyResults
    services: [mockServices[1]], // Data Preparation
    created_at: '2023-02-20T09:30:00Z',
    updated_at: '2023-04-28T11:45:00Z'
  },
  {
    id: 'cs-003',
    title: 'Financial Document Processing',
    slug: 'financial-document-processing',
    client: 'SecureBank',
    challenge: 'SecureBank was manually processing thousands of loan applications daily, resulting in slow turnaround times and inconsistent evaluation criteria.',
    solution: 'We developed an end-to-end solution that automatically extracts, categorizes, and analyzes information from loan documents, flagging complex cases for human review.',
    industry_id: 'ind-003',
    industry: mockIndustries[2], // Financial Services
    results: [], // Will be populated with references to mockCaseStudyResults
    services: [mockServices[0], mockServices[1], mockServices[2], mockServices[3]], // All services
    created_at: '2023-01-05T14:00:00Z',
    updated_at: '2023-03-18T16:30:00Z'
  },
  {
    id: 'cs-004',
    title: 'Manufacturing Quality Control',
    slug: 'manufacturing-quality-control',
    client: 'PrecisionMakers',
    challenge: 'PrecisionMakers needed to improve quality control processes for detecting defects in their production line while reducing reliance on manual inspection.',
    solution: 'We implemented a computer vision AI system with human-in-the-loop verification to identify product defects with greater accuracy than traditional methods.',
    industry_id: 'ind-004',
    industry: mockIndustries[3], // Manufacturing
    results: [], // Will be populated with references to mockCaseStudyResults
    services: [mockServices[0], mockServices[2], mockServices[3]], // Data Collection, AI Model Development, Human-in-the-Loop
    created_at: '2023-02-12T11:20:00Z',
    updated_at: '2023-04-05T09:15:00Z'
  }
];

/**
 * Mock data for metrics and results from case studies
 */
export const mockCaseStudyResults: CaseStudyResult[] = [
  // E-commerce Product Categorization results
  {
    id: 'res-001',
    case_study_id: 'cs-001',
    metric: 'Search Accuracy',
    value: '40%',
    description: 'Improvement in product search accuracy'
  },
  {
    id: 'res-002',
    case_study_id: 'cs-001',
    metric: 'Categorization Time',
    value: '95%',
    description: 'Reduction in time required to categorize new products'
  },
  {
    id: 'res-003',
    case_study_id: 'cs-001',
    metric: 'Sales Conversion',
    value: '28%',
    description: 'Increase in search-to-purchase conversion rate'
  },

  // Healthcare Image Annotation results
  {
    id: 'res-004',
    case_study_id: 'cs-002',
    metric: 'Annotation Accuracy',
    value: '99.7%',
    description: 'Accuracy of medical image annotations'
  },
  {
    id: 'res-005',
    case_study_id: 'cs-002',
    metric: 'Time Savings',
    value: '70%',
    description: 'Reduction in time to build AI training dataset'
  },
  {
    id: 'res-006',
    case_study_id: 'cs-002',
    metric: 'Diagnostic Improvement',
    value: '32%',
    description: 'Increase in AI diagnostic accuracy after training'
  },

  // Financial Document Processing results
  {
    id: 'res-007',
    case_study_id: 'cs-003',
    metric: 'Processing Time',
    value: '85%',
    description: 'Reduction in loan application processing time'
  },
  {
    id: 'res-008',
    case_study_id: 'cs-003',
    metric: 'Error Rate',
    value: '76%',
    description: 'Reduction in processing errors'
  },
  {
    id: 'res-009',
    case_study_id: 'cs-003',
    metric: 'Cost Savings',
    value: '$2.4M',
    description: 'Annual cost savings from automation'
  },

  // Manufacturing Quality Control results
  {
    id: 'res-010',
    case_study_id: 'cs-004',
    metric: 'Defect Detection',
    value: '92%',
    description: 'Increase in defect detection rate'
  },
  {
    id: 'res-011',
    case_study_id: 'cs-004',
    metric: 'False Positives',
    value: '65%',
    description: 'Reduction in false positive detections'
  },
  {
    id: 'res-012',
    case_study_id: 'cs-004',
    metric: 'Inspection Cost',
    value: '50%',
    description: 'Reduction in quality control costs'
  }
];

/**
 * Mock data for geographic locations of impact stories
 */
export const mockLocations: Location[] = [
  {
    id: 'loc-001',
    name: 'Ramanagara',
    region: 'Karnataka',
    country: 'India'
  },
  {
    id: 'loc-002',
    name: 'Yeshwantpur',
    region: 'Karnataka',
    country: 'India'
  },
  {
    id: 'loc-003',
    name: 'Chittoor',
    region: 'Andhra Pradesh',
    country: 'India'
  },
  {
    id: 'loc-004',
    name: 'Nashik',
    region: 'Maharashtra',
    country: 'India'
  }
];

/**
 * Mock data for social impact stories and initiatives
 */
export const mockImpactStories: ImpactStory[] = [
  {
    id: 'is-001',
    title: 'Empowering Rural Communities',
    slug: 'empowering-rural-communities',
    story: 'Our center in Ramanagara has transformed what was primarily an agricultural community by creating over 200 technology jobs. By bringing skilled employment opportunities to rural areas, we've enabled local talent to build careers in AI and data services without migrating to urban centers. This has strengthened the local economy and improved quality of life for hundreds of families.',
    beneficiaries: 'Rural residents of Ramanagara district, particularly young adults seeking career opportunities',
    location_id: 'loc-001',
    location: mockLocations[0], // Ramanagara
    media: '/images/impact/ramanagara-center.jpg',
    metrics: [], // Will be populated with references to mockImpactMetrics
    created_at: '2023-02-15T10:00:00Z',
    updated_at: '2023-05-10T15:30:00Z'
  },
  {
    id: 'is-002',
    title: 'Women in Technology',
    slug: 'women-in-technology',
    story: 'Through targeted recruitment, training programs, and flexible work arrangements, we've created an environment where women can thrive in the technology sector. Our centers maintain a workforce that is 70% women, many of whom are the first in their families to work in professional careers. This initiative has challenged traditional gender roles and created new paths to economic independence for women in rural India.',
    beneficiaries: 'Women in rural and semi-urban areas, particularly those with limited prior access to professional careers',
    location_id: 'loc-002',
    location: mockLocations[1], // Yeshwantpur
    media: '/images/impact/women-in-tech.jpg',
    metrics: [], // Will be populated with references to mockImpactMetrics
    created_at: '2023-01-20T11:15:00Z',
    updated_at: '2023-04-25T14:45:00Z'
  },
  {
    id: 'is-003',
    title: 'Education Initiatives',
    slug: 'education-initiatives',
    story: 'Our education initiatives include scholarship programs for underprivileged students, digital literacy training, and partnerships with local schools to improve STEM education. By investing in education, we're helping to build a pipeline of skilled professionals while addressing inequality in access to learning opportunities. To date, over 500 students have benefited from our scholarship programs, with many going on to pursue careers in technology.',
    beneficiaries: 'School and college students from low-income families, educators in rural areas',
    location_id: 'loc-003',
    location: mockLocations[2], // Chittoor
    media: '/images/impact/education-programs.jpg',
    metrics: [], // Will be populated with references to mockImpactMetrics
    created_at: '2023-03-05T09:30:00Z',
    updated_at: '2023-05-12T13:20:00Z'
  },
  {
    id: 'is-004',
    title: 'Sustainable Operations',
    slug: 'sustainable-operations',
    story: 'We've implemented comprehensive sustainability initiatives across all our operations, including solar-powered facilities, water conservation systems, and zero-waste programs. Our newest center in Nashik operates entirely on renewable energy and has achieved a zero-waste-to-landfill status. These efforts demonstrate our commitment to environmental responsibility while creating healthier workplaces for our team members.',
    beneficiaries: 'Local communities, environment, and employees',
    location_id: 'loc-004',
    location: mockLocations[3], // Nashik
    media: '/images/impact/sustainable-operations.jpg',
    metrics: [], // Will be populated with references to mockImpactMetrics
    created_at: '2023-02-28T13:45:00Z',
    updated_at: '2023-04-18T10:30:00Z'
  }
];

/**
 * Mock data for social impact metrics and measurements
 */
export const mockImpactMetrics: ImpactMetric[] = [
  // Empowering Rural Communities metrics
  {
    id: 'im-001',
    story_id: 'is-001',
    metric_name: 'Jobs Created',
    value: '200',
    unit: 'jobs',
    period_start: '2020-01-01',
    period_end: '2023-05-01'
  },
  {
    id: 'im-002',
    story_id: 'is-001',
    metric_name: 'Local Income Growth',
    value: '35',
    unit: 'percent',
    period_start: '2020-01-01',
    period_end: '2023-05-01'
  },
  {
    id: 'im-003',
    story_id: 'is-001',
    metric_name: 'Families Supported',
    value: '650',
    unit: 'families',
    period_start: '2020-01-01',
    period_end: '2023-05-01'
  },

  // Women in Technology metrics
  {
    id: 'im-004',
    story_id: 'is-002',
    metric_name: 'Women Employed',
    value: '70',
    unit: 'percent',
    period_start: '2020-01-01',
    period_end: '2023-05-01'
  },
  {
    id: 'im-005',
    story_id: 'is-002',
    metric_name: 'Women in Leadership',
    value: '65',
    unit: 'percent',
    period_start: '2020-01-01',
    period_end: '2023-05-01'
  },
  {
    id: 'im-006',
    story_id: 'is-002',
    metric_name: 'First-Generation Tech Workers',
    value: '80',
    unit: 'percent',
    period_start: '2020-01-01',
    period_end: '2023-05-01'
  },

  // Education Initiatives metrics
  {
    id: 'im-007',
    story_id: 'is-003',
    metric_name: 'Scholarships Awarded',
    value: '500',
    unit: 'scholarships',
    period_start: '2019-01-01',
    period_end: '2023-05-01'
  },
  {
    id: 'im-008',
    story_id: 'is-003',
    metric_name: 'Digital Literacy Training',
    value: '1200',
    unit: 'students',
    period_start: '2019-01-01',
    period_end: '2023-05-01'
  },
  {
    id: 'im-009',
    story_id: 'is-003',
    metric_name: 'School Partnerships',
    value: '15',
    unit: 'schools',
    period_start: '2019-01-01',
    period_end: '2023-05-01'
  },

  // Sustainable Operations metrics
  {
    id: 'im-010',
    story_id: 'is-004',
    metric_name: 'Renewable Energy',
    value: '85',
    unit: 'percent',
    period_start: '2021-01-01',
    period_end: '2023-05-01'
  },
  {
    id: 'im-011',
    story_id: 'is-004',
    metric_name: 'Water Conservation',
    value: '40',
    unit: 'percent',
    period_start: '2021-01-01',
    period_end: '2023-05-01'
  },
  {
    id: 'im-012',
    story_id: 'is-004',
    metric_name: 'Waste Reduction',
    value: '90',
    unit: 'percent',
    period_start: '2021-01-01',
    period_end: '2023-05-01'
  }
];

// Link the related objects together
// Attach features to services
mockServices[0].features = mockServiceFeatures.filter(feature => feature.service_id === 'srv-001');
mockServices[1].features = mockServiceFeatures.filter(feature => feature.service_id === 'srv-002');
mockServices[2].features = mockServiceFeatures.filter(feature => feature.service_id === 'srv-003');
mockServices[3].features = mockServiceFeatures.filter(feature => feature.service_id === 'srv-004');

// Attach results to case studies
mockCaseStudies[0].results = mockCaseStudyResults.filter(result => result.case_study_id === 'cs-001');
mockCaseStudies[1].results = mockCaseStudyResults.filter(result => result.case_study_id === 'cs-002');
mockCaseStudies[2].results = mockCaseStudyResults.filter(result => result.case_study_id === 'cs-003');
mockCaseStudies[3].results = mockCaseStudyResults.filter(result => result.case_study_id === 'cs-004');

// Attach metrics to impact stories
mockImpactStories[0].metrics = mockImpactMetrics.filter(metric => metric.story_id === 'is-001');
mockImpactStories[1].metrics = mockImpactMetrics.filter(metric => metric.story_id === 'is-002');
mockImpactStories[2].metrics = mockImpactMetrics.filter(metric => metric.story_id === 'is-003');
mockImpactStories[3].metrics = mockImpactMetrics.filter(metric => metric.story_id === 'is-004');

/**
 * Sample data for testing contact form submissions
 */
export const mockContactFormData: ContactFormData = {
  name: 'John Smith',
  email: 'john.smith@example.com',
  phone: '+1 (555) 123-4567',
  company: 'Acme Corporation',
  message: 'I\'m interested in learning more about your AI services for my e-commerce business. We\'re looking to improve our product categorization and search functionality.',
  recaptchaToken: 'mock-recaptcha-token'
};

/**
 * Sample data for testing demo request form submissions
 */
export const mockDemoRequestFormData: DemoRequestFormData = {
  firstName: 'Jane',
  lastName: 'Doe',
  email: 'jane.doe@example.com',
  phone: '+1 (555) 987-6543',
  company: 'TechInnovators',
  jobTitle: 'Director of AI Strategy',
  serviceInterests: ['data_preparation', 'ai_model_development'],
  preferredDate: '2023-07-15',
  preferredTime: '10:00',
  timeZone: 'UTC-05:00',
  projectDetails: 'We have a large dataset of customer interactions that we\'d like to use to train AI models for improved customer service automation. Looking for a comprehensive solution from data preparation to model deployment.',
  referralSource: 'LinkedIn',
  recaptchaToken: 'mock-recaptcha-token'
};

/**
 * Sample data for testing quote request form submissions
 */
export const mockQuoteRequestFormData: QuoteRequestFormData = {
  firstName: 'Robert',
  lastName: 'Johnson',
  email: 'robert.johnson@example.com',
  phone: '+1 (555) 789-0123',
  company: 'HealthTech Solutions',
  jobTitle: 'CTO',
  serviceInterests: ['data_collection', 'data_preparation', 'human_in_the_loop'],
  projectDetails: 'We need to build a dataset of medical images for an AI diagnostic tool. Looking for both data collection and preparation services with human-in-the-loop verification to ensure maximum accuracy.',
  budgetRange: 'between_50k_100k',
  timeline: 'within_3_months',
  referralSource: 'Industry Conference',
  recaptchaToken: 'mock-recaptcha-token'
};

/**
 * Sample data for testing file upload form submissions
 */
export const mockUploadFormData: UploadFormData = {
  name: 'Michael Chen',
  email: 'michael.chen@example.com',
  company: 'DataDriven Analytics',
  phone: '+1 (555) 456-7890',
  serviceInterest: 'data_preparation',
  description: 'This dataset contains product information from our e-commerce platform. We need help cleaning and standardizing the data for better analytics and potential AI applications.',
  recaptchaToken: 'mock-recaptcha-token'
};

/**
 * Mock API responses for various endpoints including success and error scenarios
 */
export const mockApiResponses = {
  // Contact form responses
  contactForm: {
    success: {
      success: true,
      message: 'Thank you for your message. We will contact you shortly.',
      submission_id: 'sub-contact-123456'
    },
    error: {
      success: false,
      message: 'There was a problem submitting your message.',
      errors: {
        email: ['Please enter a valid email address'],
        recaptchaToken: ['CAPTCHA verification failed']
      }
    }
  },

  // Demo request responses
  demoRequest: {
    success: {
      success: true,
      message: 'Your demo request has been received. A member of our team will contact you to schedule your demo.',
      submission_id: 'sub-demo-123456'
    },
    error: {
      success: false,
      message: 'There was a problem submitting your demo request.',
      errors: {
        phone: ['Please enter a valid phone number'],
        preferredDate: ['Please select a date at least 48 hours in the future']
      }
    }
  },

  // Quote request responses
  quoteRequest: {
    success: {
      success: true,
      message: 'Your quote request has been received. We will prepare a custom quote and contact you within 2 business days.',
      submission_id: 'sub-quote-123456'
    },
    error: {
      success: false,
      message: 'There was a problem submitting your quote request.',
      errors: {
        serviceInterests: ['Please select at least one service'],
        projectDetails: ['Please provide more details about your project']
      }
    }
  },

  // Services API responses
  services: {
    all: {
      success: true,
      data: mockServices,
      message: 'Services retrieved successfully'
    },
    single: {
      success: true,
      data: mockServices[0],
      message: 'Service retrieved successfully'
    },
    error: {
      success: false,
      data: null,
      message: 'Service not found',
      errors: {
        id: ['Invalid service ID']
      }
    }
  },

  // Case studies API responses
  caseStudies: {
    all: {
      success: true,
      data: mockCaseStudies,
      message: 'Case studies retrieved successfully'
    },
    single: {
      success: true,
      data: mockCaseStudies[0],
      message: 'Case study retrieved successfully'
    },
    error: {
      success: false,
      data: null,
      message: 'Case study not found',
      errors: {
        id: ['Invalid case study ID']
      }
    },
    byIndustry: {
      success: true,
      data: [mockCaseStudies[0]],
      message: 'Case studies retrieved successfully'
    }
  },

  // Impact stories API responses
  impactStories: {
    all: {
      success: true,
      data: mockImpactStories,
      message: 'Impact stories retrieved successfully'
    },
    single: {
      success: true,
      data: mockImpactStories[0],
      message: 'Impact story retrieved successfully'
    },
    error: {
      success: false,
      data: null,
      message: 'Impact story not found',
      errors: {
        id: ['Invalid impact story ID']
      }
    }
  },

  // General error responses
  errors: {
    notFound: {
      success: false,
      data: null,
      message: 'Resource not found',
      errors: {
        resource: ['The requested resource does not exist']
      }
    },
    serverError: {
      success: false,
      data: null,
      message: 'Internal server error',
      errors: {
        server: ['An unexpected error occurred. Please try again later.']
      }
    },
    unauthorized: {
      success: false,
      data: null,
      message: 'Unauthorized',
      errors: {
        auth: ['You are not authorized to access this resource']
      }
    }
  }
};

/**
 * Mock responses for file upload endpoints including request, status, and completion
 */
export const mockUploadResponses = {
  // Upload request response
  uploadRequest: {
    success: {
      upload_id: 'upload-123456',
      presigned_url: 'https://example.com/presigned-upload-url',
      presigned_fields: {
        'key': 'uploads/user123/dataset.csv',
        'bucket': 'indivillage-uploads',
        'X-Amz-Algorithm': 'AWS4-HMAC-SHA256',
        'X-Amz-Credential': 'mock-credential',
        'X-Amz-Date': '20230615T120000Z',
        'Policy': 'mock-policy',
        'X-Amz-Signature': 'mock-signature'
      },
      expires_at: '2023-06-15T12:30:00Z',
      status: UploadStatus.PENDING
    },
    error: {
      success: false,
      message: 'Unable to generate upload URL',
      errors: {
        file: ['File size exceeds maximum allowed (50MB)']
      }
    }
  },

  // Upload status responses for different stages
  uploadStatus: {
    pending: {
      upload_id: 'upload-123456',
      filename: 'dataset.csv',
      status: UploadStatus.PENDING,
      created_at: '2023-06-15T12:00:00Z',
      processed_at: null,
      analysis_result: null
    },
    uploading: {
      upload_id: 'upload-123456',
      filename: 'dataset.csv',
      status: UploadStatus.UPLOADING,
      created_at: '2023-06-15T12:00:00Z',
      processed_at: null,
      analysis_result: null
    },
    uploaded: {
      upload_id: 'upload-123456',
      filename: 'dataset.csv',
      status: UploadStatus.UPLOADED,
      created_at: '2023-06-15T12:00:00Z',
      processed_at: null,
      analysis_result: null
    },
    scanning: {
      upload_id: 'upload-123456',
      filename: 'dataset.csv',
      status: UploadStatus.SCANNING,
      created_at: '2023-06-15T12:00:00Z',
      processed_at: null,
      analysis_result: null
    },
    processing: {
      upload_id: 'upload-123456',
      filename: 'dataset.csv',
      status: UploadStatus.PROCESSING,
      created_at: '2023-06-15T12:00:00Z',
      processed_at: null,
      analysis_result: null
    },
    completed: {
      upload_id: 'upload-123456',
      filename: 'dataset.csv',
      status: UploadStatus.COMPLETED,
      created_at: '2023-06-15T12:00:00Z',
      processed_at: '2023-06-15T12:05:30Z',
      analysis_result: {
        fileType: FileType.CSV,
        rowCount: 5842,
        columnCount: 12,
        sampleColumns: [
          'product_id',
          'name',
          'description',
          'category',
          'price',
          'stock',
          'brand',
          'rating',
          'reviews',
          'created_date',
          'updated_date',
          'is_active'
        ],
        quality: {
          missingValues: 234,
          duplicateRows: 15,
          inconsistentValues: 67,
          overallQualityScore: 92
        },
        recommendations: [
          'Clean missing values in description field',
          'Standardize category values for consistent classification',
          'Normalize brand names to improve grouping',
          'Consider removing duplicate product entries'
        ]
      }
    },
    failed: {
      upload_id: 'upload-123456',
      filename: 'dataset.csv',
      status: UploadStatus.FAILED,
      created_at: '2023-06-15T12:00:00Z',
      processed_at: '2023-06-15T12:02:10Z',
      analysis_result: {
        error: 'File format not supported or file is corrupted',
        errorDetails: 'Unable to parse CSV: Invalid format at row 145'
      }
    },
    quarantined: {
      upload_id: 'upload-123456',
      filename: 'suspicious_file.csv',
      status: UploadStatus.QUARANTINED,
      created_at: '2023-06-15T12:00:00Z',
      processed_at: '2023-06-15T12:01:30Z',
      analysis_result: {
        securityIssue: 'Potential security threat detected',
        action: 'File has been quarantined and will not be processed'
      }
    }
  },

  // Upload complete response
  uploadComplete: {
    success: {
      success: true,
      message: 'Upload completed successfully',
      upload_id: 'upload-123456'
    },
    error: {
      success: false,
      message: 'Upload failed',
      errors: {
        upload: ['Upload timed out or was interrupted']
      }
    }
  }
};