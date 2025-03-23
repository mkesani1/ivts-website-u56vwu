/**
 * Content type definitions for the IndiVillage website
 * These types represent the content model structure from the Contentful CMS
 * @version 1.0.0
 */

/**
 * Enum defining the content types available in the CMS
 */
export enum ContentType {
  SERVICE = 'service',
  CASE_STUDY = 'caseStudy',
  IMPACT_STORY = 'impactStory',
  BLOG_POST = 'blogPost',
  TEAM_MEMBER = 'teamMember',
  PAGE = 'page'
}

/**
 * Type representing possible content type values
 */
export type ContentTypeValue = 
  | ContentType.SERVICE
  | ContentType.CASE_STUDY
  | ContentType.IMPACT_STORY
  | ContentType.BLOG_POST
  | ContentType.TEAM_MEMBER
  | ContentType.PAGE;

/**
 * Interface for media assets like images and videos
 */
export interface Asset {
  id: string;
  title: string;
  description: string;
  url: string;
  width: number;
  height: number;
  contentType: string;
}

/**
 * Enum defining the categories of AI services offered
 */
export enum ServiceCategory {
  DATA_COLLECTION = 'dataCollection',
  DATA_PREPARATION = 'dataPreparation',
  AI_MODEL_DEVELOPMENT = 'aiModelDevelopment',
  HUMAN_IN_THE_LOOP = 'humanInTheLoop'
}

/**
 * Type representing possible service category values
 */
export type ServiceCategoryValue = 
  | ServiceCategory.DATA_COLLECTION
  | ServiceCategory.DATA_PREPARATION
  | ServiceCategory.AI_MODEL_DEVELOPMENT
  | ServiceCategory.HUMAN_IN_THE_LOOP;

/**
 * Interface for features of a service
 */
export interface ServiceFeature {
  id: string;
  title: string;
  description: string;
  icon: Asset;
}

/**
 * Interface for AI service offerings
 */
export interface Service {
  id: string;
  title: string;
  slug: string;
  description: string;
  category: ServiceCategoryValue;
  features: ServiceFeature[];
  icon: Asset;
  heroImage: Asset;
  howItWorks: string;
  order: number;
  createdAt: string;
  updatedAt: string;
}

/**
 * Interface for industry categories for case studies
 */
export interface Industry {
  id: string;
  name: string;
  slug: string;
}

/**
 * Interface for results/metrics of a case study
 */
export interface CaseStudyResult {
  id: string;
  metric: string;
  value: string;
  description: string;
}

/**
 * Interface for case studies showcasing client success stories
 */
export interface CaseStudy {
  id: string;
  title: string;
  slug: string;
  client: string;
  industry: Industry;
  challenge: string;
  solution: string;
  results: CaseStudyResult[];
  image: Asset;
  services: Service[];
  createdAt: string;
  updatedAt: string;
}

/**
 * Interface for geographic locations of impact stories
 */
export interface Location {
  id: string;
  name: string;
  region: string;
  country: string;
}

/**
 * Interface for social impact metrics
 */
export interface ImpactMetric {
  id: string;
  metric: string;
  value: string;
  unit: string;
  description: string;
}

/**
 * Interface for UN Sustainable Development Goals
 */
export interface SDG {
  id: string;
  number: number;
  name: string;
  description: string;
  icon: Asset;
}

/**
 * Interface for social impact stories
 */
export interface ImpactStory {
  id: string;
  title: string;
  slug: string;
  story: string;
  excerpt: string;
  beneficiaries: string;
  location: Location;
  media: Asset[];
  metrics: ImpactMetric[];
  sdgs: SDG[];
  createdAt: string;
  updatedAt: string;
}

/**
 * Interface for team member profiles
 */
export interface TeamMember {
  id: string;
  name: string;
  title: string;
  bio: string;
  photo: Asset;
  socialLinks: Record<string, string>;
  order: number;
}

/**
 * Interface for blog post categories
 */
export interface BlogCategory {
  id: string;
  name: string;
  slug: string;
}

/**
 * Interface for blog posts
 */
export interface BlogPost {
  id: string;
  title: string;
  slug: string;
  excerpt: string;
  content: string;
  author: TeamMember;
  featuredImage: Asset;
  categories: BlogCategory[];
  tags: string[];
  date: string;
  createdAt: string;
  updatedAt: string;
}

/**
 * Interface for static pages
 */
export interface Page {
  id: string;
  title: string;
  slug: string;
  content: string;
  metaTitle: string;
  metaDescription: string;
  featuredImage: Asset;
  sections: any[]; // Dynamic page sections can have various shapes
  createdAt: string;
  updatedAt: string;
}

/**
 * Interface for content query parameters when fetching from CMS
 */
export interface ContentQueryParams {
  contentType: ContentTypeValue;
  filters?: Record<string, any>;
  limit?: number;
  skip?: number;
  order?: string;
  select?: string[];
}

/**
 * Interface for content response from CMS with pagination info
 */
export interface ContentResponse<T = any> {
  items: T[];
  total: number;
  skip: number;
  limit: number;
}