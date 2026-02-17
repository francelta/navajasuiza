/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'ns-dark': '#0f172a',
        'ns-darker': '#0a0f1e',
        'ns-card': '#1e293b',
        'ns-card-hover': '#334155',
        'ns-accent': '#6366f1',
        'ns-accent-light': '#818cf8',
        'ns-success': '#10b981',
        'ns-warning': '#f59e0b',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
