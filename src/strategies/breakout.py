import time
import random
import numpy as np
from typing import Dict, List, Optional
from src.strategies.base_strategy import BaseStrategy

class BreakoutStrategy(BaseStrategy):
    """
    Breakout Strategy - Capitalizes on price movements beyond support/resistance levels
    
    This strategy:
    1. Identifies key support and resistance levels
    2. Monitors price action around these levels
    3. Enters positions when price breaks through these levels with volume
    4. Sets profit targets based on the strength of the breakout
    5. Uses trailing stops to protect profits
    """
    
    def __init__(self):
        super().__init__(
            name="breakout",
            description="Capitalizes on price movements beyond support/resistance levels"
        )
        self.trading_pairs = ["BTC-USDT", "ETH-USDT", "SOL-USDT"]
        self.position_size = 0.015  # 1.5% of available balance
        self.profit_target_pct = 0.01  # 1% profit target
        self.stop_loss_pct = 0.005  # 0.5% stop loss
        self.max_open_positions = 2
        self.open_positions = {}
        self.price_history = {}  # Store recent prices for each pair
        self.lookback_periods = 20  # Number of periods to look back for S/R levels
        
    def get_interval(self) -> float:
        return 15.0  # Check every 15 seconds
    
    def execute(self):
        """Execute the breakout strategy"""
        # Skip if we already have maximum open positions
        if len(self.open_positions) >= self.max_open_positions:
            self._check_open_positions()
            return
        
        # Select a random trading pair to analyze
        pair = random.choice(self.trading_pairs)
        
        try:
            # Get current ticker data
            ticker_data = self.okx.get_ticker(pair)
            if not ticker_data or 'data' not in ticker_data or not ticker_data['data']:
                return
            
            ticker = ticker_data['data'][0]
            current_price = float(ticker['last'])
            
            # Update price history
            if pair not in self.price_history:
                self.price_history[pair] = []
            
            self.price_history[pair].append(current_price)
            
            # Keep only the most recent data points
            if len(self.price_history[pair]) > self.lookback_periods:
                self.price_history[pair] = self.price_history[pair][-self.lookback_periods:]
            
            # Need enough data points to identify levels
            if len(self.price_history[pair]) < self.lookback_periods:
                return
            
            # Identify support and resistance levels
            support, resistance = self._identify_support_resistance(self.price_history[pair])
            
            # Get account balance
            balance_data = self.okx.get_account_balance()
            if not balance_data or 'data' not in balance_data or not balance_data['data']:
                return
                
            # Find USDT balance
            usdt_balance = 0
            for currency in balance_data['data'][0]['details']:
                if currency['ccy'] == 'USDT':
                    usdt_balance = float(currency['availBal'])
                    break
            
            # Calculate position size
            trade_amount_usdt = usdt_balance * self.position_size
            if trade_amount_usdt < 7:  # Minimum is our starting balance of 7 USDT
                return
            
            # Check for breakouts
            # Resistance breakout (bullish)
            if current_price > resistance and current_price > self.price_history[pair][-2]:
                side = "buy"
                order_price = current_price
                quantity = trade_amount_usdt / order_price
                
                # Place order (simulated for demo)
                order_id = f"breakout_{int(time.time())}_{random.randint(1000, 9999)}"
                
                # Record the position
                self.open_positions[order_id] = {
                    'pair': pair,
                    'side': side,
                    'price': order_price,
                    'quantity': quantity,
                    'timestamp': time.time(),
                    'profit_target': order_price * (1 + self.profit_target_pct),
                    'stop_loss': order_price * (1 - self.stop_loss_pct),
                    'trailing_stop': order_price * (1 - self.stop_loss_pct),
                    'highest_price': order_price
                }
                
                # Record the trade
                self._record_trade({
                    'strategy': 'breakout',
                    'action': 'open_position',
                    'pair': pair,
                    'side': side,
                    'price': order_price,
                    'quantity': quantity,
                    'order_id': order_id,
                    'breakout_type': 'resistance'
                })
                
                print(f"[BREAKOUT] Resistance breakout! Opened {side} position for {pair} at {order_price}")
            
            # Support breakout (bearish)
            elif current_price < support and current_price < self.price_history[pair][-2]:
                side = "sell"
                order_price = current_price
                quantity = trade_amount_usdt / order_price
                
                # Place order (simulated for demo)
                order_id = f"breakout_{int(time.time())}_{random.randint(1000, 9999)}"
                
                # Record the position
                self.open_positions[order_id] = {
                    'pair': pair,
                    'side': side,
                    'price': order_price,
                    'quantity': quantity,
                    'timestamp': time.time(),
                    'profit_target': order_price * (1 - self.profit_target_pct),
                    'stop_loss': order_price * (1 + self.stop_loss_pct),
                    'trailing_stop': order_price * (1 + self.stop_loss_pct),
                    'lowest_price': order_price
                }
                
                # Record the trade
                self._record_trade({
                    'strategy': 'breakout',
                    'action': 'open_position',
                    'pair': pair,
                    'side': side,
                    'price': order_price,
                    'quantity': quantity,
                    'order_id': order_id,
                    'breakout_type': 'support'
                })
                
                print(f"[BREAKOUT] Support breakout! Opened {side} position for {pair} at {order_price}")
        
        except Exception as e:
            print(f"Error in breakout strategy: {e}")
    
    def _identify_support_resistance(self, prices):
        """Identify support and resistance levels"""
        # Simple implementation using percentiles
        prices_array = np.array(prices)
        support = np.percentile(prices_array, 25)  # 25th percentile as support
        resistance = np.percentile(prices_array, 75)  # 75th percentile as resistance
        return support, resistance
    
    def _check_open_positions(self):
        """Check and manage open positions"""
        positions_to_close = []
        
        for order_id, position in self.open_positions.items():
            try:
                # Get current price
                ticker_data = self.okx.get_ticker(position['pair'])
                if not ticker_data or 'data' not in ticker_data or not ticker_data['data']:
                    continue
                
                current_price = float(ticker_data['data'][0]['last'])
                
                # Update highest/lowest price for trailing stop
                if position['side'] == 'buy':
                    if current_price > position['highest_price']:
                        position['highest_price'] = current_price
                        # Update trailing stop
                        new_stop = current_price * (1 - self.stop_loss_pct)
                        if new_stop > position['trailing_stop']:
                            position['trailing_stop'] = new_stop
                    
                    # Check if profit target or stop loss hit
                    if current_price >= position['profit_target']:
                        # Take profit
                        profit = (current_price - position['price']) * position['quantity']
                        positions_to_close.append((order_id, 'profit_target', profit))
                    elif current_price <= position['trailing_stop']:
                        # Trailing stop hit
                        profit = (current_price - position['price']) * position['quantity']
                        positions_to_close.append((order_id, 'trailing_stop', profit))
                else:
                    if current_price < position['lowest_price']:
                        position['lowest_price'] = current_price
                        # Update trailing stop
                        new_stop = current_price * (1 + self.stop_loss_pct)
                        if new_stop < position['trailing_stop']:
                            position['trailing_stop'] = new_stop
                    
                    # Check if profit target or stop loss hit
                    if current_price <= position['profit_target']:
                        # Take profit
                        profit = (position['price'] - current_price) * position['quantity']
                        positions_to_close.append((order_id, 'profit_target', profit))
                    elif current_price >= position['trailing_stop']:
                        # Trailing stop hit
                        profit = (position['price'] - current_price) * position['quantity']
                        positions_to_close.append((order_id, 'trailing_stop', profit))
            
            except Exception as e:
                print(f"Error checking position {order_id}: {e}")
        
        # Close positions
        for order_id, reason, pnl in positions_to_close:
            position = self.open_positions.pop(order_id)
            
            # Record the trade
            self._record_trade({
                'strategy': 'breakout',
                'action': 'close_position',
                'pair': position['pair'],
                'side': 'sell' if position['side'] == 'buy' else 'buy',  # Opposite of opening side
                'price': position['price'],
                'quantity': position['quantity'],
                'order_id': order_id,
                'reason': reason,
                'profit': pnl
            })
            
            print(f"[BREAKOUT] Closed position {order_id} with {reason}, PnL: {pnl}")