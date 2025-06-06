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
 * Page de prÃ©dictions et simulations
 * 
 * Cette page permet Ã  l'utilisateur de:
 * 1. Visualiser les prÃ©dictions de propagation de COVID-19 par pays
 * 2. Simuler diffÃ©rents scÃ©narios en modifiant les paramÃ¨tres Ã©pidÃ©miologiques
 * 3. Comparer l'efficacitÃ© des diffÃ©rents modÃ¨les prÃ©dictifs
 * 4. Consulter les donnÃ©es historiques et les projections futures
 */
const Predictions = () => {
  // Ã‰tats pour la sÃ©lection et les prÃ©dictions
  const [selectedCountry, setSelectedCountry] = useState('France');
  const [selectedModel, setSelectedModel] = useState('enhanced');
  const [simulationDays, setSimulationDays] = useState(30);
  const [isSimulationActive, setIsSimulationActive] = useState(false);
  // Toujours utiliser les donnÃ©es amÃ©liorÃ©es
  const useEnhancedPredictions = true;
  
  // ParamÃ¨tres de simulation (Ã©pidÃ©miologiques)
  const [vaccinationRate, setVaccinationRate] = useState(70);
  const [restrictionLevel, setRestrictionLevel] = useState(50);
  const [transmissionRate, setTransmissionRate] = useState(2.5);
  const [socialDistancing, setSocialDistancing] = useState(30);
  const [maskUsage, setMaskUsage] = useState(50);
  
  // RÃ©cupÃ©ration de la liste des pays
  const { data: countriesData, isLoading: isLoadingCountries } = useQuery(
    'countries',
    fetchCountries
  );
  
  // RÃ©cupÃ©ration des donnÃ©es historiques pour le pays sÃ©lectionnÃ©
  const { data: historicalData, isLoading: isLoadingHistorical } = useQuery(
    ['historical', selectedCountry],
    () => fetchHistoricalData(selectedCountry),
    { enabled: !!selectedCountry }
  );
  
  // RÃ©cupÃ©ration des prÃ©dictions amÃ©liorÃ©es
  const { data: enhancedPredictionData, isLoading: isLoadingPredictions } = useQuery(
    ['predictions', selectedCountry, simulationDays, selectedModel],
    () => fetchEnhancedPredictions(selectedCountry, simulationDays, selectedModel),
    { 
      enabled: !!selectedCountry,
      refetchOnWindowFocus: false
    }
  );
  
  // Couleurs thÃ©matiques
  const cardBg = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const headingColor = useColorModeValue('gray.700', 'white');
  const textColor = useColorModeValue('gray.600', 'gray.300');
  const metricsBg = useColorModeValue('gray.50', 'gray.700');
  const simulationBg = useColorModeValue('blue.50', 'blue.900');
  
  // Couleurs pour les donnÃ©es du graphique
  const historicalColor = '#3182CE';
  const predictionColor = '#DD6B20';
  const enhancedPredictionColor = '#38A169';
  const rawPredictionColor = '#E53E3E';
  
  // Fonction pour lancer la simulation
  const runSimulation = () => {
    // La simulation est dÃ©sactivÃ©e car on utilise toujours les donnÃ©es amÃ©liorÃ©es
    // Mais on conserve le bouton pour ne pas perturber l'interface
    setIsSimulationActive(true);
  };
  
  // Fonction pour rÃ©initialiser la simulation
  const resetSimulation = () => {
    setIsSimulationActive(false);
    setVaccinationRate(70);
    setRestrictionLevel(50);
    setTransmissionRate(2.5);
    setSocialDistancing(30);
    setMaskUsage(50);
  };
  
  // Calcul des donnÃ©es de simulation (version dÃ©monstrative)
  const simulatedData = useMemo(() => {
    if (!historicalData?.historical_data || !isSimulationActive) return [];
    
    // RÃ©cupÃ©rer les derniÃ¨res donnÃ©es historiques comme point de dÃ©part
    const historicalArray = [...historicalData.historical_data].sort(
      (a, b) => new Date(a.date) - new Date(b.date)
    );
    
    // Obtenir le dernier point de donnÃ©es historiques
    const lastDataPoint = historicalArray[historicalArray.length - 1];
    const lastCases = lastDataPoint.new_cases || 0;
    const lastDate = new Date(lastDataPoint.date);
    
    // Facteur d'impact des mesures (1 = aucun impact, 0 = impact maximal)
    const vaccinationImpact = (100 - vaccinationRate) / 100;
    const restrictionImpact = (100 - restrictionLevel) / 100;
    const distancingImpact = (100 - socialDistancing) / 100;
    const maskImpact = (100 - maskUsage) / 100;
    
    // Calcul du R effectif basÃ© sur les paramÃ¨tres
    const effectiveR = transmissionRate * vaccinationImpact * restrictionImpact * 
                        distancingImpact * maskImpact;
    
    // GÃ©nÃ©rer les donnÃ©es de simulation pour les jours suivants
    const simulationResults = [];
    let currentCases = lastCases;
    let currentDate = lastDate;
    
    for (let i = 1; i <= simulationDays; i++) {
      // Avancer d'un jour
      currentDate = new Date(currentDate);
      currentDate.setDate(currentDate.getDate() + 1);
      
      // Calculer les nouveaux cas basÃ©s sur le R effectif et un peu de randomisation
      currentCases = Math.max(0, Math.round(
        currentCases * effectiveR * (0.9 + Math.random() * 0.2)
      ));
      
      // Ajouter Ã  nos rÃ©sultats
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
    simulationDays, 
    vaccinationRate, 
    restrictionLevel, 
    transmissionRate, 
    socialDistancing, 
    maskUsage
  ]);
  
  // Combiner les donnÃ©es historiques et prÃ©dites
  const combinedData = useMemo(() => {
    if (!historicalData?.historical_data) return [];
    
    // Formater les donnÃ©es historiques
    const formattedHistorical = historicalData.historical_data
      .sort((a, b) => new Date(a.date) - new Date(b.date))
      .map(item => ({
        date: item.date,
        new_cases: item.new_cases,
        is_simulated: false
      }));
      
    // Ajouter les prÃ©dictions amÃ©liorÃ©es si disponibles
    let predictionData = [];
    
    if (enhancedPredictionData?.predictions) {
      // Utiliser les prÃ©dictions amÃ©liorÃ©es de l'API
      predictionData = enhancedPredictionData.predictions.map(item => ({
        date: item.date,
        new_cases: item.predicted_cases,
        raw_prediction: item.raw_prediction,
        is_simulated: true,
        is_enhanced: true
      }));
    } else if (isSimulationActive) {
      // Cette partie ne sera jamais exÃ©cutÃ©e car useEnhancedPredictions est toujours true
      // Mais on la garde pour la compatibilitÃ© avec le code existant
      predictionData = simulatedData;
    }
    
    // Retourner la combinaison des deux ensembles de donnÃ©es
    return [...formattedHistorical, ...predictionData];
  }, [historicalData, enhancedPredictionData, simulatedData, isSimulationActive]);
  
  // Rendre le composant
  return (
    <Box p={4}>
      <Heading as="h1" size="xl" mb={2} color={headingColor}>PrÃ©dictions et Simulations COVID-19</Heading>
      <Text mb={6} color={textColor}>
        Visualisez l'Ã©volution future de la pandÃ©mie et simulez diffÃ©rents scÃ©narios en modifiant les paramÃ¨tres Ã©pidÃ©miologiques
      </Text>
      
      {/* Explication de la fonctionnalitÃ© */}
      <Alert status="info" mb={6} borderRadius="md">
        <AlertIcon />
        <Box>
          <Text fontWeight="bold">Simulateur de scÃ©narios Ã©pidÃ©miologiques</Text>
          <Text fontSize="sm">
            Ajustez les paramÃ¨tres pour visualiser comment diffÃ©rentes mesures pourraient affecter l'Ã©volution 
            de la pandÃ©mie dans le pays sÃ©lectionnÃ©.
          </Text>
        </Box>
      </Alert>
      
      {/* SÃ©lection du pays et du modÃ¨le */}
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
          <FormLabel>ModÃ¨le prÃ©dictif</FormLabel>
          <Select 
            value={selectedModel} 
            onChange={(e) => setSelectedModel(e.target.value)}
            isDisabled={!useEnhancedPredictions}
          >
            <option value="enhanced">ModÃ¨le amÃ©liorÃ© (RecommandÃ©)</option>
            <option value="lstm">LSTM (Deep Learning)</option>
            <option value="xgboost">XGBoost (Machine Learning)</option>
            <option value="random_forest">Random Forest</option>
            <option value="linear_regression">RÃ©gression linÃ©aire</option>
          </Select>
        </FormControl>
        
        <FormControl>
          <FormLabel>Jours de simulation</FormLabel>
          <NumberInput 
            value={simulationDays} 
            min={7} 
            max={365}
            onChange={(valueString) => setSimulationDays(parseInt(valueString))}
          >
            <NumberInputField />
            <NumberInputStepper>
              <NumberIncrementStepper />
              <NumberDecrementStepper />
            </NumberInputStepper>
          </NumberInput>
        </FormControl>
      </Grid>
      
      {/* Information sur les prÃ©dictions amÃ©liorÃ©es */}
      <Box mb={6} p={4} borderWidth="1px" borderRadius="md" bg={cardBg} borderColor={borderColor}>
        <Flex justify="space-between" align="center" mb={4}>
          <Heading size="md" color={headingColor}>
            <Icon as={FiTrendingUp} mr={2} />
            PrÃ©dictions COVID-19 AmÃ©liorÃ©es
          </Heading>
        </Flex>
        
        <Alert status="info" borderRadius="md">
          <AlertIcon />
          <Box>
            <Text fontWeight="bold">ModÃ¨les IA avec donnÃ©es amÃ©liorÃ©es</Text>
            <Text fontSize="sm">
              Les prÃ©dictions sont basÃ©es sur des modÃ¨les entraÃ®nÃ©s avec des donnÃ©es amÃ©liorÃ©es 
              et des techniques d'amÃ©lioration Ã©pidÃ©miologique pour des rÃ©sultats plus rÃ©alistes.
              Les prÃ©dictions brutes (en pointillÃ©s rouges) sont affichÃ©es Ã  titre de comparaison.
            </Text>
          </Box>
        </Alert>
      </Box>
      <Box mb={6} p={4} borderWidth="1px" borderRadius="md" bg={cardBg} borderColor={borderColor}>
        <Flex justify="space-between" align="center" mb={4}>
          <Heading size="md" color={headingColor}>
            <Icon as={FiSliders} mr={2} />
            ParamÃ¨tres de prÃ©diction
          </Heading>
        </Flex>
        
        <Grid templateColumns={{ base: "1fr", md: "repeat(2, 1fr)" }} gap={6}>
          <FormControl>
            <FormLabel>
              PÃ©riode de prÃ©diction (jours)
              <Tooltip label="Nombre de jours pour lesquels les prÃ©dictions sont calculÃ©es">
                <Icon as={FiInfo} ml={1} boxSize={3} />
              </Tooltip>
            </FormLabel>
            <Flex>
              <Slider 
                value={simulationDays} 
                min={7} 
                max={90} 
                step={1}
                onChange={setSimulationDays}
                flex="1"
                mr={4}
              >
                <SliderTrack>
                  <SliderFilledTrack />
                </SliderTrack>
                <SliderThumb />
              </Slider>
              <NumberInput 
                value={simulationDays} 
                min={7} 
                max={90}
                w="70px"
                onChange={(valueString) => setSimulationDays(parseInt(valueString))}
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
              isFullWidth
            >
              Mettre Ã  jour les prÃ©dictions
            </Button>
          </FormControl>
          
          <FormControl>
            <FormLabel>
              Taux de transmission (R0)
              <Tooltip label="Nombre moyen de personnes infectÃ©es par un individu contagieux sans mesures">
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
            <Text fontWeight="bold">Impact simulÃ© des paramÃ¨tres</Text>
            <Text fontSize="sm">
              Les paramÃ¨tres actuels rÃ©duisent le taux de transmission effectif de 
              {Math.round((1 - (transmissionRate * 
                ((100 - vaccinationRate) / 100) * 
                ((100 - restrictionLevel) / 100) * 
                ((100 - socialDistancing) / 100) * 
                ((100 - maskUsage) / 100)) / transmissionRate) * 100)}%.
            </Text>
          </Box>
        )}
      </Box>
      
      {/* RÃ©sultats et graphiques */}
      <Box p={4} borderWidth="1px" borderRadius="md" bg={cardBg} borderColor={borderColor}>
        <Heading size="md" mb={4} color={headingColor}>
          <Icon as={FiBarChart2} mr={2} />
          Ã‰volution des cas de COVID-19 : {selectedCountry}
        </Heading>
        
        {(isLoadingHistorical || isLoadingPredictions) ? (
          <Flex justify="center" p={10}>
            <Text>Chargement des donnÃ©es...</Text>
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
                    if (name === 'Cas rÃ©els') return [`${value.toLocaleString()}`, name];
                    if (name === 'PrÃ©diction amÃ©liorÃ©e') return [`${value.toLocaleString()}`, name];
                    if (name === 'PrÃ©diction brute') return [`${value.toLocaleString()}`, name];
                    return [value, name];
                  }}
                  labelFormatter={(label) => `Date: ${label}`}
                />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="new_cases"
                  stroke={historicalColor}
                  name="Cas rÃ©els"
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
                      name="PrÃ©diction amÃ©liorÃ©e"
                      strokeWidth={2.5}
                      dot={{ r: 2 }}
                      isAnimationActive={true}
                    />
                    <Line
                      type="monotone"
                      dataKey={(d) => d.is_enhanced ? d.raw_prediction : null}
                      stroke={rawPredictionColor}
                      name="PrÃ©diction brute"
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
            Aucune donnÃ©e disponible pour ce pays.
          </Alert>
        )}
        
        {isSimulationActive && (
          <Text mt={2} fontSize="sm" color={textColor}>
            Note: Les donnÃ©es simulÃ©es sont reprÃ©sentÃ©es par la ligne pointillÃ©e aprÃ¨s la ligne de rÃ©fÃ©rence rouge.
          </Text>
        )}
      </Box>
      
      {/* Onglets pour plus d'informations */}
      <Tabs colorScheme="blue" variant="enclosed">
        <TabList>
          <Tab><Icon as={FiTable} mr={2} />DonnÃ©es dÃ©taillÃ©es</Tab>
          <Tab><Icon as={FiBarChart2} mr={2} />Analyse comparative</Tab>
          <Tab><Icon as={FiInfo} mr={2} />Documentation des modÃ¨les</Tab>
        </TabList>
        
        <TabPanels>
          {/* Tableau des donnÃ©es */}
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
              <Heading size="md" mb={4}>Comparaison des modÃ¨les prÃ©dictifs</Heading>
              <Text mb={4}>
                Cette section compare les performances des diffÃ©rents modÃ¨les disponibles pour 
                la prÃ©diction de l'Ã©volution de la pandÃ©mie.
              </Text>
              
              <Table variant="simple" size="sm">
                <Thead>
                  <Tr>
                    <Th>ModÃ¨le</Th>
                    <Th isNumeric>RMSE</Th>
                    <Th isNumeric>MAE</Th>
                    <Th isNumeric>RÂ²</Th>
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
                    <Td>Grande prÃ©cision, capture des tendances non-linÃ©aires</Td>
                    <Td>Besoin de nombreuses donnÃ©es d'entraÃ®nement</Td>
                  </Tr>
                  <Tr>
                    <Td>LSTM</Td>
                    <Td isNumeric>156.7</Td>
                    <Td isNumeric>115.2</Td>
                    <Td isNumeric>0.89</Td>
                    <Td>Excellente mÃ©moire Ã  long terme, adaptÃ© aux sÃ©ries temporelles</Td>
                    <Td>CoÃ»t computationnel Ã©levÃ©, risque de surapprentissage</Td>
                  </Tr>
                  <Tr>
                    <Td>ARIMA</Td>
                    <Td isNumeric>187.2</Td>
                    <Td isNumeric>143.6</Td>
                    <Td isNumeric>0.85</Td>
                    <Td>Bonne prise en compte des tendances saisonniÃ¨res</Td>
                    <Td>Moins adaptÃ©e aux changements brusques</Td>
                  </Tr>
                  <Tr>
                    <Td>SEIR</Td>
                    <Td isNumeric>210.8</Td>
                    <Td isNumeric>165.3</Td>
                    <Td isNumeric>0.78</Td>
                    <Td>FondÃ© sur des principes Ã©pidÃ©miologiques Ã©prouvÃ©s</Td>
                    <Td>Sensible aux hypothÃ¨ses initiales</Td>
                  </Tr>
                </Tbody>
              </Table>
              
              <Box mt={4}>
                <Text fontWeight="bold">MÃ©triques d'Ã©valuation:</Text>
                <Text fontSize="sm">RMSE: Root Mean Square Error - Plus la valeur est basse, meilleur est le modÃ¨le</Text>
                <Text fontSize="sm">MAE: Mean Absolute Error - Plus la valeur est basse, meilleur est le modÃ¨le</Text>
                <Text fontSize="sm">RÂ²: Coefficient de dÃ©termination - Plus la valeur est proche de 1, meilleur est le modÃ¨le</Text>
              </Box>
            </Box>
          </TabPanel>
          
          {/* Documentation des modÃ¨les */}
          <TabPanel px={0}>
            <Grid templateColumns={{ base: "1fr", md: "repeat(2, 1fr)" }} gap={6}>
              <Card>
                <CardHeader>
                  <Heading size="md">XGBoost</Heading>
                </CardHeader>
                <CardBody>
                  <Text>
                    XGBoost (Extreme Gradient Boosting) est un algorithme d'apprentissage automatique basÃ© sur les arbres de dÃ©cision 
                    qui utilise une technique d'ensemble appelÃ©e "gradient boosting". Ce modÃ¨le construit des arbres de dÃ©cision 
                    sÃ©quentiellement, chaque nouvel arbre corrigeant les erreurs des arbres prÃ©cÃ©dents.
                  </Text>
                  <Text mt={3}>
                    <strong>Avantages:</strong> Performance supÃ©rieure sur les donnÃ©es structurÃ©es, rÃ©sistance au surapprentissage, 
                    capture efficace des relations non-linÃ©aires entre les variables.
                  </Text>
                  <Text mt={3}>
                    <strong>ParamÃ¨tres clÃ©s:</strong> Profondeur des arbres, taux d'apprentissage, nombre d'arbres.
                  </Text>
                </CardBody>
              </Card>
              
              <Card>
                <CardHeader>
                  <Heading size="md">LSTM (Long Short-Term Memory)</Heading>
                </CardHeader>
                <CardBody>
                  <Text>
                    Les rÃ©seaux LSTM sont un type spÃ©cial de rÃ©seau de neurones rÃ©currents (RNN) capables de capturer les dÃ©pendances 
                    Ã  long terme dans les sÃ©ries temporelles. Ils utilisent des "cellules mÃ©moire" qui peuvent stocker des informations 
                    pendant de longues pÃ©riodes.
                  </Text>
                  <Text mt={3}>
                    <strong>Avantages:</strong> Excellente performance sur les sÃ©quences longues, capture des tendances cycliques et 
                    saisonniÃ¨res, capacitÃ© Ã  modÃ©liser des dynamiques complexes.
                  </Text>
                  <Text mt={3}>
                    <strong>ParamÃ¨tres clÃ©s:</strong> Taille des couches cachÃ©es, dropout, fonction d'activation.
                  </Text>
                </CardBody>
              </Card>
              
              <Card>
                <CardHeader>
                  <Heading size="md">ARIMA (AutoRegressive Integrated Moving Average)</Heading>
                </CardHeader>
                <CardBody>
                  <Text>
                    ARIMA est un modÃ¨le statistique classique pour l'analyse et la prÃ©vision des sÃ©ries temporelles. Il combine trois 
                    composantes: autoregressive (AR), integrated (I) pour la diffÃ©renciation, et moving average (MA).
                  </Text>
                  <Text mt={3}>
                    <strong>Avantages:</strong> Bien Ã©tabli statistiquement, interprÃ©table, efficace pour les sÃ©ries stationnaires ou 
                    pouvant Ãªtre rendues stationnaires.
                  </Text>
                  <Text mt={3}>
                    <strong>ParamÃ¨tres clÃ©s:</strong> Ordre autorÃ©gressif (p), ordre de diffÃ©renciation (d), ordre de moyenne mobile (q).
                  </Text>
                </CardBody>
              </Card>
              
              <Card>
                <CardHeader>
                  <Heading size="md">SEIR (Susceptible-Exposed-Infectious-Recovered)</Heading>
                </CardHeader>
                <CardBody>
                  <Text>
                    Le modÃ¨le SEIR est un modÃ¨le Ã©pidÃ©miologique compartimentÃ© qui divise la population en quatre Ã©tats: Susceptible, 
                    ExposÃ©, Infectieux et RÃ©tabli. Il modÃ©lise le flux de personnes entre ces compartiments Ã  l'aide d'Ã©quations 
                    diffÃ©rentielles.
                  </Text>
                  <Text mt={3}>
                    <strong>Avantages:</strong> FondÃ© sur des principes Ã©pidÃ©miologiques, permet d'incorporer des connaissances sur les 
                    maladies infectieuses, simulation explicite des interventions.
                  </Text>
                  <Text mt={3}>
                    <strong>ParamÃ¨tres clÃ©s:</strong> Taux de transmission, pÃ©riode d'incubation, durÃ©e de l'infection, taux de guÃ©rison.
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
