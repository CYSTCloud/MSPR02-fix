import React, { useState, useEffect } from 'react';
import {
  Box,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Text,
  Spinner,
  Alert,
  AlertIcon,
  Select,
  HStack,
  Badge,
  Button,
  useColorModeValue,
  VisuallyHidden
} from '@chakra-ui/react';
import { useQuery } from 'react-query';
import { fetchPredictions } from '../../services/api';

/**
 * Composant RecentPredictionsTable
 * Tableau des prédictions récentes pour un pays spécifique
 * 
 * @param {Object} props - Propriétés du composant
 * @param {string} props.country - Code du pays pour lequel afficher les prédictions
 * @returns {JSX.Element} Tableau des prédictions
 */
const RecentPredictionsTable = ({ country }) => {
  const [modelType, setModelType] = useState('xgboost');
  const [days, setDays] = useState(7);
  
  // Couleurs
  const headerBg = useColorModeValue('gray.50', 'gray.700');
  const headerColor = useColorModeValue('gray.600', 'gray.200');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const hoverBg = useColorModeValue('gray.50', 'gray.600');
  
  // Récupération des prédictions
  const { 
    data: predictionsData,
    isLoading,
    error,
    refetch
  } = useQuery(
    ['predictions', country, days, modelType], 
    () => fetchPredictions(country, days, modelType),
    { 
      enabled: !!country,
      refetchOnWindowFocus: false
    }
  );
  
  // Effet pour actualiser les prédictions lorsque le pays change
  useEffect(() => {
    if (country) {
      refetch();
    }
  }, [country, refetch]);
  
  // Fonction pour formater une date
  const formatDate = (dateString) => {
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    return new Date(dateString).toLocaleDateString(undefined, options);
  };
  
  // Fonction pour déterminer la tendance (hausse, baisse, stable)
  const getTrend = (currentValue, previousValue) => {
    if (!previousValue) return { type: 'neutral', label: 'Stable' };
    
    const diff = currentValue - previousValue;
    const percentChange = (diff / previousValue) * 100;
    
    if (Math.abs(percentChange) < 1) {
      return { type: 'neutral', label: 'Stable', value: '±0%' };
    } else if (diff > 0) {
      return { 
        type: 'increase', 
        label: 'Hausse', 
        value: `+${percentChange.toFixed(1)}%` 
      };
    } else {
      return { 
        type: 'decrease', 
        label: 'Baisse', 
        value: `${percentChange.toFixed(1)}%` 
      };
    }
  };
  
  // Si les données sont en cours de chargement
  if (isLoading) {
    return (
      <Box textAlign="center" py={4}>
        <Spinner size="lg" color="blue.500" />
        <Text mt={2}>Chargement des prédictions...</Text>
      </Box>
    );
  }
  
  // Si une erreur s'est produite
  if (error) {
    return (
      <Alert status="error" borderRadius="md">
        <AlertIcon />
        Une erreur s'est produite lors du chargement des prédictions. 
        Veuillez réessayer ultérieurement.
      </Alert>
    );
  }
  
  // Si aucune donnée n'est disponible
  if (!predictionsData || !predictionsData.predictions || predictionsData.predictions.length === 0) {
    return (
      <Alert status="info" borderRadius="md">
        <AlertIcon />
        Aucune prédiction disponible pour {country} avec le modèle {modelType}.
      </Alert>
    );
  }
  
  // Préparation des données pour l'affichage
  const predictions = predictionsData.predictions;
  
  return (
    <Box>
      {/* Contrôles pour filtrer les prédictions */}
      <HStack mb={4} spacing={4} flexWrap="wrap">
        <Box>
          <Text fontSize="sm" mb={1}>Modèle:</Text>
          <Select 
            value={modelType} 
            onChange={(e) => setModelType(e.target.value)}
            size="sm"
            w="180px"
            aria-label="Sélectionner un modèle"
          >
            <option value="xgboost">XGBoost</option>
            <option value="random_forest">Random Forest</option>
            <option value="gradient_boosting">Gradient Boosting</option>
            <option value="linear_regression">Régression linéaire</option>
            <option value="ridge_regression">Ridge Regression</option>
            <option value="lasso_regression">Lasso Regression</option>
          </Select>
        </Box>
        
        <Box>
          <Text fontSize="sm" mb={1}>Nombre de jours:</Text>
          <Select 
            value={days} 
            onChange={(e) => setDays(parseInt(e.target.value))}
            size="sm"
            w="100px"
            aria-label="Sélectionner le nombre de jours"
          >
            <option value={5}>5</option>
            <option value={7}>7</option>
            <option value={14}>14</option>
            <option value={30}>30</option>
          </Select>
        </Box>
        
        <Button 
          size="sm" 
          colorScheme="blue" 
          mt={4} 
          onClick={() => refetch()}
          alignSelf="flex-end"
        >
          Actualiser
        </Button>
      </HStack>
      
      {/* En-tête accessible pour le tableau */}
      <VisuallyHidden id="predictions-table-desc">
        Tableau des prédictions de cas COVID-19 pour {country} sur les {days} prochains jours
        utilisant le modèle {modelType}.
      </VisuallyHidden>
      
      {/* Tableau des prédictions */}
      <Box overflowX="auto">
        <Table variant="simple" aria-describedby="predictions-table-desc">
          <Thead>
            <Tr>
              <Th bg={headerBg} color={headerColor}>Date</Th>
              <Th bg={headerBg} color={headerColor} isNumeric>Cas prévus</Th>
              <Th bg={headerBg} color={headerColor}>Tendance</Th>
            </Tr>
          </Thead>
          <Tbody>
            {predictions.map((prediction, index) => {
              const previousValue = index > 0 ? predictions[index - 1].predicted_cases : null;
              const trend = getTrend(prediction.predicted_cases, previousValue);
              
              // Déterminer la couleur de la tendance
              let badgeColorScheme = 'gray';
              if (trend.type === 'increase') badgeColorScheme = 'red';
              if (trend.type === 'decrease') badgeColorScheme = 'green';
              
              return (
                <Tr 
                  key={prediction.date}
                  _hover={{ bg: hoverBg }}
                  borderBottomWidth="1px"
                  borderColor={borderColor}
                >
                  <Td>{formatDate(prediction.date)}</Td>
                  <Td isNumeric fontWeight="medium">
                    {Math.round(prediction.predicted_cases).toLocaleString()}
                  </Td>
                  <Td>
                    <Badge colorScheme={badgeColorScheme} px={2} py={1} borderRadius="full">
                      {trend.value || trend.label}
                    </Badge>
                  </Td>
                </Tr>
              );
            })}
          </Tbody>
        </Table>
      </Box>
      
      {/* Informations sur le modèle utilisé */}
      <Box mt={4} fontSize="sm" color="gray.500">
        <Text>
          Modèle: {predictionsData.model_used} | 
          RMSE: {predictionsData.metrics?.RMSE?.toFixed(2) || 'N/A'} | 
          MAE: {predictionsData.metrics?.MAE?.toFixed(2) || 'N/A'} | 
          R²: {predictionsData.metrics?.['R²']?.toFixed(4) || 'N/A'}
        </Text>
      </Box>
    </Box>
  );
};

export default RecentPredictionsTable;
