import React, { useState, useCallback, useEffect } from 'react'; // version ^18.2.0
import classNames from 'classnames'; // version ^2.3.2

import FormField from './FormField';
import Input from '../ui/Input';
import Select from '../ui/Select';
import Checkbox from '../ui/Checkbox';
import Textarea from '../ui/Textarea';
import Button from '../ui/Button';
import Captcha from './Captcha';
import FormSuccess from './FormSuccess';
import FormError from './FormError';
import { useForm } from '../../hooks/useForm';
import { submitDemoRequestWithValidation, getDemoRequestValidationRules } from '../../services/formSubmissionService';
import { DemoRequestFormData, FormStatus, ServiceCategory, TimeZoneOption } from '../../types/forms';
import { SERVICE_CATEGORIES } from '../../constants/services';

/**
 * Interface defining the props for the DemoRequestForm component
 */
export interface DemoRequestFormProps {
  /**
   * Callback function called when form submission is successful
   */
  onSuccess?: () => void;
  /**
   * Additional CSS class names
   */
  className?: string;
}

/**
 * Generates a list of time zone options for the select dropdown
 * @returns Array of time zone options with value, label, and offset
 */
const getTimeZoneOptions = (): TimeZoneOption[] => {
  const timeZones = [
    { value: 'UTC-12:00', label: '(UTC-12:00) Baker Island, Howland Island', offset: '-12:00' },
    { value: 'UTC-11:00', label: '(UTC-11:00) American Samoa, Niue', offset: '-11:00' },
    { value: 'UTC-10:00', label: '(UTC-10:00) Hawaii, Cook Islands', offset: '-10:00' },
    { value: 'UTC-09:00', label: '(UTC-09:00) Alaska', offset: '-09:00' },
    { value: 'UTC-08:00', label: '(UTC-08:00) Pacific Time (US & Canada)', offset: '-08:00' },
    { value: 'UTC-07:00', label: '(UTC-07:00) Mountain Time (US & Canada)', offset: '-07:00' },
    { value: 'UTC-06:00', label: '(UTC-06:00) Central Time (US & Canada)', offset: '-06:00' },
    { value: 'UTC-05:00', label: '(UTC-05:00) Eastern Time (US & Canada)', offset: '-05:00' },
    { value: 'UTC-04:00', label: '(UTC-04:00) Atlantic Time (Canada)', offset: '-04:00' },
    { value: 'UTC-03:00', label: '(UTC-03:00) Buenos Aires, Greenland', offset: '-03:00' },
    { value: 'UTC-02:00', label: '(UTC-02:00) South Georgia and the South Sandwich Islands', offset: '-02:00' },
    { value: 'UTC-01:00', label: '(UTC-01:00) Azores, Cape Verde Islands', offset: '-01:00' },
    { value: 'UTC+00:00', label: '(UTC+00:00) London, Dublin, Lisbon', offset: '+00:00' },
    { value: 'UTC+01:00', label: '(UTC+01:00) Amsterdam, Berlin, Rome', offset: '+01:00' },
    { value: 'UTC+02:00', label: '(UTC+02:00) Athens, Cairo, Jerusalem', offset: '+02:00' },
    { value: 'UTC+03:00', label: '(UTC+03:00) Moscow, Baghdad, Nairobi', offset: '+03:00' },
    { value: 'UTC+04:00', label: '(UTC+04:00) Dubai, Baku, Muscat', offset: '+04:00' },
    { value: 'UTC+05:00', label: '(UTC+05:00) Islamabad, Tashkent', offset: '+05:00' },
    { value: 'UTC+06:00', label: '(UTC+06:00) Dhaka, Almaty', offset: '+06:00' },
    { value: 'UTC+07:00', label: '(UTC+07:00) Bangkok, Hanoi, Jakarta', offset: '+07:00' },
    { value: 'UTC+08:00', label: '(UTC+08:00) Beijing, Singapore, Perth', offset: '+08:00' },
    { value: 'UTC+09:00', label: '(UTC+09:00) Tokyo, Seoul, Yakutsk', offset: '+09:00' },
    { value: 'UTC+10:00', label: '(UTC+10:00) Sydney, Guam', offset: '+10:00' },
    { value: 'UTC+11:00', label: '(UTC+11:00) Magadan, Solomon Islands', offset: '+11:00' },
    { value: 'UTC+12:00', label: '(UTC+12:00) Auckland, Fiji', offset: '+12:00' },
  ];

  // Sort time zones by offset
  timeZones.sort((a, b) => a.offset.localeCompare(b.offset));

  return timeZones;
};

/**
 * Generates a list of referral source options for the select dropdown
 * @returns Array of referral source options with value and label
 */
const getReferralSourceOptions = (): { value: string; label: string }[] => {
  return [
    { value: 'search_engine', label: 'Search Engine (Google, Bing, etc.)' },
    { value: 'social_media', label: 'Social Media (LinkedIn, Twitter, etc.)' },
    { value: 'recommendation', label: 'Recommendation from a Colleague' },
    { value: 'event', label: 'Event (Webinar, Conference, etc.)' },
    { value: 'advertisement', label: 'Online Advertisement' },
    { value: 'other', label: 'Other' },
  ];
};

/**
 * Generates a list of service interest options based on service categories
 * @returns Array of service interest options with value and label
 */
const getServiceInterestOptions = (): { value: string; label: string }[] => {
  return Object.keys(SERVICE_CATEGORIES).map((category) => ({
    value: category,
    label: SERVICE_CATEGORIES[category as ServiceCategory].title,
  });
};

/**
 * Form component for requesting a demo of IndiVillage's AI services
 */
const DemoRequestForm: React.FC<DemoRequestFormProps> = ({ onSuccess, className, ...rest }) => {
  // Initialize form state with useForm hook using initial values and validation rules
  const { formState, handleChange, handleBlur, handleSubmit, resetForm, setStatus, setError } = useForm<DemoRequestFormData>({
    initialValues: {
      firstName: '',
      lastName: '',
      email: '',
      phone: '',
      company: '',
      jobTitle: '',
      serviceInterests: [],
      preferredDate: '',
      preferredTime: '',
      timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone,
      projectDetails: '',
      referralSource: '',
      recaptchaToken: '',
    },
    validationRules: getDemoRequestValidationRules(),
    resetOnSuccess: false,
  });

  // Create state for CAPTCHA token
  const [captchaToken, setCaptchaToken] = useState<string>('');

  // Create state for current date to use in date picker min attribute
  const [currentDate, setCurrentDate] = useState<string>('');

  // Define service interest options using getServiceInterestOptions
  const serviceInterestOptions = getServiceInterestOptions();

  // Define time zone options using getTimeZoneOptions
  const timeZoneOptions = getTimeZoneOptions();

  // Define referral source options using getReferralSourceOptions
  const referralSourceOptions = getReferralSourceOptions();

  // Create handleCaptchaVerify function to store CAPTCHA token
  const handleCaptchaVerify = (token: string) => {
    setCaptchaToken(token);
  };

  // Create handleCaptchaError function to handle CAPTCHA verification errors
  const handleCaptchaError = (error: Error) => {
    setError(`CAPTCHA verification failed: ${error.message}`);
  };

  // Create handleSubmit function to submit form data with CAPTCHA token
  const onSubmit = useCallback(async (values: DemoRequestFormData) => {
    try {
      // Submit form data to API
      if (!captchaToken) {
        setError('Please complete the CAPTCHA verification.');
        return;
      }

      // Submit form data to API
      setStatus(FormStatus.SUBMITTING);
      const formDataWithToken = {
        ...values,
        recaptchaToken: captchaToken,
      };
      await submitDemoRequestWithValidation(formDataWithToken);

      // Update form status to success
      setStatus(FormStatus.SUCCESS);
      if (onSuccess) {
        onSuccess();
      }
    } catch (error: any) {
      // Log error and set form error message
      setError(error.message || 'An error occurred during form submission.');
    }
  }, [captchaToken, onSuccess, setStatus, setError]);

  // Create handleReset function to reset the form after successful submission
  const handleReset = () => {
    resetForm();
    setCaptchaToken('');
  };

  // Format current date for date picker min attribute
  useEffect(() => {
    const today = new Date();
    const year = today.getFullYear();
    const month = String(today.getMonth() + 1).padStart(2, '0');
    const day = String(today.getDate()).padStart(2, '0');
    setCurrentDate(`${year}-${month}-${day}`);
  }, []);

  // Combine CSS classes
  const formClasses = classNames('demo-request-form', className);

  return (
    <div className={formClasses} {...rest}>
      {formState.status === FormStatus.SUCCESS ? (
        <FormSuccess
          message="Your demo request has been submitted successfully! We'll be in touch soon."
          actions={[
            { label: 'Submit Another Request', onClick: handleReset, variant: 'secondary' },
          ]}
        />
      ) : (
        <form onSubmit={handleSubmit(onSubmit)}>
          <FormField name="firstName" label="First Name" required error={formState.fields.firstName?.error}>
            <Input
              type="text"
              name="firstName"
              value={formState.values.firstName}
              onChange={handleChange}
              onBlur={handleBlur}
              placeholder="Enter your first name"
            />
          </FormField>

          <FormField name="lastName" label="Last Name" required error={formState.fields.lastName?.error}>
            <Input
              type="text"
              name="lastName"
              value={formState.values.lastName}
              onChange={handleChange}
              onBlur={handleBlur}
              placeholder="Enter your last name"
            />
          </FormField>

          <FormField name="email" label="Email" required error={formState.fields.email?.error}>
            <Input
              type="email"
              name="email"
              value={formState.values.email}
              onChange={handleChange}
              onBlur={handleBlur}
              placeholder="Enter your email"
            />
          </FormField>

          <FormField name="phone" label="Phone" error={formState.fields.phone?.error}>
            <Input
              type="tel"
              name="phone"
              value={formState.values.phone}
              onChange={handleChange}
              onBlur={handleBlur}
              placeholder="Enter your phone number"
            />
          </FormField>

          <FormField name="company" label="Company" required error={formState.fields.company?.error}>
            <Input
              type="text"
              name="company"
              value={formState.values.company}
              onChange={handleChange}
              onBlur={handleBlur}
              placeholder="Enter your company name"
            />
          </FormField>

          <FormField name="jobTitle" label="Job Title" required error={formState.fields.jobTitle?.error}>
            <Input
              type="text"
              name="jobTitle"
              value={formState.values.jobTitle}
              onChange={handleChange}
              onBlur={handleBlur}
              placeholder="Enter your job title"
            />
          </FormField>

          <FormField name="serviceInterests" label="Services of Interest" required error={formState.fields.serviceInterests?.error}>
            <Select
              name="serviceInterests"
              options={serviceInterestOptions}
              value={formState.values.serviceInterests}
              onChange={handleChange}
              onBlur={handleBlur}
              placeholder="Select services of interest"
              multiple
            />
          </FormField>

          <FormField name="preferredDate" label="Preferred Date" required error={formState.fields.preferredDate?.error}>
            <Input
              type="date"
              name="preferredDate"
              value={formState.values.preferredDate}
              onChange={handleChange}
              onBlur={handleBlur}
              min={currentDate}
            />
          </FormField>

          <FormField name="preferredTime" label="Preferred Time" required error={formState.fields.preferredTime?.error}>
            <Input
              type="time"
              name="preferredTime"
              value={formState.values.preferredTime}
              onChange={handleChange}
              onBlur={handleBlur}
            />
          </FormField>

          <FormField name="timeZone" label="Time Zone" required error={formState.fields.timeZone?.error}>
            <Select
              name="timeZone"
              options={timeZoneOptions}
              value={formState.values.timeZone}
              onChange={handleChange}
              onBlur={handleBlur}
              placeholder="Select your time zone"
            />
          </FormField>

          <FormField name="projectDetails" label="Project Details" error={formState.fields.projectDetails?.error}>
            <Textarea
              name="projectDetails"
              value={formState.values.projectDetails}
              onChange={handleChange}
              onBlur={handleBlur}
              placeholder="Tell us about your project or requirements"
              rows={4}
            />
          </FormField>

          <FormField name="referralSource" label="How did you hear about us?" error={formState.fields.referralSource?.error}>
            <Select
              name="referralSource"
              options={referralSourceOptions}
              value={formState.values.referralSource}
              onChange={handleChange}
              onBlur={handleBlur}
              placeholder="Select how you heard about us"
            />
          </FormField>

          <Captcha onVerify={handleCaptchaVerify} onError={handleCaptchaError} action="demo_request" />

          <Button type="submit" disabled={formState.status === FormStatus.SUBMITTING} loading={formState.status === FormStatus.SUBMITTING}>
            Request Demo
          </Button>

          {formState.status === FormStatus.ERROR && (
            <FormError error={formState.error} />
          )}
        </form>
      )}
    </div>
  );
};

export default DemoRequestForm;