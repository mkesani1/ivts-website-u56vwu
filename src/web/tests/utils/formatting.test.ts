import * as formattingUtils from '../../src/utils/formatting';

describe('formatNumber', () => {
  it('should return empty string for undefined value', () => {
    expect(formattingUtils.formatNumber(undefined as any)).toBe('');
  });

  it('should return empty string for null value', () => {
    expect(formattingUtils.formatNumber(null as any)).toBe('');
  });

  it('should format integer with thousand separators', () => {
    expect(formattingUtils.formatNumber(1000)).toBe('1,000');
  });

  it('should format decimal number with default decimal places', () => {
    expect(formattingUtils.formatNumber(1234.56)).toBe('1,234.56');
  });

  it('should format number with specified decimal places', () => {
    expect(formattingUtils.formatNumber(1234.5678, 3)).toBe('1,234.568');
  });

  it('should round number to specified decimal places', () => {
    expect(formattingUtils.formatNumber(1234.5678, 2)).toBe('1,234.57');
  });

  it('should format number with specified locale', () => {
    expect(formattingUtils.formatNumber(1234.56, 2, 'de-DE')).toBe('1.234,56');
  });

  it('should use DEFAULT_LOCALE when locale not provided', () => {
    const expected = new Intl.NumberFormat(formattingUtils.DEFAULT_LOCALE, {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(1234.56);
    expect(formattingUtils.formatNumber(1234.56, 2)).toBe(expected);
  });
});

describe('formatCurrency', () => {
  it('should return empty string for undefined value', () => {
    expect(formattingUtils.formatCurrency(undefined as any, 'USD')).toBe('');
  });

  it('should return empty string for null value', () => {
    expect(formattingUtils.formatCurrency(null as any, 'USD')).toBe('');
  });

  it('should format currency with USD by default', () => {
    expect(formattingUtils.formatCurrency(1234.56)).toContain('$');
  });

  it('should format currency with specified currency code', () => {
    expect(formattingUtils.formatCurrency(1234.56, 'EUR')).toContain('€');
  });

  it('should format currency with specified locale', () => {
    expect(formattingUtils.formatCurrency(1234.56, 'EUR', 'de-DE')).toContain('1.234,56');
  });

  it('should use DEFAULT_LOCALE when locale not provided', () => {
    const expected = new Intl.NumberFormat(formattingUtils.DEFAULT_LOCALE, {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(1234.56);
    expect(formattingUtils.formatCurrency(1234.56, 'USD')).toBe(expected);
  });
});

describe('formatPercentage', () => {
  it('should return empty string for undefined value', () => {
    expect(formattingUtils.formatPercentage(undefined as any)).toBe('');
  });

  it('should return empty string for null value', () => {
    expect(formattingUtils.formatPercentage(null as any)).toBe('');
  });

  it('should format decimal as percentage', () => {
    expect(formattingUtils.formatPercentage(0.1234, 2)).toBe('12.34%');
  });

  it('should format number with specified decimal places', () => {
    expect(formattingUtils.formatPercentage(0.1234, 1)).toBe('12.3%');
  });

  it('should round percentage to specified decimal places', () => {
    expect(formattingUtils.formatPercentage(0.1235, 1)).toBe('12.4%');
  });

  it('should format percentage with specified locale', () => {
    expect(formattingUtils.formatPercentage(0.1234, 2, 'de-DE')).toBe('12,34%');
  });

  it('should use DEFAULT_LOCALE when locale not provided', () => {
    const expected = new Intl.NumberFormat(formattingUtils.DEFAULT_LOCALE, {
      style: 'percent',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(0.1234);
    expect(formattingUtils.formatPercentage(0.1234, 2)).toBe(expected);
  });
});

describe('formatFileSize', () => {
  it("should return '0 B' for undefined value", () => {
    expect(formattingUtils.formatFileSize(undefined as any)).toBe('0 B');
  });

  it("should return '0 B' for null value", () => {
    expect(formattingUtils.formatFileSize(null as any)).toBe('0 B');
  });

  it("should return '0 B' for negative value", () => {
    expect(formattingUtils.formatFileSize(-100)).toBe('0 B');
  });

  it('should format bytes correctly', () => {
    expect(formattingUtils.formatFileSize(500)).toBe('500 B');
  });

  it('should format kilobytes correctly', () => {
    expect(formattingUtils.formatFileSize(1024)).toBe('1 KB');
  });

  it('should format megabytes correctly', () => {
    expect(formattingUtils.formatFileSize(1048576)).toBe('1 MB');
  });

  it('should format gigabytes correctly', () => {
    expect(formattingUtils.formatFileSize(1073741824)).toBe('1 GB');
  });

  it('should format terabytes correctly', () => {
    expect(formattingUtils.formatFileSize(1099511627776)).toBe('1 TB');
  });

  it('should use specified decimal places', () => {
    expect(formattingUtils.formatFileSize(1500000, 1)).toBe('1.4 MB');
  });

  it('should use default decimal places (2) when not specified', () => {
    expect(formattingUtils.formatFileSize(1500000)).toBe('1.43 MB');
  });
});

describe('truncateText', () => {
  it('should return empty string for undefined value', () => {
    expect(formattingUtils.truncateText(undefined as any)).toBe('');
  });

  it('should return empty string for null value', () => {
    expect(formattingUtils.truncateText(null as any)).toBe('');
  });

  it('should not truncate text shorter than maxLength', () => {
    expect(formattingUtils.truncateText('Short text', 20)).toBe('Short text');
  });

  it('should not truncate text equal to maxLength', () => {
    expect(formattingUtils.truncateText('Exactly 20 characters', 20)).toBe('Exactly 20 characters');
  });

  it('should truncate text longer than maxLength', () => {
    expect(formattingUtils.truncateText('This text is too long', 10)).toBe('This te...');
  });

  it('should use custom ellipsis when provided', () => {
    expect(formattingUtils.truncateText('This text is too long', 10, ' [more]')).toBe('This t [more]');
  });

  it('should use default maxLength (50) when not specified', () => {
    const longText = 'A'.repeat(60);
    expect(formattingUtils.truncateText(longText)).toBe('A'.repeat(47) + '...');
  });

  it("should use default ellipsis ('...') when not specified", () => {
    expect(formattingUtils.truncateText('This text is too long', 10)).toBe('This te...');
  });
});

describe('capitalizeFirstLetter', () => {
  it('should return empty string for undefined value', () => {
    expect(formattingUtils.capitalizeFirstLetter(undefined as any)).toBe('');
  });

  it('should return empty string for null value', () => {
    expect(formattingUtils.capitalizeFirstLetter(null as any)).toBe('');
  });

  it('should return empty string for empty string', () => {
    expect(formattingUtils.capitalizeFirstLetter('')).toBe('');
  });

  it('should capitalize first letter of single word', () => {
    expect(formattingUtils.capitalizeFirstLetter('hello')).toBe('Hello');
  });

  it('should only capitalize first letter of sentence', () => {
    expect(formattingUtils.capitalizeFirstLetter('hello world')).toBe('Hello world');
  });

  it('should handle already capitalized text', () => {
    expect(formattingUtils.capitalizeFirstLetter('Hello')).toBe('Hello');
  });

  it('should handle text with first character non-letter', () => {
    expect(formattingUtils.capitalizeFirstLetter('123abc')).toBe('123abc');
  });
});

describe('formatPhoneNumber', () => {
  it('should return empty string for undefined value', () => {
    expect(formattingUtils.formatPhoneNumber(undefined as any)).toBe('');
  });

  it('should return empty string for null value', () => {
    expect(formattingUtils.formatPhoneNumber(null as any)).toBe('');
  });

  it('should return empty string for empty string', () => {
    expect(formattingUtils.formatPhoneNumber('')).toBe('');
  });

  it('should format 10-digit number with default format', () => {
    expect(formattingUtils.formatPhoneNumber('1234567890')).toBe('+1 (123) 456-7890');
  });

  it('should format number with custom format', () => {
    expect(formattingUtils.formatPhoneNumber('1234567890', '###-###-####')).toBe('123-456-7890');
  });

  it('should handle phone number with non-digit characters', () => {
    expect(formattingUtils.formatPhoneNumber('(123) 456-7890')).toBe('+1 (123) 456-7890');
  });

  it('should handle phone number with fewer digits than format', () => {
    expect(formattingUtils.formatPhoneNumber('12345')).toBe('+1 (123) 45');
  });

  it('should handle phone number with more digits than format', () => {
    expect(formattingUtils.formatPhoneNumber('12345678901234')).toBe('+1 (123) 456-7890');
  });
});

describe('formatCompactNumber', () => {
  it('should return empty string for undefined value', () => {
    expect(formattingUtils.formatCompactNumber(undefined as any)).toBe('');
  });

  it('should return empty string for null value', () => {
    expect(formattingUtils.formatCompactNumber(null as any)).toBe('');
  });

  it('should format thousands with K', () => {
    expect(formattingUtils.formatCompactNumber(1500)).toContain('K');
  });

  it('should format millions with M', () => {
    expect(formattingUtils.formatCompactNumber(1500000)).toContain('M');
  });

  it('should format billions with B', () => {
    expect(formattingUtils.formatCompactNumber(1500000000)).toContain('B');
  });

  it('should not use compact notation for small numbers', () => {
    expect(formattingUtils.formatCompactNumber(150)).not.toContain('K');
  });

  it('should format with specified locale', () => {
    const formatted = formattingUtils.formatCompactNumber(1500000, 'de-DE');
    expect(formatted.length).toBeLessThan('1500000'.length);
  });

  it('should use DEFAULT_LOCALE when locale not provided', () => {
    const expected = new Intl.NumberFormat(formattingUtils.DEFAULT_LOCALE, {
      notation: 'compact',
      compactDisplay: 'short'
    }).format(1500000);
    expect(formattingUtils.formatCompactNumber(1500000)).toBe(expected);
  });
});

describe('formatList', () => {
  it('should return empty string for undefined value', () => {
    expect(formattingUtils.formatList(undefined as any)).toBe('');
  });

  it('should return empty string for null value', () => {
    expect(formattingUtils.formatList(null as any)).toBe('');
  });

  it('should return empty string for empty array', () => {
    expect(formattingUtils.formatList([])).toBe('');
  });

  it('should return single item without conjunction', () => {
    expect(formattingUtils.formatList(['apple'])).toBe('apple');
  });

  it('should join two items with conjunction', () => {
    expect(formattingUtils.formatList(['apple', 'banana'])).toBe('apple and banana');
  });

  it('should join multiple items with commas and conjunction', () => {
    const result = formattingUtils.formatList(['apple', 'banana', 'orange']);
    expect(result).toContain('apple');
    expect(result).toContain('banana');
    expect(result).toContain('and orange');
  });

  it('should use custom conjunction when provided', () => {
    expect(formattingUtils.formatList(['apple', 'banana'], 'or')).toBe('apple or banana');
  });

  it('should use specified locale for formatting', () => {
    const result = formattingUtils.formatList(['apple', 'banana', 'orange'], 'and', 'fr-FR');
    expect(result).toContain('apple');
    expect(result).toContain('banana');
    expect(result).toContain('orange');
  });

  it("should use default conjunction ('and') when not specified", () => {
    expect(formattingUtils.formatList(['apple', 'banana'])).toBe('apple and banana');
  });

  it('should use DEFAULT_LOCALE when locale not provided', () => {
    expect(formattingUtils.formatList(['apple', 'banana', 'orange'])).toContain('and');
  });
});

describe('slugify', () => {
  it('should return empty string for undefined value', () => {
    expect(formattingUtils.slugify(undefined as any)).toBe('');
  });

  it('should return empty string for null value', () => {
    expect(formattingUtils.slugify(null as any)).toBe('');
  });

  it('should return empty string for empty string', () => {
    expect(formattingUtils.slugify('')).toBe('');
  });

  it('should convert spaces to hyphens', () => {
    expect(formattingUtils.slugify('hello world')).toBe('hello-world');
  });

  it('should convert to lowercase', () => {
    expect(formattingUtils.slugify('Hello World')).toBe('hello-world');
  });

  it('should remove special characters', () => {
    expect(formattingUtils.slugify('hello! world?')).toBe('hello-world');
  });

  it('should remove accents from characters', () => {
    expect(formattingUtils.slugify('héllö wörld')).toBe('hello-world');
  });

  it('should handle multiple spaces and special characters', () => {
    expect(formattingUtils.slugify('  hello  world!  ')).toBe('hello-world');
  });

  it('should handle numbers', () => {
    expect(formattingUtils.slugify('hello world 123')).toBe('hello-world-123');
  });
});

describe('DEFAULT_LOCALE', () => {
  it('should be defined', () => {
    expect(formattingUtils.DEFAULT_LOCALE).toBeDefined();
  });

  it('should be a string', () => {
    expect(typeof formattingUtils.DEFAULT_LOCALE).toBe('string');
  });

  it("should be 'en-US'", () => {
    expect(formattingUtils.DEFAULT_LOCALE).toBe('en-US');
  });
});

describe('FILE_SIZE_UNITS', () => {
  it('should be defined', () => {
    expect(formattingUtils.FILE_SIZE_UNITS).toBeDefined();
  });

  it('should be an array', () => {
    expect(Array.isArray(formattingUtils.FILE_SIZE_UNITS)).toBe(true);
  });

  it('should contain expected units', () => {
    expect(formattingUtils.FILE_SIZE_UNITS).toEqual(['B', 'KB', 'MB', 'GB', 'TB']);
  });
});