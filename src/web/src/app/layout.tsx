import React from 'react'; // version ^18.2.0
import { Metadata } from 'next'; // version ^13.4.0
import { Inter } from 'next/font/google'; // version ^13.4.0

import MainLayout from '../components/layout/MainLayout';
import { ToastProvider } from '../context/ToastContext';
import { AnalyticsProvider } from '../context/AnalyticsContext';
import { UploadProvider } from '../context/UploadContext';
import '../styles/globals.css';

/**
 * Google font configuration for the Inter font
 */
const inter = Inter({ subsets: ['latin'], display: 'swap', variable: '--font-inter' });

/**
 * Default metadata for the application
 */
const metadata: Metadata = {
  title: 'IndiVillage | AI-as-a-Service with Social Impact',
  description:
    'IndiVillage provides AI-as-a-service solutions including data collection, data preparation, AI model development, and human-in-the-loop services with a social impact mission.',
  keywords: [
    'AI-as-a-service',
    'data collection',
    'data preparation',
    'AI model development',
    'human-in-the-loop',
    'social impact',
    'IndiVillage',
  ],
  viewport: 'width=device-width, initial-scale=1',
  icons: {
    icon: '/favicon.ico',
    apple: '/apple-touch-icon.png',
  },
};

/**
 * Props for the RootLayout component
 */
interface RootLayoutProps {
  children: React.ReactNode;
}

/**
 * Root layout component that wraps all pages with HTML structure, global styles, and context providers
 * @param props - Props for the RootLayout component
 * @returns Rendered layout component with children
 */
export default function RootLayout({ children }: RootLayoutProps): JSX.Element {
  return (
    <html lang="en">
      <body className={inter.variable}>
        {/* Global metadata in head section */}
        <AnalyticsProvider>
          <UploadProvider>
            <ToastProvider>
              <MainLayout meta={metadata}>
                <main id="main-content" className="main-content" role="main">
                  {children}
                </main>
              </MainLayout>
            </ToastProvider>
          </UploadProvider>
        </AnalyticsProvider>
      </body>
    </html>
  );
}

export { metadata };