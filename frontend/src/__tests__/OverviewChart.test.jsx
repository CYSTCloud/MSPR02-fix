import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { ChakraProvider } from '@chakra-ui/react';
import OverviewChart from '../components/charts/OverviewChart';

// Enveloppe les composants de test avec le ThemeProvider de Chakra UI
const renderWithChakra = (ui) => {
  return render(
    <ChakraProvider>{ui}</ChakraProvider>
  );
};

// Mock des données pour les tests
const mockData = [
  { date: '2023-01-01', new_cases: 1234, total_cases: 50000, new_deaths: 45, total_deaths: 1500 },
  { date: '2023-01-02', new_cases: 1345, total_cases: 51345, new_deaths: 48, total_deaths: 1548 },
  { date: '2023-01-03', new_cases: 1456, total_cases: 52801, new_deaths: 51, total_deaths: 1599 },
  { date: '2023-01-04', new_cases: 1567, total_cases: 54368, new_deaths: 54, total_deaths: 1653 },
  { date: '2023-01-05', new_cases: 1678, total_cases: 56046, new_deaths: 57, total_deaths: 1710 },
];

// Mock de la bibliothèque Recharts car elle utilise des fonctionnalités non disponibles dans l'environnement de test
jest.mock('recharts', () => {
  const OriginalModule = jest.requireActual('recharts');
  return {
    ...OriginalModule,
    ResponsiveContainer: ({ children }) => <div data-testid="responsive-container">{children}</div>,
    LineChart: ({ children }) => <div data-testid="line-chart">{children}</div>,
    Line: ({ dataKey, name }) => <div data-testid={`line-${dataKey}`} data-name={name}></div>,
    XAxis: () => <div data-testid="x-axis"></div>,
    YAxis: () => <div data-testid="y-axis"></div>,
    CartesianGrid: () => <div data-testid="cartesian-grid"></div>,
    Tooltip: () => <div data-testid="tooltip"></div>,
    Legend: () => <div data-testid="legend"></div>,
    Brush: () => <div data-testid="brush"></div>,
  };
});

describe('OverviewChart Component', () => {
  test('renders chart container', () => {
    renderWithChakra(<OverviewChart data={mockData} />);
    
    // Vérifier que le conteneur réactif est rendu
    expect(screen.getByTestId('responsive-container')).toBeInTheDocument();
    expect(screen.getByTestId('line-chart')).toBeInTheDocument();
  });
  
  test('renders chart elements', () => {
    renderWithChakra(<OverviewChart data={mockData} />);
    
    // Vérifier que les éléments du graphique sont rendus
    expect(screen.getByTestId('x-axis')).toBeInTheDocument();
    expect(screen.getByTestId('y-axis')).toBeInTheDocument();
    expect(screen.getByTestId('cartesian-grid')).toBeInTheDocument();
    expect(screen.getByTestId('tooltip')).toBeInTheDocument();
    expect(screen.getByTestId('legend')).toBeInTheDocument();
  });
  
  test('renders with default metric of new_cases', () => {
    renderWithChakra(<OverviewChart data={mockData} />);
    
    // Vérifier que la ligne pour new_cases est rendue par défaut
    expect(screen.getByTestId('line-new_cases')).toBeInTheDocument();
  });
  
  test('allows changing metrics', () => {
    renderWithChakra(<OverviewChart data={mockData} />);
    
    // Trouver les boutons de métriques
    const totalCasesButton = screen.getByRole('button', { name: /cas totaux/i });
    
    // Cliquer sur le bouton pour changer de métrique
    fireEvent.click(totalCasesButton);
    
    // Vérifier que le bouton est maintenant actif (a la propriété aria-pressed à true)
    expect(totalCasesButton).toHaveAttribute('aria-pressed', 'true');
  });
  
  test('allows changing time range', () => {
    renderWithChakra(<OverviewChart data={mockData} />);
    
    // Trouver les boutons de plage de temps
    const thirtyDaysButton = screen.getByRole('button', { name: /30 jours/i });
    
    // Cliquer sur le bouton pour changer la plage de temps
    fireEvent.click(thirtyDaysButton);
    
    // Vérifier que le bouton est maintenant actif
    expect(thirtyDaysButton).toHaveAttribute('aria-pressed', 'true');
  });
  
  test('has proper accessibility attributes', () => {
    renderWithChakra(<OverviewChart data={mockData} />);
    
    // Vérifier que les étiquettes d'accessibilité sont présentes
    const accessibilityLabel = screen.getByText(/graphique d'évolution des nouveaux cas au fil du temps/i);
    expect(accessibilityLabel).toBeInTheDocument();
  });
});
