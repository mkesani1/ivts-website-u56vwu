import React from 'react'; // version 18.2.0
import classNames from 'classnames'; // version 2.3.2
import Breadcrumb, { BreadcrumbItem } from '../ui/Breadcrumb';

/**
 * Interface defining the props for the PageHeader component
 */
export interface PageHeaderProps {
  /**
   * Main title of the page
   */
  title: string;
  /**
   * Optional subtitle displayed below the main title
   */
  subtitle?: string;
  /**
   * Optional breadcrumb navigation items
   */
  breadcrumbs?: BreadcrumbItem[];
  /**
   * Additional CSS classes to apply to the component
   */
  className?: string;
}

/**
 * A component that renders a page header with title, optional subtitle, and breadcrumb navigation.
 * Provides consistent styling and structure for page headers across the IndiVillage website.
 * 
 * @example
 * ```tsx
 * <PageHeader
 *   title="Data Preparation"
 *   subtitle="Transform raw data into AI-ready datasets"
 *   breadcrumbs={[
 *     { label: 'Home', href: '/' },
 *     { label: 'Services', href: '/services' },
 *     { label: 'Data Preparation', href: '/services/data-preparation', current: true }
 *   ]}
 * />
 * ```
 */
const PageHeader: React.FC<PageHeaderProps> = ({
  title,
  subtitle,
  breadcrumbs,
  className,
  ...props
}) => {
  return (
    <header 
      className={classNames(
        'page-header',
        {
          'page-header-with-breadcrumbs': !!breadcrumbs?.length,
          'page-header-with-subtitle': !!subtitle
        },
        className
      )}
      {...props}
    >
      {breadcrumbs && breadcrumbs.length > 0 && (
        <div className="page-header-breadcrumbs">
          <Breadcrumb items={breadcrumbs} />
        </div>
      )}
      
      <div className="page-header-content">
        <h1 className="page-header-title">{title}</h1>
        
        {subtitle && (
          <p className="page-header-subtitle">{subtitle}</p>
        )}
      </div>
    </header>
  );
};

export default PageHeader;