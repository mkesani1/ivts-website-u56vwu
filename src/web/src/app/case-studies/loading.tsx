import React from 'react'; // version 18.2.0
import Loader from '../../components/ui/Loader';
import { Size } from '../../types/common';
import PageHeader from '../../components/shared/PageHeader';
import Card from '../../components/ui/Card';

/**
 * A loading component specifically for the case studies section that is automatically
 * used by Next.js when case studies content is loading. This provides visual feedback
 * during page transitions and content loading.
 * 
 * @returns {JSX.Element} Rendered loading component
 */
const Loading = (): JSX.Element => {
  return (
    <div className="case-studies-container" aria-busy="true">
      {/* Skeleton for page header */}
      <PageHeader 
        title="Loading Case Studies..." 
        className="page-header--skeleton"
      />
      
      {/* Skeleton for filter bar */}
      <div className="filter-bar filter-bar--skeleton">
        <div className="filter-bar__placeholder"></div>
        <div className="filter-bar__options">
          <span className="filter-bar__option filter-bar__option--skeleton"></span>
          <span className="filter-bar__option filter-bar__option--skeleton"></span>
          <span className="filter-bar__option filter-bar__option--skeleton"></span>
        </div>
      </div>
      
      {/* Skeleton grid for case study cards */}
      <div className="case-studies-grid">
        {Array.from({ length: 6 }).map((_, index) => (
          <Card 
            key={`skeleton-card-${index}`} 
            className="case-study-card case-study-card--skeleton"
            elevation={1}
          >
            <div className="case-study-card__image-placeholder"></div>
            <div className="case-study-card__content">
              <div className="case-study-card__title-placeholder"></div>
              <div className="case-study-card__subtitle-placeholder"></div>
              <div className="case-study-card__text-placeholder"></div>
              <div className="case-study-card__text-placeholder"></div>
              <div className="case-study-card__text-placeholder"></div>
            </div>
          </Card>
        ))}
      </div>
      
      {/* Central loader spinner */}
      <div className="loader-container" role="status" aria-live="polite">
        <Loader size={Size.LARGE} />
        <span className="sr-only">Loading case studies, please wait...</span>
      </div>
    </div>
  );
};

export default Loading;