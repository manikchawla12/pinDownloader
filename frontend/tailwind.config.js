/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./*.html",
    "./blog/**/*.html",
    "./admin/**/*.html",
    "./pages/**/*.html",
    "./assets/js/**/*.js",
  ],
  theme: {
    extend: {
      colors: {
        pinterest: '#E60023',
        pinterestHover: '#ad081b',
        dark: '#111111',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
      typography: (theme) => ({
        DEFAULT: {
          css: {
            color: theme('colors.gray.700'),
            maxWidth: 'none',
            a: {
              color: theme('colors.pinterest'),
              textDecoration: 'none',
              fontWeight: '500',
              '&:hover': { textDecoration: 'underline' },
            },
            'h1, h2, h3, h4': {
              color: theme('colors.dark'),
              fontWeight: '700',
            },
            strong: { color: theme('colors.dark') },
            code: {
              color: theme('colors.pinterest'),
              backgroundColor: theme('colors.gray.100'),
              padding: '0.15em 0.4em',
              borderRadius: '0.25rem',
              fontWeight: '500',
            },
            'code::before': { content: '""' },
            'code::after': { content: '""' },
          },
        },
      }),
    },
  },
  plugins: [require('@tailwindcss/typography')],
}
