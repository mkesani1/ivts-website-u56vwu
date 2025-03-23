import React, { useEffect, useState } from 'react'; // version 18.2.0
import classNames from 'classnames'; // version 2.3.2
import { motion } from 'framer-motion'; // version 10.12.0
import { Link } from 'next/link'; // version 13.4.0
import Image from 'next/image'; // version 13.4.0

import { PageHeader, PageHeaderProps } from '../shared/PageHeader';
import Button from '../ui/Button';
import ServiceFeature from './ServiceFeature';
import HowItWorks from './HowItWorks';
import RelatedCaseStudies from './RelatedCaseStudies';
import FileUploadForm from '../forms/FileUploadForm';
import { Service, CaseStudy, Asset } from '../../types/content';
import { useAnalytics } from '../../hooks/useAnalytics';
import { ROUTES } from '../../constants/routes';

/**
 * Interface defining the props for the ServiceDetail component
 */
export interface ServiceDetailProps {
  /**
   * The service data to display
   */
  service: Service;
  /**
   * Array of case studies related to the service
   */
  relatedCaseStudies: CaseStudy[];
  /**
   * Additional CSS classes to apply to the component
   */
  className?: string;
}

/**
 * Component that displays detailed information about a specific AI service
 */
const ServiceDetail: React.FC<ServiceDetailProps> = ({
  service,
  relatedCaseStudies,
  className,
}) => {
  // Destructure props to get service data, related case studies, and className
  const { title, description, heroImage, features, howItWorks, slug } = service;

  // Get analytics tracking functions from useAnalytics hook
  const { trackServiceView, trackEvent } = useAnalytics();

  // Create state for showing/hiding the upload form modal
  const [showUploadForm, setShowUploadForm] = useState(false);

  // Create function to handle demo request button click
  const handleDemoRequestClick = () => {
    trackEvent('service_detail', 'demo_request_click', {
      service_id: service.id,
      service_name: service.title,
    });
  };

  // Create function to handle upload sample button click
  const handleUploadSampleClick = () => {
    setShowUploadForm(true);
    trackEvent('service_detail', 'upload_sample_click', {
      service_id: service.id,
      service_name: service.title,
    });
  };

  // Create function to handle upload form success
  const handleUploadFormSuccess = () => {
    setShowUploadForm(false);
  };

  // Use useEffect to track service view when component mounts
  useEffect(() => {
    trackServiceView(service.id, service.title);
  }, [trackServiceView, service.id, service.title]);

  // Parse howItWorks JSON string to get step data
  const steps = parseHowItWorksSteps(howItWorks);

  // Create breadcrumb items for navigation
  const breadcrumbItems: PageHeaderProps['breadcrumbs'] = [
    { label: 'Home', href: ROUTES.HOME },
    { label: 'Services', href: ROUTES.SERVICES.INDEX },
    { label: title, href: ROUTES.SERVICES.DETAIL.replace('[slug]', slug), current: true },
  ];

  // Return the component JSX structure
  return (
    <div className={classNames('service-detail', className)}>
      {/* Render PageHeader with service title, description, and breadcrumbs */}
      <PageHeader
        title={title}
        subtitle={description}
        breadcrumbs={breadcrumbItems}
      />

      {/* Render hero image if available */}
      {heroImage && (
        <div className="service-detail__hero-image">
          <Image
            src={heroImage.url}
            alt={heroImage.title || title}
            width={1200}
            height={600}
            style={{ objectFit: 'cover', width: '100%', height: 'auto' }}
          />
        </div>
      )}

      {/* Render service description */}
      <div className="service-detail__description">
        <p>{description}</p>
      </div>

      {/* Render grid of ServiceFeature components for each feature */}
      {features && features.length > 0 && (
        <div className="service-detail__features">
          <h2>Key Features</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature) => (
              <ServiceFeature key={feature.id} feature={feature} />
            ))}
          </div>
        </div>
      )}

      {/* Render HowItWorks component with step data */}
      {steps && steps.length > 0 && (
        <HowItWorks steps={steps} />
      )}

      {/* Render RelatedCaseStudies component with case studies related to the service */}
      {relatedCaseStudies && relatedCaseStudies.length > 0 && (
        <RelatedCaseStudies caseStudies={relatedCaseStudies} service={service} />
      )}

      {/* Render call-to-action section with demo request and upload sample buttons */}
      <div className="service-detail__cta">
        <h2>Ready to Transform Your Business?</h2>
        <div className="flex flex-col md:flex-row space-y-4 md:space-y-0 md:space-x-4">
          <Button variant="primary" onClick={handleDemoRequestClick}>
            <Link href={ROUTES.REQUEST_DEMO}>Request Demo</Link>
          </Button>
          <Button variant="secondary" onClick={handleUploadSampleClick}>
            Upload Sample Data
          </Button>
        </div>
      </div>

      {/* Render upload form modal when showUploadForm is true */}
      {showUploadForm && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed top-0 left-0 w-full h-full bg-black bg-opacity-50 z-50 flex items-center justify-center"
        >
          <motion.div
            initial={{ y: 50 }}
            animate={{ y: 0 }}
            exit={{ y: 50 }}
            className="bg-white rounded-lg p-8 max-w-2xl w-full"
            onClick={(e) => e.stopPropagation()}
          >
            <h2 className="text-2xl font-semibold mb-4">Upload Sample Data</h2>
            <FileUploadForm onSuccess={handleUploadFormSuccess} />
            <Button variant="tertiary" onClick={() => setShowUploadForm(false)}>
              Cancel
            </Button>
          </motion.div>
        </motion.div>
      )}
    </div>
  );
};

/**
 * Helper function to parse the howItWorks JSON string into step data
 */
const parseHowItWorksSteps = (howItWorksJson: string): { title: string; description: string; icon?: string }[] => {
  try {
    // Try to parse the JSON string
    const steps = JSON.parse(howItWorksJson);
    // If parsing succeeds, return the parsed steps array
    return steps;
  } catch (error) {
    // If parsing fails, return a default array of generic steps
    console.error('Failed to parse howItWorks JSON:', error);
    return [
      { title: 'Step 1', description: 'Description for step 1' },
      { title: 'Step 2', description: 'Description for step 2' },
      { title: 'Step 3', description: 'Description for step 3' },
      { title: 'Step 4', description: 'Description for step 4' },
    ];
  }
};

export default ServiceDetail;