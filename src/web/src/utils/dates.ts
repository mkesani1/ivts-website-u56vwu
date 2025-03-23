import {
  format,
  parse,
  isValid,
  addDays,
  addMonths,
  differenceInDays
} from 'date-fns'; // date-fns version: ^2.30.0

// Default formats and locale
export const DEFAULT_DATE_FORMAT = 'MMM d, yyyy';
export const DEFAULT_TIME_FORMAT = 'h:mm a';
export const DEFAULT_DATETIME_FORMAT = 'MMM d, yyyy h:mm a';
export const DEFAULT_LOCALE = 'en-US';

/**
 * Formats a date object or string into a human-readable date string
 *
 * @param date - The date to format
 * @param formatStr - The format string to use (default: DEFAULT_DATE_FORMAT)
 * @param locale - The locale to use for formatting (default: DEFAULT_LOCALE)
 * @returns Formatted date string or empty string if date is invalid
 */
export function formatDate(
  date: Date | string | number,
  formatStr: string = DEFAULT_DATE_FORMAT,
  locale: string = DEFAULT_LOCALE
): string {
  if (!isValidDate(date)) {
    return '';
  }
  
  try {
    return format(new Date(date), formatStr);
  } catch (error) {
    console.error('Error formatting date:', error);
    return '';
  }
}

/**
 * Formats a date object or string into a human-readable time string
 *
 * @param date - The date to format
 * @param formatStr - The format string to use (default: DEFAULT_TIME_FORMAT)
 * @param locale - The locale to use for formatting (default: DEFAULT_LOCALE)
 * @returns Formatted time string or empty string if date is invalid
 */
export function formatTime(
  date: Date | string | number,
  formatStr: string = DEFAULT_TIME_FORMAT,
  locale: string = DEFAULT_LOCALE
): string {
  if (!isValidDate(date)) {
    return '';
  }
  
  try {
    return format(new Date(date), formatStr);
  } catch (error) {
    console.error('Error formatting time:', error);
    return '';
  }
}

/**
 * Formats a date object or string into a human-readable date and time string
 *
 * @param date - The date to format
 * @param formatStr - The format string to use (default: DEFAULT_DATETIME_FORMAT)
 * @param locale - The locale to use for formatting (default: DEFAULT_LOCALE)
 * @returns Formatted date and time string or empty string if date is invalid
 */
export function formatDateTime(
  date: Date | string | number,
  formatStr: string = DEFAULT_DATETIME_FORMAT,
  locale: string = DEFAULT_LOCALE
): string {
  if (!isValidDate(date)) {
    return '';
  }
  
  try {
    return format(new Date(date), formatStr);
  } catch (error) {
    console.error('Error formatting date and time:', error);
    return '';
  }
}

/**
 * Parses a date string into a Date object
 *
 * @param dateStr - The date string to parse
 * @param formatStr - The format string to use (default: DEFAULT_DATE_FORMAT)
 * @param referenceDate - The reference date to use for relative parsing (default: new Date())
 * @returns Parsed Date object or invalid Date if parsing fails
 */
export function parseDate(
  dateStr: string,
  formatStr: string = DEFAULT_DATE_FORMAT,
  referenceDate: Date = new Date()
): Date {
  if (!dateStr || typeof dateStr !== 'string') {
    return new Date(NaN);
  }
  
  try {
    return parse(dateStr, formatStr, referenceDate);
  } catch (error) {
    console.error('Error parsing date:', error);
    return new Date(NaN);
  }
}

/**
 * Checks if a date object or string is valid
 *
 * @param date - The date to validate
 * @param formatStr - The format string to use if date is a string
 * @returns True if the date is valid, false otherwise
 */
export function isValidDate(
  date: Date | string | number,
  formatStr?: string
): boolean {
  if (!date) {
    return false;
  }
  
  let dateObj: Date;
  
  if (typeof date === 'string' && formatStr) {
    dateObj = parseDate(date, formatStr);
  } else {
    dateObj = new Date(date);
  }
  
  return isValid(dateObj);
}

/**
 * Returns a relative time string (e.g., '2 days ago', 'in 3 months')
 *
 * @param date - The date to format
 * @param locale - The locale to use for formatting (default: DEFAULT_LOCALE)
 * @returns Relative time string or empty string if date is invalid
 */
export function getRelativeTimeString(
  date: Date | string | number,
  locale: string = DEFAULT_LOCALE
): string {
  if (!isValidDate(date)) {
    return '';
  }
  
  const dateObj = new Date(date);
  const now = new Date();
  const diffInMilliseconds = dateObj.getTime() - now.getTime();
  
  // Determine the appropriate unit
  const getRelativeTime = (diffMs: number): [number, Intl.RelativeTimeFormatUnit] => {
    const seconds = Math.floor(Math.abs(diffMs) / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);
    const months = Math.floor(days / 30);
    const years = Math.floor(months / 12);
    
    if (years > 0) return [years, 'year'];
    if (months > 0) return [months, 'month'];
    if (days > 0) return [days, 'day'];
    if (hours > 0) return [hours, 'hour'];
    if (minutes > 0) return [minutes, 'minute'];
    return [seconds, 'second'];
  };
  
  const [value, unit] = getRelativeTime(diffInMilliseconds);
  const formatter = new Intl.RelativeTimeFormat(locale, { numeric: 'auto' });
  
  return formatter.format(diffInMilliseconds < 0 ? -value : value, unit);
}

/**
 * Returns a human-readable string representing time elapsed since the given date
 *
 * @param date - The date to format
 * @param locale - The locale to use for formatting (default: DEFAULT_LOCALE)
 * @returns Time ago string or empty string if date is invalid
 */
export function getTimeAgo(
  date: Date | string | number,
  locale: string = DEFAULT_LOCALE
): string {
  if (!isValidDate(date)) {
    return '';
  }
  
  const dateObj = new Date(date);
  const now = new Date();
  const diffInSeconds = Math.floor((now.getTime() - dateObj.getTime()) / 1000);
  
  if (diffInSeconds < 5) {
    return 'just now';
  }
  
  if (diffInSeconds < 60) {
    return `${diffInSeconds} seconds ago`;
  }
  
  const diffInMinutes = Math.floor(diffInSeconds / 60);
  if (diffInMinutes < 60) {
    return diffInMinutes === 1 ? 'a minute ago' : `${diffInMinutes} minutes ago`;
  }
  
  const diffInHours = Math.floor(diffInMinutes / 60);
  if (diffInHours < 24) {
    return diffInHours === 1 ? 'an hour ago' : `${diffInHours} hours ago`;
  }
  
  const diffInDays = Math.floor(diffInHours / 24);
  if (diffInDays < 7) {
    return diffInDays === 1 ? 'yesterday' : `${diffInDays} days ago`;
  }
  
  const diffInWeeks = Math.floor(diffInDays / 7);
  if (diffInWeeks < 4) {
    return diffInWeeks === 1 ? 'a week ago' : `${diffInWeeks} weeks ago`;
  }
  
  const diffInMonths = Math.floor(diffInDays / 30);
  if (diffInMonths < 12) {
    return diffInMonths === 1 ? 'a month ago' : `${diffInMonths} months ago`;
  }
  
  const diffInYears = Math.floor(diffInDays / 365);
  return diffInYears === 1 ? 'a year ago' : `${diffInYears} years ago`;
}

/**
 * Formats a date range into a human-readable string
 *
 * @param startDate - The start date of the range
 * @param endDate - The end date of the range
 * @param formatStr - The format string to use (default: DEFAULT_DATE_FORMAT)
 * @param locale - The locale to use for formatting (default: DEFAULT_LOCALE)
 * @returns Formatted date range string or empty string if either date is invalid
 */
export function getDateRangeString(
  startDate: Date | string | number,
  endDate: Date | string | number,
  formatStr: string = DEFAULT_DATE_FORMAT,
  locale: string = DEFAULT_LOCALE
): string {
  if (!isValidDate(startDate) || !isValidDate(endDate)) {
    return '';
  }
  
  const formattedStartDate = formatDate(startDate, formatStr, locale);
  const formattedEndDate = formatDate(endDate, formatStr, locale);
  
  return `${formattedStartDate} - ${formattedEndDate}`;
}

/**
 * Returns the local time zone identifier
 *
 * @returns Local time zone identifier
 */
export function getLocalTimeZone(): string {
  return Intl.DateTimeFormat().resolvedOptions().timeZone;
}

/**
 * Returns a list of common time zones for use in select inputs
 *
 * @returns Array of time zone options with value and label properties
 */
export function getTimeZoneOptions(): Array<{value: string, label: string}> {
  return [
    { value: 'America/New_York', label: 'Eastern Time (ET)' },
    { value: 'America/Chicago', label: 'Central Time (CT)' },
    { value: 'America/Denver', label: 'Mountain Time (MT)' },
    { value: 'America/Los_Angeles', label: 'Pacific Time (PT)' },
    { value: 'America/Anchorage', label: 'Alaska Time (AKT)' },
    { value: 'Pacific/Honolulu', label: 'Hawaii Time (HT)' },
    { value: 'Europe/London', label: 'Greenwich Mean Time (GMT)' },
    { value: 'Europe/Paris', label: 'Central European Time (CET)' },
    { value: 'Europe/Helsinki', label: 'Eastern European Time (EET)' },
    { value: 'Asia/Kolkata', label: 'India Standard Time (IST)' },
    { value: 'Asia/Tokyo', label: 'Japan Standard Time (JST)' },
    { value: 'Asia/Shanghai', label: 'China Standard Time (CST)' },
    { value: 'Australia/Sydney', label: 'Australian Eastern Time (AET)' },
    { value: 'Pacific/Auckland', label: 'New Zealand Standard Time (NZST)' }
  ];
}

/**
 * Calculates the number of business days (excluding weekends) between two dates
 *
 * @param startDate - The start date
 * @param endDate - The end date
 * @returns Number of business days or 0 if either date is invalid
 */
export function getBusinessDays(
  startDate: Date | string | number,
  endDate: Date | string | number
): number {
  if (!isValidDate(startDate) || !isValidDate(endDate)) {
    return 0;
  }
  
  const start = new Date(startDate);
  const end = new Date(endDate);
  
  // Ensure the start date is before the end date
  if (start > end) {
    return getBusinessDays(end, start);
  }
  
  // Clone dates to avoid modifying the originals
  const startCopy = new Date(start);
  const endCopy = new Date(end);
  
  // Normalize dates to midnight
  startCopy.setHours(0, 0, 0, 0);
  endCopy.setHours(0, 0, 0, 0);
  
  // Calculate total days (including weekends)
  const totalDays = Math.round(
    (endCopy.getTime() - startCopy.getTime()) / (24 * 60 * 60 * 1000)
  );
  
  // Calculate number of weekend days
  let weekendDays = 0;
  const currentDate = new Date(startCopy);
  
  for (let i = 0; i <= totalDays; i++) {
    const dayOfWeek = currentDate.getDay();
    if (dayOfWeek === 0 || dayOfWeek === 6) {
      weekendDays++;
    }
    currentDate.setDate(currentDate.getDate() + 1);
  }
  
  return totalDays - weekendDays + 1; // +1 to include the end date
}

/**
 * Adds a specified number of business days to a date
 *
 * @param date - The starting date
 * @param days - The number of business days to add
 * @returns Resulting date after adding business days or invalid Date if input is invalid
 */
export function addBusinessDays(
  date: Date | string | number,
  days: number
): Date {
  if (!isValidDate(date)) {
    return new Date(NaN);
  }
  
  const result = new Date(date);
  let businessDaysAdded = 0;
  let currentDay = 0;
  
  while (businessDaysAdded < days) {
    result.setDate(result.getDate() + 1);
    currentDay = result.getDay();
    
    // Skip weekends (0 = Sunday, 6 = Saturday)
    if (currentDay !== 0 && currentDay !== 6) {
      businessDaysAdded++;
    }
  }
  
  return result;
}