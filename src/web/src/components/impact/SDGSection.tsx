import React from 'react';
import classNames from 'classnames'; // version 2.3.2
import SectionHeader from '../shared/SectionHeader';
import Card from '../ui/Card';
import ImageWithFallback from '../shared/ImageWithFallback';
import Tooltip from '../ui/Tooltip';
import { SUSTAINABLE_DEVELOPMENT_GOALS } from '../../constants/impact';

/**
 * Props for the SDGSection component
 */
export interface SDGSectionProps {
  /**
   * Additional CSS class names for the section container
   */
  className?: string;
}

/**
 * Component that displays the Sustainable Development Goals (SDGs) that IndiVillage contributes to
 * as part of their social impact mission. Each SDG is presented with its icon, number, and name,
 * with the full description available in a tooltip on hover.
 * 
 * This component addresses the Social Impact Storytelling requirements by showcasing
 * IndiVillage's alignment with UN Sustainable Development Goals.
 */
const SDGSection: React.FC<SDGSectionProps> = ({ 
  className,
  ...props 
}) => {
  // Generate container class names combining base and custom classes
  const containerClasses = classNames('sdg-section', className);

  return (
    <section className={containerClasses} {...props}>
      {/* Section title */}
      <SectionHeader 
        title="SUSTAINABLE DEVELOPMENT GOALS" 
        align="center"
      />
      
      {/* Grid layout for SDG cards - responsive based on device breakpoints */}
      <div className="sdg-section__grid">
        {SUSTAINABLE_DEVELOPMENT_GOALS.map((sdg) => (
          <Card 
            key={sdg.id}
            variant="primary"
            elevation={1}
            className="sdg-section__card"
          >
            {/* Tooltip showing SDG description on hover */}
            <Tooltip
              content={
                <div className="sdg-section__tooltip">
                  <strong>SDG {sdg.number}: {sdg.name}</strong>
                  <p>{sdg.description}</p>
                </div>
              }
              position="top"
            >
              {/* SDG content with icon, number and name */}
              <div 
                className="sdg-section__sdg"
                aria-label={`SDG ${sdg.number}: ${sdg.name} - ${sdg.description}`}
              >
                {/* SDG icon */}
                <div className="sdg-section__icon">
                  <ImageWithFallback
                    src={sdg.icon}
                    alt={`SDG ${sdg.number} icon`}
                    width={64}
                    height={64}
                  />
                </div>
                {/* SDG number and name */}
                <div className="sdg-section__content">
                  <div className="sdg-section__number">
                    {sdg.number}
                  </div>
                  <div className="sdg-section__name">
                    {sdg.name}
                  </div>
                </div>
              </div>
            </Tooltip>
          </Card>
        ))}
      </div>
      
      {/* Brief explanation of SDGs relevance to IndiVillage's mission */}
      <div className="sdg-section__description">
        <p>
          IndiVillage aligns with the UN Sustainable Development Goals to create meaningful
          social impact through our business operations. These goals guide our efforts in
          creating sustainable livelihoods, providing quality education, promoting gender
          equality, and supporting economic growth in rural communities.
        </p>
      </div>
    </section>
  );
};

export default SDGSection;