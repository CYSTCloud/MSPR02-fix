import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { Box, useDisclosure } from '@chakra-ui/react';

// Layouts
import MainLayout from './components/layouts/MainLayout';

// Pages
import Dashboard from './pages/Dashboard';
import HistoricalData from './pages/HistoricalData';
import Predictions from './pages/Predictions';
import CountryComparison from './pages/CountryComparison';

/**
 * Composant principal de l'application EPIVIZ 4.1
 * Gère le routage vers les différentes pages de l'application
 */
function App() {
  // État pour la barre latérale responsive
  const { isOpen, onOpen, onClose } = useDisclosure();

  return (
    <Box minH="100vh">
      <MainLayout isOpen={isOpen} onOpen={onOpen} onClose={onClose}>
        <Routes>
          {/* Page d'accueil - Tableau de bord principal */}
          <Route path="/" element={<Dashboard />} />
          
          {/* Données historiques */}
          <Route path="/historical/:countryId?" element={<HistoricalData />} />
          
          {/* Prédictions */}
          <Route path="/predictions/:countryId?" element={<Predictions />} />
          
          {/* Comparaison entre pays */}
          <Route path="/compare" element={<CountryComparison />} />
          
          {/* Page 404 - Non trouvé */}
          <Route path="*" element={
            <Box p={8} textAlign="center">
              <h1>404 - Page non trouvée</h1>
              <p>La page que vous recherchez n'existe pas.</p>
            </Box>
          } />
        </Routes>
      </MainLayout>
    </Box>
  );
}

export default App;
