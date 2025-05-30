import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Text, 
  Spinner, 
  Flex, 
  useColorModeValue,
  VisuallyHidden,
  Tooltip,
  Button,
  ButtonGroup
} from '@chakra-ui/react';
import { useQuery } from 'react-query';
import { 
  ComposableMap, 
  Geographies, 
  Geography, 
  ZoomableGroup 
} from 'react-simple-maps';
import { fetchCountries } from '../../services/api';

// Fichier GeoJSON contenant les données géographiques mondiales (version locale)
const WORLD_GEO_URL = '/data/world-countries.json';

/**
 * Composant WorldMap
 * Affiche une carte choroplèthe du monde avec mise en évidence du pays sélectionné
 * 
 * @param {Object} props - Propriétés du composant
 * @param {string} props.selectedCountry - Code du pays sélectionné
 * @returns {JSX.Element} Carte mondiale interactive
 */
const WorldMap = ({ selectedCountry }) => {
  const [zoom, setZoom] = useState(1);
  const [center, setCenter] = useState([0, 0]);
  const [tooltipContent, setTooltipContent] = useState('');
  const [tooltipPosition, setTooltipPosition] = useState({ x: 0, y: 0 });
  const [showTooltip, setShowTooltip] = useState(false);
  
  // Couleurs pour la carte
  const fillColor = useColorModeValue('#F5F5F5', '#2D3748');
  const highlightColor = useColorModeValue('#3182CE', '#63B3ED');
  const borderColor = useColorModeValue('#E2E8F0', '#4A5568');
  
  // Récupération des données des pays
  const { data: countriesData, isLoading, error } = useQuery('countries', fetchCountries);
  
  // Trouver les pays avec des modèles entraînés
  const countriesWithModels = countriesData?.countries_with_models || [];
  
  // Correspondance entre les noms de pays API et les noms de pays GeoJSON
  const countryMapping = {
    'US': 'United States of America',
    'United_Kingdom': 'United Kingdom',
    'China': 'China',
    'Brazil': 'Brazil',
    'France': 'France',
    'Germany': 'Germany',
    'India': 'India',
    'Italy': 'Italy',
    'Japan': 'Japan',
    'Russia': 'Russia',
    // Ajoutez d'autres correspondances selon vos besoins
  };
  
  // Convertir le nom de pays API en nom GeoJSON
  const getGeoJsonName = (apiCountryName) => {
    return countryMapping[apiCountryName] || apiCountryName;
  };
  
  // Effet pour centrer la carte sur le pays sélectionné
  useEffect(() => {
    if (selectedCountry) {
      // Coordonnées approximatives des pays (à ajuster selon vos besoins)
      const coordinates = {
        'US': [-95, 38],
        'Brazil': [-55, -10],
        'United_Kingdom': [0, 55],
        'France': [2, 46],
        'Germany': [10, 51],
        'Italy': [12, 42],
        'Spain': [-4, 40],
        'India': [78, 21],
        'Russia': [100, 60],
        'China': [105, 35]
      };
      
      if (coordinates[selectedCountry]) {
        setCenter(coordinates[selectedCountry]);
        setZoom(4);
      } else {
        // Réinitialiser à la vue mondiale si le pays n'est pas dans notre liste
        setCenter([0, 0]);
        setZoom(1);
      }
    }
  }, [selectedCountry]);
  
  // Gestionnaire d'événements pour le survol des pays
  const handleMouseEnter = (geo, evt) => {
    const { NAME } = geo.properties;
    setTooltipContent(NAME);
    setTooltipPosition({ x: evt.clientX, y: evt.clientY });
    setShowTooltip(true);
  };
  
  const handleMouseLeave = () => {
    setTooltipContent('');
    setShowTooltip(false);
  };
  
  // Si les données sont en cours de chargement
  if (isLoading) {
    return (
      <Flex justify="center" align="center" height="100%">
        <Spinner size="xl" color="blue.500" />
      </Flex>
    );
  }
  
  // Si une erreur s'est produite
  if (error) {
    return (
      <Box p={4} borderRadius="md" bg="red.50" color="red.500">
        <Text>Une erreur s'est produite lors du chargement de la carte.</Text>
      </Box>
    );
  }
  
  return (
    <Box height="100%" position="relative">
      <VisuallyHidden id="world-map-desc">
        Carte mondiale montrant la répartition des cas COVID-19 avec mise en évidence du pays sélectionné: {selectedCountry}
      </VisuallyHidden>
      
      {/* Contrôles de zoom */}
      <ButtonGroup size="xs" position="absolute" top={2} right={2} zIndex={10}>
        <Button 
          onClick={() => setZoom(zoom + 0.5)} 
          aria-label="Zoomer"
        >
          +
        </Button>
        <Button 
          onClick={() => { 
            setZoom(Math.max(1, zoom - 0.5));
            if (zoom <= 1.5) setCenter([0, 0]);
          }} 
          aria-label="Dézoomer"
        >
          -
        </Button>
        <Button 
          onClick={() => { 
            setZoom(1);
            setCenter([0, 0]);
          }} 
          aria-label="Réinitialiser la vue"
        >
          Reset
        </Button>
      </ButtonGroup>
      
      {/* Carte */}
      <ComposableMap
        projectionConfig={{ scale: 147 }}
        aria-describedby="world-map-desc"
        style={{
          width: "100%",
          height: "100%"
        }}
      >
        <ZoomableGroup zoom={zoom} center={center}>
          <Geographies geography={WORLD_GEO_URL}>
            {({ geographies }) =>
              geographies.map(geo => {
                const isSelected = getGeoJsonName(selectedCountry) === geo.properties.NAME;
                const hasModel = countriesWithModels.some(
                  country => getGeoJsonName(country) === geo.properties.NAME
                );
                
                return (
                  <Geography
                    key={geo.rsmKey}
                    geography={geo}
                    fill={isSelected ? highlightColor : hasModel ? '#63B3ED' : fillColor}
                    stroke={borderColor}
                    strokeWidth={0.5}
                    style={{
                      default: {
                        outline: 'none',
                      },
                      hover: {
                        fill: isSelected ? highlightColor : '#90CDF4',
                        outline: 'none',
                        cursor: 'pointer'
                      },
                      pressed: {
                        outline: 'none',
                      },
                    }}
                    onMouseEnter={(evt) => handleMouseEnter(geo, evt)}
                    onMouseLeave={handleMouseLeave}
                    role="button"
                    tabIndex="0"
                    aria-label={`Pays: ${geo.properties.NAME}`}
                  />
                );
              })
            }
          </Geographies>
        </ZoomableGroup>
      </ComposableMap>
      
      {/* Tooltip */}
      {showTooltip && (
        <Box
          position="fixed"
          top={`${tooltipPosition.y + 10}px`}
          left={`${tooltipPosition.x + 10}px`}
          bg="white"
          p={2}
          borderRadius="md"
          boxShadow="md"
          zIndex={1000}
          _dark={{
            bg: "gray.700"
          }}
        >
          <Text fontSize="sm">{tooltipContent}</Text>
        </Box>
      )}
      
      {/* Légende */}
      <Box 
        position="absolute" 
        bottom={2} 
        left={2} 
        bg="white" 
        p={2} 
        borderRadius="md" 
        boxShadow="sm"
        fontSize="xs"
        _dark={{
          bg: "gray.700"
        }}
      >
        <Flex align="center" mb={1}>
          <Box w={3} h={3} bg={highlightColor} mr={2} borderRadius="sm" />
          <Text>Pays sélectionné</Text>
        </Flex>
        <Flex align="center">
          <Box w={3} h={3} bg="#63B3ED" mr={2} borderRadius="sm" />
          <Text>Pays avec modèles</Text>
        </Flex>
      </Box>
    </Box>
  );
};

export default WorldMap;
