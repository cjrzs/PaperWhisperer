/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        'heading': ['Nunito', 'system-ui', 'sans-serif'],
        'body': ['"Source Sans 3"', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [require("daisyui")],
  daisyui: {
    themes: [
      {
        light: {
          "primary": "#3B82F6",
          "primary-content": "#ffffff",
          "secondary": "#6366F1",
          "secondary-content": "#ffffff",
          "accent": "#0EA5E9",
          "accent-content": "#ffffff",
          "neutral": "#64748B",
          "neutral-content": "#ffffff",
          "base-100": "#ffffff",
          "base-200": "#F8FAFC",
          "base-300": "#E2E8F0",
          "base-content": "#1E293B",
          "info": "#3B82F6",
          "info-content": "#ffffff",
          "success": "#10B981",
          "success-content": "#ffffff",
          "warning": "#F59E0B",
          "warning-content": "#ffffff",
          "error": "#EF4444",
          "error-content": "#ffffff",
        },
      },
      {
        dark: {
          "primary": "#60A5FA",
          "primary-content": "#0F172A",
          "secondary": "#818CF8",
          "secondary-content": "#0F172A",
          "accent": "#38BDF8",
          "accent-content": "#0F172A",
          "neutral": "#475569",
          "neutral-content": "#F1F5F9",
          "base-100": "#0F172A",
          "base-200": "#1E293B",
          "base-300": "#334155",
          "base-content": "#F1F5F9",
          "info": "#60A5FA",
          "info-content": "#0F172A",
          "success": "#34D399",
          "success-content": "#0F172A",
          "warning": "#FBBF24",
          "warning-content": "#0F172A",
          "error": "#F87171",
          "error-content": "#0F172A",
        },
      },
    ],
  },
}
