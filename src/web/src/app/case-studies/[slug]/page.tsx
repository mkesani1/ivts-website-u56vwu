import React from 'react'; // react@18.2.0
import { Metadata } from 'next'; // next@13.4.0
import { notFound } from 'next/navigation'; // next@13.4.0
import CaseStudyDetail from '../../../components/case-studies/CaseStudyDetail';
import { getCaseStudyBySlug, getContentSlugs } from '../../../services/contentService';
import { ContentType } from '../../../types/content';
import { CaseStudy } from '../../../types/content';
import { ROUTES } from '../../../constants/routes';

/**
 * Generates metadata for the case study page for SEO purposes
 * @param {object} { params } - Object containing route parameters
 * @returns {Promise<Metadata>} Metadata object for the page
 */
export async function generateMetadata({ params }: { params: { slug: string } }): Promise<Metadata> {
  // Extract slug from params
  const { slug } = params;

  // Fetch case study data using getCaseStudyBySlug
  const caseStudy = await getCaseStudyBySlug(slug);

  // If case study not found, return default metadata
  if (!caseStudy) {
    return {
      title: 'Case Study Not Found | IndiVillage',
    };
  }

  // Return metadata object with title, description, and OpenGraph properties
  return {
    title: `${caseStudy.title} | IndiVillage Case Study`, // Set title to '{caseStudy.title} | IndiVillage Case Study'
    description: caseStudy.challenge, // Set description based on case study challenge
    openGraph: {
      images: [caseStudy.image?.url || ''], // Set OpenGraph image to case study image URL if available
    },
  };
}

/**
 * Generates static paths for all case studies at build time
 * @returns {Promise<{ slug: string }[]>} Array of slug objects for static path generation
 */
export async function generateStaticParams(): Promise<{ slug: string }[]> {
  // Fetch all case study slugs using getContentSlugs with ContentType.CASE_STUDY
  const slugs = await getContentSlugs(ContentType.CASE_STUDY);

  // Map the slugs to the required format { slug: string }
  return slugs.map((slug) => ({ slug }));

}

/**
 * Main page component for displaying a specific case study
 * @param {object} { params } - Object containing route parameters
 * @returns {Promise<JSX.Element>} Rendered case study page
 */
async function CaseStudyPage({ params }: { params: { slug: string } }) {
  // Extract slug from params
  const { slug } = params;

  // Fetch case study data using getCaseStudyBySlug
  const caseStudy = await getCaseStudyBySlug(slug);

  // If case study not found, call notFound() to show 404 page
  if (!caseStudy) {
    notFound();
  }

  // Return the CaseStudyDetail component with the case study data
  return (
    <CaseStudyDetail caseStudy={caseStudy as CaseStudy} />
  );
}

export default CaseStudyPage;