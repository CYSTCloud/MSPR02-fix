import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { ChakraProvider } from '@chakra-ui/react';
import ExportableDataTable from '../components/tables/ExportableDataTable';

// Enveloppe les composants de test avec le ThemeProvider de Chakra UI
const renderWithChakra = (ui) => {
  return render(
    <ChakraProvider>{ui}</ChakraProvider>
  );
};

// Mock de données pour les tests
const mockData = [
  { date: '2023-01-01', new_cases: 1234, total_cases: 50000, new_deaths: 45, total_deaths: 1500 },
  { date: '2023-01-02', new_cases: 1345, total_cases: 51345, new_deaths: 48, total_deaths: 1548 },
  { date: '2023-01-03', new_cases: 1456, total_cases: 52801, new_deaths: 51, total_deaths: 1599 },
];

// Configuration des colonnes
const mockColumns = [
  {
    Header: 'Date',
    accessor: 'date',
    Cell: (item) => new Date(item.date).toLocaleDateString()
  },
  {
    Header: 'Nouveaux Cas',
    accessor: 'new_cases',
    isNumeric: true,
  },
  {
    Header: 'Cas Totaux',
    accessor: 'total_cases',
    isNumeric: true,
  },
  {
    Header: 'Nouveaux Décès',
    accessor: 'new_deaths',
    isNumeric: true,
  },
  {
    Header: 'Décès Totaux',
    accessor: 'total_deaths',
    isNumeric: true,
  }
];

// Mock de la fonction URL.createObjectURL pour les tests d'exportation
global.URL.createObjectURL = jest.fn(() => 'mocked-url');

describe('ExportableDataTable Component', () => {
  beforeEach(() => {
    // Réinitialiser les mocks avant chaque test
    jest.clearAllMocks();
  });
  
  test('renders table headers correctly', () => {
    renderWithChakra(<ExportableDataTable 
      data={mockData}
      columns={mockColumns}
      filename="test-export"
    />);
    
    // Vérifier que les en-têtes sont présents
    expect(screen.getByText('Date')).toBeInTheDocument();
    expect(screen.getByText('Nouveaux Cas')).toBeInTheDocument();
    expect(screen.getByText('Cas Totaux')).toBeInTheDocument();
    expect(screen.getByText('Nouveaux Décès')).toBeInTheDocument();
    expect(screen.getByText('Décès Totaux')).toBeInTheDocument();
  });
  
  test('renders data rows correctly', () => {
    renderWithChakra(<ExportableDataTable 
      data={mockData}
      columns={mockColumns}
      filename="test-export"
    />);
    
    // Vérifier que les données sont présentes
    // Note: toLocaleDateString peut rendre des formats différents selon l'environnement
    // donc nous vérifions juste les valeurs numériques
    expect(screen.getByText('1234')).toBeInTheDocument();
    expect(screen.getByText('50000')).toBeInTheDocument();
    expect(screen.getByText('1345')).toBeInTheDocument();
    expect(screen.getByText('51345')).toBeInTheDocument();
  });
  
  test('has export button', () => {
    renderWithChakra(<ExportableDataTable 
      data={mockData}
      columns={mockColumns}
      filename="test-export"
    />);
    
    // Vérifier que le bouton d'exportation est présent
    const exportButton = screen.getByRole('button', { name: /exporter/i });
    expect(exportButton).toBeInTheDocument();
  });
  
  test('allows changing page size', () => {
    renderWithChakra(<ExportableDataTable 
      data={mockData}
      columns={mockColumns}
      filename="test-export"
    />);
    
    // Vérifier que le sélecteur de taille de page est présent
    const pageSizeSelect = screen.getByRole('combobox', { name: /lignes par page/i });
    expect(pageSizeSelect).toBeInTheDocument();
    
    // Simuler un changement de taille de page
    fireEvent.change(pageSizeSelect, { target: { value: '5' } });
    
    // Vérifier que la taille de page a changé
    expect(pageSizeSelect.value).toBe('5');
  });
  
  test('allows searching data', () => {
    renderWithChakra(<ExportableDataTable 
      data={mockData}
      columns={mockColumns}
      filename="test-export"
    />);
    
    // Vérifier que le champ de recherche est présent
    const searchInput = screen.getByPlaceholderText(/rechercher/i);
    expect(searchInput).toBeInTheDocument();
    
    // Simuler une recherche
    fireEvent.change(searchInput, { target: { value: '1345' } });
    
    // Après la recherche, seule la ligne avec 1345 devrait être visible
    expect(screen.getByText('1345')).toBeInTheDocument();
    expect(screen.queryByText('1234')).not.toBeInTheDocument();
  });
});
