import React, { useState } from 'react';
import {
  Box,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Button,
  Flex,
  Select,
  Input,
  HStack,
  Text,
  useColorModeValue,
  IconButton,
  Tooltip
} from '@chakra-ui/react';
import { FiDownload, FiSearch, FiFilter, FiChevronLeft, FiChevronRight } from 'react-icons/fi';

/**
 * Composant ExportableDataTable
 * Tableau de données avec fonctionnalités de pagination, filtrage et exportation
 * 
 * @param {Object} props - Propriétés du composant
 * @param {Array} props.data - Données à afficher dans le tableau
 * @param {Array} props.columns - Configuration des colonnes
 * @param {string} props.filename - Nom du fichier lors de l'exportation
 * @returns {JSX.Element} Tableau de données exportable
 */
const ExportableDataTable = ({ data = [], columns = [], filename = 'data-export' }) => {
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortField, setSortField] = useState('');
  const [sortDirection, setSortDirection] = useState('asc');
  
  // Couleurs thématiques
  const tableBorderColor = useColorModeValue('gray.200', 'gray.600');
  const headerBg = useColorModeValue('gray.50', 'gray.700');
  
  // Filtrer les données en fonction du terme de recherche
  const filteredData = data.filter(item => {
    if (!searchTerm) return true;
    
    return columns.some(column => {
      const value = item[column.accessor];
      if (typeof value === 'string') {
        return value.toLowerCase().includes(searchTerm.toLowerCase());
      }
      if (typeof value === 'number') {
        return value.toString().includes(searchTerm);
      }
      return false;
    });
  });
  
  // Tri des données
  const sortedData = [...filteredData].sort((a, b) => {
    if (!sortField) return 0;
    
    const aValue = a[sortField];
    const bValue = b[sortField];
    
    if (typeof aValue === 'string' && typeof bValue === 'string') {
      return sortDirection === 'asc' 
        ? aValue.localeCompare(bValue) 
        : bValue.localeCompare(aValue);
    }
    
    if (typeof aValue === 'number' && typeof bValue === 'number') {
      return sortDirection === 'asc' ? aValue - bValue : bValue - aValue;
    }
    
    return 0;
  });
  
  // Pagination
  const totalPages = Math.ceil(sortedData.length / pageSize);
  const startIndex = (currentPage - 1) * pageSize;
  const paginatedData = sortedData.slice(startIndex, startIndex + pageSize);
  
  // Gérer le tri des colonnes
  const handleSort = (accessor) => {
    if (sortField === accessor) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(accessor);
      setSortDirection('asc');
    }
  };
  
  // Exportation des données au format CSV
  const exportToCSV = () => {
    // Préparer les en-têtes des colonnes
    const headers = columns.map(column => column.Header);
    const headerRow = headers.join(',');
    
    // Préparer les lignes de données
    const dataRows = sortedData.map(item => {
      return columns.map(column => {
        const value = item[column.accessor];
        
        // Gérer les valeurs qui pourraient contenir des virgules
        if (typeof value === 'string' && value.includes(',')) {
          return `"${value}"`;
        }
        
        return value;
      }).join(',');
    });
    
    // Combiner les en-têtes et les données
    const csvContent = [headerRow, ...dataRows].join('\n');
    
    // Créer un Blob et un lien de téléchargement
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    
    link.setAttribute('href', url);
    link.setAttribute('download', `${filename}-${new Date().toISOString().split('T')[0]}.csv`);
    link.style.visibility = 'hidden';
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };
  
  return (
    <Box>
      {/* Contrôles du tableau */}
      <Flex 
        justify="space-between" 
        align="center" 
        mb={4} 
        flexDir={{ base: 'column', md: 'row' }}
        gap={2}
      >
        <HStack>
          <Tooltip label="Rechercher dans toutes les colonnes">
            <Box position="relative">
              <Input
                placeholder="Rechercher..."
                value={searchTerm}
                onChange={e => setSearchTerm(e.target.value)}
                pr="2.5rem"
                width={{ base: '100%', md: '250px' }}
              />
              <Box position="absolute" right="0.5rem" top="50%" transform="translateY(-50%)">
                <FiSearch />
              </Box>
            </Box>
          </Tooltip>
        </HStack>
        
        <HStack>
          <Select 
            value={pageSize} 
            onChange={e => setPageSize(Number(e.target.value))}
            size="sm"
            width="100px"
            aria-label="Lignes par page"
          >
            <option value={5}>5 lignes</option>
            <option value={10}>10 lignes</option>
            <option value={20}>20 lignes</option>
            <option value={50}>50 lignes</option>
          </Select>
          
          <Tooltip label="Exporter au format CSV">
            <Button
              leftIcon={<FiDownload />}
              colorScheme="blue"
              size="sm"
              onClick={exportToCSV}
              aria-label="Exporter les données"
            >
              Exporter
            </Button>
          </Tooltip>
        </HStack>
      </Flex>
      
      {/* Tableau de données */}
      <Box overflowX="auto">
        <Table variant="simple" size="sm" borderWidth="1px" borderColor={tableBorderColor}>
          <Thead bg={headerBg}>
            <Tr>
              {columns.map(column => (
                <Th 
                  key={column.accessor}
                  onClick={() => handleSort(column.accessor)}
                  cursor="pointer"
                  position="relative"
                  paddingRight="8"
                  textAlign={column.isNumeric ? 'right' : 'left'}
                >
                  {column.Header}
                  {sortField === column.accessor && (
                    <Text as="span" position="absolute" right="2" top="50%" transform="translateY(-50%)">
                      {sortDirection === 'asc' ? '↑' : '↓'}
                    </Text>
                  )}
                </Th>
              ))}
            </Tr>
          </Thead>
          <Tbody>
            {paginatedData.length > 0 ? (
              paginatedData.map((item, index) => (
                <Tr key={index}>
                  {columns.map(column => (
                    <Td 
                      key={`${index}-${column.accessor}`}
                      isNumeric={column.isNumeric}
                    >
                      {column.Cell ? column.Cell(item) : item[column.accessor]}
                    </Td>
                  ))}
                </Tr>
              ))
            ) : (
              <Tr>
                <Td colSpan={columns.length} textAlign="center" py={4}>
                  Aucune donnée disponible
                </Td>
              </Tr>
            )}
          </Tbody>
        </Table>
      </Box>
      
      {/* Pagination */}
      {totalPages > 1 && (
        <Flex justify="space-between" align="center" mt={4}>
          <Text fontSize="sm">
            Affichage de {startIndex + 1}-{Math.min(startIndex + pageSize, sortedData.length)} sur {sortedData.length} entrées
          </Text>
          
          <HStack>
            <IconButton
              icon={<FiChevronLeft />}
              onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
              isDisabled={currentPage === 1}
              aria-label="Page précédente"
              size="sm"
            />
            
            <Text fontSize="sm">
              Page {currentPage} sur {totalPages}
            </Text>
            
            <IconButton
              icon={<FiChevronRight />}
              onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
              isDisabled={currentPage === totalPages}
              aria-label="Page suivante"
              size="sm"
            />
          </HStack>
        </Flex>
      )}
    </Box>
  );
};

export default ExportableDataTable;
