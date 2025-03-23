import { revalidatePath, revalidateTag } from 'next/cache'; // ^13.4.0
import { ContentType } from '../../../types/content';
import { getContentSlugs } from '../../../services/contentService';
import { logError } from '../../../utils/errorHandling';

// Environment variable for revalidation secret
const REVALIDATION_SECRET = process.env.REVALIDATION_SECRET;

/**
 * Validates the revalidation secret token from the request
 * @param secret Secret token to validate
 * @returns True if the secret is valid, false otherwise
 */
const validateSecret = (secret: string): boolean => {
  return secret === REVALIDATION_SECRET;
};

/**
 * Determines the paths to revalidate based on content type
 * @param contentType Type of content that was updated
 * @returns Array of paths to revalidate
 */
const getPathsForContentType = async (contentType: string): Promise<string[]> => {
  const paths: string[] = [];
  
  // Add base paths based on content type
  switch (contentType) {
    case ContentType.SERVICE:
      paths.push('/services');
      break;
    case ContentType.CASE_STUDY:
      paths.push('/case-studies');
      break;
    case ContentType.IMPACT_STORY:
      paths.push('/impact');
      break;
    case ContentType.BLOG_POST:
      paths.push('/blog');
      break;
    case ContentType.TEAM_MEMBER:
      paths.push('/about/leadership');
      break;
    case ContentType.PAGE:
      // For pages, we don't have a central listing page, just individual pages
      break;
    default:
      // If content type not specified or unknown, revalidate homepage
      paths.push('/');
      return paths;
  }
  
  // If there's a specific content type, get all slugs for that type
  if (Object.values(ContentType).includes(contentType as ContentType)) {
    try {
      const slugs = await getContentSlugs(contentType as ContentType);
      
      // Add specific paths based on content type and slugs
      switch (contentType) {
        case ContentType.SERVICE:
          slugs.forEach(slug => paths.push(`/services/${slug}`));
          break;
        case ContentType.CASE_STUDY:
          slugs.forEach(slug => paths.push(`/case-studies/${slug}`));
          break;
        case ContentType.IMPACT_STORY:
          slugs.forEach(slug => paths.push(`/impact/${slug}`));
          break;
        case ContentType.BLOG_POST:
          slugs.forEach(slug => paths.push(`/blog/${slug}`));
          break;
        case ContentType.PAGE:
          slugs.forEach(slug => paths.push(`/${slug}`));
          break;
      }
    } catch (error) {
      logError(error, `getPathsForContentType - ${contentType}`);
      // Continue with whatever paths we have so far
    }
  }
  
  // Always include the homepage which might have summary sections
  if (!paths.includes('/')) {
    paths.push('/');
  }
  
  return paths;
};

/**
 * Revalidates content based on content type and slug
 * @param contentType Type of content that was updated
 * @param slug Optional specific slug that was updated
 * @returns Array of revalidated paths
 */
const revalidateContent = async (contentType: string, slug?: string): Promise<string[]> => {
  const revalidatedPaths: string[] = [];
  
  // Get paths to revalidate based on content type
  const paths = await getPathsForContentType(contentType);
  
  // Revalidate each path
  for (const path of paths) {
    revalidatePath(path);
    revalidatedPaths.push(path);
  }
  
  // If a specific slug was provided, also ensure its specific path is revalidated
  if (slug) {
    let slugPath = '';
    
    switch (contentType) {
      case ContentType.SERVICE:
        slugPath = `/services/${slug}`;
        break;
      case ContentType.CASE_STUDY:
        slugPath = `/case-studies/${slug}`;
        break;
      case ContentType.IMPACT_STORY:
        slugPath = `/impact/${slug}`;
        break;
      case ContentType.BLOG_POST:
        slugPath = `/blog/${slug}`;
        break;
      case ContentType.PAGE:
        slugPath = `/${slug}`;
        break;
    }
    
    if (slugPath && !revalidatedPaths.includes(slugPath)) {
      revalidatePath(slugPath);
      revalidatedPaths.push(slugPath);
    }
  }
  
  return revalidatedPaths;
};

/**
 * Handles GET requests to the revalidation endpoint
 * @param request Request object
 * @returns JSON response indicating success or failure
 */
export async function GET(request: Request): Promise<Response> {
  // Extract URL parameters
  const { searchParams } = new URL(request.url);
  const secret = searchParams.get('secret');
  const contentType = searchParams.get('contentType');
  const slug = searchParams.get('slug');
  
  // Validate secret
  if (!validateSecret(secret || '')) {
    return new Response(JSON.stringify({ 
      success: false, 
      message: 'Invalid revalidation token' 
    }), {
      status: 401,
      headers: { 'Content-Type': 'application/json' }
    });
  }
  
  // Validate content type
  if (!contentType) {
    return new Response(JSON.stringify({ 
      success: false, 
      message: 'Content type is required' 
    }), {
      status: 400,
      headers: { 'Content-Type': 'application/json' }
    });
  }
  
  try {
    // Perform revalidation
    const revalidatedPaths = await revalidateContent(contentType, slug || undefined);
    
    // Return success response
    return new Response(JSON.stringify({ 
      success: true, 
      message: 'Revalidation successful',
      revalidatedPaths 
    }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' }
    });
  } catch (error) {
    // Log and handle errors
    logError(error, 'Revalidation API');
    
    return new Response(JSON.stringify({ 
      success: false, 
      message: 'Revalidation failed',
      error: error instanceof Error ? error.message : 'Unknown error'
    }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}

/**
 * Handles POST requests to the revalidation endpoint (for webhook integration)
 * @param request Request object
 * @returns JSON response indicating success or failure
 */
export async function POST(request: Request): Promise<Response> {
  try {
    // Parse request body as JSON
    const body = await request.json();
    const { secret, contentType, slug } = body;
    
    // Validate secret
    if (!validateSecret(secret || '')) {
      return new Response(JSON.stringify({ 
        success: false, 
        message: 'Invalid revalidation token' 
      }), {
        status: 401,
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    // Validate content type
    if (!contentType) {
      return new Response(JSON.stringify({ 
        success: false, 
        message: 'Content type is required' 
      }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    // Perform revalidation
    const revalidatedPaths = await revalidateContent(contentType, slug);
    
    // Return success response
    return new Response(JSON.stringify({ 
      success: true, 
      message: 'Revalidation successful',
      revalidatedPaths 
    }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' }
    });
  } catch (error) {
    // Log and handle errors
    logError(error, 'Revalidation API (POST)');
    
    return new Response(JSON.stringify({ 
      success: false, 
      message: 'Revalidation failed',
      error: error instanceof Error ? error.message : 'Unknown error'
    }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}