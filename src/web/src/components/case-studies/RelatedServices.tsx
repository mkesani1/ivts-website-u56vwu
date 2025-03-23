import React from 'react'; // version 18.2.0
import classNames from 'classnames'; // version 2.3.2

import ServiceCard from '../services/ServiceCard';
import { Service } from '../../types/content';

/**
 * Interface defining the props for the RelatedServices component
 */
export interface RelatedServicesProps {
  /**
   * Array of services related to the case study
   */
  services: Service[];
  
  /**
   * Additional CSS classes to apply to the component
   */
  className?: string;
}

/**
 * A component that displays a grid of related services for a case study.
 * This component is used in the case study detail page to showcase the AI services 
 * that were utilized in the featured case study, providing users with easy 
 * navigation to learn more about those services.
 * 
 * @param props - Component props containing services and optional className
 * @returns JSX.Element or null if no services to display
 */
const RelatedServices = ({
  services,
  className
}: RelatedServicesProps): JSX.Element | null => {
  // Return null if no services to display
  if (!services || services.length === 0) {
    return null;
  }

  return (
    <section className={classNames('related-services py-8 md:py-12', className)}>
      <h2 className="related-services__title text-2xl md:text-3xl font-bold mb-6">
        Related Services
      </h2>
      
      <div className="related-services__grid grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 md:gap-6">
        {services.map((service) => (
          <ServiceCard 
            key={service.id} 
            service={service}
            className="related-services__card"
          />
        ))}
      </div>
    </section>
  );
};

export default RelatedServices;