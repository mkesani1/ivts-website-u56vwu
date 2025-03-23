import React from 'react';
import classNames from 'classnames'; // version 2.3.2
import Link from 'next/link'; // version 13.4.0
import Icon from './Icon';
import { Size } from '../../types/common';
import { setAriaAttributes } from '../../utils/accessibility';

/**
 * Interface defining the structure of a breadcrumb item
 */
export interface BreadcrumbItem {
  /**
   * Display text for the breadcrumb item
   */
  label: string;
  /**
   * URL for the breadcrumb item
   */
  href: string;
  /**
   * Whether this item represents the current page
   */
  current?: boolean;
}

/**
 * Interface defining the props for the Breadcrumb component
 */
export interface BreadcrumbProps {
  /**
   * Array of breadcrumb items to display
   */
  items: BreadcrumbItem[];
  /**
   * Icon name to use as separator between items
   */
  separator?: string;
  /**
   * Additional CSS classes to apply to the component
   */
  className?: string;
}

/**
 * A component that renders a breadcrumb navigation trail showing the user's current
 * location within the website hierarchy.
 * 
 * @example
 * ```tsx
 * <Breadcrumb
 *   items={[
 *     { label: 'Home', href: '/' },
 *     { label: 'Services', href: '/services' },
 *     { label: 'Data Preparation', href: '/services/data-preparation', current: true }
 *   ]}
 * />
 * ```
 */
const Breadcrumb: React.FC<BreadcrumbProps> = ({
  items,
  separator = 'arrowRight',
  className,
  ...props
}) => {
  // Early return if no items or empty array
  if (!items || items.length === 0) {
    return null;
  }

  return (
    <nav
      className={classNames(
        'breadcrumb', 
        {
          'breadcrumb-condensed': items.length > 3
        },
        className
      )}
      ref={(node) => {
        if (node) {
          setAriaAttributes(node, {
            'role': 'navigation',
            'label': 'Breadcrumb'
          });
        }
      }}
      {...props}
    >
      <ol className="breadcrumb-list">
        {items.map((item, index) => (
          <li
            key={`breadcrumb-${index}`}
            className={classNames(
              'breadcrumb-item', 
              {
                'breadcrumb-item-current': item.current,
                'breadcrumb-item-first': index === 0,
                'breadcrumb-item-last': index === items.length - 1,
                'breadcrumb-item-hidden-mobile': index > 0 && index < items.length - 1 && items.length > 3
              }
            )}
          >
            {item.current ? (
              <span aria-current="page">{item.label}</span>
            ) : (
              <Link href={item.href} className="breadcrumb-link">
                {item.label}
              </Link>
            )}
            
            {index < items.length - 1 && (
              <span className="breadcrumb-separator" aria-hidden="true">
                <Icon name={separator} size={Size.SMALL} />
              </span>
            )}
          </li>
        ))}
      </ol>
    </nav>
  );
};

export default Breadcrumb;