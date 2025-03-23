import React, { useState, useEffect } from 'react'; // version 18.2.0
import { Metadata } from 'next'; // version 13.4.0
import classNames from 'classnames'; // version 2.3.2

// Internal imports
import { PageHeader, BreadcrumbItem } from '../../components/shared/PageHeader';
import CaseStudyCard from '../../components/case-studies/CaseStudyCard';
import FilterBar, { FilterCriteria } from '../../components/case-studies/FilterBar';
import MetaTags from '../../components/shared/MetaTags';
import { getCaseStudies, getServices } from '../../services/contentService';
import { CaseStudy, Industry, Service } from '../../types/content';
import { ROUTES } from '../../constants/routes';

/**
 * Generates metadata for the case studies page for SEO purposes
 * @returns Metadata object for the page
 */
export const generateMetadata = (): Metadata => {
  // Return metadata object with title, description, and other SEO properties
  // Set title to 'Case Studies | IndiVillage'
  // Set description to 'Explore our client success stories showcasing how IndiVillage's AI services have delivered exceptional results across various industries.'
  return {
    title: 'Case Studies | IndiVillage',
    description:
      'Explore our client success stories showcasing how IndiVillage\'s AI services have delivered exceptional results across various industries.',
  };
};

/**
 * Filters case studies based on industry and service criteria
 * @param caseStudies 
 * @param criteria 
 * @returns Filtered case studies
 */
const filterCaseStudies = (
  caseStudies: CaseStudy[],
  criteria: FilterCriteria
): CaseStudy[] => {
  // Check if both industryId and serviceId are empty
  if (!criteria.industryId && !criteria.serviceId) {
    // If both are empty, return the original case studies array
    return caseStudies;
  }

  let filteredCaseStudies = [...caseStudies];

  // Filter case studies based on industryId if provided
  if (criteria.industryId) {
    filteredCaseStudies = filteredCaseStudies.filter(
      (caseStudy) => caseStudy.industry.id === criteria.industryId
    );
  }

  // Filter case studies based on serviceId if provided
  if (criteria.serviceId) {
    filteredCaseStudies = filteredCaseStudies.filter((caseStudy) =>
      caseStudy.services.some((service) => service.id === criteria.serviceId)
    );
  }

  // Return the filtered case studies array
  return filteredCaseStudies;
};

/**
 * Main page component for displaying case studies with filtering
 * @returns Rendered case studies page
 */
const CaseStudiesPage: React.FC = (): Promise<JSX.Element> => {
  // Fetch all case studies using getCaseStudies()
  const [caseStudies, setCaseStudies] = React.useState<CaseStudy[]>([]);
  // Fetch all services using getServices()
  const [services, setServices] = React.useState<Service[]>([]);
  // Set up state for filtered case studies with useState hook
  const [filteredCaseStudies, setFilteredCaseStudies] = React.useState<CaseStudy[]>([]);
  // Set up state for filter criteria with useState hook
  const [filterCriteria, setFilterCriteria] = React.useState<FilterCriteria>({
    industryId: '',
    serviceId: '',
  });

  useEffect(() => {
    const fetchData = async () => {
      const allCaseStudies = await getCaseStudies();
      setCaseStudies(allCaseStudies);
      setFilteredCaseStudies(allCaseStudies);

      const allServices = await getServices();
      setServices(allServices);
    };

    fetchData();
  }, []);

  // Extract unique industries from case studies
  const industries = React.useMemo(() => {
    const uniqueIndustries: { [key: string]: Industry } = {};
    caseStudies.forEach((caseStudy) => {
      if (caseStudy.industry && !uniqueIndustries[caseStudy.industry.id]) {
        uniqueIndustries[caseStudy.industry.id] = caseStudy.industry;
      }
    });
    return Object.values(uniqueIndustries);
  }, [caseStudies]);

  // Implement handleFilterChange function to update filter criteria
  const handleFilterChange = (newCriteria: FilterCriteria) => {
    setFilterCriteria(newCriteria);
  };

  // Use useEffect to filter case studies when criteria changes
  useEffect(() => {
    const newFilteredCaseStudies = filterCaseStudies(caseStudies, filterCriteria);
    setFilteredCaseStudies(newFilteredCaseStudies);
  }, [caseStudies, filterCriteria]);

  // Create breadcrumb items for navigation context
  const breadcrumbs: BreadcrumbItem[] = [
    { label: 'Home', href: ROUTES.HOME },
    { label: 'Case Studies', href: ROUTES.CASE_STUDIES.INDEX, current: true },
  ];

  // Return the page layout with appropriate components
  // Include MetaTags for SEO
  // Include PageHeader with title and breadcrumbs
  // Include FilterBar with industries, services, and filter handler
  // Render a grid of CaseStudyCard components for each filtered case study
  // Apply responsive grid layout based on screen size
  // Display a message when no case studies match the filter criteria
  return (
    <>
      <MetaTags
        title="Case Studies | IndiVillage"
        description="Explore our client success stories showcasing how IndiVillage's AI services have delivered exceptional results across various industries."
      />
      <PageHeader title="Case Studies" breadcrumbs={breadcrumbs} />
      <FilterBar
        industries={industries}
        services={services}
        onFilterChange={handleFilterChange}
      />
      <div className="container mx-auto py-8">
        {filteredCaseStudies.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredCaseStudies.map((caseStudy) => (
              <CaseStudyCard key={caseStudy.id} caseStudy={caseStudy} />
            ))}
          </div>
        ) : (
          <p className="text-gray-600 text-center">
            No case studies match the selected criteria.
          </p>
        )}
      </div>
    </>
  );
};

export default CaseStudiesPage;