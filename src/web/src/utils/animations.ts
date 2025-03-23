import { useEffect, useState, useRef, useCallback } from 'react'; // v18.2.0

// Animation durations in milliseconds that align with the design system specifications
export const ANIMATION_DURATIONS = {
  MICRO: 150,      // Micro-interactions (0.15s)
  SUBTLE: 200,     // Subtle transitions (0.2s)
  STANDARD: 300,   // Standard transitions (0.3s)
  PAGE: 500        // Page transitions (0.5s)
};

// CSS easing functions for different animation types
export const EASING = {
  IN: 'cubic-bezier(0.4, 0, 1, 1)',              // Accelerate
  OUT: 'cubic-bezier(0, 0, 0.2, 1)',             // Decelerate
  IN_OUT: 'cubic-bezier(0.4, 0, 0.2, 1)',        // Accelerate and decelerate
  SPRING: 'cubic-bezier(0.175, 0.885, 0.32, 1.275)' // Elastic spring effect
};

/**
 * Checks if the user has enabled the reduced motion preference
 * in their operating system or browser settings
 * @returns {boolean} True if reduced motion is preferred, false otherwise
 */
export const prefersReducedMotion = (): boolean => {
  // Check if window and matchMedia are available (for SSR compatibility)
  if (typeof window === 'undefined' || !window.matchMedia) {
    return false;
  }
  // Use matchMedia to check for prefers-reduced-motion: reduce
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
};

/**
 * A hook that provides requestAnimationFrame with proper cleanup
 * @param {function} callback - Function to call on each animation frame
 */
export const useAnimationFrame = (callback: (deltaTime: number) => void): void => {
  // Create a reference to store the request animation frame ID
  const requestRef = useRef<number>();
  const previousTimeRef = useRef<number>();
  // Create a reference to store the callback function
  const callbackRef = useRef<(deltaTime: number) => void>(callback);

  // Update the callback reference when it changes
  useEffect(() => {
    callbackRef.current = callback;
  }, [callback]);

  // Start the animation loop when the component mounts
  useEffect(() => {
    const animate = (time: number) => {
      if (previousTimeRef.current !== undefined) {
        const deltaTime = time - previousTimeRef.current;
        callbackRef.current(deltaTime);
      }
      previousTimeRef.current = time;
      requestRef.current = requestAnimationFrame(animate);
    };
    
    requestRef.current = requestAnimationFrame(animate);
    
    // Clean up by canceling the animation frame when the component unmounts
    return () => {
      if (requestRef.current) {
        cancelAnimationFrame(requestRef.current);
      }
    };
  }, []);
};

interface AnimationControlsOptions {
  autoStart?: boolean;
  onStart?: () => void;
  onStop?: () => void;
  onReset?: () => void;
}

/**
 * A hook that provides controls for managing animations
 * @param {object} options - Optional configuration with autoStart flag and callbacks
 * @returns An object with animation state and control functions
 */
export const useAnimationControls = (options: AnimationControlsOptions = {}) => {
  const { autoStart = false, onStart, onStop, onReset } = options;
  // Initialize state to track if animation is currently running
  const [isAnimating, setIsAnimating] = useState(autoStart);

  // Function to start animation
  const start = useCallback(() => {
    setIsAnimating(true);
    if (onStart) onStart();
  }, [onStart]);

  // Function to stop animation
  const stop = useCallback(() => {
    setIsAnimating(false);
    if (onStop) onStop();
  }, [onStop]);

  // Function to reset animation
  const reset = useCallback(() => {
    setIsAnimating(false);
    if (onReset) onReset();
  }, [onReset]);

  return { isAnimating, start, stop, reset };
};

interface TransitionOptions {
  duration?: number;
  easing?: string;
  onComplete?: () => void;
}

/**
 * A hook that provides smooth transitions between values
 * @param {any} initialValue - Starting value (number or array of numbers)
 * @param {object} options - Optional configuration for duration, easing, and completion callback
 * @returns [currentValue, setValue, { isTransitioning }]
 */
export const useTransition = <T extends number | number[]>(
  initialValue: T,
  options: TransitionOptions = {}
): [T, (newValue: T) => void, { isTransitioning: boolean }] => {
  const { 
    duration = ANIMATION_DURATIONS.STANDARD, 
    easing = EASING.IN_OUT,
    onComplete 
  } = options;
  
  // Initialize state for the current value and target value
  const [currentValue, setCurrentValue] = useState<T>(initialValue);
  const [targetValue, setTargetValue] = useState<T>(initialValue);
  // Initialize state to track if transition is in progress
  const [isTransitioning, setIsTransitioning] = useState(false);
  const startTimeRef = useRef<number | null>(null);
  // Check if user prefers reduced motion
  const reducedMotion = prefersReducedMotion();

  // Provide function to set new target value and trigger transition
  const setValue = useCallback((newValue: T) => {
    setTargetValue(newValue);
    // Skip animation if reduced motion is preferred
    if (reducedMotion) {
      setCurrentValue(newValue);
      if (onComplete) onComplete();
      return;
    }
    setIsTransitioning(true);
    startTimeRef.current = null;
  }, [reducedMotion, onComplete]);

  // Set up animation frame loop to update value during transition
  useAnimationFrame((time) => {
    if (!isTransitioning) return;
    
    if (startTimeRef.current === null) {
      startTimeRef.current = time;
    }
    
    const elapsed = time - startTimeRef.current;
    const progress = Math.min(elapsed / duration, 1);
    
    // Calculate interpolation between current and target values
    let easedProgress = progress;
    // More sophisticated easing could be implemented here
    
    if (Array.isArray(currentValue) && Array.isArray(targetValue)) {
      // Handle array values (e.g., for coordinates)
      setCurrentValue(
        currentValue.map((v, i) => 
          v + (targetValue[i] - v) * easedProgress
        ) as T
      );
    } else if (typeof currentValue === 'number' && typeof targetValue === 'number') {
      // Handle single numeric values
      setCurrentValue(
        (currentValue + (targetValue - currentValue) * easedProgress) as T
      );
    }
    
    if (progress >= 1) {
      setIsTransitioning(false);
      setCurrentValue(targetValue);
      if (onComplete) onComplete();
    }
  });

  return [currentValue, setValue, { isTransitioning }];
};

interface FadeInOptions {
  duration?: number;
  delay?: number;
  easing?: string;
  initialOpacity?: number;
  finalOpacity?: number;
  translateY?: number;
}

/**
 * A hook that provides fade-in animation for elements when they mount
 * @param {object} options - Optional configuration for the animation
 * @returns An object with ref to attach to element and style properties
 */
export const useFadeIn = (options: FadeInOptions = {}) => {
  const {
    duration = ANIMATION_DURATIONS.STANDARD,
    delay = 0,
    easing = EASING.OUT,
    initialOpacity = 0,
    finalOpacity = 1,
    translateY = 0
  } = options;
  
  // Create a ref to attach to the target element
  const ref = useRef<HTMLElement>(null);
  // Initialize state for opacity and transform values
  const [opacity, setOpacity] = useState(initialOpacity);
  const [transform, setTransform] = useState(translateY ? `translateY(${translateY}px)` : 'none');
  // Check if user prefers reduced motion
  const reducedMotion = prefersReducedMotion();

  // Set up effect to animate opacity from 0 to 1 when component mounts
  useEffect(() => {
    // Skip animation if reduced motion is preferred
    if (reducedMotion) {
      setOpacity(finalOpacity);
      setTransform('none');
      return;
    }

    const element = ref.current;
    if (!element) return;

    const timer = setTimeout(() => {
      setOpacity(finalOpacity);
      setTransform('none');
    }, delay);

    return () => clearTimeout(timer);
  }, [finalOpacity, delay, reducedMotion, translateY]);

  return { 
    ref, 
    style: { 
      opacity, 
      transform,
      transition: `opacity ${duration}ms ${easing}, transform ${duration}ms ${easing}`,
      willChange: 'opacity, transform'
    } 
  };
};

interface SlideInOptions {
  duration?: number;
  delay?: number;
  easing?: string;
  distance?: number;
  initialOpacity?: number;
  finalOpacity?: number;
}

/**
 * A hook that provides slide-in animation for elements when they mount
 * @param {string} direction - Direction to slide from ('left', 'right', 'top', 'bottom')
 * @param {object} options - Optional configuration for the animation
 * @returns An object with ref to attach to element and style properties
 */
export const useSlideIn = (
  direction: 'left' | 'right' | 'top' | 'bottom',
  options: SlideInOptions = {}
) => {
  const {
    duration = ANIMATION_DURATIONS.STANDARD,
    delay = 0,
    easing = EASING.OUT,
    distance = 20,
    initialOpacity = 0,
    finalOpacity = 1
  } = options;
  
  // Create a ref to attach to the target element
  const ref = useRef<HTMLElement>(null);
  // Initialize state for opacity and transform values
  const [opacity, setOpacity] = useState(initialOpacity);
  const [transform, setTransform] = useState('');
  // Check if user prefers reduced motion
  const reducedMotion = prefersReducedMotion();

  // Determine initial transform based on direction parameter
  useEffect(() => {
    let initialTransform = '';
    
    switch (direction) {
      case 'left':
        initialTransform = `translateX(-${distance}px)`;
        break;
      case 'right':
        initialTransform = `translateX(${distance}px)`;
        break;
      case 'top':
        initialTransform = `translateY(-${distance}px)`;
        break;
      case 'bottom':
        initialTransform = `translateY(${distance}px)`;
        break;
    }
    
    setTransform(initialTransform);
    
    // Skip animation if reduced motion is preferred
    if (reducedMotion) {
      setOpacity(finalOpacity);
      setTransform('none');
      return;
    }

    const element = ref.current;
    if (!element) return;

    // Set up effect to animate from initial position to final position
    const timer = setTimeout(() => {
      setOpacity(finalOpacity);
      setTransform('none');
    }, delay);

    return () => clearTimeout(timer);
  }, [direction, distance, finalOpacity, delay, reducedMotion]);

  return { 
    ref, 
    style: { 
      opacity, 
      transform,
      transition: `opacity ${duration}ms ${easing}, transform ${duration}ms ${easing}`,
      willChange: 'opacity, transform'
    } 
  };
};

interface TransitionStylesOptions {
  duration?: number;
  properties?: string | string[];
  easing?: string;
  delay?: number;
}

/**
 * Generates CSS transition styles based on provided parameters
 * @param {object} options - Optional configuration for transitions
 * @returns A CSS style object with transition properties
 */
export const getTransitionStyles = (options: TransitionStylesOptions = {}) => {
  const {
    duration = ANIMATION_DURATIONS.STANDARD,
    properties = 'all',
    easing = EASING.IN_OUT,
    delay = 0
  } = options;
  
  // Format properties as a comma-separated string if an array is provided
  const propertiesStr = Array.isArray(properties) ? properties.join(', ') : properties;
  
  // Construct and return the CSS transition string
  return {
    transition: `${propertiesStr} ${duration}ms ${easing} ${delay}ms`
  };
};

interface AnimationStylesOptions {
  duration?: number;
  easing?: string;
  delay?: number;
  iterationCount?: number | 'infinite';
  direction?: 'normal' | 'reverse' | 'alternate' | 'alternate-reverse';
  fillMode?: 'none' | 'forwards' | 'backwards' | 'both';
}

/**
 * Generates CSS animation styles based on provided parameters
 * @param {string} name - Animation name (matching a @keyframes rule)
 * @param {object} options - Optional configuration for the animation
 * @returns A CSS style object with animation properties
 */
export const getAnimationStyles = (
  name: string,
  options: AnimationStylesOptions = {}
) => {
  const {
    duration = ANIMATION_DURATIONS.STANDARD,
    easing = EASING.IN_OUT,
    delay = 0,
    iterationCount = 1,
    direction = 'normal',
    fillMode = 'forwards'
  } = options;
  
  // Construct and return the CSS animation string
  return {
    animation: `${name} ${duration}ms ${easing} ${delay}ms ${iterationCount} ${direction} ${fillMode}`
  };
};