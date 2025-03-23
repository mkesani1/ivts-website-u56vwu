import React from 'react';
import classNames from 'classnames'; // version 2.3.2

import Header from './Header';
import Footer from './Footer';
import MetaTags from '../shared/MetaTags';
import ErrorBoundary from '../shared/ErrorBoundary';
import useScrollToTop from '../../hooks/useScrollToTop';
import { ToastProvider } from '../../context/ToastContext';

/**
 * Props for the MainLayout component
 */
interface MainLayoutProps {
  /** The content to be rendered within the layout */
  children: React.ReactNode;
  /** Additional CSS class names for the layout container */
  className?: string;
  /** Metadata for SEO */
  meta?: {
    title?: string;
    description?: string;
    keywords?: string[];
    ogImage?: string;
    canonicalUrl?: string;
  };
  /** Whether to hide the footer */
  hideFooter?: boolean;
}

/**
 * Main layout component that provides a consistent structure for all pages of the IndiVillage website,
 * including header, footer, and common UI elements. It handles page transitions, error boundaries,
 * and provides context providers for the entire application.
 * 
 * This component implements the "Modern Website Design" requirement by providing a consistent
 * layout structure with intuitive navigation and proper accessibility landmarks.
 */
const MainLayout: React.FC<MainLayoutProps> = ({
  children,
  className,
  meta,
  hideFooter = false,
}) => {
  // Scroll to top on page navigation
  useScrollToTop();

  return (
    <div className={classNames('layout', className)}>
      {/* SEO metadata */}
      {meta && <MetaTags {...meta} />}

      {/* Error boundary to catch and handle errors */}
      <ErrorBoundary>
        {/* Toast notifications provider */}
        <ToastProvider>
          {/* Header with navigation */}
          <Header />

          {/* Main content area with proper ARIA landmark */}
          <main id="main-content" className="main-content" role="main">
            {children}
          </main>

          {/* Footer (conditionally rendered) */}
          {!hideFooter && <Footer />}
        </ToastProvider>
      </ErrorBoundary>
    </div>
  );
};

export default MainLayout;