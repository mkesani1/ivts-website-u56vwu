/**
 * impact.ts
 * 
 * This file defines constants related to IndiVillage's social impact initiatives,
 * including impact metrics, categories, story types, and Sustainable Development Goals (SDGs).
 * These constants are used throughout the website to showcase the company's 'AI for Good'
 * mission and social impact achievements.
 * 
 * The constants defined here support the Social Impact Storytelling feature (F-005) 
 * and are used on the Social Impact page of the website.
 */

/**
 * Interface for an individual impact metric
 */
interface ImpactMetric {
  /** Unique identifier for the metric */
  id: string;
  /** Display title of the metric */
  title: string;
  /** Numerical value of the metric */
  value: number;
  /** Unit or suffix to display after the value (e.g., '+', '%') */
  suffix: string;
  /** Detailed description of what the metric represents */
  description: string;
  /** Material icon name to display with the metric */
  icon: string;
}

/**
 * Interface for the impact metrics collection
 */
interface ImpactMetrics {
  /** Jobs created through IndiVillage's initiatives */
  JOBS_CREATED: ImpactMetric;
  /** Communities positively impacted by IndiVillage */
  COMMUNITIES_IMPACTED: ImpactMetric;
  /** Total individuals whose lives were transformed */
  LIVES_TRANSFORMED: ImpactMetric;
  /** Percentage of women in IndiVillage's workforce */
  WOMEN_EMPLOYED: ImpactMetric;
}

/**
 * Interface for a Sustainable Development Goal
 */
interface SustainableDevelopmentGoal {
  /** Unique identifier for the SDG */
  id: string;
  /** SDG number (1-17) */
  number: number;
  /** Name of the SDG */
  name: string;
  /** Description of how IndiVillage contributes to this SDG */
  description: string;
  /** Path to the SDG icon */
  icon: string;
}

/**
 * Key impact metrics showcasing IndiVillage's social achievements
 * These metrics are displayed prominently on the Social Impact page
 * and used throughout the website to highlight the company's impact.
 */
export const IMPACT_METRICS: ImpactMetrics = {
  JOBS_CREATED: {
    id: 'jobs_created',
    title: 'Jobs Created',
    value: 1000,
    suffix: '+',
    description: 'Sustainable tech jobs created in rural communities',
    icon: 'work',
  },
  COMMUNITIES_IMPACTED: {
    id: 'communities_impacted',
    title: 'Communities Impacted',
    value: 10,
    suffix: '+',
    description: 'Rural communities transformed through technology',
    icon: 'location_city',
  },
  LIVES_TRANSFORMED: {
    id: 'lives_transformed',
    title: 'Lives Transformed',
    value: 50000,
    suffix: '+',
    description: 'Individuals benefiting from our social impact initiatives',
    icon: 'people',
  },
  WOMEN_EMPLOYED: {
    id: 'women_employed',
    title: 'Women Employed',
    value: 70,
    suffix: '%',
    description: 'Percentage of women in our workforce',
    icon: 'diversity_3',
  },
};

/**
 * Categories for classifying impact stories and initiatives
 * Used for filtering and organizing impact content
 */
export const IMPACT_CATEGORIES = {
  /** Employment-related impact initiatives */
  EMPLOYMENT: 'employment',
  /** Educational programs and initiatives */
  EDUCATION: 'education',
  /** Community development and support initiatives */
  COMMUNITY: 'community',
  /** Gender equality and women's empowerment initiatives */
  GENDER_EQUALITY: 'gender-equality',
  /** Infrastructure development in rural communities */
  INFRASTRUCTURE: 'infrastructure',
};

/**
 * Types of impact stories for categorization and filtering
 * Used to identify the focus and scope of each impact story
 */
export const IMPACT_STORY_TYPES = {
  /** Stories about entire community transformations */
  COMMUNITY: 'community',
  /** Stories about individual beneficiaries */
  INDIVIDUAL: 'individual',
  /** Stories about specific projects */
  PROJECT: 'project',
  /** Stories about broader initiatives */
  INITIATIVE: 'initiative',
};

/**
 * The UN Sustainable Development Goals (SDGs) that IndiVillage contributes to
 * These are displayed on the Social Impact page to highlight alignment with global goals
 * 
 * Each SDG includes its number, name, a description of IndiVillage's contribution,
 * and a path to its icon.
 */
export const SUSTAINABLE_DEVELOPMENT_GOALS: SustainableDevelopmentGoal[] = [
  {
    id: 'sdg-1',
    number: 1,
    name: 'No Poverty',
    description: 'Creating sustainable livelihoods through technology jobs in rural areas',
    icon: '/images/sdg/sdg-1.svg',
  },
  {
    id: 'sdg-4',
    number: 4,
    name: 'Quality Education',
    description: 'Providing digital literacy and technical training programs',
    icon: '/images/sdg/sdg-4.svg',
  },
  {
    id: 'sdg-5',
    number: 5,
    name: 'Gender Equality',
    description: 'Empowering women through equal employment opportunities in technology',
    icon: '/images/sdg/sdg-5.svg',
  },
  {
    id: 'sdg-8',
    number: 8,
    name: 'Decent Work & Economic Growth',
    description: 'Creating quality jobs and economic opportunities in underserved communities',
    icon: '/images/sdg/sdg-8.svg',
  },
];