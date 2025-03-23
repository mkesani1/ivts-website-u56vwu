import React, { useState, useEffect } from 'react'; // version ^18.0.0
import Link from 'next/link'; // version ^13.0.0
import classNames from 'classnames'; // version 2.3.2

import Navigation from './Navigation';
import MobileNavigation from './MobileNavigation';
import Button from '../ui/Button';
import Icon from '../ui/Icon';
import ImageWithFallback from '../shared/ImageWithFallback';
import { ROUTES } from '../../constants/routes';
import useBreakpoint from '../../hooks/useBreakpoint';
import { Breakpoint } from '../../types/common';

/**
 * Props for the Header component
 */
interface HeaderProps {
  /** Additional CSS class names for the header container */
  className?: string;
}

/**
 * The main header component that provides navigation, branding, and call-to-action elements.
 * Implements a responsive design that adapts based on screen size with appropriate
 * accessibility considerations.
 */
const Header: React.FC<HeaderProps> = ({ className }) => {
  // State to control mobile menu visibility
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  
  // Get current breakpoint for responsive behavior
  const breakpoint = useBreakpoint();
  
  // Function to toggle mobile menu
  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };
  
  // Function to close mobile menu
  const closeMobileMenu = () => {
    setIsMobileMenuOpen(false);
  };
  
  // Lock body scroll when mobile menu is open to prevent background scrolling
  useEffect(() => {
    if (isMobileMenuOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    
    return () => {
      document.body.style.overflow = '';
    };
  }, [isMobileMenuOpen]);
  
  // Close mobile menu when viewport size increases to desktop
  useEffect(() => {
    if ((breakpoint === Breakpoint.DESKTOP || breakpoint === Breakpoint.LARGE_DESKTOP) && isMobileMenuOpen) {
      closeMobileMenu();
    }
  }, [breakpoint, isMobileMenuOpen]);
  
  // Determine if we should show mobile navigation based on breakpoint
  const isMobileBreakpoint = breakpoint === Breakpoint.MOBILE || 
                             breakpoint === Breakpoint.MOBILE_SMALL || 
                             breakpoint === Breakpoint.TABLET;
  
  // Generate container class names
  const headerClasses = classNames(
    'header',
    {
      'header--mobile-menu-open': isMobileMenuOpen,
    },
    className
  );
  
  return (
    <header className={headerClasses} role="banner">
      <div className="header__container">
        {/* Logo with link to homepage */}
        <div className="header__logo">
          <Link href={ROUTES.HOME} aria-label="IndiVillage - Home">
            <ImageWithFallback
              src="/images/indivillage-logo.svg"
              alt="IndiVillage Logo"
              width={180}
              height={40}
              priority
            />
          </Link>
        </div>
        
        {/* Navigation section - desktop or mobile toggle */}
        <div className="header__navigation">
          {isMobileBreakpoint ? (
            // Mobile menu toggle button
            <button 
              className="header__mobile-toggle" 
              onClick={toggleMobileMenu}
              aria-expanded={isMobileMenuOpen}
              aria-controls="mobile-navigation"
              aria-label="Toggle navigation menu"
              data-testid="mobile-menu-toggle"
            >
              <Icon name="menu" size={24} />
              <span className="sr-only">Menu</span>
            </button>
          ) : (
            // Desktop navigation
            <Navigation className="header__desktop-nav" />
          )}
        </div>
        
        {/* Utility Navigation - CTA Buttons - only shown on desktop */}
        <div className="header__actions">
          {!isMobileBreakpoint && (
            <>
              <Link href={ROUTES.CONTACT} className="header__contact-link">
                Contact
              </Link>
              <Link href={ROUTES.REQUEST_DEMO} legacyBehavior passHref>
                <a>
                  <Button variant="primary" size="small">
                    Request Demo
                  </Button>
                </a>
              </Link>
            </>
          )}
        </div>
      </div>
      
      {/* Mobile Navigation - always rendered but visibility controlled by isOpen prop */}
      <MobileNavigation 
        isOpen={isMobileMenuOpen} 
        onClose={closeMobileMenu} 
      />
    </header>
  );
};

export default Header;