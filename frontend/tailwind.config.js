/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'lenny-bg': '#0B0F19',
        'lenny-card': '#1E293B',
        'lenny-border': '#334155',
      },
    },
  },
  plugins: [],
}
