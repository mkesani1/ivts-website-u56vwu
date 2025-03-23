# IndiVillage Website Pages Documentation

## Introduction

This document provides a comprehensive overview of the pages in the IndiVillage website. It covers the structure, functionality, and implementation details of each page, serving as a reference for developers working on the website. The website is built using Next.js App Router, which provides a file-based routing system where each folder in the `src/web/src/app` directory represents a route segment.

## Page Structure

All pages in the IndiVillage website follow a consistent structure with the following components:

1. **Layout**: All pages use the `MainLayout` component which provides the header, footer, and overall page structure.
2. **Metadata**: Each page implements the `generateMetadata` function or exports a `metadata` object for SEO optimization.
3. **Page Header**: Most pages include a `PageHeader` component with title, subtitle, and breadcrumb navigation.
4. **Main Content**: The specific content of each page, typically composed of multiple components.
5. **Call to Action**: Many pages include call-to-action sections to encourage user engagement.

## Homepage

**Path**: `/`
**File**: `src/web/src/app/page.tsx`

The homepage serves as the main entry point for visitors and showcases IndiVillage's AI-as-a-service capabilities and social impact mission. It includes the following sections:

- **Hero Banner**: A visually striking hero section with headline, subheadline, and primary call-to-action buttons.
- **Service Overview**: A grid of service cards highlighting IndiVillage's core AI services.
- **Impact Overview**: A section showcasing IndiVillage's social impact metrics and mission.
- **Case Study Highlight**: Featured case studies demonstrating successful client implementations.
- **Partner Logos**: Logos of trusted partner companies.
- **Call to Action**: Final section encouraging visitors to take action.

The homepage is designed to be visually appealing while clearly communicating IndiVillage's dual value proposition of technological excellence and social impact.

**Key Components:**
- `Hero`
- `ServiceOverview`
- `ImpactOverview`
- `CaseStudyHighlight`
- `PartnerLogos`
- `CTASection`

## Services Pages

### Services Overview Page
**Path**: `/services`
**File**: `src/web/src/app/services/page.tsx`

The services overview page lists all of IndiVillage's AI-as-a-service offerings. It includes:

- Page header with title and breadcrumbs
- Introduction to IndiVillage's services
- Grid of service cards with icons, titles, and brief descriptions
- Call-to-action section

### Service Detail Page
**Path**: `/services/[slug]`
**File**: `src/web/src/app/services/[slug]/page.tsx`

Dynamic page that displays detailed information about a specific service. The page includes:

- Service title and description
- Service features in a grid layout
- How it works section with step-by-step process
- Related case studies
- Sample data upload section
- Call-to-action buttons for demo/quote requests

The service detail pages are dynamically generated based on the service slug parameter. The `generateStaticParams` function is used to pre-render all service pages at build time for optimal performance.

**Key Components:**
- `ServiceDetail`
- `ServiceFeature`
- `HowItWorks`
- `RelatedCaseStudies`

## Case Studies Pages

### Case Studies Overview Page
**Path**: `/case-studies`
**File**: `src/web/src/app/case-studies/page.tsx`

The case studies overview page displays a filterable grid of client success stories. It includes:

- Page header with title and breadcrumbs
- Filter bar for filtering by industry and service type
- Grid of case study cards with images, titles, and brief descriptions

### Case Study Detail Page
**Path**: `/case-studies/[slug]`
**File**: `src/web/src/app/case-studies/[slug]/page.tsx`

Dynamic page that displays detailed information about a specific case study. The page includes:

- Case study title and client information
- Challenge, solution, and results sections
- Key metrics and outcomes
- Related services section
- Call-to-action for similar solutions

The case study detail pages are dynamically generated based on the case study slug parameter. The `generateStaticParams` function is used to pre-render all case study pages at build time.

**Key Components:**
- `CaseStudyCard`
- `CaseStudyDetail`
- `CaseStudyResults`
- `FilterBar`
- `RelatedServices`

## Social Impact Pages

### Impact Overview Page
**Path**: `/impact`
**File**: `src/web/src/app/impact/page.tsx`

The impact overview page showcases IndiVillage's 'AI for Good' mission and social impact initiatives. It includes:

- Page header with title and breadcrumbs
- Impact video or hero image
- Impact metrics section with key statistics
- Mission statement explaining IndiVillage's approach
- Gallery of impact stories
- Sustainable Development Goals (SDG) alignment section
- Partnership call-to-action

### Impact Story Detail Page
**Path**: `/impact/[slug]`
**File**: `src/web/src/app/impact/[slug]/page.tsx`

Dynamic page that displays detailed information about a specific impact story. The page includes:

- Story title and location information
- Story narrative with images
- Beneficiary information
- Impact metrics specific to the story
- Related stories section

The impact story detail pages are dynamically generated based on the story slug parameter.

**Key Components:**
- `ImpactMetrics`
- `ImpactGallery`
- `ImpactStory`
- `MissionStatement`
- `SDGSection`
- `ResponsiveVideo`

## Form Pages

### Contact Page
**Path**: `/contact`
**File**: `src/web/src/app/contact/page.tsx`

The contact page provides a form for visitors to get in touch with IndiVillage. It includes:

- Page header with title and breadcrumbs
- Contact form with fields for name, email, company, phone, and message
- Company contact information and address
- Map or location information

### Demo Request Page
**Path**: `/request-demo`
**File**: `src/web/src/app/request-demo/page.tsx`

The demo request page allows potential clients to request a demonstration of IndiVillage's services. It includes:

- Page header with title and breadcrumbs
- Comprehensive form with fields for:
  - Contact information (name, email, company, phone)
  - Service interests (checkboxes for different services)
  - Preferred demo date and time
  - Project details
  - How they heard about IndiVillage
- Form submission handling with validation
- Success message and follow-up information

Both form pages implement client-side validation, CAPTCHA verification, and analytics tracking for form submissions.

**Key Components:**
- `ContactForm`
- `DemoRequestForm`
- `Captcha`
- `FormField`
- `FormError`
- `FormSuccess`

## File Upload Pages

### Upload Sample Page
**Path**: `/upload-sample`
**File**: `src/web/src/app/upload-sample/page.tsx`

The upload sample page allows potential clients to upload sample datasets for analysis. It includes:

- Page header with title and breadcrumbs
- Multi-step form with:
  - Contact information (name, email, company, phone)
  - Service interest selection
  - File upload dropzone with drag-and-drop support
  - Optional project description
- File validation for size and format
- Form submission handling with validation

### Upload Processing Page
**Path**: `/upload-sample/processing`
**File**: `src/web/src/app/upload-sample/processing/page.tsx`

The upload processing page shows the status of the file upload and processing. It includes:

- Page header with title and breadcrumbs
- Processing status indicator with icon
- Progress bar showing completion percentage
- Current processing step information
- Estimated time remaining
- 'What happens next' information section
- Service exploration section while waiting

### Upload Success Page
**Path**: `/upload-sample/success`
**File**: `src/web/src/app/upload-sample/success/page.tsx`

The upload success page confirms successful upload and processing. It includes:

- Page header with title and breadcrumbs
- Success message with confirmation details
- Next steps information
- Related services section
- Call-to-action for demo request

The file upload pages implement secure file handling, real-time status updates, and integration with backend processing services.

**Key Components:**
- `FileUploadForm`
- `FileDropzone`
- `ProgressBar`
- `FormField`
- `FormError`
- `FormSuccess`

## Other Pages

### About Page
**Path**: `/about`
**File**: `src/web/src/app/about/page.tsx`

The about page provides information about IndiVillage's history, mission, and team. It includes sections on the company's founding story, values, and approach.

### Leadership Page
**Path**: `/about/leadership`
**File**: `src/web/src/app/about/leadership/page.tsx`

The leadership page showcases IndiVillage's leadership team with photos, bios, and roles.

### Careers Page
**Path**: `/about/careers`
**File**: `src/web/src/app/about/careers/page.tsx`

The careers page lists job opportunities at IndiVillage and provides information about the company culture and benefits.

### Blog Pages
**Path**: `/blog` and `/blog/[slug]`
**Files**: `src/web/src/app/blog/page.tsx` and `src/web/src/app/blog/[slug]/page.tsx`

The blog section includes an index page listing all blog posts and dynamic detail pages for individual posts.

## Error Pages

### Not Found Page
**Path**: Dynamic 404 routes
**File**: `src/web/src/app/not-found.tsx`

Custom 404 page displayed when a route is not found. It includes a friendly message, search functionality, and navigation links to help users find what they're looking for.

### Error Page
**Path**: Dynamic error routes
**File**: `src/web/src/app/error.tsx`

General error page displayed when an unexpected error occurs. It includes an error message, option to retry, and contact information for support.

### Global Error Page
**Path**: Application-wide errors
**File**: `src/web/src/app/global-error.tsx`

Fallback error page for catastrophic application errors that affect the entire application.

## Page Routing and Navigation

The IndiVillage website uses Next.js App Router for page routing. The routing structure is defined by the folder structure in the `src/web/src/app` directory:

- Each folder represents a route segment
- `page.tsx` files define the UI for a route segment
- Dynamic routes use `[param]` folder naming convention
- Loading states are defined in `loading.tsx` files
- Error states are defined in `error.tsx` and `not-found.tsx` files

Navigation between pages is implemented using Next.js `Link` component for client-side navigation and the `useRouter` hook for programmatic navigation. Breadcrumb navigation is provided on most pages to help users understand their location in the site hierarchy.

## Page Performance Optimization

The IndiVillage website implements several performance optimization techniques for pages:

1. **Static Generation**: Where possible, pages are statically generated at build time using `generateStaticParams` for dynamic routes.

2. **Image Optimization**: Images are optimized using Next.js Image component with appropriate sizing, formats, and lazy loading.

3. **Code Splitting**: Automatic code splitting by route and manual code splitting using dynamic imports for large components.

4. **Font Optimization**: Web fonts are optimized with font display swap and preloading of critical fonts.

5. **Third-party Script Management**: Third-party scripts are loaded with appropriate priority and loading strategies.

6. **Metadata Optimization**: Each page implements proper metadata for SEO using the Next.js metadata API.

Performance metrics are monitored using Core Web Vitals, and optimizations are made based on real user monitoring data.

## Accessibility Considerations

All pages in the IndiVillage website are designed to meet WCAG 2.1 AA compliance standards. Key accessibility features include:

1. **Semantic HTML**: Proper use of heading hierarchy, landmarks, and semantic elements.

2. **Keyboard Navigation**: All interactive elements are keyboard accessible with visible focus states.

3. **ARIA Attributes**: Appropriate ARIA roles, states, and properties for complex components.

4. **Color Contrast**: Sufficient color contrast for text and UI elements.

5. **Screen Reader Support**: Alt text for images, form labels, and descriptive link text.

6. **Responsive Design**: Content remains accessible across all device sizes.

Accessibility is tested using automated tools and manual testing with screen readers and keyboard navigation.

## Internationalization

While the initial version of the IndiVillage website is in English only, the page structure is designed to support future internationalization. The Next.js App Router provides built-in support for internationalization through:

1. **Locale-based Routing**: Future support for routes like `/en/services` and `/fr/services`.

2. **Locale Detection**: Automatic locale detection based on user preferences.

3. **Translation Files**: Structured JSON files for text translations.

4. **Direction Support**: Support for right-to-left (RTL) languages through CSS logical properties.

When internationalization is implemented, each page will load the appropriate translations based on the detected or selected locale.