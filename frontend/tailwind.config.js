/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        hazard: {
          red: "#ef4444",
          yellow: "#eab308",
          green: "#22c55e",
          critical: "#dc2626",
        },
        slate: {
          850: "#172033",
          950: "#0b0f19",
        }
      }
    },
  },
  plugins: [],
}
