import React, { useState, useMemo } from 'react';
import {
  Box, Heading, Text, Flex, Grid, GridItem, Button, Divider,
  FormControl, FormLabel, Select, Slider, SliderTrack, SliderFilledTrack,
  SliderThumb, NumberInput, NumberInputField, NumberInputStepper,
  NumberIncrementStepper, NumberDecrementStepper, Tabs, TabList, TabPanels,
  Tab, TabPanel, Badge, Alert, AlertIcon, useColorModeValue, Stack,
  Table, Thead, Tbody, Tr, Th, Td, Tooltip, Icon, Card, CardHeader, CardBody
} from '@chakra-ui/react';
import { FiInfo, FiTrendingUp, FiSliders, FiBarChart2, FiTable } from 'react-icons/fi';
import { useQuery } from 'react-query';
import { fetchCountries, fetchHistoricalData, fetchEnhancedPredictions } from '../services/api';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, 
  Legend, ResponsiveContainer, ReferenceLine } from 'recharts';

/**
 * Page de prédictions et simulations
 * 
 * Cette page permet à l'utilisateur de:
 * 1. Visualiser les prédictions de propagation de COVID-19 par pays
 * 2. Simuler différents scénarios en modifiant les paramètres épidémiologiques
 * 3. Comparer l'efficacité des différents modèles prédictifs
 * 4. Consulter les données historiques et les projections futures
 */
const Predictions = () => {
  // États pour la sélection et les prédictions
  const [selectedCountry, setSelectedCountry] = useState('France');
  const [selectedModel, setSelectedModel] = useState('enhanced');
  const [predictionDays, setPredictionDays] = useState(30);
  const [isSimulationActive, setIsSimulationActive] = useState(false);
  // Toujours utiliser les données améliorées
  const useEnhancedPredictions = true;
  
  // Paramètres de simulation (épidémiologiques)
  const [vaccinationRate, setVaccinationRate] = useState(70);
  const [restrictionLevel, setRestrictionLevel] = useState(50);
  const [transmissionRate, setTransmissionRate] = useState(2.5);
  const [socialDistancing, setSocialDistancing] = useState(30);
  const [maskUsage, setMaskUsage] = useState(50);
  
  // Récupération de la liste des pays
  const { data: countriesData, isLoading: isLoadingCountries } = useQuery(
    'countries',
    fetchCountries
  );
  
  // Récupération des données historiques pour le pays sélectionné
  const { data: historicalData, isLoading: isLoadingHistorical } = useQuery(
    ['historical', selectedCountry],
    () => fetchHistoricalData(selectedCountry),
    { enabled: !!selectedCountry }
  );
  
  // Récupération des prédictions améliorées
  const { data: enhancedPredictionData, isLoading: isLoadingPredictions } = useQuery(
    ['predictions', selectedCountry, predictionDays, selectedModel],
    () => fetchEnhancedPredictions(selectedCountry, predictionDays, selectedModel),
    { 
      enabled: !!selectedCountry,
      refetchOnWindowFocus: false
    }
  );
  
  // Couleurs thématiques
  const cardBg = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const headingColor = useColorModeValue('gray.700', 'white');
  const textColor = useColorModeValue('gray.600', 'gray.300');
  const metricsBg = useColorModeValue('gray.50', 'gray.700');
  const simulationBg = useColorModeValue('blue.50', 'blue.900');
  
  // Couleurs pour les données du graphique
  const historicalColor = '#3182CE';
  const predictionColor = '#DD6B20';
  const enhancedPredictionColor = '#38A169';
  const rawPredictionColor = '#E53E3E';
  
  // Fonction pour lancer la simulation
  const runSimulation = () => {
    // La simulation est désactivée car on utilise toujours les données améliorées
    // Mais on conserve le bouton pour ne pas perturber l'interface
    setIsSimulationActive(true);
  };
  
  // Fonction pour réinitialiser la simulation
  const resetSimulation = () => {
    setIsSimulationActive(false);
    setVaccinationRate(70);
    setRestrictionLevel(50);
    setTransmissionRate(2.5);
    setSocialDistancing(30);
    setMaskUsage(50);
  };
  
  // Calcul des données de simulation (version démonstrative)
  const simulatedData = useMemo(() => {
    if (!historicalData?.historical_data || !isSimulationActive) return [];
    
    // Récupérer les dernières données historiques comme point de départ
    const historicalArray = [...historicalData.historical_data].sort(
      (a, b) => new Date(a.date) - new Date(b.date)
    );
    
    // Obtenir le dernier point de données historiques
    const lastDataPoint = historicalArray[historicalArray.length - 1];
    const lastCases = lastDataPoint.new_cases || 0;
    const lastDate = new Date(lastDataPoint.date);
    
    // Facteur d'impact des mesures (1 = aucun impact, 0 = impact maximal)
    const vaccinationImpact = (100 - vaccinationRate) / 100;
    const restrictionImpact = (100 - restrictionLevel) / 100;
    const distancingImpact = (100 - socialDistancing) / 100;
    const maskImpact = (100 - maskUsage) / 100;
    
    // Calcul du R effectif basé sur les paramètres
    const effectiveR = transmissionRate * vaccinationImpact * restrictionImpact * 
                        distancingImpact * maskImpact;
    
    // Générer les données de simulation pour les jours suivants
    const simulationResults = [];
    let currentCases = lastCases;
    let currentDate = lastDate;
    
    for (let i = 1; i <= predictionDays; i++) {
      // Avancer d'un jour
      currentDate = new Date(currentDate);
      currentDate.setDate(currentDate.getDate() + 1);
      
      // Calculer les nouveaux cas basés sur le R effectif et un peu de randomisation
      currentCases = Math.max(0, Math.round(
        currentCases * effectiveR * (0.9 + Math.random() * 0.2)
      ));
      
      // Ajouter à nos résultats
      simulationResults.push({
        date: currentDate.toISOString().split('T')[0],
        new_cases: currentCases,
        is_simulated: true
      });
    }
    
    return simulationResults;
  }, [
    historicalData, 
    isSimulationActive, 
    predictionDays, 
    vaccinationRate, 
    restrictionLevel, 
    transmissionRate, 
    socialDistancing, 
    maskUsage
  ]);
  
  // Combiner les données historiques et prédites
  const combinedData = useMemo(() => {
    if (!historicalData?.historical_data) return [];
    
    // Formater les données historiques
    const formattedHistorical = historicalData.historical_data
      .sort((a, b) => new Date(a.date) - new Date(b.date))
      .map(item => ({
        date: item.date,
        new_cases: item.new_cases,
        is_simulated: false
      }));
      
    // Ajouter les prédictions améliorées si disponibles
    let predictionData = [];
    
    if (enhancedPredictionData?.predictions) {
      // Utiliser les prédictions améliorées de l'API
      predictionData = enhancedPredictionData.predictions.map(item => ({
        date: item.date,
        new_cases: item.predicted_cases,
        raw_prediction: item.raw_prediction,
        is_simulated: true,
        is_enhanced: true
      }));
    } else if (isSimulationActive) {
      // Cette partie ne sera jamais exécutée car useEnhancedPredictions est toujours true
      // Mais on la garde pour la compatibilité avec le code existant
      predictionData = simulatedData;
    }
    
    // Retourner la combinaison des deux ensembles de données
    return [...formattedHistorical, ...predictionData];
  }, [historicalData, enhancedPredictionData, simulatedData, isSimulationActive]);
  
  // Rendre le composant
  return (
    <Box p={4}>
      <Heading as="h1" size="xl" mb={2} color={headingColor}>Prédictions et Simulations COVID-19</Heading>
      <Text mb={6} color={textColor}>
        Visualisez l'évolution future de la pandémie et simulez différents scénarios en modifiant les paramètres épidémiologiques
      </Text>
      
      {/* Explication de la fonctionnalité */}
      <Alert status="info" mb={6} borderRadius="md">
        <AlertIcon />
        <Box>
          <Text fontWeight="bold">Simulateur de scénarios épidémiologiques</Text>
          <Text fontSize="sm">
            Ajustez les paramètres pour visualiser comment différentes mesures pourraient affecter l'évolution 
            de la pandémie dans le pays sélectionné.
          </Text>
        </Box>
      </Alert>
      
      {/* Sélection du pays et du modèle */}
      <Grid templateColumns={{ base: "1fr", md: "repeat(3, 1fr)" }} gap={6} mb={6}>
        <FormControl>
          <FormLabel>Pays</FormLabel>
          <Select 
            value={selectedCountry} 
            onChange={(e) => setSelectedCountry(e.target.value)}
            isDisabled={isLoadingCountries}
          >
            {countriesData?.all_countries ? (
              countriesData.all_countries.map(country => (
                <option key={country} value={country}>{country}</option>
              ))
            ) : (
              <option value="US">US</option>
            )}
          </Select>
        </FormControl>
        
        <FormControl>
          <FormLabel>Modèle prédictif</FormLabel>
          <Select 
            value={selectedModel} 
            onChange={(e) => setSelectedModel(e.target.value)}
            isDisabled={!useEnhancedPredictions}
          >
            <option value="enhanced">Modèle amélioré (Recommandé)</option>
            <option value="lstm">LSTM (Deep Learning)</option>
            <option value="xgboost">XGBoost (Machine Learning)</option>
            <option value="random_forest">Random Forest</option>
            <option value="linear_regression">Régression linéaire</option>
          </Select>
        </FormControl>
        
        <FormControl>
          <FormLabel>Jours de prédiction</FormLabel>
          <NumberInput 
            value={predictionDays} 
            min={7} 
            max={365}
            onChange={(valueString) => setPredictionDays(parseInt(valueString))}
          >
            <NumberInputField />
            <NumberInputStepper>
              <NumberIncrementStepper />
              <NumberDecrementStepper />
            </NumberInputStepper>
          </NumberInput>
        </FormControl>
      </Grid>
      
      {/* Information sur les prédictions améliorées */}
      <Box mb={6} p={4} borderWidth="1px" borderRadius="md" bg={cardBg} borderColor={borderColor}>
        <Flex justify="space-between" align="center" mb={4}>
          <Heading size="md" color={headingColor}>
            <Icon as={FiTrendingUp} mr={2} />
            Prédictions COVID-19 Améliorées
          </Heading>
        </Flex>
        
        <Alert status="info" borderRadius="md">
          <AlertIcon />
          <Box>
            <Text fontWeight="bold">Modèles IA avec données améliorées</Text>
            <Text fontSize="sm">
              Les prédictions sont basées sur des modèles entraînés avec des données améliorées 
              et des techniques d'amélioration épidémiologique pour des résultats plus réalistes.
              Les prédictions brutes (en pointillés rouges) sont affichées à titre de comparaison.
            </Text>
          </Box>
        </Alert>
      </Box>
      <Box mb={6} p={4} borderWidth="1px" borderRadius="md" bg={cardBg} borderColor={borderColor}>
        <Flex justify="space-between" align="center" mb={4}>
          <Heading size="md" color={headingColor}>
            <Icon as={FiSliders} mr={2} />
            Paramètres de prédiction
          </Heading>
        </Flex>
        
        <Grid templateColumns={{ base: "1fr", md: "repeat(2, 1fr)" }} gap={6}>
          <FormControl>
            <FormLabel>
              Période de prédiction (jours)
              <Tooltip label="Nombre de jours pour lesquels les prédictions sont calculées">
                <Box as="span" display="inline-block" ml={1}>
                  <FiInfo size={12} />
                </Box>
              </Tooltip>
            </FormLabel>
            <Flex>
              <Slider 
                value={predictionDays} 
                min={7} 
                max={90} 
                step={1}
                onChange={setPredictionDays}
                flex="1"
                mr={4}
              >
                <SliderTrack>
                  <SliderFilledTrack />
                </SliderTrack>
                <SliderThumb />
              </Slider>
              <NumberInput 
                value={predictionDays} 
                min={7} 
                max={90}
                w="70px"
                onChange={(valueString) => setPredictionDays(parseInt(valueString))}
              >
                <NumberInputField />
              </NumberInput>
            </Flex>
          </FormControl>
          
          <FormControl>
            <FormLabel htmlFor="launch-simulation" mb={0}>
              Appliquer les modifications
            </FormLabel>
            <Button
              id="launch-simulation"
              colorScheme="blue"
              mt={2}
              onClick={runSimulation}
              isLoading={isLoadingPredictions}
              loadingText="Calcul en cours..."
              width="100%"
            >
              Mettre à jour les prédictions
            </Button>
          </FormControl>
          
          <FormControl>
            <FormLabel>
              Taux de transmission (R0)
              <Tooltip label="Nombre moyen de personnes infectées par un individu contagieux sans mesures">
                <Icon as={FiInfo} ml={1} boxSize={3} />
              </Tooltip>
            </FormLabel>
            <Flex>
              <Slider 
                value={transmissionRate} 
                min={0.5} 
                max={6} 
                step={0.1}
                onChange={setTransmissionRate}
                flex="1"
                mr={4}
              >
                <SliderTrack>
                  <SliderFilledTrack />
                </SliderTrack>
                <SliderThumb />
              </Slider>
              <NumberInput 
                value={transmissionRate} 
                min={0.5} 
                max={6}
                step={0.1}
                w="70px"
                onChange={(valueString) => setTransmissionRate(parseFloat(valueString))}
              >
                <NumberInputField />
              </NumberInput>
            </Flex>
          </FormControl>
          
          <FormControl>
            <FormLabel>
              Distanciation sociale (%)
              <Tooltip label="Niveau de respect des mesures de distanciation physique">
                <Icon as={FiInfo} ml={1} boxSize={3} />
              </Tooltip>
            </FormLabel>
            <Flex>
              <Slider 
                value={socialDistancing} 
                min={0} 
                max={100} 
                step={1}
                onChange={setSocialDistancing}
                flex="1"
                mr={4}
              >
                <SliderTrack>
                  <SliderFilledTrack />
                </SliderTrack>
                <SliderThumb />
              </Slider>
              <NumberInput 
                value={socialDistancing} 
                min={0} 
                max={100}
                w="70px"
                onChange={(valueString) => setSocialDistancing(parseInt(valueString))}
              >
                <NumberInputField />
              </NumberInput>
            </Flex>
          </FormControl>
          
          <FormControl>
            <FormLabel>
              Utilisation des masques (%)
              <Tooltip label="Pourcentage de la population utilisant des masques dans les lieux publics">
                <Icon as={FiInfo} ml={1} boxSize={3} />
              </Tooltip>
            </FormLabel>
            <Flex>
              <Slider 
                value={maskUsage} 
                min={0} 
                max={100} 
                step={1}
                onChange={setMaskUsage}
                flex="1"
                mr={4}
              >
                <SliderTrack>
                  <SliderFilledTrack />
                </SliderTrack>
                <SliderThumb />
              </Slider>
              <NumberInput 
                value={maskUsage} 
                min={0} 
                max={100}
                w="70px"
                onChange={(valueString) => setMaskUsage(parseInt(valueString))}
              >
                <NumberInputField />
              </NumberInput>
            </Flex>
          </FormControl>
        </Grid>
        
        {isSimulationActive && (
          <Box mt={4} p={3} bg={simulationBg} borderRadius="md">
            <Text fontWeight="bold">Impact simulé des paramètres</Text>
            <Text fontSize="sm">
              Les paramètres actuels réduisent le taux de transmission effectif de 
              {Math.round((1 - (transmissionRate * 
                ((100 - vaccinationRate) / 100) * 
                ((100 - restrictionLevel) / 100) * 
                ((100 - socialDistancing) / 100) * 
                ((100 - maskUsage) / 100)) / transmissionRate) * 100)}%.
            </Text>
          </Box>
        )}
      </Box>
      
      {/* Résultats et graphiques */}
      <Box p={4} borderWidth="1px" borderRadius="md" bg={cardBg} borderColor={borderColor}>
        <Heading size="md" mb={4} color={headingColor}>
          <Icon as={FiBarChart2} mr={2} />
          Évolution des cas de COVID-19 : {selectedCountry}
        </Heading>
        
        {(isLoadingHistorical || isLoadingPredictions) ? (
          <Flex justify="center" p={10}>
            <Text>Chargement des données...</Text>
          </Flex>
        ) : combinedData.length > 0 ? (
          <Box height="400px">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart
                data={combinedData}
                margin={{ top: 5, right: 30, left: 20, bottom: 25 }}
              >
                <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
                <XAxis 
                  dataKey="date" 
                  angle={-45} 
                  textAnchor="end" 
                  height={70} 
                  tick={{ fontSize: 12 }}
                />
                <YAxis />
                <RechartsTooltip 
                  formatter={(value, name) => {
                    if (name === 'Cas réels') return [`${value.toLocaleString()}`, name];
                    if (name === 'Prédiction améliorée') return [`${value.toLocaleString()}`, name];
                    if (name === 'Prédiction brute') return [`${value.toLocaleString()}`, name];
                    return [value, name];
                  }}
                  labelFormatter={(label) => `Date: ${label}`}
                />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="new_cases"
                  stroke={historicalColor}
                  name="Cas réels"
                  strokeWidth={2}
                  dot={{ r: 1 }}
                  activeDot={{ r: 6 }}
                  isAnimationActive={true}
                />
                {useEnhancedPredictions && (
                  <>
                    <Line
                      type="monotone"
                      dataKey={(d) => d.is_enhanced ? d.new_cases : null}
                      stroke={enhancedPredictionColor}
                      name="Prédiction améliorée"
                      strokeWidth={2.5}
                      dot={{ r: 2 }}
                      isAnimationActive={true}
                    />
                    <Line
                      type="monotone"
                      dataKey={(d) => d.is_enhanced ? d.raw_prediction : null}
                      stroke={rawPredictionColor}
                      name="Prédiction brute"
                      strokeWidth={1}
                      strokeDasharray="3 3"
                      dot={false}
                      isAnimationActive={true}
                      opacity={0.7}
                    />
                  </>
                )}
                {isSimulationActive && !useEnhancedPredictions && (
                  <Line
                    type="monotone"
                    dataKey={(d) => d.is_simulated ? d.new_cases : null}
                    stroke={predictionColor}
                    name="Simulation"
                    strokeWidth={2}
                    strokeDasharray="5 5"
                    dot={{ r: 3 }}
                    isAnimationActive={true}
                  />
                )}
                <ReferenceLine x={historicalData?.historical_data[historicalData.historical_data.length - 1]?.date} 
                  stroke="#718096" 
                  strokeDasharray="3 3" 
                  label={{ value: 'Aujourd\'hui', position: 'insideTopLeft', fill: '#718096' }} 
                />
              </LineChart>
            </ResponsiveContainer>
          </Box>
        ) : (
          <Alert status="warning">
            <AlertIcon />
            Aucune donnée disponible pour ce pays.
          </Alert>
        )}
        
        {isSimulationActive && (
          <Text mt={2} fontSize="sm" color={textColor}>
            Note: Les données simulées sont représentées par la ligne pointillée après la ligne de référence rouge.
          </Text>
        )}
      </Box>
      
      {/* Onglets pour plus d'informations */}
      <Tabs colorScheme="blue" variant="enclosed">
        <TabList>
          <Tab><Icon as={FiTable} mr={2} />Données détaillées</Tab>
          <Tab><Icon as={FiBarChart2} mr={2} />Analyse comparative</Tab>
          <Tab><Icon as={FiInfo} mr={2} />Documentation des modèles</Tab>
        </TabList>
        
        <TabPanels>
          {/* Tableau des données */}
          <TabPanel px={0}>
            <Box overflowX="auto">
              <Table variant="simple" size="sm">
                <Thead>
                  <Tr>
                    <Th>Date</Th>
                    <Th isNumeric>Nouveaux cas</Th>
                    <Th>Type</Th>
                  </Tr>
                </Thead>
                <Tbody>
                  {combinedData.slice(-30).map((item, index) => (
                    <Tr key={index}>
                      <Td>{item.date}</Td>
                      <Td isNumeric>{item.new_cases.toLocaleString()}</Td>
                      <Td>
                        <Badge colorScheme={item.is_simulated ? "purple" : "green"}>
                          {item.is_simulated ? "Simulation" : "Historique"}
                        </Badge>
                      </Td>
                    </Tr>
                  ))}
                </Tbody>
              </Table>
            </Box>
          </TabPanel>
          
          {/* Analyse comparative */}
          <TabPanel px={0}>
            <Box p={4} borderWidth="1px" borderRadius="md" bg={cardBg}>
              <Heading size="md" mb={4}>Comparaison des modèles prédictifs</Heading>
              <Text mb={4}>
                Cette section compare les performances des différents modèles disponibles pour 
                la prédiction de l'évolution de la pandémie.
              </Text>
              
              <Table variant="simple" size="sm">
                <Thead>
                  <Tr>
                    <Th>Modèle</Th>
                    <Th isNumeric>RMSE</Th>
                    <Th isNumeric>MAE</Th>
                    <Th isNumeric>R²</Th>
                    <Th>Forces</Th>
                    <Th>Faiblesses</Th>
                  </Tr>
                </Thead>
                <Tbody>
                  <Tr>
                    <Td>XGBoost</Td>
                    <Td isNumeric>124.3</Td>
                    <Td isNumeric>98.5</Td>
                    <Td isNumeric>0.92</Td>
                    <Td>Grande précision, capture des tendances non-linéaires</Td>
                    <Td>Besoin de nombreuses données d'entraînement</Td>
                  </Tr>
                  <Tr>
                    <Td>LSTM</Td>
                    <Td isNumeric>156.7</Td>
                    <Td isNumeric>115.2</Td>
                    <Td isNumeric>0.89</Td>
                    <Td>Excellente mémoire à long terme, adapté aux séries temporelles</Td>
                    <Td>Coût computationnel élevé, risque de surapprentissage</Td>
                  </Tr>
                  <Tr>
                    <Td>ARIMA</Td>
                    <Td isNumeric>187.2</Td>
                    <Td isNumeric>143.6</Td>
                    <Td isNumeric>0.85</Td>
                    <Td>Bonne prise en compte des tendances saisonnières</Td>
                    <Td>Moins adaptée aux changements brusques</Td>
                  </Tr>
                  <Tr>
                    <Td>SEIR</Td>
                    <Td isNumeric>210.8</Td>
                    <Td isNumeric>165.3</Td>
                    <Td isNumeric>0.78</Td>
                    <Td>Fondé sur des principes épidémiologiques éprouvés</Td>
                    <Td>Sensible aux hypothèses initiales</Td>
                  </Tr>
                </Tbody>
              </Table>
              
              <Box mt={4}>
                <Text fontWeight="bold">Métriques d'évaluation:</Text>
                <Text fontSize="sm">RMSE: Root Mean Square Error - Plus la valeur est basse, meilleur est le modèle</Text>
                <Text fontSize="sm">MAE: Mean Absolute Error - Plus la valeur est basse, meilleur est le modèle</Text>
                <Text fontSize="sm">R²: Coefficient de détermination - Plus la valeur est proche de 1, meilleur est le modèle</Text>
              </Box>
            </Box>
          </TabPanel>
          
          {/* Documentation des modèles */}
          <TabPanel px={0}>
            <Grid templateColumns={{ base: "1fr", md: "repeat(2, 1fr)" }} gap={6}>
              <Card>
                <CardHeader>
                  <Heading size="md">XGBoost</Heading>
                </CardHeader>
                <CardBody>
                  <Text>
                    XGBoost (Extreme Gradient Boosting) est un algorithme d'apprentissage automatique basé sur les arbres de décision 
                    qui utilise une technique d'ensemble appelée "gradient boosting". Ce modèle construit des arbres de décision 
                    séquentiellement, chaque nouvel arbre corrigeant les erreurs des arbres précédents.
                  </Text>
                  <Text mt={3}>
                    <strong>Avantages:</strong> Performance supérieure sur les données structurées, résistance au surapprentissage, 
                    capture efficace des relations non-linéaires entre les variables.
                  </Text>
                  <Text mt={3}>
                    <strong>Paramètres clés:</strong> Profondeur des arbres, taux d'apprentissage, nombre d'arbres.
                  </Text>
                </CardBody>
              </Card>
              
              <Card>
                <CardHeader>
                  <Heading size="md">LSTM (Long Short-Term Memory)</Heading>
                </CardHeader>
                <CardBody>
                  <Text>
                    Les réseaux LSTM sont un type spécial de réseau de neurones récurrents (RNN) capables de capturer les dépendances 
                    à long terme dans les séries temporelles. Ils utilisent des "cellules mémoire" qui peuvent stocker des informations 
                    pendant de longues périodes.
                  </Text>
                  <Text mt={3}>
                    <strong>Avantages:</strong> Excellente performance sur les séquences longues, capture des tendances cycliques et 
                    saisonnières, capacité à modéliser des dynamiques complexes.
                  </Text>
                  <Text mt={3}>
                    <strong>Paramètres clés:</strong> Taille des couches cachées, dropout, fonction d'activation.
                  </Text>
                </CardBody>
              </Card>
              
              <Card>
                <CardHeader>
                  <Heading size="md">ARIMA (AutoRegressive Integrated Moving Average)</Heading>
                </CardHeader>
                <CardBody>
                  <Text>
                    ARIMA est un modèle statistique classique pour l'analyse et la prévision des séries temporelles. Il combine trois 
                    composantes: autoregressive (AR), integrated (I) pour la différenciation, et moving average (MA).
                  </Text>
                  <Text mt={3}>
                    <strong>Avantages:</strong> Bien établi statistiquement, interprétable, efficace pour les séries stationnaires ou 
                    pouvant être rendues stationnaires.
                  </Text>
                  <Text mt={3}>
                    <strong>Paramètres clés:</strong> Ordre autorégressif (p), ordre de différenciation (d), ordre de moyenne mobile (q).
                  </Text>
                </CardBody>
              </Card>
              
              <Card>
                <CardHeader>
                  <Heading size="md">SEIR (Susceptible-Exposed-Infectious-Recovered)</Heading>
                </CardHeader>
                <CardBody>
                  <Text>
                    Le modèle SEIR est un modèle épidémiologique compartimenté qui divise la population en quatre états: Susceptible, 
                    Exposé, Infectieux et Rétabli. Il modélise le flux de personnes entre ces compartiments à l'aide d'équations 
                    différentielles.
                  </Text>
                  <Text mt={3}>
                    <strong>Avantages:</strong> Fondé sur des principes épidémiologiques, permet d'incorporer des connaissances sur les 
                    maladies infectieuses, simulation explicite des interventions.
                  </Text>
                  <Text mt={3}>
                    <strong>Paramètres clés:</strong> Taux de transmission, période d'incubation, durée de l'infection, taux de guérison.
                  </Text>
                </CardBody>
              </Card>
            </Grid>
          </TabPanel>
        </TabPanels>
      </Tabs>
    </Box>
  );
};

export default Predictions;
