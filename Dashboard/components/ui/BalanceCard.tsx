import React from 'react';
import { StyleSheet, View, Dimensions } from 'react-native';
import { ThemedText } from '@/components/ThemedText';
import { ThemedView } from '@/components/ThemedView';

// Get screen dimensions for responsive design
const { width } = Dimensions.get('window');

// Calculate card width based on screen size (2 cards per row with gap)
const cardWidth = (width - 48) / 2; // 16px padding on each side + 16px gap

interface BalanceCardProps {
  currency: string;
  balance: number;
  colorScheme: 'light' | 'dark';
}

export function BalanceCard({
  currency,
  balance,
  colorScheme,
}: BalanceCardProps) {
  // Get currency icon and color
  const getCurrencyDetails = (curr: string) => {
    const currUpper = curr.toUpperCase();
    switch (currUpper) {
      case 'BTC':
        return { icon: '₿', color: '#F7931A' };
      case 'ETH':
        return { icon: 'Ξ', color: '#627EEA' };
      case 'USDT':
        return { icon: '₮', color: '#26A17B' };
      case 'SOL':
        return { icon: 'S', color: '#00FFA3' };
      case 'XRP':
        return { icon: 'X', color: '#23292F' };
      case 'ADA':
        return { icon: 'A', color: '#0033AD' };
      default:
        return { icon: '$', color: '#888888' };
    }
  };

  const { icon, color } = getCurrencyDetails(currency);
  
  // Determine card background color based on theme
  const cardBgColor = colorScheme === 'dark' ? '#2D2D2D' : '#F8F8F8';

  return (
    <ThemedView style={[styles.card, { backgroundColor: cardBgColor, width: cardWidth }]}>
      <View style={styles.header}>
        <View style={[styles.iconContainer, { backgroundColor: color }]}>
          <ThemedText style={styles.icon}>{icon}</ThemedText>
        </View>
        <ThemedText style={styles.currency}>{currency}</ThemedText>
      </View>
      
      <ThemedText style={styles.balance}>
        {typeof balance === 'number' ? balance.toFixed(6) : balance}
      </ThemedText>
      
      <ThemedText style={styles.label}>Available Balance</ThemedText>
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
    alignItems: 'center',
    marginBottom: 12,
  },
  iconContainer: {
    width: 28,
    height: 28,
    borderRadius: 14,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 8,
  },
  icon: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: 'bold',
  },
  currency: {
    fontSize: 16,
    fontWeight: 'bold',
  },
  balance: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  label: {
    fontSize: 12,
    opacity: 0.6,
  },
});