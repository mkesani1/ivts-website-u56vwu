import React, { useRef, useEffect } from 'react'; // version 18.2.0
import classNames from 'classnames'; // version 2.3.2

import { Variant, VariantValue } from '../../types/common';
import { setAriaAttributes } from '../../utils/accessibility';

/**
 * Interface for Card component props
 */
export interface CardProps extends 
  Omit<React.HTMLAttributes<HTMLDivElement> & 
  React.ButtonHTMLAttributes<HTMLButtonElement>, 
  'onClick'> {
  /** Style variant of the card */
  variant?: VariantValue;
  /** Elevation level (affects shadow depth) */
  elevation?: number;
  /** Whether the card is clickable */
  clickable?: boolean;
  /** Whether the card has hover effects */
  hoverable?: boolean;
  /** Content to be rendered inside the card */
  children: React.ReactNode;
  /** Additional CSS classes to apply */
  className?: string;
  /** Click handler (required if clickable is true) */
  onClick?: (event: React.MouseEvent<HTMLElement>) => void;
}

/**
 * Generates CSS class names for the card based on its props
 */
const getCardClasses = (
  variant: VariantValue,
  elevation: number,
  clickable: boolean,
  hoverable: boolean,
  className?: string
): string => {
  // Define base card classes for all cards
  const baseClasses = 'card';
  
  // Add variant-specific classes
  const variantClass = `card--${variant}`;
  
  // Add elevation-specific classes for shadow depth
  const elevationClass = `card--elevation-${elevation}`;
  
  // Add conditional classes for interactive states
  const interactiveClasses = {
    'card--clickable': clickable,
    'card--hoverable': hoverable,
  };

  // Combine all classes including any custom className provided
  return classNames(
    baseClasses,
    variantClass,
    elevationClass,
    interactiveClasses,
    className
  );
};

/**
 * A customizable card component that serves as a container for various content types
 * throughout the IndiVillage website. Supports different variants, elevations, and 
 * interactive states.
 */
const Card = ({
  variant = Variant.PRIMARY,
  elevation = 1,
  clickable = false,
  hoverable = false,
  children,
  className,
  onClick,
  ...rest
}: CardProps): JSX.Element => {
  // Reference to the DOM element for setting ARIA attributes
  const cardRef = useRef<HTMLElement>(null);
  
  // Set ARIA attributes using the accessibility utility after component mounts
  useEffect(() => {
    if (cardRef.current) {
      const ariaAttributes: Record<string, string> = {};
      
      // Set appropriate ARIA attributes based on card properties
      if (clickable) {
        ariaAttributes.haspopup = 'false';
      }
      
      // Apply ARIA attributes using the utility function
      setAriaAttributes(cardRef.current, ariaAttributes);
    }
  }, [clickable]);

  // Generate card classes based on props
  const cardClasses = getCardClasses(variant, elevation, clickable, hoverable, className);

  // If card is clickable, render as a button, otherwise as a div
  if (clickable) {
    // Warning if clickable is true but no onClick handler is provided
    if (!onClick) {
      console.warn('Card is set as clickable but no onClick handler is provided.');
    }

    return (
      <button
        ref={cardRef as React.RefObject<HTMLButtonElement>}
        type="button"
        className={cardClasses}
        onClick={onClick}
        role="button"
        tabIndex={0}
        {...rest}
      >
        {children}
      </button>
    );
  }

  // Render as a standard div container when not clickable
  return (
    <div 
      ref={cardRef as React.RefObject<HTMLDivElement>}
      className={cardClasses} 
      {...rest}
    >
      {children}
    </div>
  );
};

export default Card;