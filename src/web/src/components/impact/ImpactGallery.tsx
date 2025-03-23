import React from 'react'; // version 18.2.0
import classNames from 'classnames'; // version 2.3.2
import { motion } from 'framer-motion'; // version 10.12+
import Link from 'next/link'; // version 13.4+

import ImpactStory from './ImpactStory';
import Carousel from '../shared/Carousel';
import SectionHeader from '../shared/SectionHeader';
import { ImpactStory as ImpactStoryType } from '../../types/content';
import { ROUTES } from '../../constants/routes';
import useBreakpoint from '../../hooks/useBreakpoint';

/**
 * Props interface for the ImpactGallery component
 */
interface ImpactGalleryProps extends React.HTMLAttributes<HTMLDivElement> {
  /** Array of impact stories to display */
  stories: ImpactStoryType[];
  /** Optional section title */
  title?: string;
  /** Optional subtitle text */
  subtitle?: string;
  /** Optional additional CSS class */
  className?: string;
  /** Whether to show "See All" link */
  showAllLink?: boolean;
  /** Whether to use carousel layout instead of grid */
  useCarousel?: boolean;
  /** Whether to show impact metrics with the stories */
  showMetrics?: boolean;
  /** Whether these are featured stories */
  featured?: boolean;
}

/**
 * A component that displays a gallery of impact stories in a grid or carousel layout.
 * This component is used on the Social Impact page to showcase IndiVillage's
 * community initiatives and their positive outcomes.
 *
 * The layout adapts responsively between a grid for larger screens and a
 * carousel for mobile devices, providing an optimal viewing experience
 * across different devices.
 */
const ImpactGallery: React.FC<ImpactGalleryProps> = ({
  stories,
  title = 'Impact Stories',
  subtitle,
  className,
  showAllLink = true,
  useCarousel,
  showMetrics = false,
  featured = false,
  ...rest
}) => {
  // Use breakpoint hook to determine current device size for responsive adjustments
  const breakpoint = useBreakpoint();
  
  // Determine if carousel should be used based on both props and current breakpoint
  const isMobileOrTablet = breakpoint === 'mobileSmall' || breakpoint === 'mobile' || breakpoint === 'tablet';
  const shouldUseCarousel = useCarousel !== undefined ? useCarousel : isMobileOrTablet;
  
  // Calculate how many items to show in carousel based on breakpoint
  const itemsToShow = (() => {
    if (breakpoint === 'mobileSmall' || breakpoint === 'mobile') {
      return 1;
    } else if (breakpoint === 'tablet') {
      return 2;
    } else {
      return Math.min(3, stories.length);
    }
  })();
  
  // Determine if stories should be shown in compact mode based on count and layout
  const useCompactView = stories.length > 3 || shouldUseCarousel;
  
  // Combine CSS classes for the container
  const galleryClasses = classNames(
    'impact-gallery',
    `impact-gallery--${breakpoint}`,
    {
      'impact-gallery--featured': featured,
      'impact-gallery--carousel': shouldUseCarousel,
      'impact-gallery--grid': !shouldUseCarousel,
    },
    className
  );
  
  // Animation variants for staggered children
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
        delayChildren: 0.1
      }
    }
  };
  
  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { 
      opacity: 1, 
      y: 0,
      transition: { 
        duration: 0.5,
        ease: [0.25, 0.1, 0.25, 1.0]
      }
    }
  };
  
  return (
    <section 
      className={galleryClasses}
      aria-label={`${title} - Impact Gallery`}
      {...rest}
    >
      {/* Section header with title, subtitle, and optional "See All" link */}
      <SectionHeader
        title={title}
        subtitle={subtitle}
        align="center"
        actionText={showAllLink ? "See All Stories" : undefined}
        actionHref={showAllLink ? ROUTES.IMPACT.INDEX : undefined}
      />
      
      {/* Render either a carousel or grid based on layout decision */}
      {shouldUseCarousel ? (
        <Carousel
          autoPlay={true}
          interval={5000}
          showIndicators={true}
          showArrows={true}
          itemsToShow={itemsToShow}
          className="impact-gallery__carousel"
        >
          {stories.map((story) => (
            <div 
              key={story.id} 
              className="impact-gallery__item"
            >
              <ImpactStory
                story={story}
                compact={useCompactView}
                featured={featured}
                showMetrics={showMetrics}
              />
            </div>
          ))}
        </Carousel>
      ) : (
        <motion.div 
          className="impact-gallery__grid"
          role="list"
          initial="hidden"
          animate="visible"
          variants={containerVariants}
        >
          {stories.map((story) => (
            <motion.div
              key={story.id}
              className="impact-gallery__item"
              role="listitem"
              variants={itemVariants}
            >
              <ImpactStory
                story={story}
                compact={useCompactView}
                featured={featured}
                showMetrics={showMetrics}
              />
            </motion.div>
          ))}
        </motion.div>
      )}
    </section>
  );
};

export default ImpactGallery;