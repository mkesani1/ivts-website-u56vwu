import React from 'react'; // version 18.2.0
import Loader from '../../components/ui/Loader';
import { Size } from '../../types/common';

/**
 * Loading component for the Impact page
 * Displays a centered loading spinner when the Impact content is being loaded
 * Used automatically by Next.js during page transitions and initial loading
 */
export default function Loading() {
  return (
    <div className="w-full min-h-screen flex items-center justify-center">
      <Loader 
        size={Size.LARGE} 
        color="#0055A4" // Primary brand color
      />
    </div>
  );
}