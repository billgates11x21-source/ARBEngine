import time
import random
import traceback
from typing import Dict, List, Optional
from src.strategies.base_strategy import BaseStrategy
from src.config import load_state, save_state
from src.utils.resilience import SmartSession, CircuitBreaker

session = SmartSession()
cb = CircuitBreaker()

class ArbEngine(BaseStrategy):
    """
    Arbitrage Strategy - Exploits price differences between markets
    
    This strategy:
    1. Identifies price differences for the same asset across different markets
    2. Executes trades to profit from these differences
    3. Manages risk through position sizing and quick execution
    4. Focuses on high-liquidity markets to ensure execution
    5. Monitors and adapts to changing market conditions
    """
    
    def __init__(self):
        super().__init__(
            name="arb",
            description="Exploits price differences between markets"
        )
        self.state = load_state()
        self.balance = {'BTC': 0.0001, 'ETH': 0.001, 'USDT': 7.0}  # Initial balance with 7 USDT
        self.trading_pairs = ["BTC-USDT", "ETH-USDT", "SOL-USDT"]
        self.position_size = 0.03  # 3% of available balance
        self.min_price_diff = 0.003  # Minimum 0.3% price difference to trade
        self.max_open_positions = 2
        self.open_positions = {}
        
        # Load balance from state if available
        if 'balance' in self.state:
            self.balance = self.state['balance']
        
        # Initialize trades list if not exists
        if 'trades' not in self.state:
            self.state['trades'] = []
        
        # Initialize last_trade if not exists
        if 'last_trade' not in self.state:
            self.state['last_trade'] = {}
    
    def get_interval(self) -> float:
        return 25.0  # Check every 25 seconds
    
    def execute(self):
        """Execute the arbitrage strategy"""
        # Skip if we already have maximum open positions
        if len(self.open_positions) >= self.max_open_positions:
            self._check_open_positions()
            return
        
        # Select a random trading pair to analyze
        pair = random.choice(self.trading_pairs)
        
        try:
            # Get current orderbook
            orderbook_data = self.okx.get_orderbook(pair)
            if not orderbook_data or 'data' not in orderbook_data or not orderbook_data['data']:
                return
            
            orderbook = orderbook_data['data'][0]
            
            # Simulate finding an arbitrage opportunity
            # In a real implementation, we would compare prices across different markets
            # For demo, we'll simulate finding an opportunity with a random chance
            
            if random.random() < 0.3:  # 30% chance to find an opportunity
                # Simulate market prices
                market_a_price = float(orderbook['bids'][0][0])
                market_b_price = market_a_price * (1 + random.uniform(self.min_price_diff, 0.01))
                
                # Calculate price difference percentage
                price_diff_pct = (market_b_price - market_a_price) / market_a_price
                
                # Get account balance (use our simulated balance for demo)
                usdt_balance = self.balance['USDT']
                
                # Calculate position size
                trade_amount_usdt = usdt_balance * self.position_size
                if trade_amount_usdt < 1:  # Minimum trade size
                    return
                
                # Calculate quantity
                quantity = trade_amount_usdt / market_a_price
                
                # Calculate fees (0.1% per trade)
                fee_pct = 0.001
                fees = (market_a_price * quantity * fee_pct) + (market_b_price * quantity * fee_pct)
                
                # Calculate potential profit
                potential_profit = (market_b_price - market_a_price) * quantity - fees
                
                # Only proceed if profitable after fees
                if potential_profit <= 0:
                    return
                
                # Create a position
                order_id = f"arb_{int(time.time())}_{random.randint(1000, 9999)}"
                
                # Record the position
                self.open_positions[order_id] = {
                    'pair': pair,
                    'buy_market': 'Market A',
                    'buy_price': market_a_price,
                    'sell_market': 'Market B',
                    'sell_price': market_b_price,
                    'quantity': quantity,
                    'timestamp': time.time(),
                    'fees': fees,
                    'expected_profit': potential_profit,
                    'status': 'executing'
                }
                
                # Update balance (simulate buying)
                self.balance['USDT'] -= trade_amount_usdt
                base_currency = pair.split('-')[0]  # e.g., "BTC" from "BTC-USDT"
                if base_currency not in self.balance:
                    self.balance[base_currency] = 0
                self.balance[base_currency] += quantity
                
                # Record the trade in state
                self.state['last_trade'] = {
                    'token': base_currency,
                    'profit': potential_profit,
                    'timestamp': time.time()
                }
                
                # Add to trades list
                self.state['trades'].append({
                    'token': base_currency,
                    'profit': potential_profit,
                    'timestamp': time.time()
                })
                
                # Save state
                self.state['balance'] = self.balance
                save_state(self.state)
                
                # Record the trade for strategy tracking
                self._record_trade({
                    'strategy': 'arb',
                    'action': 'open_position',
                    'pair': pair,
                    'buy_market': 'Market A',
                    'buy_price': market_a_price,
                    'sell_market': 'Market B',
                    'sell_price': market_b_price,
                    'quantity': quantity,
                    'order_id': order_id,
                    'fees': fees,
                    'expected_profit': potential_profit
                })
                
                print(f"[ARB] Found opportunity: Buy {pair} on Market A at {market_a_price}, "
                      f"Sell on Market B at {market_b_price}, "
                      f"Expected profit: {potential_profit}")
        
        except Exception as e:
            print(f"Error in arbitrage strategy: {e}")
            traceback.print_exc()
    
    def _check_open_positions(self):
        """Check and manage open positions"""
        positions_to_complete = []
        
        for order_id, position in self.open_positions.items():
            try:
                current_time = time.time()
                time_elapsed = current_time - position['timestamp']
                
                # Simulate execution time (30 seconds)
                if time_elapsed > 30:
                    # Simulate execution results
                    # In a real implementation, we would check the actual execution prices
                    # For demo, we'll simulate some slippage
                    actual_buy_price = position['buy_price'] * (1 + random.uniform(0, 0.001))
                    actual_sell_price = position['sell_price'] * (1 - random.uniform(0, 0.001))
                    
                    # Calculate actual profit
                    actual_profit = (actual_sell_price - actual_buy_price) * position['quantity'] - position['fees']
                    
                    # Update balance (simulate selling)
                    base_currency = position['pair'].split('-')[0]
                    self.balance[base_currency] -= position['quantity']
                    self.balance['USDT'] += actual_sell_price * position['quantity']
                    
                    # Update state
                    self.state['balance'] = self.balance
                    self.state['last_trade'] = {
                        'token': base_currency,
                        'profit': actual_profit,
                        'timestamp': time.time()
                    }
                    
                    # Add to trades list
                    self.state['trades'].append({
                        'token': base_currency,
                        'profit': actual_profit,
                        'timestamp': time.time()
                    })
                    
                    # Save state
                    save_state(self.state)
                    
                    # Complete the position
                    positions_to_complete.append((order_id, actual_profit))
            
            except Exception as e:
                print(f"Error checking position {order_id}: {e}")
                traceback.print_exc()
        
        # Complete positions
        for order_id, profit in positions_to_complete:
            position = self.open_positions.pop(order_id)
            
            # Record the trade
            self._record_trade({
                'strategy': 'arb',
                'action': 'close_position',
                'pair': position['pair'],
                'buy_market': position['buy_market'],
                'buy_price': position['buy_price'],
                'sell_market': position['sell_market'],
                'sell_price': position['sell_price'],
                'quantity': position['quantity'],
                'order_id': order_id,
                'fees': position['fees'],
                'expected_profit': position['expected_profit'],
                'actual_profit': profit,
                'profit': profit  # This is used for profit tracking
            })
            
            print(f"[ARB] Completed position {order_id} with profit: {profit}")
    
    @cb
    def step(self, token='ETH', price_spread=0.005, fee_pct=0.001, gas_cost=0.0002):
        """Legacy method for backward compatibility"""
        try:
            profit, loan_amt = self.simulate(token, price_spread, fee_pct, gas_cost)
            if profit > 0:
                print(f'[EXECUTE] {token} arb with loan {loan_amt}, profit {profit:.2f}')
                self.state['last_trade'] = {'token': token, 'profit': profit}
                save_state(self.state)
            else:
                print(f'[SKIP] {token} unprofitable (profit={profit:.2f})')
        except Exception as e:
            print('Error:', e, traceback.format_exc())
    
    def simulate(self, token, price_spread, fee_pct, gas_cost):
        """Legacy method for backward compatibility"""
        loan_ratio = 0.8 if token in ['BTC', 'ETH'] else 0.9
        reserve_ratio = 0.2 if token in ['BTC', 'ETH'] else 0.1
        loan_amt = self.balance['BTC'] * loan_ratio if token == 'BTC' else \
                   self.balance['ETH'] * loan_ratio if token == 'ETH' else \
                   self.balance['USDT'] * loan_ratio
        fees = loan_amt * fee_pct + loan_amt * gas_cost
        profit = loan_amt * price_spread - fees
        return profit, loan_amt