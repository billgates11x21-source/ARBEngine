import React from 'react';
import { StyleSheet, View } from 'react-native';
import { ThemedText } from '@/components/ThemedText';
import { ThemedView } from '@/components/ThemedView';

interface SystemStatusCardProps {
  status: any;
  colorScheme: 'light' | 'dark';
}

export function SystemStatusCard({
  status,
  colorScheme,
}: SystemStatusCardProps) {
  // Determine card background color based on theme
  const cardBgColor = colorScheme === 'dark' ? '#2D2D2D' : '#F8F8F8';

  // Determine connection status colors
  const getStatusColor = (status: string) => {
    return status === 'Connected' ? '#4CAF50' : '#F44336';
  };

  return (
    <ThemedView style={[styles.card, { backgroundColor: cardBgColor }]}>
      <ThemedText style={styles.title}>System Status</ThemedText>
      
      <View style={styles.divider} />
      
      <ThemedText style={styles.sectionTitle}>OKX Connections</ThemedText>
      
      {status?.okx_connections ? (
        <>
          <View style={styles.statusRow}>
            <ThemedText style={styles.statusLabel}>Public WebSocket:</ThemedText>
            <View style={styles.statusValueContainer}>
              <View 
                style={[
                  styles.statusIndicator, 
                  { backgroundColor: getStatusColor(status.okx_connections.public_ws) }
                ]} 
              />
              <ThemedText style={styles.statusValue}>
                {status.okx_connections.public_ws}
              </ThemedText>
            </View>
          </View>
          
          <View style={styles.statusRow}>
            <ThemedText style={styles.statusLabel}>Private WebSocket:</ThemedText>
            <View style={styles.statusValueContainer}>
              <View 
                style={[
                  styles.statusIndicator, 
                  { backgroundColor: getStatusColor(status.okx_connections.private_ws) }
                ]} 
              />
              <ThemedText style={styles.statusValue}>
                {status.okx_connections.private_ws}
              </ThemedText>
            </View>
          </View>
          
          <View style={styles.statusRow}>
            <ThemedText style={styles.statusLabel}>REST API:</ThemedText>
            <View style={styles.statusValueContainer}>
              <View 
                style={[
                  styles.statusIndicator, 
                  { backgroundColor: getStatusColor(status.okx_connections.rest_api) }
                ]} 
              />
              <ThemedText style={styles.statusValue}>
                {status.okx_connections.rest_api}
              </ThemedText>
            </View>
          </View>
          
          <View style={styles.statusRow}>
            <ThemedText style={styles.statusLabel}>Last Check:</ThemedText>
            <ThemedText style={styles.statusValue}>
              {status.okx_connections.last_check}
            </ThemedText>
          </View>
        </>
      ) : (
        <ThemedText style={styles.loadingText}>Loading connection status...</ThemedText>
      )}
      
      <View style={styles.divider} />
      
      <ThemedText style={styles.sectionTitle}>Strategy Orchestrator</ThemedText>
      
      {status?.orchestrator ? (
        <>
          <View style={styles.statusRow}>
            <ThemedText style={styles.statusLabel}>Running:</ThemedText>
            <View style={styles.statusValueContainer}>
              <View 
                style={[
                  styles.statusIndicator, 
                  { backgroundColor: status.orchestrator.running ? '#4CAF50' : '#F44336' }
                ]} 
              />
              <ThemedText style={styles.statusValue}>
                {status.orchestrator.running ? 'Yes' : 'No'}
              </ThemedText>
            </View>
          </View>
          
          <View style={styles.statusRow}>
            <ThemedText style={styles.statusLabel}>Active Strategies:</ThemedText>
            <ThemedText style={styles.statusValue}>
              {status.orchestrator.active_strategies} / {status.orchestrator.total_strategies}
            </ThemedText>
          </View>
        </>
      ) : (
        <ThemedText style={styles.loadingText}>Loading orchestrator status...</ThemedText>
      )}
      
      <View style={styles.divider} />
      
      <ThemedText style={styles.sectionTitle}>Error Statistics</ThemedText>
      
      {status?.errors ? (
        <>
          <View style={styles.statusRow}>
            <ThemedText style={styles.statusLabel}>Total Errors:</ThemedText>
            <ThemedText style={[
              styles.statusValue, 
              { color: status.errors.total_errors > 0 ? '#F44336' : '#4CAF50' }
            ]}>
              {status.errors.total_errors}
            </ThemedText>
          </View>
          
          {status.errors.total_errors > 0 && (
            <View style={styles.statusRow}>
              <ThemedText style={styles.statusLabel}>Error Types:</ThemedText>
              <ThemedText style={styles.statusValue}>
                {status.errors.error_types.length}
              </ThemedText>
            </View>
          )}
        </>
      ) : (
        <ThemedText style={styles.loadingText}>Loading error statistics...</ThemedText>
      )}
    </ThemedView>
  );
}

const styles = StyleSheet.create({
  card: {
    borderRadius: 12,
    padding: 16,
    marginTop: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  title: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 8,
  },
  divider: {
    height: 1,
    backgroundColor: '#E0E0E0',
    marginVertical: 12,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '500',
    marginBottom: 8,
  },
  statusRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  statusLabel: {
    fontSize: 14,
    opacity: 0.7,
  },
  statusValueContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  statusIndicator: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginRight: 6,
  },
  statusValue: {
    fontSize: 14,
    fontWeight: '500',
  },
  loadingText: {
    fontSize: 14,
    fontStyle: 'italic',
    opacity: 0.6,
    marginBottom: 8,
  },
});