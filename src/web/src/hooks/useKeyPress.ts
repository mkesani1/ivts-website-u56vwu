import { useState, useEffect, useCallback } from 'react'; // React 18.2.0

/**
 * Options for configuring the useKeyPress hook.
 */
export interface UseKeyPressOptions {
  /**
   * Whether the key press detection is enabled.
   * @default true
   */
  enabled?: boolean;
  
  /**
   * The element to attach the event listener to.
   * @default document
   */
  eventTarget?: Window | Document | HTMLElement;
  
  /**
   * The type of key event to listen for.
   * @default "both"
   */
  keyEvent?: 'keydown' | 'keyup' | 'both';
  
  /**
   * Whether to prevent the default browser behavior when the key is pressed.
   * @default false
   */
  preventDefault?: boolean;
}

/**
 * A custom hook that detects when a specific key or set of keys is pressed and triggers a callback function.
 * This hook is useful for implementing keyboard shortcuts, accessibility features, and enhanced user interactions.
 * 
 * @param targetKey The key or keys to detect. Can be a single key (e.g., "Escape") or an array of keys (e.g., ["a", "A"]).
 * @param callback The function to call when the target key is pressed.
 * @param options Configuration options for the hook.
 * @returns A boolean indicating whether the target key is currently pressed.
 * 
 * @example
 * // Basic usage - detect when Escape key is pressed
 * const isEscapePressed = useKeyPress("Escape", () => {
 *   // Handle Escape key press
 *   closeModal();
 * });
 * 
 * @example
 * // Detect multiple keys and disable when not needed
 * const isNavigationKey = useKeyPress(["ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight"], 
 *   (event) => {
 *     // Handle arrow key navigation
 *     navigateWithArrowKeys(event.key);
 *   },
 *   { enabled: isModalOpen }
 * );
 */
const useKeyPress = (
  targetKey: string | string[],
  callback?: (event: KeyboardEvent) => void,
  options: UseKeyPressOptions = {}
): boolean => {
  // Default options
  const {
    enabled = true,
    eventTarget = document,
    keyEvent = 'both',
    preventDefault = false
  } = options;

  // State to track if the key is pressed
  const [keyPressed, setKeyPressed] = useState<boolean>(false);

  // Convert targetKey to array for consistent handling
  const targetKeys = Array.isArray(targetKey) ? targetKey : [targetKey];

  // Key down handler
  const handleKeyDown = useCallback(
    (event: KeyboardEvent) => {
      if (!enabled) return;

      const keyPressed = targetKeys.includes(event.key);
      if (keyPressed) {
        if (preventDefault) {
          event.preventDefault();
        }
        setKeyPressed(true);
        callback?.(event);
      }
    },
    [targetKeys, callback, enabled, preventDefault]
  );

  // Key up handler
  const handleKeyUp = useCallback(
    (event: KeyboardEvent) => {
      if (!enabled) return;

      const keyReleased = targetKeys.includes(event.key);
      if (keyReleased) {
        setKeyPressed(false);
      }
    },
    [targetKeys, enabled]
  );

  // Set up event listeners
  useEffect(() => {
    if (!enabled || !eventTarget) return;

    if (keyEvent === 'keydown' || keyEvent === 'both') {
      eventTarget.addEventListener('keydown', handleKeyDown as EventListener);
    }
    
    if (keyEvent === 'keyup' || keyEvent === 'both') {
      eventTarget.addEventListener('keyup', handleKeyUp as EventListener);
    }

    // Clean up
    return () => {
      if (keyEvent === 'keydown' || keyEvent === 'both') {
        eventTarget.removeEventListener('keydown', handleKeyDown as EventListener);
      }
      
      if (keyEvent === 'keyup' || keyEvent === 'both') {
        eventTarget.removeEventListener('keyup', handleKeyUp as EventListener);
      }
    };
  }, [eventTarget, handleKeyDown, handleKeyUp, keyEvent, enabled]);

  return keyPressed;
};

export default useKeyPress;