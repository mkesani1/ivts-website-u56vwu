/**
 * Content Service for IndiVillage Website
 * 
 * This service provides a unified interface for content retrieval across the IndiVillage website.
 * It abstracts the content source (Contentful CMS or backend API) and provides consistent
 * methods for fetching services, case studies, impact stories, and other content types
 * with proper caching and error handling.
 *
 * @module services/contentService
 * @version 1.0.0
 */

import { 
  Service, 
  CaseStudy, 
  ImpactStory, 
  BlogPost, 
  TeamMember, 
  Page,
  ContentType
} from '../types/content';

import { 
  getServices as getServicesFromApi, 
  getServiceBySlug as getServiceBySlugFromApi,
  getCaseStudies as getCaseStudiesFromApi,
  getCaseStudyBySlug as getCaseStudyBySlugFromApi,
  getImpactStories as getImpactStoriesFromApi,
  getImpactStoryBySlug as getImpactStoryBySlugFromApi
} from './api';

import {
  getServices as getServicesFromCMS,
  getServiceBySlug as getServiceBySlugFromCMS,
  getCaseStudies as getCaseStudiesFromCMS,
  getCaseStudyBySlug as getCaseStudyBySlugFromCMS,
  getImpactStories as getImpactStoriesFromCMS,
  getImpactStoryBySlug as getImpactStoryBySlugFromCMS,
  getBlogPosts as getBlogPostsFromCMS,
  getBlogPostBySlug as getBlogPostBySlugFromCMS,
  getTeamMembers as getTeamMembersFromCMS,
  getPageBySlug as getPageBySlugFromCMS,
  getAllContentSlugs
} from '../lib/contentful';

import { logError } from '../utils/errorHandling';

// Configuration constants
const USE_CMS = process.env.NEXT_PUBLIC_USE_CMS === 'true';
const ENABLE_CONTENT_CACHE = process.env.NEXT_PUBLIC_ENABLE_CONTENT_CACHE !== 'false';

// Cache for content data (simple in-memory cache)
const contentCache: Record<string, { data: any; timestamp: number }> = {};
const CACHE_TTL = 5 * 60 * 1000; // 5 minutes in milliseconds

/**
 * Helper function to get cached data or fetch new data
 * @param cacheKey Unique key for the cached content
 * @param fetchFn Function that fetches the data when cache is invalid or missing
 * @returns Promise resolving to cached or freshly fetched data
 */
const getCachedOrFetch = async <T>(
  cacheKey: string,
  fetchFn: () => Promise<T>
): Promise<T> => {
  // Skip cache if disabled
  if (!ENABLE_CONTENT_CACHE) {
    return fetchFn();
  }

  const cachedItem = contentCache[cacheKey];
  const now = Date.now();

  // Return cached data if valid
  if (cachedItem && now - cachedItem.timestamp < CACHE_TTL) {
    return cachedItem.data as T;
  }

  // Fetch new data
  const data = await fetchFn();
  
  // Cache the result
  contentCache[cacheKey] = {
    data,
    timestamp: now
  };
  
  return data;
};

/**
 * Fetches all services with optional category filtering
 * @param category Optional category to filter services by
 * @returns Promise resolving to an array of services
 */
export const getServices = async (category?: string): Promise<Service[]> => {
  try {
    const cacheKey = `services_${category || 'all'}`;
    
    return getCachedOrFetch(cacheKey, async () => {
      if (USE_CMS) {
        return await getServicesFromCMS(category);
      } else {
        const filters = category ? { category } : {};
        const response = await getServicesFromApi(filters);
        return response.items || [];
      }
    });
  } catch (error) {
    logError(error, 'getServices');
    return [];
  }
};

/**
 * Fetches a service by its slug
 * @param slug Slug of the service to fetch
 * @returns Promise resolving to a service or null if not found
 */
export const getServiceBySlug = async (slug: string): Promise<Service | null> => {
  try {
    const cacheKey = `service_${slug}`;
    
    return getCachedOrFetch(cacheKey, async () => {
      if (USE_CMS) {
        return await getServiceBySlugFromCMS(slug);
      } else {
        return await getServiceBySlugFromApi(slug);
      }
    });
  } catch (error) {
    logError(error, 'getServiceBySlug');
    return null;
  }
};

/**
 * Fetches all case studies with optional filtering
 * @param filters Optional filters to apply to the query
 * @returns Promise resolving to an array of case studies
 */
export const getCaseStudies = async (filters: Record<string, any> = {}): Promise<CaseStudy[]> => {
  try {
    const cacheKey = `case_studies_${JSON.stringify(filters)}`;
    
    return getCachedOrFetch(cacheKey, async () => {
      if (USE_CMS) {
        return await getCaseStudiesFromCMS(filters);
      } else {
        const response = await getCaseStudiesFromApi(filters);
        return response.items || [];
      }
    });
  } catch (error) {
    logError(error, 'getCaseStudies');
    return [];
  }
};

/**
 * Fetches a case study by its slug
 * @param slug Slug of the case study to fetch
 * @returns Promise resolving to a case study or null if not found
 */
export const getCaseStudyBySlug = async (slug: string): Promise<CaseStudy | null> => {
  try {
    const cacheKey = `case_study_${slug}`;
    
    return getCachedOrFetch(cacheKey, async () => {
      if (USE_CMS) {
        return await getCaseStudyBySlugFromCMS(slug);
      } else {
        return await getCaseStudyBySlugFromApi(slug);
      }
    });
  } catch (error) {
    logError(error, 'getCaseStudyBySlug');
    return null;
  }
};

/**
 * Fetches all impact stories with optional filtering
 * @param filters Optional filters to apply to the query
 * @returns Promise resolving to an array of impact stories
 */
export const getImpactStories = async (filters: Record<string, any> = {}): Promise<ImpactStory[]> => {
  try {
    const cacheKey = `impact_stories_${JSON.stringify(filters)}`;
    
    return getCachedOrFetch(cacheKey, async () => {
      if (USE_CMS) {
        return await getImpactStoriesFromCMS(filters);
      } else {
        const response = await getImpactStoriesFromApi(filters);
        return response.items || [];
      }
    });
  } catch (error) {
    logError(error, 'getImpactStories');
    return [];
  }
};

/**
 * Fetches an impact story by its slug
 * @param slug Slug of the impact story to fetch
 * @returns Promise resolving to an impact story or null if not found
 */
export const getImpactStoryBySlug = async (slug: string): Promise<ImpactStory | null> => {
  try {
    const cacheKey = `impact_story_${slug}`;
    
    return getCachedOrFetch(cacheKey, async () => {
      if (USE_CMS) {
        return await getImpactStoryBySlugFromCMS(slug);
      } else {
        return await getImpactStoryBySlugFromApi(slug);
      }
    });
  } catch (error) {
    logError(error, 'getImpactStoryBySlug');
    return null;
  }
};

/**
 * Fetches all blog posts with optional filtering
 * @param filters Optional filters to apply to the query
 * @returns Promise resolving to an array of blog posts
 */
export const getBlogPosts = async (filters: Record<string, any> = {}): Promise<BlogPost[]> => {
  try {
    const cacheKey = `blog_posts_${JSON.stringify(filters)}`;
    
    return getCachedOrFetch(cacheKey, async () => {
      // Blog posts are only available from CMS
      const posts = await getBlogPostsFromCMS(filters);
      return posts;
    });
  } catch (error) {
    logError(error, 'getBlogPosts');
    return [];
  }
};

/**
 * Fetches a blog post by its slug
 * @param slug Slug of the blog post to fetch
 * @returns Promise resolving to a blog post or null if not found
 */
export const getBlogPostBySlug = async (slug: string): Promise<BlogPost | null> => {
  try {
    const cacheKey = `blog_post_${slug}`;
    
    return getCachedOrFetch(cacheKey, async () => {
      // Blog posts are only available from CMS
      const post = await getBlogPostBySlugFromCMS(slug);
      return post;
    });
  } catch (error) {
    logError(error, 'getBlogPostBySlug');
    return null;
  }
};

/**
 * Fetches all team members with optional filtering
 * @param filters Optional filters to apply to the query
 * @returns Promise resolving to an array of team members
 */
export const getTeamMembers = async (filters: Record<string, any> = {}): Promise<TeamMember[]> => {
  try {
    const cacheKey = `team_members_${JSON.stringify(filters)}`;
    
    return getCachedOrFetch(cacheKey, async () => {
      // Team members are only available from CMS
      const members = await getTeamMembersFromCMS(filters);
      return members;
    });
  } catch (error) {
    logError(error, 'getTeamMembers');
    return [];
  }
};

/**
 * Fetches a page by its slug
 * @param slug Slug of the page to fetch
 * @returns Promise resolving to a page or null if not found
 */
export const getPageBySlug = async (slug: string): Promise<Page | null> => {
  try {
    const cacheKey = `page_${slug}`;
    
    return getCachedOrFetch(cacheKey, async () => {
      // Pages are only available from CMS
      const page = await getPageBySlugFromCMS(slug);
      return page;
    });
  } catch (error) {
    logError(error, 'getPageBySlug');
    return null;
  }
};

/**
 * Fetches all slugs for a specific content type
 * @param contentType Type of content to fetch slugs for
 * @returns Promise resolving to an array of slugs
 */
export const getContentSlugs = async (contentType: ContentType): Promise<string[]> => {
  try {
    const cacheKey = `slugs_${contentType}`;
    
    return getCachedOrFetch(cacheKey, async () => {
      // Content slugs are only available from CMS
      const slugs = await getAllContentSlugs(contentType);
      return slugs;
    });
  } catch (error) {
    logError(error, 'getContentSlugs');
    return [];
  }
};

/**
 * Maps a Contentful service to the API service format
 * @param contentfulService Service data from Contentful
 * @returns Service in API format
 */
const mapContentfulToApiService = (contentfulService: any): Service => {
  if (!contentfulService) return null as any;
  
  return {
    id: contentfulService.id,
    name: contentfulService.title,
    slug: contentfulService.slug,
    description: contentfulService.description,
    icon: contentfulService.icon?.url || '',
    order: contentfulService.order || 0,
    features: contentfulService.features?.map((feature: any) => ({
      id: feature.id,
      service_id: contentfulService.id,
      title: feature.title,
      description: feature.description,
      order: feature.order || 0
    })) || [],
    case_studies: contentfulService.caseStudies?.map(mapContentfulToApiCaseStudy) || [],
    created_at: contentfulService.createdAt,
    updated_at: contentfulService.updatedAt
  };
};

/**
 * Maps a Contentful case study to the API case study format
 * @param contentfulCaseStudy Case study data from Contentful
 * @returns Case study in API format
 */
const mapContentfulToApiCaseStudy = (contentfulCaseStudy: any): CaseStudy => {
  if (!contentfulCaseStudy) return null as any;
  
  return {
    id: contentfulCaseStudy.id,
    title: contentfulCaseStudy.title,
    slug: contentfulCaseStudy.slug,
    client: contentfulCaseStudy.client,
    challenge: contentfulCaseStudy.challenge,
    solution: contentfulCaseStudy.solution,
    industry_id: contentfulCaseStudy.industry?.id,
    industry: contentfulCaseStudy.industry ? {
      id: contentfulCaseStudy.industry.id,
      name: contentfulCaseStudy.industry.name,
      slug: contentfulCaseStudy.industry.slug
    } : null,
    results: contentfulCaseStudy.results?.map((result: any) => ({
      id: result.id,
      case_study_id: contentfulCaseStudy.id,
      metric: result.metric,
      value: result.value,
      description: result.description
    })) || [],
    services: contentfulCaseStudy.services?.map(mapContentfulToApiService) || [],
    created_at: contentfulCaseStudy.createdAt,
    updated_at: contentfulCaseStudy.updatedAt
  };
};

/**
 * Maps a Contentful impact story to the API impact story format
 * @param contentfulImpactStory Impact story data from Contentful
 * @returns Impact story in API format
 */
const mapContentfulToApiImpactStory = (contentfulImpactStory: any): ImpactStory => {
  if (!contentfulImpactStory) return null as any;
  
  return {
    id: contentfulImpactStory.id,
    title: contentfulImpactStory.title,
    slug: contentfulImpactStory.slug,
    story: contentfulImpactStory.story,
    beneficiaries: contentfulImpactStory.beneficiaries,
    location_id: contentfulImpactStory.location?.id,
    location: contentfulImpactStory.location ? {
      id: contentfulImpactStory.location.id,
      name: contentfulImpactStory.location.name,
      region: contentfulImpactStory.location.region,
      country: contentfulImpactStory.location.country
    } : null,
    media: contentfulImpactStory.media?.map((item: any) => item.url).join(',') || '',
    metrics: contentfulImpactStory.metrics?.map((metric: any) => ({
      id: metric.id,
      story_id: contentfulImpactStory.id,
      metric_name: metric.metric,
      value: metric.value,
      unit: metric.unit,
      period_start: '',
      period_end: ''
    })) || [],
    created_at: contentfulImpactStory.createdAt,
    updated_at: contentfulImpactStory.updatedAt
  };
};