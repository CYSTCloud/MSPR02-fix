import React, { useState } from 'react';
import {
  Box,
  Heading,
  FormControl,
  FormLabel,
  Button,
  Flex,
  useColorModeValue,
  Tag,
  TagLabel,
  TagCloseButton,
  HStack,
  VStack,
  Alert,
  AlertIcon,
  Select,
  Input,
  SimpleGrid,
  Text
} from '@chakra-ui/react';
import { useQuery } from 'react-query';
import { fetchCountries } from '../services/api';
import CountryComparisonChart from '../components/charts/CountryComparisonChart';
import WorldMap from '../components/charts/WorldMap';

/**
 * Page de comparaison entre pays
 * Permet de comparer les données COVID-19 entre différents pays
 */
const CountryComparison = () => {
  const [selectedCountries, setSelectedCountries] = useState([]);
  const [countryToAdd, setCountryToAdd] = useState('');
  
  // Couleurs thématiques
  const cardBg = useColorModeValue('white', 'gray.700');
  
  // Récupération de la liste des pays
  const { data: countriesData, isLoading: isLoadingCountries } = useQuery('countries', fetchCountries);
  
  // Fonction pour ajouter un pays à la comparaison
  const handleAddCountry = () => {
    if (countryToAdd && !selectedCountries.includes(countryToAdd)) {
      setSelectedCountries([...selectedCountries, countryToAdd]);
      setCountryToAdd('');
    }
  };
  
  // Fonction pour supprimer un pays de la comparaison
  const handleRemoveCountry = (country) => {
    setSelectedCountries(selectedCountries.filter(c => c !== country));
  };
  
  // Pays disponibles pour la sélection (exclusion des pays déjà sélectionnés)
  const availableCountries = countriesData?.countries?.filter(country => 
    !selectedCountries.includes(country)
  ) || [];
  
  return (
    <Box p={4}>
      <Heading as="h1" size="xl" mb={6}>
        Comparaison entre Pays
      </Heading>
      
      <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6} mb={8}>
        {/* Panneau de sélection de pays */}
        <Box p={4} bg={cardBg} borderRadius="lg" boxShadow="md">
          <Heading as="h2" size="md" mb={4}>
            Sélection des Pays
          </Heading>
          
          <FormControl mb={4}>
            <FormLabel htmlFor="country-select">Ajouter un pays à la comparaison</FormLabel>
            <Flex>
              <Select
                id="country-select"
                value={countryToAdd}
                onChange={(e) => setCountryToAdd(e.target.value)}
                placeholder="Sélectionner un pays"
                isDisabled={isLoadingCountries || availableCountries.length === 0}
                mr={2}
              >
                {availableCountries.map((country) => (
                  <option key={country} value={country}>
                    {country.replace('_', ' ')}
                  </option>
                ))}
              </Select>
              <Button 
                colorScheme="blue" 
                onClick={handleAddCountry}
                isDisabled={!countryToAdd || selectedCountries.length >= 5}
              >
                Ajouter
              </Button>
            </Flex>
          </FormControl>
          
          {/* Message d'aide */}
          <Text fontSize="sm" color="gray.500" mb={4}>
            Vous pouvez comparer jusqu'à 5 pays à la fois. Sélectionnez les pays et utilisez les graphiques ci-dessous pour visualiser la comparaison.
          </Text>
          
          {/* Liste des pays sélectionnés */}
          <Box mb={4}>
            <FormLabel>Pays sélectionnés</FormLabel>
            {selectedCountries.length === 0 ? (
              <Alert status="info" borderRadius="md">
                <AlertIcon />
                Aucun pays sélectionné. Ajoutez des pays pour commencer la comparaison.
              </Alert>
            ) : (
              <HStack spacing={2} flexWrap="wrap">
                {selectedCountries.map((country) => (
                  <Tag 
                    key={country} 
                    size="lg" 
                    borderRadius="full" 
                    variant="solid" 
                    colorScheme="blue"
                    m={1}
                  >
                    <TagLabel>{country.replace('_', ' ')}</TagLabel>
                    <TagCloseButton onClick={() => handleRemoveCountry(country)} />
                  </Tag>
                ))}
              </HStack>
            )}
          </Box>
        </Box>
        
        {/* Carte du monde */}
        <Box 
          p={4} 
          bg={cardBg} 
          borderRadius="lg" 
          boxShadow="md" 
          h={{ base: "300px", md: "400px" }}
        >
          <Heading as="h2" size="md" mb={4}>
            Carte Mondiale
          </Heading>
          <WorldMap selectedCountry={selectedCountries[0] || ''} />
        </Box>
      </SimpleGrid>
      
      {/* Graphiques de comparaison */}
      <Box p={4} bg={cardBg} borderRadius="lg" boxShadow="md" mb={8}>
        <Heading as="h2" size="md" mb={6}>
          Comparaison des Métriques
        </Heading>
        
        {selectedCountries.length === 0 ? (
          <Alert status="info" borderRadius="md">
            <AlertIcon />
            Sélectionnez au moins un pays pour voir les comparaisons.
          </Alert>
        ) : (
          <CountryComparisonChart countries={selectedCountries} />
        )}
      </Box>
      
      {/* Explication des métriques */}
      <Box p={4} bg={cardBg} borderRadius="lg" boxShadow="md">
        <Heading as="h2" size="md" mb={4}>
          Guide des Métriques
        </Heading>
        
        <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
          <Box>
            <Text fontWeight="bold">Cas Totaux</Text>
            <Text mb={2}>
              Le nombre cumulatif de cas confirmés de COVID-19 depuis le début de la pandémie.
            </Text>
            
            <Text fontWeight="bold">Décès Totaux</Text>
            <Text mb={2}>
              Le nombre cumulatif de décès attribués à la COVID-19 depuis le début de la pandémie.
            </Text>
          </Box>
          
          <Box>
            <Text fontWeight="bold">Nouveaux Cas</Text>
            <Text mb={2}>
              Le nombre de nouveaux cas confirmés de COVID-19 pour la période la plus récente.
            </Text>
            
            <Text fontWeight="bold">Nouveaux Décès</Text>
            <Text mb={2}>
              Le nombre de nouveaux décès attribués à la COVID-19 pour la période la plus récente.
            </Text>
          </Box>
        </SimpleGrid>
        
        <Alert status="info" mt={4} borderRadius="md">
          <AlertIcon />
          <Box>
            <Text fontWeight="bold">Note sur les données:</Text>
            <Text>
              Les méthodes de comptage et de rapport peuvent varier entre les pays, ce qui peut affecter la comparabilité directe des données.
            </Text>
          </Box>
        </Alert>
      </Box>
    </Box>
  );
};

export default CountryComparison;
