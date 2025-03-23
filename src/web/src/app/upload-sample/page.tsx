import React from 'react'; // version ^18.2.0
import { useRouter } from 'next/navigation'; // version ^13.4.0
import { Metadata } from 'next'; // version ^13.4.0

import MainLayout from '../../components/layout/MainLayout';
import PageHeader from '../../components/shared/PageHeader';
import FileUploadForm from '../../components/forms/FileUploadForm';
import { ROUTES } from '../../constants/routes';
import { getDefaultMetaData, createPageTitle } from '../../utils/seo';

/**
 * Generates metadata for the upload sample page
 * @returns {Metadata} Next.js Metadata object for the page
 */
export const generateMetadata = (): Metadata => {
  // Get default metadata using getDefaultMetaData
  const defaultMetadata = getDefaultMetaData();

  // Create page-specific metadata with title and description
  const uploadSampleTitle = createPageTitle('Upload Sample Data');
  const uploadSampleDescription =
    'Upload a sample dataset to receive a customized AI solution proposal from IndiVillage. Experience our AI-as-a-service capabilities firsthand.';

  // Return the metadata object for Next.js
  return {
    title: uploadSampleTitle,
    description: uploadSampleDescription,
  };
};

/**
 * Page component for the upload sample page
 * @returns {JSX.Element} Rendered upload sample page
 */
const UploadSamplePage: React.FC = () => {
  // Initialize router for navigation
  const router = useRouter();

  // Create breadcrumb items for navigation context
  const breadcrumbItems = [
    { label: 'Home', href: ROUTES.HOME },
    { label: 'Upload Sample Data', href: ROUTES.UPLOAD_SAMPLE.INDEX, current: true },
  ];

  /**
   * Defines handleUploadSuccess function to redirect to processing page
   * @param {string} uploadId - The ID of the successful upload
   */
  const handleUploadSuccess = (uploadId: string) => {
    // Redirect to the processing page with the upload ID
    router.push(`${ROUTES.UPLOAD_SAMPLE.PROCESSING}?uploadId=${uploadId}`);
  };

  // Render MainLayout component with page metadata
  return (
    <MainLayout meta={generateMetadata()}>
      {/* Render PageHeader with title, subtitle, and breadcrumbs */}
      <PageHeader
        title="Upload Sample Data"
        subtitle="Let us analyze your data and provide a customized solution proposal for your specific needs."
        breadcrumbs={breadcrumbItems}
      />

      {/* Render main content section with description text */}
      <section className="py-8">
        <div className="container mx-auto px-4">
          {/* Render FileUploadForm component with success handler */}
          <FileUploadForm onSuccess={handleUploadSuccess} />
        </div>
      </section>
    </MainLayout>
  );
};

export default UploadSamplePage;