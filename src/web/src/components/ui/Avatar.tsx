import React from 'react';
import classNames from 'classnames'; // version 2.3.2
import { Size, SizeValue } from '../../types/common';
import { setAriaAttributes } from '../../utils/accessibility';
import ImageWithFallback from '../shared/ImageWithFallback';
import Icon from './Icon';

/**
 * Interface for Avatar component props
 */
export interface AvatarProps {
  /**
   * Image source URL
   */
  src?: string;
  
  /**
   * Alt text for accessibility
   */
  alt?: string;
  
  /**
   * Size of the avatar
   * @default 'medium'
   */
  size?: SizeValue;
  
  /**
   * Shape of the avatar
   * @default 'circle'
   */
  shape?: 'circle' | 'square';
  
  /**
   * Additional CSS class names
   */
  className?: string;
  
  /**
   * Fallback image to display if primary image fails to load
   */
  fallbackSrc?: string;
  
  /**
   * Click handler for the avatar
   */
  onClick?: () => void;
}

/**
 * Returns the CSS class name for a given avatar size
 * @param size - Size value
 * @returns CSS class name for the specified size
 */
const getAvatarSizeClass = (size: SizeValue): string => {
  switch (size) {
    case Size.SMALL:
      return 'avatar--small';
    case Size.LARGE:
      return 'avatar--large';
    case Size.MEDIUM:
    default:
      return 'avatar--medium';
  }
};

/**
 * A customizable avatar component that displays user profile images with fallback options
 * 
 * @param props - Component props including image source, size, shape, and fallback image
 * @returns Rendered avatar component
 */
const Avatar = ({
  src,
  alt = 'User avatar',
  size = Size.MEDIUM,
  shape = 'circle',
  className,
  fallbackSrc,
  onClick,
  ...rest
}: AvatarProps): JSX.Element => {
  // Determine CSS classes based on size and shape
  const avatarClasses = classNames(
    'avatar',
    getAvatarSizeClass(size),
    `avatar--${shape}`,
    { 'avatar--clickable': !!onClick },
    className
  );
  
  // Calculate pixel dimensions based on size
  let pixelSize: number;
  switch (size) {
    case Size.SMALL:
      pixelSize = 32;
      break;
    case Size.LARGE:
      pixelSize = 64;
      break;
    case Size.MEDIUM:
    default:
      pixelSize = 48;
      break;
  }
  
  // Create a ref for the avatar element
  const avatarRef = React.useRef<HTMLDivElement>(null);
  
  // Set ARIA attributes for accessibility once the component is mounted
  React.useEffect(() => {
    if (avatarRef.current) {
      setAriaAttributes(avatarRef.current, {
        'role': onClick ? 'button' : 'img',
        'label': alt
      });
      
      // If clickable, add tabindex for keyboard navigation
      if (onClick) {
        avatarRef.current.setAttribute('tabindex', '0');
      }
    }
  }, [alt, onClick]);
  
  // Handle keyboard events for accessibility if clickable
  const handleKeyDown = (event: React.KeyboardEvent<HTMLDivElement>) => {
    if (onClick && (event.key === 'Enter' || event.key === ' ')) {
      event.preventDefault();
      onClick();
    }
  };
  
  return (
    <div 
      ref={avatarRef}
      className={avatarClasses}
      onClick={onClick}
      onKeyDown={handleKeyDown}
      {...rest}
    >
      {src ? (
        <ImageWithFallback
          src={src}
          alt={alt}
          width={pixelSize}
          height={pixelSize}
          fallbackSrc={fallbackSrc}
          className="avatar__image"
          objectFit="cover"
        />
      ) : (
        <div className="avatar__placeholder">
          <Icon 
            name="user" 
            size={pixelSize * 0.6} 
          />
        </div>
      )}
    </div>
  );
};

export default Avatar;