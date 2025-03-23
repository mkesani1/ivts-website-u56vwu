import { NextRequest, NextResponse } from 'next/server'; // next/server ^13.4.0
import { ROUTES } from '../constants/routes';
import { logError } from './utils/errorHandling';
import { trackPageView } from './lib/analytics';

// Debug mode flag
const DEBUG_MODE = process.env.NODE_ENV === 'development';

// Very simple rate limiter that can detect basic abuse patterns
// Note: This is not a production-grade solution as it uses in-memory storage
const requestCounts: Record<string, { timestamp: number, count: number }> = {};

/**
 * Adds security headers to the response
 * @param response The Next.js response object
 * @returns Response with security headers added
 */
function addSecurityHeaders(response: NextResponse): NextResponse {
  // Content Security Policy
  // This header helps prevent XSS attacks by specifying which resources can be loaded
  response.headers.set(
    'Content-Security-Policy',
    "default-src 'self'; " +
    "script-src 'self' https://www.googletagmanager.com https://www.google-analytics.com https://www.gstatic.com https://www.google.com https://www.gstatic.com 'unsafe-inline'; " +
    "style-src 'self' https://fonts.googleapis.com 'unsafe-inline'; " +
    "img-src 'self' https://www.google-analytics.com https://www.googletagmanager.com data: blob:; " +
    "font-src 'self' https://fonts.gstatic.com data:; " +
    "connect-src 'self' https://www.google-analytics.com https://analytics.google.com; " +
    "frame-src 'self' https://www.google.com https://www.youtube.com; " +
    "object-src 'none';"
  );

  // XSS Protection
  // Enables browser's built-in reflected XSS protection
  response.headers.set('X-XSS-Protection', '1; mode=block');

  // Frame Options
  // Prevents clickjacking attacks by ensuring the page cannot be embedded in an iframe
  response.headers.set('X-Frame-Options', 'SAMEORIGIN');

  // Content Type Options
  // Prevents MIME type sniffing, which can lead to security vulnerabilities
  response.headers.set('X-Content-Type-Options', 'nosniff');

  // Referrer Policy
  // Controls what information is sent in the Referer header
  response.headers.set('Referrer-Policy', 'strict-origin-when-cross-origin');

  // Permissions Policy
  // Controls which browser features and APIs can be used
  response.headers.set(
    'Permissions-Policy',
    'camera=(), microphone=(), geolocation=(), interest-cohort=()'
  );

  // Strict Transport Security
  // Ensures the site is always loaded over HTTPS
  if (!DEBUG_MODE) {
    response.headers.set('Strict-Transport-Security', 'max-age=63072000; includeSubDomains; preload');
  }

  return response;
}

/**
 * Handles redirects based on request path
 * @param request The Next.js request object
 * @returns Redirect response or null if no redirect needed
 */
function handleRedirects(request: NextRequest): NextResponse | null {
  const url = new URL(request.url);
  const { pathname } = url;
  let redirectTo: string | null = null;

  // Legacy URL patterns redirect
  if (pathname.startsWith('/services-overview')) {
    redirectTo = ROUTES.SERVICES.INDEX;
  } else if (pathname.startsWith('/about-us')) {
    redirectTo = ROUTES.ABOUT.INDEX;
  } else if (pathname.startsWith('/our-impact')) {
    redirectTo = ROUTES.IMPACT.INDEX;
  } else if (pathname.startsWith('/showcase')) {
    redirectTo = ROUTES.CASE_STUDIES.INDEX;
  } else if (pathname.startsWith('/news')) {
    redirectTo = ROUTES.BLOG.INDEX;
  } else if (pathname.startsWith('/contact-us')) {
    redirectTo = ROUTES.CONTACT;
  } else if (pathname.startsWith('/request-a-demo')) {
    redirectTo = ROUTES.REQUEST_DEMO;
  } else if (pathname.startsWith('/upload')) {
    redirectTo = ROUTES.UPLOAD_SAMPLE.INDEX;
  }

  // Enforce trailing slash consistency
  // We're choosing to remove trailing slashes for consistency
  if (pathname !== '/' && pathname.endsWith('/')) {
    redirectTo = pathname.slice(0, -1) + (url.search || '');
  }

  // Handle uppercase letters in paths
  const lowercasePath = pathname.toLowerCase();
  if (pathname !== lowercasePath && !pathname.includes('/api/')) {
    redirectTo = lowercasePath + (url.search || '');
  }

  // Return redirect response if needed
  if (redirectTo) {
    const statusCode = 308; // Permanent Redirect
    return NextResponse.redirect(new URL(redirectTo, request.url), {
      status: statusCode,
      headers: {
        'Cache-Control': 'public, max-age=86400, s-maxage=86400', // Cache for 24 hours
      },
    });
  }

  return null;
}

/**
 * Basic rate limiting check for sensitive routes
 * @param request The Next.js request object
 * @returns NextResponse with 429 status if rate limited, null otherwise
 */
function checkRateLimit(request: NextRequest): NextResponse | null {
  const { pathname } = new URL(request.url);
  
  // Only rate limit specific sensitive routes
  const sensitiveRoutes = [
    ROUTES.UPLOAD_SAMPLE.INDEX,
    ROUTES.REQUEST_DEMO,
    ROUTES.CONTACT,
  ];
  
  if (!sensitiveRoutes.some(route => pathname.startsWith(route))) {
    return null;
  }
  
  // Get a key for the requester (IP or header)
  // In production, this should use a more reliable identifier
  const ip = request.ip || 
             request.headers.get('x-forwarded-for') || 
             'unknown';
  
  const key = `${ip}:${pathname}`;
  const now = Date.now();
  const windowMs = 60 * 1000; // 1 minute window
  const maxRequests = 10; // Max requests per window
  
  // Initialize or reset if window has passed
  if (!requestCounts[key] || now - requestCounts[key].timestamp > windowMs) {
    requestCounts[key] = { timestamp: now, count: 1 };
    return null;
  }
  
  // Increment the counter
  requestCounts[key].count++;
  
  // Check if over the limit
  if (requestCounts[key].count > maxRequests) {
    return NextResponse.json(
      { error: 'Too many requests. Please try again later.' },
      { 
        status: 429, 
        headers: {
          'Retry-After': '60',
          'X-RateLimit-Limit': maxRequests.toString(),
          'X-RateLimit-Remaining': '0',
          'X-RateLimit-Reset': Math.ceil((requestCounts[key].timestamp + windowMs) / 1000).toString()
        }
      }
    );
  }
  
  return null;
}

/**
 * Determines if middleware should be applied to the current request
 * @param request The Next.js request object
 * @returns True if middleware should be applied, false otherwise
 */
function shouldApplyMiddleware(request: NextRequest): boolean {
  const { pathname } = new URL(request.url);

  // Skip middleware for static files
  if (
    pathname.startsWith('/_next/') ||
    pathname.startsWith('/favicon.ico') ||
    pathname.startsWith('/robots.txt') ||
    pathname.startsWith('/sitemap.xml') ||
    pathname.match(/\.(ico|png|jpg|jpeg|svg|css|js|woff|woff2|ttf)$/i)
  ) {
    return false;
  }

  // Skip middleware for API routes
  if (pathname.startsWith('/api/')) {
    return false;
  }

  return true;
}

/**
 * Main middleware function that processes requests
 * @param request The Next.js request object
 * @returns Processed response
 */
export function middleware(request: NextRequest): NextResponse {
  try {
    // Check if middleware should be applied to this request
    if (!shouldApplyMiddleware(request)) {
      return NextResponse.next();
    }

    // Handle redirects
    const redirectResponse = handleRedirects(request);
    if (redirectResponse) {
      return redirectResponse;
    }

    // Check rate limits for sensitive routes
    const rateLimitResponse = checkRateLimit(request);
    if (rateLimitResponse) {
      return rateLimitResponse;
    }

    // Continue with the request
    const response = NextResponse.next();

    // Add security headers
    const secureResponse = addSecurityHeaders(response);

    // Track page view for analytics, but not in development
    if (!DEBUG_MODE) {
      const { pathname } = new URL(request.url);
      trackPageView(pathname);
    }

    return secureResponse;
  } catch (error) {
    // Log any errors that occur in middleware
    logError(error, 'middleware');
    
    // Always continue with the request even if middleware fails
    return NextResponse.next();
  }
}

/**
 * Configuration object for the middleware, specifying which paths it should run on
 */
export const config = {
  // Match all paths except static files and images
  matcher: ['/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)'],
};