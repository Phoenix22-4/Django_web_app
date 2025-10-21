/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./dashboard/templates/**/*.html",
    "./dashboard/static/**/*.js",
    "./dashboard/static/**/*.css",
  ],
  theme: {
    extend: {
      colors: {
        'sky-blue': '#0ea5e9',
        'sky-blue-dark': '#0284c7'
      }
    },
  },
  plugins: [],
}
