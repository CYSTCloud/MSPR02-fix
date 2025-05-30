import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Grid, 
  GridItem, 
  Heading, 
  Text, 
  Tab, 
  Tabs, 
  TabList, 
  TabPanel, 
  TabPanels,
  Select, 
  Flex, 
  Button, 
  Link,
  useColorModeValue, 
  Icon,
  Spinner,
  Alert,
  AlertIcon,
  Badge,
  Divider,
  useDisclosure,
  Collapse,
  SimpleGrid
} from '@chakra-ui/react';
import { 
  FiTrendingUp, 
  FiUsers, 
  FiAlertCircle, 
  FiMap, 
  FiBarChart2, 
  FiInfo,
  FiChevronDown,
  FiChevronUp,
  FiGlobe,
  FiCalendar
} from 'react-icons/fi';
import { Link as RouterLink } from 'react-router-dom';
import { useQuery } from 'react-query';
import { fetchCountries, fetchHistoricalData, fetchPredictions } from '../services/api';
import OverviewChart from '../components/charts/OverviewChart';
import WorldMap from '../components/charts/WorldMap';
import MetricCard from '../components/ui/MetricCard';
import RecentPredictionsTable from '../components/tables/RecentPredictionsTable';
import ExportableDataTable from '../components/tables/ExportableDataTable';
import GlobalStats from '../components/ui/GlobalStats';
import CountryComparisonChart from '../components/charts/CountryComparisonChart';

/**
 * Page Dashboard
 * Page d'accueil de l'application EPIVIZ 4.1 présentant une vue d'ensemble
 * des données de pandémie et des principales fonctionnalités
 */
const Dashboard = () => {
  const [selectedCountry, setSelectedCountry] = useState('US');
  
  // Définir tous les hooks au niveau supérieur du composant
  // pour respecter les règles des hooks React
  const cardBg = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const infoBgColor = useColorModeValue('blue.50', 'blue.900');
  const noteBgColor = useColorModeValue('gray.50', 'gray.700');
  const noteTextColor = useColorModeValue('gray.600', 'gray.300');
  const { isOpen, onToggle } = useDisclosure({ defaultIsOpen: false });
  
  // Récupération de la liste des pays
  const { 
    data: countriesData,
    isLoading: isLoadingCountries,
    error: countriesError
  } = useQuery('countries', fetchCountries);
  
  // Récupération des données historiques pour le pays sélectionné
  const { 
    data: historicalData,
    isLoading: isLoadingHistorical,
    error: historicalError,
    refetch: refetchHistorical
  } = useQuery(
    ['historical', selectedCountry], 
    () => fetchHistoricalData(selectedCountry),
    { enabled: !!selectedCountry }
  );
  
  // Récupération des prédictions pour le pays sélectionné
  const { 
    data: predictionsData,
    isLoading: isLoadingPredictions
  } = useQuery(
    ['predictions', selectedCountry, 7, 'xgboost'],
    () => fetchPredictions(selectedCountry, 7, 'xgboost'),
    { enabled: !!selectedCountry && countriesData?.countries_with_models?.includes(selectedCountry) }
  );
  
  // Met à jour les données historiques lorsque le pays sélectionné change
  useEffect(() => {
    if (selectedCountry) {
      refetchHistorical();
    }
  }, [selectedCountry, refetchHistorical]);
  
  // Calcul des métriques pour le pays sélectionné
  const calculateMetrics = () => {
    if (!historicalData || !historicalData.historical_data || historicalData.historical_data.length < 2) {
      return {
        totalCases: 0,
        newCases: 0,
        percentChange: 0,
        totalDeaths: 0
      };
    }
    
    const sortedData = [...historicalData.historical_data].sort((a, b) => 
      new Date(b.date) - new Date(a.date)
    );
    
    const latest = sortedData[0];
    const previous = sortedData[1];
    
    const percentChange = previous.new_cases !== 0 
      ? ((latest.new_cases - previous.new_cases) / previous.new_cases) * 100 
      : 0;
    
    return {
      totalCases: latest.total_cases,
      newCases: latest.new_cases,
      percentChange: percentChange.toFixed(2),
      totalDeaths: latest.total_deaths
    };
  };
  
  const metrics = historicalData ? calculateMetrics() : { totalCases: 0, newCases: 0, percentChange: 0, totalDeaths: 0 };
  
  // Gestion des erreurs de chargement
  if (countriesError || historicalError) {
    return (
      <Alert status="error" borderRadius="md">
        <AlertIcon />
        Une erreur s'est produite lors du chargement des données. 
        Veuillez réessayer ultérieurement.
      </Alert>
    );
  }
  
  // Les prédictions sont maintenant récupérées plus haut dans le composant
  
  // Colonnes pour le tableau de données exportable
  const dataColumns = [
    {
      Header: 'Date',
      accessor: 'date',
      Cell: (item) => new Date(item.date).toLocaleDateString()
    },
    {
      Header: 'Nouveaux Cas',
      accessor: 'new_cases',
      isNumeric: true,
      Cell: (item) => item.new_cases?.toLocaleString() || '0'
    },
    {
      Header: 'Cas Totaux',
      accessor: 'total_cases',
      isNumeric: true,
      Cell: (item) => item.total_cases?.toLocaleString() || '0'
    },
    {
      Header: 'Nouveaux Décès',
      accessor: 'new_deaths',
      isNumeric: true,
      Cell: (item) => item.new_deaths?.toLocaleString() || '0'
    },
    {
      Header: 'Décès Totaux',
      accessor: 'total_deaths',
      isNumeric: true,
      Cell: (item) => item.total_deaths?.toLocaleString() || '0'
    }
  ];
  
  return (
    <Box p={4}>
      <Heading as="h1" mb={2} fontSize={{ base: "2xl", md: "3xl" }}>
        Tableau de bord COVID-19
      </Heading>
      
      <Text mb={6} color="gray.600" _dark={{ color: "gray.300" }}>
        Visualisez et analysez les données de la pandémie COVID-19 en temps réel
      </Text>
      
      {/* Section d'informations sur l'application */}
      <Box 
        mb={6} 
        p={4} 
        bg={infoBgColor} 
        borderRadius="md"
        borderLeftWidth="4px"
        borderLeftColor="blue.500"
      >
        <Flex justify="space-between" align="center" onClick={onToggle} cursor="pointer">
          <Flex align="center">
            <Icon as={FiInfo} mr={2} color="blue.500" />
            <Heading size="sm">À propos de EPIVIZ 4.1</Heading>
          </Flex>
          <Icon as={isOpen ? FiChevronUp : FiChevronDown} />
        </Flex>
        
        <Collapse in={isOpen} animateOpacity>
          <Text mt={4}>
            EPIVIZ 4.1 est une plateforme de visualisation et de prédiction des cas de COVID-19 développée pour l'OMS. 
            Elle utilise des modèles d'apprentissage automatique pour prédire l'évolution de la pandémie et fournit des 
            outils avancés de visualisation des données historiques.
          </Text>
          <Flex mt={2} wrap="wrap" gap={2}>
            <Badge colorScheme="blue">Visualisation Interactive</Badge>
            <Badge colorScheme="green">Prédictions IA</Badge>
            <Badge colorScheme="purple">Analyse Comparative</Badge>
            <Badge colorScheme="orange">Données en Temps Réel</Badge>
          </Flex>
        </Collapse>
      </Box>
      
      {/* Statistiques globales */}
      <Box mb={8}>
        <Heading as="h2" size="md" mb={4}>
          <Flex align="center">
            <Icon as={FiGlobe} mr={2} />
            Statistiques Globales
          </Flex>
        </Heading>
        <GlobalStats />
      </Box>
      
      {/* Sélecteur de pays */}
      <Flex mb={6} align="center" wrap="wrap" gap={2}>
        <Text fontWeight="medium">Pays:</Text>
        {isLoadingCountries ? (
          <Spinner size="sm" ml={2} />
        ) : (
          <Select 
            value={selectedCountry} 
            onChange={(e) => setSelectedCountry(e.target.value)}
            maxW="300px"
            aria-label="Sélectionner un pays"
          >
            {countriesData?.countries?.map((country) => (
              <option key={country} value={country}>
                {country.replace('_', ' ')}
              </option>
            ))}
          </Select>
        )}
        <Button 
          colorScheme="blue"
          size="sm"
          onClick={() => refetchHistorical()}
          isLoading={isLoadingHistorical}
        >
          Actualiser
        </Button>
        
        {countriesData?.countries_with_models?.includes(selectedCountry) && (
          <Badge colorScheme="green" ml={2} p={1}>
            Modèles de prédiction disponibles
          </Badge>
        )}
      </Flex>
      
      {/* Contenu principal en onglets */}
      <Tabs variant="enclosed" colorScheme="blue" mb={8}>
        <TabList>
          <Tab><Icon as={FiBarChart2} mr={2} /> Aperçu</Tab>
          <Tab><Icon as={FiMap} mr={2} /> Carte</Tab>
          <Tab><Icon as={FiTrendingUp} mr={2} /> Prédictions</Tab>
          <Tab>Données</Tab>
        </TabList>
        
        <TabPanels>
          {/* Onglet Aperçu */}
          <TabPanel px={0}>
            {/* Cartes de métriques principales */}
            <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={6} mb={8}>
              <MetricCard
                title="Cas Totaux"
                value={metrics.totalCases.toLocaleString()}
                icon={FiUsers}
                color="blue.500"
              />
              <MetricCard
                title="Nouveaux Cas"
                value={metrics.newCases.toLocaleString()}
                icon={FiTrendingUp}
                change={metrics.percentChange}
                color="orange.500"
              />
              <MetricCard
                title="Décès Totaux"
                value={metrics.totalDeaths.toLocaleString()}
                icon={FiAlertCircle}
                color="red.500"
              />
              <MetricCard
                title="Pays avec Modèles"
                value={countriesData?.countries_with_models?.length || 0}
                subtitle={`sur ${countriesData?.countries?.length || 0} pays`}
                color="purple.500"
              />
            </SimpleGrid>
            
            {/* Graphique d'évolution */}
            <Box 
              p={5} 
              bg={cardBg} 
              borderRadius="lg" 
              boxShadow="md" 
              borderWidth="1px"
              borderColor={borderColor}
              height="400px"
              mb={6}
            >
              <Heading as="h3" size="md" mb={4}>
                Évolution des cas - {selectedCountry}
              </Heading>
              {isLoadingHistorical ? (
                <Flex justify="center" align="center" height="300px">
                  <Spinner size="xl" color="blue.500" />
                </Flex>
              ) : (
                <OverviewChart data={historicalData?.historical_data || []} />
              )}
            </Box>
            
            {/* Comparaison entre pays */}
            <Box 
              p={5} 
              bg={cardBg} 
              borderRadius="lg" 
              boxShadow="md" 
              borderWidth="1px"
              borderColor={borderColor}
            >
              <Flex justify="space-between" align="center" mb={4}>
                <Heading as="h3" size="md">
                  Comparaison des pays les plus touchés
                </Heading>
                <Link as={RouterLink} to="/compare" color="blue.500" fontSize="sm">
                  Voir l'analyse complète →
                </Link>
              </Flex>
              
              {isLoadingCountries ? (
                <Flex justify="center" align="center" height="200px">
                  <Spinner size="xl" color="blue.500" />
                </Flex>
              ) : (
                <CountryComparisonChart 
                  countries={countriesData?.countries?.slice(0, 5) || []} 
                />
              )}
            </Box>
          </TabPanel>
          
          {/* Onglet Carte */}
          <TabPanel px={0}>
            <Box 
              p={5} 
              bg={cardBg} 
              borderRadius="lg" 
              boxShadow="md" 
              borderWidth="1px"
              borderColor={borderColor}
              height="600px"
            >
              <Heading as="h3" size="md" mb={4}>
                Carte mondiale des cas COVID-19
              </Heading>
              <WorldMap selectedCountry={selectedCountry} />
            </Box>
          </TabPanel>
          
          {/* Onglet Prédictions */}
          <TabPanel px={0}>
            {countriesData?.countries_with_models?.includes(selectedCountry) ? (
              <Box>
                <Box 
                  p={5} 
                  bg={cardBg} 
                  borderRadius="lg" 
                  boxShadow="md" 
                  borderWidth="1px"
                  borderColor={borderColor}
                  mb={6}
                >
                  <Heading as="h3" size="md" mb={4}>
                    Prédictions pour {selectedCountry.replace('_', ' ')}
                  </Heading>
                  <RecentPredictionsTable country={selectedCountry} />
                </Box>
                
                <Flex justify="center" mt={4}>
                  <Button 
                    as={RouterLink} 
                    to={`/predictions/${selectedCountry}`}
                    colorScheme="blue"
                    leftIcon={<FiTrendingUp />}
                  >
                    Analyse complète des prédictions
                  </Button>
                </Flex>
              </Box>
            ) : (
              <Alert status="info" borderRadius="md">
                <AlertIcon />
                Les modèles de prédiction ne sont pas disponibles pour {selectedCountry.replace('_', ' ')}.
                Veuillez sélectionner un autre pays pour voir les prédictions.
              </Alert>
            )}
          </TabPanel>
          
          {/* Onglet Données */}
          <TabPanel px={0}>
            <Box 
              p={5} 
              bg={cardBg} 
              borderRadius="lg" 
              boxShadow="md" 
              borderWidth="1px"
              borderColor={borderColor}
            >
              <Heading as="h3" size="md" mb={4}>
                Données historiques - {selectedCountry.replace('_', ' ')}
              </Heading>
              
              {isLoadingHistorical ? (
                <Flex justify="center" align="center" height="200px">
                  <Spinner size="xl" color="blue.500" />
                </Flex>
              ) : (
                <ExportableDataTable 
                  data={historicalData?.historical_data || []} 
                  columns={dataColumns}
                  filename={`covid-data-${selectedCountry}`}
                />
              )}
            </Box>
          </TabPanel>
        </TabPanels>
      </Tabs>
        
      {/* Liens rapides vers d'autres sections */}
      <Box 
        p={5} 
        bg={cardBg} 
        borderRadius="lg" 
        boxShadow="md" 
        borderWidth="1px"
        borderColor={borderColor}
        mb={8}
      >
        <Heading as="h3" size="md" mb={4}>
          Explorer les fonctionnalités
        </Heading>
        <SimpleGrid columns={{ base: 1, md: 3 }} spacing={6}>
          <Box 
            p={4} 
            borderWidth="1px" 
            borderRadius="md" 
            borderColor={borderColor}
            _hover={{ boxShadow: "md", transform: "translateY(-2px)" }}
            transition="all 0.2s"
          >
            <Flex direction="column" align="center" textAlign="center">
              <Icon as={FiCalendar} boxSize={8} color="blue.500" mb={3} />
              <Heading size="sm" mb={2}>Données Historiques</Heading>
              <Text fontSize="sm" color="gray.600" _dark={{ color: "gray.300" }} mb={4}>
                Explorez les données historiques par pays avec des filtres avancés
              </Text>
              <Button 
                as={RouterLink} 
                to="/historical"
                colorScheme="blue" 
                size="sm"
                variant="outline"
              >
                Voir les données
              </Button>
            </Flex>
          </Box>
          
          <Box 
            p={4} 
            borderWidth="1px" 
            borderRadius="md" 
            borderColor={borderColor}
            _hover={{ boxShadow: "md", transform: "translateY(-2px)" }}
            transition="all 0.2s"
          >
            <Flex direction="column" align="center" textAlign="center">
              <Icon as={FiTrendingUp} boxSize={8} color="green.500" mb={3} />
              <Heading size="sm" mb={2}>Prédictions</Heading>
              <Text fontSize="sm" color="gray.600" _dark={{ color: "gray.300" }} mb={4}>
                Découvrez les prévisions générées par nos modèles d'IA
              </Text>
              <Button 
                as={RouterLink} 
                to="/predictions"
                colorScheme="green" 
                size="sm"
                variant="outline"
              >
                Voir les prédictions
              </Button>
            </Flex>
          </Box>
          
          <Box 
            p={4} 
            borderWidth="1px" 
            borderRadius="md" 
            borderColor={borderColor}
            _hover={{ boxShadow: "md", transform: "translateY(-2px)" }}
            transition="all 0.2s"
          >
            <Flex direction="column" align="center" textAlign="center">
              <Icon as={FiBarChart2} boxSize={8} color="purple.500" mb={3} />
              <Heading size="sm" mb={2}>Comparaison</Heading>
              <Text fontSize="sm" color="gray.600" _dark={{ color: "gray.300" }} mb={4}>
                Comparez les données entre différents pays
              </Text>
              <Button 
                as={RouterLink} 
                to="/compare"
                colorScheme="purple" 
                size="sm"
                variant="outline"
              >
                Comparer les pays
              </Button>
            </Flex>
          </Box>
        </SimpleGrid>
      </Box>
      
      {/* Note d'accessibilité */}
      <Box 
        p={4} 
        bg={noteBgColor} 
        borderRadius="md"
        fontSize="sm"
        color={noteTextColor}
      >
        <Heading as="h3" size="xs" mb={2}>
          Accessibilité et Ergonomie
        </Heading>
        <Text>
          EPIVIZ 4.1 est conçu pour être accessible à tous les utilisateurs, y compris ceux utilisant des technologies d'assistance. 
          L'interface est entièrement navigable au clavier et compatible avec les lecteurs d'écran. 
          Si vous rencontrez des problèmes d'accessibilité, n'hésitez pas à nous contacter.            
        </Text>
      </Box>
    </Box>
  );
};

export default Dashboard;
