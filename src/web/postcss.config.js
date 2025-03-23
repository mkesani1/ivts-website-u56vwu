/**
 * PostCSS Configuration
 * 
 * This file configures the PostCSS processing pipeline for the IndiVillage website.
 * It sets up TailwindCSS for utility-class generation and Autoprefixer for
 * cross-browser compatibility.
 * 
 * @see https://tailwindcss.com/docs/installation
 * @see https://github.com/postcss/autoprefixer
 */

const tailwindcss = require('tailwindcss'); // tailwindcss v3.3.2
const autoprefixer = require('autoprefixer'); // autoprefixer v10.4.14

/**
 * PostCSS configuration object
 * 
 * The order of plugins is important:
 * 1. TailwindCSS processes the utility directives first
 * 2. Autoprefixer adds vendor prefixes to the generated CSS
 * 
 * In production, TailwindCSS will automatically purge unused styles
 * based on the configuration in tailwind.config.ts
 */
module.exports = {
  plugins: [
    tailwindcss,
    autoprefixer,
  ],
};