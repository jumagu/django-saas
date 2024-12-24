/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/templates/**/*.{html,js}'],
  theme: {
    extend: {},
  },
  daisyui: {
    "themes": ['dark', 'light'],
  },
  plugins: [require('daisyui')],
}