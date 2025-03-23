import React, { useState, useEffect, useRef } from 'react'; // react v18.2.0
import classNames from 'classnames'; // v2.3.2
import useIntersectionObserver from '../../hooks/useIntersectionObserver';
import { prefersReducedMotion, ANIMATION_DURATIONS } from '../../utils/animations';

/**
 * Props interface for the AnimatedCounter component
 */
interface AnimatedCounterProps extends React.HTMLAttributes<HTMLDivElement> {
  /** The target value to count to */
  value: number;
  /** Animation duration in milliseconds, defaults to 1200ms */
  duration?: number;
  /** Delay before animation starts in milliseconds, defaults to 0 */
  delay?: number;
  /** Text to display before the number */
  prefix?: string;
  /** Text to display after the number */
  suffix?: string;
  /** Number of decimal places to show, defaults to 0 */
  decimals?: number;
  /** Additional CSS classes */
  className?: string;
}

/**
 * Easing function that creates a smooth deceleration effect for the counter animation
 * @param t - Progress value between 0 and 1
 * @returns Calculated easing value
 */
const easeOutExpo = (t: number): number => {
  return t === 1 ? 1 : 1 - Math.pow(2, -10 * t);
};

/**
 * Formats a number with thousands separators and optional decimal places
 * @param value - The number to format
 * @param decimals - Number of decimal places to display
 * @returns Formatted number string
 */
const formatNumber = (value: number, decimals: number = 0): string => {
  // Format with fixed decimals to get the correctly rounded string with trailing zeros
  const fixedString = value.toFixed(decimals);
  
  // Split into integer and decimal parts
  const parts = fixedString.split('.');
  
  // Add thousands separators to the integer part
  parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ',');
  
  // Join parts back together
  return parts.join('.');
};

/**
 * Component that animates counting from zero to a target value when it enters the viewport
 * 
 * @example
 * ```tsx
 * <AnimatedCounter 
 *   value={1000} 
 *   prefix="$" 
 *   decimals={2} 
 *   duration={2000} 
 * />
 * ```
 */
const AnimatedCounter = ({
  value,
  duration = ANIMATION_DURATIONS.STANDARD * 4, // Default to 1200ms (300ms * 4)
  delay = 0,
  prefix = '',
  suffix = '',
  decimals = 0,
  className = '',
  ...props
}: AnimatedCounterProps) => {
  // State to hold the current displayed value
  const [count, setCount] = useState<number>(0);
  
  // Detect when the counter is visible in the viewport
  const [counterRef, isVisible] = useIntersectionObserver<HTMLDivElement>({
    threshold: 0.1 // Trigger when at least 10% of the counter is visible
  });
  
  // Reference to the animation frame for cleanup
  const requestRef = useRef<number>();
  
  // Reference to track animation start time
  const startTimeRef = useRef<number | null>(null);
  
  // Check if user prefers reduced motion
  const reducedMotion = prefersReducedMotion();

  // Effect to handle the animation
  useEffect(() => {
    // Only start animation when element is visible
    if (isVisible) {
      // If reduced motion is preferred, skip animation
      if (reducedMotion) {
        setCount(value);
        return;
      }

      // Reset animation start time
      startTimeRef.current = null;

      // Animation function to run with requestAnimationFrame
      const animate = (timestamp: number) => {
        // Initialize start time on first frame
        if (startTimeRef.current === null) {
          startTimeRef.current = timestamp;
        }

        const elapsed = timestamp - startTimeRef.current;
        
        // If we've passed the delay, start the animation
        if (elapsed > delay) {
          const animationElapsed = elapsed - delay;
          const progress = Math.min(animationElapsed / duration, 1);
          const easedProgress = easeOutExpo(progress);
          
          // Update the counter with eased progress
          setCount(easedProgress * value);
          
          // Continue animation if not complete
          if (progress < 1) {
            requestRef.current = requestAnimationFrame(animate);
          }
        } else {
          // Still in delay period, continue waiting
          requestRef.current = requestAnimationFrame(animate);
        }
      };

      // Start the animation
      requestRef.current = requestAnimationFrame(animate);
    }

    // Clean up animation frame on unmount or when dependencies change
    return () => {
      if (requestRef.current) {
        cancelAnimationFrame(requestRef.current);
      }
    };
  }, [isVisible, value, duration, delay, reducedMotion]);

  // Format the current value for display
  const formattedValue = formatNumber(count, decimals);

  // Render the counter with prefix and suffix
  return (
    <div
      ref={counterRef}
      className={classNames('animated-counter', className)}
      {...props}
    >
      {prefix}{formattedValue}{suffix}
    </div>
  );
};

export default AnimatedCounter;