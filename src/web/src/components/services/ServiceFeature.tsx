import React from 'react';
import Image from 'next/image';
import classNames from 'classnames';
import { motion } from 'framer-motion';
import Icon from '../ui/Icon';
import { ServiceFeature as ServiceFeatureType } from '../../types/content';
import { useFadeIn } from '../../utils/animations';
import { IconName, SizeValue } from '../../types/common';

/**
 * Interface defining the props for the ServiceFeature component
 */
export interface ServiceFeatureProps {
  feature: ServiceFeatureType;
  className?: string;
}

/**
 * Component that displays a service feature with icon, title, and description
 * Used within the ServiceDetail component to showcase the key capabilities of each service offering
 * 
 * @param {ServiceFeatureProps} props - The component props
 * @returns {JSX.Element} - Rendered service feature component
 */
const ServiceFeature: React.FC<ServiceFeatureProps> = ({ 
  feature, 
  className 
}) => {
  // Get animation properties from useFadeIn hook for fade-in animation
  const { ref, style } = useFadeIn({
    duration: 300, // Standard transition duration from design system
    delay: 100,
    translateY: 10
  });

  // Determine if feature has a custom icon from CMS or should use a default icon
  const hasCustomIcon = feature.icon && feature.icon.url;
  
  // Determine default icon name based on feature content for fallback
  let defaultIconName: IconName = 'check';
  
  // Map feature title to appropriate icon name
  if (feature.title.toLowerCase().includes('collection')) {
    defaultIconName = 'dataCollection';
  } else if (feature.title.toLowerCase().includes('preparation')) {
    defaultIconName = 'dataPreparation';
  } else if (feature.title.toLowerCase().includes('model')) {
    defaultIconName = 'aiModel';
  } else if (feature.title.toLowerCase().includes('human')) {
    defaultIconName = 'humanInTheLoop';
  }

  return (
    <motion.div 
      ref={ref}
      style={style}
      className={classNames(
        // Base styles
        'bg-white rounded-lg p-6 shadow-md hover:shadow-lg transition-shadow duration-300',
        'flex flex-col items-start',
        // Responsive classes based on breakpoints from Technical Specifications/7.12 RESPONSIVE BREAKPOINTS
        'w-full sm:w-1/2 lg:w-1/4',
        className
      )}
      aria-labelledby={`feature-title-${feature.id}`}
    >
      {/* Feature icon - either custom from CMS or default icon */}
      <div className="mb-4 text-primary">
        {hasCustomIcon ? (
          <Image 
            src={feature.icon.url}
            alt={feature.icon.title || `${feature.title} icon`}
            width={48}
            height={48}
            className="rounded-md"
          />
        ) : (
          <Icon 
            name={defaultIconName}
            size={'large' as SizeValue}
            color="#0055A4" // Primary blue from design system color palette
          />
        )}
      </div>
      
      {/* Feature title */}
      <h3 
        id={`feature-title-${feature.id}`}
        className="text-xl font-semibold mb-2 text-gray-900"
      >
        {feature.title}
      </h3>
      
      {/* Feature description */}
      <p className="text-gray-700">
        {feature.description}
      </p>
    </motion.div>
  );
};

export default ServiceFeature;