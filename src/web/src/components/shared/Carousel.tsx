import React, { useState, useEffect, useCallback, useRef } from 'react'; // version 18.2.0
import classNames from 'classnames'; // version 2.3.2

import Button from '../ui/Button';
import Icon from '../ui/Icon';
import useIntersectionObserver from '../../hooks/useIntersectionObserver';
import useKeyPress from '../../hooks/useKeyPress';
import useBreakpoint from '../../hooks/useBreakpoint';
import { setAriaAttributes } from '../../utils/accessibility';

/**
 * Props for the Carousel component
 */
export interface CarouselProps {
  /**
   * The content to display in the carousel (typically a collection of elements)
   */
  children: React.ReactNode;
  
  /**
   * Whether the carousel should automatically rotate through items
   * @default false
   */
  autoPlay?: boolean;
  
  /**
   * Time in milliseconds between automatic slide transitions
   * @default 5000
   */
  interval?: number;
  
  /**
   * Whether to show indicator dots at the bottom of the carousel
   * @default true
   */
  showIndicators?: boolean;
  
  /**
   * Whether to show navigation arrows
   * @default true
   */
  showArrows?: boolean;
  
  /**
   * Number of items to show at once (will be adjusted for smaller screens)
   * @default 1
   */
  itemsToShow?: number;
  
  /**
   * Whether the carousel should loop infinitely
   * @default true
   */
  infiniteLoop?: boolean;
  
  /**
   * Additional className to apply to the carousel container
   */
  className?: string;
  
  /**
   * Function called when the active slide changes
   */
  onSlideChange?: (index: number) => void;
}

/**
 * Calculates the width of each carousel item based on the current breakpoint
 * 
 * @param breakpoint - Current responsive breakpoint
 * @param itemsToShow - Configured number of items to show
 * @returns The calculated width as a percentage string
 */
const getCarouselItemWidth = (breakpoint: string, itemsToShow: number): string => {
  let itemsPerView = itemsToShow;
  
  // Adjust items per view based on breakpoint
  if (breakpoint === 'mobileSmall' || breakpoint === 'mobile') {
    itemsPerView = 1; // Show only 1 item on mobile
  } else if (breakpoint === 'tablet') {
    itemsPerView = Math.min(2, itemsToShow); // Max 2 items on tablet
  }
  
  // Calculate width as a percentage
  const width = 100 / itemsPerView;
  return `${width}%`;
};

/**
 * A reusable carousel/slider component that allows users to navigate through a collection of content items.
 * Supports automatic rotation, manual navigation, responsive behavior, and accessibility features.
 * 
 * @example
 * ```tsx
 * <Carousel autoPlay showIndicators showArrows>
 *   <div>Slide 1</div>
 *   <div>Slide 2</div>
 *   <div>Slide 3</div>
 * </Carousel>
 * ```
 */
const Carousel: React.FC<CarouselProps> = ({
  children,
  autoPlay = false,
  interval = 5000,
  showIndicators = true,
  showArrows = true,
  itemsToShow = 1,
  infiniteLoop = true,
  className,
  onSlideChange,
}) => {
  // Get array of child elements
  const childrenArray = React.Children.toArray(children);
  const totalSlides = childrenArray.length;
  
  // State for tracking the current slide index
  const [currentSlide, setCurrentSlide] = useState(0);
  
  // State for tracking drag interactions
  const [isDragging, setIsDragging] = useState(false);
  const [dragStartX, setDragStartX] = useState(0);
  const [dragCurrentX, setDragCurrentX] = useState(0);
  
  // Refs for carousel elements and timers
  const carouselRef = useRef<HTMLDivElement>(null);
  const autoPlayTimerRef = useRef<NodeJS.Timeout | null>(null);
  
  // Get current breakpoint for responsive behavior
  const breakpoint = useBreakpoint();
  
  // Calculate item width based on current breakpoint and configuration
  const itemWidth = getCarouselItemWidth(breakpoint, itemsToShow);
  
  // Use IntersectionObserver to detect when carousel is visible
  const [containerRef, isInView] = useIntersectionObserver<HTMLDivElement>({
    threshold: 0.1, // Trigger when at least 10% of the carousel is visible
  });
  
  // Function to go to a specific slide
  const goToSlide = useCallback((index: number) => {
    let slideIndex = index;
    
    // Handle infinite loop logic
    if (infiniteLoop) {
      if (index < 0) {
        slideIndex = totalSlides - 1;
      } else if (index >= totalSlides) {
        slideIndex = 0;
      }
    } else {
      // Constrain within bounds if not infinite loop
      slideIndex = Math.max(0, Math.min(index, totalSlides - 1));
    }
    
    // Update current slide state
    setCurrentSlide(slideIndex);
    
    // Call onSlideChange callback if provided
    if (onSlideChange) {
      onSlideChange(slideIndex);
    }
  }, [totalSlides, infiniteLoop, onSlideChange]);
  
  // Function to go to the next slide
  const nextSlide = useCallback(() => {
    goToSlide(currentSlide + 1);
  }, [currentSlide, goToSlide]);
  
  // Function to go to the previous slide
  const prevSlide = useCallback(() => {
    goToSlide(currentSlide - 1);
  }, [currentSlide, goToSlide]);
  
  // Handle auto-rotation with useEffect
  useEffect(() => {
    // Only auto-rotate if autoPlay is enabled, the carousel is in view, and not being dragged
    if (autoPlay && isInView && !isDragging && totalSlides > 1) {
      // Clear any existing timer
      if (autoPlayTimerRef.current) {
        clearTimeout(autoPlayTimerRef.current);
      }
      
      // Set up new timer for auto-rotation
      autoPlayTimerRef.current = setTimeout(() => {
        nextSlide();
      }, interval);
    }
    
    // Clean up timer on unmount or dependencies change
    return () => {
      if (autoPlayTimerRef.current) {
        clearTimeout(autoPlayTimerRef.current);
      }
    };
  }, [autoPlay, interval, isInView, isDragging, nextSlide, totalSlides]);
  
  // Set up keyboard navigation with arrow keys
  useKeyPress('ArrowLeft', () => {
    // Only respond to key press if carousel is in view
    if (isInView) {
      prevSlide();
    }
  }, { 
    enabled: isInView && showArrows,
    preventDefault: true 
  });
  
  useKeyPress('ArrowRight', () => {
    // Only respond to key press if carousel is in view
    if (isInView) {
      nextSlide();
    }
  }, { 
    enabled: isInView && showArrows,
    preventDefault: true 
  });
  
  // Mouse and touch event handlers for drag functionality
  const handleMouseDown = (e: React.MouseEvent<HTMLDivElement>) => {
    setIsDragging(true);
    setDragStartX(e.clientX);
    setDragCurrentX(e.clientX);
  };
  
  const handleTouchStart = (e: React.TouchEvent<HTMLDivElement>) => {
    setIsDragging(true);
    setDragStartX(e.touches[0].clientX);
    setDragCurrentX(e.touches[0].clientX);
  };
  
  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (isDragging) {
      setDragCurrentX(e.clientX);
    }
  };
  
  const handleTouchMove = (e: React.TouchEvent<HTMLDivElement>) => {
    if (isDragging) {
      setDragCurrentX(e.touches[0].clientX);
    }
  };
  
  const handleDragEnd = () => {
    if (isDragging) {
      const dragDistance = dragCurrentX - dragStartX;
      const threshold = 50; // Minimum drag distance to trigger slide change
      
      if (dragDistance > threshold) {
        prevSlide(); // Dragged right, go to previous slide
      } else if (dragDistance < -threshold) {
        nextSlide(); // Dragged left, go to next slide
      }
      
      setIsDragging(false);
    }
  };
  
  // Render indicators (dots) for the carousel
  const renderIndicators = () => {
    if (!showIndicators || totalSlides <= 1) return null;
    
    return (
      <div className="carousel__indicators" role="tablist">
        {Array.from({ length: totalSlides }).map((_, index) => (
          <button
            key={`indicator-${index}`}
            className={classNames('carousel__indicator', {
              'carousel__indicator--active': index === currentSlide,
            })}
            onClick={() => goToSlide(index)}
            aria-label={`Go to slide ${index + 1}`}
            aria-selected={index === currentSlide ? 'true' : 'false'}
            role="tab"
            tabIndex={index === currentSlide ? 0 : -1}
          />
        ))}
      </div>
    );
  };
  
  // Render navigation arrows
  const renderArrows = () => {
    if (!showArrows || totalSlides <= 1) return null;
    
    return (
      <>
        <Button
          className="carousel__arrow carousel__arrow--prev"
          onClick={prevSlide}
          aria-label="Previous slide"
          icon="arrowLeft"
          variant="secondary"
          size="small"
          disabled={!infiniteLoop && currentSlide === 0}
        />
        <Button
          className="carousel__arrow carousel__arrow--next"
          onClick={nextSlide}
          aria-label="Next slide"
          icon="arrowRight"
          variant="secondary"
          size="small"
          disabled={!infiniteLoop && currentSlide === totalSlides - 1}
        />
      </>
    );
  };
  
  // Calculate drag offset for smooth dragging
  const dragOffset = isDragging ? dragCurrentX - dragStartX : 0;
  
  // Calculate transform style for slide positioning
  const slideStyle = {
    transform: `translateX(calc(-${currentSlide * 100}% + ${dragOffset}px))`,
    transition: isDragging ? 'none' : 'transform 0.3s ease',
  };
  
  // Combine class names
  const carouselClasses = classNames(
    'carousel',
    `carousel--items-${Math.min(itemsToShow, totalSlides)}`,
    `carousel--breakpoint-${breakpoint}`,
    {
      'carousel--dragging': isDragging,
    },
    className
  );
  
  // Combine refs
  const combinedRef = (node: HTMLDivElement) => {
    // Apply to both refs
    containerRef.current = node;
    carouselRef.current = node;
  };
  
  // Apply accessibility attributes to carousel
  useEffect(() => {
    if (carouselRef.current) {
      setAriaAttributes(carouselRef.current, {
        'roledescription': 'carousel',
        'label': 'Content carousel'
      });
    }
  }, []);
  
  return (
    <div 
      ref={combinedRef}
      className={carouselClasses}
      role="region"
    >
      <div 
        className="carousel__container"
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleDragEnd}
        onMouseLeave={handleDragEnd}
        onTouchStart={handleTouchStart}
        onTouchMove={handleTouchMove}
        onTouchEnd={handleDragEnd}
      >
        <div 
          className="carousel__track"
          style={slideStyle}
          role="presentation"
        >
          {React.Children.map(children, (child, index) => (
            <div 
              className="carousel__item"
              style={{ width: itemWidth }}
              aria-hidden={index !== currentSlide ? 'true' : 'false'}
              role="tabpanel"
              id={`carousel-item-${index}`}
            >
              {child}
            </div>
          ))}
        </div>
        
        {renderArrows()}
      </div>
      
      {renderIndicators()}
    </div>
  );
};

export default Carousel;