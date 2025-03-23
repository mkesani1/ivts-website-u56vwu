import React from 'react'; // version 18.2.0

/**
 * CSS selector for all potentially focusable elements
 * This covers standard interactive elements and those with tabindex attribute
 */
export const FocusableElementSelector = 'a[href], button:not([disabled]), input:not([disabled]), textarea:not([disabled]), select:not([disabled]), details, [tabindex]:not([tabindex="-1"])';

/**
 * Sets appropriate ARIA attributes on an element to improve accessibility
 * @param element - The HTML element to set attributes on
 * @param attributes - Object containing ARIA attribute key-value pairs
 */
export const setAriaAttributes = (element: HTMLElement, attributes: Record<string, string>): void => {
  if (!element) return;

  Object.entries(attributes).forEach(([key, value]) => {
    // Handle special case for role attribute
    if (key === 'role') {
      element.setAttribute('role', value);
    } 
    // Handle special case for label attribute
    else if (key === 'label') {
      element.setAttribute('aria-label', value);
    } 
    // All other aria attributes
    else {
      const ariaKey = key.startsWith('aria-') ? key : `aria-${key}`;
      element.setAttribute(ariaKey, value);
    }
  });
};

/**
 * Gets all focusable elements within a container element
 * @param container - The container element to search within
 * @returns Array of focusable elements
 */
export const getFocusableElements = (container: HTMLElement): HTMLElement[] => {
  if (!container) return [];

  // Query all potential focusable elements
  const elements = Array.from(
    container.querySelectorAll<HTMLElement>(FocusableElementSelector)
  );

  // Filter out elements that are not actually focusable
  return elements.filter(element => {
    // Check if element is visible
    const isVisible = !!(element.offsetWidth || element.offsetHeight || element.getClientRects().length);
    // Check if element is not disabled
    const isNotDisabled = !element.hasAttribute('disabled');
    // Check if element does not have tabindex=-1
    const isNotExcludedByTabIndex = element.getAttribute('tabindex') !== '-1';
    
    return isVisible && isNotDisabled && isNotExcludedByTabIndex;
  });
};

/**
 * Sets focus on a specified element with additional options
 * @param element - The element to focus
 * @param options - Focus options (e.g. preventScroll)
 */
export const setFocus = (element: HTMLElement, options: { preventScroll?: boolean } = {}): void => {
  if (!element) return;
  
  element.focus(options);
};

/**
 * Traps keyboard focus within a specified container element
 * @param container - The container element to trap focus within
 * @param options - Additional options for focus trapping
 * @returns Cleanup function to remove event listeners
 */
export const trapFocus = (
  container: HTMLElement, 
  options: { initialFocus?: HTMLElement } = {}
): () => void => {
  if (!container) return () => {};
  
  // Get all focusable elements
  const focusableElements = getFocusableElements(container);
  
  if (focusableElements.length === 0) return () => {};
  
  // Focus the initial element if specified, otherwise focus the first element
  if (options.initialFocus) {
    setFocus(options.initialFocus);
  } else {
    setFocus(focusableElements[0]);
  }
  
  const handleTabKey = (event: KeyboardEvent) => {
    // Only handle Tab key presses
    if (event.key !== 'Tab') return;
    
    // Get current focus position
    const currentFocusIndex = focusableElements.indexOf(document.activeElement as HTMLElement);
    
    // Handle wrapping at the end and start of the focusable elements
    if (event.shiftKey) {
      // If Shift+Tab and we're at the first element or before it
      if (currentFocusIndex <= 0) {
        event.preventDefault();
        setFocus(focusableElements[focusableElements.length - 1]);
      }
    } else {
      // If Tab and we're at the last element
      if (currentFocusIndex === focusableElements.length - 1) {
        event.preventDefault();
        setFocus(focusableElements[0]);
      }
    }
  };
  
  // Add event listener
  container.addEventListener('keydown', handleTabKey);
  
  // Return cleanup function
  return () => {
    container.removeEventListener('keydown', handleTabKey);
  };
};

/**
 * Manages focus when components mount/unmount or modals open/close
 * @param element - The element to focus
 * @param returnElement - The element to return focus to when cleaning up
 * @param shouldFocus - Whether focus should be applied
 * @returns Cleanup function to restore focus
 */
export const manageFocus = (
  element: HTMLElement, 
  returnElement?: HTMLElement, 
  shouldFocus: boolean = true
): () => void => {
  // Store the currently focused element
  const previouslyFocused = document.activeElement as HTMLElement;
  
  // Focus the specified element if shouldFocus is true
  if (shouldFocus && element) {
    setFocus(element);
  }
  
  // Return cleanup function
  return () => {
    // Determine which element to restore focus to
    const elementToFocus = returnElement || previouslyFocused;
    
    // Restore focus if the element exists and is focusable
    if (elementToFocus && typeof elementToFocus.focus === 'function') {
      setFocus(elementToFocus);
    }
  };
};

/**
 * Announces a message to screen readers using ARIA live regions
 * @param message - The message to announce
 * @param politeness - The politeness level ('polite' or 'assertive')
 */
export const announceToScreenReader = (
  message: string, 
  politeness: 'polite' | 'assertive' = 'polite'
): void => {
  if (!message) return;
  
  // Create or get existing aria-live region
  let liveRegion = document.getElementById('aria-live-announcer');
  
  if (!liveRegion) {
    // Create the live region if it doesn't exist
    liveRegion = document.createElement('div');
    liveRegion.id = 'aria-live-announcer';
    liveRegion.className = 'sr-only'; // Screen reader only
    
    // Apply styles to hide visually but keep available to screen readers
    liveRegion.style.position = 'absolute';
    liveRegion.style.width = '1px';
    liveRegion.style.height = '1px';
    liveRegion.style.padding = '0';
    liveRegion.style.margin = '-1px';
    liveRegion.style.overflow = 'hidden';
    liveRegion.style.clip = 'rect(0, 0, 0, 0)';
    liveRegion.style.whiteSpace = 'nowrap';
    liveRegion.style.border = '0';
    
    document.body.appendChild(liveRegion);
  }
  
  // Set appropriate aria-live attribute
  liveRegion.setAttribute('aria-live', politeness);
  
  // Update the content to announce it
  liveRegion.textContent = message;
  
  // Clear the announcement after it's been processed
  setTimeout(() => {
    liveRegion.textContent = '';
  }, 1000);
};

/**
 * Sets up an event listener for the Escape key to trigger a callback
 * @param callback - Function to call when Escape is pressed
 * @param element - Element to attach the listener to (defaults to document)
 * @returns Cleanup function to remove event listener
 */
export const handleEscapeKey = (
  callback: () => void, 
  element: HTMLElement | Document = document
): () => void => {
  if (!callback) return () => {};
  
  const handleKeyDown = (event: KeyboardEvent) => {
    if (event.key === 'Escape') {
      callback();
    }
  };
  
  // Add event listener
  element.addEventListener('keydown', handleKeyDown);
  
  // Return cleanup function
  return () => {
    element.removeEventListener('keydown', handleKeyDown);
  };
};

/**
 * Detects if the user has enabled reduced motion preferences
 * @returns Whether reduced motion is preferred
 */
export const isReducedMotionPreferred = (): boolean => {
  // Check if window is defined (for SSR compatibility)
  if (typeof window === 'undefined') return false;
  
  // Check for reduced motion preference
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
};