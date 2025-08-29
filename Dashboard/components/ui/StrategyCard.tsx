import React from 'react';
import { StyleSheet, TouchableOpacity, View, Dimensions } from 'react-native';
import { ThemedText } from '@/components/ThemedText';
import { ThemedView } from '@/components/ThemedView';

// Get screen dimensions for responsive design
const { width } = Dimensions.get('window');

interface StrategyCardProps {
  name: string;
  description: string;
  active: boolean;
  profit24h: number;
  lastExecution: string | null;
  onToggle: () => void;
  colorScheme: 'light' | 'dark';
}

export function StrategyCard({
  name,
  description,
  active,
  profit24h,
  lastExecution,
  onToggle,
  colorScheme,
}: StrategyCardProps) {
  // Format the last execution time
  const formattedTime = lastExecution 
    ? new Date(lastExecution).toLocaleTimeString() 
    : 'Never';
  
  // Determine colors based on theme
  const cardBgColor = colorScheme === 'dark' 
    ? active ? '#2A4D3E' : '#3A3A3A' 
    : active ? '#E6F4EA' : '#F5F5F5';
  
  const statusColor = active ? '#4CAF50' : '#9E9E9E';
  
  const profitColor = profit24h > 0 
    ? '#4CAF50' 
    : profit24h < 0 
      ? '#F44336' 
      : colorScheme === 'dark' ? '#FFFFFF' : '#000000';

  return (
    <ThemedView style={[styles.card, { backgroundColor: cardBgColor }]}>
      <View style={styles.header}>
        <ThemedText type="subtitle" style={styles.name}>{name}</ThemedText>
        <View style={[styles.statusIndicator, { backgroundColor: statusColor }]} />
      </View>
      
      <ThemedText style={styles.description}>{description}</ThemedText>
      
      <View style={styles.statsContainer}>
        <View style={styles.statItem}>
          <ThemedText style={styles.statLabel}>24h Profit:</ThemedText>
          <ThemedText style={[styles.statValue, { color: profitColor }]}>
            {profit24h.toFixed(4)} USDT
          </ThemedText>
        </View>
        
        <View style={styles.statItem}>
          <ThemedText style={styles.statLabel}>Last Run:</ThemedText>
          <ThemedText style={styles.statValue}>{formattedTime}</ThemedText>
        </View>
      </View>
      
      <TouchableOpacity 
        style={[
          styles.toggleButton, 
          { backgroundColor: active ? '#F44336' : '#4CAF50' }
        ]}
        onPress={onToggle}
      >
        <ThemedText style={styles.toggleButtonText}>
          {active ? 'Stop' : 'Start'}
        </ThemedText>
      </TouchableOpacity>
    </ThemedView>
  );
}

const styles = StyleSheet.create({
  card: {
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
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
    marginBottom: 8,
  },
  name: {
    fontWeight: 'bold',
    fontSize: 18,
  },
  statusIndicator: {
    width: 12,
    height: 12,
    borderRadius: 6,
  },
  description: {
    marginBottom: 16,
    fontSize: 14,
    opacity: 0.8,
  },
  statsContainer: {
    marginBottom: 16,
  },
  statItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 4,
  },
  statLabel: {
    fontSize: 14,
    opacity: 0.7,
  },
  statValue: {
    fontSize: 14,
    fontWeight: '500',
  },
  toggleButton: {
    borderRadius: 8,
    paddingVertical: 8,
    paddingHorizontal: 16,
    alignItems: 'center',
  },
  toggleButtonText: {
    color: '#FFFFFF',
    fontWeight: 'bold',
  },
});