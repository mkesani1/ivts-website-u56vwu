import React from 'react'; // react v18.2.0
import classNames from 'classnames'; // v2.3.2

import Card from '../ui/Card';
import AnimatedCounter from '../shared/AnimatedCounter';
import { CaseStudyResult } from '../../types/content';
import { Variant } from '../../types/common';

/**
 * Props interface for the CaseStudyResults component
 */
export interface CaseStudyResultsProps {
  /** Array of case study results to display */
  results: CaseStudyResult[];
  /** Optional CSS class to apply to the component */
  className?: string;
}

/**
 * Parses a string value to extract numeric value, prefix, and suffix
 * @param value String value to parse (e.g., "$1,000+", "30%", "2x")
 * @returns Object containing numericValue, prefix, and suffix
 */
const parseValue = (value: string): { numericValue: number, prefix: string, suffix: string } => {
  // Default values
  let numericValue = 0;
  let prefix = '';
  let suffix = '';

  // Handle empty or undefined values
  if (!value) {
    return { numericValue, prefix, suffix };
  }

  // Extract numeric portion using regex
  // Looking for one or more digits, optionally with commas and a decimal point
  const numericMatch = value.match(/[\d,]+(\.\d+)?/);
  
  if (numericMatch) {
    // Get the raw numeric string and convert to number
    const numericString = numericMatch[0];
    // Remove commas before parsing
    numericValue = parseFloat(numericString.replace(/,/g, ''));
    
    // Find index of the numeric portion
    const startIndex = value.indexOf(numericString);
    const endIndex = startIndex + numericString.length;
    
    // Extract prefix and suffix
    prefix = value.substring(0, startIndex);
    suffix = value.substring(endIndex);
  } else {
    // If no numeric portion found, treat the whole string as a suffix
    suffix = value;
  }
  
  return { numericValue, prefix, suffix };
};

/**
 * A component that displays the results and metrics of a case study in a
 * visually appealing grid layout. Each result is presented with an animated counter.
 */
const CaseStudyResults = ({ results, className }: CaseStudyResultsProps): JSX.Element | null => {
  // Return null if no results are provided
  if (!results || results.length === 0) {
    return null;
  }

  return (
    <section 
      className={classNames('case-study-results', className)}
      aria-labelledby="case-study-results-heading"
    >
      <h2 id="case-study-results-heading" className="sr-only">Case Study Results</h2>
      
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 md:gap-6">
        {results.map((result) => {
          const { numericValue, prefix, suffix } = parseValue(result.value);
          
          return (
            <Card 
              key={result.id}
              variant={Variant.PRIMARY}
              elevation={2}
              className="p-4 md:p-6 text-center h-full flex flex-col justify-center items-center"
            >
              <div className="mb-3 text-3xl md:text-4xl font-bold text-primary">
                <AnimatedCounter 
                  value={numericValue}
                  prefix={prefix}
                  suffix={suffix}
                  duration={1500}
                />
              </div>
              <h3 className="text-lg md:text-xl font-semibold mb-2">{result.metric}</h3>
              {result.description && (
                <p className="text-sm md:text-base text-gray-600">{result.description}</p>
              )}
            </Card>
          );
        })}
      </div>
    </section>
  );
};

export default CaseStudyResults;