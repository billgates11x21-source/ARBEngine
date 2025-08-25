import React from 'react';
import { Image } from 'expo-image';
import { Platform, StyleSheet } from 'react-native';

import { Collapsible } from '@/components/Collapsible';
import { ExternalLink } from '@/components/ExternalLink';
import ParallaxScrollView from '@/components/ParallaxScrollView';
import { ThemedText } from '@/components/ThemedText';
import { ThemedView } from '@/components/ThemedView';
import { IconSymbol } from '@/components/ui/IconSymbol';

export default function TabTwoScreen() {
  const [balance, setBalance] = React.useState<any>(null);
  const [lastTrade, setLastTrade] = React.useState<any>(null);
  const [profit, setProfit] = React.useState<any>(null);
  React.useEffect(() => {
    fetch('http://127.0.0.1:8000/balance')
      .then(res => res.json())
      .then(data => setBalance(data.balances));
    fetch('http://127.0.0.1:8000/last_trade')
      .then(res => res.json())
      .then(data => setLastTrade(data));
    fetch('http://127.0.0.1:8000/profit')
      .then(res => res.json())
      .then(data => setProfit(data));
  }, []);
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
    >
      <ThemedView style={styles.titleContainer}>
        <ThemedText type="title">Profit Monitor</ThemedText>
      </ThemedView>
      <ThemedText>Live Balances:</ThemedText>
      <ThemedText>{balance ? JSON.stringify(balance) : 'Loading...'}</ThemedText>
      <ThemedText>Last Trade:</ThemedText>
      <ThemedText>{lastTrade ? JSON.stringify(lastTrade) : 'Loading...'}</ThemedText>
      <ThemedText>Profit Monitor:</ThemedText>
      <ThemedText>{profit ? JSON.stringify(profit) : 'Loading...'}</ThemedText>
      {/* Example collapsible sections below. You can further clean up or replace as needed. */}
      <Collapsible title="File-based routing">
        <ThemedText>
          This app has two screens:{' '}
          <ThemedText type="defaultSemiBold">app/(tabs)/index.tsx</ThemedText> and{' '}
          <ThemedText type="defaultSemiBold">app/(tabs)/explore.tsx</ThemedText>
        </ThemedText>
        <ThemedText>
          The layout file in <ThemedText type="defaultSemiBold">app/(tabs)/_layout.tsx</ThemedText>{' '}
          sets up the tab navigator.
        </ThemedText>
        <ExternalLink href="https://docs.expo.dev/router/introduction">
          <ThemedText type="link">Learn more</ThemedText>
        </ExternalLink>
      </Collapsible>
      <Collapsible title="Android, iOS, and web support">
        <ThemedText>
          You can open this project on Android, iOS, and the web. To open the web version, press{' '}
          <ThemedText type="defaultSemiBold">w</ThemedText> in the terminal running this project.
        </ThemedText>
      </Collapsible>
      <Collapsible title="Images">
        <ThemedText>
          For static images, you can use the <ThemedText type="defaultSemiBold">@2x</ThemedText> and{' '}
          <ThemedText type="defaultSemiBold">@3x</ThemedText> suffixes to provide files for different screen densities.
        </ThemedText>
      </Collapsible>
    </ParallaxScrollView>
  );
}

const styles = StyleSheet.create({
  headerImage: {
    color: '#808080',
    bottom: -90,
    left: -35,
    position: 'absolute',
  },
  titleContainer: {
    flexDirection: 'row',
    gap: 8,
  },
});
