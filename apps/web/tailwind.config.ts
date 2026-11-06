import type { Config } from "tailwindcss";

export default {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/features/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        ink: {
          950: "#0E1210",
          900: "#161C19",
          800: "#1F2924",
          700: "#2C3A32",
          500: "#5B6B61",
          300: "#A7B4AC",
          100: "#E6EBE7",
          50: "#F4F7F5",
        },
        accent: {
          DEFAULT: "#0F7A5F",
          soft: "#D8F0E7",
          strong: "#0A5A46",
        },
        evidence: {
          DEFAULT: "#C45C26",
          soft: "#F8E6DA",
        },
      },
      fontFamily: {
        sans: ["var(--font-sans)", "ui-sans-serif", "system-ui"],
        display: ["var(--font-display)", "ui-serif", "Georgia"],
        mono: ["var(--font-mono)", "ui-monospace", "monospace"],
      },
      boxShadow: {
        soft: "0 12px 40px rgba(14, 18, 16, 0.08)",
      },
      keyframes: {
        rise: {
          "0%": { opacity: "0", transform: "translateY(10px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        pulseSoft: {
          "0%, 100%": { opacity: "0.55" },
          "50%": { opacity: "1" },
        },
        trace: {
          "0%": { strokeDashoffset: "120" },
          "100%": { strokeDashoffset: "0" },
        },
      },
      animation: {
        rise: "rise 0.55s ease-out both",
        "pulse-soft": "pulseSoft 2.4s ease-in-out infinite",
        trace: "trace 1.4s ease-out both",
      },
    },
  },
  plugins: [],
} satisfies Config;
