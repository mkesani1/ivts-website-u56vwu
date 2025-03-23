import React from 'react'; // version ^18.2.0
import { render, screen, waitFor, within } from '@testing-library/react'; // version ^14.0.0
import userEvent from '@testing-library/user-event'; // version ^14.4.3
import { describe, it, expect, beforeEach, jest } from '@jest/globals'; // version ^29.5.0

import ServicesPage from '../../src/app/services/page';
import { renderWithProviders } from '../../src/utils/testing';
import { mockServices } from '../mocks/data';
import { ROUTES } from '../../src/constants/routes';
import { ServiceCategory } from '../../src/types/content';

// Mock for Next.js navigation hooks and components
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
  }),
}));

// Mock for the contentService to return predictable test data
jest.mock('../../src/services/contentService', () => ({
  getServices: jest.fn().mockResolvedValue(mockServices),
}));

describe('ServicesPage', () => {
  beforeEach(() => {
    // Reset any mocks or state between tests
    (jest.mocked(require('../../src/services/contentService').getServices)).mockClear();
  });

  it('should render the services page with page header', async () => {
    // Render the ServicesPage component with test providers
    renderWithProviders(<ServicesPage />);

    // Verify the page title is present
    const pageTitle = await screen.findByText('Our AI Services');
    expect(pageTitle).toBeInTheDocument();

    // Verify the breadcrumb navigation is present
    const breadcrumb = screen.getByRole('navigation', { name: 'Breadcrumb' });
    expect(breadcrumb).toBeInTheDocument();

    // Verify the page introduction text is present
    const introText = await screen.findByText(/IndiVillage offers a comprehensive suite of AI-as-a-service solutions/i);
    expect(introText).toBeInTheDocument();
  });

  it('should render all service categories', async () => {
    // Render the ServicesPage component with test providers
    renderWithProviders(<ServicesPage />);

    // Verify that all service categories are present (Data Collection, Data Preparation, AI Model Development, Human-in-the-Loop)
    const dataCollectionHeader = await screen.findByRole('heading', { name: /Data Collection/i });
    expect(dataCollectionHeader).toBeInTheDocument();

    const dataPreparationHeader = await screen.findByRole('heading', { name: /Data Preparation/i });
    expect(dataPreparationHeader).toBeInTheDocument();

    const aiModelDevelopmentHeader = await screen.findByRole('heading', { name: /AI Model Development/i });
    expect(aiModelDevelopmentHeader).toBeInTheDocument();

    const humanInTheLoopHeader = await screen.findByRole('heading', { name: /Human-in-the-Loop/i });
    expect(humanInTheLoopHeader).toBeInTheDocument();
  });

  it('should render service cards for each service', async () => {
    // Render the ServicesPage component with test providers
    renderWithProviders(<ServicesPage />);

    // Verify that service cards are rendered for each service in mockServices
    await waitFor(() => {
      mockServices.forEach(service => {
        const serviceCard = screen.getByRole('article', {
          name: service.name,
        });
        expect(serviceCard).toBeInTheDocument();

        // Verify each service card has a title, description, and icon
        const title = within(serviceCard).getByRole('heading', { name: service.name });
        expect(title).toBeInTheDocument();

        const description = within(serviceCard).getByText(service.description);
        expect(description).toBeInTheDocument();

        // Verify each service card has a 'Learn More' link
        const learnMoreLink = within(serviceCard).getByRole('link', { name: /Learn More/i });
        expect(learnMoreLink).toBeInTheDocument();
      });
    });
  });

  it('should navigate to service detail page when clicking on a service card', async () => {
    // Set up mock for Next.js router/navigation
    const pushMock = jest.fn();
    jest.mock('next/router', () => ({
      useRouter: () => ({
        push: pushMock,
      }),
    }));

    // Render the ServicesPage component with test providers
    renderWithProviders(<ServicesPage />);

    // Click on a service card 'Learn More' link
    const learnMoreLink = await screen.findByRole('link', { name: /Learn More/i });
    await userEvent.click(learnMoreLink);

    // Verify navigation to the correct service detail page is triggered with the correct slug
    expect(pushMock).toHaveBeenCalledWith(ROUTES.SERVICES.DETAIL.replace('[slug]', mockServices[0].slug));
  });

  it('should render the call-to-action section', async () => {
    // Render the ServicesPage component with test providers
    renderWithProviders(<ServicesPage />);

    // Verify the CTA heading is present
    const ctaHeading = await screen.findByRole('heading', { name: /Ready to Transform Your Business?/i });
    expect(ctaHeading).toBeInTheDocument();

    // Verify the 'Request Demo' button is present
    const requestDemoButton = await screen.findByRole('link', { name: /Request Demo/i });
    expect(requestDemoButton).toBeInTheDocument();

    // Verify the 'Upload Sample Data' button is present
    const uploadSampleDataButton = await screen.findByRole('link', { name: /Upload Sample Data/i });
    expect(uploadSampleDataButton).toBeInTheDocument();

    // Verify the 'Contact Us' button is present
    const contactUsButton = await screen.findByRole('link', { name: /Contact Us/i });
    expect(contactUsButton).toBeInTheDocument();
  });

  it('should filter services when a category is provided', async () => {
    // Mock the getServices function to simulate category filtering
    const mockGetServices = jest.fn().mockResolvedValue([mockServices[0]]);
    (require('../../src/services/contentService') as any).getServices = mockGetServices;

    // Render the ServicesPage component with a category parameter
    renderWithProviders(<ServicesPage category={ServiceCategory.DATA_COLLECTION} />);

    // Verify only services from the specified category are displayed
    await waitFor(() => {
      const serviceCard = screen.getByRole('article', {
        name: mockServices[0].name,
      });
      expect(serviceCard).toBeInTheDocument();
    });

    // Verify the correct category heading is displayed
    const categoryHeading = await screen.findByRole('heading', { name: /Data Collection/i });
    expect(categoryHeading).toBeInTheDocument();
  });

  it('should handle empty services data gracefully', async () => {
    // Mock the getServices function to return an empty array
    (require('../../src/services/contentService') as any).getServices = jest.fn().mockResolvedValue([]);

    // Render the ServicesPage component with test providers
    renderWithProviders(<ServicesPage />);

    // Verify a 'No services found' message is displayed
    const noServicesMessage = await screen.findByText(/No services found/i);
    expect(noServicesMessage).toBeInTheDocument();
  });

  it('should handle error state gracefully', async () => {
    // Mock the getServices function to throw an error
    (require('../../src/services/contentService') as any).getServices = jest.fn().mockRejectedValue(new Error('Failed to fetch services'));

    // Render the ServicesPage component with test providers
    renderWithProviders(<ServicesPage />);

    // Verify an error message is displayed
    const errorMessage = await screen.findByText(/Failed to fetch services/i);
    expect(errorMessage).toBeInTheDocument();
  });
});