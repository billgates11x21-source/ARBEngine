import React from 'react';
import { StyleSheet, View, Dimensions } from 'react-native';
import { ThemedText } from '@/components/ThemedText';
import { ThemedView } from '@/components/ThemedView';

// Get screen dimensions for responsive design
const { width } = Dimensions.get('window');

interface ProfitChartProps {
  profit: number;
  colorScheme: 'light' | 'dark';
}

export function ProfitChart({
  profit,
  colorScheme,
}: ProfitChartProps) {
  // Generate some fake historical data for the chart
  const generateHistoricalData = () => {
    const data = [];
    let currentProfit = profit * 0.7; // Start at 70% of current profit
    
    for (let i = 0; i < 24; i++) {
      // Add some random variation
      const change = (Math.random() - 0.45) * (profit * 0.05);
      currentProfit += change;
      data.push(currentProfit);
    }
    
    // Ensure the last point is the current profit
    data[data.length - 1] = profit;
    
    return data;
  };
  
  const historicalData = generateHistoricalData();
  
  // Find min and max for scaling
  const minValue = Math.min(...historicalData);
  const maxValue = Math.max(...historicalData);
  const range = maxValue - minValue;
  
  // Calculate chart dimensions
  const chartWidth = width - 32; // 16px padding on each side
  const chartHeight = 120;
  const barWidth = (chartWidth - (historicalData.length - 1) * 2) / historicalData.length;
  
  // Determine colors based on profit and theme
  const profitColor = profit >= 0 ? '#4CAF50' : '#F44336';
  const chartBgColor = colorScheme === 'dark' ? '#2D2D2D' : '#F8F8F8';
  
  // Format profit with 6 decimal places and + sign for positive values
  const formattedProfit = profit >= 0 
    ? `+${profit.toFixed(6)}` 
    : profit.toFixed(6);

  return (
    <ThemedView style={[styles.container, { backgroundColor: chartBgColor }]}>
      <View style={styles.header}>
        <ThemedText style={styles.label}>Total Profit (USDT)</ThemedText>
        <ThemedText style={[styles.profitValue, { color: profitColor }]}>
          {formattedProfit}
        </ThemedText>
      </View>
      
      <View style={styles.chartContainer}>
        {historicalData.map((value, index) => {
          // Calculate bar height as percentage of chart height
          const normalizedValue = range === 0 
            ? 0.5 // If all values are the same, show half-height bars
            : (value - minValue) / range;
          const barHeight = Math.max(4, normalizedValue * chartHeight);
          
          return (
            <View 
              key={index}
              style={[
                styles.bar,
                {
                  height: barHeight,
                  width: barWidth,
                  backgroundColor: value >= 0 ? profitColor : '#F44336',
                  marginRight: index < historicalData.length - 1 ? 2 : 0,
                }
              ]}
            />
          );
        })}
      </View>
      
      <View style={styles.timeLabels}>
        <ThemedText style={styles.timeLabel}>24h ago</ThemedText>
        <ThemedText style={styles.timeLabel}>12h ago</ThemedText>
        <ThemedText style={styles.timeLabel}>Now</ThemedText>
      </View>
    </ThemedView>
  );
}

const styles = StyleSheet.create({
  container: {
    borderRadius: 12,
    padding: 16,
    marginTop: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  label: {
    fontSize: 14,
    opacity: 0.7,
  },
  profitValue: {
    fontSize: 18,
    fontWeight: 'bold',
  },
  chartContainer: {
    height: 120,
    flexDirection: 'row',
    alignItems: 'flex-end',
    marginBottom: 8,
  },
  bar: {
    borderTopLeftRadius: 2,
    borderTopRightRadius: 2,
  },
  timeLabels: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 4,
  },
  timeLabel: {
    fontSize: 12,
    opacity: 0.6,
  },
});