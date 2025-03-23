# IndiVillage Website Component Documentation

This document provides a comprehensive guide to the component architecture, usage patterns, and guidelines for the IndiVillage website frontend. It serves as the primary reference for developers working with the UI components of the site.

## Table of Contents

- [Component Architecture](#component-architecture)
  - [Folder Structure](#folder-structure)
  - [Component Categories](#component-categories)
  - [Component Hierarchy](#component-hierarchy)
- [UI Components](#ui-components)
  - [Button](#button)
  - [Input](#input)
  - [Select](#select)
  - [Checkbox](#checkbox)
  - [Textarea](#textarea)
  - [Card](#card)
  - [Modal](#modal)
  - [Alert](#alert)
  - [Badge](#badge)
  - [Icon](#icon)
  - [Loader](#loader)
  - [Tooltip](#tooltip)
- [Form Components](#form-components)
  - [FormField](#formfield)
  - [FileDropzone](#filedropzone)
  - [Captcha](#captcha)
  - [ProgressBar](#progressbar)
  - [FormSuccess](#formsuccess)
  - [FormError](#formerror)
  - [ContactForm](#contactform)
  - [DemoRequestForm](#demorequestform)
  - [QuoteRequestForm](#quoterequestform)
  - [FileUploadForm](#fileuploadform)
- [Layout Components](#layout-components)
  - [Header](#header)
  - [Footer](#footer)
  - [Navigation](#navigation)
  - [MobileNavigation](#mobilenavigation)
  - [MainLayout](#mainlayout)
- [Shared Components](#shared-components)
  - [PageHeader](#pageheader)
  - [SectionHeader](#sectionheader)
  - [Breadcrumb](#breadcrumb)
  - [MetaTags](#metatags)
  - [ImageWithFallback](#imagewithfallback)
  - [AnimatedCounter](#animatedcounter)
  - [Carousel](#carousel)
  - [ResponsiveVideo](#responsivevideo)
  - [ErrorBoundary](#errorboundary)
- [Feature Components](#feature-components)
  - [Home Components](#home-components)
  - [Service Components](#service-components)
  - [Case Study Components](#case-study-components)
  - [Impact Components](#impact-components)
- [Component Best Practices](#component-best-practices)
  - [Component Structure](#component-structure)
  - [Accessibility](#accessibility)
  - [Performance](#performance)
  - [Testing](#testing)
  - [Documentation](#documentation)
- [Custom Hooks](#custom-hooks)
  - [useForm](#useform)
  - [useFileUpload](#usefileupload)
  - [useBreakpoint](#usebreakpoint)
  - [useAnalytics](#useanalytics)
  - [useUploadStatus](#useuploadstatus)
  - [Other Custom Hooks](#other-custom-hooks)
- [Component Theming](#component-theming)
  - [Color System](#color-system)
  - [Typography](#typography)
  - [Spacing](#spacing)
  - [Breakpoints](#breakpoints)
  - [Customization](#customization)

## Component Architecture

The IndiVillage website's frontend is built using a component-based architecture with React. Components are organized into logical categories to promote reusability, maintainability, and a consistent user experience.

### Folder Structure

The component folder structure follows a logical organization:

```
/src
  /components
    /ui             # Base UI components
    /form           # Form-related components
    /layout         # Page structure components
    /shared         # Reusable components
    /features       # Feature-specific components
      /home
      /services
      /case-studies
      /impact
    /hooks          # Custom React hooks
```

### Component Categories

Components are categorized based on their role in the application:

- **UI Components**: Base building blocks like buttons, inputs, modals
- **Form Components**: Components for user input and data collection
- **Layout Components**: Components that define the page structure
- **Shared Components**: Reusable components used across multiple features
- **Feature Components**: Components specific to particular sections of the website
- **Hooks**: Custom React hooks used with components

### Component Hierarchy

The component hierarchy follows a composition pattern, where complex components are built from simpler ones:

```
MainLayout
├── Header
│   ├── Navigation
│   └── MobileNavigation
├── Page Content
│   ├── PageHeader
│   │   └── Breadcrumb
│   ├── Feature Components
│   │   ├── UI Components
│   │   └── Shared Components
│   └── Forms
│       └── Form Components
└── Footer
```

## UI Components

### Button

The Button component is used for all clickable actions throughout the site.

**Props**
- `variant`: "primary" | "secondary" | "tertiary" (default: "primary")
- `size`: "small" | "medium" | "large" (default: "medium")
- `disabled`: boolean (default: false)
- `loading`: boolean (default: false)
- `onClick`: function
- `type`: "button" | "submit" | "reset" (default: "button")
- `children`: React.ReactNode

**Usage**

```jsx
// Primary button (default)
<Button onClick={handleClick}>Click Me</Button>

// Secondary button
<Button variant="secondary" size="large">Learn More</Button>

// Tertiary button with loading state
<Button variant="tertiary" loading={isLoading}>Submit</Button>

// Disabled button
<Button disabled>Unavailable</Button>
```

**Accessibility**
- When used as a submit button, it should be within a `<form>` element
- When used with loading state, it displays a spinner and adds `aria-busy="true"`
- When used as a link, it should use the appropriate aria attributes

### Input

The Input component is used for single-line text input.

**Props**
- `id`: string (required)
- `name`: string (required)
- `type`: string (default: "text")
- `value`: string
- `placeholder`: string
- `disabled`: boolean (default: false)
- `required`: boolean (default: false)
- `error`: string
- `onChange`: function (required)
- `onBlur`: function
- `icon`: React.ReactNode
- `iconPosition`: "left" | "right" (default: "left")

**Usage**

```jsx
// Basic input
<Input 
  id="email"
  name="email"
  type="email"
  value={email}
  onChange={handleChange}
  placeholder="Enter your email"
/>

// Input with error state
<Input
  id="username"
  name="username"
  value={username}
  onChange={handleChange}
  error="Username is required"
/>

// Input with icon
<Input
  id="search"
  name="search"
  value={searchTerm}
  onChange={handleChange}
  placeholder="Search"
  icon={<SearchIcon />}
  iconPosition="right"
/>
```

**Accessibility**
- Always used with a proper label (typically with FormField component)
- Error messages are linked via aria-describedby
- Uses appropriate input types (email, password, etc.)

### Select

The Select component is used for selecting from a list of options.

**Props**
- `id`: string (required)
- `name`: string (required)
- `value`: string
- `options`: Array<{ value: string, label: string }>
- `placeholder`: string
- `disabled`: boolean (default: false)
- `required`: boolean (default: false)
- `error`: string
- `onChange`: function (required)
- `onBlur`: function

**Usage**

```jsx
// Basic select
<Select
  id="country"
  name="country"
  value={country}
  onChange={handleChange}
  options={[
    { value: 'us', label: 'United States' },
    { value: 'ca', label: 'Canada' },
    { value: 'uk', label: 'United Kingdom' }
  ]}
  placeholder="Select a country"
/>

// Select with error state
<Select
  id="service"
  name="service"
  value={service}
  onChange={handleChange}
  options={serviceOptions}
  error="Please select a service"
/>
```

**Accessibility**
- Implements proper ARIA roles for custom select UI
- Supports keyboard navigation
- Error messages are linked via aria-describedby

### Checkbox

The Checkbox component is used for boolean input selections.

**Props**
- `id`: string (required)
- `name`: string (required)
- `checked`: boolean
- `disabled`: boolean (default: false)
- `required`: boolean (default: false)
- `error`: string
- `onChange`: function (required)
- `label`: string | React.ReactNode
- `labelPosition`: "right" | "left" (default: "right")

**Usage**

```jsx
// Basic checkbox
<Checkbox
  id="terms"
  name="terms"
  checked={isAccepted}
  onChange={handleChange}
  label="I agree to the terms and conditions"
/>

// Checkbox with error
<Checkbox
  id="privacy"
  name="privacy"
  checked={privacyAccepted}
  onChange={handleChange}
  label="I agree to the privacy policy"
  error="You must accept the privacy policy"
/>

// Disabled checkbox
<Checkbox
  id="newsletter"
  name="newsletter"
  checked={true}
  onChange={handleChange}
  label="Subscribe to newsletter"
  disabled
/>
```

**Accessibility**
- Associates the label with the checkbox using htmlFor
- Error messages are linked via aria-describedby

### Textarea

The Textarea component is used for multi-line text input.

**Props**
- `id`: string (required)
- `name`: string (required)
- `value`: string
- `placeholder`: string
- `disabled`: boolean (default: false)
- `required`: boolean (default: false)
- `error`: string
- `onChange`: function (required)
- `onBlur`: function
- `rows`: number (default: 4)
- `maxLength`: number
- `showCharCount`: boolean (default: false)

**Usage**

```jsx
// Basic textarea
<Textarea
  id="message"
  name="message"
  value={message}
  onChange={handleChange}
  placeholder="Enter your message"
  rows={6}
/>

// Textarea with character count
<Textarea
  id="description"
  name="description"
  value={description}
  onChange={handleChange}
  maxLength={500}
  showCharCount
/>

// Textarea with error
<Textarea
  id="feedback"
  name="feedback"
  value={feedback}
  onChange={handleChange}
  error="Feedback is required"
/>
```

**Accessibility**
- Always used with a proper label (typically with FormField component)
- Error messages are linked via aria-describedby
- Character count information is announced to screen readers

### Card

The Card component is used to create visually distinct content containers.

**Props**
- `variant`: "default" | "outlined" | "elevated" (default: "default")
- `padding`: "none" | "small" | "medium" | "large" (default: "medium")
- `className`: string
- `children`: React.ReactNode
- `onClick`: function

**Usage**

```jsx
// Basic card
<Card>
  <h3>Service Overview</h3>
  <p>Our data preparation services transform raw data into AI-ready datasets.</p>
  <Button>Learn More</Button>
</Card>

// Elevated card with click handler
<Card variant="elevated" onClick={() => navigateToService('data-prep')}>
  <Icon name="data-preparation" />
  <h3>Data Preparation</h3>
  <p>Transform raw data into AI-ready datasets.</p>
</Card>

// Outlined card with custom padding
<Card variant="outlined" padding="large">
  <TestimonialContent />
</Card>
```

**Accessibility**
- If clickable, adds proper keyboard and focus handling
- Maintains proper contrast for content
- Preserves content semantics within the card

### Modal

The Modal component displays content in a layer that overlays the page.

**Props**
- `isOpen`: boolean (required)
- `onClose`: function (required)
- `title`: string
- `size`: "small" | "medium" | "large" (default: "medium")
- `children`: React.ReactNode
- `closeOnBackdropClick`: boolean (default: true)
- `closeOnEsc`: boolean (default: true)
- `footer`: React.ReactNode

**Usage**

```jsx
// Basic modal
<Modal
  isOpen={isModalOpen}
  onClose={handleCloseModal}
  title="Request a Demo"
>
  <DemoRequestForm onSubmit={handleDemoRequest} />
</Modal>

// Modal with custom footer
<Modal
  isOpen={isConfirmOpen}
  onClose={handleCloseConfirm}
  title="Confirm Submission"
  footer={
    <div className="flex justify-end gap-4">
      <Button variant="secondary" onClick={handleCloseConfirm}>Cancel</Button>
      <Button onClick={handleConfirm}>Confirm</Button>
    </div>
  }
>
  <p>Are you sure you want to submit this request?</p>
</Modal>
```

**Accessibility**
- Traps focus within the modal when open
- Returns focus to the trigger element when closed
- Supports closing via Escape key
- Uses proper ARIA attributes for screen readers

### Alert

The Alert component displays important messages to the user.

**Props**
- `variant`: "success" | "error" | "warning" | "info" (default: "info")
- `title`: string
- `message`: string | React.ReactNode (required)
- `onClose`: function
- `showIcon`: boolean (default: true)
- `dismissible`: boolean (default: false)

**Usage**

```jsx
// Info alert
<Alert 
  message="Learn how our services can benefit your business." 
/>

// Success alert with title
<Alert
  variant="success"
  title="Success!"
  message="Your form has been submitted successfully."
/>

// Error alert that can be dismissed
<Alert
  variant="error"
  message="There was an error processing your request. Please try again."
  dismissible
  onClose={handleDismissError}
/>
```

**Accessibility**
- Uses appropriate ARIA roles for alerts
- Uses appropriate colors with sufficient contrast
- Icons have appropriate alt text

### Badge

The Badge component displays small numerical or status indicators.

**Props**
- `variant`: "primary" | "secondary" | "success" | "error" | "warning" | "info" (default: "primary")
- `size`: "small" | "medium" (default: "medium")
- `children`: React.ReactNode
- `rounded`: boolean (default: false)

**Usage**

```jsx
// Primary badge
<Badge>New</Badge>

// Success badge
<Badge variant="success">Completed</Badge>

// Error badge with number
<Badge variant="error">3</Badge>

// Rounded badge for notifications
<Badge variant="primary" rounded>5</Badge>
```

**Accessibility**
- Maintains proper color contrast
- Uses appropriate semantic elements

### Icon

The Icon component displays vector icons from the icon library.

**Props**
- `name`: string (required) - name of the icon from the library
- `size`: "small" | "medium" | "large" (default: "medium")
- `color`: string - color token or CSS color value
- `className`: string
- `title`: string - for accessibility

**Usage**

```jsx
// Basic icon
<Icon name="arrow-right" />

// Icon with custom size and color
<Icon 
  name="data-collection" 
  size="large" 
  color="primary.500"
/>

// Icon with accessibility title
<Icon
  name="warning"
  color="warning.500"
  title="Warning message"
/>
```

**Accessibility**
- Decorative icons use aria-hidden="true"
- Meaningful icons have descriptive title or aria-label

### Loader

The Loader component indicates loading states.

**Props**
- `variant`: "spinner" | "dots" | "bar" (default: "spinner")
- `size`: "small" | "medium" | "large" (default: "medium")
- `color`: string - color token or CSS color value
- `text`: string - loading text to display

**Usage**

```jsx
// Basic spinner
<Loader />

// Dots loader with text
<Loader 
  variant="dots" 
  text="Uploading your file..." 
/>

// Custom colored loader
<Loader
  size="large"
  color="primary.500"
/>
```

**Accessibility**
- Uses aria-busy="true"
- Includes screen reader text to indicate loading state
- Animation is reduced if user prefers reduced motion

### Tooltip

The Tooltip component provides additional information in a small overlay.

**Props**
- `content`: string | React.ReactNode (required)
- `position`: "top" | "right" | "bottom" | "left" (default: "top")
- `children`: React.ReactNode (required)
- `delay`: number (default: 300) - delay before showing in ms
- `maxWidth`: string (default: "200px")

**Usage**

```jsx
// Basic tooltip
<Tooltip content="Additional information about this feature">
  <Icon name="info-circle" />
</Tooltip>

// Tooltip with custom position
<Tooltip
  content="Files must be under 50MB and in supported formats"
  position="right"
>
  <Button variant="secondary" size="small">Learn More</Button>
</Tooltip>
```

**Accessibility**
- Uses appropriate ARIA attributes for tooltip
- Supports keyboard activation for non-mouse users
- Ensures tooltip content is readable

## Form Components

### FormField

The FormField component wraps input elements with labels and error handling.

**Props**
- `id`: string (required)
- `label`: string (required)
- `required`: boolean (default: false)
- `error`: string
- `hint`: string
- `children`: React.ReactNode (required)

**Usage**

```jsx
// Basic form field with input
<FormField
  id="firstName"
  label="First Name"
  required
>
  <Input
    id="firstName"
    name="firstName"
    value={firstName}
    onChange={handleChange}
  />
</FormField>

// Form field with error and hint
<FormField
  id="email"
  label="Email Address"
  required
  error={errors.email}
  hint="We'll never share your email with anyone else."
>
  <Input
    id="email"
    name="email"
    type="email"
    value={email}
    onChange={handleChange}
  />
</FormField>
```

**Accessibility**
- Associates label with input using htmlFor
- Communicates errors via aria-describedby
- Required fields are indicated visually and with aria-required

### FileDropzone

The FileDropzone component enables drag-and-drop file uploads.

**Props**
- `id`: string (required)
- `onFilesSelected`: function (required) - callback with selected files
- `accept`: string - allowed file types (e.g., ".csv,.json,.xml")
- `maxSize`: number - maximum file size in bytes
- `maxFiles`: number (default: 1)
- `disabled`: boolean (default: false)
- `error`: string
- `value`: File[] - current selected files

**Usage**

```jsx
// Basic file dropzone
<FileDropzone
  id="uploadData"
  onFilesSelected={handleFileSelection}
  accept=".csv,.json,.xml"
  maxSize={52428800} // 50MB
/>

// File dropzone with validation error
<FileDropzone
  id="uploadImage"
  onFilesSelected={handleImageSelection}
  accept=".jpg,.png"
  maxSize={10485760} // 10MB
  error="Please upload an image file under 10MB"
/>
```

**Accessibility**
- Provides keyboard-accessible alternative to drag-and-drop
- Clearly communicates file requirements and errors
- Uses appropriate ARIA attributes

### Captcha

The Captcha component integrates reCAPTCHA for form security.

**Props**
- `siteKey`: string (required) - reCAPTCHA site key
- `onVerify`: function (required) - callback when verified
- `size`: "normal" | "compact" (default: "normal")
- `theme`: "light" | "dark" (default: "light")

**Usage**

```jsx
// Basic reCAPTCHA
<Captcha
  siteKey={process.env.NEXT_PUBLIC_RECAPTCHA_SITE_KEY}
  onVerify={handleCaptchaVerify}
/>

// Compact dark theme reCAPTCHA
<Captcha
  siteKey={process.env.NEXT_PUBLIC_RECAPTCHA_SITE_KEY}
  onVerify={handleCaptchaVerify}
  size="compact"
  theme="dark"
/>
```

**Accessibility**
- Uses the accessibility features provided by reCAPTCHA
- Ensures page doesn't rely solely on CAPTCHA for form submission

### ProgressBar

The ProgressBar component visualizes upload or processing progress.

**Props**
- `value`: number (required) - progress percentage (0-100)
- `variant`: "default" | "success" | "error" (default: "default")
- `showPercentage`: boolean (default: true)
- `size`: "small" | "medium" | "large" (default: "medium")
- `label`: string - descriptive label
- `indeterminate`: boolean (default: false) - for unknown progress

**Usage**

```jsx
// Basic progress bar at 75%
<ProgressBar value={75} />

// Progress bar with label and no percentage
<ProgressBar
  value={50}
  label="Uploading file..."
  showPercentage={false}
/>

// Indeterminate progress bar
<ProgressBar
  indeterminate
  label="Processing your request..."
/>
```

**Accessibility**
- Uses aria-valuemin, aria-valuemax, and aria-valuenow
- Provides text alternative for screen readers
- Uses appropriate color contrast

### FormSuccess

The FormSuccess component displays success messages after form submission.

**Props**
- `title`: string (default: "Success!")
- `message`: string | React.ReactNode (required)
- `actions`: React.ReactNode - buttons or links for next steps

**Usage**

```jsx
// Basic success message
<FormSuccess
  message="Your request has been submitted successfully."
/>

// Success with custom title and actions
<FormSuccess
  title="Request Received!"
  message="We've received your demo request and will contact you within 24 hours."
  actions={
    <>
      <Button onClick={resetForm}>Submit Another</Button>
      <Button variant="secondary" onClick={navigateToHome}>Return Home</Button>
    </>
  }
/>
```

**Accessibility**
- Uses semantic HTML for heading structure
- Focuses the component when displayed for screen reader users

### FormError

The FormError component displays error messages for form submissions.

**Props**
- `title`: string (default: "Error")
- `message`: string | React.ReactNode (required)
- `actions`: React.ReactNode - buttons or links to resolve the error

**Usage**

```jsx
// Basic error message
<FormError
  message="There was a problem submitting your form. Please try again."
/>

// Error with custom title and actions
<FormError
  title="Submission Failed"
  message="We encountered an error processing your request. Please try again or contact support."
  actions={
    <>
      <Button onClick={retrySubmission}>Try Again</Button>
      <Button variant="secondary" onClick={contactSupport}>Contact Support</Button>
    </>
  }
/>
```

**Accessibility**
- Uses appropriate ARIA roles for alerts
- Focuses the component when displayed for screen reader users

### ContactForm

The ContactForm component is a complete form for general inquiries.

**Props**
- `onSubmit`: function (required) - form submission handler
- `initialValues`: object - initial form values
- `loading`: boolean (default: false)
- `error`: string - submission error
- `success`: boolean (default: false)

**Usage**

```jsx
// Basic contact form
<ContactForm
  onSubmit={handleContactSubmit}
/>

// Contact form with initial values and loading state
<ContactForm
  onSubmit={handleContactSubmit}
  initialValues={{
    name: currentUser.name,
    email: currentUser.email
  }}
  loading={isSubmitting}
/>

// Contact form with error or success state
<ContactForm
  onSubmit={handleContactSubmit}
  error={submissionError}
  success={isSubmissionSuccessful}
/>
```

**Accessibility**
- All form fields have proper labels
- Validation errors are clearly communicated
- Loading state is properly indicated

### DemoRequestForm

The DemoRequestForm component is a specialized form for requesting service demonstrations.

**Props**
- `onSubmit`: function (required) - form submission handler
- `initialValues`: object - initial form values
- `loading`: boolean (default: false)
- `error`: string - submission error
- `success`: boolean (default: false)
- `serviceOptions`: Array<{ value: string, label: string }> - available services

**Usage**

```jsx
// Basic demo request form
<DemoRequestForm
  onSubmit={handleDemoRequest}
  serviceOptions={availableServices}
/>

// Demo request form with initial values
<DemoRequestForm
  onSubmit={handleDemoRequest}
  serviceOptions={availableServices}
  initialValues={{
    company: currentCompany,
    serviceInterest: preselectedService
  }}
  loading={isSubmitting}
/>
```

**Accessibility**
- Uses FormField components for proper labeling
- Clearly indicates required fields
- Provides clear feedback on submission status

### QuoteRequestForm

The QuoteRequestForm component is a specialized form for requesting service quotes.

**Props**
- `onSubmit`: function (required) - form submission handler
- `initialValues`: object - initial form values
- `loading`: boolean (default: false)
- `error`: string - submission error
- `success`: boolean (default: false)
- `serviceOptions`: Array<{ value: string, label: string }> - available services

**Usage**

```jsx
// Basic quote request form
<QuoteRequestForm
  onSubmit={handleQuoteRequest}
  serviceOptions={availableServices}
/>

// Quote request form with loading state
<QuoteRequestForm
  onSubmit={handleQuoteRequest}
  serviceOptions={availableServices}
  loading={isSubmitting}
/>
```

**Accessibility**
- All form fields have proper labels
- Required fields are clearly marked
- Submission state is properly communicated

### FileUploadForm

The FileUploadForm component is a specialized form for file uploads with metadata collection.

**Props**
- `onSubmit`: function (required) - form submission handler
- `fileTypes`: Array<string> - allowed file types
- `maxSize`: number - maximum file size in bytes
- `loading`: boolean (default: false)
- `error`: string - submission error
- `success`: boolean (default: false)
- `serviceOptions`: Array<{ value: string, label: string }> - available services

**Usage**

```jsx
// Basic file upload form
<FileUploadForm
  onSubmit={handleFileUpload}
  fileTypes={['.csv', '.json', '.xml']}
  maxSize={52428800} // 50MB
  serviceOptions={availableServices}
/>

// File upload form with error state
<FileUploadForm
  onSubmit={handleFileUpload}
  fileTypes={['.csv', '.json', '.xml']}
  maxSize={52428800}
  serviceOptions={availableServices}
  error="There was an error uploading your file. Please try again."
/>
```

**Accessibility**
- Clearly communicates file requirements
- Provides accessible error messages
- Progress is clearly indicated during upload

## Layout Components

### Header

The Header component displays the site branding, navigation, and utility links.

**Props**
- `transparent`: boolean (default: false) - for transparent header on specific pages
- `sticky`: boolean (default: true) - for sticky header that stays visible on scroll

**Usage**

```jsx
// Default header
<Header />

// Transparent header for hero sections
<Header transparent />

// Non-sticky header
<Header sticky={false} />
```

**Accessibility**
- Uses semantic HTML (header, nav)
- Implements keyboard navigation
- Mobile menu is properly handled for screen readers

### Footer

The Footer component displays site-wide links, legal information, and social media.

**Props**
- `variant`: "default" | "simple" (default: "default")

**Usage**

```jsx
// Default footer with all sections
<Footer />

// Simple footer for specific pages
<Footer variant="simple" />
```

**Accessibility**
- Uses semantic HTML (footer, nav)
- Link groups have proper headings
- Social media icons have accessible labels

### Navigation

The Navigation component displays the main site navigation.

**Props**
- `items`: Array - navigation structure

**Usage**

```jsx
// Navigation with predefined items
<Navigation items={navigationItems} />
```

**Accessibility**
- Implements proper keyboard navigation
- Dropdown menus are accessible
- Active state is properly indicated

### MobileNavigation

The MobileNavigation component displays navigation optimized for mobile devices.

**Props**
- `items`: Array - navigation structure
- `isOpen`: boolean (required)
- `onClose`: function (required)

**Usage**

```jsx
// Mobile navigation component
<MobileNavigation
  items={navigationItems}
  isOpen={isMobileMenuOpen}
  onClose={closeMobileMenu}
/>
```

**Accessibility**
- Traps focus within open mobile menu
- Uses appropriate ARIA for menu state
- Supports closing via Escape key

### MainLayout

The MainLayout component wraps all pages with consistent header and footer.

**Props**
- `children`: React.ReactNode (required)
- `transparentHeader`: boolean (default: false)
- `simpleFooter`: boolean (default: false)
- `stickyHeader`: boolean (default: true)

**Usage**

```jsx
// Basic layout
<MainLayout>
  <HomePage />
</MainLayout>

// Layout with transparent header
<MainLayout transparentHeader>
  <LandingPage />
</MainLayout>
```

**Accessibility**
- Implements skip to content link
- Maintains logical focus order
- Preserves semantic structure

## Shared Components

### PageHeader

The PageHeader component displays the page title, subtitle, and breadcrumb navigation.

**Props**
- `title`: string (required)
- `subtitle`: string
- `breadcrumbs`: Array<{ label: string, url: string }>
- `background`: "light" | "dark" | "primary" (default: "light")
- `align`: "left" | "center" (default: "left")

**Usage**

```jsx
// Basic page header
<PageHeader
  title="Data Preparation Services"
/>

// Complete page header
<PageHeader
  title="Data Preparation Services"
  subtitle="Transform raw data into AI-ready datasets"
  breadcrumbs={[
    { label: 'Home', url: '/' },
    { label: 'Services', url: '/services' },
    { label: 'Data Preparation', url: '/services/data-preparation' }
  ]}
  background="primary"
  align="center"
/>
```

**Accessibility**
- Uses appropriate heading levels
- Breadcrumbs are properly marked up for accessibility

### SectionHeader

The SectionHeader component provides consistent section headings.

**Props**
- `title`: string (required)
- `subtitle`: string
- `align`: "left" | "center" | "right" (default: "left")
- `divider`: boolean (default: false)

**Usage**

```jsx
// Basic section header
<SectionHeader
  title="Our Services"
/>

// Section header with subtitle and center alignment
<SectionHeader
  title="AI for Good: Our Impact"
  subtitle="Creating sustainable livelihoods through technology"
  align="center"
  divider
/>
```

**Accessibility**
- Uses appropriate heading levels
- Maintains proper contrast and text size

### Breadcrumb

The Breadcrumb component displays the page navigation hierarchy.

**Props**
- `items`: Array<{ label: string, url: string }> (required)

**Usage**

```jsx
// Basic breadcrumb navigation
<Breadcrumb
  items={[
    { label: 'Home', url: '/' },
    { label: 'Services', url: '/services' },
    { label: 'Data Preparation', url: '/services/data-preparation' }
  ]}
/>
```

**Accessibility**
- Uses appropriate ARIA for breadcrumb navigation
- Visual separators are not read by screen readers

### MetaTags

The MetaTags component manages SEO and social sharing metadata.

**Props**
- `title`: string (required)
- `description`: string (required)
- `keywords`: string
- `image`: string - social sharing image URL
- `canonical`: string - canonical URL
- `type`: string (default: "website") - Open Graph type

**Usage**

```jsx
// Basic meta tags
<MetaTags
  title="Data Preparation Services | IndiVillage"
  description="Transform your raw data into AI-ready datasets with IndiVillage's comprehensive data preparation services."
/>

// Complete meta tags for social sharing
<MetaTags
  title="Data Preparation Services | IndiVillage"
  description="Transform your raw data into AI-ready datasets with IndiVillage's comprehensive data preparation services."
  keywords="data preparation, data annotation, AI data, machine learning data"
  image="https://www.indivillage.com/images/services/data-preparation.jpg"
  canonical="https://www.indivillage.com/services/data-preparation"
  type="article"
/>
```

**Accessibility**
- Provides appropriate page title for screen readers
- Enhances discoverability through proper metadata

### ImageWithFallback

The ImageWithFallback component displays images with graceful fallback handling.

**Props**
- `src`: string (required)
- `alt`: string (required)
- `fallbackSrc`: string - URL to fallback image
- `...rest`: other image props (width, height, className, etc.)

**Usage**

```jsx
// Basic image with fallback
<ImageWithFallback
  src="/images/case-studies/retail-client.jpg"
  fallbackSrc="/images/placeholder.jpg"
  alt="Retail client case study"
  width={640}
  height={360}
/>
```

**Accessibility**
- Requires meaningful alt text
- Handles loading states appropriately

### AnimatedCounter

The AnimatedCounter component displays animated number counts for impact metrics.

**Props**
- `end`: number (required) - final number to count to
- `duration`: number (default: 2000) - animation duration in ms
- `prefix`: string - text before number
- `suffix`: string - text after number

**Usage**

```jsx
// Basic animated counter
<AnimatedCounter end={1000} />

// Counter with prefix and suffix
<AnimatedCounter
  end={50000}
  prefix="Over "
  suffix="+ Lives Transformed"
  duration={2500}
/>
```

**Accessibility**
- Provides non-animated version for reduced motion preference
- Uses appropriate ARIA to announce the final value

### Carousel

The Carousel component displays a slideshow of content.

**Props**
- `items`: Array<React.ReactNode> (required)
- `autoPlay`: boolean (default: false)
- `interval`: number (default: 5000) - time between slides in ms
- `showDots`: boolean (default: true)
- `showArrows`: boolean (default: true)

**Usage**

```jsx
// Basic carousel
<Carousel
  items={[
    <TestimonialCard key="1" author="John Doe" />,
    <TestimonialCard key="2" author="Jane Smith" />,
    <TestimonialCard key="3" author="Alex Johnson" />
  ]}
/>

// Auto-playing carousel
<Carousel
  items={caseStudySlides}
  autoPlay
  interval={7000}
/>
```

**Accessibility**
- Implements keyboard navigation
- Uses appropriate ARIA for carousel
- Pauses auto-play on hover or focus

### ResponsiveVideo

The ResponsiveVideo component embeds videos with responsive sizing.

**Props**
- `src`: string (required) - video embed URL
- `title`: string (required)
- `aspectRatio`: "16:9" | "4:3" | "1:1" (default: "16:9")
- `allowFullScreen`: boolean (default: true)

**Usage**

```jsx
// YouTube video embed
<ResponsiveVideo
  src="https://www.youtube.com/embed/VIDEO_ID"
  title="IndiVillage Impact Story"
/>

// Vimeo video with custom aspect ratio
<ResponsiveVideo
  src="https://player.vimeo.com/video/VIDEO_ID"
  title="Data Preparation Process"
  aspectRatio="4:3"
/>
```

**Accessibility**
- Requires title for screen readers
- Maintains proper aspect ratio on resize

### ErrorBoundary

The ErrorBoundary component catches JavaScript errors in child components.

**Props**
- `children`: React.ReactNode (required)
- `fallback`: React.ReactNode - custom fallback UI
- `onError`: function - error callback

**Usage**

```jsx
// Basic error boundary
<ErrorBoundary>
  <FeatureComponent />
</ErrorBoundary>

// Error boundary with custom fallback
<ErrorBoundary
  fallback={<ErrorDisplay message="Something went wrong with this component" />}
  onError={logErrorToService}
>
  <ComplexComponent />
</ErrorBoundary>
```

**Accessibility**
- Provides accessible error messages
- Maintains focus for keyboard users after error

## Feature Components

### Home Components

Home components are specialized components used on the homepage.

#### Hero

Displays the main hero section on the homepage.

**Props**
- `title`: string (required)
- `subtitle`: string
- `ctaButtons`: Array<{ label: string, url: string, variant: string }>
- `backgroundImage`: string

**Usage**

```jsx
<Hero
  title="AI-Powered Solutions with Social Impact"
  subtitle="Transform your business with AI solutions that create positive social change"
  ctaButtons={[
    { label: 'Learn More', url: '/about', variant: 'secondary' },
    { label: 'Request Demo', url: '/request-demo', variant: 'primary' }
  ]}
  backgroundImage="/images/hero-background.jpg"
/>
```

#### ServiceOverview

Displays a grid of service cards on the homepage.

**Props**
- `services`: Array<{ title: string, description: string, icon: string, url: string }>

**Usage**

```jsx
<ServiceOverview services={servicesList} />
```

#### ImpactOverview

Displays impact metrics and mission statement on the homepage.

**Props**
- `metrics`: Array<{ value: number, label: string }>
- `missionStatement`: string
- `imageUrl`: string

**Usage**

```jsx
<ImpactOverview
  metrics={impactMetrics}
  missionStatement="Creating sustainable livelihoods through technology while delivering exceptional AI services."
  imageUrl="/images/impact/community.jpg"
/>
```

#### PartnerLogos

Displays a scrolling or static list of partner/client logos.

**Props**
- `logos`: Array<{ src: string, alt: string, url: string }>
- `scrolling`: boolean (default: false)

**Usage**

```jsx
<PartnerLogos
  logos={clientLogos}
  scrolling
/>
```

#### CTASection

Displays a call-to-action section with multiple buttons.

**Props**
- `title`: string (required)
- `buttons`: Array<{ label: string, url: string, variant: string }>
- `background`: "light" | "dark" | "primary" (default: "primary")

**Usage**

```jsx
<CTASection
  title="Ready to Transform Your Business?"
  buttons={[
    { label: 'Request Demo', url: '/request-demo', variant: 'primary' },
    { label: 'Upload Sample Data', url: '/upload-data', variant: 'secondary' },
    { label: 'Contact Us', url: '/contact', variant: 'tertiary' }
  ]}
/>
```

### Service Components

Service components are specialized components used on service-related pages.

#### ServiceCard

Displays a card for a specific service with icon and description.

**Props**
- `title`: string (required)
- `description`: string (required)
- `icon`: string (required)
- `url`: string (required)

**Usage**

```jsx
<ServiceCard
  title="Data Preparation"
  description="Transform raw data into AI-ready datasets"
  icon="data-preparation"
  url="/services/data-preparation"
/>
```

#### ServiceDetail

Displays detailed information about a service.

**Props**
- `title`: string (required)
- `description`: string (required)
- `imageUrl`: string
- `features`: Array<{ title: string, description: string, icon: string }>

**Usage**

```jsx
<ServiceDetail
  title="Data Preparation"
  description="Transform raw data into AI-ready datasets with our comprehensive data preparation services."
  imageUrl="/images/services/data-preparation.jpg"
  features={dataPreparationFeatures}
/>
```

#### ServiceFeature

Displays a specific feature of a service.

**Props**
- `title`: string (required)
- `description`: string (required)
- `icon`: string (required)

**Usage**

```jsx
<ServiceFeature
  title="Data Annotation"
  description="Precise tagging of data elements for AI training"
  icon="annotation"
/>
```

#### HowItWorks

Displays a step-by-step process explanation.

**Props**
- `steps`: Array<{ title: string, description: string, icon: string }>

**Usage**

```jsx
<HowItWorks steps={processSteps} />
```

#### RelatedCaseStudies

Displays case studies related to a specific service.

**Props**
- `caseStudies`: Array<{ title: string, client: string, description: string, imageUrl: string, url: string }>
- `title`: string (default: "Case Studies")

**Usage**

```jsx
<RelatedCaseStudies
  caseStudies={relatedCaseStudies}
  title="Client Success Stories"
/>
```

### Case Study Components

Case study components are specialized components used for displaying case studies.

#### CaseStudyCard

Displays a card for a specific case study.

**Props**
- `title`: string (required)
- `client`: string (required)
- `description`: string (required)
- `imageUrl`: string (required)
- `url`: string (required)
- `industry`: string
- `service`: string

**Usage**

```jsx
<CaseStudyCard
  title="E-Commerce Product Categorization"
  client="Major Retailer"
  description="How we helped improve product search accuracy by 40%"
  imageUrl="/images/case-studies/retail-client.jpg"
  url="/case-studies/retail-product-categorization"
  industry="Retail"
  service="Data Preparation"
/>
```

#### CaseStudyDetail

Displays detailed information about a case study.

**Props**
- `title`: string (required)
- `client`: string (required)
- `industry`: string
- `challenge`: string (required)
- `solution`: string (required)
- `results`: Array<{ metric: string, value: string }>
- `imageUrl`: string
- `testimonial`: { quote: string, author: string, position: string }

**Usage**

```jsx
<CaseStudyDetail
  title="E-Commerce Product Categorization"
  client="Major Retailer"
  industry="Retail"
  challenge="Inconsistent product categorization leading to poor search results and customer experience."
  solution="Implemented a comprehensive data preparation solution with custom annotation and machine learning model training."
  results={caseStudyResults}
  imageUrl="/images/case-studies/retail-detail.jpg"
  testimonial={clientTestimonial}
/>
```

#### CaseStudyResults

Displays the measurable results of a case study.

**Props**
- `results`: Array<{ metric: string, value: string, description: string }>

**Usage**

```jsx
<CaseStudyResults results={caseStudyResults} />
```

#### FilterBar

Provides filtering controls for case study listings.

**Props**
- `industries`: Array<{ value: string, label: string }>
- `services`: Array<{ value: string, label: string }>
- `onFilterChange`: function - callback when filters change
- `activeFilters`: object - currently active filters

**Usage**

```jsx
<FilterBar
  industries={industryOptions}
  services={serviceOptions}
  onFilterChange={handleFilterChange}
  activeFilters={currentFilters}
/>
```

### Impact Components

Impact components are specialized components used for social impact content.

#### ImpactMetrics

Displays key impact metrics with animated counters.

**Props**
- `metrics`: Array<{ value: number, label: string, icon: string }>

**Usage**

```jsx
<ImpactMetrics metrics={socialImpactMetrics} />
```

#### ImpactStory

Displays a specific impact story with image and narrative.

**Props**
- `title`: string (required)
- `location`: string
- `story`: string (required)
- `imageUrl`: string (required)
- `beneficiaries`: string
- `url`: string

**Usage**

```jsx
<ImpactStory
  title="Empowering Rural Communities"
  location="Ramanagara, India"
  story="How our center created 200+ tech jobs in a previously agricultural community."
  imageUrl="/images/impact/ramanagara.jpg"
  beneficiaries="200+ community members"
  url="/impact/empowering-rural-communities"
/>
```

#### ImpactGallery

Displays a gallery of impact images.

**Props**
- `images`: Array<{ src: string, alt: string, caption: string }>

**Usage**

```jsx
<ImpactGallery images={impactGalleryImages} />
```

#### MissionStatement

Displays the company mission statement with supporting content.

**Props**
- `statement`: string (required)
- `supportingText`: string
- `imageUrl`: string

**Usage**

```jsx
<MissionStatement
  statement="Creating sustainable livelihoods through technology while delivering exceptional AI services to global clients."
  supportingText="Our dual mission drives everything we do, from project selection to team development."
  imageUrl="/images/mission.jpg"
/>
```

#### SDGSection

Displays the Sustainable Development Goals alignment.

**Props**
- `goals`: Array<{ number: number, title: string, description: string, imageUrl: string }>

**Usage**

```jsx
<SDGSection goals={sdgAlignment} />
```

## Component Best Practices

### Component Structure

**File Organization**

Each component should be organized in a consistent structure:

```
ComponentName/
  index.ts           // Re-exports the component
  ComponentName.tsx  // Main component file
  ComponentName.test.tsx // Unit tests
  ComponentName.module.scss // Component styles (if using CSS modules)
  types.ts           // TypeScript interfaces/types (optional)
```

**Component Code Structure**

Components should follow this general structure:

```typescript
import React from 'react';
import styles from './ComponentName.module.scss';
import { ComponentNameProps } from './types';

export const ComponentName: React.FC<ComponentNameProps> = ({
  prop1,
  prop2,
  children,
  ...restProps
}) => {
  // Internal logic, state, effects
  
  // Render
  return (
    <div className={styles.container} {...restProps}>
      {/* Component implementation */}
    </div>
  );
};
```

**Props Definition**

Define props using TypeScript interfaces, including documentation:

```typescript
/**
 * Props for the Button component
 */
export interface ButtonProps {
  /** The button's visual style */
  variant?: 'primary' | 'secondary' | 'tertiary';
  
  /** The button's size */
  size?: 'small' | 'medium' | 'large';
  
  /** Disables the button */
  disabled?: boolean;
  
  /** Shows a loading spinner */
  loading?: boolean;
  
  /** Click handler */
  onClick?: (event: React.MouseEvent<HTMLButtonElement>) => void;
  
  /** Button contents */
  children: React.ReactNode;
  
  /** HTML button type */
  type?: 'button' | 'submit' | 'reset';
}
```

### Accessibility

**Keyboard Navigation**

- Ensure all interactive elements are keyboard accessible
- Implement proper focus management for modal dialogs
- Use logical tab order following visual layout

**Screen Readers**

- Use semantic HTML elements (button, nav, header, etc.)
- Provide text alternatives for non-text content
- Use ARIA attributes when necessary (sparingly)
- Test with screen readers (NVDA, VoiceOver)

**Color and Contrast**

- Maintain minimum contrast ratio of 4.5:1 for normal text
- Don't rely on color alone to convey information
- Test with color blindness simulators

**Form Accessibility**

- Associate labels with form controls
- Provide clear error messages
- Group related controls with fieldset and legend
- Mark required fields both visually and with aria-required

**Responsive Design**

- Ensure content is accessible at all breakpoints
- Use appropriate touch target sizes (44x44px minimum)
- Test with different zoom levels

### Performance

**Rendering Optimization**

- Use React.memo() for pure functional components that render often
- Implement shouldComponentUpdate or React.PureComponent for class components
- Avoid anonymous functions in render methods
- Memoize expensive calculations with useMemo()
- Memoize callback functions with useCallback()

**Bundle Size**

- Implement code-splitting for large components
- Use tree-shaking compatible imports (avoid importing entire libraries)
- Monitor bundle size with tools like webpack-bundle-analyzer

**Resource Loading**

- Lazy load below-the-fold images and components
- Use appropriate image formats and sizes
- Implement proper loading states for asynchronous operations

**State Management**

- Keep state as local as possible
- Use context API for shared state that doesn't change often
- Consider using libraries like Zustand for complex state needs

### Testing

**Unit Tests**

Every component should have unit tests covering:

- Rendering with default props
- Rendering with different prop combinations
- User interactions
- Edge cases

Example test structure:

```jsx
import { render, screen, fireEvent } from '@testing-library/react';
import { Button } from './Button';

describe('Button', () => {
  it('renders correctly with default props', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByRole('button')).toHaveTextContent('Click me');
    expect(screen.getByRole('button')).toHaveClass('primary');
  });
  
  it('handles clicks correctly', () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>Click me</Button>);
    fireEvent.click(screen.getByRole('button'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });
  
  it('does not call onClick when disabled', () => {
    const handleClick = jest.fn();
    render(<Button disabled onClick={handleClick}>Click me</Button>);
    fireEvent.click(screen.getByRole('button'));
    expect(handleClick).not.toHaveBeenCalled();
  });
});
```

**Integration Tests**

Test complex components and their interactions:

- Form submission flows
- Multi-step processes
- Component interactions

**Accessibility Testing**

- Use jest-axe for automated accessibility testing
- Test keyboard navigation
- Test with screen readers

**Visual Regression Testing**

Consider using tools like Storybook with Chromatic for visual regression testing.

### Documentation

**Code Comments**

- Add JSDoc comments for component props
- Document complex logic or non-obvious solutions
- Avoid comments that just repeat the code

**Component Documentation**

Each component should have:

- Clear description of its purpose
- Prop documentation (types, defaults, required)
- Usage examples
- Accessibility considerations
- Known limitations or edge cases

## Custom Hooks

### useForm

The useForm hook manages form state, validation, and submission.

**Parameters**
- `initialValues`: object - initial form values
- `validationSchema`: Yup schema - validation rules
- `onSubmit`: function - submission handler

**Returns**
- `values`: object - current form values
- `errors`: object - validation errors
- `touched`: object - fields that have been touched
- `handleChange`: function - field change handler
- `handleBlur`: function - field blur handler
- `handleSubmit`: function - form submission handler
- `isSubmitting`: boolean - submission state
- `resetForm`: function - reset form to initial values

**Usage**

```jsx
const {
  values,
  errors,
  touched,
  handleChange,
  handleBlur,
  handleSubmit,
  isSubmitting
} = useForm({
  initialValues: {
    name: '',
    email: '',
    message: ''
  },
  validationSchema: contactSchema,
  onSubmit: async (values) => {
    await submitContactForm(values);
  }
});

return (
  <form onSubmit={handleSubmit}>
    <FormField
      id="name"
      label="Name"
      error={touched.name && errors.name}
    >
      <Input
        id="name"
        name="name"
        value={values.name}
        onChange={handleChange}
        onBlur={handleBlur}
      />
    </FormField>
    {/* Other fields */}
    <Button type="submit" loading={isSubmitting}>Submit</Button>
  </form>
);
```

### useFileUpload

The useFileUpload hook handles file selection, validation, and uploading.

**Parameters**
- `options`: object
  - `acceptedFileTypes`: Array<string> - allowed file types
  - `maxFileSize`: number - maximum file size in bytes
  - `maxFiles`: number - maximum number of files
  - `onUploadComplete`: function - callback after successful upload

**Returns**
- `files`: Array<File> - selected files
- `fileErrors`: Array<string> - validation errors
- `isUploading`: boolean - upload state
- `progress`: number - upload progress percentage
- `handleSelectFiles`: function - file selection handler
- `handleDrop`: function - drag and drop handler
- `handleUpload`: function - initiate upload
- `resetFiles`: function - clear selected files

**Usage**

```jsx
const {
  files,
  fileErrors,
  isUploading,
  progress,
  handleSelectFiles,
  handleDrop,
  handleUpload,
  resetFiles
} = useFileUpload({
  acceptedFileTypes: ['.csv', '.json', '.xml'],
  maxFileSize: 52428800, // 50MB
  maxFiles: 1,
  onUploadComplete: (uploadedFiles) => {
    console.log('Upload complete', uploadedFiles);
  }
});

return (
  <div>
    <FileDropzone
      onFilesSelected={handleSelectFiles}
      onDrop={handleDrop}
      accept=".csv,.json,.xml"
      error={fileErrors[0]}
    />
    
    {files.length > 0 && (
      <div>
        <p>Selected file: {files[0].name}</p>
        {isUploading ? (
          <ProgressBar value={progress} />
        ) : (
          <Button onClick={handleUpload}>Upload</Button>
        )}
      </div>
    )}
  </div>
);
```

### useBreakpoint

The useBreakpoint hook detects responsive breakpoints for adaptive rendering.

**Returns**
- `breakpoint`: string - current breakpoint (xs, sm, md, lg, xl)
- `isMobile`: boolean - true if xs or sm
- `isTablet`: boolean - true if md
- `isDesktop`: boolean - true if lg or xl

**Usage**

```jsx
const { breakpoint, isMobile, isTablet, isDesktop } = useBreakpoint();

return (
  <div>
    {isMobile && <MobileLayout />}
    {isTablet && <TabletLayout />}
    {isDesktop && <DesktopLayout />}
    
    {/* Or use breakpoint directly */}
    {breakpoint === 'xs' && <ExtraSmallLayout />}
    {breakpoint === 'sm' && <SmallLayout />}
    {breakpoint === 'md' && <MediumLayout />}
    {breakpoint === 'lg' && <LargeLayout />}
    {breakpoint === 'xl' && <ExtraLargeLayout />}
  </div>
);
```

### useAnalytics

The useAnalytics hook provides tracking functions for user interactions.

**Returns**
- `trackPageView`: function - track page view
- `trackEvent`: function - track user event
- `trackConversion`: function - track conversion event
- `trackDownload`: function - track file download
- `trackFormSubmission`: function - track form submission

**Usage**

```jsx
const { trackEvent, trackConversion, trackFormSubmission } = useAnalytics();

// Track button click
const handleClick = () => {
  trackEvent('button_click', { button_name: 'request_demo' });
  // Handle the click
};

// Track form submission
const handleSubmit = (values) => {
  trackFormSubmission('contact_form', { form_type: 'contact' });
  // Submit the form
};

// Track conversion
const handleDemoRequest = () => {
  trackConversion('demo_request', { service: 'data_preparation' });
  // Process the demo request
};
```

### useUploadStatus

The useUploadStatus hook monitors file upload progress and status.

**Parameters**
- `uploadId`: string - unique identifier for the upload

**Returns**
- `status`: string - current status (idle, processing, success, error)
- `progress`: number - processing progress percentage
- `result`: object - processing result
- `error`: string - error message if failed
- `checkStatus`: function - manually check status

**Usage**

```jsx
const {
  status,
  progress,
  result,
  error
} = useUploadStatus(uploadId);

return (
  <div>
    {status === 'idle' && <p>Waiting to start processing...</p>}
    
    {status === 'processing' && (
      <div>
        <p>Processing your upload...</p>
        <ProgressBar value={progress} />
      </div>
    )}
    
    {status === 'success' && (
      <div>
        <p>Processing complete!</p>
        <pre>{JSON.stringify(result, null, 2)}</pre>
      </div>
    )}
    
    {status === 'error' && (
      <div>
        <p>Error processing your upload:</p>
        <Alert variant="error" message={error} />
      </div>
    )}
  </div>
);
```

### Other Custom Hooks

#### useClickOutside

Detects clicks outside of a specified element.

```jsx
const ref = useRef();
useClickOutside(ref, () => {
  // Handle click outside
});

return <div ref={ref}>Click outside me</div>;
```

#### useIntersectionObserver

Detects when an element enters or exits the viewport.

```jsx
const ref = useRef();
const isVisible = useIntersectionObserver(ref, { threshold: 0.1 });

return (
  <div ref={ref}>
    {isVisible ? 'I am visible' : 'I am not visible'}
  </div>
);
```

#### useKeyPress

Detects when a specific key is pressed.

```jsx
const isEscapePressed = useKeyPress('Escape');

useEffect(() => {
  if (isEscapePressed) {
    // Handle Escape key press
  }
}, [isEscapePressed]);
```

#### useLocalStorage

Provides persistent state using localStorage.

```jsx
const [theme, setTheme] = useLocalStorage('theme', 'light');

// Usage
const toggleTheme = () => setTheme(theme === 'light' ? 'dark' : 'light');
```

## Component Theming

### Color System

The color system is based on design tokens that provide a consistent palette across the application.

**Primary Colors**
- Primary Blue: `#0055A4` (primary.500)
  - Lighter variations: primary.100, primary.200, primary.300, primary.400
  - Darker variations: primary.600, primary.700, primary.800, primary.900
- Secondary Orange: `#FF671F` (secondary.500)
  - Lighter/darker variations follow the same pattern

**Neutral Colors**
- Dark Gray: `#212529` (neutral.900)
- Medium Gray: `#6C757D` (neutral.500)
- Light Gray: `#E9ECEF` (neutral.200)
- Off-White: `#F8F9FA` (neutral.100)

**Functional Colors**
- Success: `#28A745` (success.500)
- Warning: `#FFC107` (warning.500)
- Error: `#DC3545` (error.500)
- Info: `#17A2B8` (info.500)

**Usage**

```jsx
// In component styles
import { tokens } from '@/styles/tokens';

const styles = {
  container: {
    backgroundColor: tokens.colors.primary[500],
    color: tokens.colors.neutral[100],
  }
};

// With TailwindCSS utility classes
<div className="bg-primary-500 text-neutral-100">Content</div>
```

### Typography

The typography system defines font families, sizes, weights, and line heights.

**Font Families**
- Primary (Headings): Montserrat
- Secondary (Body): Open Sans

**Font Sizes**
- xs: 0.75rem (12px)
- sm: 0.875rem (14px)
- base: 1rem (16px)
- lg: 1.125rem (18px)
- xl: 1.25rem (20px)
- 2xl: 1.5rem (24px)
- 3xl: 1.875rem (30px)
- 4xl: 2.25rem (36px)
- 5xl: 3rem (48px)

**Font Weights**
- light: 300
- regular: 400
- medium: 500
- semibold: 600
- bold: 700

**Line Heights**
- tight: 1.2
- normal: 1.5
- relaxed: 1.75

**Usage**

```jsx
// In component styles
import { tokens } from '@/styles/tokens';

const styles = {
  heading: {
    fontFamily: tokens.typography.fontFamily.primary,
    fontSize: tokens.typography.fontSize['3xl'],
    fontWeight: tokens.typography.fontWeight.bold,
    lineHeight: tokens.typography.lineHeight.tight,
  }
};

// With TailwindCSS utility classes
<h1 className="font-primary text-3xl font-bold leading-tight">Heading</h1>
```

### Spacing

The spacing system provides consistent measurements for margins, padding, and layout.

**Base Unit**: 0.25rem (4px)

**Spacing Scale**
- 0: 0
- 1: 0.25rem (4px)
- 2: 0.5rem (8px)
- 3: 0.75rem (12px)
- 4: 1rem (16px)
- 5: 1.25rem (20px)
- 6: 1.5rem (24px)
- 8: 2rem (32px)
- 10: 2.5rem (40px)
- 12: 3rem (48px)
- 16: 4rem (64px)
- 20: 5rem (80px)
- 24: 6rem (96px)

**Usage**

```jsx
// In component styles
import { tokens } from '@/styles/tokens';

const styles = {
  container: {
    padding: tokens.spacing[4],
    marginBottom: tokens.spacing[8],
    gap: tokens.spacing[2],
  }
};

// With TailwindCSS utility classes
<div className="p-4 mb-8 gap-2">Content</div>
```

### Breakpoints

The responsive breakpoint system defines screen size thresholds.

**Breakpoint Values**
- xs: < 375px (Mobile Small)
- sm: 376px - 767px (Mobile)
- md: 768px - 1023px (Tablet)
- lg: 1024px - 1439px (Desktop)
- xl: ≥ 1440px (Large Desktop)

**Usage**

```jsx
// In media queries
import { tokens } from '@/styles/tokens';

const styles = {
  container: {
    width: '100%',
    [`@media (min-width: ${tokens.breakpoints.md})`]: {
      width: '50%',
    },
    [`@media (min-width: ${tokens.breakpoints.lg})`]: {
      width: '33.33%',
    },
  }
};

// With TailwindCSS utility classes
<div className="w-full md:w-1/2 lg:w-1/3">Content</div>

// With useBreakpoint hook
const { isMobile, isTablet, isDesktop } = useBreakpoint();

return (
  <div>
    {isMobile && <MobileLayout />}
    {isTablet && <TabletLayout />}
    {isDesktop && <DesktopLayout />}
  </div>
);
```

### Customization

Components can be customized while maintaining design consistency through various approaches:

**Props**
- Most components accept variant, size, and color props
- Use these props as the primary customization method

**CSS Modules**
- Use CSS modules for component-specific styling
- Follow naming conventions: `ComponentName.module.scss`

**Global Theme**
- The global theme can be customized by updating design tokens
- This affects all components using the theme tokens

**TailwindCSS**
- For minor customizations, TailwindCSS utility classes can be used
- Custom classes should be added via the className prop

**Best Practices**
- Prefer using the built-in customization props when available
- Add custom styling via className only when necessary
- Maintain consistent visual design by using theme tokens
- Consider creating a new component variant for significant customizations

```jsx
// Good - using built-in props
<Button variant="primary" size="large">Submit</Button>

// Good - minor customization with className
<Button variant="primary" className="mt-4">Submit</Button>

// Avoid - excessive custom styling
<Button 
  variant="primary" 
  className="bg-purple-500 hover:bg-purple-600 text-xl py-6 px-8 rounded-full shadow-lg"
>
  Submit
</Button>

// Better - create a new component for significant customizations
<PurpleButton size="large">Submit</PurpleButton>
```