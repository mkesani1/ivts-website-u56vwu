/**
 * Utility functions for managing SEO (Search Engine Optimization) metadata across the IndiVillage website.
 * This module provides functions for generating canonical URLs, creating default metadata,
 * truncating descriptions to appropriate lengths for meta tags, and other SEO-related utilities.
 */

import { Metadata } from 'next'; // ^13.4.0
import { MetaData } from '../types/common';
import { ROUTES } from '../constants/routes';
import { truncateText } from './formatting';

// Base URL for canonical URL generation
export const BASE_URL = 'https://indivillage.com';

// Default SEO metadata values
export const DEFAULT_TITLE = 'IndiVillage - AI-Powered Solutions with Social Impact';
export const DEFAULT_DESCRIPTION = 'Transform your business with AI solutions that create positive social change. IndiVillage offers data collection, preparation, AI model development, and human-in-the-loop services.';
export const DEFAULT_KEYWORDS = ['AI services', 'data collection', 'data preparation', 'AI model development', 'human-in-the-loop', 'social impact', 'AI for good'];
export const DEFAULT_OG_IMAGE = '/images/og-image.jpg';

// Maximum lengths for metadata fields
export const MAX_META_DESCRIPTION_LENGTH = 160;
export const MAX_OG_DESCRIPTION_LENGTH = 200;

/**
 * Generates a canonical URL for a given path
 * 
 * @param path - The path to generate a canonical URL for
 * @returns The full canonical URL
 */
export const getCanonicalUrl = (path: string): string => {
  if (typeof path !== 'string') {
    return BASE_URL;
  }

  // If path is empty or just the homepage, return the base URL
  if (!path || path === '/') {
    return BASE_URL;
  }

  // Ensure path starts with a forward slash
  const normalizedPath = path.startsWith('/') ? path : `/${path}`;
  
  // Combine base URL with normalized path
  return `${BASE_URL}${normalizedPath}`;
};

/**
 * Truncates a description to the appropriate length for meta tags
 * 
 * @param description - The description to truncate
 * @param maxLength - Maximum length for the description
 * @returns Truncated description
 */
export const truncateDescription = (description: string, maxLength: number): string => {
  if (typeof description !== 'string') {
    return '';
  }

  if (!description) {
    return '';
  }

  return truncateText(description, maxLength);
};

/**
 * Returns default metadata for the website
 * 
 * @returns Default metadata object
 */
export const getDefaultMetaData = (): MetaData => {
  return {
    title: DEFAULT_TITLE,
    description: DEFAULT_DESCRIPTION,
    keywords: DEFAULT_KEYWORDS,
    ogImage: DEFAULT_OG_IMAGE,
    canonicalUrl: getCanonicalUrl(ROUTES.HOME)
  };
};

/**
 * Generates metadata for Next.js App Router
 * 
 * @param customMetadata - Custom metadata to merge with defaults
 * @returns Next.js Metadata object
 */
export const generateMetadata = (customMetadata: MetaData): Metadata => {
  // Get default metadata
  const defaultMetadata = getDefaultMetaData();
  
  // Merge custom metadata with defaults
  const metadata = {
    ...defaultMetadata,
    ...customMetadata
  };
  
  // Truncate descriptions to appropriate lengths
  const metaDescription = truncateDescription(metadata.description, MAX_META_DESCRIPTION_LENGTH);
  const ogDescription = truncateDescription(metadata.description, MAX_OG_DESCRIPTION_LENGTH);
  
  // Format according to Next.js Metadata structure
  return {
    title: metadata.title,
    description: metaDescription,
    keywords: metadata.keywords,
    openGraph: {
      title: metadata.title,
      description: ogDescription,
      images: [
        {
          url: metadata.ogImage || DEFAULT_OG_IMAGE,
          alt: metadata.title
        }
      ],
      url: metadata.canonicalUrl,
      siteName: 'IndiVillage',
      type: 'website',
      locale: 'en_US'
    },
    twitter: {
      card: 'summary_large_image',
      title: metadata.title,
      description: ogDescription,
      images: [metadata.ogImage || DEFAULT_OG_IMAGE]
    },
    alternates: {
      canonical: metadata.canonicalUrl
    }
  };
};

/**
 * Creates a formatted page title with site name
 * 
 * @param pageTitle - The page-specific title
 * @returns Formatted page title
 */
export const createPageTitle = (pageTitle: string): string => {
  if (typeof pageTitle !== 'string' || !pageTitle.trim()) {
    return DEFAULT_TITLE;
  }

  return `${pageTitle} | IndiVillage`;
};