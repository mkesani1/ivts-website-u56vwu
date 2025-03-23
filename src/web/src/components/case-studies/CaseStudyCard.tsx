import React from 'react';
import classNames from 'classnames'; // version 2.3.2
import Link from 'next/link'; // version 13.4.0

import { CaseStudy } from '../../types/content';
import Card from '../../components/ui/Card';
import Badge from '../../components/ui/Badge';
import Button from '../../components/ui/Button';
import ImageWithFallback from '../../components/shared/ImageWithFallback';
import { ROUTES } from '../../constants/routes';
import { Variant, Size } from '../../types/common';

/**
 * Props for the CaseStudyCard component
 */
export interface CaseStudyCardProps {
  /** Case study data to display */
  caseStudy: CaseStudy;
  /** Additional CSS class names */
  className?: string;
}

/**
 * Truncates text to a specified length and adds ellipsis if needed
 * @param text - The text to truncate
 * @param maxLength - Maximum allowed length
 * @returns Truncated text with ellipsis if needed
 */
const truncateText = (text: string, maxLength: number): string => {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength) + '...';
}

/**
 * A component that displays a case study in a card format with image, title, client, industry, and a brief description
 * 
 * This component is used throughout the IndiVillage website to highlight successful AI service implementations.
 * It presents key information about client case studies in a visually appealing, consistent format.
 */
const CaseStudyCard = ({ 
  caseStudy, 
  className,
  ...props
}: CaseStudyCardProps): JSX.Element => {
  // Extract case study details
  const { title, slug, client, industry, image, challenge } = caseStudy;
  
  // Generate the detail page URL
  const detailUrl = ROUTES.CASE_STUDIES.DETAIL.replace('[slug]', slug);
  
  // Create a truncated version of the challenge text for the card preview
  const truncatedChallenge = truncateText(challenge, 150);
  
  // Generate CSS classes for the component
  const cardClasses = classNames('case-study-card', className);
  
  return (
    <Card 
      variant={Variant.PRIMARY} 
      elevation={1}
      hoverable
      className={cardClasses}
      {...props}
    >
      <div className="case-study-card__image-container">
        <ImageWithFallback 
          src={image.url} 
          alt={image.title || title} 
          width={400}
          height={225}
          className="case-study-card__image"
          objectFit="cover"
        />
        
        {industry && (
          <Badge 
            variant={Variant.SECONDARY} 
            size={Size.SMALL}
            rounded
            className="case-study-card__industry-badge"
          >
            {industry.name}
          </Badge>
        )}
      </div>
      
      <div className="case-study-card__content">
        <div className="case-study-card__client">{client}</div>
        <h3 className="case-study-card__title">{title}</h3>
        <p className="case-study-card__excerpt">{truncatedChallenge}</p>
        
        <Link 
          href={detailUrl} 
          className="case-study-card__link"
          aria-label={`Read full case study about ${client}: ${title}`}
        >
          <Button 
            variant={Variant.SECONDARY} 
            size={Size.MEDIUM}
            icon="arrowRight"
            iconPosition="right"
          >
            Read Case Study
          </Button>
        </Link>
      </div>
    </Card>
  );
};

export default CaseStudyCard;