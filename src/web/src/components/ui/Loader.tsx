import React from 'react'; // version 18.2.0
import classNames from 'classnames'; // version 2.3.2
import { Size, SizeValue } from '../../types/common';
import { setAriaAttributes } from '../../utils/accessibility';

/**
 * Interface for Loader component props
 */
export interface LoaderProps extends React.HTMLAttributes<HTMLDivElement> {
  /**
   * Size of the loader, can be a predefined size or a custom number in pixels
   * @default 'medium'
   */
  size?: SizeValue | number;
  
  /**
   * Color of the loader
   * @default 'currentColor'
   */
  color?: string;
  
  /**
   * Additional CSS classes to apply to the loader
   */
  className?: string;
  
  /**
   * Type of loader animation
   * @default 'spinner'
   */
  variant?: string;
}

/**
 * Determines the appropriate dimensions for a loader based on the size prop
 * @param size - The size value (can be a number or a predefined size)
 * @returns The size in pixels
 */
const getLoaderSize = (size?: SizeValue | number): number => {
  if (typeof size === 'number') {
    return size;
  }

  switch (size) {
    case Size.SMALL:
      return 16;
    case Size.LARGE:
      return 32;
    case Size.MEDIUM:
    default:
      return 24;
  }
};

/**
 * A customizable loading indicator component that displays a spinner or dots animation
 * to provide visual feedback during asynchronous operations like form submissions and file uploads.
 * 
 * @param props - Component props including size, color, className, and variant
 * @returns Rendered loader element
 */
const Loader: React.FC<LoaderProps> = ({
  size,
  color = 'currentColor',
  className,
  variant = 'spinner',
  ...rest
}) => {
  // Calculate the size in pixels based on the size prop
  const sizeInPx = getLoaderSize(size);
  
  // Combine base loader classes with any custom classes
  const loaderClasses = classNames(
    'loader',
    `loader--${variant}`,
    className
  );

  // Create a ref for the loader element
  const loaderRef = React.useRef<HTMLDivElement>(null);

  // Set ARIA attributes for accessibility once the component is mounted
  React.useEffect(() => {
    if (loaderRef.current) {
      setAriaAttributes(loaderRef.current, {
        'role': 'status',
        'live': 'polite',
        'busy': 'true',
        'label': 'Loading, please wait.'
      });
    }
  }, []);

  // Render different loader variants based on the variant prop
  switch (variant) {
    case 'dots':
      // Dots variant - multiple dots with a pulsing animation
      return (
        <div 
          ref={loaderRef}
          className={loaderClasses}
          role="status"
          aria-live="polite"
          {...rest}
        >
          {[...Array(3)].map((_, index) => (
            <div 
              key={index}
              className="loader__dot"
              style={{
                width: `${sizeInPx / 4}px`,
                height: `${sizeInPx / 4}px`,
                backgroundColor: color,
              }}
            />
          ))}
          <span className="sr-only">Loading, please wait.</span>
        </div>
      );
    
    case 'spinner':
    default:
      // Spinner variant (default) - a circular spinner with a rotating animation
      return (
        <div
          ref={loaderRef}
          className={loaderClasses}
          role="status"
          aria-live="polite"
          style={{
            width: `${sizeInPx}px`,
            height: `${sizeInPx}px`,
            borderColor: `${color} transparent transparent transparent`,
          }}
          {...rest}
        >
          <span className="sr-only">Loading, please wait.</span>
        </div>
      );
  }
};

export default Loader;