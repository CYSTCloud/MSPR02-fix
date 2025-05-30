import React, { useState } from 'react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer,
  LabelList
} from 'recharts';
import { 
  Box, 
  Flex, 
  Select, 
  Text, 
  useColorModeValue,
  Spinner,
  Alert,
  AlertIcon,
  VisuallyHidden
} from '@chakra-ui/react';
import { useQuery } from 'react-query';
import { compareCountries } from '../../services/api';

/**
 * Composant CountryComparisonChart
 * Graphique de comparaison de métriques entre différents pays
 * 
 * @param {Object} props - Propriétés du composant
 * @param {Array<string>} props.countries - Liste des pays à comparer
 * @returns {JSX.Element} Graphique de comparaison
 */
const CountryComparisonChart = ({ countries = [] }) => {
  const [metric, setMetric] = useState('total_cases');
  
  // Couleurs thématiques
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const backgroundColor = useColorModeValue('white', 'gray.700');
  // Ajouter cette ligne pour résoudre l'erreur du hook dans le LabelList
  const labelColor = useColorModeValue('#1A202C', '#E2E8F0');
  
  // Palette de couleurs pour les pays
  const countryColors = [
    '#3182CE', // bleu
    '#E53E3E', // rouge
    '#38A169', // vert
    '#D69E2E', // jaune
    '#805AD5', // violet
    '#DD6B20', // orange
    '#00B5D8', // cyan
    '#ED64A6'  // rose
  ];
  
  // Récupération des données comparatives
  const { 
    data: comparisonData, 
    isLoading, 
    error 
  } = useQuery(
    ['countryComparison', countries, metric],
    () => compareCountries(countries, metric),
    {
      enabled: countries.length > 0,
      refetchOnWindowFocus: false,
      staleTime: 5 * 60 * 1000, // 5 minutes
    }
  );
  
  // Fonction pour formater les grands nombres
  const formatNumber = (value) => {
    if (value >= 1000000) {
      return `${(value / 1000000).toFixed(1)}M`;
    } else if (value >= 1000) {
      return `${(value / 1000).toFixed(0)}K`;
    }
    return value;
  };
  
  // Fonction pour obtenir le label de la métrique
  const getMetricLabel = () => {
    switch (metric) {
      case 'total_cases':
        return 'Cas Totaux';
      case 'total_deaths':
        return 'Décès Totaux';
      case 'new_cases':
        return 'Nouveaux Cas';
      case 'new_deaths':
        return 'Nouveaux Décès';
      default:
        return 'Cas Totaux';
    }
  };
  
  // Préparation des données pour le graphique
  const prepareChartData = () => {
    if (!comparisonData || !comparisonData.comparison_data) return [];
    
    return countries.map((country, index) => {
      const countryData = comparisonData.comparison_data.find(data => data.country === country);
      return {
        country: country.replace('_', ' '),
        value: countryData ? countryData[metric] : 0,
        color: countryColors[index % countryColors.length]
      };
    }).sort((a, b) => b.value - a.value); // Tri par ordre décroissant
  };
  
  const chartData = prepareChartData();
  
  // Composant personnalisé pour le tooltip
  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <Box 
          bg={backgroundColor} 
          p={2} 
          borderRadius="md" 
          boxShadow="md" 
          borderWidth="1px"
          borderColor={borderColor}
        >
          <Text fontWeight="bold">{payload[0].payload.country}</Text>
          <Text>
            {getMetricLabel()}: {payload[0].value.toLocaleString()}
          </Text>
        </Box>
      );
    }
    return null;
  };
  
  // Si les données sont en cours de chargement
  if (isLoading) {
    return (
      <Flex justify="center" align="center" h="200px">
        <Spinner size="xl" color="blue.500" />
      </Flex>
    );
  }
  
  // Si une erreur s'est produite
  if (error) {
    return (
      <Alert status="error" borderRadius="md">
        <AlertIcon />
        Une erreur s'est produite lors du chargement des données comparatives.
      </Alert>
    );
  }
  
  // Si aucune donnée n'est disponible ou aucun pays sélectionné
  if (countries.length === 0 || !comparisonData) {
    return (
      <Alert status="info" borderRadius="md">
        <AlertIcon />
        Veuillez sélectionner des pays à comparer.
      </Alert>
    );
  }
  
  return (
    <Box>
      {/* Sélecteur de métrique */}
      <Flex mb={4} justify="flex-end">
        <Box>
          <Text fontSize="sm" mb={1}>Métrique:</Text>
          <Select 
            value={metric} 
            onChange={(e) => setMetric(e.target.value)}
            size="sm"
            w="180px"
            aria-label="Sélectionner une métrique"
          >
            <option value="total_cases">Cas Totaux</option>
            <option value="total_deaths">Décès Totaux</option>
            <option value="new_cases">Nouveaux Cas</option>
            <option value="new_deaths">Nouveaux Décès</option>
          </Select>
        </Box>
      </Flex>
      
      {/* Label accessible pour le graphique */}
      <VisuallyHidden id="comparison-chart-desc">
        Graphique de comparaison des {getMetricLabel()} entre {countries.join(', ')}
      </VisuallyHidden>
      
      {/* Graphique de comparaison */}
      <Box height="300px">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={chartData}
            layout="vertical"
            margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
            aria-labelledby="comparison-chart-desc"
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              type="number" 
              tickFormatter={formatNumber}
            />
            <YAxis 
              type="category" 
              dataKey="country" 
              width={100}
              tick={{ fontSize: 12 }}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            <Bar 
              dataKey="value" 
              name={getMetricLabel()} 
              fill="#3182CE"
              barSize={30}
            >
              {/* Utiliser la variable labelColor définie au niveau supérieur */}
              <LabelList 
                dataKey="value" 
                position="right" 
                formatter={formatNumber}
                style={{ fill: labelColor, fontSize: '12px' }}
              />
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </Box>
    </Box>
  );
};

export default CountryComparisonChart;
