'use client';

import React, { useEffect } from 'react';

import Alert from '../components/ui/Alert';
import Button from '../components/ui/Button';
import { Variant, ToastType } from '../types/common';
import { logError, getErrorMessage } from '../utils/errorHandling';

/**
 * Next.js Global Error component that handles application-level errors
 * Implements the "Fail Gracefully" pattern to maintain system stability and provide clear user feedback
 */
export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  // Log the error when component mounts
  useEffect(() => {
    logError(error, 'GlobalError');
  }, [error]);

  // Get user-friendly error message
  const errorMessage = getErrorMessage(error);

  // Update document title to indicate error
  useEffect(() => {
    document.title = 'Error - IndiVillage';
  }, []);

  return (
    <html lang="en">
      <body>
        <div className="error-container min-h-screen flex flex-col items-center justify-center p-4">
          <div className="error-content max-w-lg w-full">
            <h1 className="text-2xl font-bold mb-4" role="alert">
              Something went wrong
            </h1>
            
            <Alert
              variant={ToastType.ERROR}
              message={errorMessage}
              className="mb-6"
            />
            
            <p className="mb-6">
              We apologize for the inconvenience. A critical error has occurred in the application.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4">
              <Button
                variant={Variant.PRIMARY}
                onClick={() => reset()}
              >
                Try again
              </Button>
              
              <Button
                variant={Variant.SECONDARY}
                onClick={() => window.location.href = '/'}
              >
                Go to homepage
              </Button>
            </div>
            
            {process.env.NODE_ENV === 'development' && (
              <div className="mt-8 p-4 bg-gray-100 rounded overflow-auto">
                <h2 className="text-lg font-semibold mb-2">Error details:</h2>
                <pre className="text-sm overflow-x-auto">
                  {error.stack || error.message}
                </pre>
              </div>
            )}
          </div>
        </div>
      </body>
    </html>
  );
}