import React from 'react';
import Loader from '../../components/ui/Loader';
import { Size } from '../../types/common';
import PageHeader from '../../components/shared/PageHeader';

/**
 * A loading component for the blog section that provides visual feedback during 
 * page transitions and content loading in the Next.js app router.
 * This component is automatically used by Next.js when blog content is being loaded.
 */
export default function Loading() {
  return (
    <div className="blog-section blog-loading">
      {/* Skeleton for the page header */}
      <div className="blog-header-skeleton">
        <PageHeader title="Blog" />
      </div>
      
      {/* Skeleton for the blog post grid */}
      <div className="blog-posts-grid">
        {/* Generate 6 skeleton blog post cards */}
        {Array.from({ length: 6 }).map((_, index) => (
          <div key={index} className="blog-post-skeleton" aria-hidden="true">
            {/* Image placeholder */}
            <div className="blog-post-skeleton-image pulse-animation" />
            
            {/* Content placeholders */}
            <div className="blog-post-skeleton-content">
              <div className="blog-post-skeleton-title pulse-animation" />
              <div className="blog-post-skeleton-date pulse-animation" />
              <div className="blog-post-skeleton-excerpt pulse-animation" />
              <div className="blog-post-skeleton-excerpt pulse-animation" />
              <div className="blog-post-skeleton-excerpt pulse-animation shorter-width" />
            </div>
          </div>
        ))}
      </div>
      
      {/* Main loading indicator */}
      <div className="blog-loading-indicator" role="status" aria-live="polite">
        <Loader 
          size={Size.LARGE}
          className="blog-main-loader"
        />
        <span className="sr-only">Loading blog content...</span>
      </div>
    </div>
  );
}