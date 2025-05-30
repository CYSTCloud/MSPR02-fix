import React, { useState } from 'react';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer,
  Brush
} from 'recharts';
import { 
  Box, 
  Flex, 
  ButtonGroup, 
  Button, 
  Text, 
  useColorModeValue,
  VisuallyHidden
} from '@chakra-ui/react';

/**
 * Composant OverviewChart
 * Affiche un graphique d'évolution des cas COVID-19 pour un pays
 * 
 * @param {Object} props - Propriétés du composant
 * @param {Array} props.data - Données historiques à afficher
 * @returns {JSX.Element} Graphique d'évolution
 */
const OverviewChart = ({ data = [] }) => {
  const [metric, setMetric] = useState('new_cases');
  const [timeRange, setTimeRange] = useState('all');
  
  const lineColor = useColorModeValue('brand.600', 'brand.400');
  const gridColor = useColorModeValue('gray.200', 'gray.600');
  
  // Préparer les données pour le graphique
  const prepareChartData = () => {
    if (!data || data.length === 0) return [];
    
    // Trier les données par date
    const sortedData = [...data].sort((a, b) => new Date(a.date) - new Date(b.date));
    
    // Filtrer les données selon la plage de temps sélectionnée
    let filteredData = sortedData;
    if (timeRange !== 'all') {
      const today = new Date();
      const pastDate = new Date();
      
      switch (timeRange) {
        case '30d':
          pastDate.setDate(today.getDate() - 30);
          break;
        case '90d':
          pastDate.setDate(today.getDate() - 90);
          break;
        case '180d':
          pastDate.setDate(today.getDate() - 180);
          break;
        default:
          break;
      }
      
      filteredData = sortedData.filter(item => new Date(item.date) >= pastDate);
    }
    
    // Formater les données pour le graphique
    return filteredData.map(item => ({
      date: new Date(item.date).toLocaleDateString(),
      [metric]: item[metric] || 0,
      fullDate: item.date
    }));
  };
  
  const chartData = prepareChartData();
  
  // Déterminer les labels et couleurs en fonction de la métrique sélectionnée
  const getMetricConfig = () => {
    switch (metric) {
      case 'new_cases':
        return { 
          label: 'Nouveaux Cas', 
          color: 'dataViz.confirmed',
          labelId: 'new-cases-label'
        };
      case 'total_cases':
        return { 
          label: 'Cas Totaux', 
          color: 'dataViz.country1',
          labelId: 'total-cases-label'
        };
      case 'new_deaths':
        return { 
          label: 'Nouveaux Décès', 
          color: 'dataViz.deaths',
          labelId: 'new-deaths-label'
        };
      case 'total_deaths':
        return { 
          label: 'Décès Totaux', 
          color: 'dataViz.country2',
          labelId: 'total-deaths-label'
        };
      default:
        return { 
          label: 'Nouveaux Cas', 
          color: 'dataViz.confirmed',
          labelId: 'default-label'
        };
    }
  };
  
  const metricConfig = getMetricConfig();
  
  // Formatter personnalisé pour le tooltip
  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <Box
          bg="white"
          p={2}
          borderRadius="md"
          boxShadow="md"
          border="1px solid"
          borderColor="gray.200"
          _dark={{
            bg: "gray.700",
            borderColor: "gray.600"
          }}
        >
          <Text fontWeight="bold">{label}</Text>
          <Text color={metricConfig.color}>
            {metricConfig.label}: {payload[0].value.toLocaleString()}
          </Text>
        </Box>
      );
    }
    return null;
  };
  
  return (
    <Box height="100%">
      {/* Contrôles du graphique */}
      <Flex justifyContent="space-between" mb={4} flexWrap="wrap">
        <ButtonGroup size="sm" isAttached variant="outline" mb={2}>
          <Button
            onClick={() => setMetric('new_cases')}
            colorScheme={metric === 'new_cases' ? 'blue' : 'gray'}
            aria-pressed={metric === 'new_cases'}
          >
            Nouveaux Cas
          </Button>
          <Button
            onClick={() => setMetric('total_cases')}
            colorScheme={metric === 'total_cases' ? 'blue' : 'gray'}
            aria-pressed={metric === 'total_cases'}
          >
            Cas Totaux
          </Button>
          <Button
            onClick={() => setMetric('new_deaths')}
            colorScheme={metric === 'new_deaths' ? 'blue' : 'gray'}
            aria-pressed={metric === 'new_deaths'}
          >
            Nouveaux Décès
          </Button>
          <Button
            onClick={() => setMetric('total_deaths')}
            colorScheme={metric === 'total_deaths' ? 'blue' : 'gray'}
            aria-pressed={metric === 'total_deaths'}
          >
            Décès Totaux
          </Button>
        </ButtonGroup>
        
        <ButtonGroup size="sm" isAttached variant="outline">
          <Button
            onClick={() => setTimeRange('30d')}
            colorScheme={timeRange === '30d' ? 'blue' : 'gray'}
            aria-pressed={timeRange === '30d'}
          >
            30 jours
          </Button>
          <Button
            onClick={() => setTimeRange('90d')}
            colorScheme={timeRange === '90d' ? 'blue' : 'gray'}
            aria-pressed={timeRange === '90d'}
          >
            90 jours
          </Button>
          <Button
            onClick={() => setTimeRange('180d')}
            colorScheme={timeRange === '180d' ? 'blue' : 'gray'}
            aria-pressed={timeRange === '180d'}
          >
            180 jours
          </Button>
          <Button
            onClick={() => setTimeRange('all')}
            colorScheme={timeRange === 'all' ? 'blue' : 'gray'}
            aria-pressed={timeRange === 'all'}
          >
            Tout
          </Button>
        </ButtonGroup>
      </Flex>
      
      {/* Label accessible pour l'écran de lecteur */}
      <VisuallyHidden id={metricConfig.labelId}>
        Graphique d'évolution des {metricConfig.label} au fil du temps
      </VisuallyHidden>
      
      {/* Graphique */}
      <Box height="calc(100% - 50px)">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart
            data={chartData}
            margin={{
              top: 5,
              right: 30,
              left: 20,
              bottom: 5,
            }}
            aria-labelledby={metricConfig.labelId}
          >
            <CartesianGrid strokeDasharray="3 3" stroke={gridColor} />
            <XAxis 
              dataKey="date" 
              tick={{ fontSize: 12 }}
              tickFormatter={(value) => {
                // Formater la date de manière plus concise pour éviter l'encombrement
                const dateParts = value.split('/');
                return `${dateParts[1]}/${dateParts[0]}`;
              }}
            />
            <YAxis 
              tick={{ fontSize: 12 }}
              tickFormatter={(value) => {
                // Formater les grands nombres
                return value >= 1000 ? `${(value / 1000).toFixed(0)}k` : value;
              }}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            <Line
              type="monotone"
              dataKey={metric}
              stroke={lineColor}
              activeDot={{ r: 8 }}
              name={metricConfig.label}
              strokeWidth={2}
            />
            {chartData.length > 30 && (
              <Brush 
                dataKey="date" 
                height={30} 
                stroke={lineColor}
                startIndex={Math.max(0, chartData.length - 30)}
              />
            )}
          </LineChart>
        </ResponsiveContainer>
      </Box>
    </Box>
  );
};

export default OverviewChart;
