import React from 'react'; // version ^18.2.0
import { screen, waitFor, fireEvent } from '@testing-library/react'; // version ^14.0.0
import userEvent from '@testing-library/user-event'; // version ^14.4.3
import { vi } from 'vitest'; // version ^0.34.0

import DemoRequestForm from '../../src/components/forms/DemoRequestForm';
import { renderWithProviders } from '../../src/utils/testing';
import { mockDemoRequestFormData } from '../mocks/data';
import { submitDemoRequestWithValidation } from '../../src/services/formSubmissionService';
import { FormStatus } from '../../src/types/forms';

/**
 * Test suite for the DemoRequestForm component
 */
describe('DemoRequestForm', () => {
  // Setup function that runs before each test
  beforeEach(() => {
    // Reset all mocks before each test
    vi.resetAllMocks();

    // Mock the submitDemoRequestWithValidation function
    vi.mock('../../src/services/formSubmissionService', async () => {
      const actual = await vi.importActual('../../src/services/formSubmissionService');
      return {
        ...actual,
        submitDemoRequestWithValidation: vi.fn(),
      };
    });
  });

  /**
   * Tests that the form renders with all required fields and elements
   */
  it('renders the form correctly', () => {
    // Render the DemoRequestForm component with renderWithProviders
    renderWithProviders(<DemoRequestForm />);

    // Check that all form fields are present (first name, last name, email, etc.)
    expect(screen.getByLabelText(/First Name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Last Name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Company/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Job Title/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Services of Interest/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Preferred Date/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Preferred Time/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Time Zone/i)).toBeInTheDocument();

    // Check that the submit button is present and enabled
    expect(screen.getByRole('button', { name: /Request Demo/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Request Demo/i })).toBeEnabled();
  });

  /**
   * Tests that validation errors are displayed when submitting an empty form
   */
  it('displays validation errors when submitting empty form', async () => {
    // Render the DemoRequestForm component
    renderWithProviders(<DemoRequestForm />);

    // Submit the form without filling any fields
    const submitButton = screen.getByRole('button', { name: /Request Demo/i });
    await userEvent.click(submitButton);

    // Check that validation error messages are displayed for required fields
    await waitFor(() => {
      expect(screen.getByText(/This field is required/i)).toBeVisible();
    });
  });

  /**
   * Tests that email validation works correctly
   */
  it('validates email format', async () => {
    // Render the DemoRequestForm component
    renderWithProviders(<DemoRequestForm />);

    // Enter an invalid email format
    const emailInput = screen.getByLabelText(/Email/i);
    await userEvent.type(emailInput, 'invalid-email');

    // Submit the form
    const submitButton = screen.getByRole('button', { name: /Request Demo/i });
    await userEvent.click(submitButton);

    // Check that email validation error is displayed
    await waitFor(() => {
      expect(screen.getByText(/Please enter a valid email address/i)).toBeVisible();
    });
  });

  /**
   * Tests that phone number validation works correctly
   */
  it('validates phone number format', async () => {
    // Render the DemoRequestForm component
    renderWithProviders(<DemoRequestForm />);

    // Enter an invalid phone number format
    const phoneInput = screen.getByLabelText(/Phone/i);
    await userEvent.type(phoneInput, 'invalid-phone');

    // Submit the form
    const submitButton = screen.getByRole('button', { name: /Request Demo/i });
    await userEvent.click(submitButton);

    // Check that phone validation error is displayed
    await waitFor(() => {
      expect(screen.getByText(/Please enter a valid phone number/i)).toBeVisible();
    });
  });

  /**
   * Tests that the form submits successfully when all data is valid
   */
  it('submits the form successfully with valid data', async () => {
    // Mock submitDemoRequestWithValidation to return success
    (submitDemoRequestWithValidation as vi.Mock).mockResolvedValue({ success: true, message: 'Success' });

    // Render the DemoRequestForm component
    renderWithProviders(<DemoRequestForm />);

    // Fill all required fields with valid data
    await fillDemoRequestForm(userEvent.setup());

    // Submit the form
    await submitForm(userEvent.setup());

    // Check that submitDemoRequestWithValidation was called with correct data
    expect(submitDemoRequestWithValidation).toHaveBeenCalledWith(expect.objectContaining(mockDemoRequestFormData));

    // Verify that success message is displayed
    await waitFor(() => {
      expect(screen.getByText(/Your demo request has been submitted successfully!/i)).toBeVisible();
    });
  });

  /**
   * Tests that the form shows loading state while submitting
   */
  it('shows loading state during submission', async () => {
    // Mock submitDemoRequestWithValidation to return a delayed promise
    (submitDemoRequestWithValidation as vi.Mock).mockImplementation(() => new Promise(resolve => setTimeout(() => resolve({ success: true, message: 'Success' }), 500)));

    // Render the DemoRequestForm component
    renderWithProviders(<DemoRequestForm />);

    // Fill all required fields with valid data
    await fillDemoRequestForm(userEvent.setup());

    // Submit the form
    await submitForm(userEvent.setup());

    // Check that submit button shows loading state
    expect(screen.getByRole('button', { name: /Request Demo/i })).toHaveAttribute('aria-busy', 'true');

    // Check that form status is SUBMITTING
    expect(screen.getByRole('button', { name: /Request Demo/i })).toBeDisabled();
  });

  /**
   * Tests that the form handles submission errors correctly
   */
  it('handles submission errors correctly', async () => {
    // Mock submitDemoRequestWithValidation to return an error
    (submitDemoRequestWithValidation as vi.Mock).mockRejectedValue(new Error('Submission failed'));

    // Render the DemoRequestForm component
    renderWithProviders(<DemoRequestForm />);

    // Fill all required fields with valid data
    await fillDemoRequestForm(userEvent.setup());

    // Submit the form
    await submitForm(userEvent.setup());

    // Check that error message is displayed
    await waitFor(() => {
      expect(screen.getByText(/Submission failed/i)).toBeVisible();
    });

    // Verify that form is still editable
    expect(screen.getByRole('button', { name: /Request Demo/i })).toBeEnabled();
  });

  /**
   * Tests that the onSuccess callback is called when submission is successful
   */
  it('calls onSuccess callback when submission is successful', async () => {
    // Create a mock onSuccess function
    const onSuccess = vi.fn();

    // Mock submitDemoRequestWithValidation to return success
    (submitDemoRequestWithValidation as vi.Mock).mockResolvedValue({ success: true, message: 'Success' });

    // Render the DemoRequestForm component with onSuccess prop
    renderWithProviders(<DemoRequestForm onSuccess={onSuccess} />);

    // Fill all required fields with valid data
    await fillDemoRequestForm(userEvent.setup());

    // Submit the form
    await submitForm(userEvent.setup());

    // Verify that onSuccess callback was called
    await waitFor(() => {
      expect(onSuccess).toHaveBeenCalledTimes(1);
    });
  });

  /**
   * Tests that the form handles CAPTCHA verification correctly
   */
  it('handles CAPTCHA verification correctly', async () => {
    // Mock CAPTCHA verification functions
    const mockExecuteRecaptcha = vi.fn().mockResolvedValue('mock-captcha-token');
    vi.mock('../../src/lib/recaptcha', () => ({
      executeRecaptchaV3: mockExecuteRecaptcha,
    }));

    // Mock submitDemoRequestWithValidation to return success
    (submitDemoRequestWithValidation as vi.Mock).mockResolvedValue({ success: true, message: 'Success' });

    // Render the DemoRequestForm component
    renderWithProviders(<DemoRequestForm />);

    // Fill all required fields with valid data
    await fillDemoRequestForm(userEvent.setup());

    // Trigger CAPTCHA verification
    const submitButton = screen.getByRole('button', { name: /Request Demo/i });
    await userEvent.click(submitButton);

    // Verify that form submission includes CAPTCHA token
    expect(submitDemoRequestWithValidation).toHaveBeenCalledWith(
      expect.objectContaining({
        ...mockDemoRequestFormData,
        recaptchaToken: 'mock-captcha-token',
      })
    );
  });
});

/**
 * Helper function to fill all fields in the demo request form
 * @param user UserEvent instance for simulating user interactions
 * @param formData Optional custom form data to use instead of default mock data
 * @returns Promise that resolves when all fields are filled
 */
const fillDemoRequestForm = async (user: any, formData: Partial<DemoRequestFormData> = {}) => {
  const data = { ...mockDemoRequestFormData, ...formData };

  await user.type(screen.getByLabelText(/First Name/i), data.firstName);
  await user.type(screen.getByLabelText(/Last Name/i), data.lastName);
  await user.type(screen.getByLabelText(/Email/i), data.email);
  await user.type(screen.getByLabelText(/Phone/i), data.phone);
  await user.type(screen.getByLabelText(/Company/i), data.company);
  await user.type(screen.getByLabelText(/Job Title/i), data.jobTitle);

  // Select service interests
  const serviceInterestSelect = screen.getByLabelText(/Services of Interest/i);
  await user.click(serviceInterestSelect);
  const serviceInterestOptions = within(serviceInterestSelect).getAllRole('option');
  for (const option of serviceInterestOptions) {
    if (data.serviceInterests.includes(option.value)) {
      await user.click(option);
    }
  }
  await user.click(serviceInterestSelect); // Close the select

  await user.type(screen.getByLabelText(/Preferred Date/i), data.preferredDate);
  await user.type(screen.getByLabelText(/Preferred Time/i), data.preferredTime);

  // Select time zone
  const timeZoneSelect = screen.getByLabelText(/Time Zone/i);
  await user.selectOptions(timeZoneSelect, data.timeZone);

  await user.type(screen.getByLabelText(/Project Details/i), data.projectDetails);

  // Select referral source
  const referralSourceSelect = screen.getByLabelText(/How did you hear about us?/i);
  await user.selectOptions(referralSourceSelect, data.referralSource);
};

/**
 * Helper function to submit the form
 * @param user UserEvent instance for simulating user interactions
 * @returns Promise that resolves when form is submitted
 */
const submitForm = async (user: any) => {
  const submitButton = screen.getByRole('button', { name: /Request Demo/i });
  await user.click(submitButton);
};