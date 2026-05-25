import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      screens: {
        // xl을 1100px로 낮춰 일반 FHD(1920x1080)나 1366px 노트북에서도 풀 레이아웃 동작
        'xl': '1100px',
        '2xl': '1440px',
      },
      colors: {
        background: "var(--bg-color)",
        foreground: "var(--text-primary)",
      },
      fontFamily: {
        sans: ['Outfit', 'sans-serif'],
      },
    },
  },
  plugins: [],
};
export default config;

