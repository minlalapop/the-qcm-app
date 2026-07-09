import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        background: "#f7f9fb",
        surface: "#f7f9fb",
        "surface-bright": "#f7f9fb",
        "surface-container-lowest": "#ffffff",
        "surface-container-low": "#f2f4f6",
        "surface-container": "#eceef0",
        "surface-container-high": "#e6e8ea",
        "surface-container-highest": "#e0e3e5",
        "on-surface": "#191c1e",
        "on-surface-variant": "#4d4354",
        primary: "#862dbe",
        "primary-container": "#a14bd9",
        "primary-fixed": "#f4daff",
        "primary-fixed-dim": "#e4b5ff",
        "on-primary": "#ffffff",
        "on-primary-fixed": "#2f004c",
        "on-primary-fixed-variant": "#6e06a7",
        secondary: "#0061a4",
        "secondary-container": "#72b5fe",
        "secondary-fixed": "#d1e4ff",
        "on-secondary-container": "#004677",
        tertiary: "#8d7b3d",
        "tertiary-container": "#fdf4d7",
        "tertiary-fixed": "#fff8e1",
        "on-tertiary-container": "#524400",
        outline: "#7e7385",
        "outline-variant": "#cfc2d6",
        error: "#ba1a1a",
        "error-container": "#ffdad6",
      },
      fontFamily: {
        body: ["Hanken Grotesk", "ui-sans-serif", "system-ui", "sans-serif"],
        display: ["Bricolage Grotesque", "ui-sans-serif", "system-ui", "sans-serif"],
      },
      boxShadow: {
        glass: "0 30px 60px rgba(134, 45, 190, 0.06)",
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
