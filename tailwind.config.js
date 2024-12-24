/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/templates/**/*.{html,js}'],
  safelist: [
    'alert-info',
    'alert-success',
    'alert-warning',
    'alert-error',
  ],
  theme: {
    extend: {},
  },
  daisyui: {
    "themes": ['dark', 'light'],
  },
  plugins: [require('daisyui')],
}