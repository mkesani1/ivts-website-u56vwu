import { useEffect } from 'react'; // React 18.2.0
import { usePathname } from 'next/navigation'; // Next.js 13.4.0

/**
 * Interface for scroll configuration options
 */
export interface ScrollOptions {
  /**
   * The scroll behavior - smooth for animated scrolling, auto for instant scrolling
   */
  behavior?: ScrollBehavior;
  
  /**
   * The vertical position to scroll to (default is 0, the top)
   */
  top?: number;
  
  /**
   * The horizontal position to scroll to (default is 0, the left)
   */
  left?: number;
}

/**
 * A custom hook that automatically scrolls the window to the top when the route changes.
 * This is particularly useful in single-page applications to ensure users start at the 
 * top of the page after navigation, improving both user experience and accessibility.
 * 
 * @param options - Configuration options for scrolling behavior
 */
const useScrollToTop = (options: ScrollOptions = {}): void => {
  // Get the current pathname to detect route changes
  const pathname = usePathname();
  
  // Destructure options with default values
  const { 
    behavior = 'auto', 
    top = 0, 
    left = 0 
  } = options;

  useEffect(() => {
    // Check if window is available (not in SSR context)
    if (typeof window !== 'undefined') {
      // Scroll to the specified position when pathname changes
      window.scrollTo({
        behavior,
        top,
        left
      });
    }
  }, [pathname, behavior, top, left]); // Re-run when pathname or options change
};

export default useScrollToTop;