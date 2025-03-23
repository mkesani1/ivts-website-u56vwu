import React from 'react'; // version ^18.2.0
import { screen, waitFor, fireEvent } from '@testing-library/react'; // version ^14.0.0
import userEvent from '@testing-library/user-event'; // version ^14.4.3
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest'; // version ^0.34.3

import ContactForm from '../../../src/components/forms/ContactForm';
import { renderWithProviders } from '../../../src/utils/testing';
import { mockContactFormData } from '../../mocks/data';
import { submitContactFormWithValidation } from '../../../src/services/formSubmissionService';

// Mock the submitContactFormWithValidation function
vi.mock('../../../src/services/formSubmissionService', () => ({
  submitContactFormWithValidation: vi.fn()
}));

/**
 * Setup function to configure mocks before each test
 */
describe('setup', () => {
  beforeEach(() => {
    // Mock the submitContactFormWithValidation function
    (submitContactFormWithValidation as vi.Mock).mockClear();
  });
});

/**
 * Cleanup function to reset mocks after each test
 */
describe('cleanup', () => {
  afterEach(() => {
    // Reset all mocks to their original implementation
    vi.restoreAllMocks();
  });
});

/**
 * Helper function to fill out the contact form with valid data
 * @param user UserEvent instance
 * @param overrides Optional field value overrides
 */
const fillContactForm = async (user: any, overrides: Partial<typeof mockContactFormData> = {}) => {
  const formData = { ...mockContactFormData, ...overrides };

  // Type name into the name field
  await user.type(screen.getByLabelText(/Name/i), formData.name);

  // Type email into the email field
  await user.type(screen.getByLabelText(/Email/i), formData.email);

  // Type phone into the phone field
  await user.type(screen.getByLabelText(/Phone \(Optional\)/i), formData.phone);

  // Type company into the company field
  await user.type(screen.getByLabelText(/Company/i), formData.company);

  // Type message into the message field
  await user.type(screen.getByLabelText(/Message/i), formData.message);
};

describe('ContactForm', () => {
  it('renders correctly', async () => {
    // Render the ContactForm component with providers
    renderWithProviders(<ContactForm />);

    // Check that all form fields are present (name, email, phone, company, message)
    expect(screen.getByLabelText(/Name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Phone \(Optional\)/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Company/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Message/i)).toBeInTheDocument();

    // Check that the submit button is present and enabled
    const submitButton = screen.getByRole('button', { name: /Submit/i });
    expect(submitButton).toBeInTheDocument();
    expect(submitButton).toBeEnabled();
  });

  it('displays validation errors for required fields', async () => {
    // Render the ContactForm component
    renderWithProviders(<ContactForm />);

    // Click the submit button without filling any fields
    const submitButton = screen.getByRole('button', { name: /Submit/i });
    await fireEvent.click(submitButton);

    // Check that validation error messages are displayed for required fields
    expect(screen.getByText(/This field is required./i)).toBeVisible();

    // Verify that the form was not submitted
    expect(submitContactFormWithValidation).not.toHaveBeenCalled();
  });

  it('validates email format', async () => {
    // Render the ContactForm component
    renderWithProviders(<ContactForm />);

    // Fill the form with an invalid email format
    const user = userEvent.setup();
    await fillContactForm(user, { email: 'invalid-email' });

    // Submit the form
    const submitButton = screen.getByRole('button', { name: /Submit/i });
    await fireEvent.click(submitButton);

    // Check that an email validation error is displayed
    expect(screen.getByText(/Please enter a valid email address./i)).toBeVisible();

    // Verify that the form was not submitted
    expect(submitContactFormWithValidation).not.toHaveBeenCalled();
  });

  it('submits the form with valid data', async () => {
    // Mock submitContactFormWithValidation to return a successful response
    (submitContactFormWithValidation as vi.Mock).mockResolvedValue({ success: true, message: 'Success' });

    // Create a mock onSuccess callback function
    const onSuccess = vi.fn();

    // Render the ContactForm component
    const {mockAnalyticsContext} = renderWithProviders(<ContactForm onSuccess={onSuccess} />);

    // Fill all form fields with valid data
    const user = userEvent.setup();
    await fillContactForm(user);

    // Submit the form
    const submitButton = screen.getByRole('button', { name: /Submit/i });
    await fireEvent.click(submitButton);

    // Verify that submitContactFormWithValidation was called with correct data
    expect(submitContactFormWithValidation).toHaveBeenCalledWith(mockContactFormData);

    // Check that the form shows a success message
    await waitFor(() => {
      expect(screen.getByText(/Success/i)).toBeVisible();
    });

    // Verify that onSuccess callback was called
    await waitFor(() => {
      expect(onSuccess).toHaveBeenCalled();
    });
  });

  it('handles submission errors', async () => {
    // Mock submitContactFormWithValidation to return an error
    (submitContactFormWithValidation as vi.Mock).mockResolvedValue({ success: false, message: 'Error' });

    // Create a mock onSuccess callback function
    const onSuccess = vi.fn();

    // Render the ContactForm component
    renderWithProviders(<ContactForm onSuccess={onSuccess} />);

    // Fill all form fields with valid data
    const user = userEvent.setup();
    await fillContactForm(user);

    // Submit the form
    const submitButton = screen.getByRole('button', { name: /Submit/i });
    await fireEvent.click(submitButton);

    // Check that an error message is displayed
    await waitFor(() => {
      expect(screen.getByText(/Error/i)).toBeVisible();
    });

    // Verify that onSuccess callback was not called
    expect(onSuccess).not.toHaveBeenCalled();
  });

  it('disables submit button during submission', async () => {
    // Mock submitContactFormWithValidation to return a delayed response
    (submitContactFormWithValidation as vi.Mock).mockImplementation(() => {
      return new Promise((resolve) => {
        setTimeout(() => {
          resolve({ success: true, message: 'Success' });
        }, 1000);
      });
    });

    // Render the ContactForm component
    renderWithProviders(<ContactForm />);

    // Fill all form fields with valid data
    const user = userEvent.setup();
    await fillContactForm(user);

    // Submit the form
    const submitButton = screen.getByRole('button', { name: /Submit/i });
    fireEvent.click(submitButton);

    // Check that the submit button is disabled and shows loading state
    expect(submitButton).toBeDisabled();
    expect(submitButton).toHaveAttribute('aria-busy', 'true');

    // Verify that the form cannot be submitted again while processing
    await waitFor(() => {
      expect(submitContactFormWithValidation).toHaveBeenCalledTimes(1);
    });
  });

  it('resets form after successful submission', async () => {
    // Mock submitContactFormWithValidation to return a successful response
    (submitContactFormWithValidation as vi.Mock).mockResolvedValue({ success: true, message: 'Success' });

    // Render the ContactForm component
    const {mockAnalyticsContext} = renderWithProviders(<ContactForm />);

    // Fill all form fields with valid data
    const user = userEvent.setup();
    await fillContactForm(user);

    // Submit the form
    const submitButton = screen.getByRole('button', { name: /Submit/i });
    fireEvent.click(submitButton);

    // Wait for successful submission
    await waitFor(() => {
      expect(screen.getByText(/Success/i)).toBeVisible();
    });

    // Click the 'Send another message' button
    const anotherMessageButton = screen.getByRole('button', { name: /Submit Another/i });
    await fireEvent.click(anotherMessageButton);

    // Verify that all form fields are empty
    expect((screen.getByLabelText(/Name/i) as HTMLInputElement).value).toBe('');
    expect((screen.getByLabelText(/Email/i) as HTMLInputElement).value).toBe('');
    expect((screen.getByLabelText(/Phone \(Optional\)/i) as HTMLInputElement).value).toBe('');
    expect((screen.getByLabelText(/Company/i) as HTMLInputElement).value).toBe('');
    expect((screen.getByLabelText(/Message/i) as HTMLTextAreaElement).value).toBe('');

    // Verify that the form is ready for a new submission
    expect(submitButton).toBeEnabled();
  });

  it('integrates with CAPTCHA verification', async () => {
    // Mock the CAPTCHA verification function
    const mockExecuteRecaptchaV3 = vi.fn().mockResolvedValue('mock-captcha-token');
    vi.mock('../../../src/lib/recaptcha', () => ({
      executeRecaptchaV3: mockExecuteRecaptchaV3
    }));

    // Mock submitContactFormWithValidation to return a successful response
    (submitContactFormWithValidation as vi.Mock).mockResolvedValue({ success: true, message: 'Success' });

    // Render the ContactForm component
    renderWithProviders(<ContactForm />);

    // Fill all form fields with valid data
    const user = userEvent.setup();
    await fillContactForm(user);

    // Submit the form
    const submitButton = screen.getByRole('button', { name: /Submit/i });
    await fireEvent.click(submitButton);

    // Verify that the form submission includes the CAPTCHA token
    await waitFor(() => {
      expect(submitContactFormWithValidation).toHaveBeenCalledWith({
        ...mockContactFormData,
        recaptchaToken: 'mock-captcha-token'
      });
    });
  });
});