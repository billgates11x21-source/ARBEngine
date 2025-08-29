import time
import random
from typing import Dict, List, Optional
from src.strategies.base_strategy import BaseStrategy

class LiquidityStrategy(BaseStrategy):
    """
    Liquidity Strategy - Provides liquidity to earn fees in high-volume markets
    
    This strategy:
    1. Places limit orders on both sides of the order book
    2. Aims to capture the bid-ask spread
    3. Continuously rebalances orders as market moves
    4. Focuses on high-volume trading pairs
    5. Manages inventory to avoid excessive exposure
    """
    
    def __init__(self):
        super().__init__(
            name="liquidity",
            description="Provides liquidity to earn fees in high-volume markets"
        )
        self.trading_pairs = ["BTC-USDT", "ETH-USDT", "SOL-USDT"]
        self.position_size = 0.02  # 2% of available balance per side
        self.spread_factor = 0.001  # 0.1% away from mid price
        self.max_open_orders = 6  # Maximum 3 pairs with buy/sell orders
        self.open_orders = {}
        self.inventory = {}  # Track our inventory for each asset
        self.rebalance_threshold = 0.005  # Rebalance when price moves 0.5%
        
    def get_interval(self) -> float:
        return 20.0  # Check every 20 seconds
    
    def execute(self):
        """Execute the liquidity strategy"""
        # Skip if we already have maximum open orders
        if len(self.open_orders) >= self.max_open_orders:
            self._check_open_orders()
            return
        
        # Select a random trading pair to analyze
        available_pairs = [p for p in self.trading_pairs if 
                          len([o for o in self.open_orders.values() if o['pair'] == p]) < 2]
        
        if not available_pairs:
            self._check_open_orders()
            return
            
        pair = random.choice(available_pairs)
        
        try:
            # Get current orderbook
            orderbook_data = self.okx.get_orderbook(pair)
            if not orderbook_data or 'data' not in orderbook_data or not orderbook_data['data']:
                return
            
            orderbook = orderbook_data['data'][0]
            
            # Calculate mid price
            best_bid = float(orderbook['bids'][0][0])
            best_ask = float(orderbook['asks'][0][0])
            mid_price = (best_bid + best_ask) / 2
            
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
            
            # Calculate order prices
            buy_price = mid_price * (1 - self.spread_factor)
            sell_price = mid_price * (1 + self.spread_factor)
            
            # Calculate quantities
            buy_quantity = trade_amount_usdt / buy_price
            
            # For sell orders, check if we have the asset
            base_currency = pair.split('-')[0]  # e.g., "BTC" from "BTC-USDT"
            base_balance = 0
            
            # Check if we have the base currency in our inventory
            if base_currency in self.inventory:
                base_balance = self.inventory[base_currency]
            
            # If we don't have enough of the base currency, use a smaller amount for the sell order
            sell_quantity = min(buy_quantity, base_balance) if base_balance > 0 else buy_quantity * 0.5
            
            # Place buy order
            if len([o for o in self.open_orders.values() if o['pair'] == pair and o['side'] == 'buy']) == 0:
                buy_order_id = f"liq_buy_{int(time.time())}_{random.randint(1000, 9999)}"
                
                # Record the order
                self.open_orders[buy_order_id] = {
                    'pair': pair,
                    'side': 'buy',
                    'price': buy_price,
                    'quantity': buy_quantity,
                    'timestamp': time.time(),
                    'original_mid': mid_price
                }
                
                # Record the trade
                self._record_trade({
                    'strategy': 'liquidity',
                    'action': 'place_order',
                    'pair': pair,
                    'side': 'buy',
                    'price': buy_price,
                    'quantity': buy_quantity,
                    'order_id': buy_order_id
                })
                
                print(f"[LIQUIDITY] Placed buy order for {pair} at {buy_price}")
            
            # Place sell order if we have inventory
            if len([o for o in self.open_orders.values() if o['pair'] == pair and o['side'] == 'sell']) == 0 and sell_quantity > 0:
                sell_order_id = f"liq_sell_{int(time.time())}_{random.randint(1000, 9999)}"
                
                # Record the order
                self.open_orders[sell_order_id] = {
                    'pair': pair,
                    'side': 'sell',
                    'price': sell_price,
                    'quantity': sell_quantity,
                    'timestamp': time.time(),
                    'original_mid': mid_price
                }
                
                # Record the trade
                self._record_trade({
                    'strategy': 'liquidity',
                    'action': 'place_order',
                    'pair': pair,
                    'side': 'sell',
                    'price': sell_price,
                    'quantity': sell_quantity,
                    'order_id': sell_order_id
                })
                
                print(f"[LIQUIDITY] Placed sell order for {pair} at {sell_price}")
        
        except Exception as e:
            print(f"Error in liquidity strategy: {e}")
    
    def _check_open_orders(self):
        """Check and manage open orders"""
        orders_to_fill = []
        orders_to_cancel = []
        
        for order_id, order in self.open_orders.items():
            try:
                # Get current orderbook
                orderbook_data = self.okx.get_orderbook(order['pair'])
                if not orderbook_data or 'data' not in orderbook_data or not orderbook_data['data']:
                    continue
                
                orderbook = orderbook_data['data'][0]
                
                # Calculate mid price
                best_bid = float(orderbook['bids'][0][0])
                best_ask = float(orderbook['asks'][0][0])
                current_mid = (best_bid + best_ask) / 2
                
                # Check if price has moved significantly
                price_change = abs(current_mid - order['original_mid']) / order['original_mid']
                
                if price_change > self.rebalance_threshold:
                    # Cancel order to rebalance
                    orders_to_cancel.append(order_id)
                    continue
                
                # Simulate order fills
                # For buy orders, fill if market price drops below our order price
                if order['side'] == 'buy' and best_bid <= order['price']:
                    orders_to_fill.append(order_id)
                
                # For sell orders, fill if market price rises above our order price
                elif order['side'] == 'sell' and best_ask >= order['price']:
                    orders_to_fill.append(order_id)
                
                # Cancel orders that have been open too long (5 minutes)
                if time.time() - order['timestamp'] > 300:
                    orders_to_cancel.append(order_id)
            
            except Exception as e:
                print(f"Error checking order {order_id}: {e}")
        
        # Process filled orders
        for order_id in orders_to_fill:
            order = self.open_orders.pop(order_id)
            
            # Update inventory
            base_currency = order['pair'].split('-')[0]
            
            if order['side'] == 'buy':
                # Add to inventory
                if base_currency not in self.inventory:
                    self.inventory[base_currency] = 0
                self.inventory[base_currency] += order['quantity']
                
                # Calculate fee (0.1% maker fee)
                fee = order['price'] * order['quantity'] * 0.001
                
                # Record the trade
                self._record_trade({
                    'strategy': 'liquidity',
                    'action': 'fill_order',
                    'pair': order['pair'],
                    'side': order['side'],
                    'price': order['price'],
                    'quantity': order['quantity'],
                    'order_id': order_id,
                    'fee': fee,
                    'profit': -fee  # Initial profit is negative due to fee
                })
            else:  # sell
                # Remove from inventory
                if base_currency in self.inventory:
                    self.inventory[base_currency] = max(0, self.inventory[base_currency] - order['quantity'])
                
                # Calculate fee (0.1% maker fee)
                fee = order['price'] * order['quantity'] * 0.001
                
                # Calculate profit (assuming we bought at a lower price)
                # For demo, we'll use a simple estimate
                avg_buy_price = order['price'] * 0.995  # Assume we bought 0.5% lower
                profit = (order['price'] - avg_buy_price) * order['quantity'] - fee
                
                # Record the trade
                self._record_trade({
                    'strategy': 'liquidity',
                    'action': 'fill_order',
                    'pair': order['pair'],
                    'side': order['side'],
                    'price': order['price'],
                    'quantity': order['quantity'],
                    'order_id': order_id,
                    'fee': fee,
                    'profit': profit
                })
            
            print(f"[LIQUIDITY] Filled {order['side']} order {order_id} for {order['pair']} at {order['price']}")
        
        # Process cancelled orders
        for order_id in orders_to_cancel:
            order = self.open_orders.pop(order_id)
            
            # Record the cancellation
            self._record_trade({
                'strategy': 'liquidity',
                'action': 'cancel_order',
                'pair': order['pair'],
                'side': order['side'],
                'price': order['price'],
                'quantity': order['quantity'],
                'order_id': order_id,
                'reason': 'rebalance' if time.time() - order['timestamp'] <= 300 else 'timeout'
            })
            
            print(f"[LIQUIDITY] Cancelled {order['side']} order {order_id} for {order['pair']}")