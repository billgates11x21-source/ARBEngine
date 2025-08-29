import time
import threading
import json
from typing import Dict, List
from src.strategies.arb_engine import ArbEngine
from src.strategies.breakout import BreakoutStrategy
from src.strategies.crossagg import CrossExchangeAggregationStrategy
from src.strategies.liquidity import LiquidityStrategy
from src.strategies.scalper import ScalperStrategy
from src.strategies.triangular_arb import TriangularArbStrategy
from src.config import load_state, save_state

class StrategyOrchestrator:
    """
    Orchestrates and manages all trading strategies
    """
    def __init__(self):
        self.strategies = {}
        self.state = load_state()
        self.running = False
        self.stop_event = threading.Event()
        
        # Initialize strategies
        self._init_strategies()
        
        # Load active strategies from state
        if 'active_strategies' in self.state:
            for strategy_name in self.state['active_strategies']:
                if strategy_name in self.strategies:
                    self.strategies[strategy_name].start()
    
    def _init_strategies(self):
        """Initialize all strategies"""
        self.strategies = {
            'arb': ArbEngine(),
            'breakout': BreakoutStrategy(),
            'crossagg': CrossExchangeAggregationStrategy(),
            'liquidity': LiquidityStrategy(),
            'scalping': ScalperStrategy(),
            'triangular_arb': TriangularArbStrategy()  # Add the new triangular arbitrage strategy
        }
    
    def start_strategy(self, strategy_name: str) -> bool:
        """Start a specific strategy"""
        if strategy_name in self.strategies:
            result = self.strategies[strategy_name].start()
            if result:
                # Update state
                if 'active_strategies' not in self.state:
                    self.state['active_strategies'] = []
                if strategy_name not in self.state['active_strategies']:
                    self.state['active_strategies'].append(strategy_name)
                    save_state(self.state)
            return result
        return False
    
    def stop_strategy(self, strategy_name: str) -> bool:
        """Stop a specific strategy"""
        if strategy_name in self.strategies:
            result = self.strategies[strategy_name].stop()
            if result:
                # Update state
                if 'active_strategies' in self.state and strategy_name in self.state['active_strategies']:
                    self.state['active_strategies'].remove(strategy_name)
                    save_state(self.state)
            return result
        return False
    
    def get_strategy_status(self, strategy_name: str) -> Dict:
        """Get status of a specific strategy"""
        if strategy_name in self.strategies:
            return self.strategies[strategy_name].get_status()
        return {'error': 'Strategy not found'}
    
    def get_all_strategies_status(self) -> List[Dict]:
        """Get status of all strategies"""
        return [strategy.get_status() for strategy in self.strategies.values()]
    
    def start_all(self) -> bool:
        """Start all strategies"""
        success = True
        for strategy_name in self.strategies:
            if not self.start_strategy(strategy_name):
                success = False
        return success
    
    def stop_all(self) -> bool:
        """Stop all strategies"""
        success = True
        for strategy_name in self.strategies:
            if not self.stop_strategy(strategy_name):
                success = False
        return success
    
    def start_monitoring(self):
        """Start monitoring thread"""
        if not self.running:
            self.running = True
            self.stop_event.clear()
            self.monitor_thread = threading.Thread(target=self._monitor_loop)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()
            return True
        return False
    
    def stop_monitoring(self):
        """Stop monitoring thread"""
        if self.running:
            self.running = False
            self.stop_event.set()
            if hasattr(self, 'monitor_thread') and self.monitor_thread.is_alive():
                self.monitor_thread.join(timeout=5)
            return True
        return False
    
    def _monitor_loop(self):
        """Monitor all strategies in a loop"""
        while not self.stop_event.is_set():
            try:
                # Check each strategy's status
                for strategy_name, strategy in self.strategies.items():
                    if strategy.active:
                        status = strategy.get_status()
                        print(f"[MONITOR] {strategy_name}: active={status['active']}, "
                              f"profit_24h={status['profit_24h']}, trades={status['trade_count']}")
                
                # Sleep for a while
                time.sleep(60)  # Check every minute
            except Exception as e:
                print(f"Error in monitor loop: {e}")
                time.sleep(60)  # Sleep on error

# Create a global instance
orchestrator = StrategyOrchestrator()

def start_strategies():
    """Start all strategies and monitoring"""
    orchestrator.start_monitoring()
    
    # Start with just 3 strategies initially, including triangular arbitrage
    orchestrator.start_strategy('scalping')
    orchestrator.start_strategy('breakout')
    orchestrator.start_strategy('triangular_arb')  # Add the new triangular arbitrage strategy
    
    print("Started strategies: scalping, breakout, triangular_arb")
    print("Monitoring active")

if __name__ == "__main__":
    start_strategies()