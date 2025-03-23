import React, { useState, useEffect } from 'react'; // version 18.2.0
import classNames from 'classnames'; // version 2.3.2

// Internal imports
import { Industry, Service } from '../../types/content';
import { SelectOption, Variant, Size, Breakpoint } from '../../types/common';
import Select from '../../components/ui/Select';
import Button from '../../components/ui/Button';
import useBreakpoint from '../../hooks/useBreakpoint';

/**
 * Interface for FilterBar component props
 */
export interface FilterBarProps {
  /**
   * Array of industries for filter options
   */
  industries: Industry[];
  
  /**
   * Array of services for filter options
   */
  services: Service[];
  
  /**
   * Callback function triggered when filters change
   */
  onFilterChange: (filters: FilterCriteria) => void;
  
  /**
   * Optional CSS class name
   */
  className?: string;
}

/**
 * Interface defining the structure of filter criteria
 */
export interface FilterCriteria {
  /**
   * Selected industry ID
   */
  industryId: string;
  
  /**
   * Selected service ID
   */
  serviceId: string;
}

/**
 * Converts an array of industries or services into select options format
 * 
 * @param items - Array of industries or services to convert
 * @returns Array of options formatted for the Select component
 */
const createFilterOptions = (items: Array<Industry | Service>): SelectOption[] => {
  // Create an empty option for 'All'
  const allOption: SelectOption = { value: '', label: 'All' };
  
  // Map items to SelectOption format
  const itemOptions = items.map(item => ({
    value: item.id,
    label: 'title' in item ? item.title : item.name
  }));
  
  // Return combined array with 'All' option first
  return [allOption, ...itemOptions];
};

/**
 * Component that provides filtering capabilities for case studies
 * Allows users to filter by industry and service type to find relevant case studies
 */
const FilterBar: React.FC<FilterBarProps> = ({
  industries,
  services,
  onFilterChange,
  className
}) => {
  // State for selected filters
  const [selectedIndustryId, setSelectedIndustryId] = useState<string>('');
  const [selectedServiceId, setSelectedServiceId] = useState<string>('');
  
  // Get current breakpoint for responsive design
  const breakpoint = useBreakpoint();
  
  // Create select options from industries and services
  const industryOptions = createFilterOptions(industries);
  const serviceOptions = createFilterOptions(services);
  
  // Handle industry filter change
  const handleIndustryChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedIndustryId(event.target.value);
  };
  
  // Handle service filter change
  const handleServiceChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedServiceId(event.target.value);
  };
  
  // Handle clear filters
  const handleClearFilters = () => {
    setSelectedIndustryId('');
    setSelectedServiceId('');
  };
  
  // Update parent component when filters change
  useEffect(() => {
    onFilterChange({
      industryId: selectedIndustryId,
      serviceId: selectedServiceId
    });
  }, [selectedIndustryId, selectedServiceId, onFilterChange]);
  
  // Determine if any filters are applied
  const hasFilters = selectedIndustryId !== '' || selectedServiceId !== '';
  
  // Determine if we're on mobile/small screens
  const isMobileView = breakpoint === Breakpoint.MOBILE || breakpoint === Breakpoint.MOBILE_SMALL;
  
  // Generate component class names
  const filterBarClasses = classNames(
    'filter-bar',
    {
      'filter-bar--has-filters': hasFilters,
      'filter-bar--mobile': isMobileView,
      'filter-bar--tablet': breakpoint === Breakpoint.TABLET,
      'filter-bar--desktop': breakpoint === Breakpoint.DESKTOP || breakpoint === Breakpoint.LARGE_DESKTOP,
    },
    className
  );
  
  return (
    <div className={filterBarClasses} role="search" aria-label="Case studies filter">
      <div className="filter-bar__container">
        <div className="filter-bar__label" id="filter-label">
          {isMobileView ? 'Filter:' : 'Filter Case Studies:'}
        </div>
        
        <div className="filter-bar__controls" aria-labelledby="filter-label">
          <Select
            name="industry-filter"
            value={selectedIndustryId}
            options={industryOptions}
            placeholder="All Industries"
            onChange={handleIndustryChange}
            className="filter-bar__select"
            aria-label="Filter by industry"
          />
          
          <Select
            name="service-filter"
            value={selectedServiceId}
            options={serviceOptions}
            placeholder="All Services"
            onChange={handleServiceChange}
            className="filter-bar__select"
            aria-label="Filter by service"
          />
          
          {hasFilters && (
            <Button
              variant={Variant.SECONDARY}
              size={Size.SMALL}
              onClick={handleClearFilters}
              className="filter-bar__clear-btn"
              aria-label="Clear all filters"
            >
              Clear Filters
            </Button>
          )}
        </div>
      </div>
    </div>
  );
};

export default FilterBar;