import React from 'react'; // version 18.2.0
import Link from 'next/link'; // version 13.4.0
import Image from 'next/image'; // version 13.4.0
import classNames from 'classnames'; // version 2.3.2

import Card from '../ui/Card';
import Button from '../ui/Button';
import { Service, ServiceCategory, ServiceCategoryValue } from '../../types/content';
import { ROUTES } from '../../constants/routes';
import { SERVICE_ICONS } from '../../constants/services';

/**
 * Interface defining the props for the ServiceCard component
 */
export interface ServiceCardProps {
  /**
   * Service data to display in the card
   */
  service: Service | {
    title: string;
    description: string;
    category: ServiceCategoryValue;
    slug?: string;
    icon?: { url: string };
  };
  
  /**
   * Additional CSS classes to apply to the component
   */
  className?: string;
}

/**
 * Generates the URL for a service detail page based on the service slug or category
 * 
 * @param service - Service object with either a slug or category
 * @returns URL path to the service detail page
 */
const getServiceUrl = (
  service: Service | { category: ServiceCategoryValue; slug?: string }
): string => {
  // If the service has a slug, use it to generate a dynamic route
  if ('slug' in service && service.slug) {
    return ROUTES.SERVICES.DETAIL.replace('[slug]', service.slug);
  }
  
  // Otherwise, use the category to determine the appropriate route
  switch (service.category) {
    case ServiceCategory.DATA_COLLECTION:
      return ROUTES.SERVICES.DATA_COLLECTION;
    case ServiceCategory.DATA_PREPARATION:
      return ROUTES.SERVICES.DATA_PREPARATION;
    case ServiceCategory.AI_MODEL_DEVELOPMENT:
      return ROUTES.SERVICES.AI_MODEL_DEVELOPMENT;
    case ServiceCategory.HUMAN_IN_THE_LOOP:
      return ROUTES.SERVICES.HUMAN_IN_THE_LOOP;
    default:
      return ROUTES.SERVICES.INDEX;
  }
};

/**
 * Gets the source URL for the service icon, using either the provided icon asset
 * or a fallback from SERVICE_ICONS
 * 
 * @param service - Service object with either an icon asset or category
 * @returns URL for the service icon
 */
const getIconSrc = (
  service: Service | { category: ServiceCategoryValue; icon?: { url: string } }
): string => {
  // If the service has an icon with a URL, use it
  if ('icon' in service && service.icon && service.icon.url) {
    return service.icon.url;
  }
  
  // Otherwise, return the fallback icon based on the service category
  return SERVICE_ICONS[service.category];
};

/**
 * Component that renders a card displaying a service with its icon, title,
 * description, and a call-to-action button to learn more about the service.
 * Used throughout the website to showcase IndiVillage's AI-as-a-service offerings.
 */
const ServiceCard = ({
  service,
  className,
  ...rest
}: ServiceCardProps): JSX.Element => {
  // Get the URL for the service detail page
  const serviceUrl = getServiceUrl(service);
  
  // Get the icon source URL
  const iconSrc = getIconSrc(service);
  
  return (
    <Card 
      className={classNames('service-card', className)}
      hoverable
      {...rest}
    >
      <div className="service-card__content">
        <div className="service-card__icon-container">
          <Image
            src={iconSrc}
            alt={`${service.title} icon`}
            width={64}
            height={64}
            className="service-card__icon"
          />
        </div>
        
        <h3 className="service-card__title">{service.title}</h3>
        
        <p className="service-card__description">{service.description}</p>
        
        <div className="service-card__action">
          <Link href={serviceUrl}>
            <Button 
              variant="tertiary" 
              icon="arrowRight" 
              iconPosition="right"
            >
              Learn More
            </Button>
          </Link>
        </div>
      </div>
    </Card>
  );
};

export default ServiceCard;