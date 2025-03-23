import React from 'react';
import classNames from 'classnames'; // v2.3.2
import { UploadProgress, formatFileSize } from '../../types/upload';

/**
 * Interface for ProgressBar component props
 */
export interface ProgressBarProps {
  /** Upload progress data with loaded, total, and percentage */
  progress: UploadProgress;
  /** Optional class name for custom styling */
  className?: string;
  /** Whether to show percentage text (default: true) */
  showPercentage?: boolean;
  /** Whether to show details like loaded/total (default: true) */
  showDetails?: boolean;
  /** Color of the progress bar (default: #0055A4 - primary blue) */
  color?: string;
  /** Height of the progress bar in pixels (default: 8) */
  height?: number;
  /** Optional label to display above the progress bar */
  label?: string;
  /** Optional text describing current processing step */
  processingStep?: string;
  /** Optional time remaining in seconds */
  estimatedTimeRemaining?: number;
}

/**
 * A customizable progress bar component that visualizes the progress of 
 * operations like file uploads and processing.
 */
const ProgressBar: React.FC<ProgressBarProps> = ({
  progress,
  className,
  showPercentage = true,
  showDetails = true,
  color = '#0055A4', // Primary blue from the design system
  height = 8,
  label,
  processingStep,
  estimatedTimeRemaining
}) => {
  // Calculate width percentage, defaulting to 0 if not available
  const percentage = progress?.percentage || 0;
  
  // Format loaded and total values if showing details
  let loadedFormatted, totalFormatted;
  if (showDetails && progress) {
    loadedFormatted = formatFileSize(progress.loaded);
    totalFormatted = formatFileSize(progress.total);
  }
  
  // Format estimated time remaining in a human-readable format
  let timeRemainingFormatted;
  if (estimatedTimeRemaining !== undefined && estimatedTimeRemaining > 0) {
    const minutes = Math.floor(estimatedTimeRemaining / 60);
    const seconds = Math.floor(estimatedTimeRemaining % 60);
    
    if (minutes > 0) {
      timeRemainingFormatted = `${minutes} minute${minutes !== 1 ? 's' : ''}`;
      if (seconds > 0) {
        timeRemainingFormatted += ` ${seconds} second${seconds !== 1 ? 's' : ''}`;
      }
    } else {
      timeRemainingFormatted = `${seconds} second${seconds !== 1 ? 's' : ''}`;
    }
  }
  
  // Combine className prop with default classes
  const containerClasses = classNames(
    'progress-bar-container',
    className
  );
  
  const infoClasses = classNames(
    "progress-bar-info mt-1 text-sm text-gray-600",
    { "flex justify-between items-center": showPercentage && showDetails }
  );
  
  const detailsClasses = classNames(
    "progress-bar-details",
    { "ml-auto": showPercentage }
  );
  
  return (
    <div className={containerClasses}>
      {/* Optional label */}
      {label && <div className="progress-bar-label text-sm font-medium mb-1">{label}</div>}
      
      {/* Progress bar track (background) */}
      <div 
        className="progress-bar-track w-full rounded-full bg-gray-200" 
        style={{ height: `${height}px` }}
      >
        {/* Progress bar fill (foreground) */}
        <div 
          className="progress-bar-fill rounded-full transition-width duration-300 ease-in-out" 
          style={{ 
            width: `${percentage}%`, 
            backgroundColor: color,
            height: `${height}px`
          }}
        ></div>
      </div>
      
      {/* Info section with percentage and/or details */}
      {(showPercentage || showDetails) && (
        <div className={infoClasses}>
          {showPercentage && (
            <div className="progress-bar-percentage font-medium">
              {Math.round(percentage)}%
            </div>
          )}
          
          {showDetails && progress && progress.total > 0 && (
            <div className={detailsClasses}>
              {loadedFormatted} / {totalFormatted}
            </div>
          )}
        </div>
      )}
      
      {/* Optional processing step information */}
      {processingStep && (
        <div className="progress-bar-step mt-2 text-sm text-gray-700">
          {processingStep}
        </div>
      )}
      
      {/* Optional estimated time remaining */}
      {timeRemainingFormatted && (
        <div className="progress-bar-time-remaining mt-1 text-sm text-gray-600">
          Estimated time remaining: {timeRemainingFormatted}
        </div>
      )}
    </div>
  );
};

export default ProgressBar;