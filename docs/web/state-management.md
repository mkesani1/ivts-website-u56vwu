# State Management in IndiVillage Website

This document outlines the state management approach used in the IndiVillage website frontend. The application uses a combination of React Context API for global state, custom hooks for reusable state logic, and component-level state for UI-specific concerns.

## React Context Providers

The application uses several context providers to share state across components without prop drilling. These providers are defined in the `src/web/src/context` directory.

### AnalyticsContext

Provides analytics tracking functionality throughout the application. This context enables components to track user interactions, page views, form submissions, and business events without directly coupling to the analytics implementation.

```jsx
// Using analytics in a component
import { useAnalyticsContext } from '../context/AnalyticsContext';

const MyComponent = () => {
  const { trackEvent } = useAnalyticsContext();
  
  const handleClick = () => {
    trackEvent('button_click', 'cta_button', { location: 'homepage' });
    // Perform action
  };
  
  return <button onClick={handleClick}>Click Me</button>;
};
```

### ToastContext

Manages toast notifications across the application. This context allows any component to display success, error, warning, or info messages without managing the toast UI state directly.

```jsx
// Displaying a toast notification
import { useToastContext } from '../context/ToastContext';

const MyForm = () => {
  const { showSuccess, showError } = useToastContext();
  
  const handleSubmit = async (data) => {
    try {
      await submitData(data);
      showSuccess('Success', 'Your form has been submitted successfully');
    } catch (error) {
      showError('Error', 'Failed to submit form. Please try again.');
    }
  };
  
  return <form onSubmit={handleSubmit}>...</form>;
};
```

### UploadContext

Centralizes file upload state and functionality. This context provides a consistent interface for file upload features throughout the application, managing upload state, configuration, and operations.

```jsx
// Using upload context in a component
import { useUploadContext } from '../context/UploadContext';

const UploadComponent = () => {
  const { uploadState, handleFileSelect, startUpload, cancelUpload } = useUploadContext();
  
  return (
    <div>
      <input type="file" onChange={handleFileSelect} />
      {uploadState.file && (
        <button onClick={() => startUpload(formData)}>Upload</button>
      )}
      {uploadState.isUploading && (
        <>
          <ProgressBar progress={uploadState.progress} />
          <button onClick={cancelUpload}>Cancel</button>
        </>
      )}
    </div>
  );
};
```

## Custom Hooks

The application uses custom hooks to encapsulate and reuse stateful logic. These hooks are defined in the `src/web/src/hooks` directory.

### useForm

Provides comprehensive form state management, validation, and submission handling. This hook manages form values, field-level validation, form submission, and error handling to create a consistent form experience.

```jsx
// Using useForm hook
import { useForm } from '../hooks/useForm';

const ContactForm = () => {
  const initialValues = { name: '', email: '', message: '' };
  const validationRules = {
    name: { required: true },
    email: { required: true, email: true },
    message: { required: true, minLength: 10 }
  };
  
  const { formState, handleChange, handleBlur, handleSubmit } = useForm({
    initialValues,
    validationRules,
    validateOnBlur: true
  });
  
  const onSubmit = async (values) => {
    // Submit form data
  };
  
  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      {/* Form fields */}
    </form>
  );
};
```

### useFileUpload

Manages the file upload process including file selection, validation, upload state tracking, progress monitoring, and error handling. This hook serves as the core functionality for the sample data upload feature.

```jsx
// Using useFileUpload hook directly
import { useFileUpload } from '../hooks/useFileUpload';

const FileUploader = () => {
  const config = {
    maxFileSize: 50 * 1024 * 1024, // 50MB
    allowedFileTypes: ['csv', 'json', 'xml']
  };
  
  const {
    uploadState,
    validateFile,
    handleFileSelect,
    startUpload,
    cancelUpload,
    resetUpload
  } = useFileUpload(config);
  
  return (
    <div>
      {/* File upload UI */}
    </div>
  );
};
```

### useUploadStatus

Provides real-time tracking of file upload status and processing progress. This hook periodically polls the backend API to get the current status of an uploaded file.

```jsx
// Using useUploadStatus hook
import { useUploadStatus } from '../hooks/useUploadStatus';

const UploadStatus = ({ uploadId }) => {
  const initialState = { status: 'pending', progress: 0 };
  const { uploadState, isPolling } = useUploadStatus(uploadId, initialState);
  
  return (
    <div>
      <p>Status: {uploadState.status}</p>
      <p>Progress: {uploadState.progress}%</p>
      {uploadState.estimatedTimeRemaining && (
        <p>Estimated time remaining: {uploadState.estimatedTimeRemaining}</p>
      )}
    </div>
  );
};
```

### useLocalStorage

Provides a convenient interface for storing and retrieving data from the browser's localStorage API. This hook enables persistent state across page refreshes and browser sessions.

```jsx
// Using useLocalStorage hook
import { useLocalStorage } from '../hooks/useLocalStorage';

const UserPreferences = () => {
  const [theme, setTheme, removeTheme] = useLocalStorage('theme', 'light');
  
  return (
    <div>
      <p>Current theme: {theme}</p>
      <button onClick={() => setTheme('dark')}>Dark Mode</button>
      <button onClick={() => setTheme('light')}>Light Mode</button>
      <button onClick={removeTheme}>Reset to Default</button>
    </div>
  );
};
```

### Other Custom Hooks

The application includes several other custom hooks for specific functionality:

- useBreakpoint - Provides responsive breakpoint detection
- useClickOutside - Detects clicks outside a referenced element
- useIntersectionObserver - Tracks element visibility in viewport
- useKeyPress - Detects when specific keys are pressed
- useScrollToTop - Provides functionality to scroll to top of page

## Component-Level State

For UI-specific concerns that don't need to be shared across components, we use React's built-in useState and useReducer hooks directly in components.

```jsx
// Component-level state example
import { useState } from 'react';

const Accordion = ({ title, children }) => {
  const [isOpen, setIsOpen] = useState(false);
  
  return (
    <div className="accordion">
      <button 
        className="accordion-header" 
        onClick={() => setIsOpen(!isOpen)}
      >
        {title} {isOpen ? '▲' : '▼'}
      </button>
      {isOpen && (
        <div className="accordion-content">
          {children}
        </div>
      )}
    </div>
  );
};
```

## State Management Best Practices

The IndiVillage website follows these state management best practices:

- Use React Context for global state that needs to be accessed by many components
- Create custom hooks to encapsulate and reuse stateful logic
- Keep state as close as possible to where it's used (component-level when appropriate)
- Use TypeScript for type safety in state management
- Implement proper error handling in all state operations
- Avoid prop drilling by using context or custom hooks
- Optimize performance by preventing unnecessary re-renders

## Context Provider Composition

The application composes multiple context providers in the application root to make state available throughout the component tree.

```jsx
// Context provider composition in _app.tsx
import { AnalyticsProvider } from '../context/AnalyticsContext';
import { ToastProvider } from '../context/ToastContext';
import { UploadProvider } from '../context/UploadContext';

const App = ({ Component, pageProps }) => {
  return (
    <AnalyticsProvider>
      <ToastProvider>
        <UploadProvider>
          <Component {...pageProps} />
        </UploadProvider>
      </ToastProvider>
    </AnalyticsProvider>
  );
};
```