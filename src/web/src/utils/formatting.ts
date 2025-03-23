/**
 * Utility functions for formatting various data types including numbers, currency, 
 * percentages, file sizes, text, and lists. These functions ensure consistent 
 * data presentation throughout the IndiVillage website.
 * 
 * Uses the browser's Intl API for locale-aware formatting.
 */

// Default locale for formatting
export const DEFAULT_LOCALE = 'en-US';

// Units for file size formatting
export const FILE_SIZE_UNITS = ['B', 'KB', 'MB', 'GB', 'TB'];

/**
 * Formats a number with thousand separators and decimal places
 * 
 * @param value - The number to format
 * @param decimalPlaces - Number of decimal places to show (default: 0)
 * @param locale - The locale to use for formatting (default: DEFAULT_LOCALE)
 * @returns Formatted number string or empty string if input is invalid
 */
export const formatNumber = (
  value: number,
  decimalPlaces: number = 0,
  locale: string = DEFAULT_LOCALE
): string => {
  if (typeof value !== 'number' || isNaN(value)) {
    return '';
  }

  return new Intl.NumberFormat(locale, {
    maximumFractionDigits: decimalPlaces,
    minimumFractionDigits: decimalPlaces
  }).format(value);
};

/**
 * Formats a number as currency with the specified currency code
 * 
 * @param value - The number to format as currency
 * @param currencyCode - The ISO 4217 currency code (default: 'USD')
 * @param locale - The locale to use for formatting (default: DEFAULT_LOCALE)
 * @returns Formatted currency string or empty string if input is invalid
 */
export const formatCurrency = (
  value: number,
  currencyCode: string = 'USD',
  locale: string = DEFAULT_LOCALE
): string => {
  if (typeof value !== 'number' || isNaN(value)) {
    return '';
  }

  return new Intl.NumberFormat(locale, {
    style: 'currency',
    currency: currencyCode,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(value);
};

/**
 * Formats a number as a percentage
 * 
 * @param value - The number to format as percentage (0.1 = 10%)
 * @param decimalPlaces - Number of decimal places to show (default: 0)
 * @param locale - The locale to use for formatting (default: DEFAULT_LOCALE)
 * @returns Formatted percentage string or empty string if input is invalid
 */
export const formatPercentage = (
  value: number,
  decimalPlaces: number = 0,
  locale: string = DEFAULT_LOCALE
): string => {
  if (typeof value !== 'number' || isNaN(value)) {
    return '';
  }

  return new Intl.NumberFormat(locale, {
    style: 'percent',
    maximumFractionDigits: decimalPlaces,
    minimumFractionDigits: decimalPlaces
  }).format(value);
};

/**
 * Formats a file size in bytes to a human-readable string
 * 
 * @param bytes - The file size in bytes
 * @param decimalPlaces - Number of decimal places to show (default: 2)
 * @returns Formatted file size string (e.g., "2.5 MB")
 */
export const formatFileSize = (
  bytes: number,
  decimalPlaces: number = 2
): string => {
  if (typeof bytes !== 'number' || isNaN(bytes) || bytes < 0) {
    return '0 B';
  }

  if (bytes === 0) {
    return '0 B';
  }

  const k = 1024;
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  const size = parseFloat((bytes / Math.pow(k, i)).toFixed(decimalPlaces));

  return `${formatNumber(size, decimalPlaces)} ${FILE_SIZE_UNITS[i]}`;
};

/**
 * Truncates text to a specified maximum length with ellipsis
 * 
 * @param text - The text to truncate
 * @param maxLength - Maximum length of the returned string including ellipsis (default: 100)
 * @param ellipsis - The ellipsis string to append (default: "...")
 * @returns Truncated text string with ellipsis or original text if short enough
 */
export const truncateText = (
  text: string,
  maxLength: number = 100,
  ellipsis: string = '...'
): string => {
  if (typeof text !== 'string') {
    return '';
  }

  if (text.length <= maxLength) {
    return text;
  }

  return text.slice(0, maxLength - ellipsis.length) + ellipsis;
};

/**
 * Capitalizes the first letter of a string
 * 
 * @param text - The string to capitalize
 * @returns String with first letter capitalized
 */
export const capitalizeFirstLetter = (text: string): string => {
  if (typeof text !== 'string' || !text.length) {
    return text;
  }

  return text.charAt(0).toUpperCase() + text.slice(1);
};

/**
 * Formats a phone number according to a specified pattern
 * 
 * @param phoneNumber - The phone number to format
 * @param format - The format pattern (default: "+1 (###) ###-####")
 *   Use # as placeholder for digits
 * @returns Formatted phone number or empty string if input is invalid
 */
export const formatPhoneNumber = (
  phoneNumber: string,
  format: string = '+1 (###) ###-####'
): string => {
  if (typeof phoneNumber !== 'string') {
    return '';
  }

  // Extract digits only
  const digits = phoneNumber.replace(/\D/g, '');
  
  if (!digits.length) {
    return '';
  }

  let result = format;
  let digitIndex = 0;

  // Replace each # in the format with a digit
  for (let i = 0; i < result.length && digitIndex < digits.length; i++) {
    if (result[i] === '#') {
      result = result.substring(0, i) + digits[digitIndex++] + result.substring(i + 1);
    }
  }

  // Remove any remaining placeholders
  result = result.replace(/#/g, '');

  return result;
};

/**
 * Formats a number in compact notation (K, M, B)
 * 
 * @param value - The number to format
 * @param locale - The locale to use for formatting (default: DEFAULT_LOCALE)
 * @returns Compact formatted number (e.g., "1.2K" for 1200)
 */
export const formatCompactNumber = (
  value: number,
  locale: string = DEFAULT_LOCALE
): string => {
  if (typeof value !== 'number' || isNaN(value)) {
    return '';
  }

  return new Intl.NumberFormat(locale, {
    notation: 'compact',
    compactDisplay: 'short'
  }).format(value);
};

/**
 * Formats an array of items into a readable list with conjunction
 * 
 * @param items - Array of strings to format as a list
 * @param conjunction - The conjunction to use between the last two items (default: "and")
 * @param locale - The locale to use for formatting (default: DEFAULT_LOCALE)
 * @returns Formatted list string (e.g., "apples, bananas, and oranges")
 */
export const formatList = (
  items: string[],
  conjunction: string = 'and',
  locale: string = DEFAULT_LOCALE
): string => {
  if (!Array.isArray(items) || items.length === 0) {
    return '';
  }

  if (items.length === 1) {
    return items[0];
  }

  if (items.length === 2) {
    return `${items[0]} ${conjunction} ${items[1]}`;
  }

  // For lists with more than 2 items, join all but the last with commas
  // and add the conjunction before the last item
  const formatter = new Intl.ListFormat(locale, {
    style: 'long',
    type: 'conjunction'
  });

  // Some browsers may not support ListFormat, so provide a fallback
  try {
    return formatter.format(items);
  } catch (e) {
    const lastItem = items[items.length - 1];
    const otherItems = items.slice(0, -1).join(', ');
    return `${otherItems}, ${conjunction} ${lastItem}`;
  }
};

/**
 * Converts a string to a URL-friendly slug
 * 
 * @param text - The text to convert to a slug
 * @returns URL-friendly slug
 */
export const slugify = (text: string): string => {
  if (typeof text !== 'string') {
    return '';
  }

  return text
    .toString()
    .toLowerCase()
    .trim()
    // Replace spaces with hyphens
    .replace(/\s+/g, '-')
    // Remove accents from characters
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    // Remove non-word characters, keep hyphens and spaces
    .replace(/[^\w\-]+/g, '')
    // Replace multiple hyphens with a single hyphen
    .replace(/\-\-+/g, '-');
};