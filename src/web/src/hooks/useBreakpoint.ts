import { useState, useEffect } from 'react'; // v18.0.0
import { Breakpoint } from '../types/common';
import { BREAKPOINTS, getWindowDimensions } from '../utils/responsive';

/**
 * A custom React hook that provides responsive breakpoint detection for the IndiVillage website.
 * This hook tracks window resize events and determines the current active breakpoint based on screen width.
 * 
 * @returns {Breakpoint} The current active breakpoint (MOBILE_SMALL, MOBILE, TABLET, DESKTOP, or LARGE_DESKTOP)
 */
const useBreakpoint = (): Breakpoint => {
  // Initialize state for current breakpoint with a default for SSR
  const [breakpoint, setBreakpoint] = useState<Breakpoint>(Breakpoint.DESKTOP);

  /**
   * Determines the current breakpoint based on window width
   * 
   * @param {number} width - The current window width
   * @returns {Breakpoint} The matching breakpoint
   */
  const determineBreakpoint = (width: number): Breakpoint => {
    if (width < BREAKPOINTS.MOBILE_SMALL) {
      return Breakpoint.MOBILE_SMALL;
    } else if (width >= 376 && width <= BREAKPOINTS.MOBILE) {
      return Breakpoint.MOBILE;
    } else if (width >= 768 && width <= BREAKPOINTS.TABLET) {
      return Breakpoint.TABLET;
    } else if (width >= 1024 && width <= BREAKPOINTS.DESKTOP) {
      return Breakpoint.DESKTOP;
    } else {
      return Breakpoint.LARGE_DESKTOP;
    }
  };

  useEffect(() => {
    // Skip effect during SSR
    if (typeof window === 'undefined') return;

    // Handler for window resize events
    const handleResize = () => {
      const { width } = getWindowDimensions();
      const newBreakpoint = determineBreakpoint(width);
      
      // Only update state if breakpoint has changed
      setBreakpoint(prevBreakpoint => {
        if (newBreakpoint !== prevBreakpoint) {
          return newBreakpoint;
        }
        return prevBreakpoint;
      });
    };

    // Add window resize event listener
    window.addEventListener('resize', handleResize);
    
    // Set initial breakpoint on mount
    handleResize();
    
    // Clean up event listener on component unmount
    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, []); // Empty dependency array ensures effect runs only on mount and unmount

  return breakpoint;
};

export default useBreakpoint;