import React, { useState, useEffect } from 'react';
import {
  Box,
  Heading,
  SimpleGrid,
  Text,
  Select,
  FormControl,
  FormLabel,
  HStack,
  Input,
  Button,
  Flex,
  useToast,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  Grid,
  GridItem,
  Divider,
  Alert,
  AlertIcon,
  VisuallyHidden
} from '@chakra-ui/react';
import { useQuery } from 'react-query';
import { fetchCountries, fetchHistoricalData } from '../services/api';
import OverviewChart from '../components/charts/OverviewChart';
import WorldMap from '../components/charts/WorldMap';

/**
 * Page de données historiques
 * Permet d'explorer les données historiques de COVID-19 par pays
 */
const HistoricalData = () => {
  const [selectedCountry, setSelectedCountry] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const toast = useToast();
  
  // Récupération de la liste des pays
  const { 
    data: countriesData, 
    isLoading: isLoadingCountries 
  } = useQuery('countries', fetchCountries);
  
  // Récupération des données historiques
  const { 
    data: historicalData,
    isLoading: isLoadingHistorical,
    error: historicalError,
    refetch: refetchHistorical
  } = useQuery(
    ['historical', selectedCountry, startDate, endDate],
    () => fetchHistoricalData(selectedCountry, startDate, endDate),
    {
      enabled: !!selectedCountry,
      refetchOnWindowFocus: false
    }
  );
  
  // Définir le pays par défaut une fois que les données sont chargées
  useEffect(() => {
    if (countriesData && countriesData.countries && countriesData.countries.length > 0 && !selectedCountry) {
      setSelectedCountry(countriesData.countries[0]);
    }
  }, [countriesData, selectedCountry]);
  
  // Fonction pour rechercher les données
  const handleSearch = () => {
    if (!selectedCountry) {
      toast({
        title: "Pays requis",
        description: "Veuillez sélectionner un pays pour voir les données historiques.",
        status: "warning",
        duration: 3000,
        isClosable: true,
      });
      return;
    }
    
    refetchHistorical();
  };
  
  // Fonction pour calculer les statistiques
  const calculateStats = (data) => {
    if (!data || data.length === 0) return {};
    
    // Calculer les valeurs maximales
    const maxCases = Math.max(...data.map(d => d.new_cases || 0));
    const maxDeaths = Math.max(...data.map(d => d.new_deaths || 0));
    
    // Trouver la date du pic de cas
    const peakCasesData = data.find(d => d.new_cases === maxCases);
    const peakCasesDate = peakCasesData ? new Date(peakCasesData.date).toLocaleDateString() : 'N/A';
    
    // Trouver la date du pic de décès
    const peakDeathsData = data.find(d => d.new_deaths === maxDeaths);
    const peakDeathsDate = peakDeathsData ? new Date(peakDeathsData.date).toLocaleDateString() : 'N/A';
    
    // Calculer les totaux
    const totalCases = data.reduce((sum, d) => sum + (d.new_cases || 0), 0);
    const totalDeaths = data.reduce((sum, d) => sum + (d.new_deaths || 0), 0);
    
    // Obtenir les dernières valeurs
    const latestData = [...data].sort((a, b) => new Date(b.date) - new Date(a.date))[0];
    
    return {
      maxCases,
      maxDeaths,
      peakCasesDate,
      peakDeathsDate,
      totalCases,
      totalDeaths,
      latestData
    };
  };
  
  const stats = historicalData ? calculateStats(historicalData.historical_data) : {};
  
  return (
    <Box p={4}>
      <Heading as="h1" size="xl" mb={6}>
        Données Historiques COVID-19
      </Heading>
      
      <Grid templateColumns={{ base: "1fr", md: "3fr 1fr" }} gap={6} mb={8}>
        {/* Carte du monde */}
        <GridItem h={{ base: "300px", md: "400px" }}>
          <Box 
            p={4} 
            bg="white" 
            borderRadius="lg" 
            boxShadow="md" 
            h="100%"
            _dark={{ bg: "gray.700" }}
          >
            <Heading as="h2" size="md" mb={4}>
              Carte Mondiale
            </Heading>
            <WorldMap selectedCountry={selectedCountry} />
          </Box>
        </GridItem>
        
        {/* Filtres de recherche */}
        <GridItem>
          <Box 
            p={4} 
            bg="white" 
            borderRadius="lg" 
            boxShadow="md"
            _dark={{ bg: "gray.700" }}
          >
            <Heading as="h2" size="md" mb={4}>
              Filtres
            </Heading>
            
            <FormControl mb={4}>
              <FormLabel htmlFor="country-select">Pays</FormLabel>
              <Select
                id="country-select"
                value={selectedCountry}
                onChange={(e) => setSelectedCountry(e.target.value)}
                placeholder="Sélectionner un pays"
                isDisabled={isLoadingCountries}
              >
                {countriesData?.countries?.map((country) => (
                  <option key={country} value={country}>
                    {country.replace('_', ' ')}
                  </option>
                ))}
              </Select>
            </FormControl>
            
            <FormControl mb={4}>
              <FormLabel htmlFor="start-date">Date de début</FormLabel>
              <Input
                id="start-date"
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
              />
            </FormControl>
            
            <FormControl mb={4}>
              <FormLabel htmlFor="end-date">Date de fin</FormLabel>
              <Input
                id="end-date"
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
              />
            </FormControl>
            
            <Button 
              colorScheme="blue" 
              width="full" 
              onClick={handleSearch}
              isLoading={isLoadingHistorical}
            >
              Rechercher
            </Button>
          </Box>
        </GridItem>
      </Grid>
      
      {/* Affichage d'erreurs */}
      {historicalError && (
        <Alert status="error" mb={6} borderRadius="md">
          <AlertIcon />
          Une erreur s'est produite lors du chargement des données historiques.
          Veuillez réessayer ultérieurement.
        </Alert>
      )}
      
      {/* Statistiques clés */}
      {historicalData && historicalData.historical_data && (
        <>
          <VisuallyHidden>
            Statistiques COVID-19 pour {selectedCountry.replace('_', ' ')}
          </VisuallyHidden>
          
          <SimpleGrid columns={{ base: 2, md: 4 }} spacing={6} mb={8}>
            <Box p={4} bg="white" borderRadius="lg" boxShadow="md" _dark={{ bg: "gray.700" }}>
              <Stat>
                <StatLabel>Cas Totaux</StatLabel>
                <StatNumber>{stats.latestData?.total_cases.toLocaleString() || 'N/A'}</StatNumber>
                <StatHelpText>
                  Données les plus récentes
                </StatHelpText>
              </Stat>
            </Box>
            
            <Box p={4} bg="white" borderRadius="lg" boxShadow="md" _dark={{ bg: "gray.700" }}>
              <Stat>
                <StatLabel>Décès Totaux</StatLabel>
                <StatNumber>{stats.latestData?.total_deaths.toLocaleString() || 'N/A'}</StatNumber>
                <StatHelpText>
                  Données les plus récentes
                </StatHelpText>
              </Stat>
            </Box>
            
            <Box p={4} bg="white" borderRadius="lg" boxShadow="md" _dark={{ bg: "gray.700" }}>
              <Stat>
                <StatLabel>Pic de Nouveaux Cas</StatLabel>
                <StatNumber>{stats.maxCases?.toLocaleString() || 'N/A'}</StatNumber>
                <StatHelpText>
                  {stats.peakCasesDate}
                </StatHelpText>
              </Stat>
            </Box>
            
            <Box p={4} bg="white" borderRadius="lg" boxShadow="md" _dark={{ bg: "gray.700" }}>
              <Stat>
                <StatLabel>Pic de Nouveaux Décès</StatLabel>
                <StatNumber>{stats.maxDeaths?.toLocaleString() || 'N/A'}</StatNumber>
                <StatHelpText>
                  {stats.peakDeathsDate}
                </StatHelpText>
              </Stat>
            </Box>
          </SimpleGrid>
          
          {/* Graphique d'évolution */}
          <Box 
            p={4} 
            bg="white" 
            borderRadius="lg" 
            boxShadow="md" 
            mb={8} 
            h="500px"
            _dark={{ bg: "gray.700" }}
          >
            <Heading as="h2" size="md" mb={4}>
              Évolution des Données pour {selectedCountry.replace('_', ' ')}
            </Heading>
            <OverviewChart data={historicalData.historical_data} />
          </Box>
        </>
      )}
    </Box>
  );
};

export default HistoricalData;
