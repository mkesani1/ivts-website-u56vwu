import React from 'react'; // version 18.2.0
import classNames from 'classnames'; // version 2.3.2
import Button from '../ui/Button';
import { AlignmentValue } from '../../types/common';

export interface SectionHeaderProps {
  /**
   * Main title of the section
   */
  title: string;
  
  /**
   * Optional subtitle text to display below the title
   */
  subtitle?: string;
  
  /**
   * Alignment of the header content
   * @default 'left'
   */
  align?: AlignmentValue;
  
  /**
   * Text for the optional action button
   */
  actionText?: string;
  
  /**
   * URL for the action button if it should act as a link
   * This is provided for reference, but navigation should be handled by the parent component
   */
  actionHref?: string;
  
  /**
   * Click handler for the action button
   */
  actionOnClick?: (event: React.MouseEvent<HTMLButtonElement>) => void;
  
  /**
   * HTML heading level to use for the title
   * @default 'h2'
   */
  headingLevel?: 'h1' | 'h2' | 'h3' | 'h4' | 'h5' | 'h6';
  
  /**
   * Additional CSS class names to apply to the container
   */
  className?: string;
}

/**
 * A reusable component that renders section headers with consistent styling.
 * Supports optional subtitles, alignment options, and action buttons to provide
 * a standardized way to introduce content sections throughout the IndiVillage website.
 * 
 * @example
 * // Basic usage
 * <SectionHeader title="Our Services" />
 * 
 * // With subtitle and centered alignment
 * <SectionHeader
 *   title="AI for Good: Our Impact"
 *   subtitle="Creating sustainable livelihoods through technology"
 *   align="center"
 * />
 * 
 * // With action button
 * <SectionHeader
 *   title="Ready to Transform Your Business?"
 *   actionText="Request Demo"
 *   actionOnClick={handleDemoRequest}
 * />
 */
const SectionHeader: React.FC<SectionHeaderProps> = ({
  title,
  subtitle,
  align = 'left',
  actionText,
  actionHref,
  actionOnClick,
  headingLevel = 'h2',
  className,
  ...rest
}) => {
  const headerClasses = classNames(
    'section-header',
    `section-header--${align}`,
    className
  );

  // Create the heading component based on headingLevel prop
  const Heading = headingLevel as keyof JSX.IntrinsicElements;
  
  // Generate unique ID for accessibility
  const titleId = React.useId();

  return (
    <header 
      className={headerClasses} 
      aria-labelledby={titleId}
      {...rest}
    >
      <div className="section-header__content">
        <Heading 
          id={titleId}
          className="section-header__title"
        >
          {title}
        </Heading>
        
        {subtitle && (
          <p className="section-header__subtitle">
            {subtitle}
          </p>
        )}
      </div>
      
      {actionText && (
        <div className="section-header__action">
          <Button 
            variant="primary" 
            size="medium"
            onClick={actionOnClick}
          >
            {actionText}
          </Button>
        </div>
      )}
    </header>
  );
};

export default SectionHeader;