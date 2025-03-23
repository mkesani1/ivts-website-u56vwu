/**
 * Responsive design utility module for the IndiVillage website
 * This module provides responsive design functionality including breakpoint definitions,
 * window dimension detection, and responsive helper functions.
 * 
 * Implements responsive breakpoint constants and utilities to support adaptive layouts
 * across mobile, tablet, and desktop devices as defined in Technical Specifications/7.12 RESPONSIVE BREAKPOINTS
 */

import { Breakpoint } from '../types/common';

/**
 * Pixel values for each breakpoint as defined in the Technical Specifications
 */
export const BREAKPOINTS = {
  MOBILE_SMALL: 375,      // < 375px (upper limit)
  MOBILE: 767,            // 376px - 767px (upper limit)
  TABLET: 1023,           // 768px - 1023px (upper limit)
  DESKTOP: 1439,          // 1024px - 1439px (upper limit)
  LARGE_DESKTOP: 1440     // ≥ 1440px (minimum)
};

/**
 * Minimum width values for each breakpoint
 * Used internally for breakpoint matching logic
 */
const BREAKPOINT_MIN_WIDTHS: Record<Breakpoint, number> = {
  [Breakpoint.MOBILE_SMALL]: 0,        // Any width
  [Breakpoint.MOBILE]: 376,            // 376px - 767px
  [Breakpoint.TABLET]: 768,            // 768px - 1023px
  [Breakpoint.DESKTOP]: 1024,          // 1024px - 1439px
  [Breakpoint.LARGE_DESKTOP]: 1440     // ≥ 1440px
};

/**
 * Gets the current window dimensions (width and height)
 * Handles SSR by checking if window is defined
 * 
 * @returns {Object} The current window width and height
 */
export const getWindowDimensions = (): { width: number; height: number } => {
  if (typeof window !== 'undefined') {
    return {
      width: window.innerWidth,
      height: window.innerHeight
    };
  }
  // Return default values for SSR
  return {
    width: 0,
    height: 0
  };
};

/**
 * Determines the current breakpoint based on window width
 * 
 * @returns {Breakpoint} The current active breakpoint (MOBILE_SMALL, MOBILE, TABLET, DESKTOP, or LARGE_DESKTOP)
 */
export const getCurrentBreakpoint = (): Breakpoint => {
  const { width } = getWindowDimensions();
  
  if (width < BREAKPOINTS.MOBILE_SMALL) {
    return Breakpoint.MOBILE_SMALL;
  } else if (width >= BREAKPOINT_MIN_WIDTHS[Breakpoint.MOBILE] && width <= BREAKPOINTS.MOBILE) {
    return Breakpoint.MOBILE;
  } else if (width >= BREAKPOINT_MIN_WIDTHS[Breakpoint.TABLET] && width <= BREAKPOINTS.TABLET) {
    return Breakpoint.TABLET;
  } else if (width >= BREAKPOINT_MIN_WIDTHS[Breakpoint.DESKTOP] && width <= BREAKPOINTS.DESKTOP) {
    return Breakpoint.DESKTOP;
  } else {
    return Breakpoint.LARGE_DESKTOP;
  }
};

/**
 * Checks if the current window width matches or exceeds a specific breakpoint
 * 
 * @param {Breakpoint} breakpoint - The breakpoint to check
 * @returns {boolean} True if the current width matches or exceeds the specified breakpoint
 */
export const isBreakpointMatched = (breakpoint: Breakpoint): boolean => {
  const { width } = getWindowDimensions();
  const minWidth = BREAKPOINT_MIN_WIDTHS[breakpoint];
  
  return width >= minWidth;
};

/**
 * Checks if the current device is a mobile device (MOBILE or MOBILE_SMALL)
 * 
 * @returns {boolean} True if the current device is a mobile device
 */
export const isMobile = (): boolean => {
  const currentBreakpoint = getCurrentBreakpoint();
  return (
    currentBreakpoint === Breakpoint.MOBILE ||
    currentBreakpoint === Breakpoint.MOBILE_SMALL
  );
};

/**
 * Checks if the current device is a tablet
 * 
 * @returns {boolean} True if the current device is a tablet
 */
export const isTablet = (): boolean => {
  const currentBreakpoint = getCurrentBreakpoint();
  return currentBreakpoint === Breakpoint.TABLET;
};

/**
 * Checks if the current device is a desktop (DESKTOP or LARGE_DESKTOP)
 * 
 * @returns {boolean} True if the current device is a desktop
 */
export const isDesktop = (): boolean => {
  const currentBreakpoint = getCurrentBreakpoint();
  return (
    currentBreakpoint === Breakpoint.DESKTOP ||
    currentBreakpoint === Breakpoint.LARGE_DESKTOP
  );
};