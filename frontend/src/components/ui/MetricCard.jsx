import React from 'react';
import {
  Box,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  StatArrow,
  Flex,
  Icon,
  useColorModeValue
} from '@chakra-ui/react';
import { FiTrendingUp } from 'react-icons/fi';

/**
 * Composant MetricCard
 * Carte affichant une métrique importante avec un titre, une valeur et une évolution optionnelle
 * 
 * @param {Object} props - Propriétés du composant
 * @param {string} props.title - Titre de la métrique
 * @param {string|number} props.value - Valeur principale à afficher
 * @param {string} props.subtitle - Texte secondaire optionnel
 * @param {number} props.change - Pourcentage de changement (optionnel)
 * @param {React.ElementType} props.icon - Icône à afficher (optionnel)
 * @param {string} props.color - Couleur principale de la carte (optionnel)
 * @returns {JSX.Element} Carte de métrique
 */
const MetricCard = ({ title, value, subtitle, change, icon, color = 'blue.500' }) => {
  const bgColor = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const textColor = useColorModeValue('gray.600', 'gray.300');
  
  return (
    <Box
      p={5}
      bg={bgColor}
      borderRadius="lg"
      boxShadow="md"
      borderWidth="1px"
      borderColor={borderColor}
      transition="transform 0.3s"
      _hover={{ transform: 'translateY(-2px)', boxShadow: 'lg' }}
      role="group"
      aria-label={`Métrique: ${title}`}
    >
      <Flex justify="space-between" align="center">
        <Stat>
          <StatLabel color={textColor} fontSize="sm" fontWeight="medium">
            {title}
          </StatLabel>
          <StatNumber fontSize="2xl" fontWeight="bold" color={color}>
            {value}
          </StatNumber>
          
          {change !== undefined && (
            <StatHelpText>
              <StatArrow type={change >= 0 ? 'increase' : 'decrease'} />
              {Math.abs(change)}%
            </StatHelpText>
          )}
          
          {subtitle && (
            <StatHelpText fontSize="sm" color={textColor}>
              {subtitle}
            </StatHelpText>
          )}
        </Stat>
        
        {icon && (
          <Flex 
            w={12} 
            h={12} 
            align="center" 
            justify="center" 
            rounded="full" 
            bg={`${color}10`}
          >
            <Icon as={icon} color={color} boxSize={6} />
          </Flex>
        )}
      </Flex>
    </Box>
  );
};

export default MetricCard;
