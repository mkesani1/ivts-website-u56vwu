import React from 'react'; // version ^18.2.0
import { render, screen, waitFor, within } from '@testing-library/react'; // version ^14.0.0
import userEvent from '@testing-library/user-event'; // version ^14.4.3
import { describe, it, expect, beforeEach, jest } from '@jest/globals'; // version ^29.5.0

import HomePage from '../../src/app/page';
import { renderWithProviders } from '../../src/utils/testing';
import { mockServices, mockCaseStudies } from '../mocks/data';
import { ROUTES } from '../../src/constants/routes';

// Mock for Next.js navigation hooks and components
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
  }),
}));

describe('HomePage', () => {
  beforeEach(() => {
    // Reset mocks before each test
    jest.clearAllMocks();
  });

  it('should render the hero section with headline and CTA buttons', async () => {
    // Render the HomePage component with test providers
    renderWithProviders(<HomePage />);

    // Verify the hero headline text is present
    const headlineElement = await screen.findByText(/AI-Powered Solutions with Social Impact/i);
    expect(headlineElement).toBeInTheDocument();

    // Verify the hero subheading text is present
    const subheadingElement = await screen.findByText(/Transform your business with AI solutions that create positive social change/i);
    expect(subheadingElement).toBeInTheDocument();

    // Verify the 'Learn More' button is present
    const learnMoreButton = screen.getByRole('link', { name: /Learn More/i });
    expect(learnMoreButton).toBeInTheDocument();

    // Verify the 'Request Demo' button is present and links to the correct route
    const requestDemoButton = screen.getByRole('link', { name: /Request Demo/i });
    expect(requestDemoButton).toBeInTheDocument();
  });

  it('should render the service overview section with all services', async () => {
    // Render the HomePage component with test providers
    renderWithProviders(<HomePage />);

    // Verify the service section heading is present
    const serviceSectionHeading = await screen.findByText(/OUR SERVICES/i);
    expect(serviceSectionHeading).toBeInTheDocument();

    // Verify all service cards are rendered (Data Collection, Data Preparation, AI Model Development, Human-in-the-Loop)
    const dataCollectionCard = await screen.findByText(/Data Collection/i);
    expect(dataCollectionCard).toBeInTheDocument();

    const dataPreparationCard = await screen.findByText(/Data Preparation/i);
    expect(dataPreparationCard).toBeInTheDocument();

    const aiModelDevelopmentCard = await screen.findByText(/AI Model Development/i);
    expect(aiModelDevelopmentCard).toBeInTheDocument();

    const humanInTheLoopCard = await screen.findByText(/Human-in-the-Loop/i);
    expect(humanInTheLoopCard).toBeInTheDocument();

    // Verify each service card has a title, description, and 'Learn More' link
    const serviceCards = await screen.findAllByRole('article');
    expect(serviceCards.length).toBe(4);

    for (const card of serviceCards) {
      expect(within(card).getByRole('heading')).toBeInTheDocument();
      expect(within(card).getByText(/Comprehensive/i)).toBeInTheDocument();
      expect(within(card).getByRole('link', { name: /Learn More/i })).toBeInTheDocument();
    }
  });

  it('should render the impact overview section with metrics', async () => {
    // Render the HomePage component with test providers
    renderWithProviders(<HomePage />);

    // Verify the impact section heading is present
    const impactSectionHeading = await screen.findByText(/AI FOR GOOD: OUR IMPACT/i);
    expect(impactSectionHeading).toBeInTheDocument();

    // Verify the impact metrics are displayed (jobs created, communities impacted, lives transformed)
    const jobsCreatedMetric = await screen.findByText(/Jobs Created/i);
    expect(jobsCreatedMetric).toBeInTheDocument();

    const communitiesImpactedMetric = await screen.findByText(/Communities Impacted/i);
    expect(communitiesImpactedMetric).toBeInTheDocument();

    const livesTransformedMetric = await screen.findByText(/Lives Transformed/i);
    expect(livesTransformedMetric).toBeInTheDocument();

    // Verify the mission statement is present
    const missionStatement = await screen.findByText(/Creating sustainable livelihoods through technology/i);
    expect(missionStatement).toBeInTheDocument();

    // Verify the 'Learn About Our Foundation' link is present
    const foundationLink = screen.getByRole('link', { name: /Learn About Our Foundation/i });
    expect(foundationLink).toBeInTheDocument();
  });

  it('should render the case study highlight section', async () => {
    // Render the HomePage component with test providers
    renderWithProviders(<HomePage />);

    // Verify case study highlights are displayed
    const caseStudySectionHeading = await screen.findByText(/CASE STUDIES/i);
    expect(caseStudySectionHeading).toBeInTheDocument();

    // Verify each case study has a title, client name, and description
    const caseStudyCards = await screen.findAllByRole('article');
    expect(caseStudyCards.length).toBeGreaterThan(0);

    for (const card of caseStudyCards) {
      expect(within(card).getByRole('heading')).toBeInTheDocument();
      expect(within(card).getByText(/GlobalShop/i)).toBeInTheDocument();
      expect(within(card).getByText(/With over 1 million products/i)).toBeInTheDocument();
      expect(within(card).getByRole('link', { name: /Read Case Study/i })).toBeInTheDocument();
    }
  });

  it('should render the partner logos section', async () => {
    // Render the HomePage component with test providers
    renderWithProviders(<HomePage />);

    // Verify the partner section heading is present
    const partnerSectionHeading = await screen.findByText(/TRUSTED BY LEADING COMPANIES/i);
    expect(partnerSectionHeading).toBeInTheDocument();

    // Verify partner logos are displayed
    const partnerLogos = await screen.findAllByRole('img');
    expect(partnerLogos.length).toBeGreaterThan(0);
  });

  it('should render the CTA section with action buttons', async () => {
    // Render the HomePage component with test providers
    renderWithProviders(<HomePage />);

    // Verify the CTA heading is present
    const ctaHeading = await screen.findByText(/READY TO TRANSFORM YOUR BUSINESS?/i);
    expect(ctaHeading).toBeInTheDocument();

    // Verify the 'Request Demo' button is present and links to the correct route
    const requestDemoButton = screen.getByRole('link', { name: /Request Demo/i });
    expect(requestDemoButton).toBeInTheDocument();
    expect(requestDemoButton).toHaveAttribute('href', ROUTES.REQUEST_DEMO);

    // Verify the 'Upload Sample Data' button is present and links to the correct route
    const uploadSampleButton = screen.getByRole('link', { name: /Upload Sample Data/i });
    expect(uploadSampleButton).toBeInTheDocument();
    expect(uploadSampleButton).toHaveAttribute('href', ROUTES.UPLOAD_SAMPLE.INDEX);

    // Verify the 'Contact Us' button is present and links to the correct route
    const contactUsButton = screen.getByRole('link', { name: /Contact Us/i });
    expect(contactUsButton).toBeInTheDocument();
    expect(contactUsButton).toHaveAttribute('href', ROUTES.CONTACT);
  });

  it('should navigate to the correct page when CTA buttons are clicked', async () => {
    // Render the HomePage component with test providers
    const { mockAnalyticsContext } = renderWithProviders(<HomePage />);

    // Set up mock for Next.js router/navigation
    const pushMock = jest.fn();
    jest.spyOn(require('next/navigation'), 'useRouter').mockReturnValue({ push: pushMock });

    // Click on the 'Request Demo' button
    const requestDemoButton = screen.getByRole('link', { name: /Request Demo/i });
    await userEvent.click(requestDemoButton);

    // Verify navigation to the demo request page is triggered
    expect(pushMock).toHaveBeenCalledWith(ROUTES.REQUEST_DEMO);

    // Click on the 'Upload Sample Data' button
    const uploadSampleButton = screen.getByRole('link', { name: /Upload Sample Data/i });
    await userEvent.click(uploadSampleButton);

    // Verify navigation to the upload sample page is triggered
    expect(pushMock).toHaveBeenCalledWith(ROUTES.UPLOAD_SAMPLE.INDEX);

    // Click on the 'Contact Us' button
    const contactUsButton = screen.getByRole('link', { name: /Contact Us/i });
    await userEvent.click(contactUsButton);

    // Verify navigation to the contact page is triggered
    expect(pushMock).toHaveBeenCalledWith(ROUTES.CONTACT);
  });

  it('should navigate to service details when service card is clicked', async () => {
    // Render the HomePage component with test providers
    const { mockAnalyticsContext } = renderWithProviders(<HomePage />);

    // Set up mock for Next.js router/navigation
    const pushMock = jest.fn();
    jest.spyOn(require('next/navigation'), 'useRouter').mockReturnValue({ push: pushMock });

    // Click on a service card 'Learn More' link
    const learnMoreLink = await screen.findByRole('link', { name: /Learn More/i });
    await userEvent.click(learnMoreLink);

    // Verify navigation to the correct service details page is triggered
    expect(pushMock).toHaveBeenCalled();
  });
});