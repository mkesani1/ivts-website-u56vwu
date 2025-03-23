import React, { useState, useCallback, useEffect } from 'react'; // version 18.2.0
import classNames from 'classnames'; // version 2.3.2
import FormField from './FormField';
import Input from '../ui/Input';
import Textarea from '../ui/Textarea';
import Button from '../ui/Button';
import Captcha from './Captcha';
import FormSuccess from './FormSuccess';
import { useForm } from '../../hooks/useForm';
import { ContactFormData, FormStatus } from '../../types/forms';
import { submitContactFormWithValidation, getContactFormValidationRules } from '../../services/formSubmissionService';
import { useAnalytics } from '../../hooks/useAnalytics';

/**
 * Interface defining the props for the ContactForm component
 */
export interface ContactFormProps extends React.HTMLAttributes<HTMLDivElement> {
  /** Additional CSS class names */
  className?: string;
  /** Callback function called when form submission is successful */
  onSuccess?: () => void;
}

/**
 * A form component that allows users to submit contact inquiries
 * @param {ContactFormProps} props - The component props
 * @returns {JSX.Element} Rendered contact form component
 */
const ContactForm: React.FC<ContactFormProps> = (props) => {
  // Destructure props including className, onSuccess, and other HTML attributes
  const { className, onSuccess, ...rest } = props;

  // Initialize analytics tracking hook
  const analytics = useAnalytics();

  // Get contact form validation rules
  const validationRules = getContactFormValidationRules();

  // Initialize form state using useForm hook with validation rules
  const {
    formState,
    handleChange,
    handleBlur,
    handleSubmit,
    resetForm
  } = useForm<ContactFormData>({
    initialValues: {
      name: '',
      email: '',
      phone: '',
      company: '',
      message: ''
    },
    validationRules
  });

  // Create state for CAPTCHA token
  const [captchaToken, setCaptchaToken] = useState<string | null>(null);

  // Create state for form success message
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Create function to handle CAPTCHA verification
  const handleVerify = useCallback((token: string) => {
    setCaptchaToken(token);
  }, []);

  // Create function to handle CAPTCHA error
  const handleError = useCallback((error: Error) => {
    console.error('CAPTCHA error:', error);
  }, []);

  // Create function to handle form submission
  const onSubmit = useCallback(async (values: ContactFormData) => {
    // Add CAPTCHA token to form data
    const formDataWithCaptcha: ContactFormData = {
      ...values,
      recaptchaToken: captchaToken || ''
    };

    // Submit the form with validation
    const response = await submitContactFormWithValidation(formDataWithCaptcha);

    if (response.success) {
      // Set success message and reset form
      setSuccessMessage(response.message);
      analytics.trackEvent('contact_form', 'submission_success');
      resetForm();
      if (onSuccess) {
        onSuccess();
      }
    } else {
      // Track form submission failure
      analytics.trackEvent('contact_form', 'submission_failure', {
        error: response.message
      });
    }
  }, [captchaToken, analytics, resetForm, onSuccess]);

  // Create function to handle form reset
  const handleFormReset = useCallback(() => {
    setSuccessMessage(null);
    resetForm();
  }, [resetForm]);

  // Check if form is in submitting state
  const isSubmitting = formState.status === FormStatus.SUBMITTING;

  // Generate form container class names
  const formClasses = classNames(
    'contact-form',
    'max-w-md',
    'mx-auto',
    className
  );

  // If form is in success state, render success message with reset option
  if (successMessage) {
    return (
      <FormSuccess
        message={successMessage}
        actions={[
          {
            label: 'Submit Another',
            onClick: handleFormReset,
            variant: 'TERTIARY'
          }
        ]}
      />
    );
  }

  // Otherwise, render the form with all fields and validation
  return (
    <form
      className={formClasses}
      onSubmit={handleSubmit(onSubmit)}
      {...rest}
    >
      {/* Include name field with validation */}
      <FormField
        id="name"
        name="name"
        label="Name"
        required
        error={formState.fields.name?.error}
      >
        <Input
          type="text"
          name="name"
          value={formState.values.name}
          placeholder="Your Name"
          onChange={handleChange}
          onBlur={handleBlur}
        />
      </FormField>

      {/* Include email field with validation */}
      <FormField
        id="email"
        name="email"
        label="Email"
        required
        error={formState.fields.email?.error}
      >
        <Input
          type="email"
          name="email"
          value={formState.values.email}
          placeholder="Your Email"
          onChange={handleChange}
          onBlur={handleBlur}
        />
      </FormField>

      {/* Include phone field (optional) */}
      <FormField
        id="phone"
        name="phone"
        label="Phone (Optional)"
        error={formState.fields.phone?.error}
      >
        <Input
          type="tel"
          name="phone"
          value={formState.values.phone}
          placeholder="Your Phone"
          onChange={handleChange}
          onBlur={handleBlur}
        />
      </FormField>

      {/* Include company field with validation */}
      <FormField
        id="company"
        name="company"
        label="Company"
        required
        error={formState.fields.company?.error}
      >
        <Input
          type="text"
          name="company"
          value={formState.values.company}
          placeholder="Your Company"
          onChange={handleChange}
          onBlur={handleBlur}
        />
      </FormField>

      {/* Include message textarea with validation */}
      <FormField
        id="message"
        name="message"
        label="Message"
        required
        error={formState.fields.message?.error}
      >
        <Textarea
          name="message"
          value={formState.values.message}
          placeholder="Your Message"
          rows={5}
          onChange={handleChange}
          onBlur={handleBlur}
        />
      </FormField>

      {/* Include CAPTCHA component */}
      <Captcha
        onVerify={handleVerify}
        onError={handleError}
        action="contact_form"
      />

      {/* Include submit button with loading state */}
      <Button
        type="submit"
        variant="primary"
        loading={isSubmitting}
        disabled={isSubmitting || !formState.isValid}
        fullWidth
      >
        Submit
      </Button>
    </form>
  );
};

export default ContactForm;