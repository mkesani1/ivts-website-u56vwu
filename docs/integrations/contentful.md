# Contentful CMS Integration

This document provides comprehensive documentation for the Contentful CMS integration in the IndiVillage website project. It covers setup, configuration, content models, and usage patterns for both frontend and backend implementations.

## Overview

The IndiVillage website uses Contentful as its headless CMS to manage and deliver content for services, case studies, impact stories, blog posts, team members, and static pages. The integration follows a content-as-a-service approach, with content being delivered via APIs to both the frontend and backend applications.

## Setup and Configuration

### Environment Variables

The following environment variables are required for Contentful integration:

**Backend (.env):**
```
CONTENTFUL_SPACE_ID=your_space_id
CONTENTFUL_ACCESS_TOKEN=your_delivery_api_token
CONTENTFUL_MANAGEMENT_TOKEN=your_management_api_token
CONTENTFUL_ENVIRONMENT=master
```

**Frontend (.env.local):**
```
NEXT_PUBLIC_CONTENTFUL_SPACE_ID=your_space_id
NEXT_PUBLIC_CONTENTFUL_ACCESS_TOKEN=your_delivery_api_token
NEXT_PUBLIC_CONTENTFUL_ENVIRONMENT=master
NEXT_PUBLIC_CONTENTFUL_PREVIEW=false
CONTENTFUL_PREVIEW_ACCESS_TOKEN=your_preview_api_token
```

### Dependencies

**Backend:**
```
contentful==2.6.0
contentful-management==2.11.0
```

**Frontend:**
```
contentful==10.3.0
```

### Authentication

The integration uses two types of authentication:

1. **Content Delivery API (CDA)** - Read-only access for retrieving published content
2. **Content Management API (CMA)** - Read-write access for managing content (backend only)

For preview functionality, the Content Preview API is used with a separate access token.

## Content Models

### Service

Represents an AI service offering:

- **Fields:**
  - `title` (Text): Name of the service
  - `slug` (Text): URL-friendly identifier
  - `description` (Rich Text): Detailed description
  - `category` (Symbol): Service category (DATA_COLLECTION, DATA_PREPARATION, AI_MODEL_DEVELOPMENT, HUMAN_IN_THE_LOOP)
  - `features` (References, many): List of service features
  - `icon` (Asset): Service icon
  - `heroImage` (Asset): Hero image for service detail page
  - `howItWorks` (Rich Text): Process description
  - `order` (Number): Display order

### ServiceFeature

Represents a feature of a service:

- **Fields:**
  - `title` (Text): Feature name
  - `description` (Text): Feature description
  - `icon` (Asset): Feature icon

### CaseStudy

Represents a client success story:

- **Fields:**
  - `title` (Text): Case study title
  - `slug` (Text): URL-friendly identifier
  - `client` (Text): Client name
  - `industry` (Reference): Industry category
  - `challenge` (Rich Text): Client challenge
  - `solution` (Rich Text): Implemented solution
  - `results` (References, many): Measurable outcomes
  - `image` (Asset): Featured image
  - `services` (References, many): Related services

### ImpactStory

Represents a social impact narrative:

- **Fields:**
  - `title` (Text): Story title
  - `slug` (Text): URL-friendly identifier
  - `story` (Rich Text): Full narrative
  - `excerpt` (Text): Brief summary
  - `beneficiaries` (Text): People impacted
  - `location` (Reference): Geographic location
  - `media` (Assets, many): Photos and videos
  - `metrics` (References, many): Impact metrics
  - `sdgs` (References, many): Related UN Sustainable Development Goals

### Other Content Types

Additional content types include:

- **BlogPost**: Blog articles
- **TeamMember**: Staff profiles
- **Page**: Static pages
- **Navigation**: Site navigation structure

## Backend Integration

### Architecture

The backend integration consists of two main components:

1. **Contentful Integration Module** (`app/integrations/contentful.py`): Low-level client for direct Contentful API interactions
2. **Content Service** (`app/services/content_service.py`): High-level service that provides business logic and caching

### Contentful Client

The `ContentfulClient` class provides methods for interacting with both the Delivery and Management APIs:

```python
from app.integrations.contentful import ContentfulClient

client = ContentfulClient()

# Delivery API (read-only)
delivery_client = client.get_delivery_client()
entry = client.get_entry('entry_id', include_level=2)
entries = client.get_entries({'content_type': 'service'})

# Management API (read-write)
management_client = client.get_management_client()
client.create_entry('service', fields={
    'title': {'en-US': 'New Service'},
    'slug': {'en-US': 'new-service'}
})
```

### Content Service

The `ContentService` class provides higher-level methods with caching:

```python
from app.services.content_service import ContentService

content_service = ContentService()

# Get all services
services = content_service.get_services()

# Get a specific service by slug
service = content_service.get_service_by_slug('data-preparation')

# Get case studies filtered by industry or service
case_studies = content_service.get_case_studies(
    industry_slug='healthcare',
    service_slug='data-preparation'
)

# Refresh content cache
content_service.refresh_content_cache('service', 'data-preparation')
```

### Caching Strategy

Content is cached using Redis with the following approach:

- **Cache Keys**: Prefixed with `content:` followed by content type and optional slug
- **TTL**: Default 3600 seconds (1 hour)
- **Invalidation**: Triggered by content updates via webhooks or manual refresh

The `@cached` decorator is used to automatically cache function results:

```python
from app.cache.decorators import cached

@cached(ttl=3600)
def get_service(slug):
    # Function implementation
```

## Frontend Integration

### Architecture

The frontend integration uses the Contentful JavaScript SDK to fetch content directly from Contentful's CDN. The integration is implemented in `src/lib/contentful.ts` and provides functions for fetching and transforming content.

### Content Types

Content types are defined as TypeScript interfaces in `src/types/content.ts`, ensuring type safety throughout the application.

### Fetching Content

Content can be fetched using the provided utility functions:

```typescript
import { getServices, getServiceBySlug, getCaseStudies } from '../lib/contentful';

// Get all services
const services = await getServices();

// Get a specific service by slug
const service = await getServiceBySlug('data-preparation');

// Get case studies with filtering
const caseStudies = await getCaseStudies({ industry: 'healthcare' });
```

### Static Generation

For optimal performance, content is fetched at build time using Next.js's static generation capabilities:

```typescript
// In a page component
export async function getStaticProps({ params }) {
  const slug = params.slug;
  const service = await getServiceBySlug(slug);
  
  return {
    props: {
      service,
    },
    revalidate: 60 * 60, // Revalidate every hour
  };
}

export async function getStaticPaths() {
  const slugs = await getAllContentSlugs('service');
  
  return {
    paths: slugs.map(slug => ({ params: { slug } })),
    fallback: 'blocking',
  };
}
```

### Preview Mode

The integration supports Contentful's preview mode for viewing unpublished content:

```typescript
// Preview is enabled via environment variable
const IS_PREVIEW_MODE = process.env.NEXT_PUBLIC_CONTENTFUL_PREVIEW === 'true';

// Create client with preview mode when needed
function getContentfulClient() {
  return createContentfulClient(IS_PREVIEW_MODE);
}
```

## Content Webhooks

### Setup

Contentful webhooks are configured to notify the application when content changes. This enables automatic cache invalidation and static regeneration.

### Cache Invalidation

When content is updated in Contentful, a webhook triggers the following process:

1. Webhook sends a POST request to `/api/revalidate`
2. The API route identifies the content type and slug from the payload
3. The cache for that specific content is invalidated
4. Next.js regenerates the affected static pages

### Implementation

```typescript
// src/app/api/revalidate/route.ts
export async function POST(request: Request) {
  const payload = await request.json();
  const contentType = payload.sys.contentType.sys.id;
  const slug = payload.fields.slug['en-US'];
  
  // Revalidate the path based on content type and slug
  await revalidatePath(`/${contentType}s/${slug}`);
  
  return Response.json({ revalidated: true, now: Date.now() });
}
```

## Rich Text Rendering

### Backend

Rich text fields are delivered as structured JSON objects that need to be rendered appropriately. The backend typically passes this structured content to the frontend for rendering.

### Frontend

The frontend uses the `@contentful/rich-text-react-renderer` package to render rich text content:

```typescript
import { documentToReactComponents } from '@contentful/rich-text-react-renderer';
import { BLOCKS, INLINES } from '@contentful/rich-text-types';

const options = {
  renderNode: {
    [BLOCKS.PARAGRAPH]: (node, children) => <p className="mb-4">{children}</p>,
    [BLOCKS.HEADING_2]: (node, children) => <h2 className="text-2xl font-bold mb-4">{children}</h2>,
    [INLINES.HYPERLINK]: (node, children) => (
      <a href={node.data.uri} className="text-blue-600 hover:underline">
        {children}
      </a>
    ),
    // Additional node renderers...
  },
};

function RichTextRenderer({ content }) {
  return <div>{documentToReactComponents(content, options)}</div>;
}
```

## Best Practices

### Content Modeling

- Keep content models modular and reusable
- Use references to create relationships between content types
- Define clear validation rules for each field
- Use appropriate field types (e.g., Rich Text for formatted content)

### Performance Optimization

- Use the `include` parameter to reduce API calls for linked entries
- Implement caching at multiple levels (Redis, CDN, browser)
- Use selective fetching with the `select` parameter when only specific fields are needed
- Implement proper cache invalidation strategies

### Error Handling

- Implement robust error handling for API calls
- Provide fallback content when API calls fail
- Log errors with appropriate context for debugging
- Use circuit breakers for external API calls

### Security

- Never expose management tokens in client-side code
- Use environment variables for all sensitive credentials
- Implement proper access controls in Contentful
- Validate and sanitize all content before rendering

## Troubleshooting

### Common Issues

- **Missing Content**: Check content publication status in Contentful
- **Stale Content**: Verify cache invalidation is working properly
- **Rate Limiting**: Implement proper request throttling
- **Missing Fields**: Ensure content model matches expected structure

### Debugging Tools

- Contentful Web App's "Preview" feature
- API request logging
- Contentful CLI for content management
- GraphQL Explorer for query testing

## References

- [Contentful Developer Documentation](https://www.contentful.com/developers/docs/)
- [Contentful JavaScript SDK](https://github.com/contentful/contentful.js)
- [Contentful Management SDK](https://github.com/contentful/contentful-management.js)
- [Rich Text Rendering](https://www.contentful.com/developers/docs/javascript/tutorials/rendering-contentful-rich-text-with-javascript/)