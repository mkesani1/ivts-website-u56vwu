# src/web/src/app/services/[slug]/page.tsx
```tsx
import { Metadata } from 'next'; // version ^13.4.0
import { notFound } from 'next/navigation'; // version ^13.4.0
import { ServiceDetail } from '../../../components/services/ServiceDetail';
import { getServiceBySlug, getCaseStudies } from '../../../services/contentService';
import { ContentType } from '../../../types/content';
import { generateMetadata } from '../../../utils/seo';
import { getCanonicalUrl } from '../../../utils/seo';

/**
 * Generates metadata for the service detail page
 * @param {object} { params } - Object containing route parameters
 * @returns {Promise<Metadata>} Promise resolving to page metadata
 */
export async function generateMetadata({ params }: { params: { slug: string } }): Promise<Metadata> {
  // Extract slug from params
  const { slug } = params;

  // Fetch service data using getServiceBySlug
  const service = await getServiceBySlug(slug);

  // If service not found, return default metadata
  if (!service) {
    return generateMetadata({
      title: 'Service Not Found',
      description: 'Service not found',
      keywords: [],
    });
  }

  // Create custom metadata object with service title, description
  const customMetadata = {
    title: service.title,
    description: service.description,
    keywords: [service.category, ...service.features.map(feature => feature.title)],
  };

  // Set canonical URL using getCanonicalUrl
  const canonicalUrl = getCanonicalUrl(`/services/${slug}`);

  // Generate and return metadata using generateMetadata utility
  return generateMetadata({
    ...customMetadata,
    canonicalUrl,
  });
}

/**
 * Generates static paths for all services at build time
 * @returns {Promise<{ slug: string }[]>} Promise resolving to array of slug params
 */
export async function generateStaticParams(): Promise<{ slug: string }[]> {
  // Fetch all content slugs for SERVICE content type
  const slugs = await getServiceBySlug()

  // Map slugs to params object format { slug: string }
  return slugs.map((slug: string) => ({ slug }));
}

/**
 * Main page component for service detail view
 * @param {object} { params } - Object containing route parameters
 * @returns {Promise<JSX.Element>} Promise resolving to rendered page component
 */
const ServicePage = async ({ params }: { params: { slug: string } }): Promise<JSX.Element> => {
  // Extract slug from params
  const { slug } = params;

  // Fetch service data using getServiceBySlug
  const service = await getServiceBySlug(slug);

  // If service not found, call notFound() to render 404 page
  if (!service) {
    notFound();
  }

  // Fetch related case studies using getCaseStudies with service ID filter
  const relatedCaseStudies = await getCaseStudies({
    'services.sys.id': service.id,
  });

  // Return ServiceDetail component with service and related case studies data
  return (
    <ServiceDetail
      service={service}
      relatedCaseStudies={relatedCaseStudies}
    />
  );
};

export default ServicePage;