import { useState, useCallback, useEffect } from 'react'; // react@^18.0.0
import { FormState, FormField, FormStatus, FormValidationRules } from '../types/forms';
import { validateField, validateForm } from '../utils/validation';
import { logError } from '../utils/errorHandling';

/**
 * Options for configuring the useForm hook
 */
interface UseFormOptions {
  /** Initial form values */
  initialValues: Record<string, any>;
  /** Validation rules for form fields */
  validationRules?: Record<string, FormValidationRules>;
  /** Whether to validate fields on change */
  validateOnChange?: boolean;
  /** Whether to validate fields on blur */
  validateOnBlur?: boolean;
  /** Whether to reset form after successful submission */
  resetOnSuccess?: boolean;
}

/**
 * Return type of the useForm hook
 */
interface UseFormReturn {
  /** Current form state */
  formState: FormState;
  /** Handler for input change events */
  handleChange: (name: string, valueOrEvent: any) => void;
  /** Handler for input blur events */
  handleBlur: (name: string) => void;
  /** Handler for form submission */
  handleSubmit: (onSubmit: (values: Record<string, any>) => Promise<void> | void) => (e?: React.FormEvent) => Promise<void>;
  /** Function to validate all form fields */
  validateForm: () => boolean;
  /** Function to reset form to initial state */
  resetForm: () => void;
  /** Function to set form status */
  setStatus: (status: FormStatus) => void;
  /** Function to set form error message */
  setError: (error: string) => void;
}

/**
 * Custom React hook for managing form state, validation, and submission
 * 
 * Provides a comprehensive solution for form handling, including:
 * - Form state management
 * - Field-level validation
 * - Form submission with loading states
 * - Error handling
 * 
 * @param options - Configuration options for the form
 * @returns Form state and handler functions
 */
export const useForm = (options: UseFormOptions): UseFormReturn => {
  const {
    initialValues,
    validationRules = {},
    validateOnChange = false,
    validateOnBlur = true,
    resetOnSuccess = true
  } = options;

  // Initialize form state
  const [formState, setFormState] = useState<FormState>({
    values: { ...initialValues },
    fields: {},
    status: FormStatus.IDLE,
    error: '',
    isValid: false,
    isDirty: false
  });

  // Initialize field objects for each form value
  const initializeFields = useCallback(() => {
    const fields: Record<string, FormField> = {};
    
    // Create a field object for each initial value
    Object.keys(initialValues).forEach(key => {
      fields[key] = {
        value: initialValues[key],
        touched: false,
        error: ''
      };
    });
    
    setFormState(prevState => ({
      ...prevState,
      fields
    }));
  }, [initialValues]);

  // Initialize form fields on first render
  useEffect(() => {
    initializeFields();
  }, [initializeFields]);

  // Handler for input change events
  const handleChange = useCallback((name: string, valueOrEvent: any) => {
    // Extract value from event if needed
    let value = valueOrEvent;
    
    // Check if the value is a React SyntheticEvent or DOM event
    if (valueOrEvent && typeof valueOrEvent === 'object' && 'target' in valueOrEvent) {
      const target = valueOrEvent.target as HTMLInputElement;
      value = target.type === 'checkbox' ? target.checked : target.value;
    }
    
    setFormState(prevState => {
      // Update the field value
      const updatedFields = {
        ...prevState.fields,
        [name]: {
          ...prevState.fields[name],
          value,
          // Optionally mark as touched on change
          touched: prevState.fields[name]?.touched || false
        }
      };
      
      // Validate the field if validateOnChange is enabled
      if (validateOnChange && validationRules[name]) {
        updatedFields[name].error = validateField(name, value, validationRules[name]);
      }
      
      // Check if the form has any errors
      const hasErrors = Object.values(updatedFields).some(field => field.error);
      
      return {
        ...prevState,
        values: {
          ...prevState.values,
          [name]: value
        },
        fields: updatedFields,
        isValid: !hasErrors,
        isDirty: true
      };
    });
  }, [validateOnChange, validationRules]);

  // Handler for input blur events
  const handleBlur = useCallback((name: string) => {
    setFormState(prevState => {
      // Get the current field
      const field = prevState.fields[name];
      
      if (!field) {
        return prevState;
      }
      
      // Mark the field as touched
      const updatedField: FormField = {
        ...field,
        touched: true
      };
      
      // Validate the field if validateOnBlur is enabled
      if (validateOnBlur && validationRules[name]) {
        updatedField.error = validateField(name, field.value, validationRules[name]);
      }
      
      // Update the fields object
      const updatedFields = {
        ...prevState.fields,
        [name]: updatedField
      };
      
      // Check if the form has any errors
      const hasErrors = Object.values(updatedFields).some(f => f.error);
      
      return {
        ...prevState,
        fields: updatedFields,
        isValid: !hasErrors
      };
    });
  }, [validateOnBlur, validationRules]);

  // Validate all form fields
  const validateFormFields = useCallback(() => {
    if (!validationRules || Object.keys(validationRules).length === 0) {
      return true;
    }
    
    let isValid = true;
    
    setFormState(prevState => {
      const updatedFields = { ...prevState.fields };
      
      // Validate each field with a validation rule
      Object.keys(validationRules).forEach(fieldName => {
        const fieldValue = prevState.values[fieldName];
        const error = validateField(fieldName, fieldValue, validationRules[fieldName]);
        
        if (error) {
          isValid = false;
        }
        
        updatedFields[fieldName] = {
          ...updatedFields[fieldName],
          error,
          touched: true
        };
      });
      
      return {
        ...prevState,
        fields: updatedFields,
        isValid
      };
    });
    
    return isValid;
  }, [validationRules]);

  // Handler for form submission
  const handleSubmit = useCallback((onSubmit: (values: Record<string, any>) => Promise<void> | void) => {
    return async (e?: React.FormEvent) => {
      // Prevent default form submission if event is provided
      if (e) {
        e.preventDefault();
      }
      
      // Validate all fields before submission
      const isValid = validateFormFields();
      
      if (!isValid) {
        // If not valid, update form status to show errors
        setFormState(prevState => ({
          ...prevState,
          status: FormStatus.ERROR,
          error: 'Please correct the errors in the form.'
        }));
        
        return;
      }
      
      try {
        // Update form status to submitting
        setFormState(prevState => ({
          ...prevState,
          status: FormStatus.SUBMITTING,
          error: ''
        }));
        
        // Call the onSubmit callback and handle both Promise and non-Promise returns
        const result = onSubmit(formState.values);
        if (result instanceof Promise) {
          await result;
        }
        
        // Update form status to success
        setFormState(prevState => ({
          ...prevState,
          status: FormStatus.SUCCESS,
          error: ''
        }));
        
        // Reset form if resetOnSuccess is enabled
        if (resetOnSuccess) {
          setTimeout(() => {
            resetForm();
          }, 0);
        }
      } catch (error) {
        // Log the error
        logError(error, 'form_submission');
        
        // Update form status to error
        setFormState(prevState => ({
          ...prevState,
          status: FormStatus.ERROR,
          error: error instanceof Error ? error.message : 'An error occurred during form submission.'
        }));
      }
    };
  }, [formState.values, validateFormFields, resetOnSuccess]);

  // Reset form to initial state
  const resetForm = useCallback(() => {
    // Re-initialize the form with initial values
    setFormState({
      values: { ...initialValues },
      fields: Object.keys(initialValues).reduce((fields, key) => {
        fields[key] = {
          value: initialValues[key],
          touched: false,
          error: ''
        };
        return fields;
      }, {} as Record<string, FormField>),
      status: FormStatus.IDLE,
      error: '',
      isValid: false,
      isDirty: false
    });
  }, [initialValues]);

  // Set form status
  const setStatus = useCallback((status: FormStatus) => {
    setFormState(prevState => ({
      ...prevState,
      status
    }));
  }, []);

  // Set form error message
  const setError = useCallback((error: string) => {
    setFormState(prevState => ({
      ...prevState,
      status: FormStatus.ERROR,
      error
    }));
  }, []);

  return {
    formState,
    handleChange,
    handleBlur,
    handleSubmit,
    validateForm: validateFormFields,
    resetForm,
    setStatus,
    setError
  };
};

export default useForm;