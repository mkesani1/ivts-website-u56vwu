import React from 'react'; // react v18.2.0
import { Metadata } from 'next'; // next 13.4+
import { PageHeader, PageHeaderProps } from '../../components/shared/PageHeader';
import ImpactMetrics from '../../components/impact/ImpactMetrics';
import ImpactGallery from '../../components/impact/ImpactGallery';
import MissionStatement from '../../components/impact/MissionStatement';
import SDGSection from '../../components/impact/SDGSection';
import ResponsiveVideo from '../../components/shared/ResponsiveVideo';
import { getImpactStories } from '../../services/contentService';
import { ImpactStory } from '../../types/content';
import { ROUTES } from '../../constants/routes';
import { generateMetadata } from '../../utils/seo';

/**
 * Generates metadata for the Social Impact page
 * @returns Next.js Metadata object with SEO information
 */
export const generateMetadata = (): Metadata => {
  // Call the generateMetadata utility with custom metadata for the Impact page
  return generateMetadata({
    title: 'Social Impact | IndiVillage', // Set page title
    description: "Discover IndiVillage's AI for Good mission and how we're creating positive social impact in rural communities.", // Set page description
    keywords: ['social impact', 'AI for good', 'rural communities', 'sustainable development', 'ethical AI'] // Set keywords
  });
};

/**
 * Server component that renders the Social Impact page
 * @returns Rendered Social Impact page
 */
const ImpactPage: React.FC = async (): Promise<JSX.Element> => {
  // Define breadcrumb items for navigation context
  const breadcrumbs: PageHeaderProps['breadcrumbs'] = [
    { label: 'Home', href: ROUTES.HOME },
    { label: 'Impact', href: ROUTES.IMPACT.INDEX, current: true },
  ];

  // Fetch impact stories using getImpactStories function
  const impactStories: ImpactStory[] = await getImpactStories();

  return (
    <main className="page-content">
      {/* Render PageHeader with title and breadcrumbs */}
      <PageHeader
        title="AI FOR GOOD: OUR SOCIAL IMPACT"
        subtitle="Creating sustainable livelihoods through technology"
        breadcrumbs={breadcrumbs}
      />

      {/* Render a hero section with ResponsiveVideo showing IndiVillage's impact */}
      <section className="impact-hero">
        <ResponsiveVideo
          src="/videos/impact-video.mp4"
          title="IndiVillage Social Impact Video"
          poster="/images/impact/impact-video-poster.jpg"
          controls={true}
        />
      </section>

      {/* Render ImpactMetrics component to display key impact statistics */}
      <ImpactMetrics />

      {/* Render MissionStatement component to explain IndiVillage's mission */}
      <MissionStatement />

      {/* Render ImpactGallery component with fetched impact stories */}
      <ImpactGallery stories={impactStories} />

      {/* Render SDGSection component to show Sustainable Development Goals alignment */}
      <SDGSection />

      {/* Apply appropriate CSS classes for responsive layout and styling */}
      <style jsx>{`
        .page-content {
          padding: 20px;
        }

        .impact-hero {
          margin-bottom: 20px;
        }
      `}</style>
    </main>
  );
};

export default ImpactPage;