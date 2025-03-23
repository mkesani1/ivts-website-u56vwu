import React, { useState, useEffect, useRef } from 'react'; // version ^18.0.0
import Link from 'next/link'; // version ^13.0.0
import { useRouter } from 'next/router'; // version ^13.0.0
import classNames from 'classnames'; // version 2.3.2

import Button from '../ui/Button';
import Icon from '../ui/Icon';
import { ROUTES } from '../../constants/routes';

/**
 * Props for the MobileNavigation component
 */
interface MobileNavigationProps {
  /** Whether the mobile navigation is open */
  isOpen: boolean;
  /** Function to close the mobile navigation */
  onClose: () => void;
}

/**
 * Structure for navigation items with potential dropdown children
 */
interface NavigationItem {
  /** Display label for the navigation item */
  label: string;
  /** URL path for the navigation item */
  path: string;
  /** Whether to match the path exactly for active state */
  exact?: boolean;
  /** Nested navigation items */
  children?: NavigationChild[];
}

/**
 * Structure for dropdown navigation items
 */
interface NavigationChild {
  /** Display label for the child navigation item */
  label: string;
  /** URL path for the child navigation item */
  path: string;
}

/**
 * The mobile navigation component that provides a responsive menu for smaller screen sizes
 */
const MobileNavigation: React.FC<MobileNavigationProps> = ({ isOpen, onClose }) => {
  // State to track which dropdown sections are open
  const [activeDropdowns, setActiveDropdowns] = useState<string[]>([]);
  
  // Reference to the navigation container element
  const navRef = useRef<HTMLDivElement>(null);
  
  // Close button reference for initial focus
  const closeButtonRef = useRef<HTMLButtonElement>(null);
  
  // Get current router instance to determine active route
  const router = useRouter();

  // Define the navigation items with their routes and children
  const navigationItems: NavigationItem[] = [
    {
      label: 'Services',
      path: ROUTES.SERVICES.INDEX,
      children: [
        { label: 'Data Collection', path: ROUTES.SERVICES.DATA_COLLECTION },
        { label: 'Data Preparation', path: ROUTES.SERVICES.DATA_PREPARATION },
        { label: 'AI Model Development', path: ROUTES.SERVICES.AI_MODEL_DEVELOPMENT },
        { label: 'Human-in-the-Loop', path: ROUTES.SERVICES.HUMAN_IN_THE_LOOP },
      ],
    },
    {
      label: 'About Us',
      path: ROUTES.ABOUT.INDEX,
      children: [
        { label: 'Our Story', path: ROUTES.ABOUT.INDEX },
        { label: 'Leadership Team', path: ROUTES.ABOUT.LEADERSHIP },
        { label: 'Careers', path: ROUTES.ABOUT.CAREERS },
        { label: 'Press & Media', path: ROUTES.ABOUT.PRESS },
      ],
    },
    {
      label: 'Social Impact',
      path: ROUTES.IMPACT.INDEX,
      children: [
        { label: 'Our Mission', path: ROUTES.IMPACT.INDEX },
        { label: 'Impact Stories', path: ROUTES.IMPACT.INDEX + '#stories' },
        { label: 'Foundation', path: ROUTES.IMPACT.FOUNDATION },
        { label: 'Sustainability', path: ROUTES.IMPACT.SUSTAINABILITY },
      ],
    },
    {
      label: 'Case Studies',
      path: ROUTES.CASE_STUDIES.INDEX,
      exact: true,
    },
    {
      label: 'Blog',
      path: ROUTES.BLOG.INDEX,
      exact: true,
    },
    {
      label: 'Contact',
      path: ROUTES.CONTACT,
      exact: true,
    },
  ];
  
  // Function to toggle dropdown visibility
  const toggleDropdown = (label: string) => {
    setActiveDropdowns(prev => 
      prev.includes(label) 
        ? prev.filter(item => item !== label) 
        : [...prev, label]
    );
  };
  
  // Handle keyboard navigation
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape') {
      onClose();
    }
  };
  
  // Set focus to close button when menu opens
  useEffect(() => {
    if (isOpen && closeButtonRef.current) {
      closeButtonRef.current.focus();
    }
  }, [isOpen]);
  
  // Add event listener for escape key
  useEffect(() => {
    const handleEscKey = (e: KeyboardEvent) => {
      if (isOpen && e.key === 'Escape') {
        onClose();
      }
    };
    
    document.addEventListener('keydown', handleEscKey);
    
    return () => {
      document.removeEventListener('keydown', handleEscKey);
    };
  }, [isOpen, onClose]);
  
  // Helper function to determine if a navigation link is active based on the current route
  const isActiveLink = (path: string, currentPath: string, exact = false): boolean => {
    if (exact) {
      return path === currentPath;
    }
    
    // Special case for home page
    if (path === ROUTES.HOME) {
      return currentPath === ROUTES.HOME;
    }
    
    return currentPath.startsWith(path);
  };
  
  // Don't render anything if the menu is closed
  if (!isOpen) {
    return null;
  }
  
  return (
    <div 
      className="mobile-nav-overlay"
      onClick={(e) => {
        // Close menu when clicking on the overlay background
        if (e.target === e.currentTarget) {
          onClose();
        }
      }}
      data-testid="mobile-nav-overlay"
    >
      <div 
        ref={navRef}
        className="mobile-nav"
        aria-modal="true"
        role="dialog"
        aria-label="Mobile navigation menu"
        onKeyDown={handleKeyDown}
      >
        <div className="mobile-nav__header">
          <button 
            ref={closeButtonRef}
            className="mobile-nav__close"
            onClick={onClose}
            aria-label="Close navigation menu"
            data-testid="mobile-nav-close"
          >
            <Icon name="close" size={24} />
          </button>
        </div>
        
        <nav aria-label="Mobile navigation">
          <ul className="mobile-nav__list">
            {navigationItems.map((item) => {
              const hasChildren = !!item.children?.length;
              const isActive = isActiveLink(item.path, router.pathname, item.exact);
              const isDropdownOpen = activeDropdowns.includes(item.label);
              const dropdownId = `dropdown-${item.label.toLowerCase().replace(/\s+/g, '-')}`;
              
              return (
                <li 
                  key={item.label} 
                  className={classNames('mobile-nav__item', {
                    'mobile-nav__item--active': isActive,
                    'mobile-nav__item--has-children': hasChildren,
                    'mobile-nav__item--open': isDropdownOpen,
                  })}
                >
                  {hasChildren ? (
                    <>
                      <button
                        className="mobile-nav__dropdown-trigger"
                        onClick={() => toggleDropdown(item.label)}
                        aria-expanded={isDropdownOpen}
                        aria-controls={dropdownId}
                      >
                        {item.label}
                        <Icon 
                          name="arrowRight" 
                          size={16} 
                          className={classNames('mobile-nav__dropdown-icon', {
                            'mobile-nav__dropdown-icon--open': isDropdownOpen
                          })}
                        />
                      </button>
                      
                      <ul 
                        id={dropdownId}
                        className={classNames('mobile-nav__dropdown', {
                          'mobile-nav__dropdown--open': isDropdownOpen
                        })}
                      >
                        {item.children?.map((child) => (
                          <li key={child.label} className="mobile-nav__dropdown-item">
                            <Link 
                              href={child.path}
                              className={classNames('mobile-nav__dropdown-link', {
                                'mobile-nav__dropdown-link--active': isActiveLink(child.path, router.pathname, true)
                              })}
                              onClick={onClose}
                            >
                              {child.label}
                            </Link>
                          </li>
                        ))}
                      </ul>
                    </>
                  ) : (
                    <Link 
                      href={item.path}
                      className={classNames('mobile-nav__link', {
                        'mobile-nav__link--active': isActive
                      })}
                      onClick={onClose}
                    >
                      {item.label}
                    </Link>
                  )}
                </li>
              );
            })}
          </ul>
        </nav>
        
        <div className="mobile-nav__actions">
          <Button 
            variant="primary"
            size="medium"
            fullWidth
            onClick={() => {
              router.push(ROUTES.REQUEST_DEMO);
              onClose();
            }}
          >
            Request Demo
          </Button>
          <div className="mobile-nav__action-spacer"></div>
          <Button 
            variant="secondary"
            size="medium"
            fullWidth
            onClick={() => {
              router.push(ROUTES.UPLOAD_SAMPLE.INDEX);
              onClose();
            }}
          >
            Upload Sample Data
          </Button>
        </div>
      </div>
    </div>
  );
};

export default MobileNavigation;