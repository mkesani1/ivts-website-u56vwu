import React, { useState, useEffect, useRef } from 'react';
import classNames from 'classnames'; // version 2.3.2

import { Size, SizeValue, Direction, DirectionValue } from '../../types/common';
import { setAriaAttributes, handleEscapeKey } from '../../utils/accessibility';

/**
 * Interface defining the structure of tab items
 */
export interface TabItem {
  id: string;
  label: string | React.ReactNode;
  disabled?: boolean;
}

/**
 * Interface defining the props for the Tabs component
 */
export interface TabsProps {
  tabs: TabItem[];
  activeTab?: string;
  direction?: DirectionValue;
  size?: SizeValue;
  onChange: (tabId: string) => void;
  className?: string;
  children?: React.ReactNode;
}

/**
 * Interface for the TabPanel component props
 */
interface TabPanelProps {
  id: string;
  isActive?: boolean;
  children: React.ReactNode;
  className?: string;
}

/**
 * Generates CSS class names for the tabs container based on its props
 * @param direction - The orientation of the tabs (horizontal or vertical)
 * @param size - The size of the tabs (small, medium, large)
 * @param className - Optional custom class name
 * @returns Combined CSS class names string
 */
const getTabsClasses = (
  direction: DirectionValue = Direction.HORIZONTAL,
  size: SizeValue = Size.MEDIUM,
  className?: string
): string => {
  return classNames(
    'tabs',
    `tabs--${direction}`,
    `tabs--${size}`,
    className
  );
};

/**
 * Generates CSS class names for individual tab items based on their state
 * @param isActive - Whether the tab is currently active
 * @param disabled - Whether the tab is disabled
 * @param className - Optional custom class name
 * @returns Combined CSS class names string
 */
const getTabItemClasses = (
  isActive: boolean,
  disabled: boolean,
  className?: string
): string => {
  return classNames(
    'tabs__item',
    {
      'tabs__item--active': isActive,
      'tabs__item--disabled': disabled
    },
    className
  );
};

/**
 * A tabbed interface component that organizes content into separate views
 * @param props - Component props
 * @returns Rendered tabs component
 */
const Tabs = ({
  tabs,
  activeTab,
  direction = Direction.HORIZONTAL,
  size = Size.MEDIUM,
  onChange,
  className,
  children
}: TabsProps): JSX.Element => {
  // State to track the currently active tab index
  const [activeTabId, setActiveTabId] = useState<string>(
    activeTab || (tabs.length > 0 ? tabs[0].id : '')
  );
  
  // Reference to the tabs container element
  const tabsRef = useRef<HTMLDivElement>(null);

  // Update active tab when activeTab prop changes
  useEffect(() => {
    if (activeTab !== undefined && activeTab !== activeTabId) {
      setActiveTabId(activeTab);
    }
  }, [activeTab, activeTabId]);

  // Handle tab selection
  const handleTabClick = (tabId: string) => {
    if (tabId !== activeTabId) {
      setActiveTabId(tabId);
      onChange(tabId);
    }
  };

  // Keyboard navigation for accessibility
  const handleKeyDown = (event: React.KeyboardEvent, tabId: string) => {
    const tabsArray = tabs.filter(tab => !tab.disabled);
    const currentIndex = tabsArray.findIndex(tab => tab.id === activeTabId);
    let nextIndex = currentIndex;

    // Handle arrow key navigation differently based on tab direction
    if (direction === Direction.HORIZONTAL) {
      // Left/Right arrows for horizontal tabs
      switch (event.key) {
        case 'ArrowLeft':
          nextIndex = Math.max(0, currentIndex - 1);
          event.preventDefault();
          break;
        case 'ArrowRight':
          nextIndex = Math.min(tabsArray.length - 1, currentIndex + 1);
          event.preventDefault();
          break;
        case 'Home':
          nextIndex = 0;
          event.preventDefault();
          break;
        case 'End':
          nextIndex = tabsArray.length - 1;
          event.preventDefault();
          break;
        case 'Enter':
        case ' ':
          handleTabClick(tabId);
          event.preventDefault();
          break;
      }
    } else {
      // Up/Down arrows for vertical tabs
      switch (event.key) {
        case 'ArrowUp':
          nextIndex = Math.max(0, currentIndex - 1);
          event.preventDefault();
          break;
        case 'ArrowDown':
          nextIndex = Math.min(tabsArray.length - 1, currentIndex + 1);
          event.preventDefault();
          break;
        case 'Home':
          nextIndex = 0;
          event.preventDefault();
          break;
        case 'End':
          nextIndex = tabsArray.length - 1;
          event.preventDefault();
          break;
        case 'Enter':
        case ' ':
          handleTabClick(tabId);
          event.preventDefault();
          break;
      }
    }

    // If the index changed, update the active tab
    if (nextIndex !== currentIndex) {
      const nextTabId = tabsArray[nextIndex].id;
      setActiveTabId(nextTabId);
      onChange(nextTabId);
    }
  };

  // Set up escape key handler for accessibility
  useEffect(() => {
    if (tabsRef.current) {
      return handleEscapeKey(() => {
        // Focus can be moved to a parent element or another location when Escape is pressed
        if (tabsRef.current?.parentElement) {
          tabsRef.current.parentElement.focus();
        }
      }, tabsRef.current);
    }
    return () => {};
  }, []);

  // Get the combined class names for the tabs container
  const tabsClassName = getTabsClasses(direction, size, className);

  // Render the tabs component
  return (
    <div 
      ref={tabsRef}
      className={tabsClassName}
      data-testid="tabs"
    >
      {/* Tabs list */}
      <div 
        className="tabs__list" 
        role="tablist" 
        aria-orientation={direction}
      >
        {tabs.map((tab) => {
          const isActive = tab.id === activeTabId;
          const itemClassName = getTabItemClasses(isActive, !!tab.disabled);
          
          // Reference to the tab element
          const tabRef = useRef<HTMLDivElement>(null);

          // Add ARIA attributes for accessibility once the element is mounted
          useEffect(() => {
            if (tabRef.current) {
              setAriaAttributes(tabRef.current, {
                'role': 'tab',
                'selected': isActive.toString(),
                'controls': `panel-${tab.id}`,
                'disabled': tab.disabled ? 'true' : 'false'
              });
            }
          }, [isActive, tab.id, tab.disabled]);

          return (
            <div
              key={tab.id}
              ref={tabRef}
              className={itemClassName}
              tabIndex={isActive ? 0 : -1}
              onClick={() => !tab.disabled && handleTabClick(tab.id)}
              onKeyDown={(e) => !tab.disabled && handleKeyDown(e, tab.id)}
              data-testid={`tab-${tab.id}`}
              id={`tab-${tab.id}`}
            >
              {tab.label}
            </div>
          );
        })}
      </div>

      {/* Tab content panels */}
      <div className="tabs__content">
        {React.Children.map(children, (child) => {
          if (React.isValidElement<TabPanelProps>(child)) {
            return React.cloneElement(child, {
              isActive: child.props.id === activeTabId,
            });
          }
          return child;
        })}
      </div>
    </div>
  );
};

/**
 * Component for rendering the content of a single tab panel
 * @param props - Component props
 * @returns Rendered tab panel
 */
const TabPanel = ({ id, isActive, children, className }: TabPanelProps): JSX.Element => {
  const panelClassName = classNames(
    'tabs__panel',
    {
      'tabs__panel--active': isActive
    },
    className
  );

  // Reference to the panel element
  const panelRef = useRef<HTMLDivElement>(null);

  // Add ARIA attributes for accessibility once the element is mounted
  useEffect(() => {
    if (panelRef.current) {
      setAriaAttributes(panelRef.current, {
        'role': 'tabpanel',
        'hidden': (!isActive).toString(),
        'labelledby': `tab-${id}`
      });
    }
  }, [id, isActive]);

  return (
    <div
      ref={panelRef}
      id={`panel-${id}`}
      className={panelClassName}
      data-testid={`panel-${id}`}
    >
      {isActive && children}
    </div>
  );
};

export default Tabs;