import React from 'react'; // version 18.2.0
import classNames from 'classnames'; // version 2.3.2
import { motion } from 'framer-motion'; // version 10.12+

import { ImpactStory as ImpactStoryType } from '../../types/content';
import Button from '../ui/Button';
import ImageWithFallback from '../shared/ImageWithFallback';
import SectionHeader from '../shared/SectionHeader';
import ImpactMetrics from './ImpactMetrics';
import SDGSection from './SDGSection';
import Carousel from '../shared/Carousel';
import useBreakpoint from '../../hooks/useBreakpoint';

/**
 * Props interface for the ImpactStory component
 */
interface ImpactStoryProps extends React.HTMLAttributes<HTMLElement> {
  /**
   * The impact story data to display
   */
  story: ImpactStoryType;
  
  /**
   * Optional CSS class name
   */
  className?: string;
}

/**
 * Component that displays a detailed view of an individual social impact story.
 * This component showcases how IndiVillage's AI services create positive social change,
 * featuring rich media, impact metrics, beneficiary information, and alignment with SDGs.
 */
const ImpactStory: React.FC<ImpactStoryProps> = ({
  story,
  className,
  ...rest
}) => {
  // Use breakpoint hook to determine current device size for responsive adjustments
  const breakpoint = useBreakpoint();
  const isMobile = breakpoint === 'mobileSmall' || breakpoint === 'mobile';
  
  // Extract story details
  const { 
    title, 
    story: storyContent, 
    beneficiaries, 
    location,
    media,
    metrics,
    sdgs 
  } = story;
  
  // Determine if we should use Carousel for multiple media or single image
  const hasMultipleMedia = media && media.length > 1;
  
  // Animation variants for entrance animations
  const fadeInVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.6 } }
  };
  
  // Animation variants with delay for staggered entrance
  const staggerVariants = (delay: number) => ({
    hidden: { opacity: 0, y: 20 },
    visible: { 
      opacity: 1, 
      y: 0, 
      transition: { 
        duration: 0.6, 
        delay 
      } 
    }
  });
  
  return (
    <article 
      className={classNames('impact-story', `impact-story--${breakpoint}`, className)}
      {...rest}
    >
      {/* Story header section */}
      <motion.header 
        className="impact-story__header"
        initial="hidden"
        animate="visible"
        variants={fadeInVariants}
      >
        <h1 className="impact-story__title">
          {title}
        </h1>
        
        {location && (
          <div className="impact-story__location">
            <span className="impact-story__location-label">Location: </span>
            {location.name}, {location.region}, {location.country}
          </div>
        )}
      </motion.header>
      
      {/* Media section */}
      <motion.section 
        className="impact-story__media"
        initial="hidden"
        animate="visible"
        variants={staggerVariants(0.2)}
      >
        {hasMultipleMedia ? (
          <Carousel
            autoPlay={true}
            interval={5000}
            showIndicators={true}
            showArrows={true}
          >
            {media.map((item) => (
              <div key={item.id} className="impact-story__media-item">
                <ImageWithFallback
                  src={item.url}
                  alt={item.title || item.description || title}
                  width={1200}
                  height={675}
                  className="impact-story__image"
                  priority={media.indexOf(item) === 0}
                />
                {item.description && (
                  <p className="impact-story__media-caption">{item.description}</p>
                )}
              </div>
            ))}
          </Carousel>
        ) : (
          media && media[0] && (
            <div className="impact-story__media-item">
              <ImageWithFallback
                src={media[0].url}
                alt={media[0].title || media[0].description || title}
                width={1200}
                height={675}
                className="impact-story__image"
                priority={true}
              />
              {media[0].description && (
                <p className="impact-story__media-caption">{media[0].description}</p>
              )}
            </div>
          )
        )}
      </motion.section>
      
      {/* Story content section */}
      <motion.section 
        className="impact-story__content"
        initial="hidden"
        animate="visible"
        variants={staggerVariants(0.3)}
      >
        <div 
          className="impact-story__text"
          dangerouslySetInnerHTML={{ __html: storyContent }}
        />
      </motion.section>
      
      {/* Beneficiaries section */}
      {beneficiaries && (
        <motion.section 
          className="impact-story__beneficiaries"
          initial="hidden"
          animate="visible"
          variants={staggerVariants(0.4)}
        >
          <SectionHeader
            title="Impact on Beneficiaries"
            align="left"
          />
          <div className="impact-story__beneficiaries-content">
            <p>{beneficiaries}</p>
          </div>
        </motion.section>
      )}
      
      {/* Impact metrics section */}
      {metrics && metrics.length > 0 && (
        <motion.section 
          className="impact-story__metrics"
          initial="hidden"
          animate="visible"
          variants={staggerVariants(0.5)}
        >
          <ImpactMetrics metrics={metrics} className="impact-story__metrics-component" />
        </motion.section>
      )}
      
      {/* SDGs section */}
      {sdgs && sdgs.length > 0 && (
        <motion.section 
          className="impact-story__sdgs"
          initial="hidden"
          animate="visible"
          variants={staggerVariants(0.6)}
        >
          {/* SDGSection component provides its own title "SUSTAINABLE DEVELOPMENT GOALS" */}
          <SDGSection className="impact-story__sdgs-component" />
        </motion.section>
      )}
      
      {/* Call to action section */}
      <motion.section 
        className="impact-story__cta"
        initial="hidden"
        animate="visible"
        variants={staggerVariants(0.7)}
      >
        <div className="impact-story__cta-container">
          <h2 className="impact-story__cta-title">Support Our Mission</h2>
          <p className="impact-story__cta-text">
            When you choose IndiVillage for your AI services, you directly contribute to 
            these impactful social initiatives. Join us in creating technology solutions 
            that transform lives.
          </p>
          <div className="impact-story__cta-buttons">
            <Button 
              variant="primary" 
              size={isMobile ? "medium" : "large"}
            >
              Become a Partner
            </Button>
            <Button 
              variant="secondary" 
              size={isMobile ? "medium" : "large"}
            >
              Learn More
            </Button>
          </div>
        </div>
      </motion.section>
    </article>
  );
};

export default ImpactStory;