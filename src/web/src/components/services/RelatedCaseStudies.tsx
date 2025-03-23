import React from 'react';
import classNames from 'classnames'; // version 2.3.2
import { CaseStudy, Service } from '../../types/content';
import SectionHeader from '../shared/SectionHeader';
import CaseStudyCard from '../case-studies/CaseStudyCard';
import { ROUTES } from '../../constants/routes';
import useAnalytics from '../../hooks/useAnalytics';

/**
 * Props for the RelatedCaseStudies component
 */
export interface RelatedCaseStudiesProps {
  /**
   * Array of case studies to display
   */
  caseStudies: CaseStudy[];
  
  /**
   * The service that these case studies relate to
   */
  service?: Service;
  
  /**
   * Additional CSS class names
   */
  className?: string;
}

/**
 * Component that displays case studies related to a specific service,
 * showcasing real-world implementations of IndiVillage's AI solutions.
 */
const RelatedCaseStudies: React.FC<RelatedCaseStudiesProps> = ({
  caseStudies,
  service,
  className
}) => {
  // Get trackEvent function from useAnalytics hook
  const { trackEvent } = useAnalytics();
  
  // Don't render if there are no case studies to display
  if (!caseStudies || caseStudies.length === 0) {
    return null;
  }
  
  // Create section title based on service name if provided
  const title = service 
    ? `${service.title} Success Stories` 
    : 'Case Studies';
  
  // Create section subtitle highlighting real-world implementations
  const subtitle = 'Real-world implementations that delivered exceptional results';
  
  // Combine CSS class names
  const containerClasses = classNames(
    'related-case-studies',
    className
  );
  
  return (
    <section className={containerClasses} aria-labelledby="related-case-studies-title">
      <SectionHeader 
        title={title}
        subtitle={subtitle}
        actionText="View All Case Studies"
        actionHref={ROUTES.CASE_STUDIES.INDEX}
        id="related-case-studies-title"
      />
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mt-8">
        {caseStudies.map(caseStudy => (
          <div 
            key={caseStudy.id} 
            className="h-full"
            onClick={() => {
              // Track case study interaction for analytics
              trackEvent('case_study', 'click', {
                case_study_id: caseStudy.id,
                case_study_title: caseStudy.title,
                service_id: service?.id,
                service_name: service?.title,
                source: 'related_case_studies'
              });
            }}
          >
            <CaseStudyCard 
              caseStudy={caseStudy}
              className="h-full"
            />
          </div>
        ))}
      </div>
    </section>
  );
};

export default RelatedCaseStudies;