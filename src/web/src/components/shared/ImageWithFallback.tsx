import React, { useState } from 'react'; // version 18.2.0
import Image from 'next/image'; // version 13.4.0
import classNames from 'classnames'; // version 2.3.2
import Loader from '../ui/Loader';

/**
 * Props for the ImageWithFallback component that extends Next.js Image props
 */
export interface ImageWithFallbackProps {
  /**
   * Primary image source URL
   */
  src: string;
  
  /**
   * Alt text for accessibility
   */
  alt: string;
  
  /**
   * Fallback image to display if primary image fails to load
   */
  fallbackSrc?: string;
  
  /**
   * Image width in pixels
   */
  width: number;
  
  /**
   * Image height in pixels
   */
  height: number;
  
  /**
   * Additional CSS class names
   */
  className?: string;
  
  /**
   * Whether the image should be loaded with priority
   */
  priority?: boolean;
  
  /**
   * Image quality (1-100)
   */
  quality?: number;
  
  /**
   * Image loading behavior ('lazy' or 'eager')
   */
  loading?: string;
  
  /**
   * Object-fit CSS property for the image
   */
  objectFit?: string;
  
  /**
   * Object-position CSS property for the image
   */
  objectPosition?: string;
  
  /**
   * Additional image props passed to Next.js Image component
   */
  [key: string]: any;
}

/**
 * A component that renders an image with fallback handling when the primary image fails to load.
 * This component enhances the Next.js Image component with error handling capabilities,
 * displaying a fallback image when the primary image cannot be loaded.
 * 
 * @param props - Component props including image source, alt text, and fallback source
 * @returns Rendered image component with fallback handling
 */
const ImageWithFallback = ({
  src,
  alt,
  fallbackSrc,
  className,
  objectFit,
  objectPosition,
  ...rest
}: ImageWithFallbackProps): JSX.Element => {
  // State to track if the image is currently loading
  const [isLoading, setIsLoading] = useState(true);
  
  // State to track if the image has encountered an error
  const [hasError, setHasError] = useState(false);
  
  // Default fallback image if none provided
  const defaultFallbackSrc = '/images/placeholder.png';
  
  // Use provided fallback or default
  const actualFallbackSrc = fallbackSrc || defaultFallbackSrc;
  
  /**
   * Handler for when image finishes loading
   */
  const handleLoadingComplete = () => {
    setIsLoading(false);
  };
  
  /**
   * Handler for when image fails to load
   */
  const handleError = () => {
    setIsLoading(false);
    setHasError(true);
  };
  
  // Combine CSS classes
  const imageContainerClasses = classNames(
    'image-container',
    { 'image-loading': isLoading },
    { 'image-error': hasError },
    className
  );
  
  // Prepare style object with objectFit and objectPosition if provided
  const imageStyle: React.CSSProperties = {};
  
  if (objectFit) {
    imageStyle.objectFit = objectFit as any;
  }
  
  if (objectPosition) {
    imageStyle.objectPosition = objectPosition;
  }
  
  return (
    <div className={imageContainerClasses}>
      {isLoading && (
        <div className="image-loader" aria-hidden="true">
          <Loader size="medium" />
        </div>
      )}
      
      <Image
        src={hasError ? actualFallbackSrc : src}
        alt={alt || ''}
        onLoadingComplete={handleLoadingComplete}
        onError={handleError}
        style={Object.keys(imageStyle).length > 0 ? imageStyle : undefined}
        {...rest}
      />
      
      {hasError && !fallbackSrc && (
        <span className="sr-only">
          Image could not be loaded. Using placeholder image instead.
        </span>
      )}
    </div>
  );
};

export default ImageWithFallback;