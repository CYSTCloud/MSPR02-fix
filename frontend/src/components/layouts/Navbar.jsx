import React from 'react';
import {
  IconButton,
  Avatar,
  Box,
  Flex,
  HStack,
  VStack,
  useColorModeValue,
  Text,
  Menu,
  MenuButton,
  MenuDivider,
  MenuItem,
  MenuList,
  useColorMode,
  Button,
  Badge,
  Tooltip,
  InputGroup,
  InputLeftElement,
  Input
} from '@chakra-ui/react';
import {
  FiMenu,
  FiChevronDown,
  FiSun,
  FiMoon,
  FiSearch,
  FiBell,
  FiHelpCircle
} from 'react-icons/fi';

/**
 * Composant Navbar
 * Barre de navigation supérieure de l'application
 * 
 * @param {Object} props - Propriétés du composant
 * @param {Function} props.onOpen - Fonction pour ouvrir le menu latéral en mode responsive
 * @returns {JSX.Element} Barre de navigation
 */
const Navbar = ({ onOpen, ...rest }) => {
  const { colorMode, toggleColorMode } = useColorMode();
  
  return (
    <Flex
      ml={{ base: 0, md: 60 }}
      px={{ base: 4, md: 4 }}
      height="20"
      alignItems="center"
      bg={useColorModeValue('white', 'gray.800')}
      borderBottomWidth="1px"
      borderBottomColor={useColorModeValue('gray.200', 'gray.700')}
      justifyContent={{ base: 'space-between', md: 'flex-end' }}
      {...rest}
    >
      {/* Bouton menu hamburger pour mobile */}
      <IconButton
        display={{ base: 'flex', md: 'none' }}
        onClick={onOpen}
        variant="outline"
        aria-label="Ouvrir le menu"
        icon={<FiMenu />}
      />
      
      {/* Logo pour mobile uniquement */}
      <Text
        display={{ base: 'flex', md: 'none' }}
        fontSize="2xl"
        fontWeight="bold"
        color={useColorModeValue('brand.600', 'brand.400')}
      >
        EPIVIZ
      </Text>
      
      {/* Barre de recherche */}
      <InputGroup maxW="400px" display={{ base: 'none', md: 'flex' }} mr="auto" ml={6}>
        <InputLeftElement pointerEvents="none">
          <FiSearch color="gray.300" />
        </InputLeftElement>
        <Input 
          placeholder="Rechercher un pays..." 
          variant="filled"
          bg={useColorModeValue('gray.100', 'gray.700')}
          _hover={{ bg: useColorModeValue('gray.200', 'gray.600') }}
          aria-label="Rechercher un pays"
        />
      </InputGroup>
      
      {/* Menu utilisateur et actions */}
      <HStack spacing={{ base: '0', md: '6' }}>
        {/* Bouton thème clair/sombre */}
        <Button onClick={toggleColorMode} size="sm" variant="ghost">
          {colorMode === 'light' ? <FiMoon /> : <FiSun />}
        </Button>
        
        {/* Bouton d'aide */}
        <Tooltip label="Aide et documentation" hasArrow>
          <IconButton
            size="lg"
            variant="ghost"
            aria-label="Ouvrir l'aide"
            icon={<FiHelpCircle />}
          />
        </Tooltip>
        
        {/* Notifications */}
        <Tooltip label="Notifications" hasArrow>
          <Box position="relative">
            <IconButton
              size="lg"
              variant="ghost"
              aria-label="Voir les notifications"
              icon={<FiBell />}
            />
            <Badge
              position="absolute"
              top="0"
              right="0"
              colorScheme="red"
              borderRadius="full"
              transform="translate(25%, -25%)"
            >
              3
            </Badge>
          </Box>
        </Tooltip>
        
        {/* Menu profil */}
        <Flex alignItems="center">
          <Menu>
            <MenuButton
              py={2}
              transition="all 0.3s"
              _focus={{ boxShadow: 'none' }}
            >
              <HStack spacing="4">
                <Avatar
                  size="sm"
                  src={null}
                  name="Utilisateur OMS"
                  bg="brand.500"
                  color="white"
                />
                <VStack
                  display={{ base: 'none', md: 'flex' }}
                  alignItems="flex-start"
                  spacing="1px"
                  ml="2"
                >
                  <Text fontSize="sm">Utilisateur OMS</Text>
                  <Text fontSize="xs" color="gray.600" _dark={{ color: 'gray.400' }}>
                    Analyste
                  </Text>
                </VStack>
                <Box display={{ base: 'none', md: 'flex' }}>
                  <FiChevronDown />
                </Box>
              </HStack>
            </MenuButton>
            <MenuList
              bg={useColorModeValue('white', 'gray.800')}
              borderColor={useColorModeValue('gray.200', 'gray.700')}
            >
              <MenuItem>Profil</MenuItem>
              <MenuItem>Paramètres</MenuItem>
              <MenuDivider />
              <MenuItem>Déconnexion</MenuItem>
            </MenuList>
          </Menu>
        </Flex>
      </HStack>
    </Flex>
  );
};

export default Navbar;
