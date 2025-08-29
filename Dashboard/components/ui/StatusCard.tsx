import React from 'react';
import { StyleSheet, View } from 'react-native';
import { ThemedText } from '@/components/ThemedText';
import { ThemedView } from '@/components/ThemedView';

interface StatusCardProps {
  title: string;
  status: string;
  statusColor: string;
  description: string;
  colorScheme: 'light' | 'dark';
}

export function StatusCard({
  title,
  status,
  statusColor,
  description,
  colorScheme,
}: StatusCardProps) {
  // Determine card background color based on theme
  const cardBgColor = colorScheme === 'dark' ? '#2D2D2D' : '#F8F8F8';

  return (
    <ThemedView style={[styles.card, { backgroundColor: cardBgColor }]}>
      <View style={styles.header}>
        <ThemedText style={styles.title}>{title}</ThemedText>
        <View style={styles.statusContainer}>
          <View style={[styles.statusIndicator, { backgroundColor: statusColor }]} />
          <ThemedText style={[styles.statusText, { color: statusColor }]}>
            {status}
          </ThemedText>
        </View>
      </View>
      
      <ThemedText style={styles.description}>{description}</ThemedText>
    </ThemedView>
  );
}

const styles = StyleSheet.create({
  card: {
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
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
  title: {
    fontSize: 16,
    fontWeight: 'bold',
  },
  statusContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  statusIndicator: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginRight: 6,
  },
  statusText: {
    fontSize: 14,
    fontWeight: '500',
  },
  description: {
    fontSize: 14,
    opacity: 0.7,
  },
});