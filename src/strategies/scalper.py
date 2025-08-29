import time
import random
from typing import Dict, List, Optional
from src.strategies.base_strategy import BaseStrategy

class ScalperStrategy(BaseStrategy):
    """
    Scalping Strategy - Quick trades to profit from small price movements
    
    This strategy:
    1. Monitors price movements in short timeframes
    2. Places limit orders just above bid or just below ask
    3. Takes small profits quickly
    4. Uses tight stop losses
    5. Focuses on high-volume, liquid markets
    """
    
    def __init__(self):
        super().__init__(
            name="scalping",
            description="Quick trades to profit from small price movements"
        )
        self.trading_pairs = ["BTC-USDT", "ETH-USDT", "SOL-USDT"]
        self.position_size = 0.01  # 1% of available balance
        self.profit_target_pct = 0.002  # 0.2% profit target
        self.stop_loss_pct = 0.001  # 0.1% stop loss
        self.max_open_positions = 3
        self.open_positions = {}
        
    def get_interval(self) -> float:
        return 5.0  # Check every 5 seconds
    
    def execute(self):
        """Execute the scalping strategy"""
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
            bid_price = float(ticker['bidPx'])
            ask_price = float(ticker['askPx'])
            
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
                
            # Analyze price movement and volatility
            # For demo purposes, we'll use a simple random decision
            should_trade = random.random() > 0.7  # 30% chance to trade
            
            if should_trade:
                # Decide direction (buy/sell) based on recent price action
                # For demo, we'll use random
                side = "buy" if random.random() > 0.5 else "sell"
                
                # Calculate order price
                if side == "buy":
                    # Place buy order slightly above current bid
                    order_price = bid_price * 1.0001
                    # Calculate quantity based on USDT amount
                    quantity = trade_amount_usdt / order_price
                else:
                    # For a real sell, we'd need to check our holdings
                    # For demo, we'll assume we have the asset and calculate similarly
                    order_price = ask_price * 0.9999
                    quantity = trade_amount_usdt / order_price
                
                # Place order (simulated for demo)
                order_id = f"scalp_{int(time.time())}_{random.randint(1000, 9999)}"
                
                # Record the position
                self.open_positions[order_id] = {
                    'pair': pair,
                    'side': side,
                    'price': order_price,
                    'quantity': quantity,
                    'timestamp': time.time(),
                    'profit_target': order_price * (1 + self.profit_target_pct if side == "buy" else 1 - self.profit_target_pct),
                    'stop_loss': order_price * (1 - self.stop_loss_pct if side == "buy" else 1 + self.stop_loss_pct)
                }
                
                # Record the trade
                self._record_trade({
                    'strategy': 'scalping',
                    'action': 'open_position',
                    'pair': pair,
                    'side': side,
                    'price': order_price,
                    'quantity': quantity,
                    'order_id': order_id
                })
                
                print(f"[SCALPER] Opened {side} position for {pair} at {order_price}")
        
        except Exception as e:
            print(f"Error in scalper strategy: {e}")
    
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
                
                # Check if profit target or stop loss hit
                if position['side'] == 'buy':
                    # For buy positions
                    if current_price >= position['profit_target']:
                        # Take profit
                        profit = (current_price - position['price']) * position['quantity']
                        positions_to_close.append((order_id, 'profit', profit))
                    elif current_price <= position['stop_loss']:
                        # Stop loss
                        loss = (position['price'] - current_price) * position['quantity']
                        positions_to_close.append((order_id, 'stop_loss', -loss))
                else:
                    # For sell positions
                    if current_price <= position['profit_target']:
                        # Take profit
                        profit = (position['price'] - current_price) * position['quantity']
                        positions_to_close.append((order_id, 'profit', profit))
                    elif current_price >= position['stop_loss']:
                        # Stop loss
                        loss = (current_price - position['price']) * position['quantity']
                        positions_to_close.append((order_id, 'stop_loss', -loss))
            
            except Exception as e:
                print(f"Error checking position {order_id}: {e}")
        
        # Close positions
        for order_id, reason, pnl in positions_to_close:
            position = self.open_positions.pop(order_id)
            
            # Record the trade
            self._record_trade({
                'strategy': 'scalping',
                'action': 'close_position',
                'pair': position['pair'],
                'side': 'sell' if position['side'] == 'buy' else 'buy',  # Opposite of opening side
                'price': position['price'],
                'quantity': position['quantity'],
                'order_id': order_id,
                'reason': reason,
                'profit': pnl
            })
            
            print(f"[SCALPER] Closed position {order_id} with {reason}, PnL: {pnl}")