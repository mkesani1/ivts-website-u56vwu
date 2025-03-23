import { useEffect, useRef } from 'react'; // React 18.2.0

/**
 * Optional configuration for the useClickOutside hook.
 */
interface UseClickOutsideOptions {
  /**
   * Flag to enable/disable the click detection
   */
  enabled?: boolean;
  
  /**
   * Options for the event listener
   */
  eventOptions?: EventListenerOptions;
}

/**
 * A custom hook that detects clicks outside of a specified element and triggers a callback function.
 * This is useful for implementing dismissible components like dropdowns, modals, and popups.
 * 
 * @param ref - React ref object pointing to the element to monitor for outside clicks
 * @param callback - Function to call when a click outside the element is detected
 * @param enabled - Flag to enable/disable the hook (default: true)
 * @returns void
 * 
 * @example
 * ```tsx
 * const dropdownRef = useRef<HTMLDivElement>(null);
 * useClickOutside(dropdownRef, () => setIsOpen(false));
 * 
 * // With enabled flag
 * useClickOutside(dropdownRef, () => setIsOpen(false), isDialogOpen);
 * ```
 */
const useClickOutside = (
  ref: React.RefObject<HTMLElement>,
  callback: () => void,
  enabled: boolean = true
): void => {
  // Store the callback in a ref to avoid unnecessary effect triggers
  const callbackRef = useRef(callback);
  
  // Update the callback ref whenever the callback function changes
  useEffect(() => {
    callbackRef.current = callback;
  }, [callback]);
  
  useEffect(() => {
    // Skip setting up the listener if the hook is disabled
    if (!enabled) {
      return;
    }
    
    const handleClickOutside = (event: MouseEvent) => {
      // Cast the event target to Node for type safety
      const target = event.target as Node;
      
      // Check if the click target is outside the referenced element
      if (ref.current && !ref.current.contains(target)) {
        callbackRef.current();
      }
    };
    
    // Add event listener to the document
    document.addEventListener('mousedown', handleClickOutside);
    
    // Clean up by removing the event listener when the component unmounts or dependencies change
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [ref, enabled]);
};

export default useClickOutside;