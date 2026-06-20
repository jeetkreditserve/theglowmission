import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ivory: "rgb(var(--color-ivory-rgb) / <alpha-value>)",
        cream: "rgb(var(--color-cream-rgb) / <alpha-value>)",
        champagne: "rgb(var(--color-champagne-rgb) / <alpha-value>)",
        taupe: "rgb(var(--color-taupe-rgb) / <alpha-value>)",
        nude: "rgb(var(--color-nude-rgb) / <alpha-value>)",
        sage: "rgb(var(--color-sage-rgb) / <alpha-value>)",
        rose: "rgb(var(--color-rose-rgb) / <alpha-value>)",
        espresso: "rgb(var(--color-espresso-rgb) / <alpha-value>)"
      },
      fontFamily: {
        display: ["var(--font-display)", "Cinzel", "Georgia", "serif"],
        body: ["var(--font-body)", "Montserrat", "Lato", "Arial", "sans-serif"]
      },
      boxShadow: {
        soft: "0 24px 80px rgba(43, 38, 35, 0.12)"
      }
    }
  },
  plugins: []
};

export default config;
