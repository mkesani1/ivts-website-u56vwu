import React, { useState, useRef, useEffect } from 'react'; // version 18.2.0
import classNames from 'classnames'; // version 2.3.2
import Loader from '../ui/Loader';
import { Size } from '../../types/common';
import { setAriaAttributes } from '../../utils/accessibility';

/**
 * Props interface for the ResponsiveVideo component
 */
interface ResponsiveVideoProps extends React.VideoHTMLAttributes<HTMLVideoElement> {
  /** URL of the video source */
  src: string;
  /** Title of the video for accessibility and metadata */
  title: string;
  /** URL for the poster image to display before the video plays */
  poster?: string;
  /** Additional CSS classes to apply to the container */
  className?: string;
  /** Aspect ratio of the video in format "width:height", e.g., "16:9" */
  aspectRatio?: string;
  /** Whether to show video controls */
  controls?: boolean;
  /** Whether to automatically play the video when loaded */
  autoPlay?: boolean;
  /** Whether the video should be muted */
  muted?: boolean;
  /** Whether the video should loop when it reaches the end */
  loop?: boolean;
}

/**
 * A component that renders responsive video content with proper aspect ratio and loading states.
 * Used throughout the IndiVillage website to display video content in impact stories and service showcases.
 * 
 * @param props - Component props including src, title, aspectRatio, etc.
 * @returns Rendered video component with appropriate responsive behavior
 */
const ResponsiveVideo: React.FC<ResponsiveVideoProps> = ({
  src,
  title,
  poster,
  className,
  aspectRatio = '16:9',
  controls = true,
  autoPlay = false,
  muted = false,
  loop = false,
  ...rest
}) => {
  // State to track video loading status
  const [isLoading, setIsLoading] = useState(true);
  const [hasError, setHasError] = useState(false);
  
  // Reference to the video element
  const videoRef = useRef<HTMLVideoElement>(null);

  // Calculate padding-bottom percentage based on aspect ratio to maintain proportions
  const calculateAspectRatioPadding = (ratio: string): string => {
    const [width, height] = ratio.split(':').map(Number);
    return `${(height / width) * 100}%`;
  };

  const paddingBottom = calculateAspectRatioPadding(aspectRatio);

  // Handle video loading events
  useEffect(() => {
    const videoElement = videoRef.current;
    
    if (!videoElement) return;
    
    const handleLoadStart = () => {
      setIsLoading(true);
      setHasError(false);
    };
    
    const handleCanPlay = () => {
      setIsLoading(false);
    };
    
    const handleError = () => {
      setIsLoading(false);
      setHasError(true);
    };
    
    // Add event listeners
    videoElement.addEventListener('loadstart', handleLoadStart);
    videoElement.addEventListener('canplay', handleCanPlay);
    videoElement.addEventListener('error', handleError);
    
    // Set initial loading state
    setIsLoading(true);
    
    // Set accessibility attributes
    setAriaAttributes(videoElement, {
      'role': 'application',
      'label': title
    });
    
    // Clean up event listeners on unmount
    return () => {
      videoElement.removeEventListener('loadstart', handleLoadStart);
      videoElement.removeEventListener('canplay', handleCanPlay);
      videoElement.removeEventListener('error', handleError);
    };
  }, [src, title]);

  // Combine CSS classes
  const videoContainerClasses = classNames(
    'responsive-video',
    {
      'responsive-video--loading': isLoading,
      'responsive-video--error': hasError
    },
    className
  );

  return (
    <div className={videoContainerClasses}>
      {/* Container with aspect ratio padding */}
      <div
        className="responsive-video__container"
        style={{ position: 'relative', paddingBottom, overflow: 'hidden' }}
      >
        {/* Video element */}
        <video
          ref={videoRef}
          className="responsive-video__element"
          src={src}
          poster={poster}
          controls={controls}
          autoPlay={autoPlay}
          muted={muted}
          loop={loop}
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            width: '100%',
            height: '100%',
            objectFit: 'cover'
          }}
          {...rest}
        >
          <p>Your browser doesn't support HTML video. Here is a <a href={src}>link to the video</a> instead.</p>
        </video>
        
        {/* Loading indicator */}
        {isLoading && (
          <div className="responsive-video__loader" style={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            zIndex: 1
          }}>
            <Loader size={Size.MEDIUM} />
          </div>
        )}
        
        {/* Error message */}
        {hasError && (
          <div className="responsive-video__error" style={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            textAlign: 'center',
            color: '#DC3545',
            backgroundColor: 'rgba(255, 255, 255, 0.8)',
            padding: '1rem',
            borderRadius: '0.25rem',
            zIndex: 1
          }}>
            <p>An error occurred while loading the video.</p>
          </div>
        )}
      </div>
      
      {/* Hidden title for screen readers */}
      {title && <div className="sr-only">{title}</div>}
    </div>
  );
};

export default ResponsiveVideo;