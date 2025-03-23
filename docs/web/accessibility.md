# Accessibility Guidelines

This document outlines the accessibility implementation guidelines, standards, and testing procedures for the IndiVillage website. Our goal is to create an inclusive experience that meets WCAG 2.1 AA compliance standards while providing a seamless experience for all users, including those with disabilities.

## Accessibility Standards

The IndiVillage website adheres to the Web Content Accessibility Guidelines (WCAG) 2.1 Level AA standards. These guidelines are organized around four principles: Perceivable, Operable, Understandable, and Robust (POUR).

### Perceivable

Information and user interface components must be presentable to users in ways they can perceive.

- Provide text alternatives for non-text content
- Provide captions and transcripts for multimedia
- Create content that can be presented in different ways without losing information
- Make it easier for users to see and hear content by separating foreground from background
- Maintain minimum contrast ratio of 4.5:1 for normal text and 3:1 for large text
- Ensure text can be resized up to 200% without loss of content or functionality
- Use text rather than images of text except for logos and essential graphics

### Operable

User interface components and navigation must be operable by all users.

- Make all functionality available from a keyboard
- Provide users enough time to read and use content
- Do not design content in a way that is known to cause seizures or physical reactions
- Provide ways to help users navigate, find content, and determine where they are
- Make it easier to use inputs other than keyboard
- Implement proper focus management for interactive elements
- Ensure all interactive elements have appropriate focus indicators
- Provide skip links to bypass repetitive navigation

### Understandable

Information and the operation of the user interface must be understandable.

- Make text content readable and understandable
- Make web pages appear and operate in predictable ways
- Help users avoid and correct mistakes
- Use clear and consistent navigation patterns
- Provide clear form labels and instructions
- Provide clear error identification and suggestions
- Implement error prevention for important actions
- Use consistent and meaningful link text

### Robust

Content must be robust enough to be interpreted reliably by a wide variety of user agents, including assistive technologies.

- Maximize compatibility with current and future user tools
- Use valid, well-formed HTML
- Provide name, role, and value information for all UI components
- Ensure status messages can be programmatically determined
- Use ARIA attributes appropriately and only when necessary
- Test with assistive technologies to ensure compatibility

## Implementation Guidelines

The following guidelines provide specific implementation details for ensuring accessibility across the IndiVillage website.

### Semantic HTML

Use semantic HTML elements to provide meaning and structure to content. This helps assistive technologies understand the page structure and improves the user experience.

```html
<!-- Good example - Using semantic HTML -->
<header>
  <nav>
    <ul>
      <li><a href="/">Home</a></li>
      <li><a href="/services">Services</a></li>
    </ul>
  </nav>
</header>
<main>
  <section>
    <h1>Welcome to IndiVillage</h1>
    <p>We provide AI-as-a-service solutions with social impact.</p>
  </section>
</main>
<footer>
  <p>&copy; 2023 IndiVillage</p>
</footer>

<!-- Bad example - Using non-semantic HTML -->
<div class="header">
  <div class="nav">
    <div class="menu">
      <div><a href="/">Home</a></div>
      <div><a href="/services">Services</a></div>
    </div>
  </div>
</div>
<div class="main">
  <div class="section">
    <div class="title">Welcome to IndiVillage</div>
    <div class="text">We provide AI-as-a-service solutions with social impact.</div>
  </div>
</div>
<div class="footer">
  <div>&copy; 2023 IndiVillage</div>
</div>
```

### Keyboard Navigation

Ensure all interactive elements are keyboard accessible and implement proper focus management. This allows users who cannot use a mouse to navigate and interact with the website.

```javascript
// Using the trapFocus utility for modal dialogs
import { trapFocus } from '../utils/accessibility';
import { useRef, useEffect } from 'react';

const Modal = ({ isOpen, onClose, children }) => {
  const modalRef = useRef(null);
  
  useEffect(() => {
    if (isOpen && modalRef.current) {
      // Trap focus within the modal when it opens
      const cleanup = trapFocus(modalRef.current);
      
      // Handle Escape key to close the modal
      const handleEscape = (e) => {
        if (e.key === 'Escape') onClose();
      };
      
      document.addEventListener('keydown', handleEscape);
      
      // Clean up event listeners when the modal closes
      return () => {
        cleanup();
        document.removeEventListener('keydown', handleEscape);
      };
    }
  }, [isOpen, onClose]);
  
  if (!isOpen) return null;
  
  return (
    <div className="modal-overlay" role="dialog" aria-modal="true">
      <div 
        ref={modalRef} 
        className="modal-content"
        aria-labelledby="modal-title"
      >
        <h2 id="modal-title">Modal Title</h2>
        {children}
        <button 
          onClick={onClose}
          className="modal-close"
          aria-label="Close modal"
        >
          ×
        </button>
      </div>
    </div>
  );
};
```

### Focus Management

Implement proper focus management for interactive elements, especially for dynamic content and modal dialogs. This ensures users can navigate the website efficiently using a keyboard.

- Use the manageFocus utility for components that need to manage focus
- Ensure focus is trapped within modal dialogs
- Return focus to the triggering element when a dialog is closed
- Maintain a logical tab order that follows the visual layout
- Ensure all interactive elements have visible focus indicators
- Avoid focus traps outside of modal dialogs
- Implement skip links to bypass repetitive navigation

```javascript
// Example of focus management in a component
import { manageFocus } from '../utils/accessibility';
import { useRef, useEffect } from 'react';

const TabPanel = ({ isActive, children }) => {
  const panelRef = useRef(null);
  
  useEffect(() => {
    if (isActive && panelRef.current) {
      // Move focus to the panel when it becomes active
      const cleanup = manageFocus(panelRef.current, null, true);
      return cleanup;
    }
  }, [isActive]);
  
  return (
    <div 
      ref={panelRef} 
      role="tabpanel" 
      tabIndex={isActive ? 0 : -1}
      aria-hidden={!isActive}
      className={`tab-panel ${isActive ? 'active' : 'hidden'}`}
    >
      {children}
    </div>
  );
};
```

### ARIA Attributes

Use ARIA (Accessible Rich Internet Applications) attributes appropriately to enhance accessibility when HTML semantics are not sufficient. ARIA attributes help assistive technologies understand the purpose and state of UI components.

- Use ARIA attributes only when necessary
- Prefer semantic HTML over ARIA when possible
- Ensure ARIA attributes are used correctly
- Test ARIA implementations with screen readers
- Use the setAriaAttributes utility for consistent ARIA attribute management
- Implement appropriate ARIA landmarks (role="banner", role="main", etc.)
- Use aria-expanded, aria-selected, and aria-pressed for interactive elements
- Use aria-live regions for dynamic content updates

```javascript
// Example of proper ARIA usage
import { setAriaAttributes } from '../utils/accessibility';

const Accordion = ({ title, isExpanded, onToggle, children }) => {
  const headingId = `accordion-${title.toLowerCase().replace(/\s+/g, '-')}`;
  const contentId = `${headingId}-content`;
  
  return (
    <div className="accordion">
      <h3>
        <button 
          id={headingId}
          className="accordion-header"
          onClick={onToggle}
          aria-expanded={isExpanded}
          aria-controls={contentId}
        >
          {title}
          <span className="icon" aria-hidden="true">
            {isExpanded ? '▲' : '▼'}
          </span>
        </button>
      </h3>
      <div 
        id={contentId}
        role="region"
        aria-labelledby={headingId}
        className={`accordion-content ${isExpanded ? 'expanded' : 'collapsed'}`}
        hidden={!isExpanded}
      >
        {children}
      </div>
    </div>
  );
```

### Forms and Validation

Implement accessible forms with clear labels, instructions, and error messages. This ensures users can understand and complete forms successfully.

- Use explicit labels for form controls with the for/id association
- Group related form controls with fieldset and legend
- Provide clear instructions for form completion
- Implement client-side validation with clear error messages
- Associate error messages with form controls using aria-describedby
- Use aria-invalid for invalid form controls
- Ensure form controls have accessible names
- Maintain a logical tab order for form controls

```javascript
// Example of an accessible form field with validation
import { useState } from 'react';

const FormField = ({ id, label, type, required, validationRules, onChange }) => {
  const [value, setValue] = useState('');
  const [error, setError] = useState('');
  const [touched, setTouched] = useState(false);
  
  const handleChange = (e) => {
    const newValue = e.target.value;
    setValue(newValue);
    onChange(newValue);
    
    if (touched) {
      validateField(newValue);
    }
  };
  
  const handleBlur = () => {
    setTouched(true);
    validateField(value);
  };
  
  const validateField = (fieldValue) => {
    if (required && !fieldValue) {
      setError(`${label} is required`);
      return;
    }
    
    // Additional validation based on rules
    if (validationRules?.email && !/^\S+@\S+\.\S+$/.test(fieldValue)) {
      setError('Please enter a valid email address');
      return;
    }
    
    setError('');
  };
  
  const errorId = error ? `${id}-error` : undefined;
  
  return (
    <div className="form-field">
      <label htmlFor={id} className="form-label">
        {label}{required && <span aria-hidden="true"> *</span>}
        {required && <span className="sr-only"> (required)</span>}
      </label>
      <input
        id={id}
        type={type}
        value={value}
        onChange={handleChange}
        onBlur={handleBlur}
        aria-required={required}
        aria-invalid={!!error}
        aria-describedby={errorId}
        className={`form-input ${error ? 'input-error' : ''}`}
      />
      {error && (
        <div id={errorId} className="error-message" role="alert">
          {error}
        </div>
      )}
    </div>
  );
```

### Images and Media

Provide appropriate text alternatives for images and ensure multimedia content is accessible. This allows users who cannot see images or hear audio to understand the content.

- Provide alt text for all images that convey information
- Use empty alt attributes for decorative images
- Provide captions and transcripts for video content
- Ensure audio content has text transcripts
- Avoid content that flashes more than three times per second
- Provide audio descriptions for video content when necessary
- Ensure media controls are keyboard accessible
- Use the ImageWithFallback component for consistent image handling

```javascript
// Example of accessible image implementation
import { ImageWithFallback } from '../components/shared/ImageWithFallback';

const ServiceCard = ({ service }) => {
  return (
    <div className="service-card">
      <ImageWithFallback
        src={service.imageUrl}
        alt={service.imageAlt || `Illustration of ${service.title} service`}
        width={300}
        height={200}
        // Decorative images should have empty alt text
        // alt="" 
      />
      <h3>{service.title}</h3>
      <p>{service.description}</p>
    </div>
  );
```

### Color and Contrast

Ensure sufficient color contrast and avoid using color alone to convey information. This makes content perceivable for users with low vision or color blindness.

- Maintain minimum contrast ratio of 4.5:1 for normal text
- Maintain minimum contrast ratio of 3:1 for large text (18pt or 14pt bold)
- Ensure UI components have sufficient contrast against adjacent colors
- Do not rely on color alone to convey information
- Provide additional indicators (icons, patterns, text) alongside color
- Test color contrast using automated tools
- Consider high contrast mode users
- Use the design system color tokens for consistent contrast

### Dynamic Content

Make dynamic content accessible to all users, including those using assistive technologies. This ensures users are aware of content changes and can interact with dynamic elements.

- Use aria-live regions for important content updates
- Set appropriate aria-live politeness levels (polite, assertive)
- Announce important status changes to screen readers
- Ensure custom interactive components have proper ARIA roles and states
- Manage focus appropriately when content changes
- Provide sufficient time for users to read content before it changes
- Allow users to pause, stop, or hide moving content
- Use the announceToScreenReader utility for important announcements

```javascript
// Example of accessible dynamic content
import { announceToScreenReader } from '../utils/accessibility';
import { useState, useEffect } from 'react';

const FileUploadStatus = ({ status, progress }) => {
  const [prevStatus, setPrevStatus] = useState(status);
  
  useEffect(() => {
    if (status !== prevStatus) {
      // Announce status changes to screen readers
      if (status === 'uploading') {
        announceToScreenReader('File upload started', 'polite');
      } else if (status === 'processing') {
        announceToScreenReader('File upload complete, now processing', 'polite');
      } else if (status === 'complete') {
        announceToScreenReader('File processing complete', 'polite');
      } else if (status === 'error') {
        announceToScreenReader('Error uploading file', 'assertive');
      }
      
      setPrevStatus(status);
    }
  }, [status, prevStatus]);
  
  return (
    <div className="upload-status" aria-live="polite">
      <p>Status: {status}</p>
      {status === 'uploading' && (
        <div>
          <div 
            className="progress-bar" 
            role="progressbar" 
            aria-valuenow={progress} 
            aria-valuemin="0" 
            aria-valuemax="100"
          >
            <div 
              className="progress-bar-fill" 
              style={{ width: `${progress}%` }}
            />
          </div>
          <p>{progress}% complete</p>
        </div>
      )}
    </div>
  );
```

### Responsive Design and Zoom

Ensure the website is usable at different viewport sizes and zoom levels. This accommodates users who need to enlarge content to read it.

- Design for mobile-first with responsive breakpoints
- Ensure content is readable and functional at 320px width
- Support zooming up to 400% without loss of content or functionality
- Use relative units (rem, em) for text and spacing
- Ensure touch targets are at least 44x44 pixels
- Maintain appropriate spacing between interactive elements
- Test at different viewport sizes and zoom levels
- Avoid horizontal scrolling at standard zoom levels

### Motion and Animation

Respect user preferences for reduced motion and ensure animations do not cause discomfort. This accommodates users who are sensitive to motion or animations.

- Respect prefers-reduced-motion media query
- Provide alternative animations or transitions for users who prefer reduced motion
- Avoid content that flashes more than three times per second
- Allow users to pause, stop, or hide animations
- Keep animations subtle and purposeful
- Use the isReducedMotionPreferred utility to detect user preferences
- Test with reduced motion settings enabled
- Implement appropriate fallbacks for users with motion sensitivity

```javascript
// Example of respecting reduced motion preferences
import { isReducedMotionPreferred } from '../utils/accessibility';
import { motion } from 'framer-motion';

const AnimatedComponent = ({ children }) => {
  const prefersReducedMotion = isReducedMotionPreferred();
  
  const animationProps = prefersReducedMotion
    ? { // Subtle or no animation for reduced motion
        initial: { opacity: 0 },
        animate: { opacity: 1 },
        transition: { duration: 0.3 }
      }
    : { // Full animation for others
        initial: { opacity: 0, y: 20 },
        animate: { opacity: 1, y: 0 },
        transition: { duration: 0.5, ease: 'easeOut' }
      };
  
  return (
    <motion.div {...animationProps}>
      {children}
    </motion.div>
  );
```

## Component-Specific Guidelines

The following guidelines provide accessibility implementation details for specific components used in the IndiVillage website. For more detailed component documentation, see [components.md](./components.md).

### Navigation Components

Ensure navigation components are accessible to all users, including those using assistive technologies.

- Use semantic HTML elements (nav, ul, li) for navigation
- Implement proper ARIA landmarks (role="navigation")
- Ensure keyboard accessibility for all navigation items
- Provide skip links to bypass navigation
- Implement proper focus management for dropdown menus
- Use aria-current for the current page
- Ensure mobile navigation is accessible
- Test navigation with screen readers and keyboard

### Form Components

Implement accessible form components that are easy to use for all users.

- Use explicit labels for all form controls
- Group related form controls with fieldset and legend
- Provide clear instructions and error messages
- Ensure form controls have sufficient size and spacing
- Implement proper validation with clear error messages
- Use appropriate input types for different data
- Ensure form submission provides appropriate feedback
- Test forms with screen readers and keyboard

### Modal Dialogs

Implement accessible modal dialogs that work for all users, including those using assistive technologies.

- Use appropriate ARIA attributes (role="dialog", aria-modal="true")
- Trap focus within the modal when open
- Return focus to the triggering element when closed
- Allow closing the modal with the Escape key
- Ensure modal content is accessible
- Provide a visible close button
- Announce modal opening to screen readers
- Test modals with screen readers and keyboard

### Tabs and Accordions

Implement accessible tabs and accordions that work for all users.

- Use appropriate ARIA attributes for tabs (role="tablist", role="tab", role="tabpanel")
- Use appropriate ARIA attributes for accordions (aria-expanded, aria-controls)
- Implement keyboard navigation for tabs (arrow keys, Home, End)
- Ensure accordion headers are keyboard accessible
- Manage focus appropriately when tabs or accordions change
- Provide visual indicators for selected tabs or expanded accordions
- Ensure content is accessible within tabs and accordions
- Test with screen readers and keyboard

### File Upload Components

Implement accessible file upload components that work for all users.

- Provide clear instructions for file upload
- Ensure file input is keyboard accessible
- Provide feedback on file selection and upload progress
- Announce upload status changes to screen readers
- Implement proper error handling and messaging
- Ensure drag-and-drop functionality has keyboard alternatives
- Provide clear information about file requirements
- Test file upload with screen readers and keyboard

### Interactive Charts and Visualizations

Ensure data visualizations are accessible to all users, including those using assistive technologies.

- Provide text alternatives for charts and graphs
- Ensure interactive elements are keyboard accessible
- Use appropriate ARIA attributes for custom controls
- Do not rely on color alone to convey information
- Provide data tables as alternatives when appropriate
- Ensure sufficient color contrast for chart elements
- Implement proper focus management for interactive charts
- Test visualizations with screen readers and keyboard

## Accessibility Testing

Regular accessibility testing is essential to ensure the website meets WCAG 2.1 AA standards and provides an inclusive experience for all users.

### Automated Testing

Implement automated accessibility testing as part of the development and CI/CD process.

- Use axe-core for automated accessibility testing
- Integrate accessibility testing into the CI/CD pipeline
- Run accessibility tests on all pull requests
- Use ESLint with jsx-a11y plugin for static code analysis
- Implement automated tests for keyboard navigation
- Test color contrast automatically
- Generate accessibility reports for review
- Address all critical and serious issues before deployment

```javascript
// Example of automated accessibility testing with axe-core
import React from 'react';
import { render } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';
import { Button } from '../components/ui/Button';

expect.extend(toHaveNoViolations);

describe('Button component accessibility', () => {
  it('should not have accessibility violations', async () => {
    const { container } = render(
      <Button onClick={() => {}} variant="primary">
        Click Me
      </Button>
    );
    
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
  
  it('should have appropriate ARIA attributes when disabled', async () => {
    const { container } = render(
      <Button onClick={() => {}} variant="primary" disabled>
        Disabled Button
      </Button>
    );
    
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});
```

### Manual Testing

Perform manual accessibility testing to catch issues that automated testing might miss.

- Test keyboard navigation throughout the website
- Test with screen readers (NVDA, VoiceOver, JAWS)
- Test with browser zoom up to 400%
- Test with high contrast mode
- Test with reduced motion settings
- Test form validation and error handling
- Test interactive components (modals, tabs, accordions)
- Test responsive design at different viewport sizes

### Testing Checklist

Use the following checklist for comprehensive accessibility testing:

- Keyboard navigation: Can all interactive elements be accessed and operated using only the keyboard?
- Screen reader compatibility: Is all content and functionality accessible with screen readers?
- Focus management: Is focus visible and does it follow a logical order?
- ARIA attributes: Are ARIA attributes used correctly and appropriately?
- Color contrast: Does all text and UI components have sufficient contrast?
- Text alternatives: Do all images have appropriate alt text?
- Form accessibility: Are all forms properly labeled and do they provide clear error messages?
- Dynamic content: Are content changes announced to screen readers?
- Responsive design: Is the website usable at different viewport sizes and zoom levels?
- Motion sensitivity: Are animations respectful of user preferences for reduced motion?

### Testing Tools

Use the following tools for accessibility testing:

- axe DevTools: Browser extension for accessibility testing
- WAVE: Web Accessibility Evaluation Tool
- Lighthouse: Automated accessibility auditing
- Color Contrast Analyzer: Tool for checking color contrast
- Screen readers: NVDA (Windows), VoiceOver (macOS), JAWS (Windows)
- Keyboard: Test navigation using Tab, Shift+Tab, Enter, Space, and arrow keys
- jest-axe: Accessibility testing in Jest
- ESLint with jsx-a11y: Static code analysis for accessibility issues

### Testing Process

Follow this process for comprehensive accessibility testing:

- Automated testing during development
- Code review with accessibility focus
- Automated testing in CI/CD pipeline
- Manual testing before release
- Regular accessibility audits
- User testing with people with disabilities when possible
- Address all critical and serious issues before deployment
- Document and prioritize remaining issues for future fixes

### Integration with Development Workflow

Integrate accessibility testing into the development workflow:

- Include accessibility tests in your unit and integration test suites
- Run accessibility checks as part of the CI/CD pipeline
- Block PRs with critical accessibility issues
- Include accessibility testing in code review checklist
- Track accessibility issues in your project management system
- Establish accessibility requirements during the planning phase
- Provide accessibility training for developers
- Assign accessibility champions for each team

```javascript
// GitHub Actions workflow excerpt for accessibility testing
name: Accessibility Tests

on:
  pull_request:
    branches: [ main, develop ]
  push:
    branches: [ main, develop ]

jobs:
  accessibility:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'yarn'
      
      - name: Install dependencies
        run: yarn install --frozen-lockfile
      
      - name: Build project
        run: yarn build
      
      - name: Start server
        run: yarn start & npx wait-on http://localhost:3000
      
      - name: Run accessibility tests
        run: yarn test:a11y
      
      - name: Run lighthouse
        run: npx lighthouse http://localhost:3000 --output json --output html --output-path ./lighthouse-report.html --chrome-flags="--headless" --only-categories=accessibility
      
      - name: Upload lighthouse report
        uses: actions/upload-artifact@v3
        with:
          name: lighthouse-accessibility-report
          path: ./lighthouse-report.html
```

## Accessibility Resources

The following resources provide additional information and guidance for implementing accessibility features.

### Internal Resources

Reference these internal resources for accessibility implementation:

- Accessibility utilities in src/web/src/utils/accessibility.ts
- Component documentation in [components.md](./components.md)
- Design system documentation for color contrast and typography

### External Resources

The following external resources provide valuable guidance for accessibility implementation:

- [WCAG 2.1 Guidelines](https://www.w3.org/TR/WCAG21/)
- [MDN Web Accessibility Guide](https://developer.mozilla.org/en-US/docs/Web/Accessibility)
- [WebAIM Articles and Resources](https://webaim.org/articles/)
- [A11y Project Checklist](https://www.a11yproject.com/checklist/)
- [Inclusive Components](https://inclusive-components.design/)
- [axe-core Documentation](https://github.com/dequelabs/axe-core)
- [React Accessibility](https://reactjs.org/docs/accessibility.html)
- [Next.js Accessibility](https://nextjs.org/docs/advanced-features/accessibility)

## Continuous Improvement

Accessibility is an ongoing process that requires continuous attention and improvement. The following practices help maintain and improve accessibility over time:

- Regular accessibility audits
- Incorporate accessibility testing into the development workflow
- Address accessibility issues as they are identified
- Stay updated on accessibility best practices and standards
- Provide accessibility training for the development team
- Document accessibility features and known issues
- Collect feedback from users with disabilities when possible
- Prioritize accessibility improvements in the product roadmap