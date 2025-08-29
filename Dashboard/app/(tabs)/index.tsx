import React from 'react';
import { Image } from 'expo-image';
import { StyleSheet, Dimensions, View } from 'react-native';
import { useColorScheme } from '@/hooks/useColorScheme';

import { HelloWave } from '@/components/HelloWave';
import ParallaxScrollView from '@/components/ParallaxScrollView';
import { ThemedText } from '@/components/ThemedText';
import { ThemedView } from '@/components/ThemedView';
import { StatusCard } from '@/components/ui/StatusCard';

// Get screen dimensions for responsive design
const { width } = Dimensions.get('window');

export default function HomeScreen() {
  const colorScheme = useColorScheme();
  
  return (
    <ParallaxScrollView
      headerBackgroundColor={{ light: '#A1CEDC', dark: '#1D3D47' }}
      headerImage={
        <Image
          source={require('@/assets/images/partial-react-logo.png')}
          style={styles.reactLogo}
        />
      }>
      <ThemedView style={styles.container}>
        <ThemedView style={styles.titleContainer}>
          <ThemedText type="title">ARBengine Dashboard</ThemedText>
          <HelloWave />
        </ThemedView>
        
        <ThemedView style={styles.statusContainer}>
          <StatusCard
            title="System Status"
            status="Online"
            statusColor="#4CAF50"
            description="All systems operational"
            colorScheme={colorScheme}
          />
          
          <StatusCard
            title="API Connection"
            status="Connected"
            statusColor="#4CAF50"
            description="OKX API connected and authenticated"
            colorScheme={colorScheme}
          />
          
          <StatusCard
            title="Trading Status"
            status="Active"
            statusColor="#4CAF50"
            description="Automated trading enabled"
            colorScheme={colorScheme}
          />
        </ThemedView>
        
        <ThemedView style={styles.infoContainer}>
          <ThemedText type="subtitle">Trading Dashboard</ThemedText>
          <ThemedText style={styles.description}>
            Welcome to your OKX trading dashboard. This platform provides automated trading strategies
            optimized for maximum profit with your OKX account. The system is currently running with
            5 different spot wallet trading strategies.
          </ThemedText>
          
          <ThemedText type="subtitle" style={styles.featuresTitle}>Key Features</ThemedText>
          <ThemedView style={styles.featureItem}>
            <ThemedText style={styles.featureBullet}>•</ThemedText>
            <ThemedText style={styles.featureText}>
              <ThemedText style={styles.bold}>Automated Trading:</ThemedText> All strategies run automatically without requiring user input
            </ThemedText>
          </ThemedView>
          
          <ThemedView style={styles.featureItem}>
            <ThemedText style={styles.featureBullet}>•</ThemedText>
            <ThemedText style={styles.featureText}>
              <ThemedText style={styles.bold}>Multiple Strategies:</ThemedText> 5 different spot trading strategies working simultaneously
            </ThemedText>
          </ThemedView>
          
          <ThemedView style={styles.featureItem}>
            <ThemedText style={styles.featureBullet}>•</ThemedText>
            <ThemedText style={styles.featureText}>
              <ThemedText style={styles.bold}>Real-time Monitoring:</ThemedText> Track profits, balances, and trade history
            </ThemedText>
          </ThemedView>
          
          <ThemedView style={styles.featureItem}>
            <ThemedText style={styles.featureBullet}>•</ThemedText>
            <ThemedText style={styles.featureText}>
              <ThemedText style={styles.bold}>Mobile Optimized:</ThemedText> Fully responsive design for Android devices
            </ThemedText>
          </ThemedView>
          
          <ThemedView style={styles.featureItem}>
            <ThemedText style={styles.featureBullet}>•</ThemedText>
            <ThemedText style={styles.featureText}>
              <ThemedText style={styles.bold}>Secure API Integration:</ThemedText> Safely connected to your OKX account
            </ThemedText>
          </ThemedView>
        </ThemedView>
        
        <ThemedView style={styles.instructionContainer}>
          <ThemedText type="subtitle">Getting Started</ThemedText>
          <ThemedText style={styles.description}>
            Navigate to the "Explore" tab to view your account balance, active strategies, and trading performance.
            All strategies are pre-configured for optimal performance with your 7 USDT starting balance.
          </ThemedText>
        </ThemedView>
      </ThemedView>
    </ParallaxScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
  },
  titleContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    marginBottom: 24,
  },
  statusContainer: {
    gap: 12,
    marginBottom: 24,
  },
  infoContainer: {
    marginBottom: 24,
  },
  instructionContainer: {
    marginBottom: 24,
  },
  description: {
    marginTop: 8,
    marginBottom: 16,
    lineHeight: 22,
  },
  featuresTitle: {
    marginTop: 8,
    marginBottom: 12,
  },
  featureItem: {
    flexDirection: 'row',
    marginBottom: 8,
    paddingRight: 16,
  },
  featureBullet: {
    marginRight: 8,
    fontSize: 18,
  },
  featureText: {
    flex: 1,
    lineHeight: 22,
  },
  bold: {
    fontWeight: 'bold',
  },
  reactLogo: {
    height: 178,
    width: 290,
    bottom: 0,
    left: 0,
    position: 'absolute',
  },
});