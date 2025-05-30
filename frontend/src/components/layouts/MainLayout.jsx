import React from 'react';
import { 
  Box, 
  Flex, 
  useColorModeValue, 
  Drawer, 
  DrawerContent, 
  useDisclosure 
} from '@chakra-ui/react';
import Sidebar from './Sidebar';
import Navbar from './Navbar';

/**
 * Composant MainLayout
 * Layout principal de l'application comprenant la barre de navigation, 
 * le menu latéral et le contenu principal
 * 
 * @param {Object} props - Propriétés du composant
 * @param {boolean} props.isOpen - État d'ouverture du menu latéral (responsive)
 * @param {Function} props.onOpen - Fonction pour ouvrir le menu latéral
 * @param {Function} props.onClose - Fonction pour fermer le menu latéral
 * @param {React.ReactNode} props.children - Contenu principal de la page
 * @returns {JSX.Element} Layout principal
 */
const MainLayout = ({ isOpen, onOpen, onClose, children }) => {
  const bgColor = useColorModeValue('gray.50', 'gray.900');
  const sidebarBgColor = useColorModeValue('white', 'gray.800');

  return (
    <Box minH="100vh" bg={bgColor}>
      {/* Menu latéral pour desktop */}
      <Sidebar
        display={{ base: 'none', md: 'block' }}
        onClose={() => onClose}
        bg={sidebarBgColor}
      />
      
      {/* Menu latéral pour mobile (drawer) */}
      <Drawer
        autoFocus={false}
        isOpen={isOpen}
        placement="left"
        onClose={onClose}
        returnFocusOnClose={false}
        onOverlayClick={onClose}
        size="full"
      >
        <DrawerContent>
          <Sidebar onClose={onClose} bg={sidebarBgColor} />
        </DrawerContent>
      </Drawer>
      
      {/* Contenu principal */}
      <Box ml={{ base: 0, md: 60 }} transition=".3s ease">
        {/* Barre de navigation supérieure */}
        <Navbar onOpen={onOpen} />
        
        {/* Contenu de la page */}
        <Box as="main" p="4">
          {/* Breadcrumb ici si nécessaire */}
          
          {/* Contenu principal */}
          <Box borderRadius="lg" p={4}>
            {children}
          </Box>
        </Box>
      </Box>
    </Box>
  );
};

export default MainLayout;
