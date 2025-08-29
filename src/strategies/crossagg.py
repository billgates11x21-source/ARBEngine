import time
import random
from typing import Dict, List, Optional
from src.strategies.base_strategy import BaseStrategy

class CrossExchangeAggregationStrategy(BaseStrategy):
    """
    Cross-Exchange Aggregation Strategy - Finds price differences across multiple exchanges
    
    This strategy:
    1. Monitors prices across different exchanges (simulated for demo)
    2. Identifies price discrepancies for the same asset
    3. Buys on the exchange with lower price
    4. Sells on the exchange with higher price
    5. Manages transfer costs and timing
    """
    
    def __init__(self):
        super().__init__(
            name="crossagg",
            description="Finds price differences across multiple exchanges"
        )
        self.trading_pairs = ["BTC-USDT", "ETH-USDT", "SOL-USDT"]
        self.position_size = 0.025  # 2.5% of available balance
        self.min_price_diff = 0.005  # Minimum 0.5% price difference to trade
        self.max_open_positions = 2
        self.open_positions = {}
        
        # Simulated exchanges (in a real implementation, these would be actual API clients)
        self.exchanges = ["OKX", "Binance", "Coinbase", "Kraken"]
        
    def get_interval(self) -> float:
        return 30.0  # Check every 30 seconds
    
    def execute(self):
        """Execute the cross-exchange aggregation strategy"""
        # Skip if we already have maximum open positions
        if len(self.open_positions) >= self.max_open_positions:
            self._check_open_positions()
            return
        
        # Select a random trading pair to analyze
        pair = random.choice(self.trading_pairs)
        
        try:
            # Get OKX price (real)
            okx_ticker_data = self.okx.get_ticker(pair)
            if not okx_ticker_data or 'data' not in okx_ticker_data or not okx_ticker_data['data']:
                return
            
            okx_price = float(okx_ticker_data['data'][0]['last'])
            
            # Simulate prices on other exchanges (in a real implementation, we would fetch actual prices)
            exchange_prices = {
                "OKX": okx_price,
                "Binance": okx_price * (1 + random.uniform(-0.01, 0.01)),
                "Coinbase": okx_price * (1 + random.uniform(-0.01, 0.01)),
                "Kraken": okx_price * (1 + random.uniform(-0.01, 0.01))
            }
            
            # Find cheapest and most expensive exchange
            cheapest_exchange = min(exchange_prices.items(), key=lambda x: x[1])
            most_expensive_exchange = max(exchange_prices.items(), key=lambda x: x[1])
            
            # Calculate price difference percentage
            price_diff_pct = (most_expensive_exchange[1] - cheapest_exchange[1]) / cheapest_exchange[1]
            
            # Check if price difference is significant enough
            if price_diff_pct < self.min_price_diff:
                return
            
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
            
            # Calculate quantity
            quantity = trade_amount_usdt / cheapest_exchange[1]
            
            # Simulate transfer costs (0.1% of trade value)
            transfer_cost = trade_amount_usdt * 0.001
            
            # Calculate potential profit
            potential_profit = (most_expensive_exchange[1] - cheapest_exchange[1]) * quantity - transfer_cost
            
            # Only proceed if profitable after costs
            if potential_profit <= 0:
                return
            
            # Create a position
            order_id = f"crossagg_{int(time.time())}_{random.randint(1000, 9999)}"
            
            # Record the position
            self.open_positions[order_id] = {
                'pair': pair,
                'buy_exchange': cheapest_exchange[0],
                'buy_price': cheapest_exchange[1],
                'sell_exchange': most_expensive_exchange[0],
                'sell_price': most_expensive_exchange[1],
                'quantity': quantity,
                'timestamp': time.time(),
                'transfer_cost': transfer_cost,
                'expected_profit': potential_profit,
                'status': 'buying'  # Stages: buying -> transferring -> selling -> complete
            }
            
            # Record the trade
            self._record_trade({
                'strategy': 'crossagg',
                'action': 'open_position',
                'pair': pair,
                'buy_exchange': cheapest_exchange[0],
                'buy_price': cheapest_exchange[1],
                'sell_exchange': most_expensive_exchange[0],
                'sell_price': most_expensive_exchange[1],
                'quantity': quantity,
                'order_id': order_id,
                'transfer_cost': transfer_cost,
                'expected_profit': potential_profit
            })
            
            print(f"[CROSSAGG] Found opportunity: Buy {pair} on {cheapest_exchange[0]} at {cheapest_exchange[1]}, "
                  f"Sell on {most_expensive_exchange[0]} at {most_expensive_exchange[1]}, "
                  f"Expected profit: {potential_profit}")
        
        except Exception as e:
            print(f"Error in cross-exchange aggregation strategy: {e}")
    
    def _check_open_positions(self):
        """Check and manage open positions"""
        positions_to_update = []
        positions_to_complete = []
        
        for order_id, position in self.open_positions.items():
            try:
                current_time = time.time()
                time_elapsed = current_time - position['timestamp']
                
                # Simulate the stages of cross-exchange trading
                if position['status'] == 'buying' and time_elapsed > 10:
                    # Buy order completed, now transferring
                    position['status'] = 'transferring'
                    positions_to_update.append(order_id)
                    
                    # Record the update
                    self._record_trade({
                        'strategy': 'crossagg',
                        'action': 'update_position',
                        'order_id': order_id,
                        'status': 'transferring',
                        'note': f"Buy completed on {position['buy_exchange']}, transferring to {position['sell_exchange']}"
                    })
                    
                    print(f"[CROSSAGG] Position {order_id}: Buy completed, now transferring")
                
                elif position['status'] == 'transferring' and time_elapsed > 40:
                    # Transfer completed, now selling
                    position['status'] = 'selling'
                    positions_to_update.append(order_id)
                    
                    # Record the update
                    self._record_trade({
                        'strategy': 'crossagg',
                        'action': 'update_position',
                        'order_id': order_id,
                        'status': 'selling',
                        'note': f"Transfer to {position['sell_exchange']} completed, now selling"
                    })
                    
                    print(f"[CROSSAGG] Position {order_id}: Transfer completed, now selling")
                
                elif position['status'] == 'selling' and time_elapsed > 60:
                    # Sell completed, calculate actual profit
                    
                    # In a real implementation, we would get the actual sell price
                    # For demo, we'll simulate some slippage
                    actual_sell_price = position['sell_price'] * (1 - random.uniform(0, 0.002))
                    
                    # Calculate actual profit
                    actual_profit = (actual_sell_price - position['buy_price']) * position['quantity'] - position['transfer_cost']
                    
                    # Complete the position
                    positions_to_complete.append((order_id, actual_profit))
                    
                    print(f"[CROSSAGG] Position {order_id}: Sell completed")
            
            except Exception as e:
                print(f"Error checking position {order_id}: {e}")
        
        # Update positions
        for order_id in positions_to_update:
            # Nothing to do here, we already updated the position in the loop
            pass
        
        # Complete positions
        for order_id, profit in positions_to_complete:
            position = self.open_positions.pop(order_id)
            
            # Record the trade
            self._record_trade({
                'strategy': 'crossagg',
                'action': 'close_position',
                'pair': position['pair'],
                'buy_exchange': position['buy_exchange'],
                'buy_price': position['buy_price'],
                'sell_exchange': position['sell_exchange'],
                'sell_price': position['sell_price'],
                'quantity': position['quantity'],
                'order_id': order_id,
                'transfer_cost': position['transfer_cost'],
                'expected_profit': position['expected_profit'],
                'actual_profit': profit,
                'profit': profit  # This is used for profit tracking
            })
            
            print(f"[CROSSAGG] Completed position {order_id} with profit: {profit}")