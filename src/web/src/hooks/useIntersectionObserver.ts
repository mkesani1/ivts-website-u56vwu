import { useState, useEffect, useRef } from 'react'; // react v18.0.0

/**
 * Interface defining the options for the IntersectionObserver.
 */
export interface IntersectionObserverOptions {
  /**
   * Either a single threshold or an array of thresholds where a threshold is a percentage of the target element 
   * that should be visible before triggering the callback.
   */
  threshold?: number | number[];
  
  /**
   * The element that is used as the viewport for checking visibility of the target.
   * Defaults to the browser viewport if not specified or if null.
   */
  root?: Element | null;
  
  /**
   * Margin around the root element. Can have values similar to the CSS margin property.
   * e.g. "10px 20px 30px 40px" (top, right, bottom, left).
   */
  rootMargin?: string;
  
  /**
   * Callback function that is invoked whenever the target meets the threshold criteria.
   * @param isIntersecting - Whether the target element is currently intersecting with the root
   * @param entry - The IntersectionObserverEntry containing detailed information
   */
  onIntersect?: (isIntersecting: boolean, entry: IntersectionObserverEntry) => void;
}

/**
 * A custom React hook that uses the Intersection Observer API to detect when an element enters or exits the viewport.
 * This can be used for implementing lazy loading, infinite scrolling, or triggering animations when elements become visible.
 * 
 * @param options - Configuration options for the Intersection Observer
 * @returns [ref, isIntersecting, entry]
 *   - ref: A React ref that should be attached to the target element
 *   - isIntersecting: A boolean indicating whether the element is currently intersecting
 *   - entry: The IntersectionObserverEntry object containing detailed information about the intersection
 * 
 * @example
 * ```tsx
 * const MyComponent = () => {
 *   const [ref, isVisible] = useIntersectionObserver();
 * 
 *   return (
 *     <div ref={ref}>
 *       {isVisible ? 'Element is visible!' : 'Element is not visible'}
 *     </div>
 *   );
 * };
 * ```
 * 
 * @example
 * // With options and callback
 * ```tsx
 * const LazyImage = ({ src, alt }) => {
 *   const [ref, isVisible] = useIntersectionObserver({
 *     threshold: 0.1,
 *     rootMargin: '100px',
 *     onIntersect: (isIntersecting) => {
 *       if (isIntersecting) {
 *         console.log('Image is now in viewport');
 *       }
 *     }
 *   });
 * 
 *   return (
 *     <div ref={ref}>
 *       {isVisible ? <img src={src} alt={alt} /> : <div>Loading...</div>}
 *     </div>
 *   );
 * };
 * ```
 */
export default function useIntersectionObserver<T extends Element = Element>(
  options: IntersectionObserverOptions = {}
): [React.RefObject<T>, boolean, IntersectionObserverEntry | null] {
  const {
    threshold = 0,
    root = null,
    rootMargin = '0px',
    onIntersect
  } = options;

  // Create a ref that we'll attach to the target element
  const targetRef = useRef<T>(null);
  
  // State to keep track of whether the element is intersecting
  const [isIntersecting, setIsIntersecting] = useState<boolean>(false);
  
  // State to store the latest entry
  const [entry, setEntry] = useState<IntersectionObserverEntry | null>(null);

  useEffect(() => {
    // Check if Intersection Observer API is supported in the browser
    if (!('IntersectionObserver' in window)) {
      console.warn('IntersectionObserver is not supported in this browser.');
      return;
    }

    // The element we want to observe
    const element = targetRef.current;
    
    // If we don't have an element to observe, we can return early
    if (!element) {
      return;
    }

    // Create a callback function to handle intersection changes
    const handleIntersect: IntersectionObserverCallback = (entries, observer) => {
      // Since we're observing a single element, we only need to check the first entry
      const firstEntry = entries[0];
      
      // Update the state with the latest intersection status
      setIsIntersecting(firstEntry.isIntersecting);
      setEntry(firstEntry);
      
      // Call the user callback if provided
      if (onIntersect) {
        onIntersect(firstEntry.isIntersecting, firstEntry);
      }
    };

    // Create the IntersectionObserver instance
    const observer = new IntersectionObserver(handleIntersect, {
      threshold,
      root,
      rootMargin
    });

    // Start observing the target element
    observer.observe(element);

    // Clean up the observer when the component unmounts or when dependencies change
    return () => {
      observer.disconnect();
    };
  }, [threshold, root, rootMargin, onIntersect]); // Re-run when these dependencies change

  // Return the ref, intersection state, and the latest entry
  return [targetRef, isIntersecting, entry];
}