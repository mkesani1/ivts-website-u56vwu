import React, { useState, useEffect, useRef, useCallback } from 'react'; // version 18.2.0
import classNames from 'classnames'; // version 2.3.2

import Button from './Button';
import Icon from './Icon';
import useClickOutside from '../../hooks/useClickOutside';
import useKeyPress from '../../hooks/useKeyPress';
import { Size, SizeValue } from '../../types/common';
import { trapFocus, manageFocus, setAriaAttributes } from '../../utils/accessibility';
import { ANIMATION_DURATIONS, prefersReducedMotion } from '../../utils/animations';

/**
 * Props for the Modal component
 */
export interface ModalProps {
  /**
   * Controls whether the modal is displayed
   */
  isOpen: boolean;
  
  /**
   * Callback function called when the modal should close
   */
  onClose: () => void;
  
  /**
   * Title displayed in the modal header
   */
  title?: string;
  
  /**
   * Content to be displayed within the modal
   */
  children: React.ReactNode;
  
  /**
   * Size of the modal. Defaults to medium
   */
  size?: SizeValue;
  
  /**
   * Whether to close the modal when clicking outside. Defaults to true
   */
  closeOnClickOutside?: boolean;
  
  /**
   * Whether to close the modal when the Escape key is pressed. Defaults to true
   */
  closeOnEscape?: boolean;
  
  /**
   * Whether to show the close button in the modal header. Defaults to true
   */
  showCloseButton?: boolean;
  
  /**
   * Additional CSS class names to apply to the modal
   */
  className?: string;
  
  /**
   * ID of the element that labels the modal for accessibility
   */
  ariaLabelledBy?: string;
}

/**
 * Determines the CSS class for modal size based on the size prop
 * @param size - The size value for the modal
 * @returns The CSS class name for the specified size
 */
const getModalSizeClass = (size?: SizeValue): string => {
  switch (size) {
    case Size.SMALL:
      return 'modal-sm';
    case Size.LARGE:
      return 'modal-lg';
    case Size.MEDIUM:
    default:
      return 'modal-md';
  }
};

/**
 * A reusable modal component that displays content in an overlay with a backdrop.
 * Supports customizable sizes, accessibility features, and animations.
 */
const Modal: React.FC<ModalProps> = ({
  isOpen,
  onClose,
  title,
  children,
  size = Size.MEDIUM,
  closeOnClickOutside = true,
  closeOnEscape = true,
  showCloseButton = true,
  className,
  ariaLabelledBy,
  ...rest
}) => {
  // Reference to the modal content element
  const modalRef = useRef<HTMLDivElement>(null);
  
  // Animation state to handle entrance and exit animations
  const [animationState, setAnimationState] = useState<'entering' | 'entered' | 'exiting' | 'exited'>(
    isOpen ? 'entering' : 'exited'
  );
  
  // Flag to determine if animations should be disabled based on user preferences
  const disableAnimations = prefersReducedMotion();

  // Handle body scroll locking when modal is open
  useEffect(() => {
    if (isOpen) {
      // Lock body scroll when modal is open
      document.body.style.overflow = 'hidden';
      
      // Update animation state
      setAnimationState('entering');
      
      // After entering animation completes, update state to entered
      const enteringTimeout = setTimeout(() => {
        setAnimationState('entered');
      }, disableAnimations ? 0 : ANIMATION_DURATIONS.STANDARD);
      
      return () => {
        clearTimeout(enteringTimeout);
      };
    } else {
      // When modal closes, allow body to scroll again
      document.body.style.overflow = '';
      
      // If the modal was previously visible, animate exit
      if (animationState === 'entered' || animationState === 'entering') {
        setAnimationState('exiting');
        
        // After exiting animation completes, update state to exited
        const exitingTimeout = setTimeout(() => {
          setAnimationState('exited');
        }, disableAnimations ? 0 : ANIMATION_DURATIONS.STANDARD);
        
        return () => {
          clearTimeout(exitingTimeout);
        };
      }
    }
  }, [isOpen, disableAnimations, animationState]);

  // Handle focus management when modal opens/closes
  useEffect(() => {
    if (isOpen && modalRef.current) {
      // Focus on modal content
      const cleanup = manageFocus(
        modalRef.current.querySelector('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])') as HTMLElement || 
        modalRef.current
      );
      
      return () => {
        cleanup();
      };
    }
  }, [isOpen]);

  // Set up focus trapping within the modal
  useEffect(() => {
    if (isOpen && modalRef.current) {
      // Trap focus within the modal for keyboard navigation
      const cleanup = trapFocus(modalRef.current);
      
      return () => {
        cleanup();
      };
    }
  }, [isOpen]);

  // Set up click outside detection
  useClickOutside(
    modalRef,
    () => {
      if (closeOnClickOutside && isOpen) {
        handleClose();
      }
    },
    isOpen && closeOnClickOutside
  );

  // Set up escape key press detection
  useKeyPress(
    'Escape',
    () => {
      if (closeOnEscape && isOpen) {
        handleClose();
      }
    },
    { enabled: isOpen && closeOnEscape }
  );

  // Handle close action with animation
  const handleClose = useCallback(() => {
    // Start exit animation before closing
    setAnimationState('exiting');
    
    // Delay actual close callback until animation completes
    const exitTimeout = setTimeout(() => {
      onClose();
      setAnimationState('exited');
    }, disableAnimations ? 0 : ANIMATION_DURATIONS.STANDARD);
    
    return () => {
      clearTimeout(exitTimeout);
    };
  }, [onClose, disableAnimations]);

  // Don't render anything if the modal is not open and not animating
  if (!isOpen && animationState === 'exited') {
    return null;
  }

  // Generate modal size class
  const sizeClass = getModalSizeClass(size);
  
  // Generate class names for modal components
  const modalContainerClasses = classNames(
    'modal-container',
    {
      'modal-container--entering': animationState === 'entering',
      'modal-container--entered': animationState === 'entered',
      'modal-container--exiting': animationState === 'exiting',
    }
  );
  
  const modalContentClasses = classNames(
    'modal',
    sizeClass,
    className
  );

  // Generate unique ID for modal header if not provided
  const headerId = ariaLabelledBy || 'modal-header';

  return (
    <div 
      className={modalContainerClasses}
      role="dialog"
      aria-modal="true"
      aria-labelledby={headerId}
      {...rest}
    >
      {/* Modal backdrop */}
      <div className="modal-backdrop" />
      
      {/* Modal content */}
      <div 
        className={modalContentClasses}
        ref={modalRef}
      >
        {/* Modal header */}
        <div className="modal-header" id={headerId}>
          {title && <h2 className="modal-title">{title}</h2>}
          
          {/* Close button */}
          {showCloseButton && (
            <Button
              variant="tertiary"
              className="modal-close"
              onClick={handleClose}
              aria-label="Close modal"
            >
              <Icon name="close" />
            </Button>
          )}
        </div>
        
        {/* Modal body */}
        <div className="modal-body">
          {children}
        </div>
      </div>
    </div>
  );
};

export default Modal;