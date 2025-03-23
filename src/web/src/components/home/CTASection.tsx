import React from 'react';
import Link from 'next/link'; // version 13.4.0
import classNames from 'classnames'; // version 2.3.2

import Button from '../ui/Button';
import { ROUTES } from '../../constants/routes';
import useAnalytics from '../../hooks/useAnalytics';
import useBreakpoint from '../../hooks/useBreakpoint';
import { Breakpoint } from '../../types/common';

/**
 * Props interface for the CTASection component
 */
interface CTASectionProps extends React.HTMLAttributes<HTMLElement> {
  className?: string;
}

/**
 * A call-to-action section component that displays a heading and action buttons
 * for driving user engagement and conversions on the IndiVillage homepage.
 * The section includes buttons for requesting a demo, uploading sample data,
 * and contacting the company.
 * 
 * @param props - Component props including className and any HTML attributes
 * @returns Rendered CTA section component
 */
const CTASection: React.FC<CTASectionProps> = ({ className, ...props }) => {
  // Use the breakpoint hook to determine the current device size
  const breakpoint = useBreakpoint();
  
  // Use analytics hook to track user interactions
  const { trackEvent } = useAnalytics();
  
  /**
   * Tracks button clicks for analytics purposes
   * @param action - The action being performed (request_demo, upload_sample, contact_us)
   */
  const handleButtonClick = (action: string) => {
    trackEvent('cta_section', action, {
      location: 'homepage_cta_section',
      element: 'button'
    });
  };
  
  // Determine if we're on a mobile device for responsive styling
  const isMobile = breakpoint === Breakpoint.MOBILE_SMALL || breakpoint === Breakpoint.MOBILE;
  
  return (
    <section 
      className={classNames('cta-section py-12 md:py-16 lg:py-20 bg-gray-50', className)}
      {...props}
    >
      <div className="container mx-auto px-4 text-center">
        <h2 className="text-2xl md:text-3xl lg:text-4xl font-bold mb-8 text-gray-900">
          READY TO TRANSFORM YOUR BUSINESS?
        </h2>
        
        <div className="flex flex-col md:flex-row justify-center items-center gap-4 md:gap-6">
          <Link href={ROUTES.REQUEST_DEMO} aria-label="Request a demo">
            <Button 
              variant="primary" 
              size={isMobile ? 'medium' : 'large'}
              onClick={() => handleButtonClick('request_demo')}
              className="w-full md:w-auto"
            >
              Request Demo
            </Button>
          </Link>
          
          <Link href={ROUTES.UPLOAD_SAMPLE.INDEX} aria-label="Upload sample data">
            <Button 
              variant="secondary" 
              size={isMobile ? 'medium' : 'large'}
              onClick={() => handleButtonClick('upload_sample')}
              className="w-full md:w-auto"
            >
              Upload Sample Data
            </Button>
          </Link>
          
          <Link href={ROUTES.CONTACT} aria-label="Contact us">
            <Button 
              variant="tertiary" 
              size={isMobile ? 'medium' : 'large'}
              onClick={() => handleButtonClick('contact_us')}
              className="w-full md:w-auto"
            >
              Contact Us
            </Button>
          </Link>
        </div>
      </div>
    </section>
  );
};

export default CTASection;