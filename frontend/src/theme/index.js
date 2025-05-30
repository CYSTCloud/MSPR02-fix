import { extendTheme } from '@chakra-ui/react';

// Couleurs personnalisées pour EPIVIZ 4.1
const colors = {
  brand: {
    50: '#e6f6ff',
    100: '#b3e0ff',
    200: '#80cbff',
    300: '#4db6ff',
    400: '#1aa1ff',
    500: '#0084e6',
    600: '#0068b4',
    700: '#004c82',
    800: '#003050',
    900: '#00141f',
  },
  // Palette pour les visualisations de données
  dataViz: {
    confirmed: '#3182ce', // Bleu pour les cas confirmés
    deaths: '#e53e3e',    // Rouge pour les décès
    recovered: '#38a169', // Vert pour les guérisons
    predicted: '#805ad5',  // Violet pour les prédictions
    // Palette supplémentaire pour les comparaisons multi-pays
    country1: '#3182ce',   // Bleu
    country2: '#dd6b20',   // Orange
    country3: '#38a169',   // Vert
    country4: '#805ad5',   // Violet
    country5: '#d53f8c',   // Rose
    country6: '#718096',   // Gris
    country7: '#f6ad55',   // Orange clair
    country8: '#9ae6b4',   // Vert clair
  },
};

// Configuration des composants globaux
const components = {
  Button: {
    baseStyle: {
      fontWeight: 'semibold',
      borderRadius: 'md',
    },
    variants: {
      solid: (props) => ({
        bg: props.colorMode === 'dark' ? 'brand.600' : 'brand.500',
        color: 'white',
        _hover: {
          bg: props.colorMode === 'dark' ? 'brand.500' : 'brand.600',
        },
      }),
      outline: (props) => ({
        borderColor: props.colorMode === 'dark' ? 'brand.600' : 'brand.500',
        color: props.colorMode === 'dark' ? 'brand.600' : 'brand.500',
        _hover: {
          bg: props.colorMode === 'dark' ? 'rgba(0, 132, 230, 0.1)' : 'rgba(0, 132, 230, 0.1)',
        },
      }),
    },
  },
  Heading: {
    baseStyle: {
      fontWeight: 'bold',
      color: 'gray.800',
      _dark: {
        color: 'gray.100',
      },
    },
  },
  Card: {
    baseStyle: {
      p: 4,
      borderRadius: 'lg',
      boxShadow: 'md',
      bg: 'white',
      _dark: {
        bg: 'gray.700',
      },
    },
  },
};

// Configuration d'accessibilité
const accessibility = {
  radii: {
    sm: '0.125rem',
    md: '0.25rem',
    lg: '0.5rem',
    xl: '0.75rem',
  },
  fontSizes: {
    xs: '0.75rem',
    sm: '0.875rem',
    md: '1rem',
    lg: '1.125rem',
    xl: '1.25rem',
    '2xl': '1.5rem',
    '3xl': '1.875rem',
    '4xl': '2.25rem',
    '5xl': '3rem',
  },
  space: {
    xs: '0.25rem',
    sm: '0.5rem',
    md: '1rem',
    lg: '1.5rem',
    xl: '2rem',
  },
};

// Configuration globale du thème
const config = {
  initialColorMode: 'light',
  useSystemColorMode: true,
};

// Extension du thème de base de Chakra UI
const theme = extendTheme({
  colors,
  components,
  ...accessibility,
  config,
  styles: {
    global: (props) => ({
      body: {
        bg: props.colorMode === 'dark' ? 'gray.800' : 'gray.50',
        color: props.colorMode === 'dark' ? 'white' : 'gray.800',
      },
      // Amélioration de l'accessibilité pour les éléments de focus
      '*:focus': {
        boxShadow: `0 0 0 3px ${props.colorMode === 'dark' ? 'rgba(66, 153, 225, 0.6)' : 'rgba(66, 153, 225, 0.6)'}`,
        outline: 'none',
      },
    }),
  },
});

export default theme;
