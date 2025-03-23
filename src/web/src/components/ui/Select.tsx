import React, { useState, useRef, useEffect } from 'react'; // version 18.2.0
import classNames from 'classnames'; // version 2.3.2
import { SelectProps, SelectOption } from '../../types/common';
import Icon from './Icon';
import { setAriaAttributes } from '../../utils/accessibility';
import useClickOutside from '../../hooks/useClickOutside';
import useKeyPress from '../../hooks/useKeyPress';

/**
 * Generates CSS class names for the select component based on its props
 */
const getSelectClasses = (
  disabled: boolean,
  hasError: boolean,
  isOpen: boolean,
  className?: string
) => {
  return classNames(
    'select',
    {
      'select--disabled': disabled,
      'select--error': hasError,
      'select--open': isOpen
    },
    className
  );
};

/**
 * Generates CSS class names for select options based on their state
 */
const getOptionClasses = (
  isSelected: boolean,
  isHighlighted: boolean,
  isDisabled: boolean
) => {
  return classNames(
    'select__option',
    {
      'select__option--selected': isSelected,
      'select__option--highlighted': isHighlighted,
      'select__option--disabled': isDisabled
    }
  );
};

/**
 * A customizable select dropdown component with keyboard navigation and accessibility features
 */
const Select: React.FC<SelectProps> = ({
  name,
  value,
  options,
  placeholder = 'Select an option',
  disabled = false,
  required = false,
  error,
  className,
  onChange,
  onBlur,
  ...rest
}) => {
  // State for dropdown open/closed
  const [isOpen, setIsOpen] = useState<boolean>(false);
  
  // State for keyboard navigation
  const [highlightedIndex, setHighlightedIndex] = useState<number>(-1);
  
  // Refs for DOM elements
  const selectRef = useRef<HTMLDivElement>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);
  
  // Determine if select has an error
  const hasError = !!error;
  
  // Find the currently selected option
  const selectedOption = options.find(option => option.value === value);
  
  // Generate class names
  const selectClasses = getSelectClasses(disabled, hasError, isOpen, className);
  
  // Close dropdown when clicking outside
  useClickOutside(selectRef, () => {
    if (isOpen) {
      setIsOpen(false);
      onBlur?.({ target: { name } } as React.FocusEvent<HTMLSelectElement>);
    }
  });
  
  // Handle keyboard navigation with arrow keys
  useKeyPress(['ArrowDown', 'ArrowUp'], (event) => {
    if (disabled) return;
    
    // Open dropdown on initial arrow press if closed
    if (!isOpen) {
      event.preventDefault();
      setIsOpen(true);
      
      // Highlight selected option or first non-disabled option
      const initialIndex = value 
        ? options.findIndex(option => option.value === value) 
        : options.findIndex(option => !option.disabled);
      
      setHighlightedIndex(initialIndex >= 0 ? initialIndex : 0);
      return;
    }
    
    // Navigate through options
    if (event.key === 'ArrowDown') {
      event.preventDefault(); // Prevent page scrolling
      setHighlightedIndex(prev => {
        let nextIndex = prev + 1;
        // Find next non-disabled option
        while (nextIndex < options.length && options[nextIndex]?.disabled) {
          nextIndex++;
        }
        // Stay at current index if we've reached the end
        return nextIndex < options.length ? nextIndex : prev;
      });
    } else if (event.key === 'ArrowUp') {
      event.preventDefault(); // Prevent page scrolling
      setHighlightedIndex(prev => {
        let nextIndex = prev - 1;
        // Find previous non-disabled option
        while (nextIndex >= 0 && options[nextIndex]?.disabled) {
          nextIndex--;
        }
        // Stay at current index if we've reached the beginning
        return nextIndex >= 0 ? nextIndex : prev;
      });
    }
  }, { enabled: !disabled });
  
  // Handle Enter key and Space key press
  useKeyPress(['Enter', ' '], (event) => {
    if (disabled) return;
    
    // Toggle dropdown if closed
    if (!isOpen) {
      event.preventDefault(); // Prevent form submission
      setIsOpen(true);
      
      // Highlight selected option or first option
      const initialIndex = value 
        ? options.findIndex(option => option.value === value) 
        : options.findIndex(option => !option.disabled);
      
      setHighlightedIndex(initialIndex >= 0 ? initialIndex : 0);
      return;
    }
    
    // Select highlighted option
    if (highlightedIndex >= 0 && highlightedIndex < options.length) {
      event.preventDefault(); // Prevent form submission
      const option = options[highlightedIndex];
      if (!option.disabled) {
        handleOptionClick(option);
      }
    }
  }, { enabled: !disabled });
  
  // Handle Escape key press
  useKeyPress(['Escape'], () => {
    if (isOpen) {
      setIsOpen(false);
      selectRef.current?.focus();
      onBlur?.({ target: { name } } as React.FocusEvent<HTMLSelectElement>);
    }
  }, { enabled: isOpen });
  
  // Reset highlighted index when dropdown closes
  useEffect(() => {
    if (!isOpen) {
      setHighlightedIndex(-1);
    }
  }, [isOpen]);
  
  // Scroll highlighted option into view
  useEffect(() => {
    if (isOpen && highlightedIndex >= 0 && dropdownRef.current) {
      const highlightedOption = dropdownRef.current.querySelector(
        `.select__option:nth-child(${highlightedIndex + 1})`
      ) as HTMLElement;
      
      if (highlightedOption) {
        highlightedOption.scrollIntoView({ block: 'nearest' });
      }
    }
  }, [highlightedIndex, isOpen]);
  
  // Set ARIA attributes on mount and when relevant props change
  useEffect(() => {
    if (selectRef.current) {
      setAriaAttributes(selectRef.current, {
        'haspopup': 'listbox',
        'controls': `${name}-dropdown`,
        'label': placeholder,
        'expanded': isOpen.toString(),
        'required': required.toString(),
        'invalid': hasError.toString(),
        'disabled': disabled.toString()
      });
    }
  }, [name, placeholder, isOpen, required, hasError, disabled]);
  
  // Toggle dropdown open/closed
  const handleToggleDropdown = () => {
    if (disabled) return;
    
    const newIsOpen = !isOpen;
    setIsOpen(newIsOpen);
    
    if (newIsOpen) {
      // When opening, highlight the current selection or first non-disabled option
      const selectedIndex = value 
        ? options.findIndex(option => option.value === value) 
        : options.findIndex(option => !option.disabled);
      
      setHighlightedIndex(selectedIndex >= 0 ? selectedIndex : 0);
    } else {
      // When closing, trigger onBlur
      onBlur?.({ target: { name } } as React.FocusEvent<HTMLSelectElement>);
    }
  };
  
  // Handle option click
  const handleOptionClick = (option: SelectOption) => {
    if (disabled || option.disabled) return;
    
    // Create a synthetic change event
    const event = {
      target: {
        name,
        value: option.value
      }
    } as React.ChangeEvent<HTMLSelectElement>;
    
    onChange?.(event);
    setIsOpen(false);
    selectRef.current?.focus();
  };
  
  return (
    <div className="select-container">
      <div
        ref={selectRef}
        className={selectClasses}
        onClick={handleToggleDropdown}
        tabIndex={disabled ? -1 : 0}
        role="combobox"
        {...rest}
      >
        <div className="select__value">
          {selectedOption ? selectedOption.label : placeholder}
        </div>
        
        <div className="select__arrow">
          <Icon 
            name="arrowRight" 
            size="small" 
            className={isOpen ? 'select__arrow-icon--open' : 'select__arrow-icon'} 
          />
        </div>
        
        {isOpen && (
          <div 
            ref={dropdownRef}
            className="select__dropdown" 
            id={`${name}-dropdown`}
            role="listbox"
            aria-activedescendant={
              highlightedIndex >= 0 ? `${name}-option-${highlightedIndex}` : undefined
            }
          >
            {options.map((option, index) => (
              <div
                key={option.value}
                id={`${name}-option-${index}`}
                className={getOptionClasses(
                  option.value === value,
                  index === highlightedIndex,
                  !!option.disabled
                )}
                role="option"
                aria-selected={option.value === value}
                aria-disabled={option.disabled}
                onClick={() => handleOptionClick(option)}
                onMouseEnter={() => !option.disabled && setHighlightedIndex(index)}
              >
                {option.label}
                {option.value === value && (
                  <span className="select__check">
                    <Icon name="check" size="small" />
                  </span>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
      
      {error && <div className="select__error">{error}</div>}
      
      {/* Hidden native select for form submission */}
      <select
        name={name}
        value={value}
        disabled={disabled}
        required={required}
        onChange={() => {}} // Handled by our custom implementation
        aria-hidden="true"
        tabIndex={-1}
        style={{ 
          position: 'absolute',
          width: '1px',
          height: '1px',
          padding: 0,
          margin: '-1px',
          overflow: 'hidden',
          clip: 'rect(0, 0, 0, 0)',
          whiteSpace: 'nowrap',
          border: 0
        }}
      >
        <option value="" disabled={required}>
          {placeholder}
        </option>
        {options.map(option => (
          <option 
            key={option.value} 
            value={option.value} 
            disabled={option.disabled}
          >
            {option.label}
          </option>
        ))}
      </select>
    </div>
  );
};

export default Select;