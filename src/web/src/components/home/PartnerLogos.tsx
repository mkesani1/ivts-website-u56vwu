import React from 'react'; // version 18.2.0
import classNames from 'classnames'; // version 2.3.2
import SectionHeader from '../shared/SectionHeader';
import Carousel from '../shared/Carousel';
import ImageWithFallback from '../shared/ImageWithFallback';
import useBreakpoint from '../../hooks/useBreakpoint';
import { Breakpoint } from '../../types/common';

export interface PartnerLogosProps {
  /**
   * Additional CSS class names to apply to the component
   */
  className?: string;
}

export interface PartnerLogo {
  /**
   * Unique identifier for the partner
   */
  id: string;
  
  /**
   * Path to the partner's logo image
   */
  src: string;
  
  /**
   * Alt text describing the partner company
   */
  alt: string;
}

/**
 * Returns an array of partner logo data
 * In a real application, this might come from an API or CMS
 */
function getPartnerLogos(): PartnerLogo[] {
  return [
    {
      id: 'microsoft',
      src: '/images/partners/microsoft-logo.png',
      alt: 'Microsoft'
    },
    {
      id: 'google',
      src: '/images/partners/google-logo.png',
      alt: 'Google'
    },
    {
      id: 'amazon',
      src: '/images/partners/amazon-logo.png',
      alt: 'Amazon'
    },
    {
      id: 'ibm',
      src: '/images/partners/ibm-logo.png',
      alt: 'IBM'
    },
    {
      id: 'salesforce',
      src: '/images/partners/salesforce-logo.png',
      alt: 'Salesforce'
    },
    {
      id: 'oracle',
      src: '/images/partners/oracle-logo.png',
      alt: 'Oracle'
    }
  ];
}

/**
 * A component that displays a carousel of partner company logos on the IndiVillage homepage
 * to showcase trusted clients and build credibility with website visitors.
 */
const PartnerLogos: React.FC<PartnerLogosProps> = ({ className, ...rest }) => {
  // Get current breakpoint for responsive behavior
  const breakpoint = useBreakpoint();
  
  // Get partner logos data
  const partnerLogos = getPartnerLogos();
  
  // Determine number of logos to show based on current breakpoint
  let itemsToShow = 5; // Default for larger screens
  
  if (breakpoint === Breakpoint.MOBILE_SMALL || breakpoint === Breakpoint.MOBILE) {
    itemsToShow = 1;
  } else if (breakpoint === Breakpoint.TABLET) {
    itemsToShow = 3;
  } else if (breakpoint === Breakpoint.DESKTOP) {
    itemsToShow = 4;
  }
  
  // Generate container class names
  const containerClasses = classNames(
    'partner-logos',
    className
  );
  
  return (
    <section className={containerClasses} {...rest}>
      <SectionHeader
        title="TRUSTED BY LEADING COMPANIES"
        align="center"
        headingLevel="h2"
      />
      
      <div className="partner-logos__carousel-container">
        <Carousel
          autoPlay={true}
          interval={5000}
          itemsToShow={Math.min(itemsToShow, partnerLogos.length)}
          showIndicators={partnerLogos.length > itemsToShow}
          infiniteLoop={true}
        >
          {partnerLogos.map((logo) => (
            <div key={logo.id} className="partner-logos__item">
              <ImageWithFallback
                src={logo.src}
                alt={logo.alt}
                width={150}
                height={60}
                objectFit="contain"
              />
            </div>
          ))}
        </Carousel>
      </div>
    </section>
  );
};

export default PartnerLogos;