import React from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

import Alert from '../components/ui/Alert';
import Button from '../components/ui/Button';
import MainLayout from '../components/layout/MainLayout';
import PageHeader from '../components/shared/PageHeader';
import { Variant } from '../types/common';

/**
 * Not Found page component that renders when a user navigates to a non-existent route.
 * Provides helpful error messaging and navigation options to guide users back to valid content.
 * Implements the "Fail Gracefully" pattern from the Error Handling Patterns specifications.
 */
export default function NotFound() {
  const router = useRouter();

  return (
    <MainLayout
      meta={{
        title: '404 - Page Not Found',
        description: 'The requested page could not be found. Please check the URL or navigate back to the home page.',
        keywords: ['404', 'not found', 'error', 'page not found']
      }}
    >
      <PageHeader
        title="404 - Page Not Found"
        subtitle="Sorry, we couldn't find the page you're looking for"
      />

      <div className="container mx-auto py-8 px-4">
        <Alert
          variant={Variant.WARNING}
          message={
            <div className="not-found-message">
              <p className="mb-4">
                The page you requested could not be found. This might be due to:
              </p>
              <ul className="list-disc ml-6 mb-4">
                <li>An outdated bookmark or link</li>
                <li>A mistyped URL</li>
                <li>The page may have been moved or deleted</li>
              </ul>
              <p>
                Please check the URL and try again, or use the options below to navigate to a valid page.
              </p>
            </div>
          }
          showIcon={true}
        />

        <div className="flex flex-wrap gap-4 mt-8">
          <Link href="/">
            <Button variant={Variant.PRIMARY}>
              Return to Homepage
            </Button>
          </Link>
          <Button
            variant={Variant.SECONDARY}
            onClick={() => router.back()}
          >
            Go Back
          </Button>
        </div>
      </div>
    </MainLayout>
  );
}