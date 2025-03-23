import React from 'react';
import Head from 'next/head'; // ^13.4.0
import { MetaData } from '../../types/common';
import {
  getDefaultMetaData,
  truncateDescription,
  createPageTitle,
  MAX_META_DESCRIPTION_LENGTH,
  MAX_OG_DESCRIPTION_LENGTH
} from '../../utils/seo';

/**
 * Interface for the MetaTags component props
 * Used to define and document the properties that can be passed to the MetaTags component
 */
export interface MetaTagsProps {
  /**
   * The page title
   */
  title?: string;
  
  /**
   * The page description for SEO
   */
  description?: string;
  
  /**
   * Keywords for SEO, used in meta keywords tag
   */
  keywords?: string[];
  
  /**
   * URL for the Open Graph image used in social sharing
   */
  ogImage?: string;
  
  /**
   * Canonical URL for the page to prevent duplicate content issues
   */
  canonicalUrl?: string;
}

/**
 * A reusable component for managing SEO metadata across the IndiVillage website
 * 
 * This component handles page titles, descriptions, Open Graph tags, and other metadata
 * for improved search engine visibility and social sharing. It uses Next.js Head component
 * to inject metadata into the document head.
 * 
 * @param props - Component props following MetaTagsProps interface
 * @returns React component with Next.js Head containing SEO metadata
 */
const MetaTags: React.FC<MetaTagsProps> = ({
  title,
  description,
  keywords,
  ogImage,
  canonicalUrl
}) => {
  // Get default metadata values
  const defaultMetadata = getDefaultMetaData();
  
  // Merge provided props with default metadata for consistency
  const metadata: MetaData = {
    title: title || defaultMetadata.title,
    description: description || defaultMetadata.description,
    keywords: keywords || defaultMetadata.keywords,
    ogImage: ogImage || defaultMetadata.ogImage,
    canonicalUrl: canonicalUrl || defaultMetadata.canonicalUrl
  };
  
  // Format the page title with site name
  const formattedTitle = createPageTitle(metadata.title);
  
  // Truncate descriptions to appropriate lengths for different meta tags
  const metaDescription = truncateDescription(metadata.description, MAX_META_DESCRIPTION_LENGTH);
  const ogDescription = truncateDescription(metadata.description, MAX_OG_DESCRIPTION_LENGTH);
  
  return (
    <Head>
      {/* Basic Meta Tags */}
      <title>{formattedTitle}</title>
      <meta name="description" content={metaDescription} />
      {metadata.keywords.length > 0 && (
        <meta name="keywords" content={metadata.keywords.join(', ')} />
      )}
      
      {/* Open Graph Meta Tags for social sharing */}
      <meta property="og:title" content={formattedTitle} />
      <meta property="og:description" content={ogDescription} />
      {metadata.ogImage && <meta property="og:image" content={metadata.ogImage} />}
      <meta property="og:type" content="website" />
      {metadata.canonicalUrl && <meta property="og:url" content={metadata.canonicalUrl} />}
      <meta property="og:site_name" content="IndiVillage" />
      <meta property="og:locale" content="en_US" />
      
      {/* Twitter Card Meta Tags */}
      <meta name="twitter:card" content="summary_large_image" />
      <meta name="twitter:title" content={formattedTitle} />
      <meta name="twitter:description" content={ogDescription} />
      {metadata.ogImage && <meta name="twitter:image" content={metadata.ogImage} />}
      
      {/* Canonical URL to prevent duplicate content issues */}
      {metadata.canonicalUrl && <link rel="canonical" href={metadata.canonicalUrl} />}
      
      {/* Other Essential Meta Tags */}
      <meta charSet="utf-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1" />
      <meta name="robots" content="index, follow" />
      <meta name="theme-color" content="#0055A4" />
    </Head>
  );
};

export default MetaTags;