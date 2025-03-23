import React from 'react'; // version 18.2.0
import Link from 'next/link'; // version 13.4.0
import classNames from 'classnames'; // version 2.3.2

import SectionHeader from '../shared/SectionHeader';
import ServiceCard from '../services/ServiceCard';
import Button from '../ui/Button';
import { ServiceCategory } from '../../types/content';
import { SERVICE_CATEGORIES, SERVICE_ICONS, SERVICE_DESCRIPTIONS } from '../../constants/services';
import { ROUTES } from '../../constants/routes';

/**
 * Interface defining the props for the ServiceOverview component
 */
export interface ServiceOverviewProps {
  /**
   * Additional CSS classes to apply to the component
   */
  className?: string;
}

/**
 * Component that renders an overview of IndiVillage's AI services on the homepage.
 * Displays a grid of service cards for the four main service categories:
 * Data Collection, Data Preparation, AI Model Development, and Human-in-the-Loop.
 * 
 * The grid layout is responsive and adapts based on device breakpoints:
 * - Mobile (< 768px): Single column
 * - Tablet (768px - 1023px): Two columns
 * - Desktop (≥ 1024px): Four columns
 */
const ServiceOverview: React.FC<ServiceOverviewProps> = ({ 
  className,
  ...rest
}) => {
  // Create an array of service objects from the service categories constants
  const services = [
    {
      title: SERVICE_CATEGORIES[ServiceCategory.DATA_COLLECTION].title,
      description: SERVICE_CATEGORIES[ServiceCategory.DATA_COLLECTION].description,
      category: ServiceCategory.DATA_COLLECTION,
      icon: { url: SERVICE_ICONS[ServiceCategory.DATA_COLLECTION] }
    },
    {
      title: SERVICE_CATEGORIES[ServiceCategory.DATA_PREPARATION].title,
      description: SERVICE_CATEGORIES[ServiceCategory.DATA_PREPARATION].description,
      category: ServiceCategory.DATA_PREPARATION,
      icon: { url: SERVICE_ICONS[ServiceCategory.DATA_PREPARATION] }
    },
    {
      title: SERVICE_CATEGORIES[ServiceCategory.AI_MODEL_DEVELOPMENT].title,
      description: SERVICE_CATEGORIES[ServiceCategory.AI_MODEL_DEVELOPMENT].description,
      category: ServiceCategory.AI_MODEL_DEVELOPMENT,
      icon: { url: SERVICE_ICONS[ServiceCategory.AI_MODEL_DEVELOPMENT] }
    },
    {
      title: SERVICE_CATEGORIES[ServiceCategory.HUMAN_IN_THE_LOOP].title,
      description: SERVICE_CATEGORIES[ServiceCategory.HUMAN_IN_THE_LOOP].description,
      category: ServiceCategory.HUMAN_IN_THE_LOOP,
      icon: { url: SERVICE_ICONS[ServiceCategory.HUMAN_IN_THE_LOOP] }
    }
  ];

  return (
    <section className={classNames('service-overview', className)} {...rest}>
      <div className="container">
        <SectionHeader 
          title="OUR SERVICES"
          className="service-overview__header"
        />
        
        <div className="service-overview__grid">
          {services.map((service) => (
            <ServiceCard
              key={service.category}
              service={service}
              className="service-overview__card"
            />
          ))}
        </div>
        
        <div className="service-overview__action">
          <Link href={ROUTES.SERVICES.INDEX}>
            <Button variant="primary">View All Services</Button>
          </Link>
        </div>
      </div>
    </section>
  );
};

export default ServiceOverview;