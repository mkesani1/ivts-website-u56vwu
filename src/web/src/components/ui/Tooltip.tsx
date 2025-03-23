import React, { useState, useRef, useEffect, useCallback } from 'react'; // version 18.2.0
import classNames from 'classnames'; // version 2.3.2
import { Size, SizeValue } from '../../types/common';
import { setAriaAttributes } from '../../utils/accessibility';
import useClickOutside from '../../hooks/useClickOutside';
import useKeyPress from '../../hooks/useKeyPress';

/**
 * Interface for the tooltip position calculation result
 */
interface TooltipPosition {
  top: number;
  left: number;
  position: string;
}

/**
 * Props for the Tooltip component
 */
export interface TooltipProps {
  /** Content to display inside the tooltip */
  content: React.ReactNode;
  /** Element that triggers the tooltip */
  children: React.ReactNode;
  /** Position of the tooltip relative to the trigger element */
  position?: 'top' | 'right' | 'bottom' | 'left';
  /** Size of the tooltip */
  size?: SizeValue;
  /** How the tooltip is triggered */
  trigger?: 'hover' | 'click' | 'focus';
  /** Additional CSS class names */
  className?: string;
}

/**
 * Calculates the position of the tooltip based on the trigger element and preferred position
 * Adjusts position if tooltip would overflow viewport
 */
const getTooltipPosition = (
  triggerElement: HTMLElement,
  tooltipElement: HTMLElement,
  position: string
): TooltipPosition => {
  if (!triggerElement || !tooltipElement) {
    return { top: 0, left: 0, position };
  }

  const triggerRect = triggerElement.getBoundingClientRect();
  const tooltipRect = tooltipElement.getBoundingClientRect();
  
  // Calculate positions for all possible positions
  const positions = {
    top: {
      top: triggerRect.top - tooltipRect.height - 8,
      left: triggerRect.left + (triggerRect.width / 2) - (tooltipRect.width / 2),
      position: 'top'
    },
    right: {
      top: triggerRect.top + (triggerRect.height / 2) - (tooltipRect.height / 2),
      left: triggerRect.right + 8,
      position: 'right'
    },
    bottom: {
      top: triggerRect.bottom + 8,
      left: triggerRect.left + (triggerRect.width / 2) - (tooltipRect.width / 2),
      position: 'bottom'
    },
    left: {
      top: triggerRect.top + (triggerRect.height / 2) - (tooltipRect.height / 2),
      left: triggerRect.left - tooltipRect.width - 8,
      position: 'left'
    }
  };

  // Get initial position based on preferred position
  let result = positions[position as keyof typeof positions] || positions.top;
  
  // Check if tooltip would overflow viewport and adjust if necessary
  const viewport = {
    width: window.innerWidth,
    height: window.innerHeight
  };

  // Adjust for horizontal overflow
  if (result.left < 0) {
    // If it overflows on the left, try right position first, then adjust left position
    if (position === 'left') {
      result = positions.right;
    } else {
      result.left = 8;
    }
  } else if (result.left + tooltipRect.width > viewport.width) {
    // If it overflows on the right, try left position first, then adjust right-aligned
    if (position === 'right') {
      result = positions.left;
    } else {
      result.left = viewport.width - tooltipRect.width - 8;
    }
  }

  // Adjust for vertical overflow
  if (result.top < 0) {
    // If it overflows on the top, try bottom position first, then adjust top position
    if (position === 'top') {
      result = positions.bottom;
    } else {
      result.top = 8;
    }
  } else if (result.top + tooltipRect.height > viewport.height) {
    // If it overflows on the bottom, try top position first, then adjust bottom-aligned
    if (position === 'bottom') {
      result = positions.top;
    } else {
      result.top = viewport.height - tooltipRect.height - 8;
    }
  }

  // Return the adjusted position
  return result;
};

/**
 * A tooltip component that displays informational text when hovering over or focusing on an element.
 * Supports different positions, sizes, and can be triggered by hover, click, or focus events.
 */
const Tooltip = ({
  content,
  children,
  position = 'top',
  size = Size.MEDIUM,
  trigger = 'hover',
  className,
  ...rest
}: TooltipProps) => {
  // State to track if the tooltip is visible
  const [isVisible, setIsVisible] = useState(false);
  
  // Create refs for the tooltip and trigger elements
  const tooltipRef = useRef<HTMLDivElement>(null);
  const triggerRef = useRef<HTMLDivElement>(null);
  
  // Generate a unique ID for the tooltip
  const tooltipId = useRef(`tooltip-${Math.random().toString(36).substring(2, 9)}`).current;
  
  // Position the tooltip when it becomes visible
  const updateTooltipPosition = useCallback(() => {
    if (isVisible && tooltipRef.current && triggerRef.current) {
      const { top, left, position: finalPosition } = getTooltipPosition(
        triggerRef.current,
        tooltipRef.current,
        position
      );
      
      // Apply the calculated position to the tooltip element
      const tooltipElement = tooltipRef.current;
      tooltipElement.style.top = `${top}px`;
      tooltipElement.style.left = `${left}px`;
      
      // Update the position attribute for styling
      tooltipElement.setAttribute('data-position', finalPosition);
    }
  }, [isVisible, position]);
  
  // Update position when visibility or position changes
  useEffect(() => {
    if (isVisible) {
      // Use requestAnimationFrame to ensure the tooltip is rendered before calculating position
      requestAnimationFrame(updateTooltipPosition);
    }
  }, [isVisible, updateTooltipPosition]);
  
  // Handle repositioning on scroll and resize
  useEffect(() => {
    if (!isVisible) return;
    
    window.addEventListener('scroll', updateTooltipPosition);
    window.addEventListener('resize', updateTooltipPosition);
    
    return () => {
      window.removeEventListener('scroll', updateTooltipPosition);
      window.removeEventListener('resize', updateTooltipPosition);
    };
  }, [isVisible, updateTooltipPosition]);
  
  // Handle click outside for click-triggered tooltips
  useClickOutside(tooltipRef, () => {
    if (trigger === 'click' && isVisible) {
      setIsVisible(false);
    }
  }, isVisible && trigger === 'click');
  
  // Handle escape key press to close tooltip
  useKeyPress('Escape', () => {
    if (isVisible) {
      setIsVisible(false);
    }
  }, { enabled: isVisible });
  
  // Event handlers based on trigger type
  const handleTriggerEvents = (() => {
    switch (trigger) {
      case 'hover':
        return {
          onMouseEnter: () => setIsVisible(true),
          onMouseLeave: () => setIsVisible(false),
          onFocus: () => setIsVisible(true),
          onBlur: () => setIsVisible(false)
        };
      case 'click':
        return {
          onClick: (e: React.MouseEvent) => {
            e.stopPropagation();
            setIsVisible(!isVisible);
          }
        };
      case 'focus':
        return {
          onFocus: () => setIsVisible(true),
          onBlur: () => setIsVisible(false)
        };
      default:
        return {};
    }
  })();
  
  // Generate class names for the tooltip
  const tooltipClasses = classNames(
    'tooltip',
    `tooltip--${size}`,
    `tooltip--${position}`,
    {
      'tooltip--visible': isVisible
    },
    className
  );
  
  // Set appropriate ARIA attributes on the trigger element
  useEffect(() => {
    if (triggerRef.current) {
      // For hover and focus triggers, use aria-describedby
      if (trigger === 'hover' || trigger === 'focus') {
        setAriaAttributes(triggerRef.current, {
          'describedby': isVisible ? tooltipId : undefined
        });
      } 
      // For click triggers, use aria-expanded to indicate state
      else if (trigger === 'click') {
        setAriaAttributes(triggerRef.current, {
          'expanded': isVisible ? 'true' : 'false',
          'controls': tooltipId
        });
      }
    }
  }, [isVisible, tooltipId, trigger]);
  
  return (
    <div 
      className="tooltip-wrapper" 
      ref={triggerRef} 
      {...handleTriggerEvents}
      {...rest}
    >
      {children}
      
      {isVisible && (
        <div
          ref={tooltipRef}
          className={tooltipClasses}
          id={tooltipId}
          role="tooltip"
        >
          {content}
        </div>
      )}
    </div>
  );
};

export default Tooltip;