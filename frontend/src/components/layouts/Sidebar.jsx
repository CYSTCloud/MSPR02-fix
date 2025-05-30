import React from 'react';
import { 
  Box, 
  CloseButton, 
  Flex, 
  Icon, 
  useColorModeValue, 
  Text, 
  Heading,
  VStack,
  Divider,
  Link as ChakraLink
} from '@chakra-ui/react';
import { Link as RouterLink, useLocation } from 'react-router-dom';
import { 
  FiHome, 
  FiTrendingUp, 
  FiCalendar, 
  FiBarChart2, 
  FiGlobe,
  FiInfo
} from 'react-icons/fi';

/**
 * Éléments de navigation pour le menu latéral
 */
const NavItems = [
  { 
    name: 'Tableau de bord', 
    icon: FiHome, 
    path: '/',
    description: 'Vue générale des statistiques COVID-19'
  },
  { 
    name: 'Données historiques', 
    icon: FiCalendar, 
    path: '/historical',
    description: 'Consulter les données historiques par pays'
  },
  { 
    name: 'Prédictions', 
    icon: FiTrendingUp, 
    path: '/predictions',
    description: 'Prévisions des cas COVID-19 à venir'
  },
  { 
    name: 'Comparaison de pays', 
    icon: FiGlobe, 
    path: '/compare',
    description: 'Comparer les statistiques entre différents pays'
  },
];

/**
 * Composant NavItem
 * Élément individuel du menu de navigation
 */
const NavItem = ({ icon, children, path, description, isActive, ...rest }) => {
  const activeBg = useColorModeValue('brand.50', 'brand.900');
  const activeColor = useColorModeValue('brand.700', 'brand.200');
  const inactiveColor = useColorModeValue('gray.600', 'gray.300');
  // Extraire le hook pour la couleur de la description au niveau supérieur
  const descriptionColor = useColorModeValue('gray.500', 'gray.400');

  return (
    <ChakraLink
      as={RouterLink}
      to={path}
      style={{ textDecoration: 'none' }}
      _focus={{ boxShadow: 'none' }}
    >
      <Flex
        align="center"
        p="4"
        mx="4"
        borderRadius="lg"
        role="group"
        cursor="pointer"
        bg={isActive ? activeBg : 'transparent'}
        color={isActive ? activeColor : inactiveColor}
        _hover={{
          bg: activeBg,
          color: activeColor,
        }}
        {...rest}
      >
        {icon && (
          <Icon
            mr="4"
            fontSize="16"
            _groupHover={{
              color: activeColor,
            }}
            as={icon}
          />
        )}
        <Box>
          {children}
          {/* Rendu conditionnel avec la variable déjà définie au niveau supérieur */}
          {description && (
            <Text 
              fontSize="xs" 
              display={{ base: 'none', lg: 'block' }}
              color={descriptionColor}
            >
              {description}
            </Text>
          )}
        </Box>
      </Flex>
    </ChakraLink>
  );
};

/**
 * Composant Sidebar
 * Menu latéral de navigation de l'application
 */
const Sidebar = ({ onClose, ...rest }) => {
  const location = useLocation();
  
  return (
    <Box
      transition="3s ease"
      bg={useColorModeValue('white', 'gray.800')}
      borderRight="1px"
      borderRightColor={useColorModeValue('gray.200', 'gray.700')}
      w={{ base: 'full', md: 60 }}
      pos="fixed"
      h="full"
      {...rest}
    >
      <Flex h="20" alignItems="center" mx="8" justifyContent="space-between">
        <Heading
          fontSize="xl"
          fontWeight="bold"
          color={useColorModeValue('brand.600', 'brand.400')}
        >
          EPIVIZ 4.1
        </Heading>
        <CloseButton display={{ base: 'flex', md: 'none' }} onClick={onClose} />
      </Flex>
      
      <VStack spacing={1} align="stretch" mt={6}>
        {NavItems.map((link) => (
          <NavItem 
            key={link.name} 
            icon={link.icon} 
            path={link.path}
            description={link.description}
            isActive={location.pathname === link.path || location.pathname.startsWith(`${link.path}/`)}
          >
            {link.name}
          </NavItem>
        ))}
      </VStack>
      
      <Divider my={6} borderColor={useColorModeValue('gray.200', 'gray.700')} />
      
      <Box mx={8} mb={4}>
        <Text fontSize="sm" color={useColorModeValue('gray.500', 'gray.400')}>
          Version 4.1.0
        </Text>
        <ChakraLink 
          as={RouterLink} 
          to="/about"
          color={useColorModeValue('brand.600', 'brand.400')}
          fontSize="sm"
          display="flex"
          alignItems="center"
          mt={2}
        >
          <Icon as={FiInfo} mr={2} />
          À propos
        </ChakraLink>
      </Box>
    </Box>
  );
};

export default Sidebar;
