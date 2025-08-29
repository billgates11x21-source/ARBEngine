import time
import json
import asyncio
import threading
import websockets
import numpy as np
from typing import Dict, List, Optional, Tuple
from src.strategies.base_strategy import BaseStrategy
from src.api.okx_client import OKXClient

class TriangularArbStrategy(BaseStrategy):
    """
    Triangular Arbitrage Strategy - Exploits price differences across three trading pairs
    
    This strategy:
    1. Monitors prices across three related trading pairs that form a triangle
    2. Identifies opportunities where converting through the triangle results in profit
    3. Executes trades quickly to capture the price discrepancy
    4. Focuses on AUD-based triangles as requested
    5. Handles execution with precision timing to minimize slippage
    """
    
    def __init__(self):
        super().__init__(
            name="triangular_arb",
            description="Exploits price differences across three related trading pairs"
        )
        self.position_size = 0.03  # 3% of available balance
        self.min_profit_threshold = 0.005  # Minimum 0.5% profit to execute
        self.max_open_positions = 1  # Only one triangular arb at a time
        self.open_positions = {}
        self.fee_rate = 0.001  # 0.1% fee per trade
        
        # Define triangular arbitrage paths to monitor
        # Format: [pair1, pair2, pair3]
        self.triangles = [
            ["XRP-AUD", "AUD-USDT", "XRP-USDT"],  # XRP -> AUD -> USDT -> XRP
            ["BTC-AUD", "AUD-USDC", "BTC-USDC"],  # BTC -> AUD -> USDC -> BTC
            ["SOL-USDT", "USDT-AUD", "SOL-AUD"],  # SOL -> USDT -> AUD -> SOL
            ["ETH-AUD", "AUD-USDT", "ETH-USDT"],  # ETH -> AUD -> USDT -> ETH
            ["LTC-AUD", "AUD-USDT", "LTC-USDT"]   # LTC -> AUD -> USDT -> LTC
        ]
        
        # Store latest ticker data
        self.ticker_data = {}
        
        # Start WebSocket connection in a separate thread
        self.ws_thread = threading.Thread(target=self._start_websocket)
        self.ws_thread.daemon = True
        self.ws_thread.start()
    
    def get_interval(self) -> float:
        return 2.0  # Check every 2 seconds - need to be fast for arbitrage
    
    def _start_websocket(self):
        """Start WebSocket connection to get real-time ticker data"""
        # Create a list of all unique trading pairs from triangles
        pairs = set()
        for triangle in self.triangles:
            for pair in triangle:
                pairs.add(pair)
        
        # Create asyncio event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Start WebSocket connection
        loop.run_until_complete(self._subscribe_to_tickers(list(pairs)))
    
    async def _subscribe_to_tickers(self, pairs: List[str]):
        """Subscribe to ticker data for all pairs"""
        url = "wss://ws.okx.com:8443/ws/v5/public"
        
        # Create subscription message
        subscribe_args = []
        for pair in pairs:
            subscribe_args.append({"channel": "tickers", "instId": pair})
        
        subscribe_message = {
            "op": "subscribe",
            "args": subscribe_args
        }
        
        # Connect to WebSocket and subscribe
        try:
            async with websockets.connect(url) as ws:
                await ws.send(json.dumps(subscribe_message))
                print(f"[TRIANGULAR_ARB] Subscribed to {len(pairs)} ticker streams")
                
                # Process incoming messages
                while True:
                    try:
                        data = await ws.recv()
                        message = json.loads(data)
                        
                        # Handle ping messages
                        if 'event' in message and message['event'] == 'ping':
                            pong_msg = json.dumps({"event": "pong"})
                            await ws.send(pong_msg)
                            continue
                        
                        # Process ticker data
                        if 'data' in message:
                            for ticker in message['data']:
                                if 'instId' in ticker:
                                    pair = ticker['instId']
                                    self.ticker_data[pair] = {
                                        'bid': float(ticker['bidPx']),
                                        'ask': float(ticker['askPx']),
                                        'last': float(ticker['last']),
                                        'timestamp': time.time()
                                    }
                    except Exception as e:
                        print(f"[TRIANGULAR_ARB] WebSocket error: {e}")
                        # Try to reconnect
                        break
        except Exception as e:
            print(f"[TRIANGULAR_ARB] WebSocket connection error: {e}")
            # Wait and try to reconnect
            await asyncio.sleep(5)
            await self._subscribe_to_tickers(pairs)
    
    def execute(self):
        """Execute the triangular arbitrage strategy"""
        # Skip if we already have maximum open positions
        if len(self.open_positions) >= self.max_open_positions:
            self._check_open_positions()
            return
        
        try:
            # Check each triangle for arbitrage opportunities
            for triangle in self.triangles:
                # Skip if we don't have ticker data for all pairs in the triangle
                if not all(pair in self.ticker_data for pair in triangle):
                    continue
                
                # Calculate potential profit
                profit_pct, direction = self._calculate_triangle_profit(triangle)
                
                # If profit exceeds threshold, execute the arbitrage
                if profit_pct > self.min_profit_threshold:
                    # Get account balance
                    balance_data = self.okx.get_account_balance()
                    if not balance_data or 'data' not in balance_data or not balance_data['data']:
                        continue
                    
                    # Find USDT balance (or other starting currency based on the triangle)
                    usdt_balance = 0
                    for currency in balance_data['data'][0]['details']:
                        if currency['ccy'] == 'USDT':
                            usdt_balance = float(currency['availBal'])
                            break
                    
                    # Calculate position size
                    trade_amount_usdt = usdt_balance * self.position_size
                    if trade_amount_usdt < 7:  # Minimum is our starting balance of 7 USDT
                        continue
                    
                    # Execute the triangular arbitrage
                    self._execute_triangular_arbitrage(triangle, trade_amount_usdt, direction, profit_pct)
        
        except Exception as e:
            print(f"Error in triangular arbitrage strategy: {e}")
    
    def _calculate_triangle_profit(self, triangle: List[str]) -> Tuple[float, str]:
        """
        Calculate the potential profit from a triangular arbitrage
        
        Returns:
            Tuple[float, str]: (profit_percentage, direction)
            direction is either "forward" or "reverse"
        """
        # Get ticker data for all pairs in the triangle
        pair1, pair2, pair3 = triangle
        ticker1 = self.ticker_data[pair1]
        ticker2 = self.ticker_data[pair2]
        ticker3 = self.ticker_data[pair3]
        
        # Calculate forward path (e.g., XRP -> AUD -> USDT -> XRP)
        # Start with 1 unit
        # First trade: Sell asset1 for asset2
        forward_step1 = 1 / ticker1['ask']  # Selling at ask price
        forward_step1 *= (1 - self.fee_rate)  # Apply fee
        
        # Second trade: Sell asset2 for asset3
        forward_step2 = forward_step1 / ticker2['ask']  # Selling at ask price
        forward_step2 *= (1 - self.fee_rate)  # Apply fee
        
        # Third trade: Sell asset3 to buy back asset1
        forward_step3 = forward_step2 * ticker3['bid']  # Buying at bid price
        forward_step3 *= (1 - self.fee_rate)  # Apply fee
        
        # Calculate reverse path (e.g., XRP -> USDT -> AUD -> XRP)
        # Start with 1 unit
        # First trade: Sell asset1 for asset3
        reverse_step1 = ticker3['bid']  # Selling at bid price
        reverse_step1 *= (1 - self.fee_rate)  # Apply fee
        
        # Second trade: Sell asset3 for asset2
        reverse_step2 = reverse_step1 * ticker2['bid']  # Selling at bid price
        reverse_step2 *= (1 - self.fee_rate)  # Apply fee
        
        # Third trade: Sell asset2 to buy back asset1
        reverse_step3 = reverse_step2 * ticker1['bid']  # Buying at bid price
        reverse_step3 *= (1 - self.fee_rate)  # Apply fee
        
        # Calculate profit percentages
        forward_profit = forward_step3 - 1
        reverse_profit = reverse_step3 - 1
        
        # Return the better direction
        if forward_profit > reverse_profit:
            return forward_profit, "forward"
        else:
            return reverse_profit, "reverse"
    
    def _execute_triangular_arbitrage(self, triangle: List[str], amount: float, direction: str, expected_profit: float):
        """Execute a triangular arbitrage trade"""
        # Create a unique ID for this arbitrage
        arb_id = f"tri_arb_{int(time.time())}_{triangle[0].split('-')[0]}"
        
        # Parse the triangle to get the currencies involved
        currencies = []
        for pair in triangle:
            base, quote = pair.split('-')
            if base not in currencies:
                currencies.append(base)
            if quote not in currencies:
                currencies.append(quote)
        
        # Determine the trade path based on direction
        if direction == "forward":
            trade_path = triangle
        else:  # reverse
            trade_path = [triangle[2], triangle[1], triangle[0]]
        
        # Record the position
        self.open_positions[arb_id] = {
            'triangle': triangle,
            'direction': direction,
            'trade_path': trade_path,
            'amount': amount,
            'expected_profit': expected_profit,
            'timestamp': time.time(),
            'status': 'executing',
            'trades': []
        }
        
        # Record the trade
        self._record_trade({
            'strategy': 'triangular_arb',
            'action': 'start_arbitrage',
            'triangle': triangle,
            'direction': direction,
            'amount': amount,
            'expected_profit': expected_profit,
            'arb_id': arb_id
        })
        
        print(f"[TRIANGULAR_ARB] Starting arbitrage {arb_id} with expected profit {expected_profit:.4%}")
        
        # In a real implementation, we would execute the trades here
        # For this demo, we'll simulate the execution
        threading.Thread(target=self._simulate_arbitrage_execution, args=(arb_id,)).start()
    
    def _simulate_arbitrage_execution(self, arb_id: str):
        """Simulate the execution of a triangular arbitrage (for demo purposes)"""
        position = self.open_positions[arb_id]
        
        try:
            # Simulate the three trades
            for i, pair in enumerate(position['trade_path']):
                # Simulate some execution time
                time.sleep(1)
                
                # Simulate trade execution
                trade_result = {
                    'pair': pair,
                    'timestamp': time.time(),
                    'status': 'filled',
                    'fill_price': self.ticker_data[pair]['last'],
                    'fill_amount': position['amount'] if i == 0 else position['trades'][-1]['fill_amount'] * 0.998  # Simulate some slippage
                }
                
                # Add trade to position
                position['trades'].append(trade_result)
                
                # Record the trade
                self._record_trade({
                    'strategy': 'triangular_arb',
                    'action': f'trade_{i+1}',
                    'pair': pair,
                    'fill_price': trade_result['fill_price'],
                    'fill_amount': trade_result['fill_amount'],
                    'arb_id': arb_id
                })
                
                print(f"[TRIANGULAR_ARB] Executed trade {i+1} for {arb_id}: {pair} at {trade_result['fill_price']}")
            
            # Calculate actual profit
            initial_amount = position['amount']
            final_amount = position['trades'][-1]['fill_amount']
            actual_profit = (final_amount - initial_amount) / initial_amount
            
            # Update position status
            position['status'] = 'completed'
            position['actual_profit'] = actual_profit
            
            # Record the completion
            self._record_trade({
                'strategy': 'triangular_arb',
                'action': 'complete_arbitrage',
                'arb_id': arb_id,
                'initial_amount': initial_amount,
                'final_amount': final_amount,
                'actual_profit': actual_profit,
                'profit': actual_profit * initial_amount  # Absolute profit amount
            })
            
            print(f"[TRIANGULAR_ARB] Completed arbitrage {arb_id} with actual profit {actual_profit:.4%}")
            
            # Remove from open positions after a delay
            time.sleep(5)
            if arb_id in self.open_positions:
                del self.open_positions[arb_id]
        
        except Exception as e:
            # Handle execution errors
            position['status'] = 'failed'
            position['error'] = str(e)
            
            # Record the failure
            self._record_trade({
                'strategy': 'triangular_arb',
                'action': 'failed_arbitrage',
                'arb_id': arb_id,
                'error': str(e)
            })
            
            print(f"[TRIANGULAR_ARB] Failed arbitrage {arb_id}: {e}")
            
            # Remove from open positions after a delay
            time.sleep(5)
            if arb_id in self.open_positions:
                del self.open_positions[arb_id]
    
    def _check_open_positions(self):
        """Check and manage open positions"""
        # Nothing to do here as positions are managed in _simulate_arbitrage_execution
        pass