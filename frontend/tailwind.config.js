/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'Avenir', 'Helvetica', 'Arial', 'sans-serif'],
      },
      colors: {
        primary: '#FF6B35',
        secondary: '#004E89',
        success: '#28A745',
        warning: '#FFC107',
        error: '#DC3545',
        background: '#F8F9FA',
        surface: '#FFFFFF',
        text: '#212529',
      },
      screens: {
        mobile: '320px',
        tablet: '768px',
        desktop: '1024px',
      },
    },
  },
  plugins: [],
}

