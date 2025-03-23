# src/web/src/app/page.tsx
```typescript
import React from 'react'; // version 18.2.0
import { Metadata } from 'next'; // version ^13.4.0

import Hero from '../components/home/Hero';
import ServiceOverview from '../components/home/ServiceOverview';
import ImpactOverview from '../components/home/ImpactOverview';
import CaseStudyHighlight from '../components/home/CaseStudyHighlight';
import PartnerLogos from '../components/home/PartnerLogos';
import CTASection from '../components/home/CTASection';
import { getServices, getCaseStudies } from '../services/contentService';

/**
 * Generates static metadata for the homepage
 * @returns Metadata object for the homepage
 */
export const generateMetadata = (): Metadata => {
  return {
    title: 'IndiVillage: AI-Powered Solutions with Social Impact',
    description: 'Transform your business with AI solutions that create positive social change. Explore our AI-as-a-Service offerings and social impact initiatives.',
    keywords: ['AI', 'Artificial Intelligence', 'Social Impact', 'Data Collection', 'Data Preparation', 'AI Model Development', 'Human-in-the-Loop', 'Ethical AI', 'AI for Good']
  };
};

/**
 * Main homepage component that renders all homepage sections
 * @returns Rendered homepage component
 */
const HomePage: React.FC = () => {
  return (
    <>
      {/* Render the Hero component at the top of the page */}
      <Hero />

      {/* Render the ServiceOverview component to showcase AI services */}
      <ServiceOverview className="py-12 md:py-16 lg:py-20" />

      {/* Render the ImpactOverview component to highlight social impact */}
      <ImpactOverview className="py-12 md:py-16 lg:py-20 bg-gray-50" />

      {/* Render the CaseStudyHighlight component to feature case studies */}
      <CaseStudyHighlight className="py-12 md:py-16 lg:py-20" />

      {/* Render the PartnerLogos component to display partner companies */}
      <PartnerLogos className="py-12 md:py-16 lg:py-20 bg-gray-50" />

      {/* Render the CTASection component with call-to-action buttons */}
      <CTASection />
    </>
  );
};

export default HomePage;