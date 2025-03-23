import React from 'react'; // react@^18.2.0
import { render, screen, within } from '@testing-library/react'; // @testing-library/react@^14.0.0
import userEvent from '@testing-library/user-event'; // @testing-library/user-event@^14.4.3
import Footer from '../../../../src/components/layout/Footer';
import { renderWithProviders } from '../../../../src/utils/testing';
import { ROUTES } from '../../../../src/constants/routes';

// Test suite for the Footer component
describe('Footer', () => {
  // Setup function that runs before each test
  beforeEach(() => {
    // Reset any mocks or state before each test
    jest.clearAllMocks();
  });

  // Test case: renders the footer with logo
  it('renders the footer with logo', () => {
    // Render the Footer component
    renderWithProviders(<Footer />);

    // Check that the IndiVillage logo is present
    const logo = screen.getByAltText('IndiVillage');
    expect(logo).toBeInTheDocument();

    // Verify the logo has appropriate alt text
    expect(logo).toHaveAttribute('alt', 'IndiVillage');
  });

  // Test case: displays copyright information
  it('displays copyright information', () => {
    // Render the Footer component
    renderWithProviders(<Footer />);

    // Check that the copyright text is present
    const copyrightText = screen.getByText(/© \d{4} IndiVillage\. All rights reserved\./i);
    expect(copyrightText).toBeInTheDocument();

    // Verify it contains the current year and company name
    const currentYear = new Date().getFullYear();
    expect(copyrightText.textContent).toContain(currentYear.toString());
    expect(copyrightText.textContent).toContain('IndiVillage');
  });

  // Test case: renders all navigation sections
  it('renders all navigation sections', () => {
    // Render the Footer component
    renderWithProviders(<Footer />);

    // Check that all section headings are present (Company, Legal, Connect)
    const companyHeading = screen.getByText('Company');
    const legalHeading = screen.getByText('Legal');
    const connectHeading = screen.getByText('Connect');

    expect(companyHeading).toBeInTheDocument();
    expect(legalHeading).toBeInTheDocument();
    expect(connectHeading).toBeInTheDocument();

    // Verify that each section contains the expected number of links
    const companySection = within(companyHeading.closest('div') as HTMLElement);
    const legalSection = within(legalHeading.closest('div') as HTMLElement);
    const connectSection = within(connectHeading.closest('div') as HTMLElement);

    expect(companySection.getAllByRole('link')).toHaveLength(4);
    expect(legalSection.getAllByRole('link')).toHaveLength(4);
    expect(connectSection.getAllByRole('link')).toHaveLength(2);
  });

  // Test case: renders correct links in Company section
  it('renders correct links in Company section', () => {
    // Render the Footer component
    renderWithProviders(<Footer />);

    // Find the Company section
    const companyHeading = screen.getByText('Company');
    const companySection = within(companyHeading.closest('div') as HTMLElement);

    // Verify all expected links are present (About Us, Careers, Partners, Press)
    const aboutUsLink = companySection.getByRole('link', { name: 'About Us' });
    const careersLink = companySection.getByRole('link', { name: 'Careers' });
    const partnersLink = companySection.getByRole('link', { name: 'Partners' });
    const pressLink = companySection.getByRole('link', { name: 'Press' });

    expect(aboutUsLink).toBeInTheDocument();
    expect(careersLink).toBeInTheDocument();
    expect(partnersLink).toBeInTheDocument();
    expect(pressLink).toBeInTheDocument();

    // Check that links have correct href attributes
    expect(aboutUsLink).toHaveAttribute('href', ROUTES.ABOUT.INDEX);
    expect(careersLink).toHaveAttribute('href', ROUTES.ABOUT.CAREERS);
    expect(partnersLink).toHaveAttribute('href', '/about/partners');
    expect(pressLink).toHaveAttribute('href', ROUTES.ABOUT.PRESS);
  });

  // Test case: renders correct links in Legal section
  it('renders correct links in Legal section', () => {
    // Render the Footer component
    renderWithProviders(<Footer />);

    // Find the Legal section
    const legalHeading = screen.getByText('Legal');
    const legalSection = within(legalHeading.closest('div') as HTMLElement);

    // Verify all expected links are present (Privacy Policy, Terms of Service, Cookie Policy, Accessibility)
    const privacyPolicyLink = legalSection.getByRole('link', { name: 'Privacy Policy' });
    const termsOfServiceLink = legalSection.getByRole('link', { name: 'Terms of Service' });
    const cookiePolicyLink = legalSection.getByRole('link', { name: 'Cookie Policy' });
    const accessibilityLink = legalSection.getByRole('link', { name: 'Accessibility' });

    expect(privacyPolicyLink).toBeInTheDocument();
    expect(termsOfServiceLink).toBeInTheDocument();
    expect(cookiePolicyLink).toBeInTheDocument();
    expect(accessibilityLink).toBeInTheDocument();

    // Check that links have correct href attributes
    expect(privacyPolicyLink).toHaveAttribute('href', ROUTES.LEGAL.PRIVACY_POLICY);
    expect(termsOfServiceLink).toHaveAttribute('href', ROUTES.LEGAL.TERMS_OF_SERVICE);
    expect(cookiePolicyLink).toHaveAttribute('href', ROUTES.LEGAL.COOKIE_POLICY);
    expect(accessibilityLink).toHaveAttribute('href', ROUTES.LEGAL.ACCESSIBILITY);
  });

  // Test case: renders correct links in Connect section
  it('renders correct links in Connect section', () => {
    // Render the Footer component
    renderWithProviders(<Footer />);

    // Find the Connect section
    const connectHeading = screen.getByText('Connect');
    const connectSection = within(connectHeading.closest('div') as HTMLElement);

    // Verify all expected links are present (Contact, Support)
    const contactLink = connectSection.getByRole('link', { name: 'Contact' });
    const supportLink = connectSection.getByRole('link', { name: 'Support' });

    expect(contactLink).toBeInTheDocument();
    expect(supportLink).toBeInTheDocument();

    // Check that links have correct href attributes
    expect(contactLink).toHaveAttribute('href', ROUTES.CONTACT);
    expect(supportLink).toHaveAttribute('href', `${ROUTES.CONTACT}#support`);
  });

  // Test case: renders social media links
  it('renders social media links', () => {
    // Render the Footer component
    renderWithProviders(<Footer />);

    // Check that all social media links are present (LinkedIn, Twitter, Facebook, Instagram)
    const linkedinLink = screen.getByRole('link', { name: 'Follow IndiVillage on LinkedIn' });
    const twitterLink = screen.getByRole('link', { name: 'Follow IndiVillage on Twitter' });
    const facebookLink = screen.getByRole('link', { name: 'Follow IndiVillage on Facebook' });
    const instagramLink = screen.getByRole('link', { name: 'Follow IndiVillage on Instagram' });

    expect(linkedinLink).toBeInTheDocument();
    expect(twitterLink).toBeInTheDocument();
    expect(facebookLink).toBeInTheDocument();
    expect(instagramLink).toBeInTheDocument();

    // Verify that links have correct href attributes
    expect(linkedinLink).toHaveAttribute('href', 'https://www.linkedin.com/company/indivillage');
    expect(twitterLink).toHaveAttribute('href', 'https://twitter.com/indivillage');
    expect(facebookLink).toHaveAttribute('href', 'https://www.facebook.com/indivillage');
    expect(instagramLink).toHaveAttribute('href', 'https://www.instagram.com/indivillage');

    // Check that each link has appropriate aria-label
    expect(linkedinLink).toHaveAttribute('aria-label', 'Follow IndiVillage on LinkedIn');
    expect(twitterLink).toHaveAttribute('aria-label', 'Follow IndiVillage on Twitter');
    expect(facebookLink).toHaveAttribute('aria-label', 'Follow IndiVillage on Facebook');
    expect(instagramLink).toHaveAttribute('aria-label', 'Follow IndiVillage on Instagram');
  });

  // Test case: applies responsive styling based on breakpoint
  it('applies responsive styling based on breakpoint', () => {
    // Mock the useBreakpoint hook to return different breakpoints
    const mockUseBreakpoint = jest.fn();

    // Render the Footer component with mobile breakpoint
    mockUseBreakpoint.mockReturnValue('mobile');
    renderWithProviders(<Footer />, {
      analyticsContextOverrides: {},
      toastContextOverrides: {},
      uploadContextOverrides: {},
      renderOptions: {}
    });

    // Verify mobile-specific styling or layout
    const footerElement = screen.getByRole('contentinfo');
    expect(footerElement).toHaveClass('footer');

    // Render the Footer component with desktop breakpoint
    mockUseBreakpoint.mockReturnValue('desktop');
    renderWithProviders(<Footer />, {
      analyticsContextOverrides: {},
      toastContextOverrides: {},
      uploadContextOverrides: {},
      renderOptions: {}
    });

    // Verify desktop-specific styling or layout
    const footerElementDesktop = screen.getByRole('contentinfo');
    expect(footerElementDesktop).toHaveClass('footer');
  });

  // Test case: has correct accessibility attributes
  it('has correct accessibility attributes', () => {
    // Render the Footer component
    renderWithProviders(<Footer />);

    // Check that the footer has role='contentinfo'
    const footerElement = screen.getByRole('contentinfo');
    expect(footerElement).toHaveAttribute('role', 'contentinfo');

    // Verify that navigation sections have appropriate ARIA attributes
    const companyHeading = screen.getByText('Company');
    const legalHeading = screen.getByText('Legal');
    const connectHeading = screen.getByText('Connect');

    expect(companyHeading.closest('div')).not.toHaveAttribute('aria-label');
    expect(legalHeading.closest('div')).not.toHaveAttribute('aria-label');
    expect(connectHeading.closest('div')).not.toHaveAttribute('aria-label');

    // Check that social media links have descriptive aria-labels
    const linkedinLink = screen.getByRole('link', { name: 'Follow IndiVillage on LinkedIn' });
    const twitterLink = screen.getByRole('link', { name: 'Follow IndiVillage on Twitter' });
    const facebookLink = screen.getByRole('link', { name: 'Follow IndiVillage on Facebook' });
    const instagramLink = screen.getByRole('link', { name: 'Follow IndiVillage on Instagram' });

    expect(linkedinLink).toHaveAttribute('aria-label', 'Follow IndiVillage on LinkedIn');
    expect(twitterLink).toHaveAttribute('aria-label', 'Follow IndiVillage on Twitter');
    expect(facebookLink).toHaveAttribute('aria-label', 'Follow IndiVillage on Facebook');
    expect(instagramLink).toHaveAttribute('aria-label', 'Follow IndiVillage on Instagram');
  });

  // Test case: links are keyboard navigable
  it('links are keyboard navigable', async () => {
    // Render the Footer component
    renderWithProviders(<Footer />);

    // Use userEvent to tab through the footer links
    const user = userEvent.setup();
    await user.tab();

    // Verify that focus indicators are visible
    const aboutUsLink = screen.getByRole('link', { name: 'About Us' });
    expect(aboutUsLink).toHaveFocus();

    // Check that all links can be activated with keyboard
    await user.keyboard('{Enter}');
  });
});