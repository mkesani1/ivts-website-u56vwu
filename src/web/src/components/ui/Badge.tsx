import React from 'react';
import classNames from 'classnames'; // version 2.3.2
import { Size, SizeValue, Variant, VariantValue, IconName } from '../../types/common';
import { setAriaAttributes } from '../../utils/accessibility';
import Icon from './Icon';

/**
 * Props for the Badge component
 */
export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  /** The styling variant of the badge */
  variant?: VariantValue;
  /** The size of the badge */
  size?: SizeValue;
  /** Whether the badge has rounded corners */
  rounded?: boolean;
  /** Optional icon to display in the badge */
  icon?: IconName;
  /** Additional class names to apply */
  className?: string;
  /** Badge content */
  children?: React.ReactNode;
}

/**
 * Generates CSS class names for the badge based on variant, size, and other props
 */
const getBadgeClasses = (
  variant: VariantValue = Variant.PRIMARY,
  size: SizeValue = Size.SMALL,
  rounded: boolean = false,
  className?: string
): string => {
  return classNames(
    'badge',
    `badge-${variant}`,
    `badge-${size}`,
    {
      'badge-rounded': rounded
    },
    className
  );
};

/**
 * A customizable badge component that displays labels, tags, or status indicators
 * 
 * @example
 * // Basic usage
 * <Badge>New</Badge>
 * 
 * // With variant and size
 * <Badge variant="secondary" size="medium">Featured</Badge>
 * 
 * // With icon
 * <Badge icon="check">Verified</Badge>
 * 
 * // Rounded badge
 * <Badge rounded>10</Badge>
 */
const Badge: React.FC<BadgeProps> = ({
  variant = Variant.PRIMARY,
  size = Size.SMALL,
  rounded = false,
  icon,
  className,
  children,
  ...props
}) => {
  const badgeClasses = getBadgeClasses(variant, size, rounded, className);
  
  return (
    <span 
      className={badgeClasses}
      ref={(node) => {
        if (node) {
          // Apply appropriate accessibility attributes
          setAriaAttributes(node, {
            // For status badges, use 'status' role
            // Otherwise, no specific role is needed as they're informational labels
            'role': 'status'
          });
        }
      }}
      {...props}
    >
      {icon && <Icon name={icon} size={size} className="badge-icon" />}
      {children}
    </span>
  );
};

export default Badge;
export type { BadgeProps };