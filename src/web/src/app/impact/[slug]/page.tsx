import React from 'react'; // version ^18.2.0
import { Metadata } from 'next'; // version ^13.4.0
import { notFound } from 'next/navigation'; // version ^13.4.0

import MainLayout from '../../../components/layout/MainLayout';
import ImpactStory from '../../../components/impact/ImpactStory';
import PageHeader from '../../../components/shared/PageHeader';
import { getImpactStoryBySlug, getContentSlugs } from '../../../services/contentService';
import { ContentType, ImpactStory as ImpactStoryType } from '../../../types/content';
import { getCanonicalUrl, truncateDescription } from '../../../utils/seo';

/**
 * Generates metadata for the impact story page based on the story data
 * @param { params } { slug: string } - The slug of the impact story
 * @returns { Promise<Metadata> } A promise resolving to the page metadata
 */
export async function generateMetadata({ params }: { params: { slug: string } }): Promise<Metadata> {
  // Extract slug from params
  const { slug } = params;

  // Fetch impact story data using getImpactStoryBySlug
  const story = await getImpactStoryBySlug(slug);

  // If story not found, return default metadata
  if (!story) {
    return {
      title: 'Impact Story Not Found',
    };
  }

  // Create metadata object with story title, excerpt, and media
  const title = story.title;
  const description = story.excerpt || story.story;
  const ogImage = story.media && story.media.length > 0 ? story.media[0].url : null;

  // Generate canonical URL for the impact story page
  const canonicalUrl = getCanonicalUrl(`/impact/${slug}`);

  // Truncate description for meta tags
  const truncatedDescription = truncateDescription(description, 160);

  // Return formatted metadata object
  return {
    title: title,
    description: truncatedDescription,
    openGraph: {
      title: title,
      description: truncatedDescription,
      images: ogImage ? [{ url: ogImage }] : [],
      url: canonicalUrl,
      type: 'article',
    },
    alternates: {
      canonical: canonicalUrl,
    },
  };
}

/**
 * Generates static paths for all impact stories during build time
 * @returns { Promise<{ slug: string }[]> } A promise resolving to an array of slug params
 */
export async function generateStaticParams(): Promise<{ slug: string }[]> {
  // Fetch all impact story slugs using getContentSlugs
  const slugs = await getContentSlugs(ContentType.IMPACT_STORY);

  // Map slugs to the required format { slug: string }
  return slugs.map((slug) => ({ slug }));
}

/**
 * Page component that displays a detailed view of an impact story
 * @param { params } { slug: string } - The slug of the impact story
 * @returns { Promise<JSX.Element> } A promise resolving to the rendered page component
 */
const ImpactStoryPage = async ({ params }: { params: { slug: string } }): Promise<JSX.Element> => {
  // Extract slug from params
  const { slug } = params;

  // Fetch impact story data using getImpactStoryBySlug
  const story: ImpactStoryType | null = await getImpactStoryBySlug(slug);

  // If story not found, call notFound() to show 404 page
  if (!story) {
    notFound();
  }

  // Create breadcrumb items for navigation
  const breadcrumbs = [
    { label: 'Home', href: '/' },
    { label: 'Impact', href: '/impact' },
    { label: story.title, href: `/impact/${slug}`, current: true },
  ];

  // Return MainLayout component with appropriate meta data
  return (
    <MainLayout
      meta={{
        title: story.title,
        description: story.excerpt || story.story,
        ogImage: story.media && story.media.length > 0 ? story.media[0].url : null,
        canonicalUrl: getCanonicalUrl(`/impact/${slug}`),
      }}
    >
      {/* Render PageHeader with story title and breadcrumbs */}
      <PageHeader title={story.title} breadcrumbs={breadcrumbs} />

      {/* Render ImpactStory component with the story data */}
      <div className="container mx-auto py-8">
        <ImpactStory story={story} />
      </div>
    </MainLayout>
  );
};

export default ImpactStoryPage;