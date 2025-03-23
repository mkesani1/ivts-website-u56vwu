import React, { useEffect } from 'react'; // version ^18.2.0
import { useRouter, useSearchParams } from 'next/navigation'; // version ^13.4.0
import { Metadata } from 'next'; // version ^13.4.0

import MainLayout from '../../../components/layout/MainLayout';
import PageHeader from '../../../components/shared/PageHeader';
import ProgressBar from '../../../components/forms/ProgressBar';
import Icon from '../../../components/ui/Icon';
import Card from '../../../components/ui/Card';
import Button from '../../../components/ui/Button';
import useUploadStatus from '../../../hooks/useUploadStatus';
import useAnalytics from '../../../hooks/useAnalytics';
import { ROUTES } from '../../../constants/routes';
import { UploadStatus } from '../../../types/api';

/**
 * Generates metadata for the upload processing page
 * @returns Metadata object for the page
 */
export const generateMetadata = (): Metadata => {
  // Return metadata object with title, description, and robots noindex directive
  return {
    title: 'Processing Data Upload',
    description: 'View the processing status of your data upload.',
    robots: {
      index: false,
      follow: false,
    },
  };
};

/**
 * Page component that displays the file upload processing status and progress
 * @returns Rendered upload processing page
 */
const UploadProcessingPage: React.FC = () => {
  // Initialize router using useRouter hook for navigation
  const router = useRouter();

  // Get search parameters using useSearchParams hook
  const searchParams = useSearchParams();

  // Extract uploadId from search parameters
  const uploadId = searchParams.get('uploadId');

  // Initialize analytics using useAnalytics hook
  const analytics = useAnalytics();

  // Use useEffect to track page view analytics
  useEffect(() => {
    analytics.trackPageView(ROUTES.UPLOAD_SAMPLE.PROCESSING);
  }, [analytics]);

  // Use useEffect to redirect to success page when processing is complete
  useEffect(() => {
    if (uploadId && uploadState.status === UploadStatus.COMPLETED) {
      router.push(`${ROUTES.UPLOAD_SAMPLE.SUCCESS}?uploadId=${uploadId}`);
    }
  }, [uploadState.status, uploadId, router]);

  // Use useEffect to redirect to upload page if uploadId is missing
  useEffect(() => {
    if (!uploadId) {
      router.push(ROUTES.UPLOAD_SAMPLE.INDEX);
    }
  }, [uploadId, router]);

  // Set up initial upload state with status PROCESSING and 0% progress
  const initialState = {
    file: null,
    status: UploadStatus.PROCESSING,
    progress: { loaded: 0, total: 100, percentage: 0 },
    uploadId: uploadId || null,
    error: null,
    errorMessage: null,
    processingStep: 'Initializing...',
    estimatedTimeRemaining: 120,
    analysisResult: null
  };

  // Use useUploadStatus hook to track the upload status with the uploadId
  const { uploadState, isPolling } = useUploadStatus(uploadId, initialState);

  // Create breadcrumb items for navigation context
  const breadcrumbItems = [
    { label: 'Home', href: ROUTES.HOME },
    { label: 'Upload Sample Data', href: ROUTES.UPLOAD_SAMPLE.INDEX },
    { label: 'Processing', href: ROUTES.UPLOAD_SAMPLE.PROCESSING, current: true },
  ];

  // Return MainLayout component with appropriate metadata
  return (
    <MainLayout
      meta={{
        title: 'Processing Data Upload',
        description: 'View the processing status of your data upload.',
      }}
    >
      {/* Render PageHeader with title and breadcrumbs */}
      <PageHeader title="Processing Data Upload" breadcrumbs={breadcrumbItems} />

      <div className="container mx-auto mt-8 px-4">
        {uploadState.status === UploadStatus.FAILED ? (
          // Handle error state with appropriate message and retry button if needed
          <Card variant="error" className="text-center p-6">
            <Icon name="error" size="large" className="mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">Upload Failed</h3>
            <p className="mb-4">{uploadState.errorMessage || 'An unexpected error occurred.'}</p>
            <Button onClick={() => router.push(ROUTES.UPLOAD_SAMPLE.INDEX)}>Retry Upload</Button>
          </Card>
        ) : (
          <>
            {/* Render processing status section with icon and message */}
            <Card className="text-center p-6">
              <Icon name="upload" size="large" className="mx-auto mb-4 animate-pulse" />
              <h3 className="text-lg font-semibold mb-2">Processing Your Dataset</h3>
              <p className="mb-4">
                Your file &quot;{uploadState.file?.name}&quot; is being processed.
              </p>

              {/* Render ProgressBar component with current progress and processing step */}
              <ProgressBar
                progress={uploadState.progress}
                processingStep={uploadState.processingStep || 'Analyzing data structure'}
                estimatedTimeRemaining={uploadState.estimatedTimeRemaining}
              />
            </Card>

            {/* Render 'What Happens Next' section explaining the process */}
            <Card className="mt-6 p-6">
              <h3 className="text-lg font-semibold mb-4">What Happens Next?</h3>
              <ol className="list-decimal pl-5">
                <li className="mb-2">We&apos;ll analyze your sample dataset.</li>
                <li className="mb-2">Our AI specialists will review the results.</li>
                <li className="mb-2">You&apos;ll receive a detailed report within 24 hours.</li>
                <li>We&apos;ll schedule a consultation to discuss solutions.</li>
              </ol>
            </Card>

            {/* Render notification message about email confirmation */}
            <Card className="mt-6 p-6 bg-gray-50 border border-gray-200">
              <p className="text-sm text-gray-600">
                <Icon name="info" size="small" className="inline-block mr-1 align-text-bottom" />
                You&apos;ll receive an email confirmation when processing is complete with a link to view your results.
              </p>
            </Card>

            {/* Render service exploration section while user waits */}
            <Card className="mt-6 p-6">
              <h3 className="text-lg font-semibold mb-4">While You Wait, Explore Our Services</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Button variant="secondary" onClick={() => router.push(ROUTES.SERVICES.DATA_COLLECTION)}>
                  Data Collection
                </Button>
                <Button variant="secondary" onClick={() => router.push(ROUTES.SERVICES.DATA_PREPARATION)}>
                  Data Preparation
                </Button>
                <Button variant="secondary" onClick={() => router.push(ROUTES.SERVICES.AI_MODEL_DEVELOPMENT)}>
                  AI Model Development
                </Button>
                <Button variant="secondary" onClick={() => router.push(ROUTES.SERVICES.HUMAN_IN_THE_LOOP)}>
                  Human-in-the-Loop
                </Button>
              </div>
            </Card>
          </>
        )}
      </div>
    </MainLayout>
  );
};

export default UploadProcessingPage;