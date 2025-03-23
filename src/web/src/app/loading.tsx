import React from 'react'; // version 18.2.0
import Loader from '../../components/ui/Loader';
import { Size } from '../../types/common';

/**
 * A loading component for Next.js app directory that displays a loading state
 * while page content is being fetched or rendered.
 * 
 * This component is automatically used by Next.js during page transitions and initial loading states,
 * providing visual feedback to improve user experience.
 * 
 * @returns JSX.Element - Rendered loading component
 */
export default function Loading() {
  return (
    <div 
      className="w-full min-h-screen flex items-center justify-center"
      aria-live="polite"
      role="status"
    >
      <Loader 
        size={Size.LARGE} 
        color="#0055A4" // Primary brand blue
      />
      <span className="sr-only">Loading, please wait.</span>
    </div>
  );
}