import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
    "./App.tsx",
    "./theme.config.tsx",
  ],
  // Enable JIT mode for better performance
  mode: 'jit',
  // Purge unused styles in production
  purge: {
    enabled: process.env.NODE_ENV === 'production',
    content: [
      "./src/**/*.{js,ts,jsx,tsx,mdx}",
      "./App.tsx",
      "./theme.config.tsx",
    ],
    // Safelist important classes that might be used dynamically
    safelist: [
      'bg-blue-600',
      'bg-purple-600', 
      'bg-green-600',
      'bg-orange-600',
      'text-blue-600',
      'text-purple-600',
      'text-green-600',
      'text-orange-600',
      'border-blue-600',
      'border-purple-600',
      'border-green-600',
      'border-orange-600',
      'animate-pulse',
      'animate-bounce',
      'animate-spin',
    ]
  },
  theme: {
    extend: {
      colors: {
        primary: "#932F58",
        "primary-600": "#ae5475",
        grey: "#818898",
        redColor: "#D52B0C",
      },
      backgroundImage: {
        "gradient-radial": "radial-gradient(var(--tw-gradient-stops))",
        "gradient-conic":
          "conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))",
      },
    },
  },
  plugins: [require("@tailwindcss/forms")],
};

export default config;
