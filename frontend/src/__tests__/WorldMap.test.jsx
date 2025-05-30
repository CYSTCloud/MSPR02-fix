import React from 'react';
import { render, screen } from '@testing-library/react';
import { ChakraProvider } from '@chakra-ui/react';
import { QueryClient, QueryClientProvider } from 'react-query';
import WorldMap from '../components/charts/WorldMap';

// Mock de la bibliothèque react-simple-maps car elle utilise des fonctionnalités non disponibles dans l'environnement de test
jest.mock('react-simple-maps', () => ({
  ComposableMap: ({ children, ...props }) => <div data-testid="composable-map" {...props}>{children}</div>,
  Geographies: ({ children, ...props }) => <div data-testid="geographies" {...props}>{children}</div>,
  Geography: ({ geography, ...props }) => (
    <div 
      data-testid={`geography-${geography?.properties?.NAME || 'unknown'}`} 
      data-name={geography?.properties?.NAME}
      {...props} 
    />
  ),
  ZoomableGroup: ({ children, ...props }) => <div data-testid="zoomable-group" {...props}>{children}</div>,
}));

// Mock du service API
jest.mock('../services/api', () => ({
  fetchCountries: jest.fn(() => Promise.resolve({
    countries: ['US', 'Brazil', 'France', 'Germany', 'Italy'],
    countries_with_models: ['US', 'Brazil', 'France']
  }))
}));

// Enveloppe les composants de test avec le ThemeProvider de Chakra UI et QueryClientProvider
const renderWithProviders = (ui) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });
  
  return render(
    <QueryClientProvider client={queryClient}>
      <ChakraProvider>{ui}</ChakraProvider>
    </QueryClientProvider>
  );
};

describe('WorldMap Component', () => {
  test('renders map container', async () => {
    renderWithProviders(<WorldMap selectedCountry="US" />);
    
    // Vérifier que le conteneur de carte est rendu
    expect(await screen.findByTestId('composable-map')).toBeInTheDocument();
    expect(await screen.findByTestId('zoomable-group')).toBeInTheDocument();
  });
  
  test('has proper accessibility attributes', async () => {
    renderWithProviders(<WorldMap selectedCountry="US" />);
    
    // Vérifier que les attributs d'accessibilité sont présents
    const mapDesc = await screen.findByText(/carte mondiale/i);
    expect(mapDesc).toBeInTheDocument();
  });
  
  test('renders zoom controls', async () => {
    renderWithProviders(<WorldMap selectedCountry="US" />);
    
    // Vérifier que les contrôles de zoom sont présents
    expect(await screen.findByRole('button', { name: /zoomer/i })).toBeInTheDocument();
    expect(await screen.findByRole('button', { name: /dézoomer/i })).toBeInTheDocument();
    expect(await screen.findByRole('button', { name: /réinitialiser/i })).toBeInTheDocument();
  });
  
  test('renders legend', async () => {
    renderWithProviders(<WorldMap selectedCountry="US" />);
    
    // Attendre que la carte soit chargée
    await screen.findByTestId('composable-map');
    
    // Vérifier que la légende est présente
    expect(await screen.findByText(/pays sélectionné/i)).toBeInTheDocument();
    expect(await screen.findByText(/pays avec modèles/i)).toBeInTheDocument();
  });
});
