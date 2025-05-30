import React, { useState, useEffect } from 'react';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer,
  ReferenceLine,
  ReferenceArea,
  Brush
} from 'recharts';
import { 
  Box, 
  Flex, 
  Heading,
  Text,
  ButtonGroup, 
  Button, 
  Select,
  FormControl,
  FormLabel,
  useColorModeValue,
  Badge,
  Spinner,
  Alert,
  AlertIcon
} from '@chakra-ui/react';
import { fetchHistoricalData, fetchPredictions } from '../../services/api';
import { useQuery } from 'react-query';

/**
 * Composant PredictionContinuationChart
 * Affiche un graphique combinant données historiques et prédictions futures
 * en une courbe continue avec une distinction visuelle claire
 * 
 * @param {Object} props - Propriétés du composant
 * @param {string} props.country - Pays sélectionné
 * @returns {JSX.Element} Graphique combinant historique et prédictions
 */
const PredictionContinuationChart = ({ country }) => {
  const [metric, setMetric] = useState('new_cases');
  const [modelType, setModelType] = useState('xgboost');
  const [predictionDays, setPredictionDays] = useState(14);
  
  // Couleurs pour le graphique
  const historicalLineColor = useColorModeValue('blue.600', 'blue.400');
  const predictionLineColor = useColorModeValue('green.600', 'green.400');
  const referenceLineColor = useColorModeValue('red.400', 'red.500');
  const gridColor = useColorModeValue('gray.200', 'gray.600');
  const todayAreaColor = useColorModeValue('gray.100', 'gray.700');
  const cardBg = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const metricsBg = useColorModeValue('gray.50', 'gray.700');
  
  // Récupération des données historiques
  const { 
    data: historicalData,
    isLoading: isLoadingHistorical,
    error: historicalError
  } = useQuery(
    ['historical', country], 
    () => fetchHistoricalData(country),
    { enabled: !!country }
  );
  
  // Récupération des prédictions
  const { 
    data: predictionsData,
    isLoading: isLoadingPredictions,
    error: predictionsError,
    refetch: refetchPredictions
  } = useQuery(
    ['predictions', country, predictionDays, modelType], 
    () => fetchPredictions(country, predictionDays, modelType),
    { enabled: !!country }
  );
  
  // Refetch des prédictions quand le pays, les jours ou le modèle changent
  useEffect(() => {
    if (country) {
      refetchPredictions();
    }
  }, [country, predictionDays, modelType, refetchPredictions]);
  
  // Préparer les données combinées pour le graphique
  const prepareChartData = () => {
    if (!historicalData?.historical_data || !predictionsData?.predictions) return [];
    
    // Trier les données historiques par date
    const sortedHistoricalData = [...historicalData.historical_data]
      .sort((a, b) => new Date(a.date) - new Date(b.date));
    
    // Extraire la dernière date des données historiques
    const lastHistoricalDate = new Date(sortedHistoricalData[sortedHistoricalData.length - 1].date);
    
    // Formater les données historiques
    const formattedHistoricalData = sortedHistoricalData.map(item => ({
      date: new Date(item.date).toISOString().split('T')[0],
      [metric]: item[metric],
      dataType: 'historical'
    }));
    
    // Formater les données de prédiction
    const formattedPredictionData = predictionsData.predictions.map(item => ({
      date: new Date(item.date).toISOString().split('T')[0],
      [metric]: item.predicted_cases,
      dataType: 'prediction'
    }));
    
    // Fusionner les deux ensembles de données
    return [...formattedHistoricalData, ...formattedPredictionData];
  };
  
  // Identifier la date de transition entre historique et prédiction
  const getTransitionDate = () => {
    if (!historicalData?.historical_data || historicalData.historical_data.length === 0) return '';
    
    const sortedData = [...historicalData.historical_data]
      .sort((a, b) => new Date(a.date) - new Date(b.date));
    
    return new Date(sortedData[sortedData.length - 1].date).toISOString().split('T')[0];
  };
  
  // Gérer l'état de chargement
  if (isLoadingHistorical || isLoadingPredictions) {
    return (
      <Box p={4} borderWidth="1px" borderRadius="lg" bg={cardBg} height="400px">
        <Flex justify="center" align="center" height="100%">
          <Spinner size="xl" color="blue.500" thickness="4px" />
        </Flex>
      </Box>
    );
  }
  
  // Gérer les erreurs
  if (historicalError || predictionsError) {
    return (
      <Box p={4} borderWidth="1px" borderRadius="lg" bg={cardBg}>
        <Alert status="error">
          <AlertIcon />
          Une erreur s'est produite lors du chargement des données.
        </Alert>
      </Box>
    );
  }
  
  // Données combinées pour le graphique
  const chartData = prepareChartData();
  const transitionDate = getTransitionDate();
  
  return (
    <Box p={4} borderWidth="1px" borderRadius="lg" bg={cardBg} borderColor={borderColor}>
      <Heading size="md" mb={4}>Évolution et Prédiction des Cas COVID-19</Heading>
      
      <Flex mb={4} wrap="wrap" gap={4}>
        {/* Sélection de la métrique */}
        <FormControl maxW="200px">
          <FormLabel>Métrique</FormLabel>
          <Select 
            value={metric} 
            onChange={(e) => setMetric(e.target.value)}
            size="sm"
          >
            <option value="new_cases">Nouveaux cas</option>
            <option value="total_cases">Cas totaux</option>
            <option value="new_deaths">Nouveaux décès</option>
            <option value="total_deaths">Décès totaux</option>
          </Select>
        </FormControl>
        
        {/* Sélection du modèle */}
        <FormControl maxW="200px">
          <FormLabel>Modèle de prédiction</FormLabel>
          <Select 
            value={modelType} 
            onChange={(e) => setModelType(e.target.value)}
            size="sm"
          >
            <option value="xgboost">XGBoost</option>
            <option value="lasso_regression">Lasso Regression</option>
            <option value="ridge_regression">Ridge Regression</option>
            <option value="svm">SVM</option>
          </Select>
        </FormControl>
        
        {/* Sélection du nombre de jours de prédiction */}
        <FormControl maxW="200px">
          <FormLabel>Jours de prédiction</FormLabel>
          <Select 
            value={predictionDays} 
            onChange={(e) => setPredictionDays(Number(e.target.value))}
            size="sm"
          >
            <option value={7}>7 jours</option>
            <option value={14}>14 jours</option>
            <option value={30}>30 jours</option>
            <option value={60}>60 jours</option>
          </Select>
        </FormControl>
      </Flex>
      
      {/* Légende */}
      <Flex mb={4} wrap="wrap" gap={2} align="center">
        <Badge colorScheme="blue" px={2} py={1}>Données historiques</Badge>
        <Badge colorScheme="green" px={2} py={1}>Prédictions ({modelType})</Badge>
        <Text fontSize="sm" ml={2}>
          Transition: {new Date(transitionDate).toLocaleDateString()}
        </Text>
      </Flex>
      
      {/* Graphique */}
      <Box height="400px">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart
            data={chartData}
            margin={{
              top: 5,
              right: 30,
              left: 20,
              bottom: 5,
            }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke={gridColor} />
            <XAxis 
              dataKey="date" 
              tick={{ fontSize: 12 }}
              tickFormatter={(date) => new Date(date).toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit' })}
            />
            <YAxis 
              tick={{ fontSize: 12 }}
              tickFormatter={(value) => value >= 1000 ? `${(value / 1000).toFixed(1)}k` : value}
            />
            <Tooltip 
              formatter={(value, name) => [value.toLocaleString(), name === metric ? 'Cas' : name]}
              labelFormatter={(date) => new Date(date).toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' })}
            />
            <Legend />
            
            {/* Données historiques */}
            <Line
              type="monotone"
              dataKey={metric}
              stroke={historicalLineColor}
              strokeWidth={2}
              dot={{ r: 2 }}
              activeDot={{ r: 6 }}
              name="Données historiques"
              connectNulls
              isAnimationActive
              animationDuration={1000}
              data={chartData.filter(d => d.dataType === 'historical')}
            />
            
            {/* Prédictions */}
            <Line
              type="monotone"
              dataKey={metric}
              stroke={predictionLineColor}
              strokeWidth={2}
              strokeDasharray="5 5"
              dot={{ r: 3, fill: predictionLineColor }}
              activeDot={{ r: 6 }}
              name="Prédictions"
              connectNulls
              isAnimationActive
              animationDuration={1000}
              animationBegin={1000}
              data={chartData.filter(d => d.dataType === 'prediction')}
            />
            
            {/* Ligne de référence pour la date de transition */}
            <ReferenceLine 
              x={transitionDate} 
              stroke={referenceLineColor} 
              strokeWidth={2}
              label={{ value: 'Aujourd\'hui', position: 'top', fill: referenceLineColor, fontSize: 12 }}
            />
            
            <Brush dataKey="date" height={30} stroke="#8884d8" />
          </LineChart>
        </ResponsiveContainer>
      </Box>
      
      {/* Métriques du modèle */}
      {predictionsData?.metrics && (
        <Box mt={4} p={3} borderWidth="1px" borderRadius="md" bg={metricsBg}>
          <Text fontWeight="medium">Performance du modèle {modelType}:</Text>
          <Flex mt={1} gap={4} wrap="wrap">
            <Text fontSize="sm">RMSE: <strong>{predictionsData.metrics.rmse?.toFixed(2) || 'N/A'}</strong></Text>
            <Text fontSize="sm">MAE: <strong>{predictionsData.metrics.mae?.toFixed(2) || 'N/A'}</strong></Text>
            <Text fontSize="sm">R²: <strong>{predictionsData.metrics.r2?.toFixed(2) || 'N/A'}</strong></Text>
          </Flex>
        </Box>
      )}
    </Box>
  );
};

export default PredictionContinuationChart;
