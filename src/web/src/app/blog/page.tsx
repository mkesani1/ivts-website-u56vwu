import React from 'react'; // version 18.2.0
import Link from 'next/link'; // version 13.4.0
import Image from 'next/image'; // version 13.4.0
import { Metadata } from 'next'; // version 13.4.0

import PageHeader from '../../components/shared/PageHeader';
import Card from '../../components/ui/Card';
import Badge from '../../components/ui/Badge';
import Button from '../../components/ui/Button';
import ImageWithFallback from '../../components/shared/ImageWithFallback';

import { ContentType, BlogPost, BlogCategory } from '../../types/content';
import { getBlogPosts } from '../../services/contentService';
import { ROUTES } from '../../constants/routes';
import { formatDate } from '../../utils/dates';

/**
 * Generate metadata for the blog listing page using Next.js App Router metadata API
 */
export const generateMetadata = async (): Promise<Metadata> => {
  return {
    title: 'Blog | IndiVillage | AI-as-a-Service with Social Impact',
    description: 'Explore industry insights, technology trends, and social impact stories from IndiVillage\'s experts in AI, data services, and sustainable business practices.',
    keywords: ['IndiVillage blog', 'AI blog', 'data services', 'social impact', 'technology trends', 'AI for good'],
    openGraph: {
      title: 'Blog | IndiVillage | AI-as-a-Service with Social Impact',
      description: 'Explore industry insights, technology trends, and social impact stories from IndiVillage\'s experts.',
      url: 'https://indivillage.com/blog',
      siteName: 'IndiVillage',
      images: [
        {
          url: 'https://indivillage.com/images/og-blog.jpg',
          width: 1200,
          height: 630,
          alt: 'IndiVillage Blog'
        }
      ],
      locale: 'en_US',
      type: 'website',
    },
    alternates: {
      canonical: 'https://indivillage.com/blog',
    }
  };
};

/**
 * Main component for the blog listing page that displays a grid of blog posts
 * with filtering by category and pagination
 */
export default async function BlogPage({ 
  searchParams 
}: { 
  searchParams: { category?: string, page?: string } 
}): Promise<JSX.Element> {
  // Extract category and page from search params
  const { category, page } = searchParams;
  const currentPage = page ? parseInt(page, 10) : 1;
  const postsPerPage = 9; // 9 posts per page (3x3 grid)

  // Create filters based on category
  const filters: Record<string, any> = {};
  if (category) {
    filters['fields.categories.sys.contentType.sys.id'] = ContentType.BLOG_POST;
    filters['fields.categories.fields.slug'] = category;
  }

  // Fetch blog posts with pagination
  const blogPosts = await getBlogPosts({
    ...filters,
    limit: postsPerPage,
    skip: (currentPage - 1) * postsPerPage,
    order: '-fields.date'
  });

  // Get all categories for the filter
  const allCategories = await getBlogPosts({ limit: 100 });
  
  // Extract unique categories from all posts
  const uniqueCategories: BlogCategory[] = [];
  const categoryIds = new Set();
  
  allCategories.forEach(post => {
    if (post.categories) {
      post.categories.forEach(cat => {
        if (cat && cat.id && !categoryIds.has(cat.id)) {
          categoryIds.add(cat.id);
          uniqueCategories.push(cat);
        }
      });
    }
  });
  
  // Sort categories alphabetically
  uniqueCategories.sort((a, b) => a.name.localeCompare(b.name));

  // Calculate total pages
  const totalPosts = blogPosts.length > 0 ? blogPosts[0].total || blogPosts.length : 0;
  const totalPages = Math.ceil(totalPosts / postsPerPage);

  // Define breadcrumbs
  const breadcrumbs = [
    { label: 'Home', href: '/' },
    { label: 'Blog', href: ROUTES.BLOG.INDEX, current: true }
  ];

  return (
    <main className="blog-page">
      <PageHeader
        title="Blog"
        subtitle="Industry insights, technology trends, and social impact stories from IndiVillage"
        breadcrumbs={breadcrumbs}
      />

      <div className="container mx-auto px-4 py-8">
        {/* Category filter */}
        {uniqueCategories.length > 0 && (
          <CategoryFilter 
            categories={uniqueCategories} 
            selectedCategory={category} 
          />
        )}

        {/* Blog posts grid */}
        {blogPosts.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mt-8">
            {blogPosts.map((post) => (
              <BlogPostCard key={post.id} post={post} />
            ))}
          </div>
        ) : (
          <EmptyState />
        )}

        {/* Pagination */}
        {totalPages > 1 && (
          <Pagination 
            currentPage={currentPage} 
            totalPages={totalPages} 
            category={category} 
          />
        )}
      </div>
    </main>
  );
}

/**
 * Component to display a blog post card in the grid
 */
function BlogPostCard({ post }: { post: BlogPost }): JSX.Element {
  const formattedDate = formatDate(post.date, 'MMM d, yyyy');
  
  return (
    <Link 
      href={`${ROUTES.BLOG.INDEX}/${post.slug}`} 
      className="blog-post-card-link"
      aria-label={`Read blog post: ${post.title}`}
    >
      <Card 
        className="blog-post-card h-full flex flex-col transition-all duration-300" 
        hoverable
      >
        <div className="blog-post-card-image-container relative aspect-video w-full overflow-hidden rounded-t-md">
          <ImageWithFallback
            src={post.featuredImage?.url || '/images/placeholder-blog.jpg'}
            alt={post.title}
            width={600}
            height={340}
            className="object-cover w-full h-full"
          />
        </div>
        
        <div className="blog-post-card-content flex flex-col flex-grow p-6">
          <div className="blog-post-card-date text-sm text-gray-500 mb-2">
            {formattedDate}
          </div>
          
          <h2 className="blog-post-card-title text-xl font-semibold mb-3 line-clamp-2">
            {post.title}
          </h2>
          
          <p className="blog-post-card-excerpt text-gray-700 mb-4 flex-grow line-clamp-3">
            {post.excerpt}
          </p>
          
          {post.categories && post.categories.length > 0 && (
            <div className="blog-post-card-categories flex flex-wrap gap-2 mt-auto">
              {post.categories.map((category) => (
                <Badge 
                  key={category.id} 
                  variant="secondary" 
                  size="small" 
                  rounded
                >
                  {category.name}
                </Badge>
              ))}
            </div>
          )}
        </div>
      </Card>
    </Link>
  );
}

/**
 * Component to display and handle category filtering
 */
function CategoryFilter({ 
  categories, 
  selectedCategory 
}: { 
  categories: BlogCategory[], 
  selectedCategory?: string 
}): JSX.Element {
  return (
    <section className="category-filter mb-6">
      <div className="flex flex-wrap items-center gap-3">
        <span className="text-gray-700 font-medium">Filter by category:</span>
        
        <Link href={ROUTES.BLOG.INDEX} className="inline-block">
          <Button 
            variant={!selectedCategory ? "primary" : "secondary"} 
            size="small"
            aria-current={!selectedCategory ? 'page' : undefined}
          >
            All
          </Button>
        </Link>
        
        {categories.map((category) => (
          <Link 
            key={category.id} 
            href={`${ROUTES.BLOG.INDEX}?category=${category.slug}`}
            className="inline-block"
          >
            <Button 
              variant={selectedCategory === category.slug ? "primary" : "secondary"} 
              size="small"
              aria-current={selectedCategory === category.slug ? 'page' : undefined}
            >
              {category.name}
            </Button>
          </Link>
        ))}
      </div>
    </section>
  );
}

/**
 * Component to display pagination controls
 */
function Pagination({ 
  currentPage, 
  totalPages, 
  category 
}: { 
  currentPage: number, 
  totalPages: number, 
  category?: string 
}): JSX.Element {
  // Create base URL with category param if specified
  const baseUrl = category 
    ? `${ROUTES.BLOG.INDEX}?category=${category}&page=` 
    : `${ROUTES.BLOG.INDEX}?page=`;

  // Function to render page numbers with ellipsis for gaps
  const renderPageNumbers = () => {
    const pageNumbers = [];
    
    // Always show page 1
    pageNumbers.push(
      <Link key={1} href={`${baseUrl}1`} className="inline-block">
        <Button 
          variant={currentPage === 1 ? "primary" : "secondary"} 
          size="small" 
          aria-current={currentPage === 1 ? 'page' : undefined}
          aria-label={`Page 1`}
        >
          1
        </Button>
      </Link>
    );
    
    // Add ellipsis if needed
    if (currentPage > 3) {
      pageNumbers.push(
        <span key="start-ellipsis" className="px-2" aria-hidden="true">
          ...
        </span>
      );
    }
    
    // Show current page and adjacent pages
    for (let i = Math.max(2, currentPage - 1); i <= Math.min(totalPages - 1, currentPage + 1); i++) {
      if (i > 1 && i < totalPages) {
        pageNumbers.push(
          <Link key={i} href={`${baseUrl}${i}`} className="inline-block">
            <Button 
              variant={currentPage === i ? "primary" : "secondary"} 
              size="small"
              aria-current={currentPage === i ? 'page' : undefined}
              aria-label={`Page ${i}`}
            >
              {i}
            </Button>
          </Link>
        );
      }
    }
    
    // Add ellipsis if needed
    if (currentPage < totalPages - 2) {
      pageNumbers.push(
        <span key="end-ellipsis" className="px-2" aria-hidden="true">
          ...
        </span>
      );
    }
    
    // Always show last page if there's more than one page
    if (totalPages > 1) {
      pageNumbers.push(
        <Link key={totalPages} href={`${baseUrl}${totalPages}`} className="inline-block">
          <Button 
            variant={currentPage === totalPages ? "primary" : "secondary"} 
            size="small"
            aria-current={currentPage === totalPages ? 'page' : undefined}
            aria-label={`Page ${totalPages}`}
          >
            {totalPages}
          </Button>
        </Link>
      );
    }
    
    return pageNumbers;
  };

  return (
    <nav className="pagination flex justify-center mt-12" aria-label="Blog pagination">
      <div className="flex flex-wrap items-center gap-2">
        {/* Previous page button */}
        {currentPage > 1 && (
          <Link href={`${baseUrl}${currentPage - 1}`} className="inline-block">
            <Button 
              variant="secondary" 
              size="small"
              icon="arrowLeft" 
              iconPosition="left"
              aria-label="Previous page"
            >
              Previous
            </Button>
          </Link>
        )}
        
        {/* Page numbers */}
        {renderPageNumbers()}
        
        {/* Next page button */}
        {currentPage < totalPages && (
          <Link href={`${baseUrl}${currentPage + 1}`} className="inline-block">
            <Button 
              variant="secondary" 
              size="small" 
              icon="arrowRight" 
              iconPosition="right"
              aria-label="Next page"
            >
              Next
            </Button>
          </Link>
        )}
      </div>
    </nav>
  );
}

/**
 * Component to display when no blog posts are found
 */
function EmptyState(): JSX.Element {
  return (
    <section className="empty-state text-center py-16">
      <div className="max-w-md mx-auto">
        <h2 className="text-2xl font-bold mb-4">No blog posts found</h2>
        <p className="text-gray-600 mb-8">
          There are no blog posts matching your current filters. Try adjusting your filters or check back later for new content.
        </p>
        <Link href={ROUTES.BLOG.INDEX}>
          <Button variant="primary">View All Posts</Button>
        </Link>
      </div>
    </section>
  );
}