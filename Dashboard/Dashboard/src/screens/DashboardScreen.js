import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';
import { BlurView } from '@react-native-community/blur';
import { LineChart } from 'react-native-chart-kit';

export default function DashboardScreen() {
  const [balance, setBalance] = useState({});
  const [lastTrade, setLastTrade] = useState({});

  useEffect(() => {
    fetch('http://localhost:8000/balance')
      .then(res => res.json()).then(data => setBalance(data.balances||{}));
    fetch('http://localhost:8000/last_trade')
      .then(res => res.json()).then(data => setLastTrade(data||{}));
  }, []);

  return (
    <ScrollView style={styles.container}>
      <BlurView style={styles.panel} blurType='light' blurAmount={10}>
        <Text style={styles.title}>ARBengine Dashboard</Text>
        <Text style={styles.text}>Balance: {JSON.stringify(balance)}</Text>
        <Text style={styles.text}>Last Trade: {JSON.stringify(lastTrade)}</Text>
      </BlurView>
      <BlurView style={styles.panel} blurType='light' blurAmount={10}>
        <LineChart
          data={{
            labels: ['Day1','Day2','Day3','Day4','Day5','Day6','Day7'],
            datasets: [{ data: [10,20,30,25,40,55,60] }]
          }}
          width={350} height={220}
          chartConfig={{
            backgroundColor: '#000',
            backgroundGradientFrom: '#111',
            backgroundGradientTo: '#333',
            color: (opacity = 1) => `rgba(0, 255, 200, ${opacity})`,
            labelColor: () => '#fff'
          }}
        />
      </BlurView>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container:{flex:1, backgroundColor:'#000'},
  panel:{margin:20,padding:20,borderRadius:20,overflow:'hidden'},
  title:{fontSize:22,color:'#0ff',marginBottom:10,textAlign:'center'},
  text:{fontSize:16,color:'#fff',marginVertical:4}
});
