import React, { useEffect } from 'react'; // version ^18.2.0
import { useRouter, useSearchParams } from 'next/navigation'; // version ^13.4.0
import { Metadata } from 'next'; // version ^13.4.0

import MainLayout from '../../../components/layout/MainLayout';
import PageHeader from '../../../components/shared/PageHeader';
import Button from '../../../components/ui/Button';
import Card from '../../../components/ui/Card';
import Icon from '../../../components/ui/Icon';
import { ROUTES } from '../../../constants/routes';
import useAnalytics from '../../../hooks/useAnalytics';
import { getDefaultMetaData, createPageTitle } from '../../../utils/seo';

/**
 * Generates metadata for the upload success page
 * @returns Next.js Metadata object for the page
 */
export const generateMetadata = (): Metadata => {
  // Get default metadata using getDefaultMetaData
  const defaultMetadata = getDefaultMetaData();

  // Create page-specific metadata with title and description
  const metadata: Metadata = {
    title: createPageTitle('Upload Successful'),
    description: 'Your sample dataset has been successfully uploaded and is being processed. We will contact you soon with a customized solution proposal.',
    robots: {
      index: false, // Add robots noindex directive to prevent indexing of this utility page
      follow: false,
    },
  };

  // Return the metadata object for Next.js
  return metadata;
};

/**
 * Page component that displays a success confirmation after file upload and processing
 * @returns Rendered upload success page
 */
const UploadSuccessPage: React.FC = () => {
  // Initialize router using useRouter hook for navigation
  const router = useRouter();

  // Get search parameters using useSearchParams hook
  const searchParams = useSearchParams();

  // Extract fileId from search parameters
  const fileId = searchParams?.get('fileId');

  // Initialize analytics using useAnalytics hook
  const analytics = useAnalytics();

  // Use useEffect to track page view analytics
  useEffect(() => {
    analytics.trackPageView(ROUTES.UPLOAD_SAMPLE.SUCCESS);
  }, [analytics]);

  // Create breadcrumb items for navigation context
  const breadcrumbItems = [
    { label: 'Home', href: ROUTES.HOME },
    { label: 'Upload Sample Data', href: ROUTES.UPLOAD_SAMPLE.INDEX },
    { label: 'Success', href: ROUTES.UPLOAD_SAMPLE.SUCCESS, current: true },
  ];

  // Handle case where fileId is missing with appropriate message and button to try again
  if (!fileId) {
    return (
      <MainLayout meta={generateMetadata()}>
        <PageHeader title="Upload Error" breadcrumbs={breadcrumbItems} />
        <div className="container mx-auto py-8">
          <Card className="p-6">
            <p className="text-red-500">
              There was an error processing your file. Please try again.
            </p>
            <Button onClick={() => router.push(ROUTES.UPLOAD_SAMPLE.INDEX)}>
              Try Again
            </Button>
          </Card>
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout meta={generateMetadata()}>
      {/* Render PageHeader with title and breadcrumbs */}
      <PageHeader title="Upload Successful" breadcrumbs={breadcrumbItems} />

      <div className="container mx-auto py-8">
        {/* Render success confirmation section with checkmark icon and message */}
        <Card className="p-6 mb-8 text-center">
          <div className="flex items-center justify-center mb-4">
            <Icon name="check" size={48} color="green" />
          </div>
          <h2 className="text-2xl font-semibold mb-2">
            Your data has been successfully uploaded!
          </h2>
          <p className="text-gray-700">
            We are now processing your dataset.
          </p>
        </Card>

        {/* Render next steps section explaining what happens next */}
        <Card className="p-6 mb-8">
          <h3 className="text-xl font-semibold mb-4">What Happens Next?</h3>
          <ol className="list-decimal list-inside text-gray-700">
            <li>We'll analyze your sample dataset.</li>
            <li>Our AI specialists will review the results.</li>
            <li>You'll receive a detailed report within 24 hours.</li>
            <li>We'll schedule a consultation to discuss solutions.</li>
          </ol>
        </Card>

        {/* Render email notification message about detailed report */}
        <Card className="p-6 mb-8 bg-gray-50">
          <p className="text-gray-700">
            <Icon name="info" size={16} className="inline-block mr-1" />
            You'll receive an email confirmation when processing is complete with a link to view your results.
          </p>
        </Card>

        {/* Render CTA section with buttons for demo request and exploring services */}
        <Card className="p-6 text-center">
          <h3 className="text-xl font-semibold mb-4">
            Ready to take the next step?
          </h3>
          <div className="flex justify-center space-x-4">
            <Button variant="primary" onClick={() => router.push(ROUTES.REQUEST_DEMO)}>
              Request a Demo
            </Button>
            <Button variant="secondary" onClick={() => router.push(ROUTES.SERVICES.INDEX)}>
              Explore Our Services
            </Button>
          </div>
        </Card>
      </div>
    </MainLayout>
  );
};

export default UploadSuccessPage;