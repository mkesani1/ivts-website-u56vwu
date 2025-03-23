import React, { useState, useRef, useEffect } from 'react'; // version ^18.0.0
import Link from 'next/link'; // version ^13.0.0
import { useRouter } from 'next/router'; // version ^13.0.0
import classNames from 'classnames'; // version 2.3.2

import Button from '../ui/Button';
import Icon from '../ui/Icon';
import { ROUTES } from '../../constants/routes';

/**
 * Props for the Navigation component
 */
interface NavigationProps {
  className?: string;
}

/**
 * Structure for navigation items with potential dropdown children
 */
interface NavigationItem {
  label: string;
  path: string;
  exact?: boolean;
  children?: NavigationChild[];
}

/**
 * Structure for dropdown navigation items
 */
interface NavigationChild {
  label: string;
  path: string;
}

/**
 * Helper function to determine if a navigation link is active based on the current route
 */
const isActiveLink = (path: string, currentPath: string, exact: boolean = false): boolean => {
  if (exact) {
    return path === currentPath;
  }
  
  // Special case for home page
  if (path === ROUTES.HOME && currentPath !== ROUTES.HOME) {
    return false;
  }
  
  return currentPath.startsWith(path);
};

/**
 * The main navigation component that provides the primary navigation menu for desktop view
 * Implements the navigation structure defined in the technical specifications
 */
const Navigation: React.FC<NavigationProps> = ({ className }) => {
  // State to track which dropdown is active
  const [activeDropdown, setActiveDropdown] = useState<string | null>(null);
  
  // Ref for the navigation container to handle keyboard interactions
  const navRef = useRef<HTMLElement>(null);
  
  // Get current router path
  const router = useRouter();
  const currentPath = router.asPath;
  
  // Define navigation items based on the technical specifications
  const navigationItems: NavigationItem[] = [
    {
      label: 'Services',
      path: ROUTES.SERVICES.INDEX,
      children: [
        { label: 'Data Collection', path: ROUTES.SERVICES.DATA_COLLECTION },
        { label: 'Data Preparation', path: ROUTES.SERVICES.DATA_PREPARATION },
        { label: 'AI Model Development', path: ROUTES.SERVICES.AI_MODEL_DEVELOPMENT },
        { label: 'Human-in-the-Loop', path: ROUTES.SERVICES.HUMAN_IN_THE_LOOP },
      ]
    },
    {
      label: 'About Us',
      path: ROUTES.ABOUT.INDEX,
      children: [
        { label: 'Our Story', path: ROUTES.ABOUT.INDEX },
        { label: 'Leadership Team', path: ROUTES.ABOUT.LEADERSHIP },
        { label: 'Careers', path: ROUTES.ABOUT.CAREERS },
        { label: 'Press & Media', path: ROUTES.ABOUT.PRESS },
      ]
    },
    {
      label: 'Social Impact',
      path: ROUTES.IMPACT.INDEX,
      children: [
        { label: 'Our Mission', path: ROUTES.IMPACT.INDEX },
        { label: 'Impact Stories', path: ROUTES.IMPACT.INDEX + '#stories' },
        { label: 'Foundation', path: ROUTES.IMPACT.FOUNDATION },
        { label: 'Sustainability', path: ROUTES.IMPACT.SUSTAINABILITY },
      ]
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
  
  // Toggle dropdown visibility
  const toggleDropdown = (label: string) => {
    setActiveDropdown(activeDropdown === label ? null : label);
  };
  
  // Close dropdown when mouse leaves navigation
  const handleMouseLeave = () => {
    setActiveDropdown(null);
  };
  
  // Handle keyboard navigation within the dropdown menus
  const handleKeyDown = (e: React.KeyboardEvent, label: string) => {
    switch (e.key) {
      case 'Escape':
        setActiveDropdown(null);
        break;
      case 'Enter':
      case ' ':
        e.preventDefault();
        toggleDropdown(label);
        break;
      case 'ArrowDown':
        if (activeDropdown === label) {
          e.preventDefault();
          // Focus the first item in the dropdown
          const dropdown = navRef.current?.querySelector(`[data-dropdown="${label}"]`);
          const firstItem = dropdown?.querySelector('a') as HTMLElement;
          firstItem?.focus();
        }
        break;
    }
  };
  
  // Setup effect to close dropdowns when pressing Escape anywhere in the document
  useEffect(() => {
    const handleDocumentKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && activeDropdown) {
        setActiveDropdown(null);
      }
    };
    
    document.addEventListener('keydown', handleDocumentKeyDown);
    
    return () => {
      document.removeEventListener('keydown', handleDocumentKeyDown);
    };
  }, [activeDropdown]);
  
  return (
    <nav 
      ref={navRef}
      className={classNames('navigation', className)}
      onMouseLeave={handleMouseLeave}
      aria-label="Main Navigation"
    >
      <ul className="navigation__list">
        {navigationItems.map((item) => {
          const isActive = isActiveLink(item.path, currentPath, item.exact);
          const hasDropdown = !!item.children?.length;
          const isDropdownOpen = activeDropdown === item.label;
          
          return (
            <li 
              key={item.label} 
              className={classNames('navigation__item', {
                'navigation__item--active': isActive,
                'navigation__item--has-dropdown': hasDropdown,
                'navigation__item--dropdown-open': isDropdownOpen
              })}
            >
              {hasDropdown ? (
                <>
                  <button
                    className={classNames('navigation__dropdown-trigger', {
                      'navigation__dropdown-trigger--active': isActive
                    })}
                    onClick={() => toggleDropdown(item.label)}
                    onKeyDown={(e) => handleKeyDown(e, item.label)}
                    aria-expanded={isDropdownOpen}
                    aria-haspopup="true"
                  >
                    {item.label}
                    <Icon 
                      name="arrowRight" 
                      size="small" 
                      className={classNames('navigation__dropdown-icon', {
                        'navigation__dropdown-icon--open': isDropdownOpen
                      })}
                    />
                  </button>
                  {isDropdownOpen && (
                    <ul 
                      className="navigation__dropdown"
                      data-dropdown={item.label}
                      role="menu"
                      aria-label={`${item.label} submenu`}
                    >
                      {item.children!.map((child) => (
                        <li key={child.label} className="navigation__dropdown-item" role="none">
                          <Link
                            href={child.path}
                            className={classNames('navigation__dropdown-link', {
                              'navigation__dropdown-link--active': isActiveLink(child.path, currentPath, true)
                            })}
                            role="menuitem"
                          >
                            {child.label}
                          </Link>
                        </li>
                      ))}
                    </ul>
                  )}
                </>
              ) : (
                <Link 
                  href={item.path}
                  className={classNames('navigation__link', {
                    'navigation__link--active': isActive
                  })}
                >
                  {item.label}
                </Link>
              )}
            </li>
          );
        })}
      </ul>
      
      <div className="navigation__cta">
        <Link href={ROUTES.REQUEST_DEMO} legacyBehavior passHref>
          <a>
            <Button 
              variant="secondary" 
              size="small"
            >
              Request Demo
            </Button>
          </a>
        </Link>
      </div>
    </nav>
  );
};

export default Navigation;