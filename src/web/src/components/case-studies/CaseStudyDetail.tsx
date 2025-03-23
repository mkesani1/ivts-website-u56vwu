import React, { useEffect } from 'react'; // react@18.2.0
import classNames from 'classnames'; // classnames@2.3.2
import PageHeader from '../shared/PageHeader';
import MetaTags from '../shared/MetaTags';
import CaseStudyResults from './CaseStudyResults';
import ServiceCard from '../services/ServiceCard';
import ImageWithFallback from '../shared/ImageWithFallback';
import { BreadcrumbItem } from '../ui/Breadcrumb';
import { CaseStudy } from '../../types/content';
import { ROUTES } from '../../constants/routes';
import useAnalytics from '../../hooks/useAnalytics';

/**
 * Interface for CaseStudyDetail component props
 */
export interface CaseStudyDetailProps {
  /**
   * Case study data to display
   */
  caseStudy: CaseStudy;
  
  /**
   * Additional CSS class name
   */
  className?: string;
}

/**
 * A component that displays the detailed view of a case study, showcasing client success stories
 * with comprehensive information about challenges, solutions, results, and related services.
 * This component serves as the main content for individual case study pages.
 */
const CaseStudyDetail: React.FC<CaseStudyDetailProps> = ({
  caseStudy,
  className
}) => {
  // Get analytics tracking function
  const { trackCaseStudyView } = useAnalytics();
  
  // Track case study view when component mounts
  useEffect(() => {
    if (caseStudy) {
      const serviceIds = caseStudy.services.map(service => service.id);
      trackCaseStudyView(caseStudy.id, caseStudy.title, serviceIds);
    }
  }, [caseStudy, trackCaseStudyView]);
  
  // If no case study is provided, return null
  if (!caseStudy) {
    return null;
  }
  
  // Create breadcrumb items for navigation
  const breadcrumbs: BreadcrumbItem[] = [
    { label: 'Home', href: '/' },
    { label: 'Case Studies', href: ROUTES.CASE_STUDIES.INDEX },
    { label: caseStudy.title, href: ROUTES.CASE_STUDIES.DETAIL.replace('[slug]', caseStudy.slug), current: true },
  ];
  
  return (
    <main className={classNames('case-study-detail max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8', className)}>
      {/* SEO metadata */}
      <MetaTags 
        title={`${caseStudy.title} - Case Study`}
        description={`Learn how ${caseStudy.client} overcame challenges with IndiVillage's AI solutions. ${caseStudy.challenge.substring(0, 100)}...`}
        ogImage={caseStudy.image?.url}
      />
      
      {/* Page header with breadcrumbs */}
      <PageHeader
        title={caseStudy.title}
        subtitle={`Client: ${caseStudy.client} | Industry: ${caseStudy.industry?.name || 'Various Industries'}`}
        breadcrumbs={breadcrumbs}
      />
      
      {/* Case study hero image */}
      {caseStudy.image && (
        <div className="case-study-image-container mb-8">
          <ImageWithFallback
            src={caseStudy.image.url}
            alt={`${caseStudy.client} case study featuring ${caseStudy.title}`}
            width={1200}
            height={630}
            className="w-full h-auto rounded-lg shadow-md object-cover"
            priority={true}
          />
        </div>
      )}
      
      {/* Content sections */}
      <div className="case-study-content grid grid-cols-1 lg:grid-cols-2 gap-8 mb-12">
        {/* Challenge section */}
        <section 
          className="case-study-challenge" 
          aria-labelledby="challenge-heading"
        >
          <h2 
            id="challenge-heading" 
            className="text-2xl font-bold text-primary mb-4"
          >
            Challenge
          </h2>
          <div className="prose prose-lg max-w-none">
            {caseStudy.challenge.split('\n').map((paragraph, index) => (
              paragraph ? <p key={`challenge-p-${index}`}>{paragraph}</p> : null
            ))}
          </div>
        </section>
        
        {/* Solution section */}
        <section 
          className="case-study-solution" 
          aria-labelledby="solution-heading"
        >
          <h2 
            id="solution-heading" 
            className="text-2xl font-bold text-primary mb-4"
          >
            Solution
          </h2>
          <div className="prose prose-lg max-w-none">
            {caseStudy.solution.split('\n').map((paragraph, index) => (
              paragraph ? <p key={`solution-p-${index}`}>{paragraph}</p> : null
            ))}
          </div>
        </section>
      </div>
      
      {/* Results section */}
      {caseStudy.results && caseStudy.results.length > 0 && (
        <section 
          className="case-study-results mb-12" 
          aria-labelledby="results-heading"
        >
          <h2 
            id="results-heading" 
            className="text-2xl font-bold text-primary mb-6"
          >
            Results
          </h2>
          <CaseStudyResults results={caseStudy.results} />
        </section>
      )}
      
      {/* Related services section */}
      {caseStudy.services && caseStudy.services.length > 0 && (
        <section 
          className="case-study-related-services" 
          aria-labelledby="related-services-heading"
        >
          <h2 
            id="related-services-heading" 
            className="text-2xl font-bold text-primary mb-6"
          >
            Related Services
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {caseStudy.services.map(service => (
              <ServiceCard 
                key={service.id} 
                service={service} 
              />
            ))}
          </div>
        </section>
      )}
    </main>
  );
};

export default CaseStudyDetail;