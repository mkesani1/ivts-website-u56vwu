import { useState, useEffect, useCallback, useRef } from 'react'; // react@^18.2.0
import { UploadStatus } from '../types/api';
import { UploadState } from '../types/upload';
import { checkUploadStatus, getEstimatedTimeRemaining } from '../services/uploadService';
import { logError } from '../utils/errorHandling';

/**
 * Return type for the useUploadStatus hook
 */
export interface UseUploadStatusReturn {
  uploadState: UploadState;
  isPolling: boolean;
}

/**
 * Custom React hook that provides real-time tracking of file upload status and processing progress.
 * Periodically polls the backend API to get the current status of an uploaded file.
 * 
 * @param uploadId - ID of the upload to track, or null/undefined if no upload
 * @param initialState - Initial state of the upload
 * @returns Object containing the current upload state and polling status
 */
export const useUploadStatus = (
  uploadId: string | null | undefined,
  initialState: UploadState
): UseUploadStatusReturn => {
  // State to track the current upload state
  const [uploadState, setUploadState] = useState<UploadState>(initialState);
  
  // State to track if polling is active
  const [isPolling, setIsPolling] = useState<boolean>(false);
  
  // Ref to store the polling interval ID for cleanup
  const pollingIntervalRef = useRef<NodeJS.Timeout | null>(null);
  
  // Ref to track if the component is mounted to prevent state updates after unmount
  const isMountedRef = useRef<boolean>(true);
  
  // Ref to store the processing start time for ETA calculations
  const processingStartTimeRef = useRef<number | null>(null);
  
  // Terminal states that should stop polling
  const terminalStates = [
    UploadStatus.COMPLETED,
    UploadStatus.FAILED,
    UploadStatus.QUARANTINED
  ];
  
  /**
   * Fetches the current upload status from the API
   */
  const fetchStatus = useCallback(async () => {
    if (!uploadId) return;
    
    try {
      // Get the current status from the API
      const statusData = await checkUploadStatus(uploadId);
      
      // If component is unmounted, don't update state
      if (!isMountedRef.current) return;
      
      // If we're transitioning to processing state, record the start time
      if (statusData.status === UploadStatus.PROCESSING && 
          uploadState.status !== UploadStatus.PROCESSING &&
          !processingStartTimeRef.current) {
        processingStartTimeRef.current = Date.now();
      }
      
      // Calculate estimated time remaining if we're processing
      let estimatedTimeRemaining = statusData.estimatedTimeRemaining;
      if (statusData.status === UploadStatus.PROCESSING && processingStartTimeRef.current) {
        // Use server-provided estimate if available, otherwise calculate
        estimatedTimeRemaining = statusData.estimatedTimeRemaining || 
          getEstimatedTimeRemaining(processingStartTimeRef.current, 50); // Default to 50% progress
      }
      
      // Update the state with new information
      setUploadState(prevState => ({
        ...prevState,
        status: statusData.status,
        processingStep: statusData.processingStep || prevState.processingStep,
        estimatedTimeRemaining: estimatedTimeRemaining || prevState.estimatedTimeRemaining,
        analysisResult: statusData.analysisResult || prevState.analysisResult
      }));
      
      // If we've reached a terminal status, stop polling
      if (terminalStates.includes(statusData.status)) {
        if (pollingIntervalRef.current) {
          clearInterval(pollingIntervalRef.current);
          pollingIntervalRef.current = null;
          setIsPolling(false);
        }
      }
    } catch (error) {
      // Only log errors if component is still mounted
      if (isMountedRef.current) {
        logError(error, 'useUploadStatus.fetchStatus');
      }
    }
  }, [uploadId, uploadState.status]);
  
  // Start/stop polling based on uploadId
  useEffect(() => {
    // Don't do anything if no uploadId provided
    if (!uploadId) {
      // Clear any existing interval
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
        pollingIntervalRef.current = null;
        setIsPolling(false);
      }
      return;
    }
    
    // Check if we're already in a terminal state
    if (terminalStates.includes(uploadState.status)) {
      // If in terminal state, don't start polling
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
        pollingIntervalRef.current = null;
        setIsPolling(false);
      }
      return;
    }
    
    // We have an uploadId and are not in a terminal state, start polling
    
    // Fetch status immediately
    fetchStatus();
    
    // Set up polling interval - every 3 seconds
    pollingIntervalRef.current = setInterval(fetchStatus, 3000);
    setIsPolling(true);
    
    // Cleanup when unmounting or when dependencies change
    return () => {
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
        pollingIntervalRef.current = null;
      }
      setIsPolling(false);
    };
  }, [uploadId, fetchStatus, uploadState.status, terminalStates]);
  
  // Mark component as mounted/unmounted
  useEffect(() => {
    isMountedRef.current = true;
    return () => {
      isMountedRef.current = false;
    };
  }, []);
  
  return { uploadState, isPolling };
};

export default useUploadStatus;