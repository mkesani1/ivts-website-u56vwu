import React from 'react'; // version 18.2.0
import classNames from 'classnames'; // version 2.3.2
import SectionHeader from '../shared/SectionHeader';
import ImageWithFallback from '../shared/ImageWithFallback';
import Button from '../ui/Button';
import { ROUTES } from '../../constants/routes';

/**
 * Props interface for the MissionStatement component
 */
interface MissionStatementProps extends React.HTMLAttributes<HTMLElement> {
  /**
   * Additional CSS class name
   */
  className?: string;
}

/**
 * Component that displays IndiVillage's mission statement highlighting the company's 'AI for Good' initiative.
 * This component showcases how IndiVillage creates sustainable livelihoods through technology
 * while delivering exceptional AI services to global clients.
 * 
 * The layout is responsive:
 * - On mobile: Single column with image above text content
 * - On desktop: Two-column layout with image on left, text content on right
 */
const MissionStatement: React.FC<MissionStatementProps> = ({ 
  className,
  ...rest
}) => {
  // Combine CSS classes
  const sectionClasses = classNames(
    'mission-statement',
    className
  );

  // Handle navigation to the foundation page
  const handleLearnMoreClick = () => {
    window.location.href = ROUTES.IMPACT.FOUNDATION;
  };

  return (
    <section className={sectionClasses} {...rest}>
      <div className="mission-statement__container">
        <div className="mission-statement__grid">
          {/* Image column - ordered second on mobile, first on desktop */}
          <div className="mission-statement__image-column">
            <ImageWithFallback 
              src="/images/impact/community-impact.jpg"
              alt="IndiVillage community members working together on technology projects"
              width={560}
              height={420}
              className="mission-statement__image"
              priority
            />
          </div>
          
          {/* Content column - ordered first on mobile, second on desktop */}
          <div className="mission-statement__content-column">
            <SectionHeader
              title="OUR MISSION"
              align="left"
              headingLevel="h2"
            />
            
            <div className="mission-statement__text">
              <p className="mission-statement__primary-text">
                Creating sustainable livelihoods through technology while delivering exceptional 
                AI services to global clients.
              </p>
              
              <p className="mission-statement__secondary-text">
                At IndiVillage, we believe in the power of technology to transform lives. 
                Our unique "AI for Good" approach combines world-class AI solutions with 
                meaningful social impact in rural communities.
              </p>
            </div>
            
            <div className="mission-statement__action">
              <Button 
                variant="primary"
                size="medium"
                onClick={handleLearnMoreClick}
              >
                Learn About Our Foundation
              </Button>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default MissionStatement;