/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        base: {
          bg: "#0f172a",
          card: "#1e293b",
          border: "#293548",
          surface: "#0b1220",
        },
        brand: {
          DEFAULT: "#e31837",
          soft: "rgba(227, 24, 55, 0.15)",
        },
        segment: {
          lapsed: "#64748b",
          occasional: "#3b82f6",
          regular: "#f59e0b",
          loyalist: "#e31837",
        },
        clv: {
          bronze: "#a8714f",
          silver: "#9ca3af",
          gold: "#e3b341",
          platinum: "#7dd3fc",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "-apple-system", "sans-serif"],
        display: ["Space Grotesk", "Inter", "sans-serif"],
      },
      keyframes: {
        "fade-in": {
          from: { opacity: 0, transform: "translateY(4px)" },
          to: { opacity: 1, transform: "translateY(0)" },
        },
        "pulse-dot": {
          "0%, 80%, 100%": { opacity: 0.3 },
          "40%": { opacity: 1 },
        },
      },
      animation: {
        "fade-in": "fade-in 0.25s ease-out",
        "pulse-dot": "pulse-dot 1.4s infinite ease-in-out",
      },
    },
  },
  plugins: [],
};
