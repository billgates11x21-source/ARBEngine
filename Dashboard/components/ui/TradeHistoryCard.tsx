import React from 'react';
import { StyleSheet, View } from 'react-native';
import { ThemedText } from '@/components/ThemedText';
import { ThemedView } from '@/components/ThemedView';

interface TradeHistoryCardProps {
  trade: any;
  colorScheme: 'light' | 'dark';
}

export function TradeHistoryCard({
  trade,
  colorScheme,
}: TradeHistoryCardProps) {
  // Format timestamp if available
  const formattedTime = trade.timestamp 
    ? new Date(trade.timestamp * 1000).toLocaleString()
    : 'Unknown time';
  
  // Determine profit color
  const profitColor = trade.profit > 0 
    ? '#4CAF50' 
    : trade.profit < 0 
      ? '#F44336' 
      : colorScheme === 'dark' ? '#FFFFFF' : '#000000';
  
  // Determine card background color based on theme
  const cardBgColor = colorScheme === 'dark' ? '#2D2D2D' : '#F8F8F8';

  return (
    <ThemedView style={[styles.card, { backgroundColor: cardBgColor }]}>
      <View style={styles.header}>
        <ThemedText style={styles.title}>Trade Details</ThemedText>
        <ThemedText style={styles.timestamp}>{formattedTime}</ThemedText>
      </View>
      
      <View style={styles.divider} />
      
      {trade.token && (
        <View style={styles.detailRow}>
          <ThemedText style={styles.detailLabel}>Token:</ThemedText>
          <ThemedText style={styles.detailValue}>{trade.token}</ThemedText>
        </View>
      )}
      
      {trade.pair && (
        <View style={styles.detailRow}>
          <ThemedText style={styles.detailLabel}>Trading Pair:</ThemedText>
          <ThemedText style={styles.detailValue}>{trade.pair}</ThemedText>
        </View>
      )}
      
      {trade.strategy && (
        <View style={styles.detailRow}>
          <ThemedText style={styles.detailLabel}>Strategy:</ThemedText>
          <ThemedText style={styles.detailValue}>{trade.strategy}</ThemedText>
        </View>
      )}
      
      {trade.action && (
        <View style={styles.detailRow}>
          <ThemedText style={styles.detailLabel}>Action:</ThemedText>
          <ThemedText style={styles.detailValue}>{trade.action}</ThemedText>
        </View>
      )}
      
      {trade.side && (
        <View style={styles.detailRow}>
          <ThemedText style={styles.detailLabel}>Side:</ThemedText>
          <ThemedText style={[
            styles.detailValue, 
            { color: trade.side === 'buy' ? '#4CAF50' : '#F44336' }
          ]}>
            {trade.side.toUpperCase()}
          </ThemedText>
        </View>
      )}
      
      {trade.price !== undefined && (
        <View style={styles.detailRow}>
          <ThemedText style={styles.detailLabel}>Price:</ThemedText>
          <ThemedText style={styles.detailValue}>{trade.price}</ThemedText>
        </View>
      )}
      
      {trade.quantity !== undefined && (
        <View style={styles.detailRow}>
          <ThemedText style={styles.detailLabel}>Quantity:</ThemedText>
          <ThemedText style={styles.detailValue}>{trade.quantity}</ThemedText>
        </View>
      )}
      
      {trade.profit !== undefined && (
        <View style={styles.detailRow}>
          <ThemedText style={styles.detailLabel}>Profit:</ThemedText>
          <ThemedText style={[styles.detailValue, { color: profitColor, fontWeight: 'bold' }]}>
            {trade.profit > 0 ? '+' : ''}{typeof trade.profit === 'number' ? trade.profit.toFixed(6) : trade.profit} USDT
          </ThemedText>
        </View>
      )}
      
      {/* Display any other available trade details */}
      {Object.entries(trade).map(([key, value]) => {
        // Skip already displayed fields and non-displayable fields
        if (['token', 'pair', 'strategy', 'action', 'side', 'price', 'quantity', 'profit', 'timestamp'].includes(key) || 
            typeof value === 'object' || typeof value === 'function') {
          return null;
        }
        
        return (
          <View key={key} style={styles.detailRow}>
            <ThemedText style={styles.detailLabel}>{key.charAt(0).toUpperCase() + key.slice(1)}:</ThemedText>
            <ThemedText style={styles.detailValue}>{String(value)}</ThemedText>
          </View>
        );
      })}
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
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  title: {
    fontSize: 16,
    fontWeight: 'bold',
  },
  timestamp: {
    fontSize: 12,
    opacity: 0.6,
  },
  divider: {
    height: 1,
    backgroundColor: '#E0E0E0',
    marginBottom: 12,
  },
  detailRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  detailLabel: {
    fontSize: 14,
    opacity: 0.7,
  },
  detailValue: {
    fontSize: 14,
    fontWeight: '500',
  },
});