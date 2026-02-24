import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        bg: "#080b10",
        surface: "#0d1117",
        surface2: "#141b24",
        accent: "#00e5a0",
        accent2: "#7c6fff",
        muted: "#5a6478",
        warn: "#ff6b6b",
        amber: "#f59e0b",
      },
      fontFamily: {
        sans: ["Syne", "system-ui", "sans-serif"],
        mono: ["DM Mono", "monospace"],
      },
    },
  },
  plugins: [],
};

export default config;
