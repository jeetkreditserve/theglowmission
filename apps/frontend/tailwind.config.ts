import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ivory: "#FFF7F0",
        cream: "#F6EEE4",
        champagne: "#D9B88C",
        taupe: "#CDB8A9",
        nude: "#E6D6C6",
        espresso: "#2B2623"
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

