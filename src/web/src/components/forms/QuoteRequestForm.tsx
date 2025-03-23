import React, { useState, useCallback, useEffect } from 'react'; // version 18.2.0
import {
  FormField,
  FormError,
  Captcha,
  Input,
  Select,
  Textarea,
} from './index';
import { Button } from '../ui';
import { useForm } from '../../hooks/useForm';
import {
  submitQuoteRequestWithValidation,
  getQuoteRequestValidationRules,
} from '../../services/formSubmissionService';
import {
  QuoteRequestFormData,
  FormStatus,
} from '../../types/forms';
import { SERVICE_CATEGORIES } from '../../constants/services';

/**
 * Interface defining the props for the QuoteRequestForm component
 */
export interface QuoteRequestFormProps {
  /** Callback function called when form submission is successful */
  onSuccess: () => void;
  /** Optional CSS class name for styling the form */
  className?: string;
}

/**
 * Component for requesting a price quote for IndiVillage's AI services
 */
const QuoteRequestForm: React.FC<QuoteRequestFormProps> = ({
  onSuccess,
  className,
}) => {
  // Initialize form state using useForm hook with validation rules
  const {
    formState,
    handleChange,
    handleBlur,
    handleSubmit,
    setError,
    setStatus,
  } = useForm<QuoteRequestFormData>({
    initialValues: {
      firstName: '',
      lastName: '',
      email: '',
      phone: '',
      company: '',
      jobTitle: '',
      serviceInterests: [],
      projectDetails: '',
      budgetRange: '',
      timeline: '',
      referralSource: '',
    },
    validationRules: getQuoteRequestValidationRules(),
  });

  // State for captcha token
  const [captchaToken, setCaptchaToken] = useState<string | null>(null);

  /**
   * Handler for captcha verification to store the token
   * @param token - The reCAPTCHA token
   */
  const handleVerifyCaptcha = useCallback((token: string) => {
    setCaptchaToken(token);
  }, []);

  /**
   * Handler for captcha error to display error message
   * @param error - The error object
   */
  const handleCaptchaError = useCallback((error: Error) => {
    setError(error.message);
  }, [setError]);

  /**
   * Form submission handler that calls submitQuoteRequestWithValidation
   * @param values - The form values
   */
  const onSubmit = useCallback(async () => {
    if (!captchaToken) {
      setError('Please complete the CAPTCHA verification.');
      return;
    }

    // Prepare form data with captcha token
    const formData: QuoteRequestFormData = {
      ...formState.values,
      serviceInterests: formState.values.serviceInterests ? formState.values.serviceInterests : [],
      recaptchaToken: captchaToken,
    };

    try {
      // Submit form data to API
      await submitQuoteRequestWithValidation(formData);

      // Handle successful submission by calling onSuccess callback
      onSuccess();
    } catch (error: any) {
      // Handle submission errors by displaying error messages
      setError(error.message || 'An error occurred during form submission.');
    } finally {
      // Reset captcha token after submission
      setCaptchaToken(null);
    }
  }, [formState.values, captchaToken, onSuccess, setError]);

  /**
   * Generates service interest options for the select dropdown
   * @returns Array of service interest options with value and label
   */
  const getServiceInterestOptions = useCallback(() => {
    return Object.entries(SERVICE_CATEGORIES).map(([key, category]) => ({
      value: key,
      label: category.title,
    }));
  }, []);

  /**
   * Returns predefined budget range options for the select dropdown
   * @returns Array of budget range options with value and label
   */
  const getBudgetRangeOptions = useCallback(() => {
    return [
      { value: 'under_10k', label: 'Under $10,000' },
      { value: 'between_10k_50k', label: '$10,000 - $50,000' },
      { value: 'between_50k_100k', label: '$50,000 - $100,000' },
      { value: 'between_100k_500k', label: '$100,000 - $500,000' },
      { value: 'over_500k', label: 'Over $500,000' },
      { value: 'not_specified', label: 'Not Specified' },
    ];
  }, []);

  /**
   * Returns predefined timeline options for the select dropdown
   * @returns Array of timeline options with value and label
   */
  const getTimelineOptions = useCallback(() => {
    return [
      { value: 'immediately', label: 'Immediately' },
      { value: 'within_1_month', label: 'Within 1 Month' },
      { value: 'within_3_months', label: 'Within 3 Months' },
      { value: 'within_6_months', label: 'Within 6 Months' },
      { value: 'future_planning', label: 'Future Planning' },
    ];
  }, []);

  /**
   * Returns predefined referral source options for the select dropdown
   * @returns Array of referral source options with value and label
   */
  const getReferralSourceOptions = useCallback(() => {
    return [
      { value: 'google', label: 'Google' },
      { value: 'linkedin', label: 'LinkedIn' },
      { value: 'referral', label: 'Referral' },
      { value: 'other', label: 'Other' },
    ];
  }, []);

  // Create service interest options
  const serviceInterestOptions = getServiceInterestOptions();

  // Create budget range options
  const budgetRangeOptions = getBudgetRangeOptions();

  // Create timeline options
  const timelineOptions = getTimelineOptions();

  // Create referral source options
  const referralSourceOptions = getReferralSourceOptions();

  return (
    <form
      className={className}
      onSubmit={handleSubmit(onSubmit)}
    >
      {/* Show success message when form status is SUCCESS */}
      {formState.status === FormStatus.SUCCESS && (
        <div className="mb-4 text-green-500">
          Thank you for your quote request! We will be in touch soon.
        </div>
      )}

      {/* Show form fields when form status is not SUCCESS */}
      {formState.status !== FormStatus.SUCCESS && (
        <>
          {/* Form-level error message */}
          {formState.error && (
            <FormError error={formState.error} />
          )}

          {/* Personal Information */}
          <FormField
            label="First Name"
            name="firstName"
            required
            error={formState.fields.firstName?.error}
          >
            <Input
              type="text"
              name="firstName"
              value={formState.values.firstName || ''}
              onChange={handleChange}
              onBlur={handleBlur}
              required
            />
          </FormField>

          <FormField
            label="Last Name"
            name="lastName"
            required
            error={formState.fields.lastName?.error}
          >
            <Input
              type="text"
              name="lastName"
              value={formState.values.lastName || ''}
              onChange={handleChange}
              onBlur={handleBlur}
              required
            />
          </FormField>

          <FormField
            label="Email"
            name="email"
            required
            error={formState.fields.email?.error}
          >
            <Input
              type="email"
              name="email"
              value={formState.values.email || ''}
              onChange={handleChange}
              onBlur={handleBlur}
              required
            />
          </FormField>

          <FormField
            label="Phone"
            name="phone"
            error={formState.fields.phone?.error}
          >
            <Input
              type="tel"
              name="phone"
              value={formState.values.phone || ''}
              onChange={handleChange}
              onBlur={handleBlur}
            />
          </FormField>

          {/* Company Information */}
          <FormField
            label="Company"
            name="company"
            required
            error={formState.fields.company?.error}
          >
            <Input
              type="text"
              name="company"
              value={formState.values.company || ''}
              onChange={handleChange}
              onBlur={handleBlur}
              required
            />
          </FormField>

          <FormField
            label="Job Title"
            name="jobTitle"
            required
            error={formState.fields.jobTitle?.error}
          >
            <Input
              type="text"
              name="jobTitle"
              value={formState.values.jobTitle || ''}
              onChange={handleChange}
              onBlur={handleBlur}
              required
            />
          </FormField>

          {/* Project Information */}
          <FormField
            label="Service Interests"
            name="serviceInterests"
            required
            error={formState.fields.serviceInterests?.error}
          >
            <Select
              name="serviceInterests"
              options={serviceInterestOptions}
              value={formState.values.serviceInterests || ''}
              onChange={handleChange}
              onBlur={handleBlur}
              required
            />
          </FormField>

          <FormField
            label="Project Details"
            name="projectDetails"
            required
            error={formState.fields.projectDetails?.error}
          >
            <Textarea
              name="projectDetails"
              value={formState.values.projectDetails || ''}
              onChange={handleChange}
              onBlur={handleBlur}
              rows={4}
              required
            />
          </FormField>

          {/* Budget and Timeline */}
          <FormField
            label="Budget Range"
            name="budgetRange"
            required
            error={formState.fields.budgetRange?.error}
          >
            <Select
              name="budgetRange"
              options={budgetRangeOptions}
              value={formState.values.budgetRange || ''}
              onChange={handleChange}
              onBlur={handleBlur}
              required
            />
          </FormField>

          <FormField
            label="Timeline"
            name="timeline"
            required
            error={formState.fields.timeline?.error}
          >
            <Select
              name="timeline"
              options={timelineOptions}
              value={formState.values.timeline || ''}
              onChange={handleChange}
              onBlur={handleBlur}
              required
            />
          </FormField>

          {/* Referral Source */}
          <FormField
            label="How did you hear about us?"
            name="referralSource"
          >
            <Select
              name="referralSource"
              options={referralSourceOptions}
              value={formState.values.referralSource || ''}
              onChange={handleChange}
              onBlur={handleBlur}
            />
          </FormField>

          {/* CAPTCHA */}
          <Captcha
            onVerify={handleVerifyCaptcha}
            onError={handleCaptchaError}
            action="quote_request"
          />

          {/* Submit Button */}
          <Button
            type="submit"
            variant="primary"
            loading={formState.status === FormStatus.SUBMITTING}
            disabled={formState.status === FormStatus.SUBMITTING}
          >
            Request Quote
          </Button>
        </>
      )}
    </form>
  );
};

export default QuoteRequestForm;