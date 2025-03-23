import { useState, useEffect, useCallback } from 'react'; // react@^18.2.0
import { logError } from '../utils/errorHandling';

/**
 * Interface for configuring the useLocalStorage hook
 */
interface StorageOptions {
  serialize?: boolean;
  deserialize?: boolean;
  prefix?: string;
}

/**
 * Helper function to safely retrieve a value from localStorage
 * @param key The localStorage key to retrieve
 * @param initialValue The initial value to return if the key doesn't exist or in case of an error
 * @returns The parsed value from localStorage or the initial value
 */
function getStorageValue<T>(key: string, initialValue: T | (() => T)): T {
  // Check if we're in a browser environment with localStorage available
  if (typeof window === 'undefined' || !window.localStorage) {
    // Return initial value in SSR / no localStorage environments
    return typeof initialValue === 'function' ? (initialValue as () => T)() : initialValue;
  }

  try {
    // Get the item from localStorage
    const item = window.localStorage.getItem(key);
    
    // If the item exists, parse it and return it
    if (item) {
      return JSON.parse(item);
    }
    
    // If the item doesn't exist, return the initial value
    return typeof initialValue === 'function' ? (initialValue as () => T)() : initialValue;
  } catch (error) {
    // Log any errors that occur
    logError(error, `localStorage.getItem('${key}')`);
    
    // Return the initial value in case of an error
    return typeof initialValue === 'function' ? (initialValue as () => T)() : initialValue;
  }
}

/**
 * Custom React hook for using localStorage with React state
 * 
 * This hook provides a convenient, type-safe interface for storing and retrieving data from 
 * the browser's localStorage API. It handles common localStorage issues like:
 * - SSR compatibility (no window object)
 * - Storage quota exceeded errors
 * - Disabled localStorage (e.g., private browsing mode)
 * - JSON parsing errors
 * 
 * @param key The localStorage key to use
 * @param initialValue The initial value to use if the key doesn't exist in localStorage
 * @returns A tuple with the current value, a function to update the value, and a function to remove the value
 * 
 * @example
 * // Store user theme preference
 * const [theme, setTheme, removeTheme] = useLocalStorage<'light' | 'dark'>('theme', 'light');
 * 
 * // Store form progress
 * const [formData, setFormData, resetForm] = useLocalStorage('uploadForm', {});
 */
export function useLocalStorage<T>(
  key: string,
  initialValue: T | (() => T)
): [T, (value: T | ((val: T) => T)) => void, () => void] {
  // Create state based on the value from localStorage or the initial value
  const [storedValue, setStoredValue] = useState<T>(() => getStorageValue(key, initialValue));

  // Update stored value when key changes
  useEffect(() => {
    setStoredValue(getStorageValue(key, initialValue));
  }, [key, initialValue]);

  // Effect to update localStorage when the value changes
  useEffect(() => {
    // Only save to localStorage if we're in a browser environment
    if (typeof window === 'undefined' || !window.localStorage) {
      return;
    }

    try {
      // Save to localStorage
      window.localStorage.setItem(key, JSON.stringify(storedValue));
    } catch (error) {
      // Handle potential localStorage errors (quota exceeded, private browsing, etc.)
      logError(error, `localStorage.setItem('${key}')`);
    }
  }, [key, storedValue]);

  // Function to update the value (similar to React's setState)
  const setValue = useCallback((value: T | ((val: T) => T)) => {
    setStoredValue((prevValue) => {
      // If value is a function, call it with the previous value
      return value instanceof Function ? value(prevValue) : value;
    });
  }, []);

  // Function to remove the value from localStorage
  const removeValue = useCallback(() => {
    // Only remove from localStorage if we're in a browser environment
    if (typeof window === 'undefined' || !window.localStorage) {
      return;
    }

    try {
      // Remove from localStorage
      window.localStorage.removeItem(key);
      // Reset state to initial value
      setStoredValue(typeof initialValue === 'function' ? (initialValue as () => T)() : initialValue);
    } catch (error) {
      // Handle potential localStorage errors
      logError(error, `localStorage.removeItem('${key}')`);
    }
  }, [key, initialValue]);

  return [storedValue, setValue, removeValue];
}

export default useLocalStorage;