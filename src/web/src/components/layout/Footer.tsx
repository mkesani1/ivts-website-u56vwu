import React from 'react';
import classNames from 'classnames'; // version 2.3.2
import Link from 'next/link'; // version ^13.0.0
import Image from 'next/image'; // version ^13.0.0
import Icon from '../ui/Icon';
import { ROUTES } from '../../constants/routes';
import useBreakpoint from '../../hooks/useBreakpoint';
import { Breakpoint, IconName } from '../../types/common';

// Interfaces for component props and data structures
interface FooterProps {
  className?: string;
}

interface FooterSection {
  title: string;
  links: FooterLink[];
}

interface FooterLink {
  label: string;
  path: string;
  isExternal: boolean;
}

interface SocialLink {
  name: string;
  icon: string;
  url: string;
}

// Footer navigation sections displayed in the footer
const FOOTER_SECTIONS: FooterSection[] = [
  {
    title: 'Company',
    links: [
      { label: 'About Us', path: ROUTES.ABOUT.INDEX, isExternal: false },
      { label: 'Careers', path: ROUTES.ABOUT.CAREERS, isExternal: false },
      { label: 'Partners', path: '/about/partners', isExternal: false },
      { label: 'Press', path: ROUTES.ABOUT.PRESS, isExternal: false },
    ],
  },
  {
    title: 'Legal',
    links: [
      { label: 'Privacy Policy', path: ROUTES.LEGAL.PRIVACY_POLICY, isExternal: false },
      { label: 'Terms of Service', path: ROUTES.LEGAL.TERMS_OF_SERVICE, isExternal: false },
      { label: 'Cookie Policy', path: ROUTES.LEGAL.COOKIE_POLICY, isExternal: false },
      { label: 'Accessibility', path: ROUTES.LEGAL.ACCESSIBILITY, isExternal: false },
    ],
  },
  {
    title: 'Connect',
    links: [
      { label: 'Contact', path: ROUTES.CONTACT, isExternal: false },
      { label: 'Support', path: `${ROUTES.CONTACT}#support`, isExternal: false },
    ],
  },
];

// Social media links displayed in the footer
const SOCIAL_LINKS: SocialLink[] = [
  { name: 'LinkedIn', icon: 'linkedin', url: 'https://www.linkedin.com/company/indivillage' },
  { name: 'Twitter', icon: 'twitter', url: 'https://twitter.com/indivillage' },
  { name: 'Facebook', icon: 'facebook', url: 'https://www.facebook.com/indivillage' },
  { name: 'Instagram', icon: 'instagram', url: 'https://www.instagram.com/indivillage' },
];

/**
 * The main footer component that provides navigation links, branding, and social media connections
 * across all pages of the IndiVillage website.
 */
const Footer: React.FC<FooterProps> = ({ className }) => {
  const breakpoint = useBreakpoint();
  
  // Determine layout based on current breakpoint
  const isMobile = breakpoint === Breakpoint.MOBILE || breakpoint === Breakpoint.MOBILE_SMALL;
  const isTablet = breakpoint === Breakpoint.TABLET;
  
  return (
    <footer 
      className={classNames('footer bg-gray-900 text-white py-8 md:py-12', className)}
      role="contentinfo"
      aria-label="Site footer"
    >
      <div className="container mx-auto px-4">
        <div className={classNames(
          'footer-content grid gap-8',
          {
            'grid-cols-1': isMobile,
            'grid-cols-2 gap-6': isTablet,
            'grid-cols-12 gap-8': !isMobile && !isTablet
          }
        )}>
          {/* Logo and company info */}
          <div className={classNames('footer-branding', {
            'mb-6': isMobile,
            'col-span-1': isTablet,
            'col-span-4': !isMobile && !isTablet
          })}>
            <Link href={ROUTES.HOME} aria-label="Return to home page">
              <Image 
                src="/images/logo-white.png" 
                alt="IndiVillage" 
                width={isMobile ? 140 : 180} 
                height={isMobile ? 35 : 45} 
                className="mb-4"
                priority
              />
            </Link>
            <p className="mt-4 text-sm text-gray-400">
              Creating sustainable livelihoods through technology while delivering exceptional AI services.
            </p>
            <p className="mt-6 text-sm text-gray-500">
              &copy; {new Date().getFullYear()} IndiVillage. All rights reserved.
            </p>
          </div>
          
          {/* Navigation sections */}
          <div className={classNames('footer-nav', {
            'grid grid-cols-1 gap-6 sm:grid-cols-2': isMobile,
            'col-span-1 grid grid-cols-2 gap-4': isTablet,
            'col-span-7 grid grid-cols-3 gap-8': !isMobile && !isTablet
          })}>
            {FOOTER_SECTIONS.map((section) => (
              <div key={section.title} className={classNames('footer-nav-section', { 'mb-6': isMobile })}>
                <h3 className="text-lg font-medium mb-4">{section.title}</h3>
                <ul className="space-y-2">
                  {section.links.map((link) => (
                    <li key={link.label}>
                      {link.isExternal ? (
                        <a 
                          href={link.path}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-gray-400 hover:text-white transition-colors"
                        >
                          {link.label}
                        </a>
                      ) : (
                        <Link 
                          href={link.path}
                          className="text-gray-400 hover:text-white transition-colors"
                        >
                          {link.label}
                        </Link>
                      )}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
          
          {/* Social media links */}
          <div className={classNames('footer-social', {
            'mt-2': isMobile,
            'col-span-2': isTablet,
            'col-span-1': !isMobile && !isTablet
          })}>
            <h3 className="text-lg font-medium mb-4">Follow Us</h3>
            <div className="flex space-x-4">
              {SOCIAL_LINKS.map((social) => (
                <a 
                  key={social.name}
                  href={social.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  aria-label={`Follow IndiVillage on ${social.name}`}
                  className="text-gray-400 hover:text-white transition-colors"
                >
                  <Icon name={social.icon as IconName} size={24} />
                </a>
              ))}
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;