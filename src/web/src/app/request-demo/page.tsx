import React, { useCallback } from 'react'; // version ^18.2.0
import { useRouter } from 'next/navigation'; // version ^13.4.0

import MainLayout from '../../components/layout/MainLayout';
import PageHeader from '../../components/shared/PageHeader';
import DemoRequestForm from '../../components/forms/DemoRequestForm';
import { ROUTES } from '../../constants/routes';

/**
 * Next.js metadata function that generates SEO metadata for the page
 * @returns Metadata object with title, description, and other SEO properties
 */
export const generateMetadata = () => {
  // Return a metadata object with title, description, and other SEO properties
  // Set the title to 'Request a Demo | IndiVillage'
  // Set the description to explain the demo request process and benefits
  // Include appropriate keywords related to AI services and demos
  return {
    title: 'Request a Demo | IndiVillage',
    description:
      'Request a demo of IndiVillage\'s AI services and see how we can transform your business with AI-powered solutions and social impact.',
    keywords: ['AI services', 'demo request', 'artificial intelligence', 'machine learning'],
  };
};

/**
 * Page component that renders the demo request page
 * @returns The rendered demo request page
 */
const RequestDemoPage: React.FC = () => {
  // Initialize router using useRouter hook for navigation after form submission
  const router = useRouter();

  // Create handleFormSuccess function to handle successful form submission
  const handleFormSuccess = useCallback(() => {
    // Redirect to the home page after successful form submission
    router.push(ROUTES.HOME);
  }, [router]);

  // Define breadcrumb items for the page header
  const breadcrumbs = [
    { label: 'Home', href: ROUTES.HOME },
    { label: 'Request Demo', href: ROUTES.REQUEST_DEMO, current: true },
  ];

  // Return the page structure wrapped in MainLayout
  // Include PageHeader with title 'Request a Demo' and breadcrumbs
  // Add introductory text explaining the demo request process
  // Render the DemoRequestForm component with onSuccess handler
  // Apply appropriate container styling and spacing
  // Ensure the page is responsive across all device sizes
  return (
    <MainLayout meta={generateMetadata()}>
      <div className="container mx-auto py-8">
        <PageHeader title="Request a Demo" breadcrumbs={breadcrumbs} />
        <div className="mt-6">
          <p className="mb-4">
            See how IndiVillage's AI solutions can transform your business while creating positive social impact.
          </p>
          <DemoRequestForm onSuccess={handleFormSuccess} />
        </div>
      </div>
    </MainLayout>
  );
};

export default RequestDemoPage;