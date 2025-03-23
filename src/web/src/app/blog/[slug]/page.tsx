import React from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { notFound } from 'next/navigation';
import { Metadata } from 'next';

import PageHeader from '../../../components/shared/PageHeader';
import ImageWithFallback from '../../../components/shared/ImageWithFallback';
import Badge from '../../../components/ui/Badge';
import Avatar from '../../../components/ui/Avatar';

import { ContentType, BlogPost } from '../../../types/content';
import { getBlogPostBySlug, getContentSlugs, getBlogPosts } from '../../../services/contentService';
import { ROUTES } from '../../../constants/routes';
import { formatDateForDisplay } from '../../../utils/dates';
import { getCanonicalUrl, truncateDescription } from '../../../utils/seo';

/**
 * Generate static paths for all blog posts at build time
 */
export async function generateStaticParams() {
  try {
    const slugs = await getContentSlugs(ContentType.BLOG_POST);
    return slugs.map((slug) => ({
      slug,
    }));
  } catch (error) {
    console.error("Error generating static params for blog posts:", error);
    return [];
  }
}

/**
 * Generate metadata for the blog post page using Next.js App Router metadata API
 */
export async function generateMetadata({
  params,
}: {
  params: { slug: string };
}): Promise<Metadata> {
  const { slug } = params;
  
  const post = await getBlogPostBySlug(slug);
  
  if (!post) {
    return {
      title: 'Blog Post Not Found | IndiVillage',
      description: 'The requested blog post could not be found.',
    };
  }
  
  const description = post.excerpt || truncateDescription(post.content, 160);
  const keywords = post.tags || [];
  const canonicalUrl = getCanonicalUrl(`${ROUTES.BLOG.INDEX}/${slug}`);
  
  return {
    title: `${post.title} | IndiVillage Blog`,
    description,
    keywords,
    openGraph: {
      title: post.title,
      description: truncateDescription(description, 200),
      images: [
        {
          url: post.featuredImage?.url || '/images/og-image.jpg',
          width: post.featuredImage?.width || 1200,
          height: post.featuredImage?.height || 630,
          alt: post.title,
        },
      ],
      type: 'article',
      publishedTime: post.date,
      modifiedTime: post.updatedAt,
      authors: post.author ? [`${post.author.name}`] : undefined,
      tags: post.tags,
    },
    twitter: {
      card: 'summary_large_image',
      title: post.title,
      description: truncateDescription(description, 200),
      images: [post.featuredImage?.url || '/images/og-image.jpg'],
    },
    alternates: {
      canonical: canonicalUrl,
    },
  };
}

/**
 * Main component for the blog post page that displays a single blog post with its content
 */
export default async function BlogPostPage({
  params,
}: {
  params: { slug: string };
}) {
  const { slug } = params;
  
  const post = await getBlogPostBySlug(slug);
  
  if (!post) {
    notFound();
  }
  
  const formattedDate = formatDateForDisplay(post.date);
  
  const breadcrumbs = [
    { label: 'Home', href: '/' },
    { label: 'Blog', href: ROUTES.BLOG.INDEX },
    { label: post.title, href: `${ROUTES.BLOG.INDEX}/${slug}`, current: true },
  ];
  
  return (
    <main className="blog-post-page">
      <PageHeader
        title={post.title}
        breadcrumbs={breadcrumbs}
        className="blog-post-header"
      />
      
      <div className="container mx-auto px-4 py-8">
        <article className="blog-post max-w-4xl mx-auto">
          {post.featuredImage && (
            <div className="blog-post-featured-image mb-8">
              <ImageWithFallback
                src={post.featuredImage.url}
                alt={post.featuredImage.description || post.title}
                width={1200}
                height={630}
                priority
                className="w-full rounded-lg shadow-md"
              />
            </div>
          )}
          
          <div className="blog-post-meta flex items-center gap-6 mb-8 text-gray-600">
            <div className="blog-post-date flex items-center">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              <time dateTime={post.date}>{formattedDate}</time>
            </div>
            
            {post.author && (
              <div className="blog-post-author flex items-center">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
                <span>{post.author.name}</span>
              </div>
            )}
          </div>
          
          {post.categories && post.categories.length > 0 && (
            <div className="blog-post-categories flex flex-wrap gap-2 mb-8">
              {post.categories.map((category) => (
                <Badge key={category.id} variant="secondary">
                  {category.name}
                </Badge>
              ))}
            </div>
          )}
          
          <div 
            className="blog-post-content prose prose-lg max-w-none mb-12"
            dangerouslySetInnerHTML={{ __html: post.content }}
          />
          
          {post.author && (
            <AuthorSection author={post.author} />
          )}
        </article>
        
        {post.categories && post.categories.length > 0 && (
          <RelatedPosts categories={post.categories} currentPostId={post.id} />
        )}
        
        <CTASection />
      </div>
    </main>
  );
}

/**
 * Component to display author information for the blog post
 */
function AuthorSection({ author }: { author: BlogPost['author'] }) {
  return (
    <section className="author-section bg-gray-50 rounded-lg p-6 mb-12" aria-labelledby="author-heading">
      <div className="author-section-inner flex flex-col md:flex-row gap-6 items-center md:items-start">
        <div className="author-avatar">
          {author.photo ? (
            <Avatar
              src={author.photo.url}
              alt={author.name}
              size="large"
              className="border-2 border-primary-100"
            />
          ) : (
            <Avatar size="large" className="border-2 border-primary-100" />
          )}
        </div>
        <div className="author-info text-center md:text-left">
          <h2 id="author-heading" className="author-name text-xl font-semibold mb-1">{author.name}</h2>
          {author.title && <p className="author-title text-gray-600 mb-3">{author.title}</p>}
          {author.bio && <p className="author-bio text-gray-700">{author.bio}</p>}
          
          {author.socialLinks && Object.keys(author.socialLinks).length > 0 && (
            <div className="author-social-links flex gap-4 mt-4 justify-center md:justify-start">
              {author.socialLinks.linkedin && (
                <a href={author.socialLinks.linkedin} target="_blank" rel="noopener noreferrer" aria-label={`${author.name}'s LinkedIn profile`} className="text-gray-600 hover:text-primary-600">
                  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M19 3a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h14m-.5 15.5v-5.3a3.26 3.26 0 0 0-3.26-3.26c-.85 0-1.84.52-2.32 1.3v-1.11h-2.79v8.37h2.79v-4.93c0-.77.62-1.4 1.39-1.4a1.4 1.4 0 0 1 1.4 1.4v4.93h2.79M6.88 8.56a1.68 1.68 0 0 0 1.68-1.68c0-.93-.75-1.69-1.68-1.69a1.69 1.69 0 0 0-1.69 1.69c0 .93.76 1.68 1.69 1.68m1.39 9.94v-8.37H5.5v8.37h2.77z" />
                  </svg>
                </a>
              )}
              {author.socialLinks.twitter && (
                <a href={author.socialLinks.twitter} target="_blank" rel="noopener noreferrer" aria-label={`${author.name}'s Twitter profile`} className="text-gray-600 hover:text-primary-600">
                  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M22.46 6c-.77.35-1.6.58-2.46.69.88-.53 1.56-1.37 1.88-2.38-.83.5-1.75.85-2.72 1.05C18.37 4.5 17.26 4 16 4c-2.35 0-4.27 1.92-4.27 4.29 0 .34.04.67.11.98C8.28 9.09 5.11 7.38 3 4.79c-.37.63-.58 1.37-.58 2.15 0 1.49.75 2.81 1.91 3.56-.71 0-1.37-.2-1.95-.5v.03c0 2.08 1.48 3.82 3.44 4.21a4.22 4.22 0 0 1-1.93.07 4.28 4.28 0 0 0 4 2.98 8.521 8.521 0 0 1-5.33 1.84c-.34 0-.68-.02-1.02-.06C3.44 20.29 5.7 21 8.12 21 16 21 20.33 14.46 20.33 8.79c0-.19 0-.37-.01-.56.84-.6 1.56-1.36 2.14-2.23z" />
                  </svg>
                </a>
              )}
            </div>
          )}
        </div>
      </div>
    </section>
  );
}

/**
 * Component to display related blog posts
 */
async function RelatedPosts({
  categories,
  currentPostId,
}: {
  categories: BlogPost['categories'],
  currentPostId: string
}) {
  if (!categories || categories.length === 0) {
    return null;
  }

  try {
    // Extract category IDs for filtering
    const categoryIds = categories.map(category => category.id);
    
    // Fetch related posts
    const allRelatedPosts = await getBlogPosts({
      limit: 10, // Fetch more than we need to ensure we have enough after filtering
    });
    
    // Filter out the current post and only keep posts that share at least one category
    const filteredPosts = allRelatedPosts.filter(post => {
      if (post.id === currentPostId) return false;
      
      // Check if the post shares at least one category with the current post
      return post.categories?.some(category => 
        categoryIds.includes(category.id)
      );
    });
    
    // If no related posts found, return null
    if (!filteredPosts.length) {
      return null;
    }
    
    // Limit to 3 related posts maximum
    const postsToDisplay = filteredPosts.slice(0, 3);
    
    return (
      <section className="related-posts-section max-w-6xl mx-auto mb-16" aria-labelledby="related-posts-heading">
        <h2 id="related-posts-heading" className="section-heading text-2xl font-bold mb-8 text-center">Related Articles</h2>
        <div className="related-posts-grid grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {postsToDisplay.map((post) => (
            <Link 
              key={post.id} 
              href={`${ROUTES.BLOG.INDEX}/${post.slug}`}
              className="related-post-card block bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow duration-300"
            >
              <div className="related-post-image">
                {post.featuredImage ? (
                  <ImageWithFallback
                    src={post.featuredImage.url}
                    alt={post.featuredImage.description || post.title}
                    width={400}
                    height={225}
                    className="w-full h-48 object-cover rounded-t-lg"
                  />
                ) : (
                  <div className="w-full h-48 bg-gray-200 rounded-t-lg flex items-center justify-center">
                    <span className="text-gray-500">IndiVillage</span>
                  </div>
                )}
              </div>
              <div className="p-5">
                <h3 className="related-post-title text-lg font-semibold mb-2 hover:text-primary-600 transition-colors duration-300">{post.title}</h3>
                {post.excerpt && (
                  <p className="related-post-excerpt text-gray-600 text-sm">
                    {truncateDescription(post.excerpt, 120)}
                  </p>
                )}
              </div>
            </Link>
          ))}
        </div>
      </section>
    );
  } catch (error) {
    console.error("Error fetching related posts:", error);
    return null;
  }
}

/**
 * Component to display call-to-action section at the end of the blog post
 */
function CTASection() {
  return (
    <section className="cta-section bg-primary-50 rounded-lg p-8 text-center max-w-4xl mx-auto">
      <div className="cta-section-inner">
        <h2 className="cta-heading text-2xl font-bold mb-4">Ready to transform your business with AI?</h2>
        <p className="cta-subheading text-gray-700 mb-8 max-w-2xl mx-auto">
          Learn how IndiVillage's AI solutions can drive results while creating positive social impact.
        </p>
        <div className="cta-buttons flex flex-wrap gap-4 justify-center">
          <Link href={ROUTES.REQUEST_DEMO} className="btn btn-primary px-6 py-3 bg-primary-600 text-white rounded-md font-medium hover:bg-primary-700 transition-colors">
            Request a Demo
          </Link>
          <Link href={ROUTES.SERVICES.INDEX} className="btn btn-secondary px-6 py-3 border-2 border-primary-600 text-primary-600 rounded-md font-medium hover:bg-primary-50 transition-colors">
            Explore Our Services
          </Link>
        </div>
      </div>
    </section>
  );
}