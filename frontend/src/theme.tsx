import { createSystem, defaultConfig } from "@chakra-ui/react";
import { buttonRecipe } from "./theme/button.recipe";

export const system = createSystem(defaultConfig, {
  globalCss: {
    html: {
      fontSize: "16px",
    },
    body: {
      fontSize: "0.875rem",
      margin: 0,
      padding: 0,
      backgroundColor: { base: "bg.dark", _light: "bg.light" },
      color: { base: "text.dark", _light: "text.light" },
      fontFamily: "'Inter', sans-serif",
    },
    ".main-link": {
      color: "ui.main",
      fontWeight: "bold",
      _hover: {
        textDecoration: "underline",
        opacity: 0.9,
      },
    },
  },

  theme: {
    tokens: {
      colors: {
        primary: {
          50: { value: "#E0FCFF" },
          100: { value: "#B3F8FF" },
          200: { value: "#80F1FF" },
          300: { value: "#4DEAFF" },
          400: { value: "#1AE3FF" },
          500: { value: "#06B6D4" }, // Base Primary
          600: { value: "#0592A8" },
          700: { value: "#046E7C" },
          800: { value: "#034B50" },
          900: { value: "#01272A" },
        },
        accent: {
          50: { value: "#FFF8E6" },
          100: { value: "#FFE7B8" },
          200: { value: "#FFD58A" },
          300: { value: "#FFC35C" },
          400: { value: "#FFB12E" },
          500: { value: "#FFB020" }, // Base Accent
          600: { value: "#CC8C19" },
          700: { value: "#996913" },
          800: { value: "#66460C" },
          900: { value: "#332306" },
        },
        bg: {
          light: { value: "#F9FAFB" },
          dark: { value: "#0F1724" },
        },
        card: {
          light: { value: "#FFFFFF" },
          dark: { value: "#1A202C" },
        },
        text: {
          light: { value: "#1A202C" },
          dark: { value: "#E6EEF6" },
          mutedLight: { value: "#4A5568" },
          mutedDark: { value: "#94A3B8" },
        },
        ui: {
          main: { value: "#009688" },
        },
      },

      fonts: {
        heading: { value: "'Poppins', sans-serif" },
        body: { value: "'Inter', sans-serif" },
      },

      radii: {
        xl: { value: "1rem" },
        "2xl": { value: "1.5rem" },
      },

      shadows: {
        soft: { value: "0 2px 8px rgba(0, 0, 0, 0.1)" },
      },
    },

    recipes: {
      button: buttonRecipe,
    },

    semanticTokens: {
      colors: {
        "chakra-body-text": {
          value: { base: "text.dark", _light: "text.light" },
        },
        "chakra-body-bg": {
          value: { base: "bg.dark", _light: "bg.light" },
        },
        "chakra-card-bg": {
          value: { base: "card.dark", _light: "card.light" },
        },
        "chakra-accent-color": {
          value: { base: "accent.500", _light: "accent.400" },
        },
      },
    },
  },
});
