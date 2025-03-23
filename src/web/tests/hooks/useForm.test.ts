import { describe, it, expect, jest } from '@jest/globals'; // package_version: ^29.5.0
import { renderHook, act, waitFor } from '@testing-library/react'; // package_version: ^14.0.0
import { useForm } from '../../src/hooks/useForm'; // path: src/web/src/hooks/useForm.ts
import { FormStatus } from '../../src/types/forms'; // path: src/web/src/types/forms.ts
import { createMockValidationRules } from '../../src/utils/testing'; // path: src/web/src/utils/testing.ts
import { VALIDATION_MESSAGES } from '../../src/constants/validationMessages'; // path: src/web/src/constants/validationMessages.ts

describe('useForm hook', () => {
  it('should initialize form state with initial values', () => {
    const initialValues = { name: 'John Doe', email: 'john@example.com' };
    const { result } = renderHook(() => useForm({ initialValues }));

    expect(result.current.formState.values).toEqual(initialValues);
    expect(result.current.formState.status).toBe(FormStatus.IDLE);
    expect(result.current.formState.error).toBe('');
    expect(result.current.formState.isValid).toBe(true);
  });

  it('should update form values when handleChange is called', () => {
    const initialValues = { name: 'John Doe', email: 'john@example.com' };
    const { result } = renderHook(() => useForm({ initialValues }));

    act(() => {
      result.current.handleChange('name', 'Jane Doe');
    });

    expect(result.current.formState.values.name).toBe('Jane Doe');
    expect(result.current.formState.fields.name.touched).toBe(false);
  });

  it('should mark fields as touched when handleBlur is called', () => {
    const initialValues = { name: 'John Doe', email: 'john@example.com' };
    const { result } = renderHook(() => useForm({ initialValues }));

    act(() => {
      result.current.handleBlur('name');
    });

    expect(result.current.formState.fields.name.touched).toBe(true);
    expect(result.current.formState.values.name).toBe('John Doe');
  });

  it('should validate fields according to validation rules', () => {
    const validationRules = {
      name: createMockValidationRules({ required: true }),
      email: createMockValidationRules({ email: true }),
    };
    const initialValues = { name: '', email: 'invalid-email' };
    const { result } = renderHook(() => useForm({ initialValues, validationRules }));

    act(() => {
      result.current.handleChange('name', '');
      result.current.handleChange('email', 'invalid-email');
    });

    expect(result.current.formState.fields.name.error).toBe(VALIDATION_MESSAGES.REQUIRED);
    expect(result.current.formState.fields.email.error).toBe(VALIDATION_MESSAGES.EMAIL_INVALID);
    expect(result.current.formState.isValid).toBe(false);

    act(() => {
      result.current.handleChange('name', 'Valid Name');
      result.current.handleChange('email', 'valid@email.com');
    });

    expect(result.current.formState.fields.name.error).toBe('');
    expect(result.current.formState.fields.email.error).toBe('');
    expect(result.current.formState.isValid).toBe(true);
  });

  it('should validate on change when validateOnChange is true', () => {
    const validationRules = {
      name: createMockValidationRules({ required: true }),
    };
    const initialValues = { name: '' };
    const { result } = renderHook(() => useForm({ initialValues, validationRules, validateOnChange: true }));

    act(() => {
      result.current.handleChange('name', '');
    });

    expect(result.current.formState.fields.name.error).toBe(VALIDATION_MESSAGES.REQUIRED);
  });

  it('should validate on blur when validateOnBlur is true', () => {
    const validationRules = {
      name: createMockValidationRules({ required: true }),
    };
    const initialValues = { name: '' };
    const { result } = renderHook(() => useForm({ initialValues, validationRules, validateOnBlur: true }));

    act(() => {
      result.current.handleBlur('name');
    });

    expect(result.current.formState.fields.name.error).toBe(VALIDATION_MESSAGES.REQUIRED);
  });

  it('should handle form submission with validation', async () => {
    const validationRules = {
      name: createMockValidationRules({ required: true }),
    };
    const initialValues = { name: 'John' };
    const onSubmit = jest.fn();
    const { result } = renderHook(() => useForm({ initialValues, validationRules }));

    const handleSubmit = result.current.handleSubmit(onSubmit);

    await act(async () => {
      await handleSubmit();
    });

    expect(onSubmit).toHaveBeenCalledWith({ name: 'John' });
    expect(result.current.formState.status).toBe(FormStatus.SUCCESS);
  });

  it('should handle submission errors', async () => {
    const initialValues = { name: 'John' };
    const onSubmit = jest.fn(() => {
      throw new Error('Submission failed');
    });
    const { result } = renderHook(() => useForm({ initialValues }));

    const handleSubmit = result.current.handleSubmit(onSubmit);

    await act(async () => {
      await handleSubmit();
    });

    expect(result.current.formState.status).toBe(FormStatus.ERROR);
    expect(result.current.formState.error).toBe('Submission failed');
  });

  it('should reset form state when resetForm is called', () => {
    const initialValues = { name: 'John Doe', email: 'john@example.com' };
    const { result } = renderHook(() => useForm({ initialValues }));

    act(() => {
      result.current.handleChange('name', 'Jane Doe');
      result.current.resetForm();
    });

    expect(result.current.formState.values).toEqual(initialValues);
    expect(result.current.formState.fields.name.touched).toBe(false);
    expect(result.current.formState.status).toBe(FormStatus.IDLE);
    expect(result.current.formState.error).toBe('');
  });

  it('should update form status when setStatus is called', () => {
    const initialValues = { name: 'John Doe', email: 'john@example.com' };
    const { result } = renderHook(() => useForm({ initialValues }));

    act(() => {
      result.current.setStatus(FormStatus.SUBMITTING);
    });

    expect(result.current.formState.status).toBe(FormStatus.SUBMITTING);
  });

  it('should update form error when setError is called', () => {
    const initialValues = { name: 'John Doe', email: 'john@example.com' };
    const { result } = renderHook(() => useForm({ initialValues }));

    act(() => {
      result.current.setError('An error occurred');
    });

    expect(result.current.formState.error).toBe('An error occurred');
  });

  it('should reset form after successful submission when resetOnSuccess is true', async () => {
    const initialValues = { name: 'John Doe', email: 'john@example.com' };
    const onSubmit = jest.fn();
    const { result } = renderHook(() => useForm({ initialValues, resetOnSuccess: true }));

    act(() => {
      result.current.handleChange('name', 'Jane Doe');
    });

    const handleSubmit = result.current.handleSubmit(onSubmit);

    await act(async () => {
      await handleSubmit();
    });

    expect(result.current.formState.values).toEqual(initialValues);
  });
});