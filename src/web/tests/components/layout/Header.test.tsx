import React from 'react'; // version ^18.2.0
import { render, screen, within, waitFor } from '@testing-library/react'; // version ^14.0.0
import userEvent from '@testing-library/user-event'; // version ^14.4.3

import Header from '../../../../src/components/layout/Header';
import { renderWithProviders } from '../../../../src/utils/testing';
import { ROUTES } from '../../../../src/constants/routes';
import { Breakpoint } from '../../../../src/types/common';

// Mock the useBreakpoint hook
jest.mock('../../../../src/hooks/useBreakpoint', () => ({
  __esModule: true,
  default: jest.fn(),
}));

// Helper function to mock the useBreakpoint hook
const mockUseBreakpoint = (breakpoint: Breakpoint) => {
  const mockedUseBreakpoint = jest.requireMock('../../../../src/hooks/useBreakpoint').default;
  mockedUseBreakpoint.mockReturnValue(breakpoint);
};

describe('Header', () => {
  beforeEach(() => {
    (jest.requireMock('../../../../src/hooks/useBreakpoint').default as jest.Mock).mockClear();
  });

  it('renders the header with logo', () => {
    renderWithProviders(<Header />);
    const logoElement = screen.getByAltText('IndiVillage Logo');
    expect(logoElement).toBeInTheDocument();
    expect(logoElement).toHaveAttribute('alt', 'IndiVillage Logo');
    expect(logoElement).toHaveAttribute('src', '/images/indivillage-logo.svg');
    const linkElement = logoElement.closest('a');
    expect(linkElement).toHaveAttribute('href', ROUTES.HOME);
  });

  it('renders desktop navigation on larger screens', () => {
    mockUseBreakpoint(Breakpoint.DESKTOP);
    renderWithProviders(<Header />);
    const navigationElement = screen.getByRole('navigation', {name: 'Main Navigation'});
    expect(navigationElement).toBeInTheDocument();
    expect(screen.queryByTestId('mobile-menu-toggle')).not.toBeInTheDocument();
  });

  it('renders mobile menu button on smaller screens', () => {
    mockUseBreakpoint(Breakpoint.MOBILE);
    renderWithProviders(<Header />);
    const mobileMenuButton = screen.getByTestId('mobile-menu-toggle');
    expect(mobileMenuButton).toBeInTheDocument();
    expect(screen.queryByRole('navigation', {name: 'Main Navigation'})).not.toBeInTheDocument();
  });

  it('toggles mobile navigation when menu button is clicked', async () => {
    mockUseBreakpoint(Breakpoint.MOBILE);
    renderWithProviders(<Header />);
    const mobileMenuButton = screen.getByTestId('mobile-menu-toggle');
    const overlay = screen.getByTestId('mobile-nav-overlay');
    expect(overlay).not.toHaveClass('mobile-nav-overlay--open');

    await userEvent.click(mobileMenuButton);
    expect(overlay).toHaveClass('mobile-nav-overlay--open');

    const closeButton = screen.getByTestId('mobile-nav-close');
    await userEvent.click(closeButton);
    expect(overlay).not.toHaveClass('mobile-nav-overlay--open');
  });

  it('renders call-to-action buttons', () => {
    mockUseBreakpoint(Breakpoint.DESKTOP);
    renderWithProviders(<Header />);
    const contactButton = screen.getByText('Contact');
    expect(contactButton).toBeInTheDocument();
    expect(contactButton).toHaveAttribute('href', ROUTES.CONTACT);

    const requestDemoButton = screen.getByText('Request Demo');
    expect(requestDemoButton).toBeInTheDocument();
    expect(requestDemoButton.closest('a')).toHaveAttribute('href', ROUTES.REQUEST_DEMO);
  });

  it('applies correct responsive styling based on breakpoint', () => {
    mockUseBreakpoint(Breakpoint.MOBILE);
    renderWithProviders(<Header />);
    const mobileMenuButton = screen.getByTestId('mobile-menu-toggle');
    expect(mobileMenuButton).toBeVisible();

    mockUseBreakpoint(Breakpoint.DESKTOP);
    renderWithProviders(<Header />);
    const contactButton = screen.getByText('Contact');
    expect(contactButton).toBeVisible();
  });

  it('closes mobile menu when breakpoint changes to desktop', async () => {
    mockUseBreakpoint(Breakpoint.MOBILE);
    renderWithProviders(<Header />);
    const mobileMenuButton = screen.getByTestId('mobile-menu-toggle');
    const overlay = screen.getByTestId('mobile-nav-overlay');

    await userEvent.click(mobileMenuButton);
    expect(overlay).toHaveClass('mobile-nav-overlay--open');

    mockUseBreakpoint(Breakpoint.DESKTOP);
    window.dispatchEvent(new Event('resize'));
    expect(overlay).not.toHaveClass('mobile-nav-overlay--open');
  });

  it('locks body scroll when mobile menu is open', async () => {
    mockUseBreakpoint(Breakpoint.MOBILE);
    renderWithProviders(<Header />);
    const mobileMenuButton = screen.getByTestId('mobile-menu-toggle');
    const overlay = screen.getByTestId('mobile-nav-overlay');

    expect(document.body.style.overflow).toBe('');

    await userEvent.click(mobileMenuButton);
    expect(document.body.style.overflow).toBe('hidden');

    const closeButton = screen.getByTestId('mobile-nav-close');
    await userEvent.click(closeButton);
    expect(document.body.style.overflow).toBe('');
  });

  it('has correct accessibility attributes', () => {
    renderWithProviders(<Header />);
    const header = screen.getByRole('banner');
    expect(header).toBeInTheDocument();

    const logoElement = screen.getByAltText('IndiVillage Logo');
    expect(logoElement).toHaveAttribute('alt', 'IndiVillage Logo');

    mockUseBreakpoint(Breakpoint.MOBILE);
    renderWithProviders(<Header />);
    const mobileMenuButton = screen.getByTestId('mobile-menu-toggle');
    expect(mobileMenuButton).toHaveAttribute('aria-label', 'Toggle navigation menu');
    expect(mobileMenuButton).toHaveAttribute('aria-expanded', 'false');
  });

  it('navigation is keyboard navigable', async () => {
    mockUseBreakpoint(Breakpoint.DESKTOP);
    renderWithProviders(<Header />);
    const contactButton = screen.getByText('Contact');
    await userEvent.tab();
    expect(contactButton).toHaveFocus();
  });
});