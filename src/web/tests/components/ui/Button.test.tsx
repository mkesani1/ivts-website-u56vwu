import React from 'react'; // version 18.2.0
import { screen, fireEvent } from '@testing-library/react'; // version 14.0.0
import userEvent from '@testing-library/user-event'; // version 14.4.3

import Button from '../../../src/components/ui/Button';
import { Variant, Size } from '../../../src/types/common';
import { renderWithProviders } from '../../../src/utils/testing';

describe('Button component', () => {
  it('renders correctly with default props', () => {
    // Render Button component with default props
    renderWithProviders(<Button>Click Me</Button>);

    // Verify button is in the document
    const buttonElement = screen.getByRole('button', { name: 'Click Me' });
    expect(buttonElement).toBeInTheDocument();

    // Verify button has default text content
    expect(buttonElement).toHaveTextContent('Click Me');

    // Verify button has default primary variant styling
    expect(buttonElement).toHaveClass('btn--primary');

    // Verify button has default medium size styling
    expect(buttonElement).toHaveClass('btn--medium');
  });

  it('renders different variants correctly', () => {
    // Render Button component with PRIMARY variant
    renderWithProviders(<Button variant={Variant.PRIMARY}>Primary</Button>);
    const primaryButton = screen.getByRole('button', { name: 'Primary' });
    expect(primaryButton).toHaveClass('btn--primary');

    // Render Button component with SECONDARY variant
    renderWithProviders(<Button variant={Variant.SECONDARY}>Secondary</Button>);
    const secondaryButton = screen.getByRole('button', { name: 'Secondary' });
    expect(secondaryButton).toHaveClass('btn--secondary');

    // Render Button component with TERTIARY variant
    renderWithProviders(<Button variant={Variant.TERTIARY}>Tertiary</Button>);
    const tertiaryButton = screen.getByRole('button', { name: 'Tertiary' });
    expect(tertiaryButton).toHaveClass('btn--tertiary');
  });

  it('renders different sizes correctly', () => {
    // Render Button component with SMALL size
    renderWithProviders(<Button size={Size.SMALL}>Small</Button>);
    const smallButton = screen.getByRole('button', { name: 'Small' });
    expect(smallButton).toHaveClass('btn--small');

    // Render Button component with MEDIUM size
    renderWithProviders(<Button size={Size.MEDIUM}>Medium</Button>);
    const mediumButton = screen.getByRole('button', { name: 'Medium' });
    expect(mediumButton).toHaveClass('btn--medium');

    // Render Button component with LARGE size
    renderWithProviders(<Button size={Size.LARGE}>Large</Button>);
    const largeButton = screen.getByRole('button', { name: 'Large' });
    expect(largeButton).toHaveClass('btn--large');
  });

  it('handles click events', () => {
    // Create mock function for onClick handler
    const onClick = jest.fn();

    // Render Button component with mock onClick handler
    renderWithProviders(<Button onClick={onClick}>Click Me</Button>);

    // Click the button
    const buttonElement = screen.getByRole('button', { name: 'Click Me' });
    fireEvent.click(buttonElement);

    // Verify onClick handler was called
    expect(onClick).toHaveBeenCalledTimes(1);
  });

  it('does not trigger onClick when disabled', () => {
    // Create mock function for onClick handler
    const onClick = jest.fn();

    // Render Button component with disabled prop and mock onClick handler
    renderWithProviders(<Button disabled onClick={onClick}>Click Me</Button>);

    // Verify button has disabled attribute
    const buttonElement = screen.getByRole('button', { name: 'Click Me' });
    expect(buttonElement).toBeDisabled();

    // Click the button
    fireEvent.click(buttonElement);

    // Verify onClick handler was not called
    expect(onClick).not.toHaveBeenCalled();
  });

  it('renders loading state correctly', () => {
    // Render Button component with loading prop set to true
    renderWithProviders(<Button loading>Loading...</Button>);

    // Verify loading indicator is displayed
    const loadingIndicator = screen.getByRole('status');
    expect(loadingIndicator).toBeInTheDocument();

    // Verify button text is not displayed during loading
    expect(screen.queryByText('Loading...')).not.toBeInTheDocument();

    // Verify button has aria-busy attribute set to true
    const buttonElement = screen.getByRole('button', { name: 'Loading...' });
    expect(buttonElement).toHaveAttribute('aria-busy', 'true');
  });

  it('renders with an icon', () => {
    // Render Button component with icon prop
    renderWithProviders(<Button icon="arrowRight">Next</Button>);

    // Verify icon is displayed
    const iconElement = screen.getByTestId('icon-arrowRight');
    expect(iconElement).toBeInTheDocument();

    // Verify button text is displayed alongside icon
    const buttonElement = screen.getByRole('button', { name: 'Next' });
    expect(buttonElement).toHaveTextContent('Next');
  });

  it('renders with fullWidth prop', () => {
    // Render Button component with fullWidth prop set to true
    renderWithProviders(<Button fullWidth>Full Width</Button>);

    // Verify button has full width styling
    const buttonElement = screen.getByRole('button', { name: 'Full Width' });
    expect(buttonElement).toHaveClass('btn--full-width');
  });

  it('applies custom className', () => {
    // Render Button component with custom className
    renderWithProviders(<Button className="custom-class">Custom</Button>);

    // Verify button has custom class applied
    const buttonElement = screen.getByRole('button', { name: 'Custom' });
    expect(buttonElement).toHaveClass('custom-class');
  });

  it('has correct accessibility attributes', () => {
    // Render Button component
    renderWithProviders(<Button>Click Me</Button>);

    // Verify button has role='button'
    const buttonElement = screen.getByRole('button', { name: 'Click Me' });
    expect(buttonElement).toHaveAttribute('role', 'button');

    // Verify button is keyboard focusable
    expect(buttonElement).toHaveAttribute('tabindex');

    // Render loading button
    renderWithProviders(<Button loading>Loading</Button>);
    const loadingButton = screen.getByRole('button', { name: 'Loading' });
    expect(loadingButton).toHaveAttribute('aria-busy', 'true');

    // Render disabled button
    renderWithProviders(<Button disabled>Disabled</Button>);
    const disabledButton = screen.getByRole('button', { name: 'Disabled' });
    expect(disabledButton).toHaveAttribute('disabled');
  });
});