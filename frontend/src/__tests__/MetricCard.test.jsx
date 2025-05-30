import React from 'react';
import { render, screen } from '@testing-library/react';
import { ChakraProvider } from '@chakra-ui/react';
import { FiUsers } from 'react-icons/fi';
import MetricCard from '../components/ui/MetricCard';

// Enveloppe les composants de test avec le ThemeProvider de Chakra UI
const renderWithChakra = (ui) => {
  return render(
    <ChakraProvider>{ui}</ChakraProvider>
  );
};

describe('MetricCard Component', () => {
  test('renders the title and value correctly', () => {
    renderWithChakra(<MetricCard 
      title="Total Cases" 
      value="1,234,567" 
      icon={FiUsers}
      color="blue.500"
    />);
    
    // Vérifier que le titre est présent
    expect(screen.getByText('Total Cases')).toBeInTheDocument();
    
    // Vérifier que la valeur est présente
    expect(screen.getByText('1,234,567')).toBeInTheDocument();
  });
  
  test('renders with change indicator when change prop is provided', () => {
    renderWithChakra(<MetricCard 
      title="New Cases" 
      value="12,345" 
      change={5.2}
      icon={FiUsers}
      color="orange.500"
    />);
    
    // Vérifier que le titre est présent
    expect(screen.getByText('New Cases')).toBeInTheDocument();
    
    // Vérifier que la valeur est présente
    expect(screen.getByText('12,345')).toBeInTheDocument();
    
    // Vérifier que le pourcentage de changement est présent
    expect(screen.getByText('5.2%')).toBeInTheDocument();
  });
  
  test('renders with subtitle when provided', () => {
    const subtitle = 'Last 24 hours';
    renderWithChakra(<MetricCard 
      title="Deaths" 
      value="5,432" 
      subtitle={subtitle}
      icon={FiUsers}
      color="red.500"
    />);
    
    // Vérifier que le sous-titre est présent
    expect(screen.getByText(subtitle)).toBeInTheDocument();
  });
  
  test('has proper ARIA attributes for accessibility', () => {
    renderWithChakra(<MetricCard 
      title="Total Cases" 
      value="1,234,567" 
      icon={FiUsers}
      color="blue.500"
    />);
    
    // Vérifier que le composant a un rôle et un aria-label appropriés
    const metricCard = screen.getByRole('group');
    expect(metricCard).toHaveAttribute('aria-label', 'Métrique: Total Cases');
  });
});
