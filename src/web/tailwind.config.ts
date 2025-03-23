import type { Config } from 'tailwindcss'; // tailwindcss v3.3.2
import forms from '@tailwindcss/forms'; // @tailwindcss/forms v0.5.3
import typography from '@tailwindcss/typography'; // @tailwindcss/typography v0.5.9
import aspectRatio from '@tailwindcss/aspect-ratio'; // @tailwindcss/aspect-ratio v0.4.2

const config: Config = {
  content: [
    './src/**/*.{js,ts,jsx,tsx}',
    './src/app/**/*.{js,ts,jsx,tsx}',
    './src/components/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        // Primary and secondary colors as per design system
        primary: {
          DEFAULT: '#0055A4', // IndiVillage primary blue
          light: '#3378B8',
          dark: '#004080',
        },
        secondary: {
          DEFAULT: '#FF671F', // IndiVillage secondary orange
          light: '#FF8A4D',
          dark: '#CC5219',
        },
        // Additional functional colors
        teal: '#046B99',
        green: '#2E8540',
        success: '#28A745',
        warning: '#FFC107',
        error: '#DC3545',
        info: '#17A2B8',
        // Neutral color palette
        gray: {
          50: '#F8F9FA',  // Off-white
          100: '#E9ECEF', // Light gray
          200: '#DEE2E6',
          300: '#CED4DA',
          400: '#ADB5BD',
          500: '#6C757D', // Medium gray
          600: '#495057',
          700: '#343A40',
          800: '#212529', // Dark gray
          900: '#121416',
        },
      },
      fontFamily: {
        // Typography as per design system
        heading: ['Montserrat', 'sans-serif'],
        body: ['Open Sans', 'sans-serif'],
      },
      fontSize: {
        // Font size scale
        xs: '0.875rem',    // 14px
        sm: '1rem',        // 16px
        base: '1rem',      // 16px
        lg: '1.125rem',    // 18px
        xl: '1.25rem',     // 20px
        '2xl': '1.5rem',   // 24px
        '3xl': '1.875rem', // 30px
        '4xl': '2.25rem',  // 36px
        '5xl': '3rem',     // 48px
      },
      fontWeight: {
        light: '300',
        normal: '400',
        medium: '500',
        semibold: '600',
        bold: '700',
      },
      lineHeight: {
        none: '1',
        tight: '1.2',   // Headings
        normal: '1.5',  // Body
        relaxed: '1.625',
        loose: '2',
      },
      spacing: {
        // Spacing system
        xs: '0.25rem',  // 4px
        sm: '0.5rem',   // 8px
        md: '1rem',     // 16px
        lg: '1.5rem',   // 24px
        xl: '2rem',     // 32px
        '2xl': '3rem',  // 48px
        '3xl': '4rem',  // 64px
        '4xl': '6rem',  // 96px
      },
      borderRadius: {
        none: '0',
        xs: '0.125rem',  // 2px
        sm: '0.25rem',   // 4px
        md: '0.375rem',  // 6px
        lg: '0.5rem',    // 8px
        xl: '0.75rem',   // 12px
        '2xl': '1rem',   // 16px
        full: '9999px',
      },
      boxShadow: {
        xs: '0 1px 2px rgba(0, 0, 0, 0.05)',
        sm: '0 1px 3px rgba(0, 0, 0, 0.1)',
        md: '0 4px 6px rgba(0, 0, 0, 0.1)',
        lg: '0 10px 15px rgba(0, 0, 0, 0.1)',
        xl: '0 20px 25px rgba(0, 0, 0, 0.1)',
        inner: 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.06)',
      },
      transitionDuration: {
        micro: '100ms',
        subtle: '200ms',
        standard: '300ms',
        page: '500ms',
      },
      transitionTimingFunction: {
        'in': 'cubic-bezier(0.4, 0, 1, 1)',
        'out': 'cubic-bezier(0, 0, 0.2, 1)',
        'in-out': 'cubic-bezier(0.4, 0, 0.2, 1)',
        'spring': 'cubic-bezier(0.175, 0.885, 0.32, 1.275)',
      },
      zIndex: {
        negative: '-1',
        0: '0',
        10: '10',
        20: '20',
        30: '30',
        40: '40',
        50: '50',
        auto: 'auto',
      },
      screens: {
        // Responsive breakpoints as per 7.12
        xs: '375px',    // Mobile Small (376px - 767px)
        sm: '768px',    // Tablet (768px - 1023px)
        md: '1024px',   // Desktop (1024px - 1439px)
        lg: '1440px',   // Large Desktop (≥ 1440px)
        xl: '1920px',
      },
      container: {
        center: true,
        padding: {
          DEFAULT: '1rem',
          md: '2rem',
          lg: '4rem',
        },
        screens: {
          sm: '100%',
          md: '100%',
          lg: '1024px',
          xl: '1200px',
        },
      },
    },
  },
  plugins: [
    forms,
    typography,
    aspectRatio,
  ],
  // Classes to always include (not purged)
  safelist: [
    'bg-primary',
    'bg-secondary',
    'text-primary',
    'text-secondary',
    'border-primary',
    'border-secondary',
    // Form status classes
    'bg-success',
    'bg-error',
    'bg-warning',
    'bg-info',
    'text-success',
    'text-error',
    'text-warning',
    'text-info',
    // Accessibility classes
    'focus:ring',
    'focus:outline-none',
    'focus:ring-primary',
    'focus-visible:ring',
  ],
};

export default config;