import React, { useCallback, useEffect } from 'react'; // version 18.2.0
import { Metadata } from 'next'; // version ^13.4.0

import PageHeader from '../../components/shared/PageHeader';
import ContactForm from '../../components/forms/ContactForm';
import { ROUTES } from '../../constants/routes';
import { useAnalytics } from '../../hooks/useAnalytics';

/**
 * Static metadata for the contact page for SEO
 */
export const metadata: Metadata = {
  title: 'Contact Us | IndiVillage',
  description:
    'Get in touch with IndiVillage for AI-as-a-service solutions including data collection, data preparation, AI model development, and human-in-the-loop services.',
};

/**
 * Breadcrumb navigation items for the contact page
 */
const breadcrumbItems = [
  { label: 'Home', href: ROUTES.HOME },
  { label: 'Contact', href: ROUTES.CONTACT, active: true },
];

/**
 * Contact page component that renders the contact form and company information
 * @returns Rendered contact page component
 */
const ContactPage: React.FC = () => {
  // Initialize analytics hook for tracking page views
  const analytics = useAnalytics();

  // Define breadcrumb items for navigation context
  const breadcrumbs = breadcrumbItems;

  // Define function to handle successful form submission
  const handleFormSuccess = useCallback(() => {
    // Track successful form submission
    analytics.trackEvent('contact_form', 'submission_success');
  }, [analytics]);

  // Track page view on component mount
  useEffect(() => {
    analytics.trackPageView(ROUTES.CONTACT);
  }, [analytics]);

  return (
    <div className="container mx-auto py-12">
      {/* Render the page header with title and breadcrumbs */}
      <PageHeader title="Contact Us" breadcrumbs={breadcrumbs} />

      {/* Render the main content section with two columns on larger screens */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mt-8">
        {/* Render company information and contact details in the first column */}
        <div className="contact-info">
          <h2 className="text-2xl font-semibold mb-4">Get in Touch</h2>
          <p className="text-gray-700 mb-4">
            We're always happy to hear from you. Whether you have a question about our services,
            want to request a demo, or just want to say hello, feel free to reach out.
          </p>
          <div className="mb-4">
            <h3 className="text-lg font-semibold">Address</h3>
            <p className="text-gray-700">
              123 Main Street<br />
              Anytown, CA 12345<br />
              United States
            </p>
          </div>
          <div className="mb-4">
            <h3 className="text-lg font-semibold">Phone</h3>
            <p className="text-gray-700">
              (123) 456-7890
            </p>
          </div>
          <div>
            <h3 className="text-lg font-semibold">Email</h3>
            <p className="text-gray-700">
              <a href="mailto:info@indivillage.com" className="text-primary-500 hover:underline">
                info@indivillage.com
              </a>
            </p>
          </div>
        </div>

        {/* Render the contact form in the second column */}
        <div className="contact-form-container">
          <h2 className="text-2xl font-semibold mb-4">Send us a Message</h2>
          <ContactForm onSuccess={handleFormSuccess} className="mt-4" />
        </div>
      </div>
    </div>
  );
};

export default ContactPage;