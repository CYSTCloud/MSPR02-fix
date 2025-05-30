import React from 'react';
import {
  Box,
  SimpleGrid,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  StatArrow,
  Flex,
  Text,
  Divider,
  Spinner,
  useColorModeValue,
  VisuallyHidden
} from '@chakra-ui/react';
import { useQuery } from 'react-query';
import { fetchHistoricalData } from '../../services/api';

/**
 * Composant GlobalStats
 * Affiche les statistiques globales mondiales de COVID-19
 * 
 * @returns {JSX.Element} Grille de statistiques globales
 */
const GlobalStats = () => {
  // Récupération des données globales
  // Remplacer 'World' par 'US' ou un autre pays disponible si 'World' n'est pas disponible
  // Ensuite, on affichera un message indiquant qu'il s'agit de données pour ce pays
  // plutôt que des données mondiales
  const { 
    data: globalData,
    isLoading,
    error
  } = useQuery(
    ['historical', 'US'], // Utiliser 'US' comme fallback au lieu de 'World'
    () => fetchHistoricalData('US'),
    { 
      staleTime: 5 * 60 * 1000, // 5 minutes
      retry: 1, // Limiter le nombre de tentatives en cas d'erreur
    }
  );
  
  // Couleurs thématiques
  const cardBg = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const labelColor = useColorModeValue('gray.600', 'gray.300');
  
  // Calcul des statistiques globales
  const calculateGlobalStats = () => {
    if (!globalData || !globalData.historical_data || globalData.historical_data.length === 0) {
      return {
        totalCases: 0,
        totalDeaths: 0,
        newCasesDaily: 0,
        newDeathsDaily: 0,
        changeInCases: 0,
        changeInDeaths: 0
      };
    }
    
    // Trier les données par date (les plus récentes en premier)
    const sortedData = [...globalData.historical_data].sort((a, b) => 
      new Date(b.date) - new Date(a.date)
    );
    
    // Données les plus récentes
    const latest = sortedData[0];
    
    // Données de la veille
    const yesterday = sortedData[1] || { new_cases: 0, new_deaths: 0 };
    
    // Données de la semaine précédente
    const lastWeek = sortedData[7] || { new_cases: 0, new_deaths: 0 };
    
    // Calculer le changement quotidien en pourcentage
    const casesChange = yesterday.new_cases !== 0 
      ? ((latest.new_cases - yesterday.new_cases) / yesterday.new_cases) * 100 
      : 0;
      
    const deathsChange = yesterday.new_deaths !== 0 
      ? ((latest.new_deaths - yesterday.new_deaths) / yesterday.new_deaths) * 100 
      : 0;
    
    // Calculer la moyenne hebdomadaire
    const last7Days = sortedData.slice(0, 7);
    const averageCases7Days = last7Days.reduce((sum, day) => sum + day.new_cases, 0) / last7Days.length;
    const averageDeaths7Days = last7Days.reduce((sum, day) => sum + day.new_deaths, 0) / last7Days.length;
    
    return {
      totalCases: latest.total_cases,
      totalDeaths: latest.total_deaths,
      newCasesDaily: latest.new_cases,
      newDeathsDaily: latest.new_deaths,
      averageCases7Days,
      averageDeaths7Days,
      changeInCases: casesChange,
      changeInDeaths: deathsChange,
      latestDate: new Date(latest.date).toLocaleDateString()
    };
  };
  
  const stats = globalData ? calculateGlobalStats() : null;
  
  if (isLoading) {
    return (
      <Flex justify="center" align="center" p={4}>
        <Spinner size="xl" color="blue.500" />
        <Text ml={3}>Chargement des statistiques globales...</Text>
      </Flex>
    );
  }
  
  if (error || !stats) {
    return (
      <Box p={4} bg="red.50" color="red.500" borderRadius="md">
        <Text>
          Une erreur s'est produite lors du chargement des statistiques globales.
          Veuillez réessayer ultérieurement.
        </Text>
      </Box>
    );
  }
  
  return (
    <Box>
      <VisuallyHidden id="global-stats-desc">
        Statistiques globales mondiales de COVID-19 au {stats.latestDate}
      </VisuallyHidden>
      
      <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={4} aria-describedby="global-stats-desc">
        {/* Total des cas */}
        <Box 
          p={4} 
          bg={cardBg} 
          borderRadius="lg" 
          boxShadow="sm"
          borderWidth="1px"
          borderColor={borderColor}
        >
          <Stat>
            <StatLabel color={labelColor}>Total des cas dans le monde</StatLabel>
            <StatNumber fontSize="2xl" color="blue.500">
              {stats.totalCases.toLocaleString()}
            </StatNumber>
            <StatHelpText fontSize="sm">
              Au {stats.latestDate}
            </StatHelpText>
          </Stat>
        </Box>
        
        {/* Nouveaux cas */}
        <Box 
          p={4} 
          bg={cardBg} 
          borderRadius="lg" 
          boxShadow="sm"
          borderWidth="1px"
          borderColor={borderColor}
        >
          <Stat>
            <StatLabel color={labelColor}>Nouveaux cas (quotidien)</StatLabel>
            <StatNumber fontSize="2xl" color="orange.500">
              {stats.newCasesDaily.toLocaleString()}
            </StatNumber>
            <StatHelpText fontSize="sm">
              <StatArrow 
                type={stats.changeInCases >= 0 ? 'increase' : 'decrease'} 
                color={stats.changeInCases >= 0 ? 'red.500' : 'green.500'}
              />
              {Math.abs(stats.changeInCases).toFixed(1)}% vs hier
            </StatHelpText>
          </Stat>
        </Box>
        
        {/* Total des décès */}
        <Box 
          p={4} 
          bg={cardBg} 
          borderRadius="lg" 
          boxShadow="sm"
          borderWidth="1px"
          borderColor={borderColor}
        >
          <Stat>
            <StatLabel color={labelColor}>Total des décès dans le monde</StatLabel>
            <StatNumber fontSize="2xl" color="red.500">
              {stats.totalDeaths.toLocaleString()}
            </StatNumber>
            <StatHelpText fontSize="sm">
              Au {stats.latestDate}
            </StatHelpText>
          </Stat>
        </Box>
        
        {/* Nouveaux décès */}
        <Box 
          p={4} 
          bg={cardBg} 
          borderRadius="lg" 
          boxShadow="sm"
          borderWidth="1px"
          borderColor={borderColor}
        >
          <Stat>
            <StatLabel color={labelColor}>Nouveaux décès (quotidien)</StatLabel>
            <StatNumber fontSize="2xl" color="red.700">
              {stats.newDeathsDaily.toLocaleString()}
            </StatNumber>
            <StatHelpText fontSize="sm">
              <StatArrow 
                type={stats.changeInDeaths >= 0 ? 'increase' : 'decrease'}
                color={stats.changeInDeaths >= 0 ? 'red.500' : 'green.500'}
              />
              {Math.abs(stats.changeInDeaths).toFixed(1)}% vs hier
            </StatHelpText>
          </Stat>
        </Box>
      </SimpleGrid>
      
      {/* Moyennes sur 7 jours */}
      <Box 
        mt={4} 
        p={4} 
        bg={cardBg} 
        borderRadius="lg" 
        boxShadow="sm"
        borderWidth="1px"
        borderColor={borderColor}
      >
        <Text fontWeight="medium" mb={2}>
          Moyennes sur les 7 derniers jours
        </Text>
        <Flex 
          justify="space-between" 
          wrap={{ base: 'wrap', md: 'nowrap' }}
          gap={2}
        >
          <Box flex="1">
            <Text color={labelColor} fontSize="sm">
              Nouveaux cas (moyenne)
            </Text>
            <Text fontWeight="bold" fontSize="xl" color="orange.500">
              {Math.round(stats.averageCases7Days).toLocaleString()}
            </Text>
          </Box>
          
          <Divider orientation="vertical" height="40px" />
          
          <Box flex="1">
            <Text color={labelColor} fontSize="sm">
              Nouveaux décès (moyenne)
            </Text>
            <Text fontWeight="bold" fontSize="xl" color="red.500">
              {Math.round(stats.averageDeaths7Days).toLocaleString()}
            </Text>
          </Box>
          
          <Divider orientation="vertical" height="40px" />
          
          <Box flex="1">
            <Text color={labelColor} fontSize="sm">
              Dernière mise à jour
            </Text>
            <Text fontWeight="bold" fontSize="md">
              {stats.latestDate}
            </Text>
          </Box>
        </Flex>
      </Box>
    </Box>
  );
};

export default GlobalStats;
