/**
 * Custom React hook for polling API endpoints
 * Used to check evaluation status until completion
 * Part of Phase 3, Module 3: The Manual Evaluation Engine
 */

import { useEffect, useRef, useState } from "react";

interface UsePollingOptions<T> {
  /**
   * Function that fetches data from the API
   */
  fetchFn: () => Promise<T>;
  
  /**
   * Function that determines if polling should stop
   * Returns true to stop polling, false to continue
   */
  shouldStopPolling: (data: T) => boolean;
  
  /**
   * Polling interval in milliseconds
   * @default 3000 (3 seconds)
   */
  interval?: number;
  
  /**
   * Whether polling is enabled
   * @default false
   */
  enabled?: boolean;
  
  /**
   * Callback when data is fetched
   */
  onData?: (data: T) => void;
  
  /**
   * Callback when polling stops
   */
  onComplete?: (data: T) => void;
  
  /**
   * Callback when an error occurs
   */
  onError?: (error: Error) => void;
}

/**
 * Custom hook for polling an API endpoint at regular intervals
 * 
 * @example
 * ```tsx
 * const { data, isPolling, error } = usePolling({
 *   fetchFn: () => getEvaluation(evaluationId),
 *   shouldStopPolling: (eval) => eval.status === "COMPLETED" || eval.status === "FAILED",
 *   interval: 3000,
 *   enabled: true,
 *   onComplete: (eval) => console.log("Evaluation complete:", eval)
 * });
 * ```
 */
export function usePolling<T>({
  fetchFn,
  shouldStopPolling,
  interval = 3000,
  enabled = false,
  onData,
  onComplete,
  onError,
}: UsePollingOptions<T>) {
  const [data, setData] = useState<T | null>(null);
  const [isPolling, setIsPolling] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const isPollingRef = useRef(false);

  const stopPolling = () => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    setIsPolling(false);
    isPollingRef.current = false;
  };

  const poll = async () => {
    if (!isPollingRef.current) return;
    
    try {
      const result = await fetchFn();
      setData(result);
      setError(null);
      
      // Call onData callback
      if (onData) {
        onData(result);
      }
      
      // Check if we should stop polling
      if (shouldStopPolling(result)) {
        stopPolling();
        if (onComplete) {
          onComplete(result);
        }
      }
    } catch (err) {
      const error = err instanceof Error ? err : new Error(String(err));
      setError(error);
      
      if (onError) {
        onError(error);
      }
      
      // Stop polling on error
      stopPolling();
    }
  };

  useEffect(() => {
    if (enabled && !isPollingRef.current) {
      // Start polling
      setIsPolling(true);
      isPollingRef.current = true;
      setError(null);
      
      // Immediate first poll
      poll();
      
      // Set up interval for subsequent polls
      intervalRef.current = setInterval(poll, interval);
    } else if (!enabled && isPollingRef.current) {
      // Stop polling
      stopPolling();
    }
    
    // Cleanup on unmount
    return () => {
      stopPolling();
    };
  }, [enabled, interval]); // Dependencies: only restart if enabled or interval changes

  return {
    data,
    isPolling,
    error,
    refetch: poll, // Manual refetch function
  };
}
