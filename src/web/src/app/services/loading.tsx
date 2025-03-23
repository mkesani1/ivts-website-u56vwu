import React from 'react'; // version 18.2.0
import Loader from '../../../components/ui/Loader';
import { Size } from '../../../types/common';
import PageHeader from '../../../components/shared/PageHeader';

/**
 * A loading component that displays a skeleton UI for the services page during loading.
 * This component is automatically used by Next.js during page transitions and
 * initial loading of the services page.
 * 
 * @returns Rendered loading component
 */
const Loading = (): JSX.Element => {
  return (
    <div className="services-page-container" aria-busy="true">
      <PageHeader title="Our Services" />
      
      <div className="services-grid">
        {/* Generate 4 placeholder cards for the services */}
        {Array.from({ length: 4 }).map((_, index) => (
          <div 
            key={`service-placeholder-${index}`} 
            className="service-card service-card-placeholder"
            aria-hidden="true"
          >
            <div className="service-card-icon-placeholder" />
            <div className="service-card-title-placeholder" />
            <div className="service-card-description-placeholder" />
            <div className="service-card-cta-placeholder" />
          </div>
        ))}
      </div>
      
      <div className="loading-indicator-container">
        <Loader size={Size.LARGE} color="#0055A4" />
        <span className="sr-only">Loading services, please wait.</span>
      </div>
    </div>
  );
};

export default Loading;