import * as validationUtils from '../../src/utils/validation'; // Import validation utility functions for testing
import { VALIDATION_MESSAGES } from '../../src/constants/validationMessages'; // Import validation error messages for testing
import { createMockFile, createMockValidationRules } from '../../src/utils/testing'; // Import utility for creating mock File objects for testing
import 'jest'; // Testing framework for running unit tests // jest@^29.5.0

describe('validateRequired', () => { // Tests for the validateRequired function
  it('should return error message for undefined value', () => { // Expect validateRequired(undefined) to equal VALIDATION_MESSAGES.REQUIRED
    expect(validationUtils.validateRequired(undefined)).toEqual(VALIDATION_MESSAGES.REQUIRED);
  });

  it('should return error message for null value', () => { // Expect validateRequired(null) to equal VALIDATION_MESSAGES.REQUIRED
    expect(validationUtils.validateRequired(null)).toEqual(VALIDATION_MESSAGES.REQUIRED);
  });

  it('should return error message for empty string', () => { // Expect validateRequired('') to equal VALIDATION_MESSAGES.REQUIRED
    expect(validationUtils.validateRequired('')).toEqual(VALIDATION_MESSAGES.REQUIRED);
  });

  it('should return empty string for non-empty string', () => { // Expect validateRequired('test') to equal ''
    expect(validationUtils.validateRequired('test')).toEqual('');
  });

  it('should return empty string for number value', () => { // Expect validateRequired(0) to equal ''
    expect(validationUtils.validateRequired(0)).toEqual('');
  });

  it('should return empty string for boolean value', () => { // Expect validateRequired(false) to equal ''
    expect(validationUtils.validateRequired(false)).toEqual('');
  });
});

describe('validateEmail', () => { // Tests for the validateEmail function
  it('should return empty string for undefined value (optional field)', () => { // Expect validateEmail(undefined) to equal ''
    expect(validationUtils.validateEmail(undefined)).toEqual('');
  });

  it('should return empty string for null value (optional field)', () => { // Expect validateEmail(null) to equal ''
    expect(validationUtils.validateEmail(null)).toEqual('');
  });

  it('should return empty string for empty string (optional field)', () => { // Expect validateEmail('') to equal ''
    expect(validationUtils.validateEmail('')).toEqual('');
  });

  it('should return error message for invalid email format', () => { // Expect validateEmail('invalid-email') to equal VALIDATION_MESSAGES.EMAIL_INVALID
    expect(validationUtils.validateEmail('invalid-email')).toEqual(VALIDATION_MESSAGES.EMAIL_INVALID);
  });

  it('should return error message for email missing domain', () => { // Expect validateEmail('user@') to equal VALIDATION_MESSAGES.EMAIL_INVALID
    expect(validationUtils.validateEmail('user@')).toEqual(VALIDATION_MESSAGES.EMAIL_INVALID);
  });

  it('should return error message for email missing username', () => { // Expect validateEmail('@domain.com') to equal VALIDATION_MESSAGES.EMAIL_INVALID
    expect(validationUtils.validateEmail('@domain.com')).toEqual(VALIDATION_MESSAGES.EMAIL_INVALID);
  });

  it('should return empty string for valid email', () => { // Expect validateEmail('user@domain.com') to equal ''
    expect(validationUtils.validateEmail('user@domain.com')).toEqual('');
  });

  it('should return empty string for valid email with subdomains', () => { // Expect validateEmail('user@sub.domain.com') to equal ''
    expect(validationUtils.validateEmail('user@sub.domain.com')).toEqual('');
  });

  it('should return empty string for valid email with plus addressing', () => { // Expect validateEmail('user+tag@domain.com') to equal ''
    expect(validationUtils.validateEmail('user+tag@domain.com')).toEqual('');
  });
});

describe('validatePhone', () => { // Tests for the validatePhone function
  it('should return empty string for undefined value (optional field)', () => { // Expect validatePhone(undefined) to equal ''
    expect(validationUtils.validatePhone(undefined)).toEqual('');
  });

  it('should return empty string for null value (optional field)', () => { // Expect validatePhone(null) to equal ''
    expect(validationUtils.validatePhone(null)).toEqual('');
  });

  it('should return empty string for empty string (optional field)', () => { // Expect validatePhone('') to equal ''
    expect(validationUtils.validatePhone('')).toEqual('');
  });

  it('should return error message for invalid phone format', () => { // Expect validatePhone('abc') to equal VALIDATION_MESSAGES.PHONE_INVALID
    expect(validationUtils.validatePhone('abc')).toEqual(VALIDATION_MESSAGES.PHONE_INVALID);
  });

  it('should return error message for phone number too short', () => { // Expect validatePhone('123') to equal VALIDATION_MESSAGES.PHONE_INVALID
    expect(validationUtils.validatePhone('123')).toEqual(VALIDATION_MESSAGES.PHONE_INVALID);
  });

  it('should return empty string for valid phone number with parentheses', () => { // Expect validatePhone('(123) 456-7890') to equal ''
    expect(validationUtils.validatePhone('(123) 456-7890')).toEqual('');
  });

  it('should return empty string for valid phone number with dashes', () => { // Expect validatePhone('123-456-7890') to equal ''
    expect(validationUtils.validatePhone('123-456-7890')).toEqual('');
  });

  it('should return empty string for valid phone number with spaces', () => { // Expect validatePhone('123 456 7890') to equal ''
    expect(validationUtils.validatePhone('123 456 7890')).toEqual('');
  });

  it('should return empty string for valid phone number with country code', () => { // Expect validatePhone('+1 123 456 7890') to equal ''
    expect(validationUtils.validatePhone('+1 123 456 7890')).toEqual('');
  });
});

describe('validateMinLength', () => { // Tests for the validateMinLength function
  it('should return empty string for undefined value (optional field)', () => { // Expect validateMinLength(undefined, 5) to equal ''
    expect(validationUtils.validateMinLength(undefined, 5)).toEqual('');
  });

  it('should return empty string for null value (optional field)', () => { // Expect validateMinLength(null, 5) to equal ''
    expect(validationUtils.validateMinLength(null, 5)).toEqual('');
  });

  it('should return empty string for empty string (optional field)', () => { // Expect validateMinLength('', 5) to equal ''
    expect(validationUtils.validateMinLength('', 5)).toEqual('');
  });

  it('should return error message for string shorter than minimum length', () => { // Expect validateMinLength('abc', 5) to equal VALIDATION_MESSAGES.MIN_LENGTH(5)
    expect(validationUtils.validateMinLength('abc', 5)).toEqual(VALIDATION_MESSAGES.MIN_LENGTH(5));
  });

  it('should return empty string for string equal to minimum length', () => { // Expect validateMinLength('abcde', 5) to equal ''
    expect(validationUtils.validateMinLength('abcde', 5)).toEqual('');
  });

  it('should return empty string for string longer than minimum length', () => { // Expect validateMinLength('abcdefg', 5) to equal ''
    expect(validationUtils.validateMinLength('abcdefg', 5)).toEqual('');
  });
});

describe('validateMaxLength', () => { // Tests for the validateMaxLength function
  it('should return empty string for undefined value (optional field)', () => { // Expect validateMaxLength(undefined, 5) to equal ''
    expect(validationUtils.validateMaxLength(undefined, 5)).toEqual('');
  });

  it('should return empty string for null value (optional field)', () => { // Expect validateMaxLength(null, 5) to equal ''
    expect(validationUtils.validateMaxLength(null, 5)).toEqual('');
  });

  it('should return empty string for empty string (optional field)', () => { // Expect validateMaxLength('', 5) to equal ''
    expect(validationUtils.validateMaxLength('', 5)).toEqual('');
  });

  it('should return empty string for string shorter than maximum length', () => { // Expect validateMaxLength('abc', 5) to equal ''
    expect(validationUtils.validateMaxLength('abc', 5)).toEqual('');
  });

  it('should return empty string for string equal to maximum length', () => { // Expect validateMaxLength('abcde', 5) to equal ''
    expect(validationUtils.validateMaxLength('abcde', 5)).toEqual('');
  });

  it('should return error message for string longer than maximum length', () => { // Expect validateMaxLength('abcdefg', 5) to equal VALIDATION_MESSAGES.MAX_LENGTH(5)
    expect(validationUtils.validateMaxLength('abcdefg', 5)).toEqual(VALIDATION_MESSAGES.MAX_LENGTH(5));
  });
});

describe('validatePattern', () => { // Tests for the validatePattern function
  it('should return empty string for undefined value (optional field)', () => { // Expect validatePattern(undefined, /^[a-z]+$/, 'Error') to equal ''
    expect(validationUtils.validatePattern(undefined, /^[a-z]+$/, 'Error')).toEqual('');
  });

  it('should return empty string for null value (optional field)', () => { // Expect validatePattern(null, /^[a-z]+$/, 'Error') to equal ''
    expect(validationUtils.validatePattern(null, /^[a-z]+$/, 'Error')).toEqual('');
  });

  it('should return empty string for empty string (optional field)', () => { // Expect validatePattern('', /^[a-z]+$/, 'Error') to equal ''
    expect(validationUtils.validatePattern('', /^[a-z]+$/, 'Error')).toEqual('');
  });

  it('should return error message for string not matching pattern', () => { // Expect validatePattern('123', /^[a-z]+$/, 'Error') to equal 'Error'
    expect(validationUtils.validatePattern('123', /^[a-z]+$/, 'Error')).toEqual('Error');
  });

  it('should return empty string for string matching pattern', () => { // Expect validatePattern('abc', /^[a-z]+$/, 'Error') to equal ''
    expect(validationUtils.validatePattern('abc', /^[a-z]+$/, 'Error')).toEqual('');
  });
});

describe('validateFileType', () => { // Tests for the validateFileType function
  it('should return empty string for undefined file (optional field)', () => { // Expect validateFileType(undefined, ['image/jpeg']) to equal ''
    expect(validationUtils.validateFileType(undefined, ['image/jpeg'])).toEqual('');
  });

  it('should return empty string for null file (optional field)', () => { // Expect validateFileType(null, ['image/jpeg']) to equal ''
    expect(validationUtils.validateFileType(null, ['image/jpeg'])).toEqual('');
  });

  it('should return error message for file with invalid type', () => { // Expect validateFileType(createMockFile({ type: 'application/pdf' }), ['image/jpeg', 'image/png']) to equal VALIDATION_MESSAGES.FILE_TYPE_INVALID
    expect(validationUtils.validateFileType(createMockFile({ type: 'application/pdf' }), ['image/jpeg', 'image/png'])).toEqual(VALIDATION_MESSAGES.FILE_TYPE_INVALID);
  });

  it('should return empty string for file with valid type', () => { // Expect validateFileType(createMockFile({ type: 'image/jpeg' }), ['image/jpeg', 'image/png']) to equal ''
    expect(validationUtils.validateFileType(createMockFile({ type: 'image/jpeg' }), ['image/jpeg', 'image/png'])).toEqual('');
  });

  it('should use default allowed types when not provided', () => { // Expect validateFileType(createMockFile({ type: 'image/jpeg' })) to equal ''
    expect(validationUtils.validateFileType(createMockFile({ type: 'image/jpeg' }))).toEqual('');
  });
});

describe('validateFileSize', () => { // Tests for the validateFileSize function
  it('should return empty string for undefined file (optional field)', () => { // Expect validateFileSize(undefined, 5) to equal ''
    expect(validationUtils.validateFileSize(undefined, 5)).toEqual('');
  });

  it('should return empty string for null file (optional field)', () => { // Expect validateFileSize(null, 5) to equal ''
    expect(validationUtils.validateFileSize(null, 5)).toEqual('');
  });

  it('should return error message for file exceeding maximum size', () => { // Expect validateFileSize(createMockFile({ size: 6 * 1024 * 1024 }), 5) to equal VALIDATION_MESSAGES.FILE_SIZE_EXCEEDED
    expect(validationUtils.validateFileSize(createMockFile({ size: 6 * 1024 * 1024 }), 5)).toEqual(VALIDATION_MESSAGES.FILE_SIZE_EXCEEDED);
  });

  it('should return empty string for file within maximum size', () => { // Expect validateFileSize(createMockFile({ size: 4 * 1024 * 1024 }), 5) to equal ''
    expect(validationUtils.validateFileSize(createMockFile({ size: 4 * 1024 * 1024 }), 5)).toEqual('');
  });

  it('should use default maximum size when not provided', () => { // Expect validateFileSize(createMockFile({ size: 40 * 1024 * 1024 })) to equal ''
    expect(validationUtils.validateFileSize(createMockFile({ size: 40 * 1024 * 1024 }))).toEqual('');
  });
});

describe('validateField', () => { // Tests for the validateField function
  it('should return empty string when no rules exist for field', () => { // Expect validateField('test', 'value', {}) to equal ''
    expect(validationUtils.validateField('test', 'value', {})).toEqual('');
  });

  it('should validate required field', () => { // Expect validateField('test', '', { test: { required: true } }) to equal VALIDATION_MESSAGES.REQUIRED
    expect(validationUtils.validateField('test', '', { test: { required: true } })).toEqual(VALIDATION_MESSAGES.REQUIRED);
  });

  it('should validate email field', () => { // Expect validateField('email', 'invalid', { email: { email: true } }) to equal VALIDATION_MESSAGES.EMAIL_INVALID
    expect(validationUtils.validateField('email', 'invalid', { email: { email: true } })).toEqual(VALIDATION_MESSAGES.EMAIL_INVALID);
  });

  it('should validate phone field', () => { // Expect validateField('phone', 'invalid', { phone: { phone: true } }) to equal VALIDATION_MESSAGES.PHONE_INVALID
    expect(validationUtils.validateField('phone', 'invalid', { phone: { phone: true } })).toEqual(VALIDATION_MESSAGES.PHONE_INVALID);
  });

  it('should validate minimum length', () => { // Expect validateField('name', 'ab', { name: { minLength: 3 } }) to equal VALIDATION_MESSAGES.MIN_LENGTH(3)
    expect(validationUtils.validateField('name', 'ab', { name: { minLength: 3 } })).toEqual(VALIDATION_MESSAGES.MIN_LENGTH(3));
  });

  it('should validate maximum length', () => { // Expect validateField('name', 'abcdef', { name: { maxLength: 5 } }) to equal VALIDATION_MESSAGES.MAX_LENGTH(5)
    expect(validationUtils.validateField('name', 'abcdef', { name: { maxLength: 5 } })).toEqual(VALIDATION_MESSAGES.MAX_LENGTH(5));
  });

  it('should validate pattern', () => { // Expect validateField('name', '123', { name: { pattern: /^[a-z]+$/ } }) to contain 'pattern'
    expect(validationUtils.validateField('name', '123', { name: { pattern: /^[a-z]+$/ } })).toContain('pattern');
  });

  it('should validate using custom validation function', () => { // Expect validateField('test', 'value', { test: { custom: () => 'Custom error' } }) to equal 'Custom error'
    expect(validationUtils.validateField('test', 'value', { test: { custom: () => 'Custom error' } })).toEqual('Custom error');
  });

  it('should return first error encountered', () => { // Expect validateField('email', '', { email: { required: true, email: true } }) to equal VALIDATION_MESSAGES.REQUIRED
    expect(validationUtils.validateField('email', '', { email: { required: true, email: true } })).toEqual(VALIDATION_MESSAGES.REQUIRED);
  });

  it('should return empty string when all validations pass', () => { // Expect validateField('email', 'test@example.com', { email: { required: true, email: true } }) to equal ''
    expect(validationUtils.validateField('email', 'test@example.com', { email: { required: true, email: true } })).toEqual('');
  });
});

describe('validateForm', () => { // Tests for the validateForm function
  it('should return empty object when no validation rules provided', () => { // Expect validateForm({}, {}) to deep equal {}
    expect(validationUtils.validateForm({}, {})).toEqual({});
  });

  it('should return errors for invalid fields', () => { // Expect validateForm({ name: '', email: 'invalid' }, { name: { required: true }, email: { email: true } }) to have properties 'name' and 'email'
    expect(validationUtils.validateForm({ name: '', email: 'invalid' }, { name: { required: true }, email: { email: true } })).toHaveProperty('name');
    expect(validationUtils.validateForm({ name: '', email: 'invalid' }, { name: { required: true }, email: { email: true } })).toHaveProperty('email');
  });

  it('should not return errors for valid fields', () => { // Expect validateForm({ name: 'Test', email: 'test@example.com' }, { name: { required: true }, email: { email: true } }) to deep equal {}
    expect(validationUtils.validateForm({ name: 'Test', email: 'test@example.com' }, { name: { required: true }, email: { email: true } })).toEqual({});
  });

  it('should validate only fields with rules', () => { // Expect validateForm({ name: '', email: 'invalid', phone: '123' }, { name: { required: true }, email: { email: true } }) to not.have.property('phone')
    expect(validationUtils.validateForm({ name: '', email: 'invalid', phone: '123' }, { name: { required: true }, email: { email: true } })).not.toHaveProperty('phone');
  });

  it('should handle complex validation rules', () => { // Expect validateForm({ name: 'a', bio: 'too long text' }, { name: { required: true, minLength: 2 }, bio: { maxLength: 10 } }) to have properties 'name' and 'bio'
    const result = validationUtils.validateForm({ name: 'a', bio: 'too long text' }, { name: { required: true, minLength: 2 }, bio: { maxLength: 10 } });
    expect(result).toHaveProperty('name');
    expect(result).toHaveProperty('bio');
  });
});

describe('validateFile', () => { // Tests for the validateFile function
  it('should return isValid: false for undefined file', () => { // Expect validateFile(undefined).isValid to be false
    expect(validationUtils.validateFile(undefined).isValid).toBe(false);
  });

  it('should return isValid: false for null file', () => { // Expect validateFile(null).isValid to be false
    expect(validationUtils.validateFile(null).isValid).toBe(false);
  });

  it('should return isValid: false for file with invalid type', () => { // Expect validateFile(createMockFile({ type: 'application/pdf' }), { allowedTypes: ['image/jpeg'] }).isValid to be false
    expect(validationUtils.validateFile(createMockFile({ type: 'application/pdf' }), { allowedTypes: ['image/jpeg'] }).isValid).toBe(false);
  });

  it('should return isValid: false for file exceeding maximum size', () => { // Expect validateFile(createMockFile({ size: 6 * 1024 * 1024 }), { maxSizeMB: 5 }).isValid to be false
    expect(validationUtils.validateFile(createMockFile({ size: 6 * 1024 * 1024 }), { maxSizeMB: 5 }).isValid).toBe(false);
  });

  it('should return isValid: true for valid file', () => { // Expect validateFile(createMockFile({ type: 'image/jpeg', size: 4 * 1024 * 1024 }), { allowedTypes: ['image/jpeg'], maxSizeMB: 5 }).isValid to be true
    expect(validationUtils.validateFile(createMockFile({ type: 'image/jpeg', size: 4 * 1024 * 1024 }), { allowedTypes: ['image/jpeg'], maxSizeMB: 5 }).isValid).toBe(true);
  });

  it('should return appropriate error message for invalid file', () => { // Expect validateFile(createMockFile({ type: 'application/pdf' }), { allowedTypes: ['image/jpeg'] }).error to equal VALIDATION_MESSAGES.FILE_TYPE_INVALID
    expect(validationUtils.validateFile(createMockFile({ type: 'application/pdf' }), { allowedTypes: ['image/jpeg'] }).errorMessage).toEqual(VALIDATION_MESSAGES.FILE_TYPE_INVALID);
  });

  it('should use default allowed types when not provided', () => { // Expect validateFile(createMockFile({ type: 'image/jpeg' })).isValid to be true
    expect(validationUtils.validateFile(createMockFile({ type: 'image/jpeg' })).isValid).toBe(true);
  });

  it('should use default maximum size when not provided', () => { // Expect validateFile(createMockFile({ type: 'image/jpeg', size: 40 * 1024 * 1024 })).isValid to be true
    expect(validationUtils.validateFile(createMockFile({ type: 'image/jpeg', size: 40 * 1024 * 1024 })).isValid).toBe(true);
  });
});

describe('ALLOWED_FILE_TYPES', () => { // Tests for the ALLOWED_FILE_TYPES constant
  it('should be defined', () => { // Expect ALLOWED_FILE_TYPES to be defined
    expect(validationUtils.ALLOWED_FILE_TYPES).toBeDefined();
  });

  it('should be an array', () => { // Expect Array.isArray(ALLOWED_FILE_TYPES) to be true
    expect(Array.isArray(validationUtils.ALLOWED_FILE_TYPES)).toBe(true);
  });

  it('should include common file types', () => { // Expect ALLOWED_FILE_TYPES to include 'image/jpeg', 'image/png', 'text/csv', 'application/json'
    expect(validationUtils.ALLOWED_FILE_TYPES).toContain('image/jpeg');
    expect(validationUtils.ALLOWED_FILE_TYPES).toContain('image/png');
    expect(validationUtils.ALLOWED_FILE_TYPES).toContain('text/csv');
    expect(validationUtils.ALLOWED_FILE_TYPES).toContain('application/json');
  });
});

describe('MAX_FILE_SIZE_MB', () => { // Tests for the MAX_FILE_SIZE_MB constant
  it('should be defined', () => { // Expect MAX_FILE_SIZE_MB to be defined
    expect(validationUtils.MAX_FILE_SIZE_MB).toBeDefined();
  });

  it('should be a number', () => { // Expect typeof MAX_FILE_SIZE_MB to equal 'number'
    expect(typeof validationUtils.MAX_FILE_SIZE_MB).toEqual('number');
  });

  it('should be 50', () => { // Expect MAX_FILE_SIZE_MB to equal 50
    expect(validationUtils.MAX_FILE_SIZE_MB).toEqual(50);
  });
});