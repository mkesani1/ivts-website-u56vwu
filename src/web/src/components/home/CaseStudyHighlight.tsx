import React, { useState, useEffect } from 'react'; // version 18.2.0
import classNames from 'classnames'; // version 2.3.2

import SectionHeader from '../shared/SectionHeader';
import CaseStudyCard from '../case-studies/CaseStudyCard';
import { CaseStudy } from '../../types/content';
import { getCaseStudies } from '../../services/contentService';
import { ROUTES } from '../../constants/routes';
import useAnalytics from '../../hooks/useAnalytics';

/**
 * Props for the CaseStudyHighlight component
 */
export interface CaseStudyHighlightProps {
  /**
   * Additional CSS class names
   */
  className?: string;
}

/**
 * A component that showcases featured case studies on the homepage, highlighting
 * successful client implementations of IndiVillage's AI services.
 * 
 * It displays case studies in an engaging format with images, client information,
 * and brief descriptions to demonstrate the company's expertise and success stories.
 * The component adapts to different screen sizes according to the responsive breakpoints
 * defined in the design system.
 */
const CaseStudyHighlight = ({ 
  className,
  ...props 
}: CaseStudyHighlightProps): JSX.Element => {
  // State for storing the case studies data
  const [caseStudies, setCaseStudies] = useState<CaseStudy[]>([]);
  // State for tracking loading status
  const [isLoading, setIsLoading] = useState<boolean>(true);
  // State for tracking error state
  const [error, setError] = useState<string | null>(null);

  // Get analytics tracking function
  const { trackEvent } = useAnalytics();

  // Fetch case studies when component mounts
  useEffect(() => {
    const fetchFeaturedCaseStudies = async () => {
      try {
        setIsLoading(true);
        setError(null);
        
        // Fetch case studies with a limit of 2 and filter for featured ones
        const fetchedCaseStudies = await getCaseStudies({ 
          limit: 2,
          featured: true 
        });
        
        setCaseStudies(fetchedCaseStudies);
        
        // Track successful case studies load
        trackEvent('case_study_highlight', 'loaded', {
          count: fetchedCaseStudies.length,
          location: 'homepage'
        });
      } catch (err) {
        console.error('Error fetching case studies:', err);
        setError('Failed to load case studies. Please try again later.');
        
        // Track error loading case studies
        trackEvent('case_study_highlight', 'error', {
          error_message: 'Failed to load case studies',
          location: 'homepage'
        });
      } finally {
        setIsLoading(false);
      }
    };

    fetchFeaturedCaseStudies();
  }, [trackEvent]);

  /**
   * Tracks click on "View All Case Studies" button
   */
  const handleViewAllClick = () => {
    trackEvent('case_study_highlight', 'view_all_click', {
      location: 'homepage'
    });
  };

  // Generate CSS classes
  const sectionClasses = classNames(
    'case-study-highlight',
    className
  );

  // Generate grid classes based on number of case studies and responsive breakpoints
  const gridClasses = classNames(
    'case-study-highlight__grid',
    {
      'case-study-highlight__grid--two-cols': caseStudies.length > 1,
      'case-study-highlight__grid--one-col': caseStudies.length === 1,
      'case-study-highlight__grid--empty': caseStudies.length === 0
    }
  );

  return (
    <section 
      className={sectionClasses} 
      aria-labelledby="case-studies-title"
      {...props}
    >
      <SectionHeader
        title="CASE STUDIES"
        subtitle="See how our AI solutions transform businesses"
        align="center"
        actionText="View All Case Studies"
        actionHref={ROUTES.CASE_STUDIES.INDEX}
        actionOnClick={handleViewAllClick}
      />

      {isLoading && (
        <div className="case-study-highlight__loading" aria-live="polite">
          <span className="sr-only">Loading case studies...</span>
        </div>
      )}

      {error && (
        <div className="case-study-highlight__error" aria-live="assertive" role="alert">
          <p>{error}</p>
        </div>
      )}

      {!isLoading && !error && (
        <div className={gridClasses}>
          {caseStudies.length > 0 ? (
            caseStudies.map((caseStudy) => (
              <CaseStudyCard
                key={caseStudy.id}
                caseStudy={caseStudy}
                className="case-study-highlight__card"
              />
            ))
          ) : (
            <div className="case-study-highlight__empty">
              <p>No case studies available at the moment.</p>
            </div>
          )}
        </div>
      )}
    </section>
  );
};

export default CaseStudyHighlight;