import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        background: "#f6fbf9",
        surface: "#f6fbf9",
        "surface-bright": "#f8fffc",
        "surface-container-lowest": "#ffffff",
        "surface-container-low": "#eef8f5",
        "surface-container": "#e5f3ef",
        "surface-container-high": "#d9ede8",
        "surface-container-highest": "#cbe4de",
        "on-surface": "#13221e",
        "on-surface-variant": "#40534d",
        primary: "#1DA37D",
        "primary-container": "#147D76",
        "primary-fixed": "#d8f4ee",
        "primary-fixed-dim": "#8AD4C6",
        "on-primary": "#ffffff",
        "on-primary-fixed": "#052c24",
        "on-primary-fixed-variant": "#0D5C4C",
        secondary: "#147D76",
        "secondary-container": "#8AD4C6",
        "secondary-fixed": "#d6f3ed",
        "on-secondary-container": "#063f3b",
        tertiary: "#0D4666",
        "tertiary-container": "#b9dff0",
        "tertiary-fixed": "#e2f3fb",
        "on-tertiary-container": "#062f45",
        outline: "#6c817a",
        "outline-variant": "#bdd4cd",
        error: "#ba1a1a",
        "error-container": "#ffdad6",
      },
      fontFamily: {
        body: ["Hanken Grotesk", "ui-sans-serif", "system-ui", "sans-serif"],
        display: ["Bricolage Grotesque", "ui-sans-serif", "system-ui", "sans-serif"],
      },
      boxShadow: {
        glass: "0 30px 60px rgba(29, 163, 125, 0.08)",
        soft: "0 18px 40px rgba(25, 28, 30, 0.08)",
      },
      maxWidth: {
        container: "1280px",
      },
      keyframes: {
        float: {
          "0%, 100%": { transform: "translateY(0) rotate(0deg)" },
          "50%": { transform: "translateY(-16px) rotate(4deg)" },
        },
      },
      animation: {
        float: "float 7s ease-in-out infinite",
      },
    },
  },
  plugins: [],
} satisfies Config;
