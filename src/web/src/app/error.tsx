'use client';

import React, { useEffect } from 'react';
import { useRouter } from 'next/navigation'; // version ^13.4.0

import Alert from '../../components/ui/Alert';
import Button from '../../components/ui/Button';
import MainLayout from '../../components/layout/MainLayout';
import { Variant } from '../../types/common';
import { logError, getErrorMessage } from '../../utils/errorHandling';

/**
 * Next.js Error component that handles page-level errors in the IndiVillage website.
 * Provides a user-friendly error page when errors occur within a specific page,
 * allowing users to retry the operation or navigate to other parts of the site
 * while maintaining the overall application structure.
 * 
 * Implements the "Fail Gracefully" pattern to maintain system stability and
 * provide clear user feedback when errors occur.
 */
const Error: React.FC<{ error: Error; reset: () => void }> = ({ error, reset }) => {
  const router = useRouter();

  // Log the error when component mounts for monitoring and debugging
  useEffect(() => {
    logError(error, 'PageError');
  }, [error]);

  // Get user-friendly error message from the error object
  const errorMessage = getErrorMessage(error);

  return (
    <MainLayout
      meta={{
        title: 'Error Occurred',
        description: 'An error occurred while loading this page. Please try again or return to the homepage.'
      }}
    >
      <div className="error-page container mx-auto px-4 py-16">
        <div className="max-w-2xl mx-auto text-center">
          <h1 className="text-3xl font-bold mb-6" aria-live="assertive" role="alert">
            Something went wrong
          </h1>
          
          <Alert 
            variant={Variant.ERROR} 
            message={errorMessage}
            className="mb-8"
          />
          
          <p className="text-lg mb-8">
            We apologize for the inconvenience. You can try again or return to the homepage.
          </p>
          
          <div className="flex flex-col sm:flex-row justify-center gap-4">
            <Button 
              onClick={reset} 
              variant="primary"
              aria-label="Try loading the page again"
            >
              Try again
            </Button>
            
            <Button 
              onClick={() => router.push('/')} 
              variant="secondary"
              aria-label="Navigate to the homepage"
            >
              Return to homepage
            </Button>
          </div>
        </div>
      </div>
    </MainLayout>
  );
};

export default Error;