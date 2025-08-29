import React, { useState, useEffect } from 'react';
import { StyleSheet, RefreshControl, View, Dimensions } from 'react-native';
import { useColorScheme } from '@/hooks/useColorScheme';

import ParallaxScrollView from '@/components/ParallaxScrollView';
import { ThemedText } from '@/components/ThemedText';
import { ThemedView } from '@/components/ThemedView';
import { IconSymbol } from '@/components/ui/IconSymbol';
import { StrategyCard } from '@/components/ui/StrategyCard';
import { BalanceCard } from '@/components/ui/BalanceCard';
import { ProfitChart } from '@/components/ui/ProfitChart';
import { TradeHistoryCard } from '@/components/ui/TradeHistoryCard';
import { SystemStatusCard } from '@/components/ui/SystemStatusCard';

// Get screen dimensions for responsive design
const { width } = Dimensions.get('window');

export default function ExploreScreen() {
  const colorScheme = useColorScheme();
  const [balance, setBalance] = useState<any>(null);
  const [lastTrade, setLastTrade] = useState<any>(null);
  const [profit, setProfit] = useState<any>(null);
  const [strategies, setStrategies] = useState<any[]>([]);
  const [activeStrategies, setActiveStrategies] = useState<any[]>([]);
  const [systemStatus, setSystemStatus] = useState<any>(null);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // API base URL - change this to your actual API endpoint
  const API_BASE_URL = 'http://localhost:8000';

  const fetchData = async () => {
    try {
      setError(null);
      setRefreshing(true);
      
      // Fetch balance data
      const balanceRes = await fetch(`${API_BASE_URL}/balance`);
      const balanceData = await balanceRes.json();
      setBalance(balanceData.balances);
      
      // Fetch last trade data
      const lastTradeRes = await fetch(`${API_BASE_URL}/last_trade`);
      const lastTradeData = await lastTradeRes.json();
      setLastTrade(lastTradeData);
      
      // Fetch profit data
      const profitRes = await fetch(`${API_BASE_URL}/profit`);
      const profitData = await profitRes.json();
      setProfit(profitData);
      
      // Fetch available strategies
      const strategiesRes = await fetch(`${API_BASE_URL}/strategies/available`);
      const strategiesData = await strategiesRes.json();
      setStrategies(strategiesData.strategies || []);
      
      // Fetch active strategies
      const activeStrategiesRes = await fetch(`${API_BASE_URL}/strategies/active`);
      const activeStrategiesData = await activeStrategiesRes.json();
      setActiveStrategies(activeStrategiesData.active_strategies || []);
      
      // Fetch system status
      const systemStatusRes = await fetch(`${API_BASE_URL}/system/status`);
      const systemStatusData = await systemStatusRes.json();
      setSystemStatus(systemStatusData);
    } catch (err) {
      console.error('Error fetching data:', err);
      setError('Failed to fetch data. Please check your connection and try again.');
    } finally {
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchData();
    
    // Set up polling interval (every 30 seconds)
    const intervalId = setInterval(fetchData, 30000);
    
    // Clean up interval on component unmount
    return () => clearInterval(intervalId);
  }, []);

  const onRefresh = () => {
    fetchData();
  };

  const toggleStrategy = async (strategyId: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/strategies/${strategyId}/toggle`, {
        method: 'POST',
      });
      
      if (response.ok) {
        // Refresh data after toggling
        fetchData();
      } else {
        setError('Failed to toggle strategy. Please try again.');
      }
    } catch (err) {
      console.error('Error toggling strategy:', err);
      setError('Failed to toggle strategy. Please check your connection and try again.');
    }
  };

  return (
    <ParallaxScrollView
      headerBackgroundColor={{ light: '#D0D0D0', dark: '#353636' }}
      headerImage={
        <IconSymbol
          size={310}
          color="#808080"
          name="chevron.left.forwardslash.chevron.right"
          style={styles.headerImage}
        />
      }
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      <ThemedView style={styles.container}>
        <ThemedText type="title" style={styles.title}>OKX Trading Dashboard</ThemedText>
        
        {error && (
          <ThemedView style={styles.errorContainer}>
            <ThemedText style={styles.errorText}>{error}</ThemedText>
          </ThemedView>
        )}
        
        {/* System Status */}
        <ThemedView style={styles.section}>
          <ThemedText type="subtitle">System Status</ThemedText>
          <SystemStatusCard 
            status={systemStatus}
            colorScheme={colorScheme}
          />
        </ThemedView>
        
        {/* Profit Summary */}
        <ThemedView style={styles.section}>
          <ThemedText type="subtitle">Profit Summary</ThemedText>
          <ProfitChart 
            profit={profit?.total_profit || 0} 
            colorScheme={colorScheme}
          />
        </ThemedView>
        
        {/* Balance Cards */}
        <ThemedView style={styles.section}>
          <ThemedText type="subtitle">Account Balance</ThemedText>
          <ThemedView style={styles.balanceContainer}>
            {balance ? (
              Array.isArray(balance.data?.[0]?.details) ? 
                balance.data[0].details.map((currency: any, index: number) => (
                  <BalanceCard 
                    key={index}
                    currency={currency.ccy}
                    balance={parseFloat(currency.availBal)}
                    colorScheme={colorScheme}
                  />
                )) : (
                  // Fallback for demo data
                  Object.entries(balance).map(([currency, amount]: [string, any], index: number) => (
                    <BalanceCard 
                      key={index}
                      currency={currency}
                      balance={amount}
                      colorScheme={colorScheme}
                    />
                  ))
                )
            ) : (
              <ThemedText>Loading balances...</ThemedText>
            )}
          </ThemedView>
        </ThemedView>
        
        {/* Active Strategies */}
        <ThemedView style={styles.section}>
          <ThemedText type="subtitle">Active Strategies</ThemedText>
          <ThemedView style={styles.strategiesContainer}>
            {activeStrategies.length > 0 ? (
              activeStrategies.map((strategy, index) => (
                <StrategyCard
                  key={index}
                  name={strategy.id}
                  description={strategies.find(s => s.id === strategy.id)?.description || ''}
                  active={strategy.status === 'running'}
                  profit24h={strategy.profit_24h}
                  lastExecution={strategy.last_execution}
                  onToggle={() => toggleStrategy(strategy.id)}
                  colorScheme={colorScheme}
                />
              ))
            ) : (
              <ThemedText>No active strategies</ThemedText>
            )}
          </ThemedView>
        </ThemedView>
        
        {/* Available Strategies */}
        <ThemedView style={styles.section}>
          <ThemedText type="subtitle">Available Strategies</ThemedText>
          <ThemedView style={styles.strategiesContainer}>
            {strategies.length > 0 ? (
              strategies.map((strategy, index) => {
                const activeStrategy = activeStrategies.find(s => s.id === strategy.id);
                return (
                  <StrategyCard
                    key={index}
                    name={strategy.name}
                    description={strategy.description}
                    active={!!activeStrategy}
                    profit24h={activeStrategy?.profit_24h || 0}
                    lastExecution={activeStrategy?.last_execution || null}
                    onToggle={() => toggleStrategy(strategy.id)}
                    colorScheme={colorScheme}
                  />
                );
              })
            ) : (
              <ThemedText>Loading strategies...</ThemedText>
            )}
          </ThemedView>
        </ThemedView>
        
        {/* Last Trade */}
        <ThemedView style={styles.section}>
          <ThemedText type="subtitle">Last Trade</ThemedText>
          {lastTrade && Object.keys(lastTrade).length > 0 ? (
            <TradeHistoryCard
              trade={lastTrade}
              colorScheme={colorScheme}
            />
          ) : (
            <ThemedText>No recent trades</ThemedText>
          )}
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
  title: {
    marginBottom: 16,
    fontSize: 24,
    fontWeight: 'bold',
  },
  section: {
    marginBottom: 24,
  },
  headerImage: {
    color: '#808080',
    bottom: -90,
    left: -35,
    position: 'absolute',
  },
  balanceContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    marginTop: 8,
  },
  strategiesContainer: {
    marginTop: 8,
  },
  errorContainer: {
    backgroundColor: '#ffdddd',
    padding: 12,
    borderRadius: 8,
    marginBottom: 16,
  },
  errorText: {
    color: '#ff0000',
  },
});