/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./*.html", "./pages/**/*.html", "./assets/js/**/*.js"],
  theme: {
    extend: {
      colors: {
        pinterest: '#E60023',
        pinterestHover: '#ad081b',
        dark: '#111111',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
