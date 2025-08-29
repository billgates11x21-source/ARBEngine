from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union
import time
import threading
import json
from src.api.okx_client import OKXClient
from src.config import save_state, load_state

class BaseStrategy(ABC):
    """
    Base class for all trading strategies
    """
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.active = False
        self.okx = OKXClient()
        self.state = load_state()
        self.running_thread = None
        self.stop_event = threading.Event()
        
        # Initialize strategy state if not exists
        if 'strategies' not in self.state:
            self.state['strategies'] = {}
        if self.name not in self.state['strategies']:
            self.state['strategies'][self.name] = {
                'active': False,
                'last_execution': None,
                'profit_24h': 0.0,
                'total_profit': 0.0,
                'trades': []
            }
        
        # Load strategy state
        self.strategy_state = self.state['strategies'][self.name]
    
    def start(self):
        """Start the strategy"""
        if not self.active:
            self.active = True
            self.strategy_state['active'] = True
            self.stop_event.clear()
            self.running_thread = threading.Thread(target=self._run_strategy)
            self.running_thread.daemon = True
            self.running_thread.start()
            self._save_state()
            return True
        return False
    
    def stop(self):
        """Stop the strategy"""
        if self.active:
            self.active = False
            self.strategy_state['active'] = False
            self.stop_event.set()
            if self.running_thread and self.running_thread.is_alive():
                self.running_thread.join(timeout=5)
            self._save_state()
            return True
        return False
    
    def get_status(self):
        """Get strategy status"""
        return {
            'name': self.name,
            'description': self.description,
            'active': self.active,
            'last_execution': self.strategy_state.get('last_execution'),
            'profit_24h': self.strategy_state.get('profit_24h', 0.0),
            'total_profit': self.strategy_state.get('total_profit', 0.0),
            'trade_count': len(self.strategy_state.get('trades', []))
        }
    
    def _record_trade(self, trade_data):
        """Record a trade in the strategy state"""
        # Add timestamp
        trade_data['timestamp'] = time.time()
        
        # Add to trades list
        self.strategy_state['trades'].append(trade_data)
        
        # Update last execution time
        self.strategy_state['last_execution'] = trade_data['timestamp']
        
        # Update profit metrics
        profit = trade_data.get('profit', 0.0)
        self.strategy_state['total_profit'] += profit
        
        # Calculate 24h profit
        current_time = time.time()
        day_ago = current_time - (24 * 60 * 60)
        profit_24h = sum([
            trade.get('profit', 0.0) 
            for trade in self.strategy_state['trades'] 
            if trade.get('timestamp', 0) > day_ago
        ])
        self.strategy_state['profit_24h'] = profit_24h
        
        # Save state
        self._save_state()
    
    def _save_state(self):
        """Save strategy state"""
        self.state['strategies'][self.name] = self.strategy_state
        save_state(self.state)
    
    def _run_strategy(self):
        """Run the strategy in a loop"""
        while not self.stop_event.is_set():
            try:
                # Execute strategy step
                self.execute()
                
                # Sleep to avoid excessive API calls
                time.sleep(self.get_interval())
            except Exception as e:
                print(f"Error in strategy {self.name}: {e}")
                time.sleep(10)  # Sleep longer on error
    
    @abstractmethod
    def execute(self):
        """Execute a single step of the strategy"""
        pass
    
    @abstractmethod
    def get_interval(self) -> float:
        """Get the interval between strategy executions in seconds"""
        pass