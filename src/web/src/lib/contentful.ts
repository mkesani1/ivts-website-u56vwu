import { createClient, ContentfulClientApi, Entry, Asset } from 'contentful'; // contentful@^10.3.0
import { 
  ContentType, 
  ContentTypeValue, 
  ContentQueryParams, 
  Service,
  CaseStudy,
  ImpactStory,
  BlogPost,
  TeamMember,
  Page,
  ContentResponse 
} from '../types/content';
import { logError } from '../utils/errorHandling';

// Environment variables for Contentful configuration
const CONTENTFUL_SPACE_ID = process.env.NEXT_PUBLIC_CONTENTFUL_SPACE_ID;
const CONTENTFUL_ACCESS_TOKEN = process.env.NEXT_PUBLIC_CONTENTFUL_ACCESS_TOKEN;
const CONTENTFUL_ENVIRONMENT = process.env.NEXT_PUBLIC_CONTENTFUL_ENVIRONMENT || 'master';
const CONTENTFUL_PREVIEW_ACCESS_TOKEN = process.env.CONTENTFUL_PREVIEW_ACCESS_TOKEN;
const IS_PREVIEW_MODE = process.env.NEXT_PUBLIC_CONTENTFUL_PREVIEW === 'true';

/**
 * Creates and configures a Contentful client instance
 * @param preview Whether to use the preview API (for draft content)
 * @returns Configured Contentful client instance
 */
const createContentfulClient = (preview: boolean = false): ContentfulClientApi => {
  const accessToken = preview 
    ? CONTENTFUL_PREVIEW_ACCESS_TOKEN 
    : CONTENTFUL_ACCESS_TOKEN;
  
  return createClient({
    space: CONTENTFUL_SPACE_ID!,
    accessToken: accessToken!,
    environment: CONTENTFUL_ENVIRONMENT,
    host: preview ? 'preview.contentful.com' : 'cdn.contentful.com'
  });
};

/**
 * Gets the appropriate Contentful client (preview or production)
 * @returns Contentful client instance
 */
const getContentfulClient = (): ContentfulClientApi => {
  return createContentfulClient(IS_PREVIEW_MODE);
};

/**
 * Transforms a Contentful entry to a clean data object
 * @param entry Contentful entry
 * @returns Transformed entry data
 */
const transformContentfulEntry = (entry: Entry<any>): any => {
  if (!entry) return null;

  // Extract fields from entry
  const { fields, sys } = entry;
  const transformedFields: Record<string, any> = {};

  // Process each field to handle nested entries and assets
  Object.keys(fields).forEach(key => {
    const value = fields[key];

    if (value && typeof value === 'object' && value.sys) {
      // Handle linked entries and assets
      if (value.sys.type === 'Asset') {
        transformedFields[key] = transformContentfulAsset(value);
      } else if (value.sys.type === 'Entry') {
        transformedFields[key] = transformContentfulEntry(value);
      }
    } else if (Array.isArray(value)) {
      // Handle arrays of entries and assets
      transformedFields[key] = value.map(item => {
        if (item && typeof item === 'object' && item.sys) {
          if (item.sys.type === 'Asset') {
            return transformContentfulAsset(item);
          } else if (item.sys.type === 'Entry') {
            return transformContentfulEntry(item);
          }
        }
        return item;
      });
    } else {
      // Handle primitive values
      transformedFields[key] = value;
    }
  });

  // Add system metadata
  return {
    ...transformedFields,
    id: sys.id,
    createdAt: sys.createdAt,
    updatedAt: sys.updatedAt
  };
};

/**
 * Transforms a Contentful asset to a clean asset object
 * @param asset Contentful asset
 * @returns Transformed asset data
 */
const transformContentfulAsset = (asset: Asset): object => {
  if (!asset || !asset.fields) return null;

  const { fields, sys } = asset;
  
  return {
    id: sys.id,
    title: fields.title,
    description: fields.description,
    url: fields.file?.url ? `https:${fields.file.url}` : null,
    width: fields.file?.details?.image?.width,
    height: fields.file?.details?.image?.height,
    contentType: fields.file?.contentType
  };
};

/**
 * Fetches entries from Contentful based on query parameters
 * @param queryParams Query parameters for content retrieval
 * @returns Promise resolving to content response with items and pagination info
 */
export const getContentfulEntries = async <T = any>(
  queryParams: ContentQueryParams
): Promise<ContentResponse<T>> => {
  try {
    const client = getContentfulClient();
    const { contentType, filters = {}, limit = 100, skip = 0, order, select } = queryParams;
    
    // Build query object
    const query: Record<string, any> = {
      content_type: contentType,
      limit,
      skip,
      ...filters
    };

    // Add optional parameters if provided
    if (order) {
      query.order = order;
    }

    if (select && select.length) {
      query.select = select.join(',');
    }

    // Fetch entries from Contentful
    const response = await client.getEntries(query);
    
    // Transform response entries
    const items = response.items.map(item => transformContentfulEntry(item)) as T[];
    
    // Return formatted response
    return {
      items,
      total: response.total,
      skip: response.skip,
      limit: response.limit
    };
  } catch (error) {
    logError(error, `Contentful getEntries - ${queryParams.contentType}`);
    throw error;
  }
};

/**
 * Fetches a single content entry by its slug
 * @param contentType Type of content to fetch
 * @param slug Slug of the content entry
 * @returns Promise resolving to the content entry or null if not found
 */
export const getContentBySlug = async <T = any>(
  contentType: ContentTypeValue,
  slug: string
): Promise<T | null> => {
  try {
    const client = getContentfulClient();
    
    // Build query for specific content type and slug
    const response = await client.getEntries({
      content_type: contentType,
      'fields.slug': slug,
      limit: 1
    });
    
    // If no entries found, return null
    if (response.items.length === 0) {
      return null;
    }
    
    // Transform and return the first entry
    return transformContentfulEntry(response.items[0]) as T;
  } catch (error) {
    logError(error, `Contentful getContentBySlug - ${contentType} - ${slug}`);
    throw error;
  }
};

/**
 * Fetches all slugs for a specific content type
 * @param contentType Type of content to fetch slugs for
 * @returns Promise resolving to an array of slugs
 */
export const getAllContentSlugs = async (
  contentType: ContentTypeValue
): Promise<string[]> => {
  try {
    const client = getContentfulClient();
    
    // Only fetch the slug field to optimize the request
    const response = await client.getEntries({
      content_type: contentType,
      select: 'fields.slug',
      limit: 1000 // Adjust based on expected content volume
    });
    
    // Extract and return slugs from response
    return response.items.map(item => item.fields.slug as string);
  } catch (error) {
    logError(error, `Contentful getAllContentSlugs - ${contentType}`);
    throw error;
  }
};

/**
 * Fetches services with optional category filtering
 * @param category Optional category to filter services by
 * @returns Promise resolving to an array of services
 */
export const getServices = async (category?: string): Promise<Service[]> => {
  try {
    const queryParams: ContentQueryParams = {
      contentType: ContentType.SERVICE,
      order: 'fields.order'
    };
    
    // Add category filter if provided
    if (category) {
      queryParams.filters = {
        'fields.category': category
      };
    }
    
    const response = await getContentfulEntries<Service>(queryParams);
    return response.items;
  } catch (error) {
    logError(error, 'Contentful getServices');
    throw error;
  }
};

/**
 * Fetches a service by its slug
 * @param slug Slug of the service to fetch
 * @returns Promise resolving to a service or null if not found
 */
export const getServiceBySlug = async (slug: string): Promise<Service | null> => {
  try {
    return await getContentBySlug<Service>(ContentType.SERVICE, slug);
  } catch (error) {
    logError(error, `Contentful getServiceBySlug - ${slug}`);
    throw error;
  }
};

/**
 * Fetches case studies with optional filtering
 * @param filters Optional filters to apply to the query
 * @returns Promise resolving to an array of case studies
 */
export const getCaseStudies = async (filters: Record<string, any> = {}): Promise<CaseStudy[]> => {
  try {
    const queryParams: ContentQueryParams = {
      contentType: ContentType.CASE_STUDY,
      filters,
      order: '-sys.createdAt' // Most recent first
    };
    
    const response = await getContentfulEntries<CaseStudy>(queryParams);
    return response.items;
  } catch (error) {
    logError(error, 'Contentful getCaseStudies');
    throw error;
  }
};

/**
 * Fetches a case study by its slug
 * @param slug Slug of the case study to fetch
 * @returns Promise resolving to a case study or null if not found
 */
export const getCaseStudyBySlug = async (slug: string): Promise<CaseStudy | null> => {
  try {
    return await getContentBySlug<CaseStudy>(ContentType.CASE_STUDY, slug);
  } catch (error) {
    logError(error, `Contentful getCaseStudyBySlug - ${slug}`);
    throw error;
  }
};

/**
 * Fetches impact stories with optional filtering
 * @param filters Optional filters to apply to the query
 * @returns Promise resolving to an array of impact stories
 */
export const getImpactStories = async (filters: Record<string, any> = {}): Promise<ImpactStory[]> => {
  try {
    const queryParams: ContentQueryParams = {
      contentType: ContentType.IMPACT_STORY,
      filters,
      order: '-sys.createdAt' // Most recent first
    };
    
    const response = await getContentfulEntries<ImpactStory>(queryParams);
    return response.items;
  } catch (error) {
    logError(error, 'Contentful getImpactStories');
    throw error;
  }
};

/**
 * Fetches an impact story by its slug
 * @param slug Slug of the impact story to fetch
 * @returns Promise resolving to an impact story or null if not found
 */
export const getImpactStoryBySlug = async (slug: string): Promise<ImpactStory | null> => {
  try {
    return await getContentBySlug<ImpactStory>(ContentType.IMPACT_STORY, slug);
  } catch (error) {
    logError(error, `Contentful getImpactStoryBySlug - ${slug}`);
    throw error;
  }
};

/**
 * Fetches blog posts with optional filtering
 * @param filters Optional filters to apply to the query
 * @returns Promise resolving to an array of blog posts
 */
export const getBlogPosts = async (filters: Record<string, any> = {}): Promise<BlogPost[]> => {
  try {
    const queryParams: ContentQueryParams = {
      contentType: ContentType.BLOG_POST,
      filters,
      order: '-fields.date' // Most recent first
    };
    
    const response = await getContentfulEntries<BlogPost>(queryParams);
    return response.items;
  } catch (error) {
    logError(error, 'Contentful getBlogPosts');
    throw error;
  }
};

/**
 * Fetches a blog post by its slug
 * @param slug Slug of the blog post to fetch
 * @returns Promise resolving to a blog post or null if not found
 */
export const getBlogPostBySlug = async (slug: string): Promise<BlogPost | null> => {
  try {
    return await getContentBySlug<BlogPost>(ContentType.BLOG_POST, slug);
  } catch (error) {
    logError(error, `Contentful getBlogPostBySlug - ${slug}`);
    throw error;
  }
};

/**
 * Fetches team members with optional filtering
 * @param filters Optional filters to apply to the query
 * @returns Promise resolving to an array of team members
 */
export const getTeamMembers = async (filters: Record<string, any> = {}): Promise<TeamMember[]> => {
  try {
    const queryParams: ContentQueryParams = {
      contentType: ContentType.TEAM_MEMBER,
      filters,
      order: 'fields.order' // Ordered by specified order
    };
    
    const response = await getContentfulEntries<TeamMember>(queryParams);
    return response.items;
  } catch (error) {
    logError(error, 'Contentful getTeamMembers');
    throw error;
  }
};

/**
 * Fetches a page by its slug
 * @param slug Slug of the page to fetch
 * @returns Promise resolving to a page or null if not found
 */
export const getPageBySlug = async (slug: string): Promise<Page | null> => {
  try {
    return await getContentBySlug<Page>(ContentType.PAGE, slug);
  } catch (error) {
    logError(error, `Contentful getPageBySlug - ${slug}`);
    throw error;
  }
};