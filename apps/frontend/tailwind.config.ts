import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ivory: "#FBF4EA",
        cream: "#F4E7D8",
        champagne: "#C9A46A",
        taupe: "#BBA08E",
        nude: "#D8C7A4",
        sage: "#82947A",
        rose: "#CFAE9E",
        espresso: "#251D18"
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
